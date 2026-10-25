"""Pure model tests for the serial right-pane native fixture (017-r).

These tests exercise ONLY the repo-owned typed stdlib model
(scripts/cache_native_fixture_model.py): finite budgets including the
required zero-swap default, the ordered evidence-gated phase machine
(dispatch to exact semantic validators, no tag-only advance), the
set-once monotonic lifetime deadline, the non-resettable ledger, the
exact closed record schemas (field sets, enums, digests, fixed
non-echoing errors), the immutable exact-issued call registry with
bounded opaque IDs, and the bounded tools-region-only metadata
diagnostic with zero raw-content reflection.  No Docker, no container,
no native binary, no network: the actual capability proof is the
remote ``cache-native-fixture`` CI job, and a green test here proves
the model, never the boundary.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import inspect
import json
import struct
import sys
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_model.py"

spec = importlib.util.spec_from_file_location("cache_native_fixture_model", MODEL_PATH)
assert spec is not None and spec.loader is not None
model = importlib.util.module_from_spec(spec)
sys.modules["cache_native_fixture_model"] = model
spec.loader.exec_module(model)

# The 21001 export client reuses the SAME already-executed model
# module via the sys.modules name; loading it performs no IO.
CLIENT_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_export_client.py"
client_spec = importlib.util.spec_from_file_location(
    "cache_native_fixture_export_client", CLIENT_PATH
)
assert client_spec is not None and client_spec.loader is not None
client = importlib.util.module_from_spec(client_spec)
client_spec.loader.exec_module(client)

FixtureError = model.FixtureError
BudgetExceeded = model.BudgetExceeded


# -- valid record factories (complete actual-shaped facts) ------------------
def artifact_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_ARTIFACT,
        "tag": model.ARTIFACT_TAG,
        "commit": model.ARTIFACT_COMMIT,
        "archive_sha256": model.ARTIFACT_ARCHIVE_SHA256,
        "archive_size": model.ARTIFACT_ARCHIVE_SIZE,
        "binary_name": model.ARTIFACT_BINARY_NAME,
        "binary_sha256": "ab" * 32,
        "binary_size": 60_000_000,
        "license": "Apache-2.0",
        "license_sha256": model.ARTIFACT_LICENSE_SHA256,
        "notice": model.ARTIFACT_NOTICE,
        "notice_sha256": model.ARTIFACT_NOTICE_SHA256,
        "signature_verification": "not-run",
    }


def exec_measurement(budgets: Any = None) -> dict[str, Any]:
    budgets = budgets or model.FixtureBudgets()
    mounts = [
        {
            "root": mount,
            "size_bytes": size,
            "uid": uid,
            "gid": gid,
            "mode": 0o700 if uid == model.CONTROLLER_UID else 0o1777,
        }
        for mount, size, uid, gid in budgets.tmpfs_budgets
    ]
    # The daemon's explicitly bounded /dev/shm is part of the
    # reconciled writable-data surface (daemon-owned 0:0, mode 1777).
    mounts.append(
        {
            "root": model.SHM_MOUNT,
            "size_bytes": model.SHM_SIZE_BYTES,
            "uid": model.SHM_OWNER[0],
            "gid": model.SHM_OWNER[1],
            "mode": model.SHM_MODE,
        }
    )
    denied = {
        target: {"present_21001": True, "subject": "eacces"} for target in model.DENIED_TARGETS
    }
    return {
        "record": model.SCHEMA_EXEC_MEASUREMENT,
        "uid": 21002,
        "gid": 21002,
        "groups": [],
        "capabilities": {name: 0 for name in model.CAPABILITY_SETS},
        "no_new_privs": True,
        "seccomp_filter_mode": 2,
        "namespaces": {name: True for name in model.NAMESPACE_FACTS},
        "loopback_only": True,
        "keyring_errno": {name: 1 for name in model.KEYRING_PROBES},
        "memory_limit_bytes": budgets.memory_limit_bytes,
        "swap_limit_bytes": 0,
        "swap_source": "v2-swap-max",
        "cpu_limit": budgets.cpu_limit,
        "pids_limit": budgets.pids_limit,
        "writable_mounts": mounts,
        "mounts_scanned": 13,
        "masked_null_aliases": 2,
        "rootfs_readonly": True,
        "controller_pid1_uid": 21001,
        "private_pid1_exempt": True,
        "denied": denied,
        "host_isolation": {name: False for name in model.HOST_ISOLATION_FACTS},
    }


def diagnostic_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_METADATA_DIAGNOSTIC,
        "endpoint": "responses",
        "tool_families": ["function"],
        "function_name_count": 1,
        "known_names": ["exec_command"],
        "unknown_name_count": 0,
        "argument_field_presence": {"exec_command": {"cmd": "absent"}},
        "traversal_depth": 2,
        "required_fields": {"input": True, "tools": True},
        "unknown_modes": [],
        "response_kind": "fixed-final-text-no-tools",
        "raw_content_retained": False,
    }


def quiesce_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_QUIESCE,
        "provider_sockets_closed": True,
        "handlers_stopped": True,
        "owned_subject_stopped": True,
        "owned_tools_stopped": True,
        "active_connections": 0,
        "residual_writers": 0,
    }


def snapshot_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_SNAPSHOT,
        "synthetic": True,
        "issued_calls": [
            {
                "family": "function",
                "name": "exec_command",
                "call_id": "call_1",
                "position": 1,
                "arguments_sha256": "cd" * 32,
            }
        ],
        "originals_bytes": 128,
        "originals_sha256": "ef" * 32,
        "exporter_uid": 21001,
        "exported_before_teardown": True,
        "controller_ledger": {"requests": 2, "output_bytes": 512},
    }


def teardown_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_TEARDOWN,
        "cid": "11" * 32,
        "container_present_before": True,
        "container_inspect_after": "absent-verified",
        "image_present_before": True,
        "image_inspect_after": "absent-verified",
        "descendants_before": 2,
        "descendants_after": 0,
        "sentinel_survived": True,
        "export_completed_before_teardown": True,
    }


def publish_record() -> dict[str, Any]:
    return {
        "record": model.SCHEMA_PUBLISH,
        "publish_dir_mode": 0o700,
        "artifact_file_mode": 0o600,
        "artifact_sha256": "22" * 32,
        "snapshot_digest_match": True,
        "api_requests": 10,
        "api_attempts": 12,
        "requests_admitted": 8,
        "requests_refused": 2,
        "healthz_attempts": 3,
        "docker_admissions": 40,
        "docker_refusals": 1,
        "bytes_drained": 4096,
        "bytes_retained": 1024,
        "deadline_expired": False,
    }


def ci_summary_record() -> dict[str, Any]:
    mounts = [
        {
            "root": mount,
            "size_bytes": size,
            "uid": uid,
            "gid": gid,
            "mode": 0o700 if uid == model.CONTROLLER_UID else 0o1777,
        }
        for mount, size, uid, gid in model.DEFAULT_TMPFS_BUDGETS
    ]
    mounts.append(
        {
            "root": model.SHM_MOUNT,
            "size_bytes": model.SHM_SIZE_BYTES,
            "uid": model.SHM_OWNER[0],
            "gid": model.SHM_OWNER[1],
            "mode": model.SHM_MODE,
        }
    )
    return {
        "record": model.SCHEMA_CI_SUMMARY,
        "scenarios": [{"name": name, "state": state} for name, state in model.REQUIRED_SCENARIOS],
        "container_removal": "absent-verified",
        "image_removal": "absent-verified",
        "export_sha256": "33" * 32,
        "codex_invoked": False,
        "api_requests": 10,
        "api_attempts": 12,
        "requests_admitted": 8,
        "requests_refused": 2,
        "healthz_attempts": 3,
        "docker_admissions": 40,
        "docker_refusals": 1,
        "bytes_drained": 4096,
        "bytes_retained": 1024,
        "writable_mounts": mounts,
        "writable_data_total_bytes": sum(m["size_bytes"] for m in mounts),
        "deadline_expired": False,
    }


def full_path_records() -> list[dict[str, Any]]:
    return [
        artifact_record(),
        exec_measurement(),
        diagnostic_record(),
        quiesce_record(),
        snapshot_record(),
        teardown_record(),
        publish_record(),
    ]


# -- budgets -----------------------------------------------------------------
class TestBudgets:
    def test_default_constructs_with_zero_swap(self) -> None:
        ledger = model.FixtureLedger()
        assert ledger.budgets.swap_limit_bytes == 0

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda b: model.FixtureBudgets(swap_limit_bytes=-1),
            lambda b: model.FixtureBudgets(swap_limit_bytes=True),
            lambda b: model.FixtureBudgets(memory_limit_bytes=0),
            lambda b: model.FixtureBudgets(memory_limit_bytes=False),
            lambda b: model.FixtureBudgets(cpu_limit=0),
            lambda b: model.FixtureBudgets(pids_limit=-2),
            lambda b: model.FixtureBudgets(output_cap_bytes=0),
            lambda b: model.FixtureBudgets(max_requests=0),
            lambda b: model.FixtureBudgets(max_attempts=-1),
            lambda b: model.FixtureBudgets(max_connections=0),
            lambda b: model.FixtureBudgets(max_threads=0),
            lambda b: model.FixtureBudgets(lifetime_seconds=0),
            lambda b: model.FixtureBudgets(max_export_bytes=0),
            lambda b: model.FixtureBudgets(swap_limit_bytes=model.MEMORY_LIMIT_BYTES + 1),
            lambda b: model.FixtureBudgets(tmpfs_budgets=()),
            lambda b: model.FixtureBudgets(
                tmpfs_budgets=(
                    ("/run/slaif-ctl", 64 * 1024 * 1024, 21001, 21001),
                    ("/run/slaif-ctl", 16 * 1024 * 1024, 21001, 21001),
                )
            ),
            lambda b: model.FixtureBudgets(
                tmpfs_budgets=(("/run/slaif-ctl", 200 * 1024 * 1024, 21001, 21001),)
            ),
            lambda b: model.FixtureBudgets(
                tmpfs_budgets=(("run/slaif-ctl", 64 * 1024 * 1024, 21001, 21001),)
            ),
            lambda b: model.FixtureBudgets(tmpfs_budgets=(("/run/slaif-ctl", 0, 21001, 21001),)),
        ],
    )
    def test_invalid_budget_fails_closed(self, mutate: Any) -> None:
        with pytest.raises(FixtureError):
            model.FixtureLedger(mutate(None))

    def test_zero_swap_budget_is_the_supported_default(self) -> None:
        budgets = model.FixtureBudgets(swap_limit_bytes=0)
        budgets.validate()
        assert budgets.swap_limit_bytes == 0


# -- phase machine ------------------------------------------------------------
class TestPhaseMachine:
    def test_fresh_ledger_has_no_phase_and_requires_evidence(self) -> None:
        ledger = model.FixtureLedger()
        assert ledger.phase is None
        with pytest.raises(FixtureError):
            ledger.require_phase(model.FixturePhase.PREPARED)

    def test_full_happy_path_derives_readiness_from_evidence(self) -> None:
        ledger = model.FixtureLedger()
        targets = [phase for phase in model.FixturePhase]
        for target, record in zip(targets, full_path_records(), strict=True):
            phase = ledger.transition(target, record)
            assert phase is target
        assert ledger.phase is model.FixturePhase.PUBLISHED
        assert ledger.history == [t.value for t in targets]

    @pytest.mark.parametrize(
        "target",
        [
            model.FixturePhase.SYNTHETIC_SCENARIO,  # skip MEASURED
            model.FixturePhase.PUBLISHED,  # skip everything
        ],
    )
    def test_skip_rejected(self, target: Any) -> None:
        ledger = model.FixtureLedger()
        with pytest.raises(FixtureError):
            ledger.transition(target, artifact_record())

    def test_backward_rejected(self) -> None:
        ledger = model.FixtureLedger()
        ledger.transition(model.FixturePhase.PREPARED, artifact_record())
        with pytest.raises(FixtureError):
            ledger.transition(model.FixturePhase.PREPARED, artifact_record())

    def test_unknown_phase_rejected(self) -> None:
        ledger = model.FixtureLedger()
        with pytest.raises(FixtureError):
            ledger.transition("sideways", artifact_record())

    def test_tag_only_record_never_advances(self) -> None:
        # Every phase's bare schema tag with zero facts must fail.
        ledger = model.FixtureLedger()
        with pytest.raises(FixtureError):
            ledger.transition(model.FixturePhase.PREPARED, {"record": model.SCHEMA_ARTIFACT})
        records = full_path_records()
        ledger.transition(model.FixturePhase.PREPARED, records[0])
        ledger.transition(model.FixturePhase.MEASURED, records[1])
        for phase in list(model.FixturePhase)[2:]:
            required = model.PHASE_REQUIRED_RECORD[phase]
            with pytest.raises(FixtureError):
                ledger.transition(phase, {"record": required})
            # restore a valid state so the next phase can be probed
            ledger.transition(phase, records[model.PHASE_ORDER.index(phase)])

    def test_wrong_schema_tag_rejected(self) -> None:
        ledger = model.FixtureLedger()
        ledger.transition(model.FixturePhase.PREPARED, artifact_record())
        wrong = exec_measurement()
        wrong["record"] = model.SCHEMA_ARTIFACT
        with pytest.raises(FixtureError):
            ledger.transition(model.FixturePhase.MEASURED, wrong)

    def test_exec_record_with_facts_but_not_from_measured_context_rejected(self) -> None:
        ledger = model.FixtureLedger()
        ledger.transition(model.FixturePhase.PREPARED, artifact_record())
        ledger.transition(model.FixturePhase.MEASURED, exec_measurement())
        with pytest.raises(FixtureError):
            ledger.transition(model.FixturePhase.MEASURED, exec_measurement())

    def test_standalone_closed_record_dispatch_rejects_unknown_tag(self) -> None:
        with pytest.raises(FixtureError):
            model._validate_closed_record({"record": "slaif-not-a-schema-v0"})

    def test_standalone_dispatch_runs_semantic_validators(self) -> None:
        model._validate_closed_record(exec_measurement())
        with pytest.raises(FixtureError):
            model._validate_closed_record({"record": model.SCHEMA_EXEC_MEASUREMENT, "uid": 21002})


# -- lifetime deadline (real monotonic expiry, set once) ----------------------
class _Clock:
    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


class TestDeadline:
    def test_set_once_and_rejects_second_set(self) -> None:
        clock = _Clock()
        ledger = model.FixtureLedger(clock=clock)
        ledger.set_deadline(60)
        with pytest.raises(FixtureError):
            ledger.set_deadline(30)

    @pytest.mark.parametrize("seconds", [0, -5, float("inf"), float("nan"), True])
    def test_invalid_deadline_rejected(self, seconds: Any) -> None:
        ledger = model.FixtureLedger(clock=_Clock())
        with pytest.raises(FixtureError):
            ledger.set_deadline(seconds)

    def test_deadline_bounded_by_lifetime(self) -> None:
        budgets = model.FixtureBudgets(lifetime_seconds=10)
        ledger = model.FixtureLedger(budgets=budgets, clock=_Clock())
        with pytest.raises(BudgetExceeded):
            ledger.set_deadline(11)

    def test_transition_rejected_after_monotonic_expiry(self) -> None:
        clock = _Clock()
        ledger = model.FixtureLedger(clock=clock)
        ledger.set_deadline(60)
        assert ledger.deadline_expired() is False
        assert ledger.remaining_seconds() == 60
        clock.now += 61
        assert ledger.deadline_expired() is True
        assert ledger.remaining_seconds() == 0.0
        with pytest.raises(BudgetExceeded):
            ledger.transition(model.FixturePhase.PREPARED, artifact_record())

    def test_deadline_enforced_during_counter_work(self) -> None:
        clock = _Clock()
        ledger = model.FixtureLedger(clock=clock)
        ledger.set_deadline(30)
        assert ledger.record_request() == 1
        clock.now += 31
        with pytest.raises(BudgetExceeded):
            ledger.record_request()
        with pytest.raises(BudgetExceeded):
            ledger.record_output(1)

    def test_no_deadline_set_means_no_expiry(self) -> None:
        ledger = model.FixtureLedger(clock=_Clock())
        assert ledger.deadline_expired() is False
        assert ledger.remaining_seconds() is None
        ledger.transition(model.FixturePhase.PREPARED, artifact_record())


# -- non-resettable ledger accounting ------------------------------------------
class TestLedgerAccounting:
    def test_no_reset_api_exists(self) -> None:
        ledger = model.FixtureLedger()
        assert not any(name.startswith("reset") for name in dir(ledger) if not name.startswith("_"))

    def test_counters_accumulate_across_phases(self) -> None:
        ledger = model.FixtureLedger()
        ledger.record_request()
        ledger.transition(model.FixturePhase.PREPARED, artifact_record())
        assert ledger.record_request() == 2
        assert ledger.requests == 2
        ledger.record_output(10)
        ledger.transition(model.FixturePhase.MEASURED, exec_measurement())
        assert ledger.record_output(20) == 30

    def test_request_bound_fail_closed(self) -> None:
        budgets = model.FixtureBudgets(max_requests=2)
        ledger = model.FixtureLedger(budgets=budgets)
        ledger.record_request()
        ledger.record_request()
        with pytest.raises(BudgetExceeded):
            ledger.record_request()

    def test_output_cap_fail_closed(self) -> None:
        budgets = model.FixtureBudgets(output_cap_bytes=100)
        ledger = model.FixtureLedger(budgets=budgets)
        assert ledger.record_output(100) == 100
        with pytest.raises(BudgetExceeded):
            ledger.record_output(1)

    @pytest.mark.parametrize("n", [-1, True])
    def test_output_accounting_rejects_noninteger(self, n: Any) -> None:
        ledger = model.FixtureLedger()
        with pytest.raises(FixtureError):
            ledger.record_output(n)


# -- exec measurement exactness -------------------------------------------------
class TestExecMeasurement:
    def test_valid_record_accepted(self) -> None:
        model.validate_exec_measurement(exec_measurement(), model.FixtureBudgets())

    def test_missing_swap_field_fails_closed(self) -> None:
        record = exec_measurement()
        del record["swap_limit_bytes"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_nonzero_measured_swap_rejected(self) -> None:
        record = exec_measurement()
        record["swap_limit_bytes"] = 1
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_missing_cpu_fails_closed(self) -> None:
        record = exec_measurement()
        del record["cpu_limit"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_bounding_capability_set_required(self) -> None:
        record = exec_measurement()
        del record["capabilities"]["bounding"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_nonzero_capability_rejected(self) -> None:
        for name in model.CAPABILITY_SETS:
            record = exec_measurement()
            record["capabilities"][name] = 1
            with pytest.raises(FixtureError):
                model.validate_exec_measurement(record, model.FixtureBudgets())

    @pytest.mark.parametrize("uid", [21001, 0, 21003])
    def test_wrong_subject_identity_rejected(self, uid: Any) -> None:
        record = exec_measurement()
        record["uid"] = uid
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_supplementary_groups_rejected(self) -> None:
        record = exec_measurement()
        record["groups"] = [21002]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_unfiltered_seccomp_rejected(self) -> None:
        record = exec_measurement()
        record["seccomp_filter_mode"] = 0
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_shared_network_namespace_rejected(self) -> None:
        record = exec_measurement()
        record["namespaces"]["net_private"] = False
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_keyring_errno_zero_not_eperm_rejected(self) -> None:
        record = exec_measurement()
        record["keyring_errno"]["add_key"] = 0
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_mount_size_mismatch_rejected(self) -> None:
        record = exec_measurement()
        record["writable_mounts"][0]["size_bytes"] += 1
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_mount_root_omitted_rejected(self) -> None:
        record = exec_measurement()
        record["writable_mounts"] = record["writable_mounts"][:-1]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_unconfigured_mount_root_rejected(self) -> None:
        record = exec_measurement()
        record["writable_mounts"].append(
            {
                "root": "/run/extra",
                "size_bytes": 1024,
                "uid": 21002,
                "gid": 21002,
                "mode": 0o700,
            }
        )
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_shm_mount_omitted_rejected(self) -> None:
        # The reconciled surface is CLOSED: the explicitly bounded
        # /dev/shm must be measured, a three-root record is not it.
        record = exec_measurement()
        record["writable_mounts"] = [
            m for m in record["writable_mounts"] if m["root"] != model.SHM_MOUNT
        ]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_shm_oversize_rejected(self) -> None:
        record = exec_measurement()
        shm = next(m for m in record["writable_mounts"] if m["root"] == model.SHM_MOUNT)
        shm["size_bytes"] = model.SHM_SIZE_BYTES + 1
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_shm_owner_or_mode_rejected(self) -> None:
        mutators: tuple[Any, ...] = (
            lambda m: m.update(uid=21002),
            lambda m: m.update(gid=21002),
            lambda m: m.update(mode=0o700),
        )
        for mutate in mutators:
            record = exec_measurement()
            shm = next(m for m in record["writable_mounts"] if m["root"] == model.SHM_MOUNT)
            mutate(shm)
            with pytest.raises(FixtureError):
                model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_mounts_scanned_missing_or_zero_rejected(self) -> None:
        record = exec_measurement()
        del record["mounts_scanned"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())
        record = exec_measurement()
        record["mounts_scanned"] = 0
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_masked_null_aliases_missing_or_negative_rejected(self) -> None:
        record = exec_measurement()
        del record["masked_null_aliases"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())
        record = exec_measurement()
        record["masked_null_aliases"] = -1
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    @pytest.mark.parametrize(
        ("mounts_scanned", "masked_null_aliases", "why"),
        [
            (1, 0, "scanned below the data-mount count"),
            (4, 1, "data mounts plus aliases exceed scanned"),
            (513, 0, "scanned above the closed scanner record cap"),
        ],
        ids=["below-data-count", "aliases-over-scanned", "over-scanner-cap"],
    )
    def test_mounts_scanned_incoherent_relation_rejected(
        self, mounts_scanned: int, masked_null_aliases: int, why: str
    ) -> None:
        record = exec_measurement()
        record["mounts_scanned"] = mounts_scanned
        record["masked_null_aliases"] = masked_null_aliases
        with pytest.raises(FixtureError, match="mounts_scanned"):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_mounts_scanned_and_aliases_bool_rejected(self) -> None:
        for key in ("mounts_scanned", "masked_null_aliases"):
            record = exec_measurement()
            record[key] = True
            with pytest.raises(FixtureError):
                model.validate_exec_measurement(record, model.FixtureBudgets())

    @pytest.mark.parametrize("mode", [0o755, 0o777, 0o1777, 0])
    def test_controller_mount_mode_strict(self, mode: Any) -> None:
        record = exec_measurement()
        record["writable_mounts"][0]["mode"] = mode
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    @pytest.mark.parametrize("mode", [0o755, 0o777])
    def test_subject_mount_mode_rejects_world_writable_and_read(self, mode: Any) -> None:
        record = exec_measurement()
        record["writable_mounts"][1]["mode"] = mode
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_denied_target_without_proven_existence_rejected(self) -> None:
        record = exec_measurement()
        record["denied"]["issued_registry"]["present_21001"] = False
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_denied_target_open_state_rejected(self) -> None:
        record = exec_measurement()
        record["denied"]["exporter_socket"]["subject"] = "ok"
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_extra_denied_target_rejected(self) -> None:
        record = exec_measurement()
        record["denied"]["other_private"] = {"present_21001": True, "subject": "eacces"}
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_unknown_field_rejected_without_echo(self) -> None:
        record = exec_measurement()
        record["arbitrary_private_field"] = "synthetic_private_payload"
        with pytest.raises(FixtureError) as excinfo:
            model.validate_exec_measurement(record, model.FixtureBudgets())
        assert "synthetic_private_payload" not in str(excinfo.value)
        assert "arbitrary_private_field" not in str(excinfo.value)


# -- artifact record --------------------------------------------------------------
class TestArtifactRecord:
    def test_valid_public_record_accepted(self) -> None:
        model.validate_artifact_record(artifact_record())

    def test_missing_extracted_binary_digest_rejected(self) -> None:
        record = artifact_record()
        del record["binary_sha256"]
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_nonhex_binary_digest_rejected(self) -> None:
        record = artifact_record()
        record["binary_sha256"] = "z" * 64
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_binary_size_over_extracted_bound_rejected(self) -> None:
        record = artifact_record()
        record["binary_size"] = model.ARTIFACT_BINARY_MAX_BYTES + 1
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_zero_binary_size_rejected(self) -> None:
        record = artifact_record()
        record["binary_size"] = 0
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_wrong_license_rejected(self) -> None:
        record = artifact_record()
        record["license"] = "MIT"
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_missing_notice_rejected(self) -> None:
        record = artifact_record()
        del record["notice"]
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_wrong_notice_rejected(self) -> None:
        record = artifact_record()
        record["notice"] = "uncredited"
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_wrong_license_digest_rejected(self) -> None:
        record = artifact_record()
        record["license_sha256"] = "0" * 64
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_wrong_notice_digest_rejected(self) -> None:
        record = artifact_record()
        record["notice_sha256"] = "1" * 64
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)

    def test_signature_verification_never_asserted(self) -> None:
        for value in ("verified", "passed", "none"):
            record = artifact_record()
            record["signature_verification"] = value
            with pytest.raises(FixtureError):
                model.validate_artifact_record(record)

    def test_wrong_commit_rejected(self) -> None:
        record = artifact_record()
        record["commit"] = "00" * 20 + "01"
        with pytest.raises(FixtureError):
            model.validate_artifact_record(record)


# -- malformed-input totality (typed rejection, never TypeError) ------------
class TestMalformedTotality:
    def test_unhashable_schema_tag_is_closed_rejection(self) -> None:
        with pytest.raises(FixtureError):
            model._validate_closed_record({"record": []})

    def test_unhashable_tag_list_rejected(self) -> None:
        with pytest.raises(FixtureError):
            model._validate_closed_record({"record": ["x"]})

    def test_unhashable_mount_root_is_closed_rejection(self) -> None:
        record = exec_measurement()
        record["writable_mounts"][0]["root"] = []
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_nonstring_capabilities_value_is_closed_rejection(self) -> None:
        record = exec_measurement()
        record["capabilities"] = []
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_nonobject_records_rejected(self) -> None:
        for bad in (None, 7, "record", ["record"]):
            with pytest.raises(FixtureError):
                model._validate_closed_record(bad)

    def test_host_isolation_fact_true_rejected(self) -> None:
        record = exec_measurement()
        record["host_isolation"]["parent_proc_visible"] = True
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())

    def test_missing_host_isolation_rejected(self) -> None:
        record = exec_measurement()
        del record["host_isolation"]
        with pytest.raises(FixtureError):
            model.validate_exec_measurement(record, model.FixtureBudgets())


# -- bounded metadata diagnostic ----------------------------------------------------
class TestMetadataDiagnostic:
    CANARY = "synthetic_private_type_canary"

    def test_function_positive_and_no_canary_reflection(self) -> None:
        payload = {
            "tools": [
                {
                    "type": "function",
                    "name": "exec_command",
                    "parameters": {"type": "object"},
                }
            ],
            "input": [{"type": self.CANARY, "text": "synthetic ordinary input"}],
        }
        record = model.bounds_diagnostic(payload)
        assert "function" in record["tool_families"]
        assert record["function_name_count"] == 1
        assert self.CANARY not in json.dumps(record)
        model.validate_metadata_diagnostic(record)

    def test_chat_shaped_function_name_counted(self) -> None:
        payload = {
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "read_file", "parameters": {}},
                }
            ],
        }
        record = model.bounds_diagnostic(payload)
        assert record["function_name_count"] == 1
        assert record["traversal_depth"] == 3

    def test_custom_family_recorded(self) -> None:
        payload = {"tools": [{"type": "custom", "name": "widget_tool"}]}
        record = model.bounds_diagnostic(payload)
        assert record["tool_families"] == ["custom"]
        assert record["function_name_count"] == 0

    def test_unknown_mode_is_fixed_state_not_copied_value(self) -> None:
        payload = {"tools": [{"type": self.CANARY, "name": "x"}]}
        record = model.bounds_diagnostic(payload)
        assert record["unknown_modes"] == [{"kind": "unknown-tool-type", "state": "unsupported"}]
        assert self.CANARY not in json.dumps(record)

    def test_unrelated_body_changes_leave_diagnostic_equal(self) -> None:
        tools = [{"type": "function", "name": "exec_command"}]
        base = model.bounds_diagnostic(
            {
                "tools": tools,
                "input": [{"type": "message", "content": "alpha"}],
                "instructions": "first",
            }
        )
        changed = model.bounds_diagnostic(
            {
                "tools": tools,
                "input": [{"type": "message", "content": "completely different bytes" * 40}],
                "instructions": "second",
            }
        )
        assert base == changed

    def test_tools_not_list_closed_state(self) -> None:
        record = model.bounds_diagnostic({"tools": {"type": "function"}})
        assert {"kind": "tools-not-list", "state": "unsupported"} in record["unknown_modes"]

    def test_tool_not_object_closed_state(self) -> None:
        record = model.bounds_diagnostic({"tools": ["function"]})
        assert {"kind": "tool-not-object", "state": "unsupported"} in record["unknown_modes"]

    def test_missing_and_unclosed_function_name_states(self) -> None:
        missing = model.bounds_diagnostic({"tools": [{"type": "function"}]})
        assert {"kind": "missing-function-name", "state": "unsupported"} in missing["unknown_modes"]
        unclosed = model.bounds_diagnostic(
            {"tools": [{"type": "function", "name": "bad name/slash"}]}
        )
        assert {"kind": "function-name-not-closed", "state": "unsupported"} in unclosed[
            "unknown_modes"
        ]

    def test_overbound_tools_list_fails_closed_not_sliced(self) -> None:
        payload = {
            "tools": [
                {"type": "function", "name": f"t{i}"}
                for i in range(model.DIAGNOSTIC_MAX_TOOL_NAMES + 1)
            ]
        }
        with pytest.raises(FixtureError):
            model.bounds_diagnostic(payload)

    def test_depth_measured_not_clipped_constant(self) -> None:
        assert model.bounds_diagnostic({})["traversal_depth"] == 0
        assert model.bounds_diagnostic({"tools": []})["traversal_depth"] == 1
        assert (
            model.bounds_diagnostic({"tools": [{"type": "function", "name": "a"}]})[
                "traversal_depth"
            ]
            == 2
        )

    def test_non_envelope_rejected(self) -> None:
        with pytest.raises(FixtureError):
            model.bounds_diagnostic(["tools"])

    def test_known_names_are_distinguishable(self) -> None:
        exec_diag = model.bounds_diagnostic(
            {"input": [], "tools": [{"type": "function", "name": "exec_command"}]}
        )
        poll_diag = model.bounds_diagnostic(
            {"input": [], "tools": [{"type": "function", "name": "write_stdin"}]}
        )
        assert exec_diag != poll_diag
        assert exec_diag["known_names"] == ["exec_command"]
        assert poll_diag["known_names"] == ["write_stdin"]
        model.validate_metadata_diagnostic(exec_diag)
        model.validate_metadata_diagnostic(poll_diag)

    def test_actual_max_depth_with_mixed_shapes(self) -> None:
        nested = model.bounds_diagnostic(
            {
                "input": [],
                "tools": [
                    {"type": "function", "function": {"name": "exec_command"}},
                    {"type": "function", "name": "write_stdin"},
                ],
            }
        )
        assert nested["traversal_depth"] == 3

    def test_unknown_only_diagnostic_is_valid_typed_metadata(self) -> None:
        unknown = model.bounds_diagnostic(
            {"input": [], "tools": [{"type": "synthetic_unknown_type"}]}
        )
        assert unknown["tool_families"] == []
        assert unknown["unknown_modes"] == [{"kind": "unknown-tool-type", "state": "unsupported"}]
        model.validate_metadata_diagnostic(unknown)

    def test_unknown_name_is_counted_not_reflected(self) -> None:
        record = model.bounds_diagnostic(
            {"input": [], "tools": [{"type": "function", "name": "read_file"}]}
        )
        assert record["known_names"] == []
        assert record["unknown_name_count"] == 1
        assert "read_file" not in json.dumps(record)
        model.validate_metadata_diagnostic(record)

    def test_field_presence_states(self) -> None:
        required = model.bounds_diagnostic(
            {
                "tools": [
                    {
                        "type": "function",
                        "name": "exec_command",
                        "parameters": {
                            "required": ["cmd"],
                            "properties": {
                                "cmd": {"type": "string"},
                                "unbounded_field": {"type": "string"},
                            },
                        },
                    }
                ]
            }
        )
        assert required["argument_field_presence"] == {"exec_command": {"cmd": "required"}}
        present = model.bounds_diagnostic(
            {
                "tools": [
                    {
                        "type": "function",
                        "name": "write_stdin",
                        "parameters": {"properties": {"chars": {"type": "string"}}},
                    }
                ]
            }
        )
        assert present["argument_field_presence"] == {
            "write_stdin": {"session_id": "absent", "chars": "present"}
        }
        assert "unbounded_field" not in json.dumps(required)
        assert present["traversal_depth"] == 3

    def test_name_count_identity_enforced(self) -> None:
        record = diagnostic_record()
        record["unknown_name_count"] = 1  # breaks count == known + unknown
        with pytest.raises(FixtureError):
            model.validate_metadata_diagnostic(record)

    def test_presence_keys_must_match_known_names(self) -> None:
        record = diagnostic_record()
        record["argument_field_presence"] = {}
        with pytest.raises(FixtureError):
            model.validate_metadata_diagnostic(record)

    def test_overbound_required_list_fails_closed(self) -> None:
        params = {
            "required": [f"other{i}" for i in range(model.DIAGNOSTIC_MAX_REQUIRED_FIELDS + 1)],
            "properties": {"cmd": {}},
        }
        with pytest.raises(FixtureError):
            model.bounds_diagnostic(
                {
                    "input": [],
                    "tools": [{"type": "function", "name": "exec_command", "parameters": params}],
                }
            )

    def test_flat_depth_three_wrapped_depth_four(self) -> None:
        flat = model.bounds_diagnostic(
            {
                "tools": [
                    {
                        "type": "function",
                        "name": "exec_command",
                        "parameters": {"properties": {"cmd": {}}},
                    }
                ]
            }
        )
        assert flat["traversal_depth"] == 3
        wrapped = model.bounds_diagnostic(
            {
                "tools": [
                    {
                        "type": "function",
                        "name": "exec_command",
                        "function": {
                            "name": "exec_command",
                            "parameters": {"properties": {"cmd": {}}},
                        },
                    }
                ]
            }
        )
        assert wrapped["traversal_depth"] == 4
        assert wrapped["argument_field_presence"]["exec_command"]["cmd"] == "present"

    def test_large_properties_do_not_copy_unrelated_keys(self) -> None:
        import tracemalloc

        properties: dict[str, Any] = {f"p{i}": None for i in range(20000)}
        properties["cmd"] = {}
        payload = {
            "input": [],
            "tools": [
                {
                    "type": "function",
                    "name": "exec_command",
                    "parameters": {"properties": properties, "required": ["cmd"]},
                }
            ],
        }
        tracemalloc.start()
        result = model.bounds_diagnostic(payload)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert result["argument_field_presence"]["exec_command"]["cmd"] == "required"
        assert "p0" not in json.dumps(result)
        # regression guard only (not a runtime setting): the diagnostic
        # must not retain the unrelated key set
        assert peak < 2 * 1024 * 1024

    def test_raw_content_retained_always_false(self) -> None:
        record = model.bounds_diagnostic({"tools": []})
        assert record["raw_content_retained"] is False
        assert record["response_kind"] == "fixed-final-text-no-tools"


# -- exact-issued registry ----------------------------------------------------------
class TestIssuedRegistry:
    def test_exact_match_positive(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "exec_command", "call_a", "a" * 64, 1)
        state, entry = registry.match("function", "exec_command", "call_a", "a" * 64, 1)
        assert state == "exact_issued"
        assert entry["request_position"] == 1

    def test_conflicting_reissue_rejected_immutable(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "exec_command", "call_a", "a" * 64, 1)
        with pytest.raises(FixtureError):
            registry.issue("function", "exec_command", "call_a", "b" * 64, 2)
        # identical reissue is also a conflict: identity is immutable
        with pytest.raises(FixtureError):
            registry.issue("function", "exec_command", "call_a", "a" * 64, 1)

    def test_nonhex_digest_rejected(self) -> None:
        registry = model.IssuedRegistry()
        with pytest.raises(FixtureError):
            registry.issue("function", "exec_command", "call_b", "z" * 64, 3)

    @pytest.mark.parametrize("position", [True, -1, 1.0, "1"])
    def test_malformed_causal_position_rejected(self, position: Any) -> None:
        registry = model.IssuedRegistry()
        with pytest.raises(FixtureError):
            registry.issue("function", "exec_command", "call_c", "c" * 64, position)

    def test_uppercase_opaque_id_allowed(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "Exec_Command", "call_ABC-123.x", None, 0)
        state, _ = registry.match("function", "Exec_Command", "call_ABC-123.x", None, 0)
        assert state == "exact_issued"

    def test_same_call_id_different_name_cannot_reissue(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "exec_command", "SameCallA", "a" * 64, 0)
        with pytest.raises(FixtureError):
            registry.issue("function", "write_stdin", "SameCallA", "b" * 64, 1)
        # and the original identity is preserved, not overwritten
        state, entry = registry.match("function", "exec_command", "SameCallA", "a" * 64, 0)
        assert state == "exact_issued"
        assert entry["name"] == "exec_command"

    def test_escaped_path_id_rejected(self) -> None:
        registry = model.IssuedRegistry()
        with pytest.raises(FixtureError):
            registry.issue("function", "exec_command", "a/b", None, 0)

    def test_unsupported_family_rejected(self) -> None:
        registry = model.IssuedRegistry()
        with pytest.raises(FixtureError):
            registry.issue("custom", "widget", "call_d", None, 0)
        state, _ = registry.match("custom", "widget", "call_d", None, 0)
        assert state == "unsupported"

    def test_issuance_bounded_by_global_budget(self) -> None:
        registry = model.IssuedRegistry(max_calls=2)
        registry.issue("function", "a", "id_a", None, 0)
        registry.issue("function", "b", "id_b", None, 1)
        with pytest.raises(BudgetExceeded):
            registry.issue("function", "c", "id_c", None, 2)

    def test_unissued_and_mismatched_states(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "exec_command", "call_a", "a" * 64, 1)
        assert registry.match("function", "other", "call_x", None, 0)[0] == "unissued"
        assert registry.match("function", "exec_command", "call_a", "b" * 64, 1)[0] == "mismatched"
        assert registry.match("function", "exec_command", "call_a", "a" * 64, 2)[0] == "mismatched"

    def test_match_with_boolean_position_is_typed_unsupported(self) -> None:
        registry = model.IssuedRegistry()
        state, _ = registry.match("function", "exec_command", "call_a", None, True)
        assert state == "unsupported"

    def test_count_tracks_retention(self) -> None:
        registry = model.IssuedRegistry()
        assert registry.count() == 0
        registry.issue("function", "a", "id_a", None, 0)
        assert registry.count() == 1


class TestRegistryLookupAndEntries:
    def test_lookup_exact_and_unissued(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "exec_command", "call_X1", "a" * 64, 0)
        state, entry = registry.lookup("call_X1")
        assert state == "exact_issued"
        assert entry["name"] == "exec_command"
        assert registry.lookup("call_missing")[0] == "unissued"
        assert registry.lookup("bad id")[0] == "unsupported"

    def test_entries_closed_and_ordered(self) -> None:
        registry = model.IssuedRegistry()
        registry.issue("function", "b", "id_b", None, 1)
        registry.issue("function", "a", "id_a", "b" * 64, 0)
        entries = registry.entries()
        assert [e["call_id"] for e in entries] == ["id_a", "id_b"]
        assert all(
            set(e)
            == {"issue_seq", "family", "name", "call_id", "arguments_sha256", "request_position"}
            for e in entries
        )


# -- quiesce / snapshot / teardown / publish / ci summary --------------------------
class TestQuiesceRecord:
    def test_valid_closure_evidence_accepted(self) -> None:
        model.validate_quiesce_record(quiesce_record())

    @pytest.mark.parametrize(
        "field, value",
        [
            ("active_connections", 1),
            ("residual_writers", 1),
            ("provider_sockets_closed", False),
            ("handlers_stopped", False),
            ("owned_subject_stopped", False),
            ("owned_tools_stopped", False),
        ],
    )
    def test_incomplete_closure_rejected(self, field: Any, value: Any) -> None:
        record = quiesce_record()
        record[field] = value
        with pytest.raises(FixtureError):
            model.validate_quiesce_record(record)


class TestSnapshotRecord:
    def test_valid_snapshot_accepted(self) -> None:
        model.validate_snapshot_record(snapshot_record())

    def test_non_function_issued_call_rejected(self) -> None:
        record = snapshot_record()
        record["issued_calls"][0]["family"] = "custom"
        with pytest.raises(FixtureError):
            model.validate_snapshot_record(record)

    def test_unclosed_call_id_rejected(self) -> None:
        record = snapshot_record()
        record["issued_calls"][0]["call_id"] = "bad id"
        with pytest.raises(FixtureError):
            model.validate_snapshot_record(record)

    def test_zero_originals_rejected(self) -> None:
        record = snapshot_record()
        record["originals_bytes"] = 0
        with pytest.raises(FixtureError):
            model.validate_snapshot_record(record)

    def test_wrong_exporter_uid_rejected(self) -> None:
        record = snapshot_record()
        record["exporter_uid"] = 21002
        with pytest.raises(FixtureError):
            model.validate_snapshot_record(record)

    def test_copy_after_destroy_rejected(self) -> None:
        record = snapshot_record()
        record["exported_before_teardown"] = False
        with pytest.raises(FixtureError):
            model.validate_snapshot_record(record)


class TestTeardownRecord:
    def test_valid_positive_before_negative_after_accepted(self) -> None:
        model.validate_teardown_record(teardown_record())

    def test_query_failure_is_not_absence(self) -> None:
        for field in ("container_inspect_after", "image_inspect_after"):
            record = teardown_record()
            record[field] = "query-failed-unverified"
            with pytest.raises(FixtureError):
                model.validate_teardown_record(record)

    def test_still_present_rejected(self) -> None:
        record = teardown_record()
        record["container_inspect_after"] = "present-unexpected"
        with pytest.raises(FixtureError):
            model.validate_teardown_record(record)

    def test_surviving_descendant_rejected(self) -> None:
        record = teardown_record()
        record["descendants_after"] = 1
        with pytest.raises(FixtureError):
            model.validate_teardown_record(record)

    def test_no_positive_before_rejected(self) -> None:
        record = teardown_record()
        record["descendants_before"] = 0
        with pytest.raises(FixtureError):
            model.validate_teardown_record(record)

    def test_cid_must_be_64_hex(self) -> None:
        record = teardown_record()
        record["cid"] = "short"
        with pytest.raises(FixtureError):
            model.validate_teardown_record(record)


class TestPublishRecord:
    def test_valid_publication_evidence_accepted(self) -> None:
        model.validate_publish_record(publish_record(), model.FixtureBudgets())

    @pytest.mark.parametrize(
        "field, value",
        [
            ("publish_dir_mode", 0o755),
            ("artifact_file_mode", 0o644),
            ("snapshot_digest_match", False),
            ("deadline_expired", True),
            ("api_requests", 513),
            ("api_attempts", 65),
            ("bytes_drained", 64 * 1024 * 1024 + 1),
            ("requests_admitted", 11),
            ("requests_refused", 0),
            ("bytes_retained", 4097),
        ],
    )
    def test_invalid_publication_rejected(self, field: Any, value: Any) -> None:
        record = publish_record()
        record[field] = value
        with pytest.raises(FixtureError):
            model.validate_publish_record(record, model.FixtureBudgets())

    def test_negative_counts_rejected(self) -> None:
        for field in (
            "api_requests",
            "api_attempts",
            "bytes_drained",
            "bytes_retained",
            "healthz_attempts",
            "docker_admissions",
            "docker_refusals",
        ):
            record = publish_record()
            record[field] = -1
            with pytest.raises(FixtureError):
                model.validate_publish_record(record, model.FixtureBudgets())


class TestCiSummary:
    def test_valid_summary_accepted(self) -> None:
        model.validate_ci_summary(ci_summary_record())

    def test_codex_invocation_flag_rejected(self) -> None:
        record = ci_summary_record()
        record["codex_invoked"] = True
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_unknown_scenario_name_rejected(self) -> None:
        record = ci_summary_record()
        record["scenarios"][0]["name"] = "native-startup"
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_duplicate_scenario_rejected(self) -> None:
        record = ci_summary_record()
        record["scenarios"].append(dict(record["scenarios"][0]))
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_partial_matrix_rejected(self) -> None:
        record = ci_summary_record()
        record["scenarios"] = record["scenarios"][:3]
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_wrong_declared_outcome_rejected(self) -> None:
        record = ci_summary_record()
        for entry in record["scenarios"]:
            if entry["name"] == "synthetic-success":
                entry["state"] = "crashed-as-designed"
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_deliberate_fail_state_rejected_on_success_scenario(self) -> None:
        record = ci_summary_record()
        for entry in record["scenarios"]:
            if entry["name"] == "synthetic-hang":
                entry["state"] = "failed-as-designed"
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_unverified_removal_rejected(self) -> None:
        for field in ("container_removal", "image_removal"):
            record = ci_summary_record()
            record[field] = "query-failed-unverified"
            with pytest.raises(FixtureError):
                model.validate_ci_summary(record)

    def test_summary_mount_root_unlisted_rejected(self) -> None:
        record = ci_summary_record()
        record["writable_mounts"][0]["root"] = "/run/unlisted"
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_summary_shm_root_missing_rejected(self) -> None:
        record = ci_summary_record()
        record["writable_mounts"] = [
            m for m in record["writable_mounts"] if m["root"] != model.SHM_MOUNT
        ]
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)

    def test_summary_total_identity_and_bound_rejected(self) -> None:
        record = ci_summary_record()
        record["writable_data_total_bytes"] += 1
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)
        record = ci_summary_record()
        record["writable_data_total_bytes"] = model.WRITABLE_DATA_TOTAL_MAX_BYTES + 1
        for entry in record["writable_mounts"]:
            entry["size_bytes"] = model.WRITABLE_DATA_TOTAL_MAX_BYTES + 1 // len(
                record["writable_mounts"]
            )
        record["writable_mounts"][0]["size_bytes"] += (
            model.WRITABLE_DATA_TOTAL_MAX_BYTES + 1
        ) % len(record["writable_mounts"])
        with pytest.raises(FixtureError):
            model.validate_ci_summary(record)


# -- 21001 export client (scripted fake sockets, no real IO) ------------------
class _FakeStdout:
    """Captures the client's text lines and raw buffer writes
    separately so publication can be asserted byte-exactly."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.raw = bytearray()

        class _Buffer:
            def __init__(self, owner: _FakeStdout) -> None:
                self._owner = owner

            def write(self, data: bytes) -> int:
                self._owner.raw += data
                return len(data)

            def flush(self) -> None:
                pass

        self.buffer = _Buffer(self)

    def write(self, text: str) -> int:
        self.lines.append(text)
        return len(text)

    def flush(self) -> None:
        pass


