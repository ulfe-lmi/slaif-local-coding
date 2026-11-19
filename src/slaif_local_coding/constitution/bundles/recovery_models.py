"""Versioned closed per-session recovery record models
(objective 020, protected session recovery component).

This module carries the versioned data models of the NEW
protected per-session recovery record: the closed
``RecoveryResumeReason`` vocabulary and the immutable
``RecoveryRecord`` -- the exact trusted 018-p namespace
(the complete principal / session / repository / route /
model / configuration binding), the ACTUAL accepted 018-d
``CausalHistoryState`` (the exact extracted original source
bundles with their provenance, occurrence / causal / replay
evidence, known / unknown ownership and historical
stale / conflicting evidence), the complete supported root-
source facts, the P-state revision, the prior live cache
epoch and the recorded recovery reason, plus the bounded
pre-accounted ``quarantined`` flag that carries the 019
adverse-currentness fence through durability.

The record is METADATA + EXACT ORIGINALS ONLY: never whole
conversations, transport envelopes, environment-context
tails, images, transport credentials or unrelated tool
output (the D state retains the extracted source bytes and
derived provenance, not raw request arguments or
credential-bearing result wrappers).  The DETECTABLE
forbidden-credential law (SECURITY.md) is applied at
checkpoint construction (``from_owner``), before encode /
store and before restore by the codec (``recovery_codec``)
as typed rejection / quarantine over the ACTUAL record
string values (raw JSON text escaping can hide the same
credential), without logging content, without any
complete-detection claim, and never by silent redaction
of retained source.

The record is a durable checkpoint, not a RAM object: it is
encoded / decoded by the bounded codec (pure JSON over the
ACTUAL accepted pydantic law -- no executable / pickle
deserialization), stored by the protected per-session store
(``recovery_store``), and consumed by the resume
coordination (``recovery_resume``) which reconstructs the
P state, derives the ACTUAL accepted current graph /
admission through the 018-t kernel and re-registers the RAM
owner in a DISTINCT live epoch.  Object construction is not
authentication: the record law re-binds the scope join,
the revision 1:1 fence, the reason / quarantine join and
the digest on every construction; and a decoded record is
usable / restorable only after the codec runs the ACTUAL
complete trusted namespace law, the ACTUAL 018-d field
law, the ACTUAL root-fact law, the DETECTABLE credential
quarantine and the ACTUAL complete D cross-record
integrity law with the reconstructed P state and the
ACTUAL accepted T derivation (``recovery_restore_record``
in ``recovery_codec`` -- the record models enforce field-
level shape only, never the cross-record D integrity).

The models are INERT: no adapter wiring, no configuration
key, no v1 runtime activation, no recovery-content read on
any normal path.  All 018 / 019 public signatures, schemas,
defaults, version tags and refusal laws stay intact.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import Field, InstanceOf, model_validator

from .causal_history_models import MAX_REVISION, CausalHistoryState
from .graph_models import _check_hex64, _fixed, _GraphFrozen
from .observation_models import PRIVATE_ID_PLACEHOLDER
from .root_lineage_models import _HARD_ROOT_FACTS
from .root_region_lineage_models import (
    RootRegionLineageFact,
    RootRegionLineageNamespace,
)

RECOVERY_RECORD_CONTRACT_VERSION = "cache-recovery-record/v1"
RECOVERY_RECORD_POLICY_VERSION = "recovery-record-policy/v1"

#: The initial codec record-byte ceiling (64 MiB).
RECOVERY_RECORD_INITIAL_MAX_BYTES = 67_108_864

#: The hard codec record-byte ceiling (256 MiB).
RECOVERY_RECORD_HARD_MAX_BYTES = 268_435_456

#: The closed record field set (extra / missing top-level
#: fields refuse; the codec enforces it BEFORE any law).
_RECOVERY_RECORD_FIELDS = frozenset(
    {
        "record_version",
        "policy_version",
        "namespace",
        "d_state",
        "root_facts",
        "revision",
        "prior_epoch",
        "resume_reason",
        "quarantined",
        "payload_digest",
    }
)


class RecoveryError(Exception):
    """Base error for the 020 recovery component (fixed
    private messages; no content, path or identity echo)."""


class RecoveryRecordError(RecoveryError):
    """A fixed record-law refusal (closed vocabulary)."""

    MESSAGE = "the recovery record failed the closed record law"


def recovery_address_key(address: RecoverySessionAddress) -> str:
    """The stable 64-hex identity of the trusted resume
    ADDRESS: the SHA-256 of the canonical compact
    sorted-key JSON of the six authenticated stable
    fields (the SAME derivation the protected store
    uses for the opaque per-session directory name).
    The key is a lookup identity for the resume
    boundary's initial-load transient reservation
    (requirement 4), never authentication: the
    COMPLETE trusted namespace is still validated
    from the loaded record and joined before any RAM
    publication.  No private identity value is
    echoed (a one-way digest)."""
    payload = json.dumps(
        address.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class RecoveryResumeReason(StrEnum):
    """The closed resume-reason vocabulary (020).

    ``restart`` is the explicit NEW-EPOCH compile-once
    exception: a normal process restart rebuilds the resumed
    session's RAM in a distinct live epoch (recovery
    recompilation is separate work, never an ordinary hit
    and never a silent unquarantine).  ``quarantine_fence``
    records the durable persistence of a FAILED DURABLE
    FENCE (the owner's bounded pre-accounted
    adverse-currentness quarantine): a record carrying it
    must not resume old usable governance, and no automatic
    epoch reset / retry clears it."""

    RESTART = "restart"
    QUARANTINE_FENCE = "quarantine_fence"


class RecoverySessionAddress(_GraphFrozen):
    """The trusted resume lookup ADDRESS (020).

    The authenticated stable principal / session /
    repository / route binding plus the configured
    model / policy context -- exactly the stable address
    that locates ONE protected session namespace even
    when the first resumed request contains NO root,
    source or surviving virtual reference.  The address
    is a LOOKUP input, never authentication: the
    COMPLETE trusted namespace (workspace / mode /
    bounds / versions) is validated from the loaded
    record and ``binds`` must join it before any RAM
    publication; the opaque per-session directory name
    derived from the address is not authentication
    either.  Errors and operational reprs suppress all
    private identity values (privacy law).
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str = Field(min_length=1, max_length=1024)

    @classmethod
    def from_namespace(cls, namespace: RootRegionLineageNamespace) -> RecoverySessionAddress:
        """The address carried by the COMPLETE trusted
        namespace (the resume address of an admitted
        session is derived from its actual namespace,
        never from an opaque filename or caller header)."""
        return cls(
            principal=namespace.principal,
            session=namespace.session,
            repository=namespace.repository,
            route=namespace.route,
            model_identity=namespace.model_identity,
            config_fingerprint=namespace.config_fingerprint,
        )

    def binds(self, namespace: RootRegionLineageNamespace) -> bool:
        """The six-field equality join against the
        COMPLETE trusted namespace loaded from a record
        (a mismatch is the fixed ``namespace_mismatch``
        refusal at the store boundary)."""
        return (
            self.principal == namespace.principal
            and self.session == namespace.session
            and self.repository == namespace.repository
            and self.route == namespace.route
            and self.model_identity == namespace.model_identity
            and self.config_fingerprint == namespace.config_fingerprint
        )

    @property
    def lineage_key(self) -> str:
        """The stable 64-hex trusted-address identity
        key (requirement 4): the key the resume
        boundary reserves its initial load / decode
        transient under BEFORE the loaded namespace
        exists, then binds to the validated
        namespace's lineage key (the registry's cold
        transient seams)."""
        return recovery_address_key(self)

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RecoverySessionAddress(principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER})"
        )

    __str__ = __repr__


