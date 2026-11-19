"""Bounded versioned recovery record codec (objective 020).

The codec is the ONLY path between durable recovery bytes
and a usable / restorable ``RecoveryRecord``:

- ``encode_recovery_record`` publishes the validated record
  as canonical JSON bytes (compact sorted-key, ASCII-
  escaped, UTF-8) under the caller's declared record-byte
  bound (validated as a positive non-bool integer no
  greater than the hard 256 MiB ceiling BEFORE any
  serialization work; the output is gated against the same
  bound before anything is returned for store retention).
  The DETECTABLE forbidden-credential quarantine runs on
  the ACTUAL record string values BEFORE the bytes are
  published.
- ``decode_recovery_record`` runs the CLOSED validation
  sequence BEFORE any usable / restorable state is
  returned: (1) the bound validation, (2) the byte-size
  gate on the ACTUAL input length before any copy / parse
  work, (3) strict UTF-8 + JSON parsing, (4) the closed
  version fence, (5) the closed top-level field set, (6)
  the canonical payload digest verification, (7) the
  ACTUAL complete trusted namespace law (``RootRegion-
  LineageNamespace.model_validate`` re-running the real
  accepted D-scope revalidation), (8) the ACTUAL 018-d
  field law (``CausalHistoryState.model_validate``), (9)
  the ACTUAL root-fact law per retained fact, (10) the ONE
  closed record construction (the record law re-binds the
  scope join, the revision 1:1 fence, the reason /
  quarantine bijective join and the digest), (11) the
  DETECTABLE forbidden-credential quarantine over the
  ACTUAL decoded string values (JSON text escaping can
  hide the same credential from the raw-text early gate,
  which is why the actual-value scan is authoritative),
  and (12) ``recovery_restore_record`` -- the ACTUAL
  complete D cross-record integrity law
  (``validate_causal_history_state``; field law alone is
  NOT complete validation), the reconstructed ACTUAL P
  state, the ACTUAL accepted P lineage law
  (``validate_root_region_lineage_state`` under the
  namespace's actual bounds: a P-incoherent record --
  foreign / spliced provenance, a stored derived flag
  that does not re-derive, an omitted earned fact or a
  detached binding -- refuses as MALFORMED, never as a
  restorable typed refusal) and the ACTUAL accepted
  complete T derivation through the 018-t kernel
  (``derive_root_region_admission``): a TYPED T outcome
  -- READY, an honest non-READY currentness / conflict
  result or an honest resource REFUSED -- is restorable
  and the resume carries it; only a RAISING derivation
  is a malformed record.  Only then is the record
  restorable.

The credential law (SECURITY.md) is a DETECTABLE
forbidden-credential quarantine applied without logging
content and without any complete-detection claim: a match
is a fixed typed refusal (never a redaction, never a
silent fidelity claim), and the closed pattern set is a
conservative detectable subset.

There is NO executable / pickle / marshal / eval / exec
deserialization anywhere in this codec: pure JSON over the
ACTUAL accepted law only.  Every refusal carries a fixed
private message (no content, path or identity echo).  The
codec is INERT: no store, no RAM, no adapter wiring, no
v1 runtime activation.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from pydantic import ValidationError

from .causal_history_models import (
    CausalHistoryState,
    validate_causal_history_state,
)
from .graph_models import _check_hex64
from .recovery_models import (
    _RECOVERY_RECORD_FIELDS,
    RECOVERY_RECORD_CONTRACT_VERSION,
    RECOVERY_RECORD_HARD_MAX_BYTES,
    RECOVERY_RECORD_INITIAL_MAX_BYTES,
    RECOVERY_RECORD_POLICY_VERSION,
    RecoveryError,
    RecoveryRecord,
)
from .root_region_admission import derive_root_region_admission
from .root_region_admission_result_models import RootRegionAdmissionResult
from .root_region_lineage import validate_root_region_lineage_state
from .root_region_lineage_models import (
    RootRegionLineageFact,
    RootRegionLineageNamespace,
    RootRegionLineageState,
)


class RecoveryCodecError(RecoveryError):
    """Base codec refusal (fixed private messages)."""


class RecoveryCodecMalformedError(RecoveryCodecError):
    """A malformed / unknown-version / unknown-field /
    schema-refusing record (fixed message, no echo)."""

    MESSAGE = "the recovery record is malformed"


class RecoveryCodecIntegrityError(RecoveryCodecError):
    """A digest / cross-record integrity refusal (fixed
    message, no echo)."""

    MESSAGE = "the recovery record failed integrity verification"


class RecoveryCodecSizeError(RecoveryCodecError):
    """The record-byte ceiling refusal (fixed message, no
    echo)."""

    MESSAGE = "the recovery record exceeds its bounded byte ceiling"


class RecoveryCredentialQuarantineError(RecoveryCodecError):
    """The DETECTABLE forbidden-credential quarantine
    (SECURITY.md): a fixed refusal without logging content
    and without any complete-detection claim.  The record
    is not usable or restorable; the codec never silently
    redacts retained source while claiming exact
    fidelity."""

    MESSAGE = "a detectable forbidden credential is present in the recovery record"


#: The closed DETECTABLE forbidden-credential patterns
#: (SECURITY.md law, applied without content logging).
#: This is a conservative detectable subset (transport-
#: credential shapes that must never enter a recovery
#: record); it is NOT a complete secret-detection
#: guarantee, and a match is a quarantine, not a
#: redaction.
_CREDENTIAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"Authorization:\s*Bearer\s+[A-Za-z0-9._~+/=-]{32,}"),
)


def _recovery_bound_ok(max_bytes: object) -> bool:
    """The closed bound fence: a positive NON-BOOL raw
    integer no greater than the hard record-byte ceiling
    (bool / float / string inputs refuse before any
    coercion)."""
    return (
        isinstance(max_bytes, int)
        and not isinstance(max_bytes, bool)
        and 1 <= max_bytes <= RECOVERY_RECORD_HARD_MAX_BYTES
    )


def _scan_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in _CREDENTIAL_PATTERNS)


def recovery_record_credential_scan(record: RecoveryRecord) -> None:
    """The DETECTABLE forbidden-credential quarantine over
    the ACTUAL record string values (the decoded model
    values, never the raw JSON text -- text escaping can
    hide the same credential from a raw-text regex).  A
    match raises the fixed quarantine refusal without
    logging content; no complete-detection claim is made
    and no redaction is ever performed."""
    dump = record.model_dump(mode="python")

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if _scan_text(value):
                raise RecoveryCredentialQuarantineError(RecoveryCredentialQuarantineError.MESSAGE)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    walk(dump)


def recovery_record_canonical_bytes(payload: dict[str, Any]) -> bytes:
    """The canonical JSON bytes of a record payload mapping
    (compact, sorted keys, ASCII-escaped, UTF-8) -- the
    digest domain.  ``payload_digest`` itself is EXCLUDED
    by the caller (the digest never binds itself)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def encode_recovery_record(
    record: RecoveryRecord,
    *,
    max_bytes: int = RECOVERY_RECORD_INITIAL_MAX_BYTES,
) -> bytes:
    """Encode ONE validated record to canonical JSON bytes
    (the durable checkpoint bytes) under the caller's
    declared bound: the bound is validated BEFORE any
    serialization work, the credential quarantine runs on
    the ACTUAL record string values BEFORE the bytes are
    published, and the encoded output is gated against the
    same bound before it is returned for store retention
    (nothing oversized is ever published)."""
    if not _recovery_bound_ok(max_bytes):
        raise RecoveryCodecSizeError(RecoveryCodecSizeError.MESSAGE)
    if type(record) is not RecoveryRecord:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    recovery_record_credential_scan(record)
    data = json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    if len(data) > max_bytes:
        raise RecoveryCodecSizeError(RecoveryCodecSizeError.MESSAGE)
    return data