class _ScriptedSock:
    """Scripted AF_UNIX stand-in: exact-byte stream, recorded
    settimeout/sendall, optional first-recv hang for the shared
    deadline proof.  No real socket is ever created."""

    def __init__(self, stream: bytes, hang: float | None = None) -> None:
        self.stream = stream
        self.sent = bytearray()
        self.timeouts: list[float] = []
        self.hang = hang
        self.closed = False

    def settimeout(self, seconds: float) -> None:
        self.timeouts.append(seconds)

    def sendall(self, data: bytes) -> None:
        self.sent += data

    def recv(self, n: int) -> bytes:
        if self.hang is not None:
            time.sleep(self.hang)
            self.hang = None
        if not self.stream:
            return b""
        chunk = self.stream[:n]
        self.stream = self.stream[len(chunk) :]
        return chunk

    def close(self) -> None:
        self.closed = True


_EXPORT_ORIGINALS = (b"\x00" * 512, b"\x01" * 512, b"\x02" * 512)


def _export_payload(
    diagnostic: dict[str, Any] | None = None,
    position: int | None = None,
    originals: tuple[bytes, ...] | None = None,
    snapshot_override: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
    drop: str | None = None,
) -> bytes:
    originals = _EXPORT_ORIGINALS if originals is None else originals
    combined = b"".join(originals)
    snap = snapshot_record()
    snap["originals_bytes"] = len(combined)
    snap["originals_sha256"] = hashlib.sha256(combined).hexdigest()
    if snapshot_override is not None:
        # applied AFTER the real binding so corrupted record values
        # survive into the payload
        snap.update(snapshot_override)
    selected: dict[str, Any] = {
        "quiesce": quiesce_record(),
        "snapshot": snap,
        "diagnostic": ({"state": "unobserved"} if diagnostic is None else diagnostic),
        "observed_at_position": position,
        "originals": [base64.b64encode(o).decode("ascii") for o in originals],
        "originals_count": 3,
    }
    if extra is not None:
        selected.update(extra)
    if drop is not None:
        selected.pop(drop)
    return json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()