def recovery_record_payload_bytes(record: RecoveryRecord) -> bytes:
    """The canonical payload bytes of a validated record:
    compact sorted-key JSON of EVERY field except
    ``payload_digest`` itself (UTF-8, ASCII-escaped)."""
    payload = {
        key: value
        for key, value in record.model_dump(mode="json").items()
        if key != "payload_digest"
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def recovery_record_payload_digest(record: RecoveryRecord) -> str:
    """The record's self-integrity digest over the canonical
    payload (everything except the digest field)."""
    return hashlib.sha256(recovery_record_payload_bytes(record)).hexdigest()


class RecoveryRecord(_GraphFrozen):
    """ONE versioned closed recovery record for ONE trusted
    session (020).

    ``namespace`` is the COMPLETE trusted 018-p namespace
    (the full principal / session / repository / route /
    model / configuration binding -- the resume lookup
    address is exactly this record; an opaque filename is
    not authentication).  ``d_state`` is the ACTUAL accepted
    018-d causal-history state by immutable reference: the
    exact extracted original bundles (Unicode / CRLF / exact
    empty and ordered multi-file content), the completed
    read occurrences with their FIRST original provenance
    and argument fingerprints, the trusted issuance
    frontiers, the parent links (partial-order evidence
    only) and the result fingerprints -- the complete
    original / causal / replay evidence and known / unknown
    ownership.  ``root_facts`` retains the complete
    supported root-source evidence (provenance-
    discriminated, derived flags at the last accepted
    transition).  ``revision`` is the P-state region
    revision at checkpoint time (1:1 with the wrapped D
    revision, a serialization fence, never a clock).
    ``prior_epoch`` is the live cache epoch the record was
    checkpointed under; resume re-registers the owner in a
    DISTINCT epoch and the two must never be conflated.
    ``resume_reason`` and ``quarantined`` are bound
    bijectively: a quarantined fence persists with
    ``quarantine_fence`` (and blocks old usable governance
    through durability), an ordinary restart record carries
    ``restart``.  ``payload_digest`` is recomputed on every
    construction and must bind the canonical payload, so a
    spliced record cannot pass even when self-consistent.
    """

    record_version: str
    policy_version: str
    namespace: InstanceOf[RootRegionLineageNamespace]
    d_state: InstanceOf[CausalHistoryState]
    root_facts: tuple[RootRegionLineageFact, ...] = Field(default=(), max_length=_HARD_ROOT_FACTS)
    revision: int = Field(ge=0, le=MAX_REVISION)
    prior_epoch: int = Field(ge=1)
    resume_reason: RecoveryResumeReason
    quarantined: bool
    payload_digest: str

    @model_validator(mode="after")
    def _v_closed_law(self) -> RecoveryRecord:
        if self.record_version != RECOVERY_RECORD_CONTRACT_VERSION:
            raise _fixed("the recovery record version is not the closed version")
        if self.policy_version != RECOVERY_RECORD_POLICY_VERSION:
            raise _fixed("the recovery record policy version is not the closed version")
        _check_hex64(self.payload_digest, "payload_digest")
        # The complete trusted namespace and the retained D
        # state must be the SAME scope: the namespace law
        # re-derived the actual D scope from its own fields,
        # so the join on the actual D history key is the
        # cross-consistency fence (a spliced namespace or
        # spliced state refuses even when self-consistent).
        if self.d_state.history_key != self.namespace.history_key:
            raise _fixed("the recovery record namespace does not bind its causal history")
        # The P region revision stays in exact 1:1 with the
        # wrapped D revision (the 018-p law); the checkpoint
        # revision is a fence, never an arrival clock.
        if self.revision != self.d_state.revision:
            raise _fixed("the recovery record revision does not match its causal history")
        # The closed reason / fence bijective join: the
        # durable quarantine persists WITH the fence reason,
        # and an ordinary restart record never carries the
        # fence (no silent unquarantine, no fence without
        # reason).
        if self.quarantined != (self.resume_reason is RecoveryResumeReason.QUARANTINE_FENCE):
            raise _fixed("the recovery record reason does not bind its quarantine fence")
        if recovery_record_payload_digest(self) != self.payload_digest:
            raise _fixed("the recovery record digest does not bind its payload")
        return self

    @classmethod
    def from_owner(cls, owner: Any, *, quarantine_fence: bool = False) -> RecoveryRecord:
        """Build the closed record for ONE live RAM owner's
        CURRENT retained record set (the checkpoint source):
        the owner's trusted namespace, the ACTUAL retained
        P state's D state and root facts by reference, the
        P-state revision, the owner's live epoch as
        ``prior_epoch`` and the owner's actual quarantine
        fence as the recorded reason.  The canonical
        payload digest is computed over the exact dumped
        payload and then the ONE closed construction
        re-verifies every law (including the digest
        re-binding) -- no bypassed copy.  An empty owner
        (no retained record set) refuses with the fixed
        error: there is nothing durable to checkpoint.
        With ``quarantine_fence`` the record is the
        durable fail-closed FENCE (020): the same current
        retained record set recorded WITH the quarantine
        flag and the ``quarantine_fence`` reason regardless
        of the owner's live flag -- the fail-closed
        generation a crash between the fence and the
        transition cannot resume into old usable
        governance."""
        # The DETECTABLE forbidden-credential quarantine
        # runs BEFORE any durable record is published
        # (the lazy import keeps the model / codec split
        # cycle-free): a checkpoint carrying a detectable
        # forbidden credential is refused here, never
        # redacted.
        from .recovery_codec import recovery_record_credential_scan

        snapshot = owner.snapshot
        if snapshot is None:
            raise RecoveryRecordError(RecoveryRecordError.MESSAGE)
        state = snapshot.state
        quarantined = bool(owner.quarantined) or quarantine_fence
        payload = {
            "record_version": RECOVERY_RECORD_CONTRACT_VERSION,
            "policy_version": RECOVERY_RECORD_POLICY_VERSION,
            "namespace": snapshot.namespace.model_dump(mode="json"),
            "d_state": state.d_state.model_dump(mode="json"),
            "root_facts": [fact.model_dump(mode="json") for fact in state.root_facts],
            "revision": state.revision,
            "prior_epoch": owner.epoch,
            "resume_reason": (
                RecoveryResumeReason.QUARANTINE_FENCE
                if quarantined
                else RecoveryResumeReason.RESTART
            ),
            "quarantined": quarantined,
        }
        payload_digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
                "utf-8"
            )
        ).hexdigest()
        record = cls(
            record_version=RECOVERY_RECORD_CONTRACT_VERSION,
            policy_version=RECOVERY_RECORD_POLICY_VERSION,
            namespace=snapshot.namespace,
            d_state=state.d_state,
            root_facts=tuple(state.root_facts),
            revision=state.revision,
            prior_epoch=owner.epoch,
            resume_reason=payload["resume_reason"],
            quarantined=quarantined,
            payload_digest=payload_digest,
        )
        recovery_record_credential_scan(record)
        return record

    def with_epoch_binding(self, prior_epoch: int) -> RecoveryRecord:
        """Rebind the durable recovery epoch binding to the
        ACTUAL live cache epoch of the incarnation that
        loaded this record (the resume restart bookkeeping):
        the exact original bundles and provenance, the
        complete namespace binding, the revision, the
        recorded reason and the quarantine state are
        preserved VERBATIM -- only ``prior_epoch`` changes.
        The canonical digest is recomputed over the rebound
        payload and the ONE closed construction re-verifies
        every law (including the digest re-binding and the
        detectable-credential quarantine); a value-equal
        rebinding returns the SAME record, so a no-op
        rewrite is never published (the generation
        serializes publication, and this is epoch
        bookkeeping, never a usage-timestamp rewrite)."""
        if isinstance(prior_epoch, bool) or not isinstance(prior_epoch, int) or prior_epoch < 1:
            raise RecoveryRecordError(RecoveryRecordError.MESSAGE)
        if prior_epoch == self.prior_epoch:
            return self
        payload = {
            "record_version": RECOVERY_RECORD_CONTRACT_VERSION,
            "policy_version": RECOVERY_RECORD_POLICY_VERSION,
            "namespace": self.namespace.model_dump(mode="json"),
            "d_state": self.d_state.model_dump(mode="json"),
            "root_facts": [fact.model_dump(mode="json") for fact in self.root_facts],
            "revision": self.revision,
            "prior_epoch": prior_epoch,
            "resume_reason": self.resume_reason,
            "quarantined": self.quarantined,
        }
        payload_digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
                "utf-8"
            )
        ).hexdigest()
        record = RecoveryRecord(
            record_version=RECOVERY_RECORD_CONTRACT_VERSION,
            policy_version=RECOVERY_RECORD_POLICY_VERSION,
            namespace=self.namespace,
            d_state=self.d_state,
            root_facts=tuple(self.root_facts),
            revision=self.revision,
            prior_epoch=prior_epoch,
            resume_reason=self.resume_reason,
            quarantined=self.quarantined,
            payload_digest=payload_digest,
        )
        from .recovery_codec import recovery_record_credential_scan

        recovery_record_credential_scan(record)
        return record
