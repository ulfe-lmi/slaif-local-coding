"""The closed sealed-entry to runtime-profile selection (017-aa).

This module is the ONE small shared runtime-profile helper of the
owner-UID fixture integration: it maps each SEALED entry id to the
identity profile that entry may select, and it derives the closed
container/runtime view (subject UID, subject GID, the exact
``uid:gid`` exec user, the expected effective groups, the closed
build-arg form and the baked profile DATA bytes) from a VALIDATED
identity description.

Closed laws:

* the mapping is the complete closed set — a known order id pairs
  with exactly one profile and nothing else; an unknown entry id,
  an unknown profile name, a cross-entry pair or a caller-selected
  UID/GID/argv is a fixed non-echoing refusal.  There is no
  environment variable, CLI flag, header or file presence that can
  select a profile: only the sealed entry (whose order is resolved
  and admitted in the sealed child) selects one.
* the original entries (017-s / 017-x / 017-y) keep the exact
  historical fixed controller 21001 / subject 21002 behavior,
  defaults, record meanings and refusals — the original view is
  built from the original constants and carries NO build args and
  NO profile DATA file.
* the owner-UID profile (selected ONLY by the canonical future
  017-ab and 017-ad sealed entries) is derived from a description that has
  ALREADY passed Z's production validation
  (:mod:`cache_native_fixture_identity`); this module re-runs that
  validation (cheap, production code) and adds nothing to it.  UID
  and GID stay INDEPENDENT: the exec user is always built from the
  two separately validated values, never ``uid:uid``.
* the baked profile DATA file is the Z closed canonical record
  bytes (``encode_description``): a data file, not host authority.
  Its fixed in-image path and the fixed build-arg form are the only
  two surfaces of the new image variant; missing, unknown,
  mismatched or unsafe DATA under the new path fails closed in the
  image build itself and never falls back to the original profile.
* the future 017-ab entry is INACTIVE until its own order is
  activated: this module names it (the canonical future entry) but
  grants it no authority — under any other active order the real
  repository-context validation refuses 017-ab before external
  fixture work or admission.  The canonical FUTURE native entry
  017-ad is fixed the same way (INERT, input-gated, unqualified):
  it selects the SAME owner-UID profile and carries the DISTINCT
  versioned identity-bearing native record tags; under any other
  active order the repository-context validation refuses 017-ad
  before external fixture work or admission.
* the canonical FUTURE native-PTY qualification entry 017-af
  (017-ae: INERT, input-gated, unqualified) is fixed the same
  way: it selects the SAME owner-UID profile through the closed
  entry mapping and carries the DISTINCT versioned
  identity-bearing record tags of the native-PTY
  qualification (plus the DISTINCT attach-binding record).
  INERT means the REAL active/order/admission gates refuse
  017-af while any other order (in particular the current
  017-ae) is active — BEFORE admission or external fixture
  work — and no real AF order, namespace, admission or owner
  is created in this round; its later actual qualification is
  a separately authorized order, never a replay of a closed
  round.
* the entry mapping and every RuntimeProfile are IMMUTABLE: the
  selection table is a read-only view (no per-owner or caller
  mutation), and a RuntimeProfile owns immutable copies of every
  container field (bounded length checked BEFORE any copy) under
  the complete field/profile/exec-user/build-arg/profile-DATA
  consistency law.

This module is inert data selection: no filesystem, environment,
network or process access, and no fixture admission of any kind.
"""

from __future__ import annotations

import types
from dataclasses import dataclass

import cache_native_fixture_identity as fidentity

# -- the canonical future sealed entry (INACTIVE) ------------------------------

AB_ORDER_ID = "017-ab"
AB_ORDER_PATH = "oap/orders/017-ab-owner-uid-python-capability-qualification.md"
AB_DRIVER_RECORD = "slaif-017ab-owner-uid-exec-capability-v1"

# The DISTINCT closed AB owner-run evidence tag/scope (the
# identity-bearing owner state/evidence record; the old
# native-scope tag stays strictly its original meaning).
AB_OWNER_RUN_EVIDENCE_SCHEMA = "slaif-017ab-owner-run-evidence-v1"
AB_OWNER_RUN_SCOPE = "slaif-017ab-owner-uid-scope"

