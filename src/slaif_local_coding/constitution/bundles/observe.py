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
**unambiguous** supported envelope.  A container is present only in a
supported standard form: Responses ``input`` as a list **or** string, Chat
``messages`` as a list.  Inference must not treat an input string plus
messages as unambiguous Chat: both recognized containers present without
context is a mixed shape, typed unsupported and non-removable — pairing
bookkeeping is preserved but no read is acquired from either container,
never by precedence, never as two real calls.  The explicit validated
endpoint context is caller-supplied route authority: untrusted body text or
headers cannot assert it.

Root-domain law: only the actual selected **Responses** domain can
establish a root from its user ``input_text`` container.  An explicit Chat
selection never borrows root authority from an ignored Responses ``input``;
mixed, unknown and invalid-endpoint selections return no valid-root
occurrence eligible for later graph/cache admission, even when a
root-shaped object sits in an unused field.  Under a non-Responses
selection any root-shaped occurrence in the unused container is demoted to
non-authoritative typed evidence (status ``unsupported``, no digest,
``UNSUPPORTED_ENDPOINT`` reason) and the root result is typed
``unsupported``.  The selected Responses domain keeps the versioned
envelope contract (section 2 of the observation contract); the actual
domain is documented separately from unobservable/malformed source shapes.
"""

from __future__ import annotations

from typing import Any

from ..bundles.observation_models import (
    Limitation,
    ObservationBounds,
    ObservationReport,
    OccurrenceKind,
    PathContext,
    RootOccurrence,
    RootScanResult,
    RootStatus,
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
    if endpoint == ENDPOINT_RESPONSES:
        # Supported standard Responses forms: an input list or an input
        # string.  Other types carry no recognized container.
        return isinstance(payload.get("input"), (list, str))
    return isinstance(payload.get("messages"), list)


def select_endpoint(payload: dict[str, Any], explicit: str | None = None) -> tuple[str, bool]:
    """Select the observation endpoint domain (pure, total, typed).

    Returns ``(selected, suppress_acquisition)``:

    - explicit validated endpoint with its container present:
      ``(explicit, False)`` — the other container is never acquired;
    - explicit invalid value, or explicit endpoint whose container is
      absent: ``(unknown, False)`` — typed mismatch (the caller emits the
      typed ``ENDPOINT_UNSUPPORTED`` record);
    - no explicit context, both recognized containers present (``input``
      list or string, and ``messages`` list): ``(mixed, True)`` —
      ambiguous shape: bookkeeping only, no acquisition from either
      container, no root established from any container;
    - no explicit context, exactly one recognized container present:
      ``(that endpoint, False)`` — the unambiguous envelope;
    - no explicit context, no recognized container present:
      ``(unknown, False)``.
    """

    if explicit is not None:
        if explicit not in _VALID_EXPLICIT_ENDPOINTS or not _container_present(payload, explicit):
            return ENDPOINT_UNKNOWN, False
        return explicit, False
    has_input = isinstance(payload.get("input"), (list, str))
    has_messages = isinstance(payload.get("messages"), list)
    if has_input and has_messages:
        return ENDPOINT_MIXED, True
    if has_input:
        return ENDPOINT_RESPONSES, False
    if has_messages:
        return ENDPOINT_CHAT, False
    return ENDPOINT_UNKNOWN, False


def _demote_root_result(result: RootScanResult) -> RootScanResult:
    """Demote a root scan of an unused container to non-authoritative evidence.

    The actual endpoint is not the Responses domain: no occurrence is
    eligible for later graph/cache admission.  Valid roots lose status,
    digest and authority (typed ``unsupported`` with ``UNSUPPORTED_ENDPOINT``);
    malformed occurrences keep their typed reasons plus the endpoint
    limitation; non-root occurrences stay non-authoritative as before.
    """

    occurrences: list[RootOccurrence] = []
    for occurrence in result.occurrences:
        if occurrence.kind is OccurrenceKind.ROOT:
            if occurrence.status is RootStatus.OK:
                occurrence = occurrence.model_copy(
                    update={
                        "status": RootStatus.UNSUPPORTED,
                        "digest": None,
                        "reasons": occurrence.reasons + (Limitation.UNSUPPORTED_ENDPOINT,),
                    }
                )
            else:
                occurrence = occurrence.model_copy(
                    update={"reasons": occurrence.reasons + (Limitation.UNSUPPORTED_ENDPOINT,)}
                )
        occurrences.append(occurrence)
    return RootScanResult(
        envelope_format=result.envelope_format,
        status=RootStatus.UNSUPPORTED,
        occurrences=tuple(occurrences),
        version_candidates=(),
        conflicts=(Limitation.UNSUPPORTED_ENDPOINT,) + result.conflicts,
        scanned_items=result.scanned_items,
    )


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

    Root observation is scoped to the actual selected domain: only the
    selected Responses domain scans roots (string-form Responses input has
    no item container and yields no root occurrence); every other
    selection returns a typed unsupported root result with no valid-root
    occurrence, demoting any root-shaped text in an unused container to
    non-authoritative typed evidence.
    """

    effective_bounds = bounds if bounds is not None else ObservationBounds()
    effective_context = context if context is not None else PathContext()
    selected, suppress = select_endpoint(payload, endpoint)
    if selected == ENDPOINT_RESPONSES:
        if isinstance(payload.get("input"), list):
            roots = scan_root_envelopes(payload, effective_bounds)
        else:
            # The Responses string form carries no user item container:
            # there is nothing to scan, so no root occurrence exists.
            roots = RootScanResult(status=RootStatus.NO_ROOT, scanned_items=0)
    else:
        roots = scan_root_envelopes(payload, effective_bounds)
        if isinstance(payload.get("input"), list):
            # The actual endpoint is not the Responses domain: the ignored
            # container may hold root-shaped text, but it can never mint a
            # valid root — demote it to non-authoritative typed evidence.
            roots = _demote_root_result(roots)
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
