"""Inert pure observation stage for the dependency-bundle cache rework.

This package implements the bounded pure-observation slice (D01-D09) of
Objective 017: versioned root-envelope, literal shell-read, finite
read-plan (D06/D07/D08) and literal-loop (D07) observation, tool-
result pairing with exact source spans and typed limitations, and the
D09 native process/chunk collector (``process-chunk/v2`` over the
pinned ``codex-native-exec-wrapper/v1`` grammar; running chains and
already-exited single-final frames).  It is deliberately
**not** wired into the legacy request execution path, the graph/cache/
compiler, or any runtime stage; see
``docs/CACHE-OBSERVATION-CONTRACT.md``.
"""

from __future__ import annotations

from ..bundles.client_paths import normalize_read_path, validate_workspace
from ..bundles.compound_reads import (
    READ_PLAN_GRAMMAR,
    PlanStatement,
    PlanStatementKind,
    ReadPlanParse,
    parse_read_plan,
    plan_source_region,
)
from ..bundles.literal_loops import (
    LOOP_GRAMMAR,
    LoopOperand,
    LoopParse,
    LoopStatement,
    LoopStatementKind,
    parse_literal_loop,
)
from ..bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    ENVELOPE_FORMAT,
    NATIVE_TOOL_WRAPPER_FORMAT,
    OBSERVER_VERSION,
    PRIVATE_ID_PLACEHOLDER,
    PROCESS_CHUNK_GRAMMAR,
    READ_GRAMMAR,
    TOOL_WRAPPER_FORMAT,
    CharSpan,
    FinalCatEvidence,
    Limitation,
    NativeWrapperFacts,
    NormalizedPath,
    ObservationBounds,
    ObservationReport,
    OccurrenceKind,
    PathContext,
    PathForm,
    ProcessObservation,
    ProcessOutcome,
    ProcessPiece,
    ProcessPoll,
    ReadCommandParse,
    ReadObservation,
    ReadOutcome,
    RootOccurrence,
    RootScanResult,
    RootStatus,
    UnpairedRecord,
    VersionCandidate,
    WrapperFacts,
    canonical_payload_fingerprint,
    contains_lone_surrogates,
    sha256_hex,
    utf8_byte_span,
)
from ..bundles.observe import (
    ENDPOINT_CHAT,
    ENDPOINT_MIXED,
    ENDPOINT_RESPONSES,
    ENDPOINT_UNKNOWN,
    observe_request,
    select_endpoint,
)
from ..bundles.process_chunks import observe_processes, parse_native_wrapper
from ..bundles.read_grammar import (
    UnwrappedCommand,
    parse_read_command,
    raw_argument_bound,
    tokenize_literal,
    unwrap_call_arguments,
    unwrap_supported_arguments,
)
from ..bundles.root_envelopes import scan_root_envelopes
from ..bundles.shell_tokens import LiteralToken, tokenize_command
from ..bundles.tool_results import observe_reads, parse_wrapper

__all__ = [
    "EMPTY_SOURCE_SHA256",
    "FinalCatEvidence",
    "ENVELOPE_FORMAT",
    "LOOP_GRAMMAR",
    "NATIVE_TOOL_WRAPPER_FORMAT",
    "OBSERVER_VERSION",
    "PROCESS_CHUNK_GRAMMAR",
    "READ_GRAMMAR",
    "TOOL_WRAPPER_FORMAT",
    "LoopOperand",
    "LoopParse",
    "LoopStatement",
    "LoopStatementKind",
    "parse_literal_loop",
    "CharSpan",
    "Limitation",
    "NativeWrapperFacts",
    "NormalizedPath",
    "ObservationBounds",
    "ObservationReport",
    "OccurrenceKind",
    "ProcessObservation",
    "ProcessOutcome",
    "ProcessPiece",
    "ProcessPoll",
    "ENDPOINT_CHAT",
    "ENDPOINT_MIXED",
    "ENDPOINT_RESPONSES",
    "ENDPOINT_UNKNOWN",
    "LiteralToken",
    "READ_PLAN_GRAMMAR",
    "PlanStatement",
    "PlanStatementKind",
    "ReadPlanParse",
    "parse_read_plan",
    "plan_source_region",
    "PathContext",
    "PathForm",
    "PRIVATE_ID_PLACEHOLDER",
    "ReadCommandParse",
    "ReadObservation",
    "ReadOutcome",
    "RootOccurrence",
    "RootScanResult",
    "RootStatus",
    "UnpairedRecord",
    "UnwrappedCommand",
    "VersionCandidate",
    "WrapperFacts",
    "canonical_payload_fingerprint",
    "contains_lone_surrogates",
    "normalize_read_path",
    "observe_processes",
    "observe_reads",
    "observe_request",
    "parse_native_wrapper",
    "parse_read_command",
    "parse_wrapper",
    "raw_argument_bound",
    "scan_root_envelopes",
    "select_endpoint",
    "sha256_hex",
    "tokenize_command",
    "tokenize_literal",
    "unwrap_call_arguments",
    "unwrap_supported_arguments",
    "utf8_byte_span",
    "validate_workspace",
]