# The canonical FUTURE native-order entry (017-ac: INERT,
# input-gated, unqualified — the next order after AB).  It
# selects ONLY the owner-UID profile, exactly as AB does, and
# carries the DISTINCT versioned identity-bearing record tags
# of the native handoff (the original native-scope tags keep
# their strict original meaning and refuse the new profile
# record).  Registering it is NOT activating it: under any
# other active order the real repository-context validation
# refuses 017-ad before external fixture work or admission.
AD_ORDER_ID = "017-ad"
AD_ORDER_PATH = "oap/orders/017-ad-owner-uid-native-handoff-qualification.md"
AD_DRIVER_RECORD = "slaif-017ad-owner-uid-native-handoff-v1"
AD_OWNER_STATE_SCHEMA = "slaif-017ad-owner-state-v1"
AD_NATIVE_RUN_EVIDENCE_SCHEMA = "slaif-017ad-native-owner-run-evidence-v1"
AD_NATIVE_RUN_SCHEMA = "slaif-017ad-native-owner-run-v1"
AD_OWNER_RUN_SCOPE = "slaif-017ad-owner-uid-scope"

# The canonical FUTURE native-PTY qualification entry (017-ae:
# INERT, input-gated, unqualified): the LATER separately
# authorized actual qualification round.  It selects the SAME
# owner-UID profile through the closed entry mapping (exactly
# as AB and AD do) and carries the DISTINCT versioned
# identity-bearing record tags of the native-PTY
# qualification — the closed EXISTING records (the original,
# the AB and the AD forms) keep their exact historical key
# sets and tag laws byte-for-byte, and 017-ad in particular
# stays CLOSED and unchanged (its round is complete; no new
# AD record form is minted here).  INERT means the REAL
# active/order/admission gates refuse 017-af while ANY other
# order (in particular the current 017-ae) is active — BEFORE
# admission or external fixture work (proven in hermetic
# synthetic repositories only): no real AF order, no AF
# namespace, no AF admission, no AF owner is created in this
# round.  Registering the constants is NOT activating the
# entry.
AF_ORDER_ID = "017-af"
AF_ORDER_PATH = "oap/orders/017-af-owner-uid-native-pty-qualification.md"
AF_OWNER_STATE_SCHEMA = "slaif-017af-owner-state-v1"
AF_NATIVE_RUN_EVIDENCE_SCHEMA = "slaif-017af-native-owner-run-evidence-v1"
AF_NATIVE_RUN_SCHEMA = "slaif-017af-native-owner-run-v1"
AF_OWNER_RUN_SCOPE = "slaif-017af-owner-uid-scope"
# The DISTINCT identity-bearing attach-binding record of the
# native attach-binding phase owned by the selected native
# entry (017-ae software, 017-af qualification): the measured
# fixture-namespace devpts baseline, the second bounded
# observation, the UNIQUE fresh owned allocation and the
# independently derived expected proc tty_nr (the primary-
# source-verified new_encode_dev encoding, distinct from the
# kernel-internal MKDEV layout).  The record is bound to the
# AF entry's exact order in its own tag-pair law; the attach-
# binding facts live in this distinct honest version, never
# widened into an old consumer.
AF_NATIVE_ATTACH_BINDING_SCHEMA = "slaif-017af-native-attach-binding-v1"

# The canonical FUTURE native-PTY REQUALIFICATION entry
# (017-ag: INERT, input-gated, unqualified): the LATER
# separately authorized actual requalification round of the
# AF entry's native scope.  It selects the SAME owner-UID
# profile through the closed entry mapping (exactly as AB,
# AD and AF do) and composes the EXISTING owner/guarded
# exact-CID/NativeOwnerRun and independent devpts producer
# APIs with their unchanged bounds; it carries the DISTINCT
# versioned identity-bearing record tags of the 017-ah
# requalification — the closed EXISTING records (the
# original, the AB, the AD, the AE and the AF forms) keep
# their exact historical key sets and tag laws byte-for-byte,
# and 017-af in particular stays CLOSED and unchanged (its
# round is complete; no new AF record form is minted here).
# INERT means the REAL active/order/admission gates refuse
# 017-ah while ANY other order (in particular the current
# 017-ag) is active — BEFORE admission or external fixture
# work: no real AH order, no AH namespace, no AH admission,
# no AH owner is created in this round.  Registering the
# constants is NOT activating the entry.
AH_ORDER_ID = "017-ah"
AH_ORDER_PATH = "oap/orders/017-ah-owner-uid-native-pty-requalification.md"
AH_OWNER_STATE_SCHEMA = "slaif-017ah-owner-state-v1"
AH_NATIVE_RUN_EVIDENCE_SCHEMA = "slaif-017ah-native-owner-run-evidence-v1"
AH_NATIVE_RUN_SCHEMA = "slaif-017ah-native-owner-run-v1"
AH_OWNER_RUN_SCOPE = "slaif-017ah-owner-uid-scope"
# The DISTINCT identity-bearing attach-binding record tag of
# the AH entry's native attach-binding phase: the SAME closed
# structural core as the AF record under the AH entry's own
# tag-pair law (the AF tag remains AF-only, even for
# equal-numeric identities).
AH_NATIVE_ATTACH_BINDING_SCHEMA = "slaif-017ah-native-attach-binding-v1"

