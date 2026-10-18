"""Pure composition entry point for bundle observation (objective 017).

``observe_request`` is the small, pure, typed entry point for the inert
``dependency-bundles-v1`` observation stage.  It scans one decoded request
payload (a JSON-decoded dict, bounded upstream) and returns an
``ObservationReport``.  It never mutates the payload, never touches any
filesystem, never executes observed commands, and never infers identity from
untrusted text.  It is not wired into the legacy request execution path.
"""

from __future__ import annotations

from typing import Any

from ..bundles.observation_models import (
    ObservationBounds,
    ObservationReport,
    PathContext,
    canonical_payload_fingerprint,
)
from ..bundles.root_envelopes import scan_root_envelopes
from ..bundles.tool_results import observe_reads


def observe_request(
    payload: dict[str, Any],
    context: PathContext | None = None,
    bounds: ObservationBounds | None = None,
) -> ObservationReport:
    """Observe roots and supported reads over one decoded payload.

    ``context`` carries the explicit validated client-workspace context
    (evidenced scope and optional supported workdir); when omitted, absolute
    paths are unknown-workspace and relative paths are unproven-cwd — never
    resolved against the adapter host.
    """

    effective_bounds = bounds if bounds is not None else ObservationBounds()
    effective_context = context if context is not None else PathContext()
    roots = scan_root_envelopes(payload, effective_bounds)
    reads, unpaired = observe_reads(payload, effective_context, effective_bounds)
    return ObservationReport(
        endpoint="responses"
        if isinstance(payload.get("input"), list)
        else "chat"
        if isinstance(payload.get("messages"), list)
        else "unknown",
        input_fingerprint=canonical_payload_fingerprint(payload),
        roots=roots,
        reads=reads,
        unpaired=unpaired,
    )