def decode_recovery_record(
    data: bytes,
    *,
    max_bytes: int = RECOVERY_RECORD_INITIAL_MAX_BYTES,
) -> RecoveryRecord:
    """Decode and VALIDATE durable recovery bytes into ONE
    usable / restorable record -- the complete closed law
    (module docstring sequence) runs BEFORE the record is
    returned.  The bound is validated and the ACTUAL input
    length is gated before any copy / parse work; a
    credential match is the quarantine refusal, never a
    redaction; only a record whose ACTUAL complete D
    cross-record integrity, reconstructed P state and
    ACTUAL T derivation all succeed is restorable.
    Every refusal is a fixed typed codec error with no
    content echo."""
    if not _recovery_bound_ok(max_bytes):
        raise RecoveryCodecSizeError(RecoveryCodecSizeError.MESSAGE)
    # The ACTUAL byte length is gated BEFORE any copy work:
    # bytes / bytearray length IS the byte length, a
    # memoryview is gated by its real ``nbytes`` (its
    # ``len`` is an element count, not a byte count) and
    # any other input type refuses before any allocation.
    if isinstance(data, (bytes, bytearray)):
        length = len(data)
    elif isinstance(data, memoryview):
        length = data.nbytes
    else:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    if not 0 < length <= max_bytes:
        raise RecoveryCodecSizeError(RecoveryCodecSizeError.MESSAGE)
    data = bytes(data)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    if _scan_text(text):
        raise RecoveryCredentialQuarantineError(RecoveryCredentialQuarantineError.MESSAGE)
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    if not isinstance(payload, dict):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    if payload.get("record_version") != RECOVERY_RECORD_CONTRACT_VERSION:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    if payload.get("policy_version") != RECOVERY_RECORD_POLICY_VERSION:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    if set(payload) != _RECOVERY_RECORD_FIELDS:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    claimed_digest = payload["payload_digest"]
    if not isinstance(claimed_digest, str):
        raise RecoveryCodecIntegrityError(RecoveryCodecIntegrityError.MESSAGE)
    try:
        _check_hex64(claimed_digest, "payload_digest")
    except ValueError:
        raise RecoveryCodecIntegrityError(RecoveryCodecIntegrityError.MESSAGE) from None
    computed = hashlib.sha256(
        recovery_record_canonical_bytes(
            {key: value for key, value in payload.items() if key != "payload_digest"}
        )
    ).hexdigest()
    if computed != claimed_digest:
        raise RecoveryCodecIntegrityError(RecoveryCodecIntegrityError.MESSAGE)
    # The ACTUAL complete trusted namespace law (the real
    # accepted D-scope revalidation runs inside it).
    try:
        namespace = RootRegionLineageNamespace.model_validate(payload["namespace"])
    except (TypeError, ValidationError):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    # The ACTUAL 018-d FIELD law (cross-record integrity is
    # validate_causal_history_state, run later in the
    # restore step -- field law alone is not complete
    # validation).
    try:
        d_state = CausalHistoryState.model_validate(payload["d_state"])
    except (TypeError, ValidationError):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    raw_facts = payload["root_facts"]
    if not isinstance(raw_facts, list):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    try:
        facts = tuple(RootRegionLineageFact.model_validate(fact) for fact in raw_facts)
    except (TypeError, ValidationError):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    try:
        record = RecoveryRecord(
            record_version=payload["record_version"],
            policy_version=payload["policy_version"],
            namespace=namespace,
            d_state=d_state,
            root_facts=facts,
            revision=payload["revision"],
            prior_epoch=payload["prior_epoch"],
            resume_reason=payload["resume_reason"],
            quarantined=payload["quarantined"],
            payload_digest=claimed_digest,
        )
    except (TypeError, ValidationError):
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    # The DETECTABLE forbidden-credential quarantine over
    # the ACTUAL decoded values (authoritative over the
    # raw-text early gate: JSON text escaping can hide the
    # same credential from the raw-text regex).
    recovery_record_credential_scan(record)
    # The ACTUAL complete validation / derivation before
    # the record is declared restorable.
    recovery_restore_record(record)
    return record


