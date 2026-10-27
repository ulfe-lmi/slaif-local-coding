"""Inert versioned fixture identity contract (017-z, software-only).

This module defines closed, immutable fixture identity DESCRIPTIONS for
the disposable native-fixture work and a bounded READ-ONLY host-owner
identity collector. It is INERT:

* importing it, or calling any of its functions, selects NO live fixture
  profile, records NO fixture admission, yields NO ready or native
  verdict, and performs NO external operation (no filesystem or proc
  traversal, no environment/config/profile/credential read, no network,
  no subprocess, no signal, no UID/GID/group/privilege/prctl/kernel
  mutation);
* a valid closed data record may be DECODED into an immutable
  description — that is a pure data transformation, not measurement
  authority; serialization validity does not prove that the IDs came
  from an OS observation;
* a fingerprint is a deterministic canonical CONFIGURATION digest of a
  complete description. It is not a process hash, a trusted identity
  receipt, an admission, a cache key or a readiness certificate;
* the original fixed controller 21001 / subject 21002 profile remains
  the current fixture identity; every old record/schema/constant
  meaning is unchanged, and no old actual-evidence record is migrated,
  rewritten or reinterpreted by this module;
* the required LATER integration boundary is described, not
  implemented: a later sealed child must select a canonical profile,
  collect/freeze the actual owner IDs, bind them to its ORIGINAL
  verified order/head/run and live admission BEFORE external work, and
  revalidate the same context at actual use. This module opens no path
  through the existing local CLI, defaults or validators.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass

# -- closed vocabulary --------------------------------------------------------

RECORD_SCHEMA = "slaif-fixture-identity-record-v1"

# Explicitly named identity description profiles, distinct from adapter
# cache profiles. The original profile stays the current fixture identity;
# the owner-UID profile is an INERT candidate for a possible later,
# separately ordered fixture whose nonroot subject matches its
# unprivileged host owner.
PROFILE_ORIGINAL = "slaif-fixture-identity-original-v1"
PROFILE_OWNER_UID = "slaif-fixture-identity-owner-uid-v1"
KNOWN_PROFILES: tuple[str, ...] = (PROFILE_ORIGINAL, PROFILE_OWNER_UID)

# Fixed fixture controller identity (unchanged production constant values;
# the original 21002 subject law stays intact as well).
CONTROLLER_UID = 21001
CONTROLLER_GID = 21001
ORIGINAL_SUBJECT_UID = 21002
ORIGINAL_SUBJECT_GID = 21002

# Linux numeric IDs are bound to 1..4294967294 inclusive: 0 (root), -1
# and the u32 max 4294967295 are never admitted by this contract.
LINUX_ID_MIN = 1
LINUX_ID_MAX = 4294967294

# Bounded codec: a record is at most this many bytes.
MAX_RECORD_BYTES = 4096
# Bounded field strings: the profile name is the only string field.
MAX_PROFILE_NAME_BYTES = 64


class FixtureIdentityError(ValueError):
    """Closed refusal. ``reason`` is a fixed code and never echoes input."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# -- closed data records -------------------------------------------------------


@dataclass(frozen=True)
class HostOwnerIds:
    """One raw, complete identity observation of the calling process.

    A plain data container: the three values of each kind (real /
    effective / saved) are NOT assumed equal here. Completeness and
    contract bounds are enforced by the collector's data-validation
    layer and by :func:`derive_owner_uid_identity`, never inferred from
    another field.
    """

    real_uid: int
    effective_uid: int
    saved_uid: int
    real_gid: int
    effective_gid: int
    saved_gid: int