# The canonical FUTURE native-process format QUALIFICATION
# entry (017-ai: INERT, input-gated, unqualified): the LATER
# separately authorized actual format qualification round.
# It selects the SAME owner-UID profile through the closed
# entry mapping (exactly as AB, AD, AF and AH do) and
# composes the EXISTING owner/guarded exact-CID/NativeOwnerRun
# and independent devpts producer APIs with their unchanged
# bounds; the canonical entry selects the CLOSED native
# format-capture scenario BEFORE startup through the existing
# reviewed configuration transport (the trusted owner carries
# it; the transport is not authority — caller environment
# presence/values, HTTP flags or user-authored ready records
# never select or advance the scenario); it carries the
# DISTINCT versioned identity-bearing record tags of the
# 017-aj qualification AND the NEW strict selected native
# format-capture record tag — the closed EXISTING records
# (the original, the AB, the AD, the AE, the AF and the AH
# forms) keep their exact historical key sets and tag laws
# byte-for-byte, and 017-ah in particular stays CLOSED and
# unchanged (its round is complete; no new AH record form is
# minted here).  INERT means the REAL active/order/admission
# gates refuse 017-aj while ANY other order (in particular
# the current 017-ai) is active — BEFORE admission or
# external fixture work: no real AJ order, no AJ namespace,
# no AJ admission, no AJ owner is created in this round.
# Registering the constants is NOT activating the entry.
AJ_ORDER_ID = "017-aj"
AJ_ORDER_PATH = "oap/orders/017-aj-native-process-format-qualification.md"
AJ_OWNER_STATE_SCHEMA = "slaif-017aj-owner-state-v1"
AJ_NATIVE_RUN_EVIDENCE_SCHEMA = "slaif-017aj-native-owner-run-evidence-v1"
AJ_NATIVE_RUN_SCHEMA = "slaif-017aj-native-owner-run-v1"
AJ_OWNER_RUN_SCOPE = "slaif-017aj-owner-uid-scope"
AJ_NATIVE_ATTACH_BINDING_SCHEMA = "slaif-017aj-native-attach-binding-v1"
# The NEW strict selected native format-capture record of the
# 017-aj entry: the bounded deterministic tool scenario (the
# four serial exec cases plus the empty-stdin polls across
# the ONE running process), the strict formatter/source/byte
# verified selected frames against the immutable pre-launch
# seed identity, and the closed non-acquiring truncation
# fact.  It is a DISTINCT closed record, never a relabeled
# diagnostic or stand-in tag.
AJ_NATIVE_FORMAT_CAPTURE_SCHEMA = "slaif-017aj-native-format-capture-v1"
# The CLOSED native format scenario selected by the canonical
# 017-aj entry BEFORE startup (a closed enum value of the
# controller's construction-time scenario law; a request body
# can never select, switch or advance it).
AJ_FORMAT_SCENARIO = "format-capture"
# The closed NATIVE executable-measurement bounds of the 017-ad
# entry: exactly 320 MiB (335544320 bytes) and 10 s — a
# justified measurement bound for the pinned native artifact
# (308139304 bytes fits this finite cap), further clamped AT
# USE to the SAME remaining owner END (never a fresh phase
# deadline, never a refreshed budget).  The Python entries keep
# the historical 16 MiB / 10 s defaults unchanged.
AD_EXE_MAX_BYTES = 320 * 1024 * 1024  # 335544320
AD_EXE_DEADLINE_SECONDS = 10.0

# The new owner-profile Dockerfile (repository-only source; the
# original fixture Dockerfile stays byte-for-byte the original).
OWNER_DOCKERFILE_NAME = "cache_native_fixture_owner.Dockerfile"

# The closed profile DATA surfaces of the new image variant.
PROFILE_DATA_NAME = "fixture-identity.json"
PROFILE_DATA_PATH = f"/opt/slaif-fixture/{PROFILE_DATA_NAME}"