def _frame(payload: bytes, digest: bytes | None = None) -> bytes:
    used = digest if digest is not None else hashlib.sha256(payload).hexdigest().encode()
    return struct.pack(">I", len(payload)) + payload + used


def _quiesce_stream(record: dict[str, Any] | None = None) -> bytes:
    record = record or quiesce_record()
    return (
        b"quiesce-ok " + json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )


class TestExportClient:
    """Closed-proof tests of the ACTUAL 21001 export client with
    scripted fake sockets: the valid export publishes byte-exactly
    after the closed-object proof, and every corruption, truncation,
    trailing byte, deadline and uid violation is a fixed typed
    failure that NEVER emits or reflects the raw payload."""

    def _install(
        self, monkeypatch: Any, streams: list[_ScriptedSock]
    ) -> tuple[_FakeStdout, dict[str, int]]:
        stdout = _FakeStdout()
        monkeypatch.setattr(sys, "stdout", stdout)
        monkeypatch.setattr(client.os, "getuid", lambda: 21001)
        monkeypatch.delenv("SLAIF_FIXTURE_DEADLINE_ABS", raising=False)
        calls = {"n": 0}

        def fake_connect(deadline: float) -> _ScriptedSock:
            calls["n"] += 1
            return streams.pop(0)

        monkeypatch.setattr(client, "_connect", fake_connect)
        return stdout, calls

    def _assert_fail(self, stdout: _FakeStdout, reason: str) -> None:
        # quiesce legitimately succeeded before the export phase
        # failed: its record line is expected; the export phase must
        # publish nothing but the fixed closed reason.
        assert len(stdout.lines) == 2
        assert stdout.lines[0].startswith("quiesce-ok ")
        assert stdout.lines[1] == f"export-fail {reason}\n"
        assert not any(line.startswith("export-sha256") for line in stdout.lines)
        assert bytes(stdout.raw) == b""

    def test_main_takes_no_arguments(self) -> None:
        # the review-11 fatal: main(sys.argv) is not an entrypoint
        assert inspect.signature(client.main).parameters == {}

    def test_wrong_uid_refused_before_any_io(self, monkeypatch: Any) -> None:
        stdout, calls = self._install(monkeypatch, [])
        monkeypatch.setattr(client.os, "getuid", lambda: 1001)
        assert client.main() == 2
        assert stdout.lines == ["export-fail uid-not-21001\n"]
        assert bytes(stdout.raw) == b""
        assert calls["n"] == 0

    def test_valid_export_publishes_byte_exact(self, monkeypatch: Any) -> None:
        payload = _export_payload()
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(payload)),
            ],
        )
        assert client.main() == 0
        assert len(stdout.lines) == 2
        assert stdout.lines[0].startswith("quiesce-ok ")
        record = json.loads(stdout.lines[0][len("quiesce-ok ") :])
        model.validate_quiesce_record(record)
        assert stdout.lines[1] == "export-sha256 " + hashlib.sha256(payload).hexdigest() + "\n"
        assert bytes(stdout.raw) == payload
        # the published raw payload re-validates as a closed object
        assert client.validate_payload(bytes(stdout.raw))["originals_count"] == 3

    def test_digest_mismatch_refused(self, monkeypatch: Any) -> None:
        payload = _export_payload()
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(payload, digest=b"ab" * 32)),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-digest")

    def test_truncated_frame_refused(self, monkeypatch: Any) -> None:
        payload = _export_payload()
        stream = _frame(payload)
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(stream[:-10]),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_trailing_frame_bytes_refused(self, monkeypatch: Any) -> None:
        payload = _export_payload()
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(payload) + b"slaif-canary"),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_unknown_top_level_field_refused(self, monkeypatch: Any) -> None:
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(_export_payload(extra={"raw": "slaif-canary"}))),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_original_digest_binding_refused(self, monkeypatch: Any) -> None:
        # a valid frame digest proves framing integrity only: a
        # snapshot digest that does not bind the DECODED originals
        # must fail closed with no publication
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(
                    _frame(_export_payload(snapshot_override={"originals_sha256": "ab" * 32}))
                ),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_original_size_binding_refused(self, monkeypatch: Any) -> None:
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(_export_payload(snapshot_override={"originals_bytes": 999}))),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_unobserved_marker_with_position_refused(self, monkeypatch: Any) -> None:
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(
                    _frame(_export_payload(diagnostic={"state": "unobserved"}, position=0))
                ),
            ],
        )
        assert client.main() == 2
        self._assert_fail(stdout, "export-invalid")

    def test_invalid_anchor_refused(self, monkeypatch: Any) -> None:
        stdout, calls = self._install(monkeypatch, [])
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", "abc")
        assert client.main() == 2
        assert stdout.lines == ["export-fail deadline-invalid\n"]
        assert bytes(stdout.raw) == b""
        assert calls["n"] == 0

    def test_expired_anchor_before_any_io(self, monkeypatch: Any) -> None:
        stdout, calls = self._install(monkeypatch, [])
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() - 10.0))
        assert client.main() == 2
        assert stdout.lines == ["export-fail deadline-expired\n"]
        assert bytes(stdout.raw) == b""
        assert calls["n"] == 0

    def test_slow_read_past_shared_deadline(self, monkeypatch: Any) -> None:
        payload = _export_payload()
        stdout, _ = self._install(
            monkeypatch,
            [
                _ScriptedSock(_quiesce_stream()),
                _ScriptedSock(_frame(payload), hang=0.3),
            ],
        )
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() + 0.15))
        assert client.main() == 2
        self._assert_fail(stdout, "deadline-expired")
