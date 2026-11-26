"""The v1 stage telemetry (objective 023-a).

Law (handoff section 15, order 023-a section 1-2):
- FIXED stage vocabulary with closed per-stage outcome enums:
  recognition, acquisition, graph, admission, compilation,
  replacement, injection, recovery and main_upstream.  Every
  event is created AT THE OWNING STAGE from the ACTUAL typed
  result (never
  inferred from a request field, a selected-entry count or a
  response code); closed refusals are events of their owning
  stage.
- Content-free by construction: only the closed enum values and
  bounded NUMERIC counts cross this boundary.  Values, source,
  identifiers, paths, digests and credentials never appear in an
  event.  The approved protected synthetic evidence is assembled
  by the TEST HARNESS from its own fake-upstream / compiler
  captures plus these content-free stage facts; the runtime owns
  no raw-content persistence surface.
- The four-way cache distinction is a closed classification
  (original-present RAM reuse / source-absent injection /
  restart rebuilding in a new epoch / genuine client compaction).
  The client-compaction value is CLOSED but UN-EARNED: this
  round has no real client compaction event, so no code path
  records that value.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum

#: The fixed detail vocabulary per stage: every recorded detail
#: NAME is closed (a fixed error text on an unknown name), and
#: every detail VALUE is a bounded integer count.
V1_STAGE_DETAIL_NAMES: Mapping[str, frozenset[str]] = {
    "recognition": frozenset({"root_occurrences", "root_ok"}),
    "acquisition": frozenset(
        {
            "revision",
            "reads_complete",
            "reads_partial",
            "reads_unsupported",
            "members_observed",
            "chars_observed",
            "paths_absolute",
            "paths_normalized",
        }
    ),
    "admission": frozenset({"entries", "members"}),
    "graph": frozenset(
        {"nodes", "edges", "nodes_known", "nodes_missing", "nodes_unresolved", "candidates"}
    ),
    "compilation": frozenset({"invocations", "entries"}),
    "replacement": frozenset({"edits", "markers_emitted", "markers_replayed", "entries"}),
    "injection": frozenset(
        {
            "working_set_entries",
            "omitted_entries",
            "governance_tokens",
            "aggregate_limit",
            "request_tokens",
        }
    ),
    "recovery": frozenset({"generation", "epoch", "revision"}),
    "main_upstream": frozenset({"usage_input_tokens", "usage_output_tokens"}),
    "reuse_class": frozenset(set()),
}


class V1Stage(StrEnum):
    """The closed v1 stage vocabulary (handoff section 15 table)."""

    RECOGNITION = "recognition"
    ACQUISITION = "acquisition"
    #: The current-graph facts of the ACTUAL returned same-run
    #: R/F result (the handoff section 15 'Graph' row): recorded at
    #: the owning admission stage exactly when the returned
    #: admission carries the actual graph (the ready path); the
    #: node/edge counts with the closed honest availability
    #: partition and the retained unresolved-origin candidate
    #: count are content-free bounded counts.
    GRAPH = "graph"
    ADMISSION = "admission"
    COMPILATION = "compilation"
    REPLACEMENT = "replacement"
    INJECTION = "injection"
    RECOVERY = "recovery"
    MAIN_UPSTREAM = "main_upstream"
    #: The four-way cache distinction is a closed classification
    #: fact of the transaction stage (not a pipeline stage of its
    #: own); the reuse-class events carry no numeric details.
    REUSE_CLASS = "reuse_class"


class V1ReuseClass(StrEnum):
    """The closed four-way cache distinction (handoff section 15).

    ``CLIENT_COMPACTION`` is part of the closed vocabulary but
    UN-EARNED in this round: genuine client compaction requires a
    real client event that no test in this objective produces, so
    no code path records that value."""

    ORIGINAL_PRESENT_RAM_REUSE = "original_present_ram_reuse"
    SOURCE_ABSENT_INJECTION = "source_absent_injection"
    RESTART_REBUILD_NEW_EPOCH = "restart_rebuild_new_epoch"
    CLIENT_COMPACTION = "client_compaction"


#: The closed outcome vocabulary per stage (low cardinality,
#: fixed; nothing else may ever be recorded).
V1_STAGE_OUTCOMES: Mapping[V1Stage, frozenset[str]] = {
    V1Stage.RECOGNITION: frozenset({"root", "rootless", "root_rejected"}),
    V1Stage.ACQUISITION: frozenset({"accepted", "replayed", "refused"}),
    V1Stage.ADMISSION: frozenset(
        {"ready", "root_currentness_unproven", "root_authority_conflict", "refused"}
    ),
    V1Stage.GRAPH: frozenset({"ready"}),
    V1Stage.COMPILATION: frozenset(
        {"completed", "joined", "hit", "policy_stale", "refused", "failed"}
    ),
    V1Stage.REPLACEMENT: frozenset(
        {
            "ok",
            "no_replacement",
            "selection_not_ready",
            "generation_not_durable",
            "cross_namespace",
            "span_mismatch",
            "marker_invalid",
            "entry_unresolved",
            "edit_conflict",
            "over_bound",
        }
    ),
    V1Stage.INJECTION: frozenset({"compiled", "source_absent", "none"}),
    V1Stage.RECOVERY: frozenset(
        {"steady", "resumed", "cold", "quarantined", "refused", "published", "retained"}
    ),
    V1Stage.MAIN_UPSTREAM: frozenset(
        {
            "forwarded",
            "provider_accepted",
            "provider_rejected",
            "timeout",
            "connection_error",
            "cancelled",
            "response_read_error",
            "response_too_large",
        }
    ),
    V1Stage.REUSE_CLASS: frozenset(
        {c.value for c in V1ReuseClass if c is not V1ReuseClass.CLIENT_COMPACTION}
    ),
}


@dataclass(frozen=True, slots=True)
class V1StageEvent:
    """ONE content-free stage fact owned by its stage.

    ``details`` are closed NAME/count pairs: every name must be in
    the stage's closed detail vocabulary and every value a bounded
    non-negative integer.  The fixed error text names the closed
    violation class without echoing the offending value."""

    stage: V1Stage
    outcome: str
    duration: float = 0.0
    details: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if self.outcome not in V1_STAGE_OUTCOMES[self.stage]:
            raise ValueError("stage outcome outside the closed vocabulary")
        names = V1_STAGE_DETAIL_NAMES[self.stage.value]
        for name, value in self.details:
            if name not in names:
                raise ValueError("stage detail name outside the closed vocabulary")
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("stage detail value is not a bounded count")
        if len({name for name, _ in self.details}) != len(self.details):
            raise ValueError("stage detail names repeat")


class V1StageRecorder:
    """The per-request owning-stage recorder (one worker).

    Each owning stage calls :meth:`record` with the ACTUAL typed
    result it produced; the event is appended (the protected
    evidence correlation source) and emitted (to the private
    metrics) at that stage.  A recorder with no emitter is the
    pure content-free fact path.  The recorder carries no bytes,
    identifiers, paths, digests or credentials -- only the closed
    stage/outcome pairs and the bounded counts above."""

    __slots__ = ("_route", "_endpoint", "_emit", "_events", "_compile_attribution")

    def __init__(
        self,
        *,
        route: str,
        endpoint: str,
        emit: Callable[[V1StageEvent], None] | None = None,
    ) -> None:
        self._route = route
        self._endpoint = endpoint
        self._emit = emit
        self._events: list[V1StageEvent] = []
        #: The request-scope closed compile attribution (objective
        #: 023-a four-way distinction): the TOTAL actual dispatch
        #: count of THIS request (the replay pre-check run and the
        #: transaction run alike -- work dispatched anywhere in the
        #: request prevents a cross-request reuse fact) and whether
        #: ANY dispatched entry belonged to the restored
        #: (pre-restart) record set (the restart-rebuild fact).
        #: Only the closed count/bool cross this boundary -- no
        #: content key, no digest, no identifier.
        self._compile_attribution: tuple[int, bool] = (0, False)

    @property
    def route(self) -> str:
        return self._route

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def events(self) -> tuple[V1StageEvent, ...]:
        return tuple(self._events)

    @staticmethod
    def begin() -> float:
        return time.monotonic()

    def note_compile_dispatch(self, *, dispatched: int, restored: bool) -> None:
        """The owning compile stage (the replay pre-check run or
        the transaction run) attributes the ACTUAL work of its run
        to the request: the summed invocations and the closed
        restored-state fact (computed at the owning stage from the
        typed entry/work results; no key crosses this boundary)."""
        total, any_restored = self._compile_attribution
        self._compile_attribution = (total + dispatched, any_restored or restored)

    @property
    def request_compile_attribution(self) -> tuple[int, bool]:
        """The request-scope closed attribution:
        ``(total dispatches, any dispatched restored-state entry)``."""
        return self._compile_attribution

    def record(self, stage: V1Stage, outcome: str, started: float, **details: int) -> V1StageEvent:
        event = V1StageEvent(
            stage=stage,
            outcome=outcome,
            duration=max(0.0, time.monotonic() - started),
            details=tuple(details.items()),
        )
        self._events.append(event)
        if self._emit is not None:
            self._emit(event)
        return event


__all__ = [
    "V1Stage",
    "V1ReuseClass",
    "V1StageEvent",
    "V1StageRecorder",
    "V1_STAGE_OUTCOMES",
    "V1_STAGE_DETAIL_NAMES",
]
