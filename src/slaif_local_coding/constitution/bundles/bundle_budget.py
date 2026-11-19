"""Explicit validated context budgets (objective 021, budget half).

INERT component of the v1 dependency-bundle cache rework
(``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``): the effective context
``C`` and the generation / tool / template-uncertainty / image
reserves are EXPLICIT validated product capabilities (never
inferred from a serving maximum or an executor profile).  Slot
width, aggregate limit and every counting surface are derived here
and counted with the pinned actual tokenizer
(``bundle_tokenizer``) over the FINAL rendered text.

Law (objective 021 item 2 + plan policy 10 + compact architecture
"Insertion budgets"):

- base slot = ``floor(C/32)``; bundle width = number of DISTINCT
  represented files (repeated operands never inflate width);
  allowance = width x slot;
- aggregate injection limit = ``floor(C/4)`` (initial, explicit);
- generation reserve defaults to ``max(4096, floor(C/8))``, tools
  2048, uncertainty / template 1024 -- all explicit, configurable,
  identity-bound and validated against C;
- remaining request content and tool / envelope emissions are
  counted under EXPLICIT finite item limits: ordinary message
  content and the serialized tool data (the pinned template's own
  JSON serialization -- the Transformers ``tojson`` override
  verified in huggingface/transformers
  ``src/transformers/utils/chat_template_utils.py``: ``json.dumps``
  defaults with ``ensure_ascii=False``: insertion-ordered keys,
  default ``', '`` / ``': '`` separators, no indent, no ASCII
  escaping -- never a re-sorted or minified form, which would
  undercount that render) are counted with the real tokenizer
  over the pinned message framing; the
  pinned model envelope's fixed template pieces and
  per-item framing (tool preamble header/footer, the call /
  result wrapper tags, the no-tools reasoning system preamble,
  the generation / think framing) are
  charged as documented conservative structure bounds -- one
  token per rendered UTF-8 byte, which is a provable over-estimate
  for the BPE vocabulary (every token is at least one byte);
- the caller-requested generation limit is RESPECTED, never
  lowered to force a fit; overflow is a typed failure;
- per-retained-image reserves are explicit and require the
  explicit vision contract (the unchanged image policy decides the
  retained count upstream);
- unknown / mismatched template / model / context / vision
  capability refuses; byte / parse limits stay INDEPENDENT of
  token limits: the per-request byte fence (max_request_bytes)
  is a conservative UTF-8 total (exact dynamic bytes, exact
  in-module literal bytes, measured fixed byte bounds for the
  fixed framing fragments) enforced BEFORE any token work,
  independent of token fit; no padding, no silent truncation.

INERT: no request-pipeline wiring, no v1 runtime activation.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Final

from pydantic import Field, model_validator

from .bundle_tokenizer import (
    _IM_END,
    _IM_START,
    BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
    BundleTokenizer,
)
from .graph_models import _fixed, _GraphFrozen

BUNDLE_BUDGET_CONTRACT_VERSION = "cache-bundle-budget/v1"
BUNDLE_BUDGET_POLICY_VERSION = "bundle-budget-policy/v1"
#: The pinned model-envelope structure whose fixed / per-item
#: framing the structure bounds account for (the Qwen3 template
#: tool preamble, tool-call and tool-result wrappers, and the
#: generation / think framing).
BUNDLE_MODEL_ENVELOPE_VERSION = "qwen3-model-envelope/v1"

BUDGET_CONTEXT_MIN = 8_192
BUDGET_CONTEXT_MAX = 1_048_576
BUDGET_GENERATION_FLOOR = 4_096
BUDGET_TOOLS_RESERVE_DEFAULT = 2_048
BUDGET_UNCERTAINTY_RESERVE_DEFAULT = 1_024
BUDGET_SLOT_DIVISOR = 32
BUDGET_AGGREGATE_DIVISOR = 4
BUDGET_GENERATION_DIVISOR = 8

#: Explicit finite item limits (defaults; every one is a closed,
#: positive, identity-bound configuration value).
BUDGET_MAX_DISTINCT_FILES_DEFAULT = 128
BUDGET_MAX_MESSAGES_DEFAULT = 512
BUDGET_MAX_TOOLS_DEFAULT = 512
BUDGET_MAX_TOOL_CALLS_DEFAULT = 64
BUDGET_MAX_TOOL_ARGS_DEFAULT = 64
BUDGET_MAX_RETAINED_IMAGES_DEFAULT = 16
BUDGET_MAX_MESSAGE_BYTES_DEFAULT = 1_048_576
BUDGET_MAX_REQUEST_BYTES_DEFAULT = 16_777_216
BUDGET_MAX_ENTRY_BYTES_DEFAULT = 1_048_576
BUDGET_MAX_COMPILED_BLOCK_BYTES_DEFAULT = 2_097_152

# -- Pinned model-envelope structure bounds ---------------------------
#
# The pinned Qwen3 chat template renders, around the counted data:
# (1) a tool preamble (a fixed header + the serialized
#     provider-format tools + a fixed footer + a fixed
#     call-reminder block) whenever tools are present; (2) per
#     assistant tool call an argument wrapper (open/close call
#     tags, a function tag line, one parameter tag line per
#     argument, close lines); (3) per tool result a result wrapper
#     (open/close result tags, user framing for consecutive
#     results); (4) per assistant history message a thinking
#     frame (fixed open/close pieces around any carried
#     reasoning text, rendered by default even when the NEW
#     generation's thinking is off); (5) the no-tools reasoning
#     system preamble whenever thinking is enabled: the model's
#     built-in default reasoning header at its closed accounting
#     floor when no explicit product reasoning text is present,
#     or the explicit reasoning instruction text (real count)
#     plus the system frame and separators; (6) a generation /
#     think framing at the end (assistant turn tag + open/close
#     think tags).
# Every FIXED fragment is charged with a closed conservative
# numeric overhead (the ENVELOPE_*_BOUND_TOKENS constants below):
# a documented over-estimate of the fragment's real-tokenizer
# count, re-derived from the pinned template asset at test time.
# All DYNAMIC text -- ordinary message content, the serialized
# provider-format tool JSON, function / parameter names, argument
# values and reasoning instructions -- is counted with the real
# pinned tokenizer, so the accounting is tight where it matters.
_ENVELOPE_L = chr(60)
_ENVELOPE_R = chr(62)

#: The pinned per-argument close fragment: one newline, the closed
#: slash-parameter tag and one newline (14 UTF-8 bytes, measured
#: against the pinned template asset; charged per argument, the
#: complete wrapper).
_ENVELOPE_PARAM_CLOSE: Final = "\n" + _ENVELOPE_L + "/parameter" + _ENVELOPE_R + "\n"

#: Closed conservative token overheads for the fixed template
#: framing fragments of the pinned model envelope (one constant
#: per fragment family; each is a provable over-estimate of the
#: fragment's actual pinned-tokenizer count and is re-derived
#: from the pinned template asset at test time).
ENVELOPE_TOOLS_PREFIX_BOUND_TOKENS: Final = 128
ENVELOPE_TOOLS_SUFFIX_BOUND_TOKENS: Final = 64
ENVELOPE_CALL_WRAPPER_BOUND_TOKENS: Final = 32
ENVELOPE_RESULT_WRAPPER_BOUND_TOKENS: Final = 32
ENVELOPE_THINK_FRAMING_BOUND_TOKENS: Final = 32


#: Measured fixed byte bounds for the fixed template framing
#: fragments: each value is the measured UTF-8 length of the
#: pinned template fragment the bound accounts for (a measured
#: fixed byte bound -- no BPE token-width assumption is used in
#: the byte fence).
ENVELOPE_TOOLS_PREFIX_BOUND_BYTES: Final = 78
ENVELOPE_TOOLS_SUFFIX_BOUND_BYTES: Final = 12
ENVELOPE_CALL_WRAPPER_BOUND_BYTES: Final = 37
ENVELOPE_RESULT_WRAPPER_BOUND_BYTES: Final = 22
ENVELOPE_THINK_FRAMING_BOUND_BYTES: Final = 19


#: The pinned fixed tool-call reminder block (the template literal
#: between the tools tags and the system content).  It is a closed
#: conservative structure bound: one token per rendered UTF-8 byte
#: (a provable over-estimate for the BPE vocabulary -- a token is
#: never shorter than one byte).  The bound is the literal's byte
#: length (817), verified at test time to be >= the real-tokenizer
#: count of the exact pinned template literal (177).
ENVELOPE_TOOL_REMINDER_BOUND_TOKENS: Final = 817


#: Pinned assistant-history thinking-frame bounds, charged once
#: per assistant message in history.  The frame renders by
#: default (the pinned template's preserve_thinking default)
#: even when the NEW generation's thinking is off.  The two
#: fixed pieces measure 8 and 11 UTF-8 bytes; the pinned
#: tokenizer counts them 2 and 3 tokens separately, and with an
#: empty carried reasoning text the pieces render joined and
#: count 4 tokens (the measured joined count is charged instead
#: of the 2 + 3 sum).  The carried reasoning text itself is
#: dynamic and counted with the real pinned tokenizer.
ENVELOPE_HIST_THINK_OPEN_BOUND_BYTES: Final = 8
ENVELOPE_HIST_THINK_CLOSE_BOUND_BYTES: Final = 11
ENVELOPE_HIST_THINK_OPEN_BOUND_TOKENS: Final = 2
ENVELOPE_HIST_THINK_CLOSE_BOUND_TOKENS: Final = 3
ENVELOPE_HIST_THINK_EMPTY_BOUND_TOKENS: Final = 4


#: Closed accounting floor for the pinned no-tools built-in
#: reasoning header: whenever thinking is enabled and no
#: explicit product reasoning text is present, the pinned
#: template renders the model's built-in default reasoning
#: instruction inside the system frame.  The isolated pinned
#: Jinja render of the maximal default header measures 237
#: UTF-8 bytes / 42 pinned tokens exactly; that measured count
#: is the floor charged.
ENVELOPE_BUILTIN_REASONING_HEADER_BOUND_BYTES: Final = 237
ENVELOPE_BUILTIN_REASONING_HEADER_BOUND_TOKENS: Final = 42


class BundleBudgetReason(StrEnum):
    """The closed budget failure vocabulary (021)."""

    CONFIG_INVALID = "config_invalid"
    VISION_CONTRACT_MISMATCH = "vision_contract_mismatch"
    BAD_INPUT = "bad_input"
    ITEM_LIMIT_EXCEEDED = "item_limit_exceeded"
    BYTE_LIMIT_EXCEEDED = "byte_limit_exceeded"
    CONTEXT_OVERSUBSCRIBED = "context_oversubscribed"
    ENTRY_OVER_ALLOWANCE = "entry_over_allowance"
    REQUIRED_OVERFLOW = "required_overflow"
    REQUEST_OVERFLOW = "request_overflow"


class BundleBudgetError(Exception):
    """Fixed typed budget refusal (content-free)."""

    def __init__(self, reason: BundleBudgetReason, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"bundle budget refusal: {reason.value}")


def _sha256_hex(data: bytes) -> str:

    return hashlib.sha256(data).hexdigest()


def _canonical_fields_bytes(fields: dict[str, Any]) -> bytes:
    return json.dumps(fields, sort_keys=True, separators=(",", ":")).encode("utf-8")


class BundleBudgetConfig(_GraphFrozen):
    """Explicit validated product capability (the effective C).

    The effective context is CONFIGURED, never inferred.  The three
    text reserves default to the plan's documented initial values
    (generation ``max(4096, floor(C/8))``, tools 2048,
    uncertainty/template 1024) and are explicit, identity-bound and
    validated against C.
    """

    context_tokens: int = Field(ge=BUDGET_CONTEXT_MIN, le=BUDGET_CONTEXT_MAX)
    generation_reserve: int | None = Field(default=None, ge=1, le=BUDGET_CONTEXT_MAX)
    tools_reserve: int | None = Field(default=None, ge=1, le=BUDGET_CONTEXT_MAX)
    uncertainty_reserve: int | None = Field(default=None, ge=1, le=BUDGET_CONTEXT_MAX)
    vision_enabled: bool = False
    per_image_reserve: int = Field(default=0, ge=0, le=BUDGET_CONTEXT_MAX)
    max_distinct_files: int = Field(default=BUDGET_MAX_DISTINCT_FILES_DEFAULT, ge=1, le=4096)
    max_messages: int = Field(default=BUDGET_MAX_MESSAGES_DEFAULT, ge=1, le=8192)
    max_tools: int = Field(default=BUDGET_MAX_TOOLS_DEFAULT, ge=1, le=4096)
    max_tool_calls: int = Field(default=BUDGET_MAX_TOOL_CALLS_DEFAULT, ge=1, le=4096)
    max_tool_args: int = Field(default=BUDGET_MAX_TOOL_ARGS_DEFAULT, ge=1, le=4096)
    max_retained_images: int = Field(default=BUDGET_MAX_RETAINED_IMAGES_DEFAULT, ge=0, le=4096)
    max_message_bytes: int = Field(default=BUDGET_MAX_MESSAGE_BYTES_DEFAULT, ge=1, le=268_435_456)
    max_request_bytes: int = Field(default=BUDGET_MAX_REQUEST_BYTES_DEFAULT, ge=1, le=2_147_483_648)
    max_entry_bytes: int = Field(default=BUDGET_MAX_ENTRY_BYTES_DEFAULT, ge=1, le=67_108_864)
    max_compiled_block_bytes: int = Field(
        default=BUDGET_MAX_COMPILED_BLOCK_BYTES_DEFAULT, ge=1, le=134_217_728
    )

    @model_validator(mode="after")
    def _v_reserves(self) -> BundleBudgetConfig:
        c = self.context_tokens
        if type(c) is not int or isinstance(c, bool):
            raise _fixed("the effective context must be an explicit integer")
        gen = (
            self.generation_reserve
            if self.generation_reserve is not None
            else max(BUDGET_GENERATION_FLOOR, c // BUDGET_GENERATION_DIVISOR)
        )
        tools = (
            self.tools_reserve if self.tools_reserve is not None else BUDGET_TOOLS_RESERVE_DEFAULT
        )
        unc = (
            self.uncertainty_reserve
            if self.uncertainty_reserve is not None
            else BUDGET_UNCERTAINTY_RESERVE_DEFAULT
        )
        for name, value in (
            ("generation_reserve", gen),
            ("tools_reserve", tools),
            ("uncertainty_reserve", unc),
        ):
            if type(value) is not int or isinstance(value, bool) or not (1 <= value <= c):
                raise _fixed(f"{name} must be an explicit integer within the context")
        if gen + tools + unc > c:
            raise _fixed("the text reserves together exceed the effective context")
        if (self.per_image_reserve >= 1) != self.vision_enabled:
            raise _fixed(
                "the per-retained-image reserve requires the explicit vision contract (and only it)"
            )
        if self.vision_enabled and self.max_retained_images < 1:
            raise _fixed("the explicit vision contract requires retained capacity")
        return self

    @property
    def slot(self) -> int:
        """Base slot: ``floor(C/32)``."""
        return self.context_tokens // BUDGET_SLOT_DIVISOR

    @property
    def aggregate(self) -> int:
        """Aggregate injection limit (initial ``floor(C/4)``)."""
        return self.context_tokens // BUDGET_AGGREGATE_DIVISOR

    @property
    def default_generation(self) -> int:
        return max(BUDGET_GENERATION_FLOOR, self.context_tokens // BUDGET_GENERATION_DIVISOR)

    @property
    def effective_generation(self) -> int:
        return (
            self.generation_reserve
            if self.generation_reserve is not None
            else self.default_generation
        )

    @property
    def effective_tools(self) -> int:
        return (
            self.tools_reserve if self.tools_reserve is not None else BUDGET_TOOLS_RESERVE_DEFAULT
        )

    @property
    def effective_uncertainty(self) -> int:
        return (
            self.uncertainty_reserve
            if self.uncertainty_reserve is not None
            else BUDGET_UNCERTAINTY_RESERVE_DEFAULT
        )

    def _canonical_fields(self) -> dict[str, Any]:
        return {
            "policy_version": BUNDLE_BUDGET_POLICY_VERSION,
            "context_tokens": self.context_tokens,
            "generation_reserve": self.effective_generation,
            "tools_reserve": self.effective_tools,
            "uncertainty_reserve": self.effective_uncertainty,
            "vision_enabled": self.vision_enabled,
            "per_image_reserve": self.per_image_reserve,
            "max_distinct_files": self.max_distinct_files,
            "max_messages": self.max_messages,
            "max_tools": self.max_tools,
            "max_tool_calls": self.max_tool_calls,
            "max_tool_args": self.max_tool_args,
            "max_retained_images": self.max_retained_images,
            "max_message_bytes": self.max_message_bytes,
            "max_request_bytes": self.max_request_bytes,
            "max_entry_bytes": self.max_entry_bytes,
            "max_compiled_block_bytes": self.max_compiled_block_bytes,
        }

    @property
    def budget_identity(self) -> str:
        return _sha256_hex(_canonical_fields_bytes(self._canonical_fields()))


class BudgetMessage(_GraphFrozen):
    """One request message for envelope accounting (roles closed).

    ``reasoning_content`` carries the assistant's already-
    generated reasoning text (the pinned envelope renders it,
    trimmed, inside the assistant history thinking frame); it is
    countable ONLY on assistant messages -- any other shape is
    refused explicitly, never silently dropped or guessed.
    """

    role: str = Field(min_length=1, max_length=16)
    content: str = Field(max_length=4_194_304)
    reasoning_content: str | None = Field(default=None, max_length=4_194_304)

    @model_validator(mode="after")
    def _v_role(self) -> BudgetMessage:
        if self.role not in {"system", "user", "assistant", "tool"}:
            raise _fixed("the budget message role is not in the closed set")
        if self.reasoning_content is not None and self.role != "assistant":
            raise _fixed(
                "carried reasoning text is countable only on assistant "
                "messages (the pinned envelope renders it nowhere else)"
            )
        return self


class BudgetToolSpec(_GraphFrozen):
    """One tool definition for the serialized tool data."""

    name: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=4096)
    parameters: dict[str, Any] = Field(default_factory=dict)


class BudgetToolCall(_GraphFrozen):
    """One assistant tool call (arguments in the actual order)."""

    name: str = Field(min_length=1, max_length=256)
    arguments: tuple[tuple[str, str], ...] = ()


class BudgetEntry(_GraphFrozen):
    """One ready compiled entry presented to the budget decision."""

    label: str = Field(min_length=1, max_length=512)
    required: bool
    distinct_files: int = Field(ge=1)
    rendered_block: str = Field(min_length=1, max_length=8_388_608)


class BudgetEntryDecision(_GraphFrozen):
    label: str
    required: bool
    distinct_files: int
    tokens: int = Field(ge=0)
    allowance: int = Field(ge=1)
    included: bool


class BudgetOutcome(StrEnum):
    OK = "ok"
    REQUIRED_OVERFLOW = "required_overflow"
    REQUEST_OVERFLOW = "request_overflow"
    ENTRY_INVALID = "entry_invalid"


class BudgetDecision(_GraphFrozen):
    outcome: BudgetOutcome
    entries: tuple[BudgetEntryDecision, ...]
    total_injected_tokens: int = Field(ge=0)
    aggregate_limit: int = Field(ge=1)
    request_content_tokens: int = Field(ge=0)
    request_capacity: int = Field(ge=0)
    generation_effective: int = Field(ge=1)
    omitted_optional: tuple[str, ...] = ()
    guidance: tuple[str, ...] = ()


class BundleBudgetPlan:
    """The derived budget plan (explicit C, slots, reserves, counting).

    ``plan_identity`` binds the budget configuration identity AND
    the pinned tokenization identity: a changed context, reserve,
    item limit, tokenizer or template invalidates the plan (B04).
    """

    def __init__(self, tokenizer: BundleTokenizer, config: BundleBudgetConfig) -> None:
        self.tokenizer = tokenizer
        self.config = config
        self.tokenizer_identity = tokenizer.binding.identity
        self.model_envelope_version = BUNDLE_MODEL_ENVELOPE_VERSION
        self._frame_tokens = {
            role: tokenizer.count_tokens(_IM_START + role + "\n" + _IM_END + "\n")
            for role in ("system", "user", "assistant", "tool")
        }
        # Fixed template framing: closed conservative numeric
        # overheads (never literals); dynamic text is counted with
        # the real pinned tokenizer.
        self._tools_prefix_tokens = ENVELOPE_TOOLS_PREFIX_BOUND_TOKENS
        self._tools_suffix_tokens = ENVELOPE_TOOLS_SUFFIX_BOUND_TOKENS
        self._call_open_tokens = ENVELOPE_CALL_WRAPPER_BOUND_TOKENS
        self._call_close_tokens = ENVELOPE_CALL_WRAPPER_BOUND_TOKENS
        self._result_open_tokens = ENVELOPE_RESULT_WRAPPER_BOUND_TOKENS
        self._result_close_tokens = ENVELOPE_RESULT_WRAPPER_BOUND_TOKENS
        self._result_user_open_tokens = tokenizer.count_tokens(_IM_START + "user")
        self._result_user_close_tokens = tokenizer.count_tokens(_IM_END + "\n")
        self._gen_open_tokens = tokenizer.count_tokens(_IM_START + "assistant\n")
        self._gen_think_on_tokens = ENVELOPE_THINK_FRAMING_BOUND_TOKENS
        self._gen_think_off_tokens = ENVELOPE_THINK_FRAMING_BOUND_TOKENS
        # Pinned assistant-history thinking-frame bounds (the
        # measured fixed pieces; charged per assistant message,
        # rendered by default even when the new generation's
        # thinking is off):
        self._hist_think_open_tokens = ENVELOPE_HIST_THINK_OPEN_BOUND_TOKENS
        self._hist_think_close_tokens = ENVELOPE_HIST_THINK_CLOSE_BOUND_TOKENS
        self._hist_think_empty_tokens = ENVELOPE_HIST_THINK_EMPTY_BOUND_TOKENS
        # Measured fixed byte bounds for the fixed framing
        # fragments (each is the measured UTF-8 length of the
        # pinned template fragment it accounts for):
        self._tools_prefix_bytes = ENVELOPE_TOOLS_PREFIX_BOUND_BYTES
        self._tools_suffix_bytes = ENVELOPE_TOOLS_SUFFIX_BOUND_BYTES
        self._call_open_bytes = ENVELOPE_CALL_WRAPPER_BOUND_BYTES
        self._call_close_bytes = ENVELOPE_CALL_WRAPPER_BOUND_BYTES
        self._result_open_bytes = ENVELOPE_RESULT_WRAPPER_BOUND_BYTES
        self._result_close_bytes = ENVELOPE_RESULT_WRAPPER_BOUND_BYTES
        self._result_user_open_bytes = len((_IM_START + "user").encode("utf-8"))
        self._result_user_close_bytes = len((_IM_END + "\n").encode("utf-8"))
        self._gen_think_bytes = ENVELOPE_THINK_FRAMING_BOUND_BYTES
        self._hist_think_open_bytes = ENVELOPE_HIST_THINK_OPEN_BOUND_BYTES
        self._hist_think_close_bytes = ENVELOPE_HIST_THINK_CLOSE_BOUND_BYTES

    # -- identity -------------------------------------------------------

    def plan_identity(self) -> str:
        fields = self.config._canonical_fields()
        fields["tokenizer_identity"] = self.tokenizer_identity
        fields["render_policy_version"] = BUNDLE_TOKENIZER_RENDER_POLICY_VERSION
        fields["model_envelope_version"] = self.model_envelope_version
        return _sha256_hex(_canonical_fields_bytes(fields))

    @property
    def slot(self) -> int:
        return self.config.slot

    @property
    def aggregate(self) -> int:
        return self.config.aggregate

    # -- allowances ------------------------------------------------------

    def entry_allowance(self, distinct_files: int) -> int:
        """Allowance = width x slot for DISTINCT represented files."""
        c = self.config
        if type(distinct_files) is not int or isinstance(distinct_files, bool):
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "distinct_files")
        if not (1 <= distinct_files <= c.max_distinct_files):
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "distinct_files")
        return distinct_files * self.slot

    def generation_effective(self, requested_max_tokens: int | None) -> int:
        """Respect the caller-requested generation; never lower it."""
        if requested_max_tokens is None:
            return self.config.effective_generation
        if (
            type(requested_max_tokens) is not int
            or isinstance(requested_max_tokens, bool)
            or not (1 <= requested_max_tokens <= self.config.context_tokens)
        ):
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "requested_max_tokens")
        return requested_max_tokens

    def request_capacity(
        self,
        generation: int,
        retained_images: int,
    ) -> int:
        """Residual context for ordinary request content (>= 0)."""
        c = self.config
        if type(retained_images) is not int or isinstance(retained_images, bool):
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "retained_images")
        if not (0 <= retained_images <= c.max_retained_images):
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "retained_images")
        if retained_images > 0 and not c.vision_enabled:
            raise BundleBudgetError(
                BundleBudgetReason.VISION_CONTRACT_MISMATCH,
                "retained images require the explicit vision contract",
            )
        if c.vision_enabled and c.per_image_reserve < 1:
            raise BundleBudgetError(BundleBudgetReason.VISION_CONTRACT_MISMATCH)
        capacity = (
            c.context_tokens
            - self.aggregate
            - generation
            - c.effective_tools
            - c.effective_uncertainty
            - c.per_image_reserve * retained_images
        )
        if capacity < 0:
            raise BundleBudgetError(
                BundleBudgetReason.CONTEXT_OVERSUBSCRIBED,
                "reserves plus the aggregate exceed the effective context",
            )
        return capacity

    # -- compiled-entry counting -----------------------------------------

    def count_compiled_block(self, block: str) -> int:
        """Real-tokenizer count of the final rendered compiled block
        (references, metadata and separators included; no padding)."""
        if not isinstance(block, str) or not block:
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "compiled block")
        if len(block.encode("utf-8")) > self.config.max_compiled_block_bytes:
            raise BundleBudgetError(BundleBudgetReason.BYTE_LIMIT_EXCEEDED, "compiled block")
        return self.tokenizer.count_tokens(block)

    # -- request envelope accounting --------------------------------------

    def _serialized_tool(self, tool: BudgetToolSpec) -> str:
        """The tool JSON in the pinned template's own serialization
        form: the Transformers ``tojson`` override (verified in
        huggingface/transformers
        ``src/transformers/utils/chat_template_utils.py``) is
        ``json.dumps`` defaults with ``ensure_ascii=False`` --
        insertion-ordered keys, default ``', '`` / ``': '``
        separators, no indent, no ASCII escaping.  A re-sorted or
        minified form renders fewer bytes / tokens than that
        template output and is never used for counting."""
        obj = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }
        try:
            return json.dumps(obj, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "tool spec") from exc

    def count_tool_preamble(
        self,
        tools: tuple[BudgetToolSpec, ...],
        *,
        enable_thinking: bool,
        reasoning_instructions: str = "",
    ) -> int:
        """The pinned preamble: the single token charge shared
        with the request envelope path (``_count_preamble_actual``
        reuses this helper).  With tools present: the pinned tool
        preamble (the fixed template pieces -- header, per-tool
        separator, footer, closed reminder bound, reasoning
        instructions -- plus the serialized tool data in the
        pinned tojson form counted with the real tokenizer).
        With the tools tuple empty and thinking enabled: the
        model's built-in reasoning header (the explicit product
        reasoning text with the REAL pinned tokenizer plus the
        system frame and the separators, or the built-in default
        header at its closed accounting floor -- never free)."""
        c = self.config
        if len(tools) > c.max_tools:
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "tools")
        if not tools:
            if enable_thinking:
                if reasoning_instructions:
                    return (
                        self.tokenizer.count_tokens(reasoning_instructions + "\n\n")
                        + self._frame_tokens["system"]
                    )
                return ENVELOPE_BUILTIN_REASONING_HEADER_BOUND_TOKENS
            return 0
        total = self._tools_prefix_tokens + self._tools_suffix_tokens
        total += ENVELOPE_TOOL_REMINDER_BOUND_TOKENS
        if enable_thinking and reasoning_instructions:
            total += self.tokenizer.count_tokens(reasoning_instructions + "\n\n")
        for tool in tools:
            total += 1  # the pinned per-tool newline separator
            total += self.tokenizer.count_tokens(self._serialized_tool(tool))
        return total

    def count_tool_call(self, call: BudgetToolCall) -> int:
        """One assistant tool call: the pinned argument wrapper
        (call tags, function line, per-argument parameter lines,
        close lines) plus the actual argument values counted with
        the real tokenizer."""
        c = self.config
        if len(call.arguments) > c.max_tool_args:
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "tool args")
        total = self._call_open_tokens + 2  # the pinned blank-line separator
        total += self.tokenizer.count_tokens(
            _ENVELOPE_L + "function=" + call.name + _ENVELOPE_R + "\n"
        )
        for arg_name, arg_value in call.arguments:
            total += self.tokenizer.count_tokens(
                _ENVELOPE_L + "parameter=" + arg_name + _ENVELOPE_R + "\n"
            )
            total += self.tokenizer.count_tokens(arg_value)
            total += self.tokenizer.count_tokens(_ENVELOPE_PARAM_CLOSE)
        total += self.tokenizer.count_tokens(_ENVELOPE_L + _ENVELOPE_R + "\n")
        total += self._call_close_tokens
        return total

    # -- request byte preflight (max_request_bytes) -------------------

    @staticmethod
    def _utf8_len(text: str) -> int:
        return len(text.encode("utf-8"))

    def _envelope_byte_cost(
        self,
        messages: tuple[BudgetMessage, ...],
        tools: tuple[BudgetToolSpec, ...],
        tool_calls: tuple[BudgetToolCall, ...],
        enable_thinking: bool,
        reasoning_instructions: str,
    ) -> int:
        """Conservative UTF-8 byte total of the full pinned envelope
        (the ``max_request_bytes`` fence measure): every DYNAMIC
        text at its exact rendered bytes; every FIXED framing
        literal this module renders at its exact bytes; every
        fixed framing fragment at its measured fixed byte bound
        (the measured UTF-8 length of the pinned template
        fragment -- no BPE token-width assumption).
        A ``tool`` message is counted under the pinned template's
        tool-result wrapper group framing (the result tags plus
        the user framing that opens a consecutive tool-result
        group), never the ordinary message frame.
        Deterministic, with no tokenizer call and no
        token-capacity input: the byte fence is independent of
        token fit and runs before any token work."""
        total = 0
        prev_role: str | None = None
        for message in messages:
            if message.role == "tool":
                if prev_role is None or prev_role != "tool":
                    total += (
                        self._result_user_open_bytes
                        + self._result_open_bytes
                        + self._result_close_bytes
                    )
                else:
                    total += self._result_open_bytes
                total += self._utf8_len(message.content)
                total += self._result_close_bytes
            else:
                total += self._utf8_len(_IM_START + message.role + "\n" + _IM_END + "\n")
                if message.role == "assistant":
                    # The pinned assistant-history thinking frame
                    # at its measured fixed byte bounds plus the
                    # carried reasoning text at its exact bytes.
                    rc = (message.reasoning_content or "").strip()
                    total += (
                        self._hist_think_open_bytes
                        + self._hist_think_close_bytes
                        + self._utf8_len(rc)
                    )
                total += self._utf8_len(message.content)
            prev_role = message.role
        if tools:
            total += self._tools_prefix_bytes
            total += self._tools_suffix_bytes
            total += 4 * ENVELOPE_TOOL_REMINDER_BOUND_TOKENS
            if enable_thinking and reasoning_instructions:
                total += self._utf8_len(reasoning_instructions) + 2
            for tool in tools:
                total += 1  # the pinned per-tool newline separator
                total += self._utf8_len(self._serialized_tool(tool))
        elif enable_thinking:
            # The pinned no-tools template renders the model's
            # built-in reasoning header whenever thinking is
            # enabled: the explicit product reasoning text at
            # its exact rendered bytes plus the system frame
            # and the separators, or the built-in default
            # header at its closed accounting floor.
            if reasoning_instructions:
                total += self._utf8_len(reasoning_instructions + "\n\n") + self._utf8_len(
                    _IM_START + "system\n" + _IM_END + "\n"
                )
            else:
                total += ENVELOPE_BUILTIN_REASONING_HEADER_BOUND_BYTES
        for call in tool_calls:
            total += self._call_open_bytes + 4 * 2  # the pinned blank-line separator
            total += self._utf8_len(_ENVELOPE_L + "function=" + call.name + _ENVELOPE_R + "\n")
            for arg_name, arg_value in call.arguments:
                total += self._utf8_len(_ENVELOPE_L + "parameter=" + arg_name + _ENVELOPE_R + "\n")
                total += self._utf8_len(arg_value)
                total += self._utf8_len(_ENVELOPE_PARAM_CLOSE)
            total += self._utf8_len(_ENVELOPE_L + _ENVELOPE_R + "\n")
            total += self._call_close_bytes
        total += self._utf8_len(_IM_START + "assistant\n")
        total += self._gen_think_bytes
        return total

    def count_request_envelope(
        self,
        messages: tuple[BudgetMessage, ...],
        tools: tuple[BudgetToolSpec, ...] = (),
        *,
        tool_calls: tuple[BudgetToolCall, ...] = (),
        enable_thinking: bool = True,
        reasoning_instructions: str = "",
        retained_images: int = 0,
        requested_max_tokens: int | None = None,
    ) -> int:
        """The full pinned model envelope, counted per the law:
        message content and serialized tool data with the real
        tokenizer (the pinned template's own JSON serialization for
        the tool data); the fixed / per-item template framing with
        the documented conservative structure bounds; explicit
        finite item limits; byte limits independent of tokens,
        the per-request fence enforced before any token work.
        The capacity decision is made ONLY on the actual tokenizer
        count plus the structure costs -- never on a byte-length
        pre-bound."""
        c = self.config
        if len(messages) > c.max_messages:
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "messages")
        if len(tool_calls) > c.max_tool_calls:
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "tool calls")
        if len(tools) > c.max_tools:
            raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "tools")
        for call in tool_calls:
            if len(call.arguments) > c.max_tool_args:
                raise BundleBudgetError(BundleBudgetReason.ITEM_LIMIT_EXCEEDED, "tool args")
        for message in messages:
            if len(message.content.encode("utf-8")) > c.max_message_bytes:
                raise BundleBudgetError(BundleBudgetReason.BYTE_LIMIT_EXCEEDED, "message content")
        request_bytes = self._envelope_byte_cost(
            messages, tools, tool_calls, enable_thinking, reasoning_instructions
        )
        if request_bytes > c.max_request_bytes:
            raise BundleBudgetError(BundleBudgetReason.BYTE_LIMIT_EXCEEDED, "request")
        # The caller-requested generation and the image reserves are
        # capacity consumers, not envelope bytes; the capacity check
        # is made below on the ACTUAL tokenizer count (real framing,
        # real content, serialized tool data, argument wrappers) plus
        # the closed conservative structure bounds; the byte fences
        # above stay independent of tokens.
        generation = self.generation_effective(requested_max_tokens)
        capacity = self.request_capacity(generation, retained_images)
        actual = 0
        prev_role: str | None = None
        for message in messages:
            if message.role == "tool":
                # The pinned template wraps tool results: the user
                # framing opens each consecutive tool-result group,
                # the result tags bracket every tool result.
                if prev_role is None or prev_role != "tool":
                    actual += self._result_user_open_tokens
                    actual += self._result_open_tokens
                    actual += self._result_close_tokens
                else:
                    actual += self._result_open_tokens
                actual += self.tokenizer.count_tokens(message.content)
                actual += self._result_close_tokens
            else:
                actual += self._frame_tokens[message.role]
                if message.role == "assistant":
                    # The pinned assistant-history thinking frame
                    # (rendered by default, even with the new
                    # generation's thinking off): the fixed pieces
                    # at their measured counts plus the carried
                    # reasoning text with the real tokenizer; with
                    # no reasoning text the joined pieces are the
                    # measured joined count.
                    rc = (message.reasoning_content or "").strip()
                    if rc:
                        actual += self._hist_think_open_tokens
                        actual += self.tokenizer.count_tokens(rc)
                        actual += self._hist_think_close_tokens
                    else:
                        actual += self._hist_think_empty_tokens
                actual += self.tokenizer.count_tokens(message.content)
            prev_role = message.role
        actual += self._count_preamble_actual(tools, enable_thinking, reasoning_instructions)
        for call in tool_calls:
            actual += self.count_tool_call(call)
        actual += self._gen_open_tokens
        actual += self._gen_think_on_tokens if enable_thinking else self._gen_think_off_tokens
        if actual > capacity:
            raise BundleBudgetError(BundleBudgetReason.REQUEST_OVERFLOW)
        return actual

    def _count_preamble_actual(
        self,
        tools: tuple[BudgetToolSpec, ...],
        enable_thinking: bool,
        reasoning_instructions: str,
    ) -> int:
        # The single preamble token charge, reused from the
        # public helper so the actual request path and the
        # helper can never diverge: the pinned tool preamble
        # with tools present; the pinned no-tools built-in
        # reasoning header with the tools tuple empty and
        # thinking enabled.
        return self.count_tool_preamble(
            tools,
            enable_thinking=enable_thinking,
            reasoning_instructions=reasoning_instructions,
        )

    # -- decision ----------------------------------------------------------

    def decide(
        self,
        entries: tuple[BudgetEntry, ...],
        *,
        requested_max_tokens: int | None = None,
        retained_images: int = 0,
        request_envelope_tokens: int = 0,
        join_separator: str = "",
        final_extras: tuple[str, ...] = (),
    ) -> BudgetDecision:
        """Deterministic required-then-optional budget decision.

        Required entries are complete-or-typed-failure (never
        truncated); optional entries are whole-entry omissions when
        the aggregate cannot hold them; the rendered blocks are
        counted with the real tokenizer against the per-entry
        allowance and the aggregate limit.

        AGGREGATE LAW: when ``join_separator`` and/or
        ``final_extras`` are supplied, the aggregate decision is
        made over the EXACT COMBINED final injected text -- the
        included rendered blocks in order joined by the
        deterministic separator plus the emitted extras (the
        caller's final appended text, e.g. the selection's
        missing-binding guidance) -- counted with the REAL pinned
        tokenizer: ``join_separator.join(included_blocks +
        final_extras)``.  The combined count (not the SUM of the
        individual block counts) is what must hold under the
        aggregate floor(C/4) limit, so BPE boundary effects and
        the emitted extras are never uncounted.  The per-entry
        width x slot allowance decision stays on the individual
        block.  Without either argument the documented SUM
        behavior applies (no combined injection text was
        supplied).  Every element of ``final_extras`` is a
        nonempty text under the independent per-entry byte
        bound; the combined text is under the independent
        compiled-block byte bound; the emitted extras alone
        must fit the aggregate limit (a typed
        CONTEXT_OVERSUBSCRIBED error, never a silent pass).
        """
        generation = self.generation_effective(requested_max_tokens)
        capacity = self.request_capacity(generation, retained_images)
        if not isinstance(join_separator, str):
            raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "join_separator")
        for extra in final_extras:
            if not isinstance(extra, str) or not extra:
                raise BundleBudgetError(BundleBudgetReason.BAD_INPUT, "final_extras")
            if len(extra.encode("utf-8")) > self.config.max_entry_bytes:
                raise BundleBudgetError(BundleBudgetReason.BYTE_LIMIT_EXCEEDED, "final extras")
        combined_mode = join_separator != "" or len(final_extras) > 0
        extras_list = list(final_extras)
        if request_envelope_tokens > capacity:
            return BudgetDecision(
                outcome=BudgetOutcome.REQUEST_OVERFLOW,
                entries=(),
                total_injected_tokens=0,
                aggregate_limit=self.aggregate,
                request_content_tokens=request_envelope_tokens,
                request_capacity=capacity,
                generation_effective=generation,
            )
        decisions: list[BudgetEntryDecision] = []
        omitted: list[str] = []
        total = 0
        included_blocks: list[str] = []
        guidance: list[str] = []
        if combined_mode:
            # The caller's OWN emitted text alone must fit the
            # entire aggregate limit (typed; never a silent
            # pass).  The separator-joined extras are the floor
            # of every combined text below.
            floor_tokens = self.tokenizer.count_tokens(join_separator.join(extras_list))
            if floor_tokens > self.aggregate:
                raise BundleBudgetError(
                    BundleBudgetReason.CONTEXT_OVERSUBSCRIBED,
                    "the emitted final extras alone exceed the aggregate limit",
                )
        for entry in entries:
            allowance = self.entry_allowance(entry.distinct_files)
            if len(entry.rendered_block.encode("utf-8")) > self.config.max_entry_bytes:
                if entry.required:
                    return BudgetDecision(
                        outcome=BudgetOutcome.ENTRY_INVALID,
                        entries=tuple(decisions),
                        total_injected_tokens=total,
                        aggregate_limit=self.aggregate,
                        request_content_tokens=request_envelope_tokens,
                        request_capacity=capacity,
                        generation_effective=generation,
                        omitted_optional=tuple(omitted),
                        guidance=tuple(
                            guidance + ["required-entry exceeds the independent byte bound"]
                        ),
                    )
                omitted.append(entry.label)
                continue
            tokens = self.count_compiled_block(entry.rendered_block)
            if tokens > allowance:
                if entry.required:
                    return BudgetDecision(
                        outcome=BudgetOutcome.ENTRY_INVALID,
                        entries=tuple(decisions),
                        total_injected_tokens=total,
                        aggregate_limit=self.aggregate,
                        request_content_tokens=request_envelope_tokens,
                        request_capacity=capacity,
                        generation_effective=generation,
                        omitted_optional=tuple(omitted),
                        guidance=tuple(
                            guidance
                            + [
                                "required-entry rendered block exceeds its "
                                "width x slot allowance (typed; never truncated)"
                            ]
                        ),
                    )
                omitted.append(entry.label)
                continue
            if combined_mode:
                # The EXACT COMBINED final injected text with the
                # candidate included: real-tokenizer count (the
                # sum of the individual counts is not the
                # combined count), under the independent byte
                # bound first.
                combined_text = join_separator.join(
                    included_blocks + [entry.rendered_block] + extras_list
                )
                if len(combined_text.encode("utf-8")) > self.config.max_compiled_block_bytes:
                    if entry.required:
                        return BudgetDecision(
                            outcome=BudgetOutcome.ENTRY_INVALID,
                            entries=tuple(decisions),
                            total_injected_tokens=total,
                            aggregate_limit=self.aggregate,
                            request_content_tokens=request_envelope_tokens,
                            request_capacity=capacity,
                            generation_effective=generation,
                            omitted_optional=tuple(omitted),
                            guidance=tuple(
                                guidance
                                + [
                                    "required-entry combined injection text "
                                    "exceeds the independent byte bound "
                                    "(typed; never truncated)"
                                ]
                            ),
                        )
                    omitted.append(entry.label)
                    continue
                combined_tokens = self.tokenizer.count_tokens(combined_text)
                if combined_tokens > self.aggregate:
                    if entry.required:
                        return BudgetDecision(
                            outcome=BudgetOutcome.REQUIRED_OVERFLOW,
                            entries=tuple(decisions),
                            total_injected_tokens=total,
                            aggregate_limit=self.aggregate,
                            request_content_tokens=request_envelope_tokens,
                            request_capacity=capacity,
                            generation_effective=generation,
                            omitted_optional=tuple(omitted),
                            guidance=tuple(
                                guidance
                                + [
                                    "required governance does not fit the "
                                    "aggregate floor(C/4) limit over the "
                                    "exact combined injected text "
                                    "(typed 422; no truncation)"
                                ]
                            ),
                        )
                    omitted.append(entry.label)
                    continue
            elif total + tokens > self.aggregate:
                if entry.required:
                    return BudgetDecision(
                        outcome=BudgetOutcome.REQUIRED_OVERFLOW,
                        entries=tuple(decisions),
                        total_injected_tokens=total,
                        aggregate_limit=self.aggregate,
                        request_content_tokens=request_envelope_tokens,
                        request_capacity=capacity,
                        generation_effective=generation,
                        omitted_optional=tuple(omitted),
                        guidance=tuple(
                            guidance
                            + [
                                "required governance does not fit the aggregate "
                                "floor(C/4) limit (typed 422; no truncation)"
                            ]
                        ),
                    )
                omitted.append(entry.label)
                continue
            decisions.append(
                BudgetEntryDecision(
                    label=entry.label,
                    required=entry.required,
                    distinct_files=entry.distinct_files,
                    tokens=tokens,
                    allowance=allowance,
                    included=True,
                )
            )
            included_blocks.append(entry.rendered_block)
            if combined_mode:
                total = self.tokenizer.count_tokens(
                    join_separator.join(included_blocks + extras_list)
                )
            else:
                total += tokens
        return BudgetDecision(
            outcome=BudgetOutcome.OK,
            entries=tuple(decisions),
            total_injected_tokens=total,
            aggregate_limit=self.aggregate,
            request_content_tokens=request_envelope_tokens,
            request_capacity=capacity,
            generation_effective=generation,
            omitted_optional=tuple(omitted),
            guidance=tuple(guidance),
        )