@dataclass(frozen=True)
class FixtureIdentityDescription:
    """Immutable fixture identity description (closed, named, inert).

    Owns immutable tuples/data only. A decoded record, a profile name,
    a fingerprint or caller flags built around this value never
    establish measured authority.
    """

    profile: str
    controller_uid: int
    controller_gid: int
    subject_uid: int
    subject_gid: int
    subject_groups: tuple[int, ...]

    def __post_init__(self) -> None:
        # Closed immutable construction contract: a description is
        # ALWAYS fully valid when it exists. The group container is
        # length-checked BEFORE any copy (an arbitrarily large caller
        # vector is refused without being copied), then owned as a
        # fresh one-element tuple, and the complete field laws are
        # enforced through the production validator. No other
        # container, field type, profile or ID is admitted; no caller
        # alias is ever retained.
        if not isinstance(self.subject_groups, (list, tuple)):
            raise FixtureIdentityError("invalid-group-vector")
        if len(self.subject_groups) != 1:
            raise FixtureIdentityError("invalid-group-vector")
        object.__setattr__(self, "subject_groups", (self.subject_groups[0],))
        validate_description(self)


@dataclass(frozen=True)
class HostIdentityOutcome:
    """Explicit collector outcome: ok observation or fixed refusal code.

    ``reason`` is None on success, else one of: ``unsupported-platform``
    (the OS identity getters are absent), ``id-getter-failure`` (the raw
    read failed or did not yield the complete six-value contract),
    ``invalid-id-type``, ``root-id`` or ``invalid-id-range`` (the data
    validation layer refused the observation).
    """

    ok: bool
    ids: HostOwnerIds | None
    reason: str | None


IdentityReader = Callable[[], tuple[int, int, int, int, int, int]]


# -- strict ID law ---------------------------------------------------------------