def recovery_restore_record(
    record: RecoveryRecord,
) -> tuple[RootRegionLineageState, RootRegionAdmissionResult]:
    """Reconstruct the ACTUAL P state from the closed
    record, verify it against the ACTUAL accepted P
    lineage law and derive the ACTUAL accepted complete T
    result through the 018-t kernel -- the resume
    validation / derivation step.

    The sequence is closed: (1) the ACTUAL complete D
    cross-record integrity law (``validate_causal_history_
    state`` under the namespace's actual history bounds;
    the record models enforce field-level shape only) --
    a refusal is the fixed INTEGRITY error; (2) the ONE
    P-state reconstruction (the scope join and the
    D-state 1:1 fence) -- a refusal is the fixed
    MALFORMED error; (3) the ACTUAL accepted P lineage
    law (``validate_root_region_lineage_state`` under the
    namespace's ACTUAL root-lineage, history, graph,
    proof and observation bounds and workspace): a
    field-law-valid but P-incoherent record (foreign /
    spliced provenance, a stored derived issued /
    authority flag that does not re-derive from the
    retained D state, an omitted earned fact or a
    detached binding) is NOT a genuine P state -- it
    refuses with the fixed MALFORMED error and is never
    a restorable typed refusal; and (4) the ACTUAL
    accepted complete T derivation (``derive_root_
    region_admission``: the real Q / P / F / E / G law
    over the reconstructed state -- object construction
    is not authentication).  A derivation that RETURNS a
    typed outcome is an honest result: READY, a non-READY
    currentness / conflict outcome and an honest resource
    REFUSED are all restorable and the resume carries the
    typed outcome (legitimate non-READY / conflict
    histories remain restorable as unusable evidence);
    only a derivation that RAISES is a malformed record.
    The resume component calls this once per resume (the
    decode step already proved restorability)."""
    limitation = validate_causal_history_state(record.d_state, record.namespace.history_bounds)
    if limitation is not None:
        raise RecoveryCodecIntegrityError(RecoveryCodecIntegrityError.MESSAGE)
    try:
        p_state = RootRegionLineageState(
            lineage_key=record.namespace.lineage_key,
            revision=record.revision,
            d_state=record.d_state,
            root_facts=record.root_facts,
        )
    except Exception:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    problem = validate_root_region_lineage_state(
        p_state,
        record.namespace.root_lineage_bounds,
        history_bounds=record.namespace.history_bounds,
        graph_bounds=record.namespace.graph_bounds,
        proof_bounds=record.namespace.proof_bounds,
        observation_bounds=record.namespace.observation_bounds,
        workspace=record.namespace.workspace,
    )
    if problem is not None:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE)
    try:
        t_result = derive_root_region_admission(p_state, record.namespace)
    except Exception:
        raise RecoveryCodecMalformedError(RecoveryCodecMalformedError.MESSAGE) from None
    return p_state, t_result