# The inert identity contract module (repository-only source, copied
# into the OWNER-variant build context only: it is the single
# in-image source of truth for the subject identity; the original
# build context never contains it).
IDENTITY_MODULE_NAME = "cache_native_fixture_identity.py"

# The closed build-arg vocabulary of the owner-profile variant
# (the controller identity stays fixed at 21001/21001: only the
# subject ARGs vary, and only with the frozen validated values).
# The profile ARG carries the CANONICAL closed profile name (the
# identity module's single closed vocabulary): the owner Dockerfile
# build step asserts the received value against the same
# production constant, so producer and consumer can never drift.
_BUILD_ARG_PROFILE = (
    "--build-arg",
    f"SLAIF_FIXTURE_PROFILE={fidentity.PROFILE_OWNER_UID}",
)


class ProfileError(ValueError):
    """Closed refusal of profile selection. Fixed code, no echo."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# -- the closed entry -> profile mapping ----------------------------------------

PROFILE_ORIGINAL = fidentity.PROFILE_ORIGINAL
PROFILE_OWNER_UID = fidentity.PROFILE_OWNER_UID

# The COMPLETE closed mapping: a known entry id selects exactly one
# profile.  The original entries keep the historical original
# profile; ONLY the canonical future 017-ab entry selects the
# owner-UID profile.  Anything else refuses.
_ENTRY_PROFILES_LITERAL: dict[str, str] = {
    "017-s": PROFILE_ORIGINAL,
    "017-x": PROFILE_ORIGINAL,
    "017-y": PROFILE_ORIGINAL,
    AB_ORDER_ID: PROFILE_OWNER_UID,
    # the canonical FUTURE native entry (INERT in 017-ac): the
    # SAME owner-UID profile selection, distinct native records
    AD_ORDER_ID: PROFILE_OWNER_UID,
    # the canonical FUTURE native-PTY qualification entry
    # (INERT in 017-ae): the SAME owner-UID profile selection
    # through the existing owner composition — inertness is the
    # REAL active/order/admission gate refusing 017-af under
    # any other active order, never a missing profile mapping
    AF_ORDER_ID: PROFILE_OWNER_UID,
    # the canonical FUTURE native-PTY REQUALIFICATION entry
    # (INERT in 017-ag): the SAME owner-UID profile selection
    # through the existing owner composition — inertness is the
    # REAL active/order/admission gate refusing 017-ah under
    # any other active order, never a missing profile mapping
    AH_ORDER_ID: PROFILE_OWNER_UID,
    # the canonical FUTURE native-process format QUALIFICATION
    # entry (INERT in 017-ai): the SAME owner-UID profile
    # selection through the existing owner composition; the
    # entry additionally selects the CLOSED native
    # format-capture scenario before startup; inertness is the
    # REAL active/order/admission gate refusing 017-aj under
    # any other active order, never a missing profile mapping
    AJ_ORDER_ID: PROFILE_OWNER_UID,
}

# The immutable canonical entry mapping: no per-owner or caller
# mutation of the selection table is possible (the literal stays
# private; the public name is the read-only view).
ENTRY_PROFILES: types.MappingProxyType[str, str] = types.MappingProxyType(_ENTRY_PROFILES_LITERAL)


def entry_profile_name(order_id: object) -> str:
    """The closed sealed-entry profile selection.

    ``order_id`` must be one of the known sealed entry ids; an
    unknown id, a non-string, or a caller attempt to select a
    profile by any other means is a fixed refusal (the function
    takes no profile argument at all)."""
    if not isinstance(order_id, str):
        raise ProfileError("profile-entry-unknown")
    try:
        return ENTRY_PROFILES[order_id]
    except KeyError:
        raise ProfileError("profile-entry-unknown") from None


# -- the closed runtime profile view ---------------------------------------------

# Bounded copy limits for the caller containers the constructor
# owns (checked BEFORE any copy of a caller vector): the closed
# expected-groups form is exactly one element, and the closed
# build-arg form is exactly six elements — arbitrarily large caller
# vectors are refused without being copied.
_EXPECTED_GROUPS_MAX = 1
_BUILD_ARGS_MAX = 8


def _check_subject_id(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProfileError(f"profile-{name}-invalid")
    if value == 0:
        raise ProfileError(f"profile-{name}-root")
    if value < fidentity.LINUX_ID_MIN or value > fidentity.LINUX_ID_MAX:
        raise ProfileError(f"profile-{name}-range")
    return value


def _check_groups_element(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProfileError("profile-groups-element")
    if value == 0:
        raise ProfileError("profile-groups-root")
    if value < fidentity.LINUX_ID_MIN or value > fidentity.LINUX_ID_MAX:
        raise ProfileError("profile-groups-range")
    return value


@dataclass(frozen=True)
class RuntimeProfile:
    """The closed container/runtime view of one identity profile.

    A plain immutable data object: it carries no admission, no
    readiness and no measured authority.  ``exec_user`` is the
    exact ``uid:gid`` string the owner-scoped guarded executor and
    the stand-in identity law admit for the subject (UID and GID
    independently validated, never assumed equal); ``expected_groups``
    is exactly the primary GID (never host supplementary groups);
    ``build_args`` is the closed owner-variant build-arg form (empty
    for the original profile — its build command stays byte-for-byte
    the historical one); ``profile_data`` is the closed canonical
    Z record bytes baked into the new image (None for the original
    profile — its build context stays byte-for-byte the historical
    one).

    Closed immutable construction contract: a RuntimeProfile is
    ALWAYS fully consistent when it exists.  The constructor owns
    immutable copies of every container field (bounded length
    checked BEFORE the copy) and enforces the complete field,
    profile, exec-user, build-arg and profile-DATA consistency law
    with fixed non-echoing errors — this is DATA validation, not
    measured authority: a valid closed data view is ordinary data,
    and nothing here is an admission token, registry entry or
    readiness receipt (the real owner's own collection/admission
    gate is a separate boundary)."""

    profile: str
    subject_uid: int
    subject_gid: int
    exec_user: str
    expected_groups: tuple[int, ...]
    build_args: tuple[str, ...]
    profile_data: bytes | None

    def __post_init__(self) -> None:
        # -- own the container fields (bounded BEFORE any copy) ----
        if not isinstance(self.expected_groups, (list, tuple)):
            raise ProfileError("profile-groups-type")
        if len(self.expected_groups) > _EXPECTED_GROUPS_MAX:
            raise ProfileError("profile-groups-overbound")
        object.__setattr__(self, "expected_groups", tuple(self.expected_groups))
        if not isinstance(self.build_args, (list, tuple)):
            raise ProfileError("profile-build-args-type")
        if len(self.build_args) > _BUILD_ARGS_MAX:
            raise ProfileError("profile-build-args-overbound")
        build_args = tuple(self.build_args)
        object.__setattr__(self, "build_args", build_args)
        # -- the closed profile name ---------------------------------
        if not isinstance(self.profile, str) or self.profile not in fidentity.KNOWN_PROFILES:
            raise ProfileError("profile-name-unknown")
        # -- the strict subject ID law (independent UID and GID) ------
        uid = _check_subject_id(self.subject_uid, "subject-uid")
        gid = _check_subject_id(self.subject_gid, "subject-gid")
        # -- the exact closed exec-user form (uid:gid, never uid:uid) -
        if not isinstance(self.exec_user, str):
            raise ProfileError("profile-exec-user-type")
        if self.exec_user != f"{uid}:{gid}":
            raise ProfileError("profile-exec-user-mismatch")
        # -- expected effective groups: exactly the primary GID -------
        if len(self.expected_groups) != 1 or _check_groups_element(self.expected_groups[0]) != gid:
            raise ProfileError("profile-groups-law")
        if self.profile == PROFILE_ORIGINAL:
            # The original view is the exact historical fixed view:
            # subject 21002/21002, NO build args, NO profile DATA.
            if (uid, gid) != (
                fidentity.ORIGINAL_SUBJECT_UID,
                fidentity.ORIGINAL_SUBJECT_GID,
            ):
                raise ProfileError("profile-original-subject")
            if build_args != ():
                raise ProfileError("profile-original-build-args")
            if self.profile_data is not None:
                raise ProfileError("profile-original-data")
            return
        # -- the owner-UID view ----------------------------------------
        if uid == fidentity.CONTROLLER_UID or gid == fidentity.CONTROLLER_GID:
            raise ProfileError("profile-controller-collision")
        if build_args != (
            _BUILD_ARG_PROFILE[0],
            _BUILD_ARG_PROFILE[1],
            "--build-arg",
            f"SLAIF_SUBJ_UID={uid}",
            "--build-arg",
            f"SLAIF_SUBJ_GID={gid}",
        ):
            raise ProfileError("profile-build-args-form")
        # The baked DATA must be the closed canonical Z record of
        # THIS view (production codec + strict validation): a
        # missing, malformed, foreign or inconsistent DATA view is a
        # fixed refusal (data consistency — not a provenance claim).
        if not isinstance(self.profile_data, (bytes, bytearray)):
            raise ProfileError("profile-data-type")
        if len(self.profile_data) > fidentity.MAX_RECORD_BYTES:
            raise ProfileError("profile-data-overbound")
        try:
            decoded = fidentity.decode_description(bytes(self.profile_data))
        except fidentity.FixtureIdentityError:
            raise ProfileError("profile-data-invalid") from None
        if (
            decoded.profile != PROFILE_OWNER_UID
            or (decoded.subject_uid, decoded.subject_gid) != (uid, gid)
            or decoded.subject_groups != (gid,)
            or (decoded.controller_uid, decoded.controller_gid)
            != (fidentity.CONTROLLER_UID, fidentity.CONTROLLER_GID)
        ):
            raise ProfileError("profile-data-mismatch")
        object.__setattr__(self, "profile_data", bytes(self.profile_data))


def original_runtime_profile() -> RuntimeProfile:
    """The ORIGINAL fixed controller 21001 / subject 21002 view.

    Takes no caller arguments: no caller-selected UID, no override
    and no silent default change.  This is the view every original
    (017-s / 017-x / 017-y) caller keeps, byte-for-byte."""
    uid = _check_subject_id(fidentity.ORIGINAL_SUBJECT_UID, "subject-uid")
    gid = _check_subject_id(fidentity.ORIGINAL_SUBJECT_GID, "subject-gid")
    return RuntimeProfile(
        profile=PROFILE_ORIGINAL,
        subject_uid=uid,
        subject_gid=gid,
        exec_user=f"{uid}:{gid}",
        expected_groups=(gid,),
        build_args=(),
        profile_data=None,
    )


def owner_runtime_profile(description: object) -> RuntimeProfile:
    """The closed owner-UID runtime view of one validated
    description.

    The description must be a Z ``FixtureIdentityDescription`` of
    the owner-UID profile that passes Z's PRODUCTION validation
    (re-run here — cheap and production code): controller fixed
    21001/21001, strict nonroot finite Linux IDs, expected groups
    exactly the primary GID, subject distinct from the controller.
    The exec user is built from the INDEPENDENT validated
    ``subject_uid`` and ``subject_gid`` (never ``uid:uid``), and the
    profile DATA is the Z closed canonical record bytes."""
    if not isinstance(description, fidentity.FixtureIdentityDescription):
        raise ProfileError("profile-description-type")
    try:
        fidentity.validate_description(description)
    except fidentity.FixtureIdentityError as exc:
        raise ProfileError(f"profile-description-{exc.reason}") from None
    if description.profile != PROFILE_OWNER_UID:
        raise ProfileError("profile-name-mismatch")
    uid = _check_subject_id(description.subject_uid, "subject-uid")
    gid = _check_subject_id(description.subject_gid, "subject-gid")
    if (description.controller_uid, description.controller_gid) != (
        fidentity.CONTROLLER_UID,
        fidentity.CONTROLLER_GID,
    ):
        raise ProfileError("profile-controller-mismatch")
    return RuntimeProfile(
        profile=PROFILE_OWNER_UID,
        subject_uid=uid,
        subject_gid=gid,
        exec_user=f"{uid}:{gid}",
        expected_groups=(gid,),
        build_args=(
            _BUILD_ARG_PROFILE[0],
            _BUILD_ARG_PROFILE[1],
            "--build-arg",
            f"SLAIF_SUBJ_UID={uid}",
            "--build-arg",
            f"SLAIF_SUBJ_GID={gid}",
        ),
        profile_data=fidentity.encode_description(description),
    )


def entry_runtime_profile(order_id: object, description: object | None = None) -> RuntimeProfile:
    """The closed selection for ONE sealed entry.

    Original entries always return the fixed original view and
    accept no caller input (the ``description`` argument must be
    None for them — a caller-supplied description is never a
    selection means).  The 017-ab entry requires exactly one
    description (the one the REAL owner derived from its own
    complete actual ID observation through Z's production
    collector/derivation; a caller-authored description is data,
    and the owner's own collection is what freezes it into the
    owner context)."""
    profile_name = entry_profile_name(order_id)
    if profile_name == PROFILE_ORIGINAL:
        if description is not None:
            raise ProfileError("profile-description-unexpected")
        return original_runtime_profile()
    if description is None:
        raise ProfileError("profile-description-missing")
    return owner_runtime_profile(description)