def _check_id(value: object) -> int:
    """One closed Linux ID: strict finite int, nonroot, 1..4294967294."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FixtureIdentityError("invalid-id-type")
    if value == 0:
        raise FixtureIdentityError("root-id")
    if value < LINUX_ID_MIN or value > LINUX_ID_MAX:
        raise FixtureIdentityError("invalid-id-range")
    return value


def _check_triple(name: str, real: object, effective: object, saved: object) -> int:
    checked_real = _check_id(real)
    checked_effective = _check_id(effective)
    checked_saved = _check_id(saved)
    if not (checked_real == checked_effective == checked_saved):
        raise FixtureIdentityError(f"{name}-triple-mismatch")
    return checked_real


# -- description construction and validation ------------------------------------


def validate_description(
    description: FixtureIdentityDescription,
) -> FixtureIdentityDescription:
    """Strict closed validation of a description; refuses non-echoing.

    Enforces: known profile; controller fixed at 21001/21001; strict
    nonroot finite IDs in the closed Linux range; expected subject
    groups exactly the primary GID; the original profile's exact
    21002 subject; and the owner-UID profile's subject distinct from
    the controller identity.
    """
    profile = description.profile
    if not isinstance(profile, str) or profile not in KNOWN_PROFILES:
        raise FixtureIdentityError("invalid-profile")
    controller_uid = _check_id(description.controller_uid)
    controller_gid = _check_id(description.controller_gid)
    if (controller_uid, controller_gid) != (CONTROLLER_UID, CONTROLLER_GID):
        raise FixtureIdentityError("controller-mismatch")
    subject_uid = _check_id(description.subject_uid)
    subject_gid = _check_id(description.subject_gid)
    groups = description.subject_groups
    if not isinstance(groups, tuple) or len(groups) != 1 or _check_id(groups[0]) != subject_gid:
        raise FixtureIdentityError("invalid-group-vector")
    if profile == PROFILE_ORIGINAL and (subject_uid, subject_gid) != (
        ORIGINAL_SUBJECT_UID,
        ORIGINAL_SUBJECT_GID,
    ):
        raise FixtureIdentityError("invalid-subject-for-profile")
    if profile == PROFILE_OWNER_UID and (
        subject_uid == CONTROLLER_UID or subject_gid == CONTROLLER_GID
    ):
        raise FixtureIdentityError("controller-id-collision")
    return description


def original_fixture_identity() -> FixtureIdentityDescription:
    """The ORIGINAL fixed controller 21001 / subject 21002 description.

    Takes no caller arguments: there is no caller-selected UID, argv,
    root fallback, environment override or silent default.
    """
    return validate_description(
        FixtureIdentityDescription(
            profile=PROFILE_ORIGINAL,
            controller_uid=CONTROLLER_UID,
            controller_gid=CONTROLLER_GID,
            subject_uid=ORIGINAL_SUBJECT_UID,
            subject_gid=ORIGINAL_SUBJECT_GID,
            subject_groups=(ORIGINAL_SUBJECT_GID,),
        )
    )


def derive_owner_uid_identity(observed: HostOwnerIds) -> FixtureIdentityDescription:
    """Derive the INERT owner-UID candidate from one complete observation.

    The subject UID/GID must equal the captured eligible host owner's
    real/effective/saved values with all three values of each kind
    equal, nonroot, strict finite Linux IDs and distinct from the
    controller identity. Expected subject groups are exactly the
    primary GID — never copied from host supplementary groups.
    """
    subject_uid = _check_triple(
        "uid", observed.real_uid, observed.effective_uid, observed.saved_uid
    )
    subject_gid = _check_triple(
        "gid", observed.real_gid, observed.effective_gid, observed.saved_gid
    )
    if subject_uid == CONTROLLER_UID or subject_gid == CONTROLLER_GID:
        raise FixtureIdentityError("controller-id-collision")
    return validate_description(
        FixtureIdentityDescription(
            profile=PROFILE_OWNER_UID,
            controller_uid=CONTROLLER_UID,
            controller_gid=CONTROLLER_GID,
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            subject_groups=(subject_gid,),
        )
    )


# -- bounded closed codec -----------------------------------------------------------

_TOP_KEYS = frozenset({"schema", "profile", "controller", "subject"})
_CONTROLLER_KEYS = frozenset({"uid", "gid"})
_SUBJECT_KEYS = frozenset({"uid", "gid", "groups"})


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FixtureIdentityError("duplicate-key")
        result[key] = value
    return result


def encode_description(description: FixtureIdentityDescription) -> bytes:
    """Canonical closed record bytes for a validated description."""
    validate_description(description)
    payload = {
        "schema": RECORD_SCHEMA,
        "profile": description.profile,
        "controller": {
            "uid": description.controller_uid,
            "gid": description.controller_gid,
        },
        "subject": {
            "uid": description.subject_uid,
            "gid": description.subject_gid,
            "groups": list(description.subject_groups),
        },
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def decode_description(data: bytes) -> FixtureIdentityDescription:
    """Strict closed decoding: bounded, exact, non-echoing.

    Decoding a valid record is a pure data transformation into an
    immutable description — it establishes no measurement authority:
    nothing here proves the IDs came from an OS observation.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise FixtureIdentityError("invalid-record-type")
    # Bound BEFORE the copy: an over-bound input is refused without a
    # proportional bytes() copy of the caller's data.
    if len(data) > MAX_RECORD_BYTES:
        raise FixtureIdentityError("over-bound")
    raw = bytes(data)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise FixtureIdentityError("malformed-record") from None
    try:
        payload = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except FixtureIdentityError:
        raise
    except Exception:
        raise FixtureIdentityError("malformed-record") from None
    if not isinstance(payload, dict):
        raise FixtureIdentityError("malformed-record")
    body = set(payload)
    if _TOP_KEYS - body:
        raise FixtureIdentityError("missing-field")
    if body - _TOP_KEYS:
        raise FixtureIdentityError("unknown-field")
    schema = payload["schema"]
    if not isinstance(schema, str) or schema != RECORD_SCHEMA:
        raise FixtureIdentityError("unknown-schema")
    profile = payload["profile"]
    if (
        not isinstance(profile, str)
        or len(profile) > MAX_PROFILE_NAME_BYTES
        or profile not in KNOWN_PROFILES
    ):
        raise FixtureIdentityError("invalid-profile")
    controller = payload["controller"]
    if not isinstance(controller, dict):
        raise FixtureIdentityError("invalid-record-type")
    if _CONTROLLER_KEYS - set(controller):
        raise FixtureIdentityError("missing-field")
    if set(controller) - _CONTROLLER_KEYS:
        raise FixtureIdentityError("unknown-field")
    subject = payload["subject"]
    if not isinstance(subject, dict):
        raise FixtureIdentityError("invalid-record-type")
    if _SUBJECT_KEYS - set(subject):
        raise FixtureIdentityError("missing-field")
    if set(subject) - _SUBJECT_KEYS:
        raise FixtureIdentityError("unknown-field")
    groups_raw = subject["groups"]
    if not isinstance(groups_raw, list):
        raise FixtureIdentityError("invalid-group-vector")
    description = FixtureIdentityDescription(
        profile=profile,
        controller_uid=controller["uid"],
        controller_gid=controller["gid"],
        subject_uid=subject["uid"],
        subject_gid=subject["gid"],
        subject_groups=tuple(groups_raw),
    )
    return validate_description(description)


