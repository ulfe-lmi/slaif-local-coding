"""Pure composition entry point for bundle observation (objective 017).

``observe_request`` is the small, pure, typed entry point for the inert
``dependency-bundles-v1`` observation stage.  It scans one decoded request
payload (a JSON-decoded dict, bounded upstream) and returns an
``ObservationReport``.  It never mutates the payload, never touches any
filesystem, never executes observed commands, and never infers identity
from untrusted text.  It is not wired into the legacy request execution
path.

Endpoint law: one API request is one endpoint, never a batch of two.  The
selected domain is either an explicit validated endpoint context
(``endpoint="responses"`` or ``endpoint="chat"``) or an inferred
**unambiguous** supported envelope (exactly one of ``input`` / ``messages``
present as a list).  Mixed shapes (both present, no explicit context) are
typed unsupported and non-removable: pairing bookkeeping is preserved but
no read is acquired from either container — never by precedence, never as
two real calls.  An explicit endpoint scopes observation to its own
root/call/result container; the other container is never acquired.  Root
envelope observation keeps its own contract (the Responses ``input``
array) and is not changed by the read-observation endpoint selection.
"""

from __future__ import annotations

from typing import Any

from ..bundles.observation_models import (
    Limitation,
    ObservationBounds,
    ObservationReport,
    PathContext,
    UnpairedRecord,
    canonical_payload_fingerprint,
)
from ..bundles.root_envelopes import scan_root_envelopes
from ..bundles.tool_results import observe_reads

#: Fixed endpoint domain values carried by the report.
ENDPOINT_RESPONSES = "responses"
ENDPOINT_CHAT = "chat"
ENDPOINT_MIXED = "mixed"
ENDPOINT_UNKNOWN = "unknown"

_VALID_EXPLICIT_ENDPOINTS = frozenset({ENDPOINT_RESPONSES, ENDPOINT_CHAT})


def _container_present(payload: dict[str, Any], endpoint: str) -> bool:
    key = "input" if endpoint == ENDPOINT_RESPONSES else "messages"
    return isinstance(payload.get(key), list)


def select_endpoint(payload: dict[str, Any], explicit: str | None = None) -> tuple[str, bool]:
    """Select the observation endpoint domain (pure, total, typed).

    Returns ``(selected, suppress_acquisition)``:

    - explicit validated endpoint with its container present:
      ``(explicit, False)`` — the other container is never acquired;
    - explicit invalid value, or explicit endpoint whose container is
      absent: ``(unknown, False)`` — typed mismatch (the caller emits the
      typed ``ENDPOINT_UNSUPPORTED`` record);
    - no explicit context, both containers present:
      ``(mixed, True)`` — ambiguous shape: bookkeeping only, no
      acquisition from either container;
    - no explicit context, exactly one container present:
      ``(that endpoint, False)`` — the unambiguous envelope;
    - no explicit context, no container present: ``(unknown, False)``.
    """

    if explicit is not None:
        if explicit not in _VALID_EXPLICIT_ENDPOINTS or not _container_present(payload, explicit):
            return ENDPOINT_UNKNOWN, False
        return explicit, False
    has_input = isinstance(payload.get("input"), list)
    has_messages = isinstance(payload.get("messages"), list)
    if has_input and has_messages:
        return ENDPOINT_MIXED, True
    if has_input:
        return ENDPOINT_RESPONSES, False
    if has_messages:
        return ENDPOINT_CHAT, False
    return ENDPOINT_UNKNOWN, False


def observe_request(
    payload: dict[str, Any],
    context: PathContext | None = None,
    bounds: ObservationBounds | None = None,
    endpoint: str | None = None,
) -> ObservationReport:
    """Observe roots and supported reads over one decoded payload.

    ``context`` carries the explicit validated client-workspace context
    (evidenced scope and optional supported workdir); when omitted, absolute
    paths are unknown-workspace and relative paths are unproven-cwd — never
    resolved against the adapter host.  ``endpoint`` is the explicit
    validated endpoint context (``"responses"`` or ``"chat"``); when
    omitted, only an unambiguous supported envelope is inferred, and a
    mixed shape is typed unsupported with no acquisition (see module law).
    """

    effective_bounds = bounds if bounds is not None else ObservationBounds()
    effective_context = context if context is not None else PathContext()
    selected, suppress = select_endpoint(payload, endpoint)
    roots = scan_root_envelopes(payload, effective_bounds)
    if selected in (ENDPOINT_RESPONSES, ENDPOINT_CHAT, ENDPOINT_MIXED):
        reads, unpaired = observe_reads(
            payload,
            effective_context,
            effective_bounds,
            selected_endpoint=selected,
            suppress_acquisition=suppress,
        )
    else:
        # No selected domain: nothing is acquired.  An explicit endpoint
        # whose container is absent (or an invalid value) is a typed
        # mismatch; a payload with no container is simply unobservable.
        if endpoint is not None:
            unpaired = (
                UnpairedRecord(
                    location="$", call_id="", limitation=Limitation.ENDPOINT_UNSUPPORTED
                ),
            )
        else:
            unpaired = ()
        reads = ()
    return ObservationReport(
        endpoint=selected,
        input_fingerprint=canonical_payload_fingerprint(payload),
        roots=roots,
        reads=reads,
        unpaired=unpaired,
    )
