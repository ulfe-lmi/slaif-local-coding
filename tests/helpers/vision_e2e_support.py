"""Bounded repository-only support for the eventual Codex vision acceptance.

The helper owns disposable PNGs, a persistent disposable Codex home, and the
two-command ``exec``/``exec resume`` shape.  It returns fixed facts only.  It
never puts image bytes, prompts, tool output, source, credentials, or session
IDs in a result object.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
import subprocess
import tempfile
import zlib
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import httpx
from prometheus_client.parser import text_string_to_metric_families

from tests.helpers.e2e_support import (
    CODEX_MAX_DIAGNOSTIC_BYTES,
    CODEX_MAX_EVENT_BYTES,
    DEFAULT_MODEL,
    _ordinary_version,
    _sandbox_environment,
    write_governed_fixture,
    write_local_model_catalog,
)

VISION_MODEL = DEFAULT_MODEL
VISION_ROUTE = "qwen38-vision-codex"
VISION_CODEX_VERSION = "0.149.0"
VISION_TIMEOUT_SECONDS = 300.0
VISION_MAX_TOOL_CALLS = 4
VISION_MAX_MAIN_REQUESTS_PER_INVOCATION = VISION_MAX_TOOL_CALLS
VISION_FULL_LABEL = "full_scene"
VISION_CROP_LABEL = "right_crop"
VISION_REASON_LABELS = (
    "session_mismatch",
    "catalog_image_capability",
    "catalog_detail_original",
    "catalog_context_window",
    "catalog_parallel_tools",
    "turn1_exit",
    "turn1_timeout",
    "turn1_events",
    "turn1_tool",
    "turn1_exact_sentinel",
    "turn2_exit",
    "turn2_timeout",
    "turn2_events",
    "turn2_tool",
    "turn2_exact_sentinel",
    "metrics_missing",
    "metrics_scaled_mismatch",
    "outbound_phase_grouping",
    "outbound_request_invalid",
)

_CORE_REASON_LABELS = frozenset(
    label for label in VISION_REASON_LABELS if not label.startswith("outbound_")
)
_OUTBOUND_REASON_LABELS = frozenset(
    label for label in VISION_REASON_LABELS if label.startswith("outbound_")
)
_SAFE_EVENT_TYPES = ("thread.started", "item.completed")
_SAFE_IMAGE_TYPES = frozenset({"input_image", "image_url"})
_SAFE_OUTBOUND_LABELS = frozenset({VISION_FULL_LABEL, VISION_CROP_LABEL, "unexpected"})
_MAX_SAFE_IMAGE_BYTES = 8_388_608
_MAX_TOOL_DEFINITIONS = 16
_MAX_TOOL_SCAN_DEPTH = 32
_SUPPORTED_TOOL_DEFINITION_TYPES = frozenset({"function"})
_FINAL_BINDING_PROVENANCE = (
    "event_exact",
    "event_terminal_crlf",
    "file_exact",
    "file_terminal_crlf",
    "mismatch",
    "missing",
)

FinalBindingProvenance = Literal[
    "event_exact",
    "event_terminal_crlf",
    "file_exact",
    "file_terminal_crlf",
    "mismatch",
    "missing",
]


@dataclass(frozen=True)
class VisionImageFixture:
    """Safe identity facts for one synthetic image."""

    path: Path
    label: Literal["full_scene", "right_crop"]
    byte_length: int
    sha256: str


@dataclass(frozen=True)
class VisionFixturePaths:
    """All paths are caller-owned disposable state."""

    repository: Path
    codex_home: Path
    cache_root: Path
    codex_config: Path
    model_catalog: Path
    adapter_config: Path
    full_image: VisionImageFixture
    crop_image: VisionImageFixture
    api_key_env: str
    sentinel_token: str


@dataclass(frozen=True)
class VisionBoundaryEvidence:
    """Safe evidence from one actual request with a fixed invocation label."""

    endpoint: Literal["/v1/responses"]
    turn: Literal[1, 2]
    image_types: tuple[str, ...]
    outgoing_images_seen: int
    forwarded_labels: tuple[str, ...]
    forwarded_lengths: tuple[int | None, ...]
    forwarded_sha256: tuple[str | None, ...]
    exactly_one_expected_image: bool
    no_unexpected_image: bool
    expected_fixture_match: bool
    body_parsed: bool
    non_image_content_preserved: bool
    governance_content_preserved: bool
    tool_content_preserved: bool

    @property
    def accepted(self) -> bool:
        """Return whether this fact set meets the two-turn image contract."""
        return (
            self.endpoint == "/v1/responses"
            and self.turn in {1, 2}
            and self.image_types == ("input_image",)
            and self.outgoing_images_seen == 1
            and self.exactly_one_expected_image
            and self.no_unexpected_image
            and self.expected_fixture_match
            and self.body_parsed
            and self.non_image_content_preserved
            and self.governance_content_preserved
            and self.tool_content_preserved
        )


@dataclass(frozen=True)
class VisionMetricDeltas:
    """Per-invocation counters scaled to directly recorded request counts."""

    turn1_seen: int
    turn1_removed: int
    turn2_seen: int
    turn2_removed: int
    invocation_1_requests: int | None = None
    invocation_2_requests: int | None = None

    @property
    def exact(self) -> bool:
        if self.invocation_1_requests is None or self.invocation_2_requests is None:
            return False
        return self.exact_for(self.invocation_1_requests, self.invocation_2_requests)

    def exact_for(self, invocation_1_requests: int, invocation_2_requests: int) -> bool:
        """Validate image counters against the observed phase cardinalities."""
        return (
            1 <= invocation_1_requests <= VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
            and 1 <= invocation_2_requests <= VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
            and (self.turn1_seen, self.turn1_removed) == (invocation_1_requests, 0)
            and (self.turn2_seen, self.turn2_removed)
            == (2 * invocation_2_requests, invocation_2_requests)
        )


@dataclass(frozen=True)
class VisionTurnFacts:
    """Sanitized result of one bounded Codex invocation."""

    turn: Literal[1, 2]
    exit_status: int | None
    timed_out: bool
    event_bytes: int
    event_type_counts: Mapping[str, int]
    tool_calls: int
    sentinel_passed: bool
    response_success: bool
    resumed_command: bool
    normalized_argv: tuple[str, ...]
    event_final_message: FinalMessageEvidence = field(default_factory=lambda: _missing_message())
    file_final_message: FinalMessageEvidence = field(default_factory=lambda: _missing_message())
    final_binding_provenance: FinalBindingProvenance = "missing"


@dataclass(frozen=True)
class FinalMessageEvidence:
    """Bounded evidence for one final-message transport boundary."""

    present: bool
    byte_length: int
    sha256: str
    exact_expected: bool
    terminal_line_endings_only: bool
    non_whitespace_mismatch: bool

    @property
    def accepted(self) -> bool:
        return self.exact_expected or self.terminal_line_endings_only


def _missing_message() -> FinalMessageEvidence:
    return FinalMessageEvidence(
        present=False,
        byte_length=0,
        sha256=hashlib.sha256(b"").hexdigest(),
        exact_expected=False,
        terminal_line_endings_only=False,
        non_whitespace_mismatch=False,
    )


def _message_evidence(content: bytes | None, expected: str) -> FinalMessageEvidence:
    """Compare bounded bytes without retaining the message itself."""
    if content is None:
        return _missing_message()
    expected_bytes = expected.encode("utf-8")
    exact = content == expected_bytes
    terminal_only = (
        not exact
        and content.startswith(expected_bytes)
        and len(content) > len(expected_bytes)
        and all(byte in {10, 13} for byte in content[len(expected_bytes) :])
    )
    return FinalMessageEvidence(
        present=True,
        byte_length=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        exact_expected=exact,
        terminal_line_endings_only=terminal_only,
        non_whitespace_mismatch=not exact and not terminal_only,
    )


def _message_evidence_from_text(value: object, expected: str) -> FinalMessageEvidence:
    if not isinstance(value, str):
        return _missing_message()
    return _message_evidence(value.encode("utf-8"), expected)


def _final_binding_provenance(
    event: FinalMessageEvidence, output_file: FinalMessageEvidence
) -> FinalBindingProvenance:
    if event.exact_expected:
        return "event_exact"
    if event.terminal_line_endings_only:
        return "event_terminal_crlf"
    if output_file.exact_expected:
        return "file_exact"
    if output_file.terminal_line_endings_only:
        return "file_terminal_crlf"
    if not event.present and not output_file.present:
        return "missing"
    return "mismatch"


@dataclass(frozen=True)
class VisionSessionFacts:
    """Sanitized two-turn acceptance facts."""

    first: VisionTurnFacts
    second: VisionTurnFacts
    same_session: bool
    catalog_image_capability: bool
    catalog_detail_original_disabled: bool
    catalog_context_window: int | None
    catalog_parallel_tools_disabled: bool
    metric_deltas: VisionMetricDeltas | None
    outbound_facts: tuple[VisionBoundaryEvidence, ...] = ()

    @property
    def successful(self) -> bool:
        return _session_successful(self)

    @property
    def outbound_successful(self) -> bool:
        """Require every request in both ordered, recorder-backed phases."""
        return _outbound_successful(self)


def _session_successful(facts: VisionSessionFacts) -> bool:
    """Keep the original aggregate acceptance predicate in one place."""
    return (
        facts.same_session
        and facts.catalog_image_capability
        and facts.catalog_detail_original_disabled
        and facts.catalog_context_window == 100_000
        and facts.catalog_parallel_tools_disabled
        and facts.first.response_success
        and facts.second.response_success
        and facts.metric_deltas is not None
        and facts.metric_deltas.exact
    )


def _outbound_phase_grouping_successful(facts: VisionSessionFacts) -> bool:
    labels = tuple(fact.turn for fact in facts.outbound_facts)
    if not labels or 1 not in labels or 2 not in labels:
        return False
    first_second = labels.index(2)
    if any(label != 1 for label in labels[:first_second]) or any(
        label != 2 for label in labels[first_second:]
    ):
        return False
    first_count = first_second
    second_count = len(labels) - first_second
    return (
        1 <= first_count <= VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
        and 1 <= second_count <= VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
    )


def _outbound_successful(facts: VisionSessionFacts) -> bool:
    return _outbound_phase_grouping_successful(facts) and all(
        fact.accepted for fact in facts.outbound_facts
    )


def _append_turn_failure_reasons(
    reasons: set[str],
    turn: VisionTurnFacts,
    *,
    exit_label: str,
    timeout_label: str,
    events_label: str,
    tool_label: str,
    sentinel_label: str,
) -> None:
    """Decompose one existing response predicate without retaining response text."""
    if turn.response_success:
        return
    before = len(reasons)
    if turn.exit_status != 0:
        reasons.add(exit_label)
    if turn.timed_out:
        reasons.add(timeout_label)
    if turn.event_bytes <= 0:
        reasons.add(events_label)
    if turn.tool_calls < 1:
        reasons.add(tool_label)
    if not turn.sentinel_passed:
        reasons.add(sentinel_label)
    if len(reasons) == before:
        # A manually constructed fact may contain only an aggregate failure. Keep
        # the closed verdict non-empty without inventing a raw failure detail.
        reasons.add(events_label)


def vision_failure_reasons(facts: VisionSessionFacts) -> tuple[str, ...]:
    """Return the deterministic, privacy-safe field-level acceptance verdict."""
    reasons: set[str] = set()
    if not facts.same_session:
        reasons.add("session_mismatch")
    if not facts.catalog_image_capability:
        reasons.add("catalog_image_capability")
    if not facts.catalog_detail_original_disabled:
        reasons.add("catalog_detail_original")
    if facts.catalog_context_window != 100_000:
        reasons.add("catalog_context_window")
    if not facts.catalog_parallel_tools_disabled:
        reasons.add("catalog_parallel_tools")
    if not facts.first.response_success:
        _append_turn_failure_reasons(
            reasons,
            facts.first,
            exit_label="turn1_exit",
            timeout_label="turn1_timeout",
            events_label="turn1_events",
            tool_label="turn1_tool",
            sentinel_label="turn1_exact_sentinel",
        )
    if not facts.second.response_success:
        _append_turn_failure_reasons(
            reasons,
            facts.second,
            exit_label="turn2_exit",
            timeout_label="turn2_timeout",
            events_label="turn2_events",
            tool_label="turn2_tool",
            sentinel_label="turn2_exact_sentinel",
        )
    if facts.metric_deltas is None:
        reasons.add("metrics_missing")
    elif not facts.metric_deltas.exact:
        reasons.add("metrics_scaled_mismatch")
    if not _outbound_phase_grouping_successful(facts):
        reasons.add("outbound_phase_grouping")
    elif not all(fact.accepted for fact in facts.outbound_facts):
        reasons.add("outbound_request_invalid")
    return tuple(label for label in VISION_REASON_LABELS if label in reasons)


def _bounded_int(value: object, *, limit: int, allow_negative: bool = False) -> int | None:
    if type(value) is not int:
        return None
    lower = -limit if allow_negative else 0
    return value if lower <= value <= limit else None


def _safe_event_type_counts(counts: Mapping[str, int]) -> dict[str, int]:
    result = {
        event_type: _bounded_int(counts.get(event_type), limit=CODEX_MAX_EVENT_BYTES) or 0
        for event_type in _SAFE_EVENT_TYPES
    }
    other = 0
    for event_type, count in counts.items():
        if event_type in _SAFE_EVENT_TYPES:
            continue
        safe_count = _bounded_int(count, limit=CODEX_MAX_EVENT_BYTES)
        if safe_count is not None:
            other = min(CODEX_MAX_EVENT_BYTES, other + safe_count)
    result["other"] = other
    return result


def _safe_sha256(value: object) -> str | None:
    if not isinstance(value, str) or len(value) != 64:
        return None
    if any(character not in "0123456789abcdefABCDEF" for character in value):
        return None
    return value.lower()


def _safe_final_message_summary(evidence: FinalMessageEvidence) -> dict[str, object]:
    return {
        "present": bool(evidence.present),
        "byte_length": _bounded_int(evidence.byte_length, limit=CODEX_MAX_EVENT_BYTES + 1),
        "sha256": _safe_sha256(evidence.sha256),
        "exact_expected": bool(evidence.exact_expected),
        "terminal_line_endings_only": bool(evidence.terminal_line_endings_only),
        "non_whitespace_mismatch": bool(evidence.non_whitespace_mismatch),
    }


def _safe_turn_summary(turn: VisionTurnFacts) -> dict[str, object]:
    return {
        "turn": turn.turn if turn.turn in {1, 2} else None,
        "exit_status": _bounded_int(turn.exit_status, limit=255, allow_negative=True),
        "timed_out": bool(turn.timed_out),
        "event_bytes": _bounded_int(turn.event_bytes, limit=CODEX_MAX_EVENT_BYTES),
        "event_type_counts": _safe_event_type_counts(turn.event_type_counts),
        "tool_calls": _bounded_int(turn.tool_calls, limit=VISION_MAX_TOOL_CALLS),
        "sentinel_passed": bool(turn.sentinel_passed),
        "response_success": bool(turn.response_success),
        "resumed_command": bool(turn.resumed_command),
        "event_final_message": _safe_final_message_summary(turn.event_final_message),
        "file_final_message": _safe_final_message_summary(turn.file_final_message),
        "final_binding_provenance": (
            turn.final_binding_provenance
            if turn.final_binding_provenance in _FINAL_BINDING_PROVENANCE
            else "mismatch"
        ),
    }


def _safe_image_type(value: object) -> str:
    return value if isinstance(value, str) and value in _SAFE_IMAGE_TYPES else "unexpected"


def _safe_fixture_label(value: object) -> str:
    return value if isinstance(value, str) and value in _SAFE_OUTBOUND_LABELS else "unexpected"


def _safe_outbound_summary(fact: VisionBoundaryEvidence) -> dict[str, object]:
    limit = VISION_MAX_MAIN_REQUESTS_PER_INVOCATION + 1
    return {
        "turn": fact.turn if fact.turn in {1, 2} else None,
        "accepted": bool(fact.accepted),
        "image_types": tuple(_safe_image_type(item) for item in fact.image_types[:limit]),
        "images_seen": _bounded_int(
            fact.outgoing_images_seen, limit=VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
        ),
        "forwarded_labels": tuple(
            _safe_fixture_label(item) for item in fact.forwarded_labels[:limit]
        ),
        "forwarded_lengths": tuple(
            _bounded_int(item, limit=_MAX_SAFE_IMAGE_BYTES)
            for item in fact.forwarded_lengths[:limit]
        ),
        "forwarded_sha256": tuple(_safe_sha256(item) for item in fact.forwarded_sha256[:limit]),
        "expected_fixture_match": bool(fact.expected_fixture_match),
        "body_parsed": bool(fact.body_parsed),
        "non_image_content_preserved": bool(fact.non_image_content_preserved),
        "governance_content_preserved": bool(fact.governance_content_preserved),
        "tool_content_preserved": bool(fact.tool_content_preserved),
    }


def vision_diagnostic_summary(facts: VisionSessionFacts) -> dict[str, object]:
    """Serialize only bounded, fixed-shape facts suitable for failure output."""
    metric_deltas = facts.metric_deltas
    metrics: dict[str, object] | None = None
    if metric_deltas is not None:
        metrics = {
            "turn1_seen": _bounded_int(
                metric_deltas.turn1_seen,
                limit=2 * VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
                allow_negative=True,
            ),
            "turn1_removed": _bounded_int(
                metric_deltas.turn1_removed,
                limit=2 * VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
                allow_negative=True,
            ),
            "turn2_seen": _bounded_int(
                metric_deltas.turn2_seen,
                limit=2 * VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
                allow_negative=True,
            ),
            "turn2_removed": _bounded_int(
                metric_deltas.turn2_removed,
                limit=2 * VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
                allow_negative=True,
            ),
            "invocation_1_requests": _bounded_int(
                metric_deltas.invocation_1_requests,
                limit=VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
            ),
            "invocation_2_requests": _bounded_int(
                metric_deltas.invocation_2_requests,
                limit=VISION_MAX_MAIN_REQUESTS_PER_INVOCATION,
            ),
            "exact": bool(metric_deltas.exact),
        }
    phase_counts = (
        tuple(
            _bounded_int(count, limit=VISION_MAX_MAIN_REQUESTS_PER_INVOCATION)
            for count in (
                len(tuple(fact for fact in facts.outbound_facts if fact.turn == 1)),
                len(tuple(fact for fact in facts.outbound_facts if fact.turn == 2)),
            )
        )
        if facts.outbound_facts
        else None
    )
    return {
        "reasons": vision_failure_reasons(facts),
        "session_matches": bool(facts.same_session),
        "catalog_image_capability": bool(facts.catalog_image_capability),
        "catalog_detail_original_disabled": bool(facts.catalog_detail_original_disabled),
        "catalog_context_window": _bounded_int(facts.catalog_context_window, limit=1_000_000),
        "catalog_parallel_tools_disabled": bool(facts.catalog_parallel_tools_disabled),
        "turns": (_safe_turn_summary(facts.first), _safe_turn_summary(facts.second)),
        "metrics": metrics,
        "phase_counts": phase_counts,
        "outbound": tuple(_safe_outbound_summary(fact) for fact in facts.outbound_facts),
    }


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _rgb_png(rows: tuple[tuple[tuple[int, int, int], ...], ...]) -> bytes:
    """Encode tiny deterministic RGB fixtures without image dependencies."""
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("PNG fixture must have a rectangular non-empty pixel grid")
    width = len(rows[0])
    height = len(rows)
    raw = b"".join(b"\x00" + b"".join(bytes(pixel) for pixel in row) for row in rows)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw, level=9))
        + _png_chunk(b"IEND", b"")
    )


def _image_fixture(
    path: Path, label: Literal["full_scene", "right_crop"], data: bytes
) -> VisionImageFixture:
    path.write_bytes(data)
    os.chmod(path, 0o600)
    return VisionImageFixture(path, label, len(data), hashlib.sha256(data).hexdigest())


def _quoted(value: str | Path) -> str:
    return json.dumps(str(value))


def write_vision_fixture(root: Path, base_url: str, api_key_env: str) -> VisionFixturePaths:
    """Create the exact disposable repository/config/image fixture for vision."""
    base = write_governed_fixture(root, base_url, api_key_env)
    dependency_path = base.repository / "GOVERNANCE-DEPENDENCY.md"
    dependency_path.write_text(
        dependency_path.read_text(encoding="utf-8")
        + "\nAfter a stateless new-context request, the assistant MUST reply with exactly "
        f"SENTINEL-ACK:{base.sentinel_token} and nothing else.\n",
        encoding="utf-8",
    )
    os.chmod(dependency_path, 0o600)
    image_dir = root / "images"
    image_dir.mkdir(mode=0o700)

    full = _rgb_png(
        (
            ((220, 62, 62), (220, 62, 62), (55, 112, 220), (55, 112, 220)),
            ((220, 62, 62), (220, 62, 62), (55, 112, 220), (55, 112, 220)),
        )
    )
    crop = _rgb_png(
        (
            ((55, 112, 220), (55, 112, 220)),
            ((55, 112, 220), (55, 112, 220)),
        )
    )
    full_fixture = _image_fixture(image_dir / "full.png", "full_scene", full)
    crop_fixture = _image_fixture(image_dir / "crop.png", "right_crop", crop)

    adapter_config = root / "adapter-vision.toml"
    fallback_cache = root / "adapter-cache-fallback"
    config = (
        "[server]\n"
        'listen_host = "127.0.0.1"\n'
        "listen_port = 18031\n"
        "request_body_max_bytes = 67108864\n"
        "response_body_max_bytes = 67108864\n"
        "json_max_nesting_depth = 128\n\n"
        "[upstream]\n"
        f"base_url = {_quoted('http://127.0.0.1:18020/v1')}\n"
        f"api_key_env = {_quoted(api_key_env)}\n"
        f"model = {_quoted(VISION_MODEL)}\n"
        "connect_timeout_seconds = 10\nrequest_timeout_seconds = 300\n"
        "write_timeout_seconds = 30\npool_timeout_seconds = 10\n\n"
        "[compiler]\n"
        'enabled = true\nreasoning_effort = "low"\n'
        "timeout_seconds = 120\nmax_attempts = 2\nmax_output_tokens = 3000\n"
        "max_parallel_calls = 1\nmax_source_bytes = 262144\n"
        "max_candidates = 128\nmax_json_depth = 24\n\n"
        "[cache]\n"
        'backend = "filesystem"\n'
        f"root = {_quoted(base.cache_root)}\n"
        f"fallback_root = {_quoted(fallback_cache)}\n"
        "max_total_bytes = 67108864\nmax_entry_bytes = 65536\n"
        "max_pinned_bytes = 8388608\nmax_entries = 4096\n"
        "ttl_seconds = 604800\nmax_scan_entries = 4096\n\n"
        "[constitution]\n"
        'enabled = true\nprincipal = "vision-e2e-principal"\n'
        'session = "vision-e2e-session"\nrepository = "vision-e2e-repository"\n'
        "max_injected_bytes = 16384\ncandidate_max_count = 128\n"
        'compile_failure_policy = "preserve_original"\n'
        'selector_schema_version = "working-set-v1"\n'
        'render_version = "constitution-render-v1"\n'
        'working_set_policy_version = "foundation-v1"\n'
        "working_set_max_entries = 128\nacquisition_max_count = 128\n"
        "max_dependency_acquisitions = 4\nentry_render_max_bytes = 8192\n"
        "injection_max_depth = 64\ninjection_max_nodes = 16384\n\n"
        "[observation]\n"
        'schema_version = "observation-v1"\npolicy_version = "references-v1"\n'
        "max_roots = 8\nmax_source_bytes = 262144\nmax_candidates = 128\n"
        "max_evidence_per_candidate = 16\nmax_total_evidence = 1024\nmax_path_bytes = 512\n\n"
        "[[routes]]\n"
        f"name = {_quoted(VISION_ROUTE)}\nmodel = {_quoted(VISION_MODEL)}\n"
        'max_images_per_request = 1\nimage_overflow_policy = "retain_newest"\n'
        "enable_responses = true\nenable_chat_completions = true\n"
        "observation_enabled = true\nconstitution_enabled = true\n\n"
        '[observability]\nlog_level = "INFO"\nlog_raw_payloads = false\n'
        'metrics_enabled = true\nmetrics_host = "127.0.0.1"\n'
    )
    adapter_config.write_text(config, encoding="utf-8")
    os.chmod(adapter_config, 0o600)
    return VisionFixturePaths(
        repository=base.repository,
        codex_home=base.codex_home,
        cache_root=base.cache_root,
        codex_config=base.codex_config,
        model_catalog=base.model_catalog,
        adapter_config=adapter_config,
        full_image=full_fixture,
        crop_image=crop_fixture,
        api_key_env=api_key_env,
        sentinel_token=base.sentinel_token,
    )


def write_vision_model_catalog(
    codex_bin: Path | str, destination: Path, *, model: str = VISION_MODEL
) -> None:
    """Derive the installed catalog schema and apply the exact vision fixture contract."""
    write_local_model_catalog(codex_bin, destination, model=model)
    document = json.loads(destination.read_text(encoding="utf-8"))
    models = document.get("models")
    selected = next((item for item in models if item.get("slug") == model), None)
    if not isinstance(selected, dict):
        raise RuntimeError("vision_model_catalog_model_missing")
    selected.update(
        {
            "input_modalities": ["text", "image"],
            "supports_image_detail_original": False,
            "context_window": 100_000,
            "max_context_window": 100_000,
            "supports_parallel_tool_calls": False,
        }
    )
    destination.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    os.chmod(destination, 0o600)


def vision_subprocess_environment(fixture: VisionFixturePaths) -> dict[str, str]:
    """Return the allowlisted environment for a disposable Codex/candidate process."""
    return _sandbox_environment(fixture.codex_home, fixture.api_key_env)


def _catalog_facts(path: Path) -> tuple[bool, bool, int | None, bool]:
    document = json.loads(path.read_text(encoding="utf-8"))
    models = document.get("models")
    selected = next((item for item in models if item.get("slug") == VISION_MODEL), None)
    if not isinstance(selected, dict):
        return False, False, None, False
    modalities = selected.get("input_modalities")
    return (
        isinstance(modalities, list) and modalities == ["text", "image"],
        selected.get("supports_image_detail_original") is False,
        selected.get("context_window") if isinstance(selected.get("context_window"), int) else None,
        selected.get("supports_parallel_tool_calls") is False,
    )


def _data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


@dataclass(frozen=True)
class _ImageObservation:
    item_type: str
    url: str | None
    supported_shape: bool


def _image_items(value: object) -> list[_ImageObservation]:
    found: list[_ImageObservation] = []

    def visit(node: object) -> None:
        if isinstance(node, list):
            for item in node:
                visit(item)
            return
        if not isinstance(node, dict):
            return
        marker = node.get("type")
        if isinstance(marker, str) and (
            marker in {"input_image", "image_url", "image"} or marker.endswith("_image")
        ):
            if marker == "input_image" and isinstance(node.get("image_url"), str):
                found.append(_ImageObservation(marker, node["image_url"], True))
            elif marker == "image_url" and isinstance(node.get("image_url"), dict):
                url = node["image_url"].get("url")
                found.append(_ImageObservation(marker, url if isinstance(url, str) else None, True))
            else:
                found.append(_ImageObservation(marker, None, False))
        for child in node.values():
            visit(child)

    visit(value)
    return found


def _without_images(value: object) -> object:
    if isinstance(value, list):
        result: list[object] = []
        for item in value:
            if isinstance(item, dict) and item.get("type") in {"input_image", "image_url"}:
                continue
            result.append(_without_images(item))
        return result
    if isinstance(value, dict):
        return {key: _without_images(child) for key, child in value.items()}
    return value


def _has_tool_definitions(value: object) -> bool:
    """Recognize only a bounded, top-level list of supported definitions."""
    if not isinstance(value, list) or not value or len(value) > _MAX_TOOL_DEFINITIONS:
        return False
    return all(
        isinstance(item, dict) and item.get("type") in _SUPPORTED_TOOL_DEFINITION_TYPES
        for item in value
    )


def _has_tool_item(value: object, *, depth: int, budget: list[int]) -> bool:
    if depth > _MAX_TOOL_SCAN_DEPTH or budget[0] <= 0:
        return False
    budget[0] -= 1
    if isinstance(value, list):
        return any(_has_tool_item(item, depth=depth + 1, budget=budget) for item in value)
    if not isinstance(value, dict):
        return False
    if value.get("type") in {"function_call", "function_call_output", "exec_command"}:
        return True
    return any(
        _has_tool_item(child, depth=depth + 1, budget=budget)
        for key, child in value.items()
        if key != "tools"
    )


def _has_tool_content(value: object) -> bool:
    if not isinstance(value, dict):
        return _has_tool_item(value, depth=0, budget=[_MAX_TOOL_DEFINITIONS])
    return _has_tool_definitions(value.get("tools")) or _has_tool_item(
        value, depth=0, budget=[_MAX_TOOL_DEFINITIONS]
    )


def _content_fingerprint(value: object) -> str:
    canonical = json.dumps(
        _without_images(value), ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _governance_content_present(value: object) -> bool:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True)
    return "GOVERNANCE-DEPENDENCY.md" in encoded and "FINAL_RESPONSE_EXACTLY" in encoded


def _safe_image_identity(url: str | None) -> tuple[int, str] | None:
    """Return only fixture-comparable facts; never retain an image or data URL."""
    if url is None or not url.startswith("data:image/png;base64,") or len(url) > 8_388_608:
        return None
    try:
        image_bytes = base64.b64decode(url.removeprefix("data:image/png;base64,"), validate=True)
    except (ValueError, UnicodeError):
        return None
    return len(image_bytes), hashlib.sha256(image_bytes).hexdigest()


@dataclass(frozen=True)
class _ExpectedPreservation:
    content_sha256: str
    governance: bool
    tool: bool


class VisionOutboundRecorder(httpx.AsyncBaseTransport):
    """Acceptance-only transport recorder for the real adapter boundary.

    The wrapper observes the request passed by ``create_app`` to HTTPX, records
    safe facts, and passes the same request object to the configured transport.
    It deliberately ignores compiler ``/v1/chat/completions`` requests.
    """

    def __init__(self, fixture: VisionFixturePaths, upstream: httpx.AsyncBaseTransport) -> None:
        self._fixture = fixture
        self._upstream = upstream
        self._facts: list[VisionBoundaryEvidence] = []
        self._phase_facts: dict[int, tuple[VisionBoundaryEvidence, ...]] = {}
        self._active_turn: Literal[1, 2] | None = None
        self._next_turn: Literal[1, 2] | None = 1
        self._phase_error: str | None = None
        self._expected: dict[int, list[_ExpectedPreservation]] = {}

    @property
    def facts(self) -> tuple[VisionBoundaryEvidence, ...]:
        return tuple(self._facts)

    @property
    def phase_counts(self) -> tuple[int, int] | None:
        """Return counts only after both explicitly ordered phases are complete."""
        first = self._phase_facts.get(1)
        second = self._phase_facts.get(2)
        if first is None or second is None:
            return None
        return len(first), len(second)

    def phase_facts(self, turn: Literal[1, 2]) -> tuple[VisionBoundaryEvidence, ...]:
        """Return the immutable facts for one completed invocation phase."""
        return self._phase_facts.get(turn, ())

    def begin_phase(self, turn: Literal[1, 2]) -> None:
        """Open one bounded, ordered phase around one Codex subprocess."""
        if self._phase_error is not None:
            raise ValueError(self._phase_error)
        if self._active_turn is not None:
            raise ValueError("vision_phase_overlap")
        if self._next_turn != turn:
            raise ValueError("vision_phase_reordered")
        if turn in self._phase_facts:
            raise ValueError("vision_phase_repeated")
        self._active_turn = turn

    def end_phase(self, turn: Literal[1, 2]) -> tuple[VisionBoundaryEvidence, ...]:
        """Close a phase and reject empty, invalid, or unbounded attribution."""
        if self._active_turn != turn:
            raise ValueError("vision_phase_not_active")
        if self._phase_error is not None:
            self._active_turn = None
            raise ValueError(self._phase_error)
        facts = tuple(fact for fact in self._facts if fact.turn == turn)
        if not facts:
            self._active_turn = None
            raise ValueError("vision_phase_empty")
        if len(facts) > VISION_MAX_MAIN_REQUESTS_PER_INVOCATION:
            self._active_turn = None
            raise ValueError("vision_phase_request_bound_exceeded")
        expected = self._expected.get(turn, [])
        if expected and len(expected) != len(facts):
            self._active_turn = None
            raise ValueError("vision_phase_preservation_oracle_mismatch")
        self._phase_facts[turn] = facts
        self._active_turn = None
        self._next_turn = 2 if turn == 1 else None
        return facts

    @contextmanager
    def phase(self, turn: Literal[1, 2]) -> Iterator[tuple[VisionBoundaryEvidence, ...]]:
        """Context-manager form of the explicit invocation phase API."""
        self.begin_phase(turn)
        try:
            yield self._phase_facts.get(turn, ())
        finally:
            self.end_phase(turn)

    def expect_preserved_content(self, turn: Literal[1, 2], payload: Mapping[str, Any]) -> None:
        """Register only a safe oracle for focused fake-upstream assertions."""
        self._expected.setdefault(turn, []).append(
            _ExpectedPreservation(
                content_sha256=_content_fingerprint(payload),
                governance=_governance_content_present(payload),
                tool=_has_tool_content(payload),
            )
        )

    def _fact_from_body(
        self, turn: Literal[1, 2], body: bytes, request_index: int
    ) -> VisionBoundaryEvidence:
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            return VisionBoundaryEvidence(
                endpoint="/v1/responses",
                turn=turn,
                image_types=(),
                outgoing_images_seen=0,
                forwarded_labels=(),
                forwarded_lengths=(),
                forwarded_sha256=(),
                exactly_one_expected_image=False,
                no_unexpected_image=False,
                expected_fixture_match=False,
                body_parsed=False,
                non_image_content_preserved=False,
                governance_content_preserved=False,
                tool_content_preserved=False,
            )

        images = _image_items(payload)
        expected = {1: self._fixture.full_image, 2: self._fixture.crop_image}.get(turn)
        expected_identity = (
            (expected.byte_length, expected.sha256) if expected is not None else None
        )
        known_identities = {
            (
                self._fixture.full_image.byte_length,
                self._fixture.full_image.sha256,
            ): self._fixture.full_image,
            (
                self._fixture.crop_image.byte_length,
                self._fixture.crop_image.sha256,
            ): self._fixture.crop_image,
        }
        labels: list[str] = []
        lengths: list[int | None] = []
        hashes: list[str | None] = []
        unexpected = False
        for image in images:
            identity = _safe_image_identity(image.url) if image.supported_shape else None
            fixture_image = known_identities.get(identity) if identity is not None else None
            if image.item_type != "input_image" or fixture_image is None:
                unexpected = True
                labels.append("unexpected")
                lengths.append(None)
                hashes.append(None)
            else:
                labels.append(fixture_image.label)
                lengths.append(fixture_image.byte_length)
                hashes.append(fixture_image.sha256)
        expected_match = (
            len(images) == 1
            and not unexpected
            and _safe_image_identity(images[0].url) == expected_identity
        )
        expected_values = self._expected.get(turn, [])
        expected_preservation = (
            expected_values[request_index] if request_index < len(expected_values) else None
        )
        if expected_preservation is None:
            non_image_preserved = bool(_without_images(payload))
            governance_preserved = _governance_content_present(payload)
            tool_preserved = _has_tool_content(payload)
        else:
            non_image_preserved = (
                _content_fingerprint(payload) == expected_preservation.content_sha256
            )
            governance_preserved = expected_preservation.governance and _governance_content_present(
                payload
            )
            tool_preserved = expected_preservation.tool and _has_tool_content(payload)
        return VisionBoundaryEvidence(
            endpoint="/v1/responses",
            turn=turn,
            image_types=tuple(image.item_type for image in images),
            outgoing_images_seen=len(images),
            forwarded_labels=tuple(labels),
            forwarded_lengths=tuple(lengths),
            forwarded_sha256=tuple(hashes),
            exactly_one_expected_image=len(images) == 1 and not unexpected,
            no_unexpected_image=not unexpected,
            expected_fixture_match=expected_match,
            body_parsed=True,
            non_image_content_preserved=non_image_preserved,
            governance_content_preserved=governance_preserved,
            tool_content_preserved=tool_preserved,
        )

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/responses":
            if self._active_turn is None:
                self._phase_error = "vision_main_request_outside_phase"
                raise ValueError(self._phase_error)
            current_facts = [fact for fact in self._facts if fact.turn == self._active_turn]
            if len(current_facts) >= VISION_MAX_MAIN_REQUESTS_PER_INVOCATION:
                self._phase_error = "vision_phase_request_bound_exceeded"
                raise ValueError(self._phase_error)
            body = await request.aread()
            self._facts.append(self._fact_from_body(self._active_turn, body, len(current_facts)))
        return await self._upstream.handle_async_request(request)

    async def aclose(self) -> None:
        await self._upstream.aclose()


def image_metric_snapshot(metrics_text: str, *, route: str = VISION_ROUTE) -> tuple[int, int]:
    """Read only cumulative seen/removed image counters for the configured route."""
    values = {"seen": 0, "removed": 0}
    for family in text_string_to_metric_families(metrics_text):
        for sample in family.samples:
            if sample.name != "slaif_image_items_total" or sample.labels.get("route") != route:
                continue
            result = sample.labels.get("result")
            if result in values:
                values[result] += int(sample.value)
    return values["seen"], values["removed"]


def vision_metric_deltas(
    before: str,
    between: str,
    after: str,
    *,
    phase_counts: tuple[int, int] | None = None,
    route: str = VISION_ROUTE,
) -> VisionMetricDeltas:
    first_before = image_metric_snapshot(before, route=route)
    first_between = image_metric_snapshot(between, route=route)
    second_after = image_metric_snapshot(after, route=route)
    return VisionMetricDeltas(
        turn1_seen=first_between[0] - first_before[0],
        turn1_removed=first_between[1] - first_before[1],
        turn2_seen=second_after[0] - first_between[0],
        turn2_removed=second_after[1] - first_between[1],
        invocation_1_requests=phase_counts[0] if phase_counts is not None else None,
        invocation_2_requests=phase_counts[1] if phase_counts is not None else None,
    )


def _normalized_argv(
    argv: Iterable[str], fixture: VisionFixturePaths, *, turn: Literal[1, 2]
) -> tuple[str, ...]:
    argv_values = tuple(argv)
    replacements = {
        argv_values[0]: "<codex>",
        str(fixture.codex_home): "<codex-home>",
        str(fixture.repository): "<fixture>",
        str(fixture.full_image.path): "<full-image>",
        str(fixture.crop_image.path): "<crop-image>",
    }
    result: list[str] = []
    for item in argv_values:
        if item in replacements:
            result.append(replacements[item])
        elif item.startswith(str(fixture.repository)):
            result.append("<fixture-file>")
        elif item.startswith(str(fixture.codex_home)):
            result.append("<codex-home-file>")
        elif item == "<vision-prompt>":
            result.append(item)
        else:
            result.append(item)
    if turn == 2 and "resume" not in result:
        raise ValueError("vision resume argv missing resume subcommand")
    return tuple(result)


def _vision_prompt(turn: Literal[1, 2]) -> str:
    subject = "the full scene" if turn == 1 else "the newest right-side crop"
    return (
        f"Inspect {subject} in the attached image. Use the ordinary shell command tool "
        "exactly once with cat GOVERNANCE-DEPENDENCY.md and wait for its result. "
        "Then follow the delegated dependency's FINAL_RESPONSE_EXACTLY instruction literally."
    )


def _parse_vision_events(
    stream: Iterable[bytes], *, expected: str
) -> tuple[int, Counter[str], int, str | None, FinalMessageEvidence]:
    event_bytes = 0
    event_types: Counter[str] = Counter()
    tool_calls = 0
    thread_id: str | None = None
    final_message = _missing_message()
    for raw_line in stream:
        event_bytes += len(raw_line)
        if event_bytes > CODEX_MAX_EVENT_BYTES:
            raise OverflowError("vision event stream exceeded bound")
        try:
            event = json.loads(raw_line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if isinstance(event_type, str):
            event_types[event_type] += 1
        if event_type == "thread.started" and isinstance(event.get("thread_id"), str):
            thread_id = event["thread_id"]
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"command_execution", "function_call", "exec_command"}:
            tool_calls += 1
        if event_type == "item.completed" and item.get("type") == "agent_message":
            final_message = _message_evidence_from_text(item.get("text"), expected)
    return event_bytes, event_types, tool_calls, thread_id, final_message


def _file_final_message_evidence(path: Path, expected: str) -> FinalMessageEvidence:
    """Validate the bounded output file without retaining its sensitive text."""
    try:
        with path.open("rb") as handle:
            content = handle.read(CODEX_MAX_EVENT_BYTES + 1)
    except OSError:
        return _missing_message()
    return _message_evidence(content, expected)


def _exact_final_message(path: Path, expected: str) -> bool:
    """Backward-compatible boolean view of the bounded file evidence."""
    return _file_final_message_evidence(path, expected).accepted


def _run_vision_turn(
    codex_bin: Path | str,
    fixture: VisionFixturePaths,
    *,
    turn: Literal[1, 2],
    timeout_seconds: float,
) -> tuple[VisionTurnFacts, str | None]:
    output_path = fixture.repository / f".vision-last-message-{turn}.tmp"
    if turn == 1:
        argv = [
            str(codex_bin),
            "--dangerously-bypass-approvals-and-sandbox",
            "exec",
            "--json",
            "--strict-config",
            "--cd",
            str(fixture.repository),
            "--image",
            str(fixture.full_image.path),
            "--output-last-message",
            str(output_path),
            "<vision-prompt>",
        ]
    else:
        argv = [
            str(codex_bin),
            "--dangerously-bypass-approvals-and-sandbox",
            "exec",
            "resume",
            "--last",
            "--json",
            "--strict-config",
            "--image",
            str(fixture.crop_image.path),
            "--output-last-message",
            str(output_path),
            "<vision-prompt>",
        ]
    environment = _sandbox_environment(fixture.codex_home, fixture.api_key_env)
    event_types: Counter[str] = Counter()
    event_bytes = 0
    tool_calls = 0
    event_final_message = _missing_message()
    file_final_message = _missing_message()
    thread_id: str | None = None
    exit_status: int | None = None
    timed_out = False
    try:
        with (
            tempfile.TemporaryFile(dir=fixture.codex_home) as events,
            tempfile.TemporaryFile(dir=fixture.codex_home) as diagnostics,
        ):
            process = subprocess.Popen(
                [item if item != "<vision-prompt>" else _vision_prompt(turn) for item in argv],
                cwd=fixture.repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=events,
                stderr=diagnostics,
            )
            try:
                exit_status = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                timed_out = True
            diagnostics.seek(0, os.SEEK_END)
            if diagnostics.tell() > CODEX_MAX_DIAGNOSTIC_BYTES:
                raise OverflowError("vision diagnostics exceeded bound")
            events.seek(0)
            (
                event_bytes,
                event_types,
                tool_calls,
                thread_id,
                event_final_message,
            ) = _parse_vision_events(
                iter(events.readline, b""),
                expected=f"SENTINEL-ACK:{fixture.sentinel_token}",
            )
            file_final_message = _file_final_message_evidence(
                output_path, f"SENTINEL-ACK:{fixture.sentinel_token}"
            )
    except (OSError, OverflowError, subprocess.SubprocessError):
        exit_status = None
    finally:
        try:
            output_path.unlink()
        except OSError:
            pass
    final_binding_provenance = _final_binding_provenance(event_final_message, file_final_message)
    sentinel = event_final_message.accepted or file_final_message.accepted
    response_success = (
        exit_status == 0 and not timed_out and event_bytes > 0 and tool_calls >= 1 and sentinel
    )
    facts = VisionTurnFacts(
        turn=turn,
        exit_status=exit_status,
        timed_out=timed_out,
        event_bytes=event_bytes,
        event_type_counts=dict(event_types),
        tool_calls=tool_calls,
        sentinel_passed=sentinel,
        response_success=response_success,
        resumed_command=turn == 2,
        normalized_argv=_normalized_argv(
            [item if item != "<vision-prompt>" else "<vision-prompt>" for item in argv],
            fixture,
            turn=turn,
        ),
        event_final_message=event_final_message,
        file_final_message=file_final_message,
        final_binding_provenance=final_binding_provenance,
    )
    return facts, thread_id


def run_vision_e2e(
    codex_bin: Path | str,
    fixture: VisionFixturePaths,
    *,
    metrics_sampler: Callable[[], str] | None = None,
    outbound_recorder: VisionOutboundRecorder | None = None,
    timeout_seconds: float = VISION_TIMEOUT_SECONDS,
) -> VisionSessionFacts:
    """Run exactly one initial image turn and one same-session crop resume."""
    if timeout_seconds <= 0 or timeout_seconds > VISION_TIMEOUT_SECONDS:
        raise ValueError("invalid vision timeout")
    version = _ordinary_version(codex_bin, _sandbox_environment(fixture.codex_home))
    if version != VISION_CODEX_VERSION:
        raise RuntimeError("unsupported_codex_version")
    catalog_facts = _catalog_facts(fixture.model_catalog)
    before = metrics_sampler() if metrics_sampler is not None else None
    if outbound_recorder is not None:
        outbound_recorder.begin_phase(1)
    try:
        first, first_thread = _run_vision_turn(
            codex_bin, fixture, turn=1, timeout_seconds=timeout_seconds
        )
    finally:
        if outbound_recorder is not None:
            outbound_recorder.end_phase(1)
    between = metrics_sampler() if metrics_sampler is not None else None
    if outbound_recorder is not None:
        outbound_recorder.begin_phase(2)
    try:
        second, second_thread = _run_vision_turn(
            codex_bin, fixture, turn=2, timeout_seconds=timeout_seconds
        )
    finally:
        if outbound_recorder is not None:
            outbound_recorder.end_phase(2)
    after = metrics_sampler() if metrics_sampler is not None else None
    phase_counts = outbound_recorder.phase_counts if outbound_recorder is not None else None
    metric_deltas = (
        vision_metric_deltas(before, between, after, phase_counts=phase_counts)
        if before is not None and between is not None and after is not None
        else None
    )
    same_session = (
        first_thread is not None and second_thread is not None and second_thread == first_thread
    )
    return VisionSessionFacts(
        first=first,
        second=second,
        same_session=same_session,
        catalog_image_capability=catalog_facts[0],
        catalog_detail_original_disabled=catalog_facts[1],
        catalog_context_window=catalog_facts[2],
        catalog_parallel_tools_disabled=catalog_facts[3],
        metric_deltas=metric_deltas,
        outbound_facts=outbound_recorder.facts if outbound_recorder is not None else (),
    )