# -- deterministic canonical configuration fingerprint ------------------------------


def fingerprint_description(description: FixtureIdentityDescription) -> str:
    """Deterministic canonical CONFIGURATION fingerprint of a description.

    Binds the complete profile semantics (profile name, controller and
    subject identity, expected groups) and changes on any real
    identity/configuration change. It is not a process hash, a trusted
    identity receipt, an admission, a cache key or a readiness
    certificate, and it depends on no request counter or unrelated
    state.
    """
    validate_description(description)
    canonical = json.dumps(
        {
            "controller_gid": description.controller_gid,
            "controller_uid": description.controller_uid,
            "profile": description.profile,
            "subject_gid": description.subject_gid,
            "subject_groups": list(description.subject_groups),
            "subject_uid": description.subject_uid,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


# -- bounded read-only host-owner identity collection ---------------------------------


def _default_identity_reader() -> tuple[int, int, int, int, int, int]:
    """ONE read-only collection of the complete real/eff/saved IDs.

    Direct stdlib OS identity getters only (getresuid/getresgid plus
    the simple uid/euid/gid/egid getters, cross-checked, never used to
    infer a missing value); no filesystem/proc traversal, no
    environment/config/profile read, no subprocess, no signal, no
    mutation, no credential handling.
    """
    real_uid, effective_uid, saved_uid = os.getresuid()
    real_gid, effective_gid, saved_gid = os.getresgid()
    if (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (
        real_uid,
        effective_uid,
        real_gid,
        effective_gid,
    ):
        raise OSError("identity getters disagree")
    return real_uid, effective_uid, saved_uid, real_gid, effective_gid, saved_gid


def collect_host_owner_ids(
    reader: IdentityReader = _default_identity_reader,
) -> HostIdentityOutcome:
    """Bounded READ-ONLY collection; explicit unsupported/unavailable.

    The raw read seam (``reader``) is the only test seam: it replaces
    the raw OS read ONLY. Data validation and derivation stay
    production code; a positive outcome always passes through them.
    The reader is invoked exactly once per collection.
    """
    try:
        real_uid, effective_uid, saved_uid, real_gid, effective_gid, saved_gid = reader()
    except AttributeError:
        return HostIdentityOutcome(False, None, "unsupported-platform")
    except Exception:
        return HostIdentityOutcome(False, None, "id-getter-failure")
    try:
        checked = (
            _check_id(real_uid),
            _check_id(effective_uid),
            _check_id(saved_uid),
            _check_id(real_gid),
            _check_id(effective_gid),
            _check_id(saved_gid),
        )
    except FixtureIdentityError as exc:
        return HostIdentityOutcome(False, None, exc.reason)
    return HostIdentityOutcome(True, HostOwnerIds(*checked), None)
