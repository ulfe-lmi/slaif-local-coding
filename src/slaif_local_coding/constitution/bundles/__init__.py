"""Inert pure observation stage for the dependency-bundle cache rework.

This package implements the bounded first slice (D01-D05) of Objective 017:
versioned root-envelope, literal shell-read, and tool-result observation with
exact source spans and typed limitations.  It is deliberately **not** wired
into the legacy request execution path, the graph/cache/compiler, or any
runtime stage; see ``docs/CACHE-OBSERVATION-CONTRACT.md``.
"""

from __future__ import annotations

from ..bundles.client_paths import normalize_read_path, validate_workspace
from ..bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    ENVELOPE_FORMAT,
    OBSERVER_VERSION,
    READ_GRAMMAR,
    TOOL_WRAPPER_FORMAT,
    CharSpan,
    Limitation,
    NormalizedPath,
    ObservationBounds,
    ObservationReport,
    OccurrenceKind,
    PathContext,
    PathForm,
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
from ..bundles.observe import observe_request
from ..bundles.read_grammar import (
    UnwrappedCommand,
    parse_read_command,
    tokenize_literal,
    unwrap_call_arguments,
    unwrap_supported_arguments,
)
from ..bundles.root_envelopes import scan_root_envelopes
from ..bundles.tool_results import observe_reads, parse_wrapper

__all__ = [
    "EMPTY_SOURCE_SHA256",
    "ENVELOPE_FORMAT",
    "OBSERVER_VERSION",
    "READ_GRAMMAR",
    "TOOL_WRAPPER_FORMAT",
    "CharSpan",
    "Limitation",
    "NormalizedPath",
    "ObservationBounds",
    "ObservationReport",
    "OccurrenceKind",
    "PathContext",
    "PathForm",
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
    "observe_reads",
    "observe_request",
    "parse_read_command",
    "parse_wrapper",
    "scan_root_envelopes",
    "sha256_hex",
    "tokenize_literal",
    "unwrap_call_arguments",
    "unwrap_supported_arguments",
    "utf8_byte_span",
    "validate_workspace",
]
