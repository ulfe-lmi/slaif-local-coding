"""017-z: inert versioned fixture identity contract tests.

Software-only closed-contract proof for
``scripts/cache_native_fixture_identity.py`` (no CLI, no live path):

* the ORIGINAL fixed controller 21001 / subject 21002 description is
  exact, cross-bound to the unchanged production constants, round
  trips through the closed codec and keeps a stable canonical
  configuration fingerprint;
* the old 21002 record law is re-proved UNCHANGED through the
  production model validator (including its empty-group allowance —
  the new description law requiring exactly the primary GID is a new
  closed record, never a reinterpretation of old records);
* the INERT owner-UID candidate derives from one faithful eligible
  nonroot OS observation (each real/effective/saved triple equal,
  nonroot, distinct from the controller, groups exactly the primary
  GID — never host supplementary groups);
* mismatched triples, getter failure/missing support, root,
  controller collision, malformed/boolean/string/out-of-range IDs,
  missing/extra/contradictory fields, unknown profile/schema,
  duplicate keys and over-bound input are all closed non-echoing
  refusals;
* descriptions are closed immutable DATA: construction enforces the
  complete field laws (no caller alias retained, no oversized vector
  copied), and pure decoded/caller-authored data, profile names and
  fingerprints yield no ready/admission/native authority;
* the bounded READ-ONLY host-ID collector is driven through a narrow
  fake OS-read seam (one raw read per collection, production data
  validation never bypassed) plus one ACTUAL safe current-host UID
  read exercised as OS-data-only evidence (never containment or
  executable capability);
* importing/using the module performs no external operation and no
  existing fixture state change.

No Docker, namespaces, native binary, model/Gateway or live fixture
is invoked; no ``.oap-local/017-z`` root is created.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
IDENTITY_SCRIPT = REPO_ROOT / "scripts" / "cache_native_fixture_identity.py"
MODEL_SCRIPT = REPO_ROOT / "scripts" / "cache_native_fixture_model.py"

CLOSED_REASONS = frozenset(
    {
        "invalid-profile",
        "controller-mismatch",
        "controller-id-collision",
        "invalid-id-type",
        "root-id",
        "invalid-id-range",
        "uid-triple-mismatch",
        "gid-triple-mismatch",
        "invalid-group-vector",
        "invalid-subject-for-profile",
        "invalid-record-type",
        "over-bound",
        "malformed-record",
        "duplicate-key",
        "missing-field",
        "unknown-field",
        "unknown-schema",
        "unsupported-platform",
        "id-getter-failure",
    }
)

CONTRACT_NAMES = frozenset(
    {
        "FixtureIdentityDescription",
        "FixtureIdentityError",
        "HostIdentityOutcome",
        "HostOwnerIds",
        "collect_host_owner_ids",
        "decode_description",
        "derive_owner_uid_identity",
        "encode_description",
        "fingerprint_description",
        "original_fixture_identity",
        "validate_description",
        "LINUX_ID_MAX",
        "LINUX_ID_MIN",
        "MAX_RECORD_BYTES",
        "KNOWN_PROFILES",
        "CONTROLLER_GID",
        "CONTROLLER_UID",
        "ORIGINAL_SUBJECT_GID",
        "ORIGINAL_SUBJECT_UID",
        "PROFILE_OWNER_UID",
        "PROFILE_ORIGINAL",
        "RECORD_SCHEMA",
        "IdentityReader",
    }
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the module uses deferred annotations and
    # dataclasses resolve them through sys.modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fci = _load("cache_native_fixture_identity_z", IDENTITY_SCRIPT)
model = _load("cache_native_fixture_model_z", MODEL_SCRIPT)


def _obs(uid: int, gid: int) -> Any:
    return fci.HostOwnerIds(uid, uid, uid, gid, gid, gid)


def _refuse(func: Any, *args: Any) -> str:
    with pytest.raises(fci.FixtureIdentityError) as excinfo:
        func(*args)
    reason = excinfo.value.reason
    assert isinstance(reason, str) and reason in CLOSED_REASONS
    return reason


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": "slaif-fixture-identity-record-v1",
        "profile": fci.PROFILE_OWNER_UID,
        "controller": {"uid": 21001, "gid": 21001},
        "subject": {"uid": 1001, "gid": 1001, "groups": [1001]},
    }
    payload.update(overrides)
    return payload


_ORIGINAL_BYTES = fci.encode_description(fci.original_fixture_identity())
_DUPLICATE_TOP = (
    b'{"controller": {"gid": 21001, "uid": 21001},'
    b' "profile": "slaif-fixture-identity-owner-uid-v1",'
    b' "schema": "slaif-fixture-identity-record-v1",'
    b' "subject": {"gid": 1001, "groups": [1001], "uid": 1001},'
    b' "schema": "slaif-fixture-identity-record-v1"}'
)
_DUPLICATE_NESTED = (
    b'{"controller": {"gid": 21001, "uid": 21001, "uid": 21001},'
    b' "profile": "slaif-fixture-identity-owner-uid-v1",'
    b' "schema": "slaif-fixture-identity-record-v1",'
    b' "subject": {"gid": 1001, "groups": [1001], "uid": 1001}}'
)
_OVER_BOUND_BYTES = _ORIGINAL_BYTES + b'"' * 5000


def _dumps(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def test_original_description_exact_and_constants_cross_bound() -> None:
    d = fci.original_fixture_identity()
    assert d.profile == fci.PROFILE_ORIGINAL
    assert (d.controller_uid, d.controller_gid) == (21001, 21001)
    assert (d.subject_uid, d.subject_gid) == (21002, 21002)
    assert d.subject_groups == (21002,)
    assert isinstance(d.subject_groups, tuple)
    # Cross-bound to the unchanged production constants.
    assert model.CONTROLLER_UID == fci.CONTROLLER_UID == 21001
    assert model.SUBJECT_UID == fci.ORIGINAL_SUBJECT_UID == 21002
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.subject_uid = 0
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.profile = fci.PROFILE_OWNER_UID


def test_original_record_round_trip_and_stable_fingerprint() -> None:
    d = fci.original_fixture_identity()
    b = fci.encode_description(d)
    assert isinstance(b, bytes)
    assert fci.decode_description(b) == d
    assert fci.decode_description(fci.encode_description(d)) == d
    assert fci.decode_description(bytearray(b)) == d
    fp = fci.fingerprint_description(d)
    assert fci.fingerprint_description(d) == fp
    assert len(fp) == 64 and int(fp, 16) >= 0
    # Independent canonical recomputation in the test.
    canonical = json.dumps(
        {
            "controller_gid": 21001,
            "controller_uid": 21001,
            "profile": fci.PROFILE_ORIGINAL,
            "subject_gid": 21002,
            "subject_groups": [21002],
            "subject_uid": 21002,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == fp


def _valid_old_exec_record() -> dict[str, object]:
    budgets = model.FixtureBudgets()
    return {
        "record": model.SCHEMA_EXEC_MEASUREMENT,
        "uid": model.SUBJECT_UID,
        "gid": model.SUBJECT_UID,
        "groups": [model.SUBJECT_UID],
        "capabilities": {name: 0 for name in model.CAPABILITY_SETS},
        "no_new_privs": True,
        "seccomp_filter_mode": 2,
        "namespaces": {name: True for name in model.NAMESPACE_FACTS},
        "loopback_only": True,
        "keyring_errno": {name: model.KEYRING_ERRNO for name in model.KEYRING_PROBES},
        "memory_limit_bytes": budgets.memory_limit_bytes,
        "swap_limit_bytes": 0,
        "swap_source": "v2-swap-max",
        "cpu_limit": budgets.cpu_limit,
        "pids_limit": budgets.pids_limit,
        "writable_mounts": [
            {
                "root": "/run/slaif-ctl",
                "size_bytes": 64 * 1024 * 1024,
                "uid": 21001,
                "gid": 21001,
                "mode": 0o700,
            },
            {
                "root": "/run/slaif-subj",
                "size_bytes": 64 * 1024 * 1024,
                "uid": 21002,
                "gid": 21002,
                "mode": 0o700,
            },
            {
                "root": "/tmp",
                "size_bytes": 64 * 1024 * 1024,
                "uid": 21002,
                "gid": 21002,
                "mode": 0o700,
            },
            {
                "root": "/dev/shm",
                "size_bytes": 64 * 1024 * 1024,
                "uid": 0,
                "gid": 0,
                "mode": 0o1777,
            },
        ],
        "rootfs_readonly": True,
        "controller_pid1_uid": 21001,
        "private_pid1_exempt": True,
        "denied": {
            target: {"present_21001": True, "subject": "eacces"} for target in model.DENIED_TARGETS
        },
        "host_isolation": {name: False for name in model.HOST_ISOLATION_FACTS},
        "mounts_scanned": 6,
        "masked_null_aliases": 2,
    }


def test_old_record_semantics_unchanged() -> None:
    record = _valid_old_exec_record()
    budgets = model.FixtureBudgets()
    # The old 21002 record law still accepts exactly what it accepted.
    model.validate_exec_measurement(record, budgets)
    model.validate_exec_measurement(dict(record, groups=[]), budgets)
    with pytest.raises(model.FixtureError):
        model.validate_exec_measurement(dict(record, groups=[21002, 10]), budgets)
    with pytest.raises(model.FixtureError):
        model.validate_exec_measurement(dict(record, uid=21001, gid=21001, groups=[]), budgets)


def test_owner_uid_derivation_from_faithful_observation() -> None:
    d = fci.derive_owner_uid_identity(_obs(1001, 1001))
    assert d.profile == fci.PROFILE_OWNER_UID
    assert (d.controller_uid, d.controller_gid) == (21001, 21001)
    assert (d.subject_uid, d.subject_gid) == (1001, 1001)
    assert d.subject_groups == (1001,)
    d2 = fci.derive_owner_uid_identity(_obs(21099, 10101))
    assert (d2.subject_uid, d2.subject_gid, d2.subject_groups) == (
        21099,
        10101,
        (10101,),
    )


def test_actual_host_uid_read_os_data_only() -> None:
    # One ACTUAL safe current-host read: OS-data-only evidence, never
    # containment or executable capability.
    outcome = fci.collect_host_owner_ids()
    assert outcome.ok is True
    assert outcome.reason is None
    ids = outcome.ids
    assert ids is not None
    values = (
        ids.real_uid,
        ids.effective_uid,
        ids.saved_uid,
        ids.real_gid,
        ids.effective_gid,
        ids.saved_gid,
    )
    assert all(isinstance(v, int) and not isinstance(v, bool) for v in values)
    assert (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) == (
        ids.real_uid,
        ids.effective_uid,
        ids.real_gid,
        ids.effective_gid,
    )
    # Derivation either succeeds with the observed values or is a
    # closed refusal — never an exception, never authority.
    try:
        d = fci.derive_owner_uid_identity(ids)
    except fci.FixtureIdentityError as exc:
        assert exc.reason in CLOSED_REASONS
    else:
        assert d.subject_uid == ids.real_uid
        assert d.subject_gid == ids.real_gid
        assert d.subject_groups == (ids.real_gid,)


def test_derivation_rejects_mismatched_set_ids() -> None:
    mismatch_uid = fci.HostOwnerIds(1001, 1002, 1001, 1001, 1001, 1001)
    assert _refuse(fci.derive_owner_uid_identity, mismatch_uid) == "uid-triple-mismatch"
    mismatch_gid = fci.HostOwnerIds(1001, 1001, 1001, 1001, 1003, 1001)
    assert _refuse(fci.derive_owner_uid_identity, mismatch_gid) == "gid-triple-mismatch"


def test_derivation_rejects_root_collision_range_and_types() -> None:
    derive = fci.derive_owner_uid_identity
    HostOwnerIds = fci.HostOwnerIds
    assert _refuse(derive, HostOwnerIds(0, 0, 0, 1001, 1001, 1001)) == "root-id"
    assert _refuse(derive, HostOwnerIds(1001, 1001, 1001, 0, 0, 0)) == "root-id"
    assert (
        _refuse(derive, HostOwnerIds(21001, 21001, 21001, 1001, 1001, 1001))
        == "controller-id-collision"
    )
    assert (
        _refuse(derive, HostOwnerIds(1001, 1001, 1001, 21001, 21001, 21001))
        == "controller-id-collision"
    )
    assert _refuse(derive, HostOwnerIds(-1, -1, -1, 1001, 1001, 1001)) == ("invalid-id-range")
    assert (
        _refuse(derive, HostOwnerIds(4294967295, 4294967295, 4294967295, 1001, 1001, 1001))
        == "invalid-id-range"
    )
    assert _refuse(derive, HostOwnerIds(True, True, True, 1001, 1001, 1001)) == ("invalid-id-type")


def test_collector_fake_seam_outcomes() -> None:
    calls = 0

    def reader() -> tuple[int, int, int, int, int, int]:
        nonlocal calls
        calls += 1
        return (1001, 1001, 1001, 1001, 1001, 1001)

    outcome = fci.collect_host_owner_ids(reader)
    assert outcome.ok is True
    assert outcome.reason is None
    assert outcome.ids == fci.HostOwnerIds(1001, 1001, 1001, 1001, 1001, 1001)
    fci.collect_host_owner_ids(reader)
    assert calls == 2  # exactly one raw read per collection

    def failing() -> tuple[int, int, int, int, int, int]:
        raise OSError("boom")

    bad = fci.collect_host_owner_ids(failing)
    assert (bad.ok, bad.reason, bad.ids) == (False, "id-getter-failure", None)

    def unsupported() -> tuple[int, int, int, int, int, int]:
        raise AttributeError("no res getters")

    unsup = fci.collect_host_owner_ids(unsupported)
    assert (unsup.ok, unsup.reason, unsup.ids) == (False, "unsupported-platform", None)

    rooty = fci.collect_host_owner_ids(lambda: (0, 0, 0, 1001, 1001, 1001))
    assert (rooty.ok, rooty.reason, rooty.ids) == (False, "root-id", None)

    def str_reader() -> tuple[int, int, int, int, int, int]:
        return (1001, 1001, 1001, 1001, 1001, "1001")  # type: ignore[return-value]

    stry = fci.collect_host_owner_ids(str_reader)
    assert (stry.ok, stry.reason, stry.ids) == (False, "invalid-id-type", None)


def test_decode_valid_positives() -> None:
    owner = fci.decode_description(_dumps(_payload(profile=fci.PROFILE_OWNER_UID)))
    assert owner == fci.derive_owner_uid_identity(_obs(1001, 1001))
    original = fci.decode_description(
        _dumps(
            _payload(
                profile=fci.PROFILE_ORIGINAL,
                subject={"uid": 21002, "gid": 21002, "groups": [21002]},
            )
        )
    )
    assert original == fci.original_fixture_identity()
    # Decoding caller-authored valid data is a pure data transformation.
    assert isinstance(owner, fci.FixtureIdentityDescription)
    assert owner.profile == fci.PROFILE_OWNER_UID


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"not json", "malformed-record"),
        (b"\xff\xfe\xfd", "malformed-record"),
        (b"[1, 2, 3]", "malformed-record"),
        (b'"str"', "malformed-record"),
        (_dumps(_payload(bogus=1)), "unknown-field"),
        (
            _dumps(
                {
                    "schema": "slaif-fixture-identity-record-v1",
                    "profile": fci.PROFILE_OWNER_UID,
                    "controller": {"uid": 21001, "gid": 21001},
                }
            ),
            "missing-field",
        ),
        (_dumps(_payload(schema="slaif-fixture-identity-record-v2")), "unknown-schema"),
        (_dumps(_payload(profile="slaif-fixture-identity-original-v2")), "invalid-profile"),
        (_dumps(_payload(profile="other")), "invalid-profile"),
        (_dumps(_payload(controller={"uid": True, "gid": 21001})), "invalid-id-type"),
        (
            _dumps(_payload(subject={"uid": "1001", "gid": 1001, "groups": [1001]})),
            "invalid-id-type",
        ),
        (
            _dumps(_payload(subject={"uid": 1001.0, "gid": 1001, "groups": [1001]})),
            "invalid-id-type",
        ),
        (
            _dumps(_payload(subject={"uid": -1, "gid": 1001, "groups": [1001]})),
            "invalid-id-range",
        ),
        (
            _dumps(_payload(subject={"uid": 4294967295, "gid": 1001, "groups": [1001]})),
            "invalid-id-range",
        ),
        (
            _dumps(_payload(subject={"uid": 0, "gid": 1001, "groups": [1001]})),
            "root-id",
        ),
        (_dumps(_payload(controller={"uid": 21001, "gid": 0})), "root-id"),
        (
            _dumps(
                _payload(
                    profile=fci.PROFILE_ORIGINAL,
                    subject={"uid": 21003, "gid": 21003, "groups": [21003]},
                )
            ),
            "invalid-subject-for-profile",
        ),
        (
            _dumps(_payload(subject={"uid": 21001, "gid": 1001, "groups": [1001]})),
            "controller-id-collision",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 21001, "groups": [21001]})),
            "controller-id-collision",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": []})),
            "invalid-group-vector",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": [1002]})),
            "invalid-group-vector",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": [1001, 10]})),
            "invalid-group-vector",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": "1001"})),
            "invalid-group-vector",
        ),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": [True]})),
            "invalid-id-type",
        ),
        (_dumps(_payload(controller={"uid": 21001})), "missing-field"),
        (
            _dumps(_payload(subject={"uid": 1001, "gid": 1001, "groups": [1001], "x": 1})),
            "unknown-field",
        ),
        (_dumps(_payload(controller={"uid": 21001, "gid": 21001, "x": 1})), "unknown-field"),
        (_DUPLICATE_TOP, "duplicate-key"),
        (_DUPLICATE_NESTED, "duplicate-key"),
        (_OVER_BOUND_BYTES, "over-bound"),
    ],
)
def test_decode_closed_negatives(data: bytes, expected: str) -> None:
    assert _refuse(fci.decode_description, data) == expected


def test_construction_enforces_complete_field_laws() -> None:
    C = fci.FixtureIdentityDescription
    assert _refuse(C, "bogus", 21001, 21001, 21002, 21002, (21002,)) == "invalid-profile"
    assert (
        _refuse(C, fci.PROFILE_ORIGINAL, 21002, 21001, 21002, 21002, (21002,))
        == "controller-mismatch"
    )
    assert _refuse(C, fci.PROFILE_ORIGINAL, 21001, 21001, 0, 21002, (21002,)) == "root-id"
    assert (
        _refuse(C, fci.PROFILE_ORIGINAL, 21001, 21001, 21003, 21003, (21003,))
        == "invalid-subject-for-profile"
    )
    assert (
        _refuse(C, fci.PROFILE_OWNER_UID, 21001, 21001, 21001, 1001, (1001,))
        == "controller-id-collision"
    )
    assert (
        _refuse(C, fci.PROFILE_OWNER_UID, 21001, 21001, 1001, 21001, (21001,))
        == "controller-id-collision"
    )
    assert (
        _refuse(C, fci.PROFILE_OWNER_UID, 21001, 21001, 1001, 1001, (1002,))
        == "invalid-group-vector"
    )
    assert (
        _refuse(C, fci.PROFILE_OWNER_UID, 21001, 21001, "1001", 1001, (1001,)) == "invalid-id-type"
    )
    ok = C(fci.PROFILE_OWNER_UID, 21001, 21001, 1001, 1001, (1001,))
    assert fci.validate_description(ok) is ok


def test_constructor_closed_group_vector_law() -> None:
    C = fci.FixtureIdentityDescription
    profile = fci.PROFILE_ORIGINAL
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, []) == "invalid-group-vector"
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, [21002, 10]) == "invalid-group-vector"
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, "21002") == "invalid-group-vector"
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, 21002) == "invalid-group-vector"
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, [True]) == "invalid-id-type"
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, [["21002"]]) == "invalid-id-type"
    # An arbitrarily large caller vector is refused without being copied.
    huge = list(range(100000))
    assert _refuse(C, profile, 21001, 21001, 21002, 21002, huge) == "invalid-group-vector"


def test_caller_cannot_alter_description_or_alias_groups() -> None:
    d = fci.original_fixture_identity()
    alias = [21002]
    built = fci.FixtureIdentityDescription(fci.PROFILE_ORIGINAL, 21001, 21001, 21002, 21002, alias)
    assert built == d
    built_groups: Any = built.subject_groups
    assert isinstance(built_groups, tuple)
    assert built_groups is not alias
    alias.append(10)
    assert built_groups == (21002,)
    src = (21002,)
    built2 = fci.FixtureIdentityDescription(fci.PROFILE_ORIGINAL, 21001, 21001, 21002, 21002, src)
    built2_groups: Any = built2.subject_groups
    assert built2_groups is not src
    assert fci.encode_description(built) == fci.encode_description(d)
    assert fci.fingerprint_description(built) == fci.fingerprint_description(d)


def test_over_bound_bytearray_refused_before_copy() -> None:
    big = bytearray(_OVER_BOUND_BYTES)
    assert len(big) > fci.MAX_RECORD_BYTES
    assert _refuse(fci.decode_description, big) == "over-bound"


def test_profile_isolation_equal_numeric_tuples() -> None:
    original = fci.original_fixture_identity()
    owner_like = fci.derive_owner_uid_identity(_obs(21002, 21002))
    assert (original.subject_uid, original.subject_gid) == (21002, 21002)
    assert (owner_like.subject_uid, owner_like.subject_gid) == (21002, 21002)
    assert original.profile != owner_like.profile
    assert fci.fingerprint_description(original) != fci.fingerprint_description(owner_like)
    assert fci.encode_description(original) != fci.encode_description(owner_like)
    assert fci.validate_description(owner_like) is owner_like


def test_fingerprint_distinguishes_meaningful_changes() -> None:
    base = fci.derive_owner_uid_identity(_obs(1001, 1001))
    fp_base = fci.fingerprint_description(base)
    assert fci.fingerprint_description(fci.derive_owner_uid_identity(_obs(1001, 1001))) == fp_base
    assert fci.fingerprint_description(fci.derive_owner_uid_identity(_obs(1002, 1001))) != fp_base
    assert fci.fingerprint_description(fci.derive_owner_uid_identity(_obs(1001, 1003))) != fp_base
    assert fci.fingerprint_description(fci.original_fixture_identity()) != fp_base


def test_supplementary_groups_never_inherited() -> None:
    d = fci.derive_owner_uid_identity(_obs(21099, 21098))
    assert d.subject_groups == (21098,)
    source = IDENTITY_SCRIPT.read_text()
    assert "getgroups" not in source
    assert "getgrouplist" not in source


def test_pure_data_yields_no_authority() -> None:
    public = {name for name in dir(fci) if not name.startswith("_")}
    assert CONTRACT_NAMES.issubset(public)
    lowered = {name.lower() for name in public}
    forbidden = ("ready", "admit", "admission", "native", "auth", "token", "receipt")
    assert not any(token in name for name in lowered for token in forbidden)
    # Decoded data is an ordinary immutable description — nothing else.
    d = fci.decode_description(fci.encode_description(fci.original_fixture_identity()))
    assert isinstance(d, fci.FixtureIdentityDescription)
    assert isinstance(fci.fingerprint_description(d), str)
    assert isinstance(fci.encode_description(d), bytes)


def test_import_and_use_perform_no_external_operation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = IDENTITY_SCRIPT.read_bytes()
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "collections", "dataclasses", "hashlib", "json", "os"}

    monkeypatch.chdir(tmp_path)
    fresh = _load("cache_native_fixture_identity_fresh", IDENTITY_SCRIPT)
    model_before = MODEL_SCRIPT.read_bytes()
    description = fresh.original_fixture_identity()
    derived = fresh.derive_owner_uid_identity(
        fresh.HostOwnerIds(1001, 1001, 1001, 1001, 1001, 1001)
    )
    record = fresh.encode_description(description)
    assert fresh.decode_description(record) == description
    assert len(fresh.fingerprint_description(derived)) == 64
    outcome = fresh.collect_host_owner_ids(lambda: (1001, 1001, 1001, 1001, 1001, 1001))
    assert outcome.ok is True
    # No file or directory created in the working directory.
    assert sorted(p.name for p in tmp_path.iterdir()) == []
    # Existing fixture state untouched; no 017-z root exists.
    assert MODEL_SCRIPT.read_bytes() == model_before
    assert not (REPO_ROOT / ".oap-local" / "017-z").exists()
