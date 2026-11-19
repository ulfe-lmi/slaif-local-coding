"""020 protected session recovery: versioned closed recovery
record and bounded codec (whole020 component stage, first
increment).

These tests drive the ACTUAL accepted chain: genuine
observation -> 018-p P state -> ACTUAL 018-t
``derive_root_region_admission`` -> registered RAM owner
admission -> ``RecoveryRecord.from_owner`` -> codec encode /
decode -> ``recovery_restore_record`` (the ACTUAL complete
D cross-record integrity law, the reconstructed P state and
the ACTUAL T derivation) -> fresh owner re-admission.  The
record persists the trusted P/D source of truth (exact
original bundles, occurrence / causal / replay evidence,
known / unknown ownership) and the complete trusted
namespace binding -- the derived T / graph is re-derived
through the accepted kernel, never serialized as a
caller-positive snapshot.

The codec is pure JSON over the ACTUAL accepted law (no
executable deserialization); the detectable-credential
quarantine refuses without logging content (detectable
subset, not a complete-detection claim, never a redaction);
every refusal is fixed and private.  The stage stays
inert: no store, no resume, no adapter wiring here.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, cast

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.graph_models import ROOT_FILENAME
from slaif_local_coding.constitution.bundles.ram_state import (
    RamStateOwnerRegistry,
)
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateOutcome,
)
from slaif_local_coding.constitution.bundles.recovery_codec import (
    RecoveryCodecError,
    RecoveryCodecIntegrityError,
    RecoveryCodecMalformedError,
    RecoveryCodecSizeError,
    RecoveryCredentialQuarantineError,
    decode_recovery_record,
    encode_recovery_record,
    recovery_record_canonical_bytes,
    recovery_restore_record,
)
from slaif_local_coding.constitution.bundles.recovery_models import (
    RECOVERY_RECORD_HARD_MAX_BYTES,
    RECOVERY_RECORD_INITIAL_MAX_BYTES,
    RecoveryRecord,
    RecoveryResumeReason,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    validate_root_region_lineage_state,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    RootRegionLineageFact,
    RootRegionLineageState,
)
from tests.test_bundle_ram_lifecycle import (
    L1_LEGAL_STAGE,
    L1_V1,
    _l1_dep_read,
    _l3_states,
)
from tests.test_causal_history import ENDPOINTS, MODES, read_request
from tests.test_root_region_lineage import (
    A_TEXT,
    MARK,
    MIX_CMD,
    V2,
    _mixed_body,
    r_bootstrap,
    r_issue,
    r_observe,
)


def _genuine_record(
    mode: Any, endpoint: str, root_body: str = L1_V1
) -> tuple[Any, Any, Any, Any, RecoveryRecord]:
    """The genuine accepted chain ending in ONE closed
    recovery record for the admitted owner: (ns, state,
    result, owner, record).  The explicit legal
    (NON-DEFAULT) 1048576 GraphBounds stage instance is the
    accepted 018-t stage configuration, labeled as such."""
    ns, s0 = r_bootstrap(mode, "recovery-lineage", root_body=root_body, graph_bounds=L1_LEGAL_STAGE)
    state = _l1_dep_read(s0, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    state = _l1_dep_read(state, ns, "x", endpoint, "X.md", "Follow `Target.md`.\n")
    state = _l1_dep_read(state, ns, "t", endpoint, "Target.md", "Synthetic target governance.\n")
    result = derive_root_region_admission(state, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admitted = owner.admit(state, result, ns, expected_revision=0)
    assert admitted.outcome is RamStateOutcome.ADMITTED, admitted
    return ns, state, result, owner, RecoveryRecord.from_owner(owner)


def _genuine_owner(mode: Any, endpoint: str, root_body: str = L1_V1) -> tuple[Any, Any, Any, Any]:
    """The genuine accepted chain WITHOUT a record: (ns,
    state, result, owner) -- for the checkpoint-boundary
    negatives."""
    ns, s0 = r_bootstrap(mode, "recovery-lineage", root_body=root_body, graph_bounds=L1_LEGAL_STAGE)
    state = _l1_dep_read(s0, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    result = derive_root_region_admission(state, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admitted = owner.admit(state, result, ns, expected_revision=0)
    assert admitted.outcome is RamStateOutcome.ADMITTED, admitted
    return ns, state, result, owner


def _root_content_key(result: RootRegionAdmissionResult) -> str:
    admission = result.admission
    assert admission is not None
    rows = [row for row in admission.path_associations if row.path == ROOT_FILENAME]
    assert len(rows) == 1 and len(rows[0].content_keys) == 1
    return rows[0].content_keys[0]


def _rebind_digest(payload: dict[str, Any]) -> str:
    """The canonical digest over the SAME domain the
    production codec hashes: every field EXCEPT
    ``payload_digest`` itself (the digest never binds
    itself)."""
    domain = {k: v for k, v in payload.items() if k != "payload_digest"}
    return hashlib.sha256(recovery_record_canonical_bytes(domain)).hexdigest()


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_round_trip_genuine_record_rederives_and_reads(mode: Any, endpoint: str) -> None:
    """Exact original-byte round trip over the ACTUAL
    accepted P/namespace: the decoded record (restorable
    only after the ACTUAL D cross-record integrity, P
    reconstruction and T derivation) re-joins into a value-
    equal P state, the ACTUAL T is re-derived READY with
    the SAME admission, and a FRESH owner admits it and
    reads the retained root row from RAM."""
    ns, state, result, owner, record = _genuine_record(mode, endpoint)
    assert record.prior_epoch == owner.epoch
    assert record.resume_reason is RecoveryResumeReason.RESTART
    assert record.quarantined is False
    assert record.revision == state.revision == record.d_state.revision

    data = encode_recovery_record(record)
    assert 0 < len(data) <= RECOVERY_RECORD_INITIAL_MAX_BYTES
    decoded = decode_recovery_record(data)
    assert decoded == record

    # The closed restore step over the DECODED record:
    # ACTUAL D cross-record integrity, reconstructed P
    # state, ACTUAL T derivation.
    p2, t2 = recovery_restore_record(decoded)
    assert p2 == state
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    assert t2.admission == result.admission

    # The exact extracted original bundles survive byte for
    # byte (Unicode / CRLF / 32768-byte root source).
    assert decoded.d_state.root is not None
    assert decoded.d_state.root.root_text == L1_V1
    assert len(decoded.d_state.root.root_text.encode("utf-8")) == 32768
    original_occ = {o.call_id: o for o in state.d_state.occurrences}
    decoded_occ = {o.call_id: o for o in decoded.d_state.occurrences}
    assert set(original_occ) == set(decoded_occ)
    for call_id in original_occ:
        assert decoded_occ[call_id].proof.source_text == original_occ[call_id].proof.source_text
    envelope = next(f for f in decoded.root_facts if f.provenance.kind == "envelope")
    assert envelope.source_byte_length == 32768

    # A fresh owner re-admits the reconstructed record set
    # and the retained root row is a RAM-only hit.
    registry2 = RamStateOwnerRegistry()
    owner2 = registry2.acquire(decoded.namespace)
    admitted2 = owner2.admit(p2, t2, decoded.namespace, expected_revision=0)
    assert admitted2.outcome is RamStateOutcome.ADMITTED, admitted2
    found = owner2.lookup(_root_content_key(result), decoded.namespace)
    assert found.outcome is RamStateOutcome.FOUND, found


def test_round_trip_crlf_unicode_and_empty_root() -> None:
    """The exact CRLF / Unicode root and the exact EMPTY
    root are preserved verbatim through the codec."""
    crlf_unicode = "Root line.\r\nGovernance \u00e4\u00f6\u00fc \u4e2d\u6587\u3002\r\n"
    for root_body in (crlf_unicode, ""):
        ns, state, result, owner, record = _genuine_record(
            MODES[0], ENDPOINTS[0], root_body=root_body
        )
        assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
        decoded = decode_recovery_record(encode_recovery_record(record))
        assert decoded == record
        assert decoded.d_state.root is not None
        assert decoded.d_state.root.root_text == root_body
        if root_body:
            assert "\r\n" in decoded.d_state.root.root_text


def test_round_trip_boundaryless_unknown_membership() -> None:
    """The boundaryless (opaque) bundle record: the unknown
    per-member hashes and opaque ownership are retained
    exactly (value-equal round trip, no invented
    attribution)."""
    ns, s_bundle, _s_singleton, _s_bundle2 = _l3_states(MODES[0], ENDPOINTS[0], "recovery-l3")
    result = derive_root_region_admission(s_bundle, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admitted = owner.admit(s_bundle, result, ns, expected_revision=0)
    assert admitted.outcome is RamStateOutcome.ADMITTED, admitted
    record = RecoveryRecord.from_owner(owner)
    decoded = decode_recovery_record(encode_recovery_record(record))
    assert decoded == record
    assert decoded.d_state == s_bundle.d_state
    assert decoded.root_facts == s_bundle.root_facts


def test_decode_size_gate_and_bound_fence() -> None:
    """The bounded read gate runs on the ACTUAL input
    length BEFORE any copy / parse work; the declared bound
    itself is fenced (positive non-bool int, no greater
    than the hard ceiling) BEFORE any data work -- on both
    the encode and the decode side."""
    _ns, _state, _result, _owner, record = _genuine_record(MODES[0], ENDPOINTS[0])
    data = encode_recovery_record(record)
    with pytest.raises(RecoveryCodecSizeError):
        decode_recovery_record(data, max_bytes=len(data) - 1)
    with pytest.raises(RecoveryCodecSizeError):
        decode_recovery_record(b"", max_bytes=len(data))
    assert decode_recovery_record(data, max_bytes=len(data)) == record
    for bad_bound in (0, -1, True, 2.0, "64", RECOVERY_RECORD_HARD_MAX_BYTES + 1):
        with pytest.raises(RecoveryCodecSizeError):
            decode_recovery_record(data, max_bytes=cast(int, bad_bound))
        with pytest.raises(RecoveryCodecSizeError):
            encode_recovery_record(record, max_bytes=cast(int, bad_bound))
    # The output gate: a legal bound below the encoded
    # length refuses before anything is published.
    with pytest.raises(RecoveryCodecSizeError):
        encode_recovery_record(record, max_bytes=len(data) - 1)


def test_decode_malformed_matrix() -> None:
    """Non-UTF-8, non-JSON, non-object, unknown version and
    unknown top-level field all refuse with the fixed
    private error (no content echo)."""
    _ns, _state, _result, _owner, record = _genuine_record(MODES[0], ENDPOINTS[0])
    data = encode_recovery_record(record)
    for bad in (b"\xff\xfe\xfd{", b"not json", b"[1, 2]"):
        with pytest.raises(RecoveryCodecMalformedError):
            decode_recovery_record(bad)
    payload = json.loads(data.decode("utf-8"))
    tampered = dict(payload)
    tampered["record_version"] = "cache-recovery-record/v9"
    with pytest.raises(RecoveryCodecMalformedError):
        decode_recovery_record(_canonical_bytes(tampered))
    extra = dict(payload)
    extra["notes"] = "x"
    extra["payload_digest"] = _rebind_digest(extra)
    with pytest.raises(RecoveryCodecMalformedError):
        decode_recovery_record(_canonical_bytes(extra))


def test_decode_integrity_and_law_negatives() -> None:
    """A stale digest is an integrity refusal; a
    self-consistent (digest-rebound) forgery still refuses
    through the ACTUAL law: the revision 1:1 fence, the
    complete trusted namespace re-derivation and the
    ACTUAL complete D cross-record integrity law (a
    field-law-valid record with a duplicated occurrence
    identity is cross-record-inconsistent -- field law
    alone would have accepted it)."""
    _ns, _state, _result, _owner, record = _genuine_record(MODES[0], ENDPOINTS[0])
    payload = json.loads(encode_recovery_record(record).decode("utf-8"))

    stale = dict(payload)
    stale["prior_epoch"] = record.prior_epoch + 1
    with pytest.raises(RecoveryCodecIntegrityError):
        decode_recovery_record(_canonical_bytes(stale))

    revision_forgery = dict(payload)
    revision_forgery["revision"] = record.revision + 1
    revision_forgery["payload_digest"] = _rebind_digest(revision_forgery)
    with pytest.raises(RecoveryCodecMalformedError):
        decode_recovery_record(_canonical_bytes(revision_forgery))

    session_forgery = dict(payload)
    namespace = dict(session_forgery["namespace"])
    namespace["session"] = "foreign-session"
    session_forgery["namespace"] = namespace
    session_forgery["payload_digest"] = _rebind_digest(session_forgery)
    with pytest.raises(RecoveryCodecMalformedError):
        decode_recovery_record(_canonical_bytes(session_forgery))

    # A field-law-valid but CROSS-RECORD-inconsistent D
    # state (the first occurrence identity duplicated):
    # the ACTUAL complete D cross-record integrity law
    # refuses where field law alone would pass.
    duplicated = json.loads(encode_recovery_record(record).decode("utf-8"))
    d_state = dict(duplicated["d_state"])
    d_state["occurrences"] = d_state["occurrences"] + [d_state["occurrences"][0]]
    duplicated["d_state"] = d_state
    duplicated["payload_digest"] = _rebind_digest(duplicated)
    with pytest.raises(RecoveryCodecIntegrityError):
        decode_recovery_record(_canonical_bytes(duplicated))


def test_decode_refuses_p_law_incoherent_forgery() -> None:
    """A digest-rebound forgery that passes the field law
    and the ACTUAL complete D cross-record integrity law
    but FAILS the ACTUAL accepted P lineage law (stored
    derived issued / authority flags that do not re-derive
    from the retained D state) refuses with the fixed
    MALFORMED error: the record is not a genuine P state,
    and the refusal is a record-level malformation --
    never a restorable typed T outcome.  The genuine
    carrier is an ISSUED read_region root fact (the
    bootstrap envelope fact's flags are fixed by fact
    field law, so it cannot carry this particular
    forgery)."""
    ns, _state, _result, _owner, record = _genuine_mixed_record(MODES[0], ENDPOINTS[0])
    region = next(f for f in record.root_facts if f.provenance.kind == "read_region")
    assert region.issued is True and region.authority is True
    # The genuine carrier is restorable: decode runs the
    # P law over the issued flag and the ACTUAL T derives
    # READY (the positive control for the forgery below).
    decoded = decode_recovery_record(encode_recovery_record(record))
    assert decoded == record
    p_genuine, t_genuine = recovery_restore_record(decoded)
    assert p_genuine == _state
    assert t_genuine.outcome is RootRegionAdmissionOutcome.READY, t_genuine.diagnostics
    forged = json.loads(encode_recovery_record(record).decode("utf-8"))
    facts = [dict(fact) for fact in forged["root_facts"]]
    env = next(f for f in facts if f["provenance"]["kind"] == "read_region")
    env["issued"] = False
    env["authority"] = False
    forged["root_facts"] = facts
    forged["payload_digest"] = _rebind_digest(forged)
    # The forgery passes the FIELD law (an unissued,
    # non-authoritative read_region fact is field-legal)...
    fact = RootRegionLineageFact.model_validate(env)
    assert fact.issued is False and fact.authority is False
    # ...and the ACTUAL complete D cross-record integrity
    # law (the D state is untouched)...
    assert validate_causal_history_state(record.d_state, ns.history_bounds) is None
    # ...but FAILS the ACTUAL accepted P lineage law (the
    # stored flags do not re-derive from the retained D
    # state).
    p_forged = RootRegionLineageState(
        lineage_key=ns.lineage_key,
        revision=record.revision,
        d_state=record.d_state,
        root_facts=tuple(
            fact if f.provenance.kind == "read_region" else f for f in record.root_facts
        ),
    )
    assert validate_root_region_lineage_state(p_forged, ns.root_lineage_bounds) is not None
    with pytest.raises(RecoveryCodecMalformedError):
        decode_recovery_record(_canonical_bytes(forged))


def _genuine_mixed_record(mode: Any, endpoint: str) -> tuple[Any, Any, Any, Any, RecoveryRecord]:
    """The genuine accepted chain carrying ONE ISSUED
    read_region root fact (018-p law): bootstrap v1
    (32768B root, the legal NON-DEFAULT 1048576 GraphBounds
    stage setting) -> trusted issuance -> accepted mixed-
    only complete NEW root v2 read with NO independent
    singleton -> READY T -> admitted owner -> record."""
    ns, s0 = r_bootstrap(mode, "recovery-mixed", root_body=L1_V1, graph_bounds=L1_LEGAL_STAGE)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    state = t2.state
    result = derive_root_region_admission(state, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admitted = owner.admit(state, result, ns, expected_revision=0)
    assert admitted.outcome is RamStateOutcome.ADMITTED, admitted
    return ns, state, result, owner, RecoveryRecord.from_owner(owner)


def _credential_record_direct() -> tuple[RecoveryRecord, dict[str, Any]]:
    """A directly constructed (not checkpointed) record whose
    root source carries a detectable forbidden credential:
    the fixture for proving the ENCODE and DECODE quarantine
    boundaries independently of the checkpoint boundary
    (which refuses earlier)."""
    fake = "AKIA" + "Q" * 16
    _ns, _state, _result, owner = _genuine_owner(
        MODES[0], ENDPOINTS[0], root_body="Governs " + fake + ".\n"
    )
    snapshot = owner.snapshot
    state = snapshot.state
    payload = {
        "record_version": "cache-recovery-record/v1",
        "policy_version": "recovery-record-policy/v1",
        "namespace": snapshot.namespace.model_dump(mode="json"),
        "d_state": state.d_state.model_dump(mode="json"),
        "root_facts": [f.model_dump(mode="json") for f in state.root_facts],
        "revision": state.revision,
        "prior_epoch": owner.epoch,
        "resume_reason": "restart",
        "quarantined": False,
    }
    digest = hashlib.sha256(recovery_record_canonical_bytes(payload)).hexdigest()
    record = RecoveryRecord(
        record_version=payload["record_version"],
        policy_version=payload["policy_version"],
        namespace=snapshot.namespace,
        d_state=state.d_state,
        root_facts=tuple(state.root_facts),
        revision=state.revision,
        prior_epoch=owner.epoch,
        resume_reason=RecoveryResumeReason.RESTART,
        quarantined=False,
        payload_digest=digest,
    )
    return record, json.loads(
        json.dumps({**payload, "payload_digest": digest}, sort_keys=True).encode("utf-8")
    )


def test_credential_quarantine_at_checkpoint() -> None:
    """Detectable forbidden credentials quarantine the
    checkpoint at CONSTRUCTION (before any durable record
    exists) with the fixed private error: no content in
    the message, no record published, no redaction."""
    fake = "AKIA" + "Q" * 16
    _ns, _state, _result, owner = _genuine_owner(
        MODES[0], ENDPOINTS[0], root_body="Governs " + fake + ".\n"
    )
    with pytest.raises(RecoveryCredentialQuarantineError) as excinfo:
        RecoveryRecord.from_owner(owner)
    message = str(excinfo.value)
    assert fake not in message
    assert message == RecoveryCredentialQuarantineError.MESSAGE
    assert issubclass(RecoveryCredentialQuarantineError, RecoveryCodecError)


def test_credential_quarantine_encode_and_escape_decode() -> None:
    """The quarantine also guards ENCODE (nothing
    credential-bearing is ever published for the store) and
    DECODE where JSON text escaping hides the same
    credential from the raw-text early gate: the ACTUAL
    decoded string values are the authoritative scan."""
    record, payload = _credential_record_direct()
    raw = _canonical_bytes(payload)
    fake = "AKIA" + "Q" * 16
    assert fake.encode("utf-8") in raw
    # Hide the credential from the RAW-TEXT regex by
    # escaping its first letter in the serialized text only
    # (the parsed value still carries the credential).
    hidden = raw.replace(
        b"Governs " + fake.encode("utf-8"),
        b"Governs \\u0041KIA" + b"Q" * 16,
    )
    assert fake.encode("utf-8") not in hidden
    parsed = json.loads(hidden.decode("utf-8"))
    assert parsed == payload  # same parsed values, escaped text
    with pytest.raises(RecoveryCredentialQuarantineError):
        decode_recovery_record(hidden)
    # The unhidden form is caught by the raw-text early
    # gate (before any model work) with the same fixed
    # error.
    with pytest.raises(RecoveryCredentialQuarantineError):
        decode_recovery_record(raw)
    # Encode boundary: the encoder refuses to publish the
    # credential-bearing record (and the closed scan is the
    # same fixed refusal).
    from slaif_local_coding.constitution.bundles.recovery_codec import (
        recovery_record_credential_scan,
    )

    with pytest.raises(RecoveryCredentialQuarantineError):
        encode_recovery_record(record)
    with pytest.raises(RecoveryCredentialQuarantineError):
        recovery_record_credential_scan(record)


def test_record_law_joins_direct() -> None:
    """The closed record joins refuse at construction: the
    reason / quarantine bijective join and the digest
    binding (fixed private errors, no bypass)."""
    _ns, _state, _result, _owner, record = _genuine_record(MODES[0], ENDPOINTS[0])
    payload = json.loads(encode_recovery_record(record).decode("utf-8"))
    with pytest.raises(ValidationError):
        RecoveryRecord(
            record_version=payload["record_version"],
            policy_version=payload["policy_version"],
            namespace=record.namespace,
            d_state=record.d_state,
            root_facts=record.root_facts,
            revision=record.revision,
            prior_epoch=payload["prior_epoch"],
            resume_reason=RecoveryResumeReason.RESTART,
            quarantined=True,
            payload_digest=payload["payload_digest"],
        )
    with pytest.raises(ValidationError):
        RecoveryRecord(
            record_version=payload["record_version"],
            policy_version=payload["policy_version"],
            namespace=record.namespace,
            d_state=record.d_state,
            root_facts=record.root_facts,
            revision=record.revision,
            prior_epoch=payload["prior_epoch"],
            resume_reason=RecoveryResumeReason.RESTART,
            quarantined=False,
            payload_digest="f" * 64,
        )
    with pytest.raises(ValidationError):
        RecoveryRecord(
            record_version=payload["record_version"],
            policy_version=payload["policy_version"],
            namespace=record.namespace,
            d_state=record.d_state,
            root_facts=record.root_facts,
            revision=record.revision + 1,
            prior_epoch=payload["prior_epoch"],
            resume_reason=RecoveryResumeReason.RESTART,
            quarantined=False,
            payload_digest=payload["payload_digest"],
        )
