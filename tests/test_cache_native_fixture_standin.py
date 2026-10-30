"""Pure/mock tests for the 21002 stand-in (017-r).

Exercises the ACTUAL helper paths with fakes only: the exact reviewed
keyring ABI via a call-recording fake libc (no real syscall is ever
issued), the architecture guard, v1 cgroup swap derivation (equal
positive, underflow, missing, unlimited), the EROFS-only rootfs proof
(read-write and permission-only negatives), namespace grammar, exact
CPU math, the exact tagged SSE parser (order/duplicate/missing/
unknown negatives), the closed reason mapping including the
http.client.HTTPException escape path, stopper identity
verification, and the synthetic profile record against the closed
model schema.  No local fixture root, no network, no Codex.
"""

from __future__ import annotations

import importlib.util
import json
import os
import signal
import stat
import sys
import time
import tomllib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, NoReturn

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_model.py"
STANDIN_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_standin.py"

model_spec = importlib.util.spec_from_file_location("cache_native_fixture_model", MODEL_PATH)
assert model_spec is not None and model_spec.loader is not None
model = importlib.util.module_from_spec(model_spec)
sys.modules["cache_native_fixture_model"] = model
model_spec.loader.exec_module(model)

standin_spec = importlib.util.spec_from_file_location("cache_native_fixture_standin", STANDIN_PATH)
assert standin_spec is not None and standin_spec.loader is not None
standin = importlib.util.module_from_spec(standin_spec)
sys.modules["cache_native_fixture_standin"] = standin
standin_spec.loader.exec_module(standin)

StandinError = standin.StandinError


def _set_module_attr(module: Any, name: str, value: str) -> None:
    setattr(module, name, value)


# -- exact reviewed keyring ABI via fake libc (no real syscall) -------------
class FakeLibc:
    """Records every syscall call and programs the returned errno."""

    def __init__(self, errno_value: int = 1) -> None:
        self.calls: list[tuple[int, tuple[Any, ...]]] = []
        self.errno_value = errno_value

    def syscall(self, number: int, *args: object) -> int:
        # ctypes.c_long instances expose the integer via .value;
        # int() on a ctypes instance is NOT a conversion in 3.12
        num = getattr(number, "value", number)
        self.calls.append((int(num), args))
        sys.modules["cache_native_fixture_standin"].ctypes.set_errno(self.errno_value)
        return -1


class FakeUname:
    def __init__(self, system: str = "Linux", machine: str = "x86_64") -> None:
        self.system = system
        self.machine = machine


class TestKeyringAbi:
    def test_exact_reviewed_argument_forms(self, monkeypatch: Any) -> None:
        fake = FakeLibc(errno_value=1)
        monkeypatch.setattr(standin.platform, "uname", lambda: FakeUname())
        result = standin.measure_keyring_errno(libc=fake)
        assert result == {"add_key": 1, "request_key": 1, "keyctl": 1}
        assert len(fake.calls) == 3
        (no1, args1), (no2, args2), (no3, args3) = fake.calls
        # add_key: full five-argument x86_64 form, NULL type/desc/
        # payload, datalen 0, destination keyring serial 0
        assert no1 == 248
        assert len(args1) == 5
        assert all(isinstance(a, standin.ctypes.c_void_p) for a in args1[:3])
        assert args1[3].value == 0 and args1[4].value == 0
        # request_key: four-argument form
        assert no2 == 249
        assert len(args2) == 4
        assert args2[3].value == 0
        # keyctl: UNKNOWN command -1 (names no linux/keyctl.h opcode)
        assert no3 == 250
        assert args3[0].value == -1

    def test_no_valid_key_type_or_payload_ever_passed(self, monkeypatch: Any) -> None:
        fake = FakeLibc(errno_value=1)
        monkeypatch.setattr(standin.platform, "uname", lambda: FakeUname())
        standin.measure_keyring_errno(libc=fake)
        for _no, args in fake.calls:
            for arg in args:
                if isinstance(arg, standin.ctypes.c_void_p):
                    assert arg.value is None  # NULL: cannot name a key

    def test_non_x86_64_fails_before_any_syscall(self, monkeypatch: Any) -> None:
        fake = FakeLibc()
        monkeypatch.setattr(standin.platform, "uname", lambda: FakeUname(machine="aarch64"))
        with pytest.raises(StandinError) as excinfo:
            standin.measure_keyring_errno(libc=fake)
        assert excinfo.value.args[0] == "platform-not-x86_64"
        assert fake.calls == []  # no syscall issued at all

    def test_non_linux_fails_before_any_syscall(self, monkeypatch: Any) -> None:
        fake = FakeLibc()
        monkeypatch.setattr(standin.platform, "uname", lambda: FakeUname(system="FreeBSD"))
        with pytest.raises(StandinError):
            standin.measure_keyring_errno(libc=fake)
        assert fake.calls == []


# -- cgroup swap derivation -----------------------------------------------------
class TestSwapDerivation:
    def _patch(self, monkeypatch: Any, values: dict[str, str | None], v2: bool) -> None:
        def fake_value(name: str) -> str | None:
            return values.get(name)

        monkeypatch.setattr(standin, "_cgroup_value", fake_value)
        import os as os_mod

        if v2:
            monkeypatch.setattr(os_mod.path, "isfile", lambda p: p == "/sys/fs/cgroup/memory.max")
        else:
            monkeypatch.setattr(os_mod.path, "isfile", lambda p: False)

    def test_equal_limits_zero_swap_positive(self, monkeypatch: Any) -> None:
        self._patch(monkeypatch, {"memory.max": "1073741824", "memory.swap.max": "0"}, True)
        assert standin.cgroup_memory_swap() == (1073741824, 0, "v2-swap-max")

    def test_v1_equal_limits_zero_swap(self, monkeypatch: Any) -> None:
        self._patch(
            monkeypatch,
            {"memory.limit_in_bytes": "1073741824", "memory.memsw.limit_in_bytes": "1073741824"},
            False,
        )
        assert standin.cgroup_memory_swap() == (1073741824, 0, "v1-memsw-combined")

    def test_v1_underflow_is_typed_invalid_not_zero(self, monkeypatch: Any) -> None:
        self._patch(
            monkeypatch,
            {"memory.limit_in_bytes": "1073741824", "memory.memsw.limit_in_bytes": "536870912"},
            False,
        )
        with pytest.raises(StandinError) as excinfo:
            standin.cgroup_memory_swap()
        assert excinfo.value.args[0] == "swap-derivation-invalid"

    @pytest.mark.parametrize("name", ["memory.swap.max", "memory.memsw.limit_in_bytes"])
    def test_missing_swap_never_inferred(self, monkeypatch: Any, name: Any) -> None:
        v2 = name == "memory.swap.max"
        mem = "memory.max" if v2 else "memory.limit_in_bytes"
        self._patch(monkeypatch, {mem: "1073741824"}, v2)
        with pytest.raises(StandinError) as excinfo:
            standin.cgroup_memory_swap()
        assert excinfo.value.args[0] == "swap-missing"

    def test_v1_unlimited_sentinel_missing(self, monkeypatch: Any) -> None:
        self._patch(
            monkeypatch,
            {
                "memory.limit_in_bytes": "1073741824",
                "memory.memsw.limit_in_bytes": str(0x7FFFFFFFFFFFF000),
            },
            False,
        )
        with pytest.raises(StandinError) as excinfo:
            standin.cgroup_memory_swap()
        assert excinfo.value.args[0] == "swap-missing"

    def test_v2_unlimited_rejected(self, monkeypatch: Any) -> None:
        self._patch(monkeypatch, {"memory.max": "1073741824", "memory.swap.max": "max"}, True)
        with pytest.raises(StandinError) as excinfo:
            standin.cgroup_memory_swap()
        assert excinfo.value.args[0] == "swap-unlimited"


# -- EROFS-only rootfs proof -------------------------------------------------------
class TestRootfsProof:
    def test_erofs_is_the_only_proof(self, monkeypatch: Any) -> None:
        def open_erofs(path: Any, flags: Any, mode: Any = 0) -> NoReturn:
            import errno as errno_mod

            exc = OSError(errno_mod.EROFS, "Read-only file system")
            raise exc

        monkeypatch.setattr(os.path, "lexists", lambda p: False)
        monkeypatch.setattr(standin.os, "open", open_erofs)
        assert standin.measure_rootfs_readonly("/img/.ro-probe") is True

    def test_successful_create_is_containment_failure(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(os.path, "lexists", lambda p: False)

        def open_rw(path: Any, flags: Any, mode: Any = 0) -> int:
            return 7

        monkeypatch.setattr(standin.os, "open", open_rw)
        monkeypatch.setattr(standin.os, "close", lambda fd: None)
        monkeypatch.setattr(standin.os, "unlink", lambda p: None)
        with pytest.raises(StandinError) as excinfo:
            standin.measure_rootfs_readonly("/img/.ro-probe")
        assert excinfo.value.args[0] == "rootfs-writable"

    def test_permission_denial_is_not_proof(self, monkeypatch: Any) -> None:
        import errno as errno_mod

        monkeypatch.setattr(os.path, "lexists", lambda p: False)

        def open_eacces(path: Any, flags: Any, mode: Any = 0) -> NoReturn:
            raise OSError(errno_mod.EACCES, "Permission denied")

        monkeypatch.setattr(standin.os, "open", open_eacces)
        with pytest.raises(StandinError) as excinfo:
            standin.measure_rootfs_readonly("/img/.ro-probe")
        assert excinfo.value.args[0] == "rootfs-proof-inconclusive"

    def test_pre_existing_path_refused(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(os.path, "lexists", lambda p: True)
        with pytest.raises(StandinError) as excinfo:
            standin.measure_rootfs_readonly("/img/.ro-probe")
        assert excinfo.value.args[0] == "ro-probe-exists"


# -- namespace grammar ---------------------------------------------------------------
class TestNamespaceGrammar:
    def _patch(
        self, monkeypatch: Any, self_ids: dict[str, str], parent_ids: dict[str, str]
    ) -> None:
        monkeypatch.setattr(standin.os, "readlink", lambda p: self_ids[p.rsplit("/", 1)[1]])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_PID", parent_ids["pid"])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_MNT", parent_ids["mnt"])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_IPC", parent_ids["ipc"])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_UTS", parent_ids["uts"])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_NET", parent_ids["net"])
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_USER", parent_ids["user"])

    def test_private_shared_user_mapping(self, monkeypatch: Any) -> None:
        self._patch(
            monkeypatch,
            {
                "pid": "pid:[200]",
                "mnt": "mnt:[300]",
                "ipc": "ipc:[400]",
                "uts": "uts:[500]",
                "net": "net:[600]",
                "user": "user:[10]",
            },
            {
                "pid": "pid:[1]",
                "mnt": "mnt:[2]",
                "ipc": "ipc:[3]",
                "uts": "uts:[4]",
                "net": "net:[5]",
                "user": "user:[10]",
            },
        )
        facts = standin.measure_namespaces(standin.parent_namespaces_from_env())
        assert facts == {
            "pid_private": True,
            "mount_private": True,
            "ipc_private": True,
            "uts_private": True,
            "net_private": True,
            "user_shared": True,
        }

    def test_invalid_parent_grammar_rejected(self, monkeypatch: Any) -> None:
        monkeypatch.setenv("SLAIF_FIXTURE_PARENT_NS_PID", "pid/200")
        with pytest.raises(StandinError) as excinfo:
            standin.parent_namespaces_from_env()
        assert excinfo.value.args[0] == "parent-namespace-invalid"

    def test_self_grammar_failure_rejected(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(standin.os, "readlink", lambda p: "pid/200")
        parent = {n: f"{n}:[{i}]" for i, n in enumerate(standin.NS_NAMES, start=1)}
        for name in standin.NS_NAMES:
            monkeypatch.setenv(f"SLAIF_FIXTURE_PARENT_NS_{name.upper()}", parent[name])
        with pytest.raises(StandinError):
            standin.measure_namespaces(parent)


# -- exact CPU math --------------------------------------------------------------------
class TestCpuMath:
    def _patch(self, monkeypatch: Any, values: dict[str, str | None]) -> None:
        monkeypatch.setattr(standin, "_cgroup_value", lambda name: values.get(name))
        monkeypatch.setattr(os.path, "isfile", lambda p: values.get(p.split("/")[-1]) is not None)

    def test_exact_one_cpu(self, monkeypatch: Any) -> None:
        self._patch(monkeypatch, {"cpu.max": "100000 100000"})
        assert standin.cpu_limit(1) == 1

    def test_flooring_must_not_pass(self, monkeypatch: Any) -> None:
        self._patch(monkeypatch, {"cpu.max": "150000 100000"})
        with pytest.raises(StandinError) as excinfo:
            standin.cpu_limit(1)
        assert excinfo.value.args[0] == "cpu-mismatch"

    def test_unlimited_rejected(self, monkeypatch: Any) -> None:
        self._patch(monkeypatch, {"cpu.max": "max 100000"})
        with pytest.raises(StandinError) as excinfo:
            standin.cpu_limit(1)
        assert excinfo.value.args[0] == "cpu-unlimited"


# -- exact tagged SSE parser (0.164.0 wire subset) --------------------------------
def _sse(events: list[tuple[str, dict[str, Any]]]) -> bytes:
    out = []
    for event_type, data in events:
        out.append(f"event: {event_type}\ndata: {json.dumps(data)}\n\n")
    return "".join(out).encode()


def _created(rid: str = "resp_1") -> tuple[str, dict[str, Any]]:
    return (
        "response.created",
        {
            "type": "response.created",
            "response": {"id": rid, "object": "response", "status": "in_progress", "output": []},
        },
    )


def _added(item: dict[str, Any], index: int = 0) -> tuple[str, dict[str, Any]]:
    return (
        "response.output_item.added",
        {"type": "response.output_item.added", "output_index": index, "item": item},
    )


def _done(item: dict[str, Any], index: int = 0) -> tuple[str, dict[str, Any]]:
    return (
        "response.output_item.done",
        {"type": "response.output_item.done", "output_index": index, "item": item},
    )


def _completed(
    rid: str = "resp_1", items: list[dict[str, Any]] | None = None
) -> tuple[str, dict[str, Any]]:
    return (
        "response.completed",
        {
            "type": "response.completed",
            "response": {"id": rid, "status": "completed", "output": items or []},
        },
    )


def _msg_item(text: str = "x") -> dict[str, Any]:
    return {
        "type": "message",
        "id": "m1",
        "role": "assistant",
        "content": [{"type": "output_text", "text": text}],
    }


def _fc_item(
    name: str = "exec_command", call_id: str = "c1", args: str = '{"cmd":"slaif-synthetic-cmd"}'
) -> dict[str, Any]:
    return {
        "type": "function_call",
        "id": "fc1",
        "call_id": call_id,
        "name": name,
        "arguments": args,
    }


def _full(
    msg: dict[str, Any] | None = None, fc: dict[str, Any] | None = None, rid: str = "resp_1"
) -> list[tuple[str, dict[str, Any]]]:
    """A well-formed created/(added,done)* /completed sequence."""
    events = [_created(rid)]
    items = []
    index = 0
    for item in (fc, msg) if (fc or msg) else ():
        if item is None:
            continue
        events.append(_added(item, index))
        events.append(_done(item, index))
        items.append(item)
        index += 1
    events.append(_completed(rid, items))
    return events


class TestSseParser:
    def test_valid_sequence_message(self) -> None:
        msg = _msg_item()
        parsed = standin._parse_sse(_sse(_full(msg=msg)), expect_items=1)
        assert parsed["items"] == [msg]
        assert parsed["response_id"] == "resp_1"

    def test_valid_sequence_function_call_then_message(self) -> None:
        fc = _fc_item()
        msg = _msg_item("slaif fixed final text")
        parsed = standin._parse_sse(_sse(_full(fc=fc, msg=msg)), expect_items=2)
        assert parsed["items"] == [fc, msg]

    def test_created_must_be_first(self) -> None:
        bad_id: Any = _msg_item()
        body = _sse([_added(_msg_item()), _created(), _done(_msg_item()), _completed(bad_id)])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-order"

    def test_missing_completed_rejected(self) -> None:
        body = _sse([_created(), _added(_msg_item()), _done(_msg_item())])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-incomplete"

    def test_unterminated_added_rejected(self) -> None:
        bad_id: Any = _msg_item()
        body = _sse([_created(), _added(_msg_item()), _completed(bad_id)])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-incomplete"

    def test_done_without_added_rejected(self) -> None:
        bad_id: Any = _msg_item()
        body = _sse([_created(), _done(_msg_item()), _completed(bad_id)])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-order"

    def test_duplicate_completed_rejected(self) -> None:
        body = _sse([_created(), _completed(), _completed()])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-duplicate"

    def test_duplicate_created_rejected(self) -> None:
        body = _sse([_created(), _created(), _completed()])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-duplicate"

    def test_unknown_event_rejected(self) -> None:
        body = _sse([_created(), ("response.bogus", {"type": "response.bogus"}), _completed()])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-event-unknown"

    def test_type_mismatch_rejected(self) -> None:
        body = _sse([("response.created", {"type": "response.completed"}), _completed()])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-event-mismatch"

    def test_item_count_mismatch_rejected(self) -> None:
        body = _sse(
            [
                _created(),
                _added(_msg_item(), 0),
                _done(_msg_item(), 0),
                _added(_msg_item(), 1),
                _done(_msg_item(), 1),
                _completed("resp_1", [_msg_item(), _msg_item()]),
            ]
        )
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body, expect_items=1)
        assert excinfo.value.args[0] == "sse-item-count"

    def test_response_id_must_match(self) -> None:
        body = _sse([_created("resp_a"), _completed("resp_b")])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-response-id"

    def test_done_item_must_match_added_item(self) -> None:
        body = _sse(
            [
                _created(),
                _added(_msg_item("a"), 0),
                _done(_msg_item("b"), 0),
                _completed("resp_1", [_msg_item("b")]),
            ]
        )
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-mismatch"

    def test_output_index_must_ascending(self) -> None:
        m0, m1 = _msg_item("a"), _msg_item("b")
        body = _sse(
            [
                _created(),
                _added(m0, 0),
                _done(m0, 0),
                _added(m1, 0),
                _done(m1, 0),
                _completed("resp_1", [m0, m1]),
            ]
        )
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-order"

    def test_completed_output_must_equal_done_items(self) -> None:
        body = _sse(
            [_created(), _added(_msg_item(), 0), _done(_msg_item(), 0), _completed("resp_1", [])]
        )
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-output-mismatch"

    def test_message_role_required(self) -> None:
        item = {"type": "message", "id": "m1", "content": [{"type": "output_text", "text": "x"}]}
        body = _sse([_created(), _added(item, 0), _done(item, 0), _completed("resp_1", [item])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-shape"

    def test_message_wrong_role_rejected(self) -> None:
        item = {
            "type": "message",
            "id": "m1",
            "role": "user",
            "content": [{"type": "output_text", "text": "x"}],
        }
        body = _sse([_created(), _added(item, 0), _done(item, 0), _completed("resp_1", [item])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-role"

    def test_output_text_field_required(self) -> None:
        item = {
            "type": "message",
            "id": "m1",
            "role": "assistant",
            "content": [{"type": "output_text"}],
        }
        body = _sse([_created(), _added(item, 0), _done(item, 0), _completed("resp_1", [item])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-shape"

    def test_annotations_optional_and_accepted(self) -> None:
        item = {
            "type": "message",
            "id": "m1",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "x", "annotations": []}],
        }
        parsed = standin._parse_sse(
            _sse([_created(), _added(item, 0), _done(item, 0), _completed("resp_1", [item])])
        )
        assert parsed["items"] == [item]

    def test_function_call_arguments_closed(self) -> None:
        # extra unknown field for a known tool: refused
        bad = _fc_item(args='{"cmd":"x","extra":1}')
        body = _sse([_created(), _added(bad, 0), _done(bad, 0), _completed("resp_1", [bad])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-shape"
        # non-JSON arguments: refused
        bad2 = _fc_item(args="not json")
        body = _sse([_created(), _added(bad2, 0), _done(bad2, 0), _completed("resp_1", [bad2])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-shape"

    def test_unknown_item_type_rejected(self) -> None:
        item = {"type": "custom", "id": "c1"}
        body = _sse([_created(), _added(item, 0), _done(item, 0), _completed("resp_1", [item])])
        with pytest.raises(StandinError) as excinfo:
            standin._parse_sse(body)
        assert excinfo.value.args[0] == "sse-item-unknown"


# -- closed reason mapping (actual entry paths) ---------------------------------------------
class TestClosedReasons:
    def test_http_exception_maps_to_fixed_protocol_reason(self) -> None:
        import http.client

        exc = http.client.HTTPException("BadStatusLine: synthetic_canary_line")
        assert standin.closed_reason(exc) == "provider-protocol"

    def test_socket_timeout_maps_fixed(self) -> None:
        assert standin.closed_reason(TimeoutError()) == "provider-timeout"

    def test_generic_oserror_maps_fixed(self) -> None:
        assert standin.closed_reason(ConnectionRefusedError()) == "provider-socket"

    def test_value_error_maps_fixed(self) -> None:
        assert standin.closed_reason(ValueError("nope")) == "provider-json"

    def test_arbitrary_exception_never_leaks_text(self) -> None:
        assert (
            standin.closed_reason(RuntimeError("totally arbitrary canary text"))
            == "standin-failure"
        )

    def test_valid_standin_reason_passthrough(self) -> None:
        assert (
            standin.closed_reason(StandinError("swap-derivation-invalid"))
            == "swap-derivation-invalid"
        )

    def test_standin_reason_with_canary_rejected(self) -> None:
        assert standin.closed_reason(StandinError("Bad Status Line")) == "standin-failure"


# -- stopper identity verification -------------------------------------------------------------
class TestStopperIdentity:
    def test_vanished_pid_is_not_a_target(self) -> None:
        assert standin._verify_owned_pid(99999999, 123, "a" * 32) is False

    def test_self_is_not_a_target(self) -> None:
        # own starttime/token cannot match the token requirement
        assert standin._verify_owned_pid(os.getpid(), 1, "a" * 32) is False

    def test_pidfd_open_precedes_verification_and_signal(self, monkeypatch: Any) -> None:
        order: list[str] = []
        # the fake fd must never reach a REAL os.close
        monkeypatch.setattr(standin.os, "close", lambda fd: None)

        def fake_open(pid: int) -> int:
            order.append("open")
            return 7

        def fake_verify(pid: int, starttime: int, token: str) -> bool:
            order.append("verify")
            return True

        def fake_send(fd: int, sig: int, siginfo: Any, flags: int) -> None:
            order.append("send")

        monkeypatch.setattr(standin.os, "pidfd_open", fake_open)
        monkeypatch.setattr(standin.signal, "pidfd_send_signal", fake_send)
        monkeypatch.setattr(standin, "_verify_owned_pid", fake_verify)
        assert standin._signal_owned(123, 456, "a" * 32) is True
        # the handle is bound BEFORE identity is re-verified, and the
        # signal goes to the handle, never a bare pid
        assert order == ["open", "verify", "send"]

    def test_send_uses_exact_sigterm_siginfo_none_flags_zero(self, monkeypatch: Any) -> None:
        import signal as signal_mod

        seen: dict[str, Any] = {}
        monkeypatch.setattr(standin.os, "close", lambda fd: None)

        def fake_send(fd: int, sig: int, siginfo: Any, flags: int) -> None:
            seen.update(fd=fd, sig=sig, siginfo=siginfo, flags=flags)

        monkeypatch.setattr(standin.os, "pidfd_open", lambda pid: 9)
        monkeypatch.setattr(standin.signal, "pidfd_send_signal", fake_send)
        monkeypatch.setattr(standin, "_verify_owned_pid", lambda *a: True)
        assert standin._signal_owned(123, 456, "a" * 32) is True
        assert seen["fd"] == 9
        assert seen["sig"] == signal_mod.SIGTERM
        assert seen["siginfo"] is None
        assert seen["flags"] == 0

    def test_descriptor_closed_on_all_paths(self, monkeypatch: Any) -> None:
        closed: list[int] = []
        monkeypatch.setattr(standin.os, "close", lambda fd: closed.append(fd))
        monkeypatch.setattr(standin.os, "pidfd_open", lambda pid: 7)
        monkeypatch.setattr(standin.signal, "pidfd_send_signal", lambda *a: None)
        # success path
        monkeypatch.setattr(standin, "_verify_owned_pid", lambda *a: True)
        assert standin._signal_owned(1, 2, "a" * 32) is True
        assert closed == [7]
        # unverified path: verified AFTER open, fd still closed
        closed.clear()
        monkeypatch.setattr(standin, "_verify_owned_pid", lambda *a: False)
        assert standin._signal_owned(1, 2, "a" * 32) is False
        assert closed == [7]
        # send refused: fixed failure, fd still closed
        closed.clear()
        monkeypatch.setattr(standin, "_verify_owned_pid", lambda *a: True)

        def refused(fd: Any, sig: Any, siginfo: Any, flags: Any) -> NoReturn:
            raise PermissionError("policy")

        monkeypatch.setattr(standin.signal, "pidfd_send_signal", refused)
        assert standin._signal_owned(1, 2, "a" * 32) is False
        assert closed == [7]
        # open vanished: no verify, no send, no fd to close
        closed.clear()

        def gone(pid: int) -> int:
            raise ProcessLookupError()

        monkeypatch.setattr(standin.os, "pidfd_open", gone)
        assert standin._signal_owned(1, 2, "a" * 32) is False
        assert closed == []

    def test_unverified_target_never_signalled(self, monkeypatch: Any) -> None:
        sends: list[Any] = []
        monkeypatch.setattr(standin.os, "close", lambda fd: None)
        monkeypatch.setattr(standin.os, "pidfd_open", lambda pid: 7)
        monkeypatch.setattr(standin.signal, "pidfd_send_signal", lambda *a: sends.append(a))
        monkeypatch.setattr(standin, "_verify_owned_pid", lambda *a: False)
        assert standin._signal_owned(1, 2, "a" * 32) is False
        assert sends == []

    def test_api_unavailable_is_declared_closed_failure(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(standin.os, "pidfd_open", None, raising=False)
        assert standin._signal_owned(1, 2, "a" * 32) is False
        monkeypatch.setattr(standin.os, "pidfd_open", lambda pid: 7)
        monkeypatch.setattr(standin.signal, "pidfd_send_signal", None, raising=False)
        assert standin._signal_owned(1, 2, "a" * 32) is False

    def test_owned_target_stopped_unrelated_survives(self) -> None:
        # two TINY owned python children with distinct tokens: the
        # stopper must take the exact registered target and leave the
        # unrelated child alive.
        import subprocess
        import uuid

        token = uuid.uuid4().hex
        other = uuid.uuid4().hex
        target = subprocess.Popen(
            [sys.executable, "-c", f"import time; time.sleep(300) # {token}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        unrelated = subprocess.Popen(
            [sys.executable, "-c", f"import time; time.sleep(300) # {other}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            starttime = standin._proc_starttime(target.pid)
            assert standin._signal_owned(target.pid, starttime, token) is True
            # the exact target terminated (SIGTERM default action)
            assert target.wait(timeout=5) == -signal.SIGTERM
            # the unrelated owned child SURVIVES
            assert unrelated.poll() is None
        finally:
            for child in (target, unrelated):
                try:
                    child.kill()
                    child.wait(timeout=5)
                except OSError:
                    pass


# -- synthetic profile record against the closed model schema ------------------------------
# -- reconciled writable-data inventory from the actual mount table ------


def _mountinfo_line(
    root: str, fstype: str = "tmpfs", rw: bool = True, major: str = "0:45", src_root: str = "/"
) -> str:
    opts = "rw,nosuid,nodev" if fstype == "tmpfs" and rw else "rw,nosuid" if rw else "ro,nosuid"
    return f"42 41 {major} {src_root} {root} {opts} - {fstype} none rw,seclabel"


class TestMeasureMounts:
    """The RECONCILED writable-data inventory: configured roots plus
    the daemon's bounded /dev/shm are measured from the ACTUAL mount
    table; kernel virtual/device filesystems stay a distinct class;
    any other writable data mount fails closed."""

    @staticmethod
    def _dirs(tmp_path: Path) -> list[Path]:
        dirs = []
        for name in ("ctl", "subj", "tmp", "shm"):
            d = tmp_path / name
            d.mkdir()
            dirs.append(d)
        return dirs

    @staticmethod
    def _specs(dirs: list[Path]) -> list[tuple[str, int, int, int]]:
        return [
            (str(dirs[0]), 64 * 1024 * 1024, 21001, 21001),
            (str(dirs[1]), 64 * 1024 * 1024, 21002, 21002),
            (str(dirs[2]), 64 * 1024 * 1024, 21002, 21002),
        ]

    def _table(self, tmp_path: Path, lines: list[str], monkeypatch: Any) -> None:
        table = tmp_path / "mountinfo"
        table.write_text("\n".join(lines) + "\n", encoding="ascii")
        monkeypatch.setattr(standin, "_MOUNTINFO_PATH", str(table))
        monkeypatch.setattr(standin, "_SHM_ROOT", str(tmp_path / "shm"))

    def test_reconciled_surface_measured_and_virtuals_excluded(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        dirs = self._dirs(tmp_path)
        lines = [
            _mountinfo_line("/", "overlay", rw=False),
            _mountinfo_line("/proc", "proc"),
            _mountinfo_line("/sys", "sysfs", rw=False),
            _mountinfo_line("/sys/fs/cgroup", "cgroup2", rw=False),
            _mountinfo_line("/dev", "tmpfs"),
            _mountinfo_line("/dev/pts", "devpts"),
            _mountinfo_line("/dev/mqueue", "mqueue"),
            _mountinfo_line(str(dirs[0])),
            _mountinfo_line(str(dirs[1])),
            _mountinfo_line(str(dirs[2])),
            _mountinfo_line(str(tmp_path / "shm")),
        ]
        self._table(tmp_path, lines, monkeypatch)
        mounts, scanned, masked = standin.measure_mounts(self._specs(dirs))
        # Baseline table: no masked /dev/null file aliases present.
        assert masked == 0
        assert scanned == len(lines)
        assert [m["root"] for m in mounts] == sorted(
            [str(dirs[0]), str(dirs[1]), str(dirs[2]), str(tmp_path / "shm")]
        )
        # Measured facts come from the actual lstat/statvfs.
        for entry in mounts:
            assert set(entry) == {"root", "size_bytes", "uid", "gid", "mode"}
            assert entry["size_bytes"] == (
                os.statvfs(entry["root"]).f_blocks * os.statvfs(entry["root"]).f_bsize
            )
        # The virtual/device rw class (proc, devpts, mqueue, /dev)
        # is NEVER counted as writable data.
        for virtual in ("/proc", "/dev", "/dev/pts", "/dev/mqueue"):
            assert virtual not in {m["root"] for m in mounts}

    def test_unlisted_rw_tmpfs_root_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        unlisted = tmp_path / "unlisted"
        unlisted.mkdir()
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            _mountinfo_line(str(unlisted)),
        ]
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="unlisted-writable-mount"):
            standin.measure_mounts(self._specs(dirs))

    def test_unlisted_rw_bind_mount_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        data = tmp_path / "data"
        data.mkdir()
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            _mountinfo_line(str(data), "ext4"),
        ]
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="unlisted-writable-mount"):
            standin.measure_mounts(self._specs(dirs))

    def test_missing_configured_root_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        lines = [
            _mountinfo_line(str(dirs[0])),
            _mountinfo_line(str(dirs[2])),
            _mountinfo_line(str(tmp_path / "shm")),
        ]
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="expected-writable-mount-missing"):
            standin.measure_mounts(self._specs(dirs))

    def test_missing_shm_root_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]]
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="expected-writable-mount-missing"):
            standin.measure_mounts(self._specs(dirs))

    def test_readonly_rw_misparse_and_malformed_fail_closed(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        dirs = self._dirs(tmp_path)
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            "this line has no separator",
        ]
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="mountinfo-malformed"):
            standin.measure_mounts(self._specs(dirs))

    def test_unreadable_mountinfo_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        monkeypatch.setattr(standin, "_MOUNTINFO_PATH", str(tmp_path / "absent"))
        monkeypatch.setattr(standin, "_SHM_ROOT", str(tmp_path / "shm"))
        with pytest.raises(StandinError, match="mountinfo-unreadable"):
            standin.measure_mounts(self._specs(dirs))

    def test_oversized_record_count_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        # A table beyond the closed record cap is fail-closed: a
        # truncated prefix is never labeled complete.
        dirs = self._dirs(tmp_path)
        lines = (
            [_mountinfo_line(str(d)) for d in dirs[:3]]
            + [
                _mountinfo_line(str(tmp_path / "shm")),
            ]
            + [_mountinfo_line(f"/tmp/synthetic-vg-{i:04d}") for i in range(520)]
        )
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="mountinfo-oversized"):
            standin.measure_mounts(self._specs(dirs))

    # -- masked /dev/null file aliases (runc maskPaths) -----------------
    # The default profile bind-masks selected procfs/sysfs FILES with
    # the /dev/null character device; those rw tmpfs aliases are a
    # device surface, admitted only under the strictly-evidenced
    # closed identity (source-root /null, narrow known-default path,
    # exact chr 1:3 node) and counted, never treated as data.

    @staticmethod
    def _chr_node(major: int = 1, minor: int = 3) -> Any:
        return SimpleNamespace(
            st_mode=stat.S_IFCHR | 0o666, st_rdev=os.makedev(major, minor), st_uid=0, st_gid=0
        )

    @staticmethod
    def _fake_node_os(monkeypatch: Any, nodes: dict[str, Any]) -> None:
        real_lstat = standin.os.lstat

        def lstat(path: str) -> Any:
            # LAZY branch: a fake node must never touch the host.
            # (dict.get evaluates its default eagerly, which would
            # lstat host paths that do not exist on a CI VM.)
            if path in nodes:
                return nodes[path]
            return real_lstat(path)

        monkeypatch.setattr(standin, "os", SimpleNamespace(lstat=lstat, statvfs=standin.os.statvfs))

    def test_masked_null_file_alias_admitted_and_counted(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        dirs = self._dirs(tmp_path)
        lines = [
            _mountinfo_line("/", "overlay", rw=False),
            _mountinfo_line("/proc", "proc"),
            _mountinfo_line("/dev", "tmpfs"),
            _mountinfo_line("/proc/kcore", src_root="/null"),
            _mountinfo_line(str(dirs[0])),
            _mountinfo_line(str(dirs[1])),
            _mountinfo_line(str(dirs[2])),
            _mountinfo_line(str(tmp_path / "shm")),
        ]
        self._table(tmp_path, lines, monkeypatch)
        self._fake_node_os(monkeypatch, {"/proc/kcore": self._chr_node()})
        mounts, scanned, masked = standin.measure_mounts(self._specs(dirs))
        assert masked == 1
        assert scanned == len(lines)
        assert "/proc/kcore" not in {m["root"] for m in mounts}

    def test_masked_null_thermal_alias_admitted(self, tmp_path: Path, monkeypatch: Any) -> None:
        dirs = self._dirs(tmp_path)
        thermal = "/sys/devices/system/cpu/cpu0/thermal_throttle"
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            _mountinfo_line(thermal, src_root="/null"),
        ]
        self._table(tmp_path, lines, monkeypatch)
        self._fake_node_os(monkeypatch, {thermal: self._chr_node()})
        mounts, scanned, masked = standin.measure_mounts(self._specs(dirs))
        assert masked == 1
        assert thermal not in {m["root"] for m in mounts}

    @pytest.mark.parametrize(
        ("nodes", "why"),
        [
            (
                {
                    "/proc/kcore": SimpleNamespace(
                        st_mode=stat.S_IFCHR | 0o660, st_rdev=os.makedev(1, 5), st_uid=0, st_gid=0
                    )
                },
                "wrong character device (1:5, not null)",
            ),
            (
                {
                    "/proc/kcore": SimpleNamespace(
                        st_mode=stat.S_IFREG | 0o644, st_rdev=0, st_uid=0, st_gid=0
                    )
                },
                "regular file node",
            ),
            (
                {
                    "/proc/kcore": SimpleNamespace(
                        st_mode=stat.S_IFDIR | 0o755, st_rdev=0, st_uid=0, st_gid=0
                    )
                },
                "directory node",
            ),
            (
                {
                    "/proc/kcore": SimpleNamespace(
                        st_mode=stat.S_IFCHR | 0o666, st_rdev=os.makedev(1, 3), st_uid=0, st_gid=0
                    )
                },
                "node exists but path is unreviewed",
            ),
        ],
        ids=["wrong-device", "regular-file", "directory", "unreviewed-path"],
    )
    def test_masked_alias_identity_negatives_fail_closed(
        self, tmp_path: Path, monkeypatch: Any, nodes: Any, why: str
    ) -> None:
        dirs = self._dirs(tmp_path)
        mountpoint = "/proc/kcore"
        if why.startswith("node exists but path"):
            mountpoint = "/proc/kcore-alias"  # unreviewed path: never admitted
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            _mountinfo_line(mountpoint, src_root="/null"),
        ]
        self._table(tmp_path, lines, monkeypatch)
        self._fake_node_os(monkeypatch, nodes)
        with pytest.raises(StandinError, match="unlisted-writable-mount"):
            standin.measure_mounts(self._specs(dirs))

    def test_masked_alias_wrong_source_root_fails_closed(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # A bind of some OTHER device (source-root /zero) over a
        # known-default path with a chr 1:3 node is NOT the reviewed
        # /dev/null mask: the source identity must bind.
        dirs = self._dirs(tmp_path)
        lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
            _mountinfo_line(str(tmp_path / "shm")),
            _mountinfo_line("/proc/kcore", src_root="/zero"),
        ]
        self._table(tmp_path, lines, monkeypatch)
        self._fake_node_os(monkeypatch, {"/proc/kcore": self._chr_node()})
        with pytest.raises(StandinError, match="unlisted-writable-mount"):
            standin.measure_mounts(self._specs(dirs))

    def test_oversized_byte_count_fails_closed(self, tmp_path: Path, monkeypatch: Any) -> None:
        # A table beyond the closed byte cap (few records, long
        # roots) is fail-closed before retention.
        dirs = self._dirs(tmp_path)
        long_root = "/tmp/" + "a" * 900
        lines = (
            [_mountinfo_line(str(d)) for d in dirs[:3]]
            + [
                _mountinfo_line(str(tmp_path / "shm")),
            ]
            + [_mountinfo_line(long_root + str(i)) for i in range(300)]
        )
        self._table(tmp_path, lines, monkeypatch)
        with pytest.raises(StandinError, match="mountinfo-oversized"):
            standin.measure_mounts(self._specs(dirs))

    def test_ramfs_and_hugetlbfs_rw_are_data_not_virtual(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # RAM-backed data filesystems are NOT a virtual class: an
        # unlisted rw ramfs/hugetlbfs is writable data, fail-closed.
        dirs = self._dirs(tmp_path)
        for fstype in ("ramfs", "hugetlbfs"):
            unlisted = tmp_path / f"unlisted-{fstype}"
            unlisted.mkdir()
            lines = [_mountinfo_line(str(d)) for d in dirs[:3]] + [
                _mountinfo_line(str(tmp_path / "shm")),
                _mountinfo_line(str(unlisted), fstype),
            ]
            self._table(tmp_path, lines, monkeypatch)
            with pytest.raises(StandinError, match="unlisted-writable-mount"):
                standin.measure_mounts(self._specs(dirs))


class TestProfileRecord:
    def test_profile_record_validates(self, tmp_path: Any, monkeypatch: Any) -> None:
        monkeypatch.setenv("SLAIF_SUBJ_DIR", str(tmp_path))
        monkeypatch.setenv("SLAIF_FIXTURE_PORT", "18443")
        # local pure test: the subject uid constant is the injection
        # seam for the host uid; CI still measures 21002 for real
        monkeypatch.setattr(model, "SUBJECT_UID", os.getuid())
        # reload module constants bound at import time
        _set_module_attr(standin, "SUBJ_DIR", str(tmp_path))
        _set_module_attr(standin, "SUBJ_CODEX_HOME", f"{tmp_path}/codex-home")
        _set_module_attr(standin, "SUBJ_CREDENTIAL", f"{tmp_path}/credential")
        record = standin.create_synthetic_profile("run-token-017r")
        model.validate_profile_record(record)
        # separate profile file, no [profiles.NAME] table
        base = (tmp_path / "codex-home" / "config.toml").read_text()
        profile = (tmp_path / "codex-home" / "early-beta.config.toml").read_text()
        assert "[profiles" not in base and "[profiles" not in profile
        assert "env_key" in base and "requires_openai_auth" in base
        # credential is a file, never a profile value
        cred = (tmp_path / "credential").read_text()
        assert cred not in base and cred not in profile
        assert record["credential_sha256"] != record["base_config_sha256"]
        assert oct(record["codex_home_mode"]) == "0o700"
        assert oct(record["profile_mode"]) == "0o600"

    def test_synthetic_templates_disable_optional_external_controls(
        self, tmp_path: Any, monkeypatch: Any
    ) -> None:
        # review 24: the required optional plugin-sync/update/
        # telemetry controls of the exact pinned public 0.164.0
        # config schema must be present in the FRESH synthetic
        # templates (pure template assertion; nothing is
        # launched).
        monkeypatch.setenv("SLAIF_SUBJ_DIR", str(tmp_path))
        monkeypatch.setenv("SLAIF_FIXTURE_PORT", "18443")
        monkeypatch.setattr(model, "SUBJECT_UID", os.getuid())
        _set_module_attr(standin, "SUBJ_DIR", str(tmp_path))
        _set_module_attr(standin, "SUBJ_CODEX_HOME", f"{tmp_path}/codex-home")
        _set_module_attr(standin, "SUBJ_CREDENTIAL", f"{tmp_path}/credential")
        standin.create_synthetic_profile("run-token-017r")
        base = tomllib.loads((tmp_path / "codex-home" / "config.toml").read_text())
        assert base["check_for_update_on_startup"] is False
        assert base["analytics"] == {"enabled": False}
        assert base["otel"] == {
            "exporter": "none",
            "trace_exporter": "none",
            "metrics_exporter": "none",
        }
        # features.plugins defaults to TRUE at the pinned commit:
        # the explicit false is what disables plugin
        # synchronization.
        assert base["features"] == {
            "plugins": False,
            "remote_plugin": False,
            "recommended_plugins": False,
            "plugin_hooks": False,
        }
        assert base["history"] == {"persistence": "none"}
        # no legacy profile selector/table in the base: the
        # pinned loader rejects them together with --profile.
        assert "profile" not in base and "profiles" not in base
        profile = tomllib.loads((tmp_path / "codex-home" / "early-beta.config.toml").read_text())
        assert profile == {
            "model": "slaif-synthetic-model",
            "approval_policy": "never",
            "sandbox_mode": "danger-full-access",
        }


class TestHoldMode:
    """The 017-x finite hold: the closed identity record is flushed
    FIRST, the hard finite hold is capped by the 20 s bound and the
    SAME self-deadline backstop, the subject exits 0 naturally, and
    no model POST / child / shell path is ever touched.  Pure fake:
    the process identity is injected, the hold is captured, the
    ACTUAL mode function is exercised."""

    TOKEN = "0123456789abcdef0123456789abcdef"

    @staticmethod
    def _as_subject(monkeypatch: Any) -> None:
        # The reviewed container identity is UID/GID 21002 with the
        # subject's own group: represent BOTH identities.
        monkeypatch.setattr(standin.os, "getuid", lambda: standin.SUBJECT_UID)
        monkeypatch.setattr(standin.os, "getgid", lambda: standin.SUBJECT_UID)
        monkeypatch.setattr(standin.os, "getgroups", lambda: [standin.SUBJECT_UID])

    @staticmethod
    def _as_other_uid(monkeypatch: Any) -> None:
        monkeypatch.setattr(standin.os, "getuid", lambda: standin.SUBJECT_UID + 1)

    @staticmethod
    def _as_foreign_gid(monkeypatch: Any) -> None:
        monkeypatch.setattr(standin.os, "getuid", lambda: standin.SUBJECT_UID)
        monkeypatch.setattr(standin.os, "getgid", lambda: standin.SUBJECT_UID + 1)
        monkeypatch.setattr(
            standin.os,
            "getgroups",
            lambda: [standin.SUBJECT_UID + 1],
        )

    @staticmethod
    def _anchor(monkeypatch: Any, seconds: float) -> None:
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() + seconds))

    @staticmethod
    def _token(monkeypatch: Any, value: str | None = None) -> None:
        if value is None:
            monkeypatch.setenv("SLAIF_HOLD_TOKEN", TestHoldMode.TOKEN)
        else:
            monkeypatch.setenv("SLAIF_HOLD_TOKEN", value)

    @staticmethod
    def _capture_sleep(monkeypatch: Any) -> dict[str, float]:
        requested: dict[str, float] = {}

        def _sleep(seconds: float) -> None:
            requested["seconds"] = seconds

        monkeypatch.setattr(standin.time, "sleep", _sleep)
        return requested

    def test_closed_identity_record_flushed_before_finite_hold(
        self, monkeypatch: Any, capsys: Any
    ) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        out = capsys.readouterr().out
        assert rc == 0
        record = json.loads(out.strip())
        assert set(record) == {
            "record",
            "status",
            "mode",
            "uid",
            "gid",
            "groups",
            "pid",
            "starttime",
            "token",
            "record_flushed_before_hold",
        }
        assert record["record"] == "slaif-fixture-standin-v1"
        assert record["status"] == "pass"
        assert record["mode"] == "hold"
        assert record["uid"] == standin.SUBJECT_UID
        assert record["gid"] == standin.SUBJECT_UID
        assert record["groups"] == [standin.SUBJECT_UID]
        assert record["pid"] == os.getpid()
        assert record["starttime"] == standin._proc_starttime(os.getpid())
        assert record["token"] == self.TOKEN
        assert record["record_flushed_before_hold"] is True
        # The 20 s hard bound caps the hold (the 120 s deadline is
        # NOT the cap).
        assert requested["seconds"] == standin.HOLD_MAX_SECONDS

    def test_record_flushed_before_hold_starts(self, monkeypatch: Any, capsys: Any) -> None:
        order: list[str] = []
        real_emit = standin.emit

        def _emit(record: dict[str, object]) -> None:
            order.append("emit")
            real_emit(record)

        requested = self._capture_sleep(monkeypatch)

        def _sleep(seconds: float) -> None:
            order.append("sleep")
            requested["seconds"] = seconds

        monkeypatch.setattr(standin, "emit", _emit)
        monkeypatch.setattr(standin.time, "sleep", _sleep)
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        assert standin.hold_mode() == 0
        assert order.index("emit") < order.index("sleep")

    def test_hold_capped_by_remaining_deadline(self, monkeypatch: Any, capsys: Any) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() + 5.0))
        requested = self._capture_sleep(monkeypatch)
        assert standin.hold_mode() == 0
        seconds = requested["seconds"]
        assert 0.0 < seconds <= 5.0

    def test_expired_anchor_fails_closed(self, monkeypatch: Any, capsys: Any) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() - 1.0))
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "self-deadline-expired",
        }
        assert "seconds" not in requested

    def test_invalid_anchor_fails_closed(self, monkeypatch: Any, capsys: Any) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", "not-a-number")
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record["status"] == "fail"
        assert record["reason"] == "self-deadline-invalid"
        assert "seconds" not in requested

    @pytest.mark.parametrize(
        "token",
        [
            "",  # missing
            "a" * 31,  # too short
            "a" * 33,  # too long
            "A" * 32,  # uppercase
            "g" * 32,  # non-hex
            "a" * 16 + " " + "a" * 15,  # embedded space
        ],
    )
    def test_token_closed_refusal(self, token: str, monkeypatch: Any, capsys: Any) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch, token)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record["status"] == "fail"
        assert record["reason"] == "hold-token-invalid"
        assert "seconds" not in requested

    def test_identity_refusal_before_any_hold(self, monkeypatch: Any, capsys: Any) -> None:
        self._as_other_uid(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "identity-not-subject",
        }
        assert "seconds" not in requested

    def test_foreign_gid_refused_before_any_hold(self, monkeypatch: Any, capsys: Any) -> None:
        # UID 21002 with a FOREIGN gid is not the subject identity:
        # both uid and gid must be the subject identity.
        self._as_foreign_gid(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "identity-not-subject",
        }
        assert "seconds" not in requested

    def test_missing_absolute_anchor_refused_no_fallback(
        self, monkeypatch: Any, capsys: Any
    ) -> None:
        # Neither absolute anchor nor relative deadline present: the
        # hold must refuse — the legacy relative fallback would mint
        # a fresh phase deadline, which this mode never does.
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        monkeypatch.delenv("SLAIF_FIXTURE_DEADLINE_ABS", raising=False)
        monkeypatch.delenv("SLAIF_FIXTURE_DEADLINE", raising=False)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "self-anchor-missing",
        }
        assert "seconds" not in requested

    def test_control_character_token_closed_refusal(self, monkeypatch: Any, capsys: Any) -> None:
        # A control character in the token is rejected by the closed
        # env law before the hex check: the refusal is a closed
        # non-echoing record (the generic closed bucket per the
        # closed_reason mapping), never an uncaught exception.
        self._as_subject(monkeypatch)
        self._token(monkeypatch, "a" * 31 + "\n")
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.hold_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record["status"] == "fail"
        assert record["reason"] == "standin-failure"
        assert "seconds" not in requested

    def test_no_model_post_no_child_no_shell(self, monkeypatch: Any, capsys: Any) -> None:
        import subprocess as _sp

        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        provider_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

        def _no_post(*args: object, **kwargs: object) -> object:
            provider_calls.append((args, kwargs))
            raise AssertionError("hold must never touch the provider wire")

        def _no_child(*args: object, **kwargs: object) -> object:
            raise AssertionError("hold must never spawn a child or shell")

        monkeypatch.setattr(standin, "_provider_post", _no_post)
        monkeypatch.setattr(_sp, "Popen", _no_child)
        monkeypatch.setattr(_sp, "run", _no_child)
        monkeypatch.setattr(standin.os, "system", _no_child)
        rc = standin.hold_mode()
        assert rc == 0
        assert provider_calls == []
        assert "seconds" in requested

    def test_main_dispatch_reaches_hold_not_mode_invalid(
        self, monkeypatch: Any, capsys: Any
    ) -> None:
        assert "hold" in standin.MODES
        # The injected uid is NOT 21002: the dispatch must reach the
        # mode (identity refusal), not the closed mode-invalid.
        self._as_other_uid(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        rc = standin.main(["standin", "--mode", "hold"])
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record["reason"] == "identity-not-subject"

    def test_main_dispatch_holds_and_exits_zero(self, monkeypatch: Any, capsys: Any) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.main(["standin", "--mode", "hold"])
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 0
        assert record["mode"] == "hold"
        assert record["status"] == "pass"
        assert requested["seconds"] == standin.HOLD_MAX_SECONDS

    def test_argv_bound_token_holds_and_records_token(self, monkeypatch: Any, capsys: Any) -> None:
        # The detached capability start form: the issued marker is
        # bound on argv (the kernel-cmdline correlation identity);
        # no env token is set at all.
        argv_token = "f" * 32
        self._as_subject(monkeypatch)
        self._token(monkeypatch, "")  # env deliberately empty
        monkeypatch.setenv("SLAIF_HOLD_TOKEN", "")
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.main(["standin", "--mode", "hold", "--hold-token", argv_token])
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 0
        assert record["status"] == "pass"
        assert record["token"] == argv_token
        assert requested["seconds"] == standin.HOLD_MAX_SECONDS

    @pytest.mark.parametrize(
        "argv",
        [
            # the extension is hold-ONLY: no other mode may carry it
            ["standin", "--mode", "hang", "--hold-token", "a" * 32],
            # no argument form beyond the one closed extension
            ["standin", "--mode", "hold", "--token", "a" * 32],
            ["standin", "--mode", "hold", "--hold-token"],
            ["standin", "--mode", "hold", "--hold-token", "a" * 32, "x"],
            ["standin", "--mode", "observe", "--hold-token", "a" * 32, "y"],
            # a 4-element form is never admitted
            ["standin", "--mode", "hold", "--hold-token"],
        ],
    )
    def test_argv_form_closed_refusals(
        self, argv: list[str], monkeypatch: Any, capsys: Any
    ) -> None:
        self._as_subject(monkeypatch)
        self._token(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.main(argv)
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record["status"] == "fail"
        assert record["reason"] == "mode-invalid"
        assert "seconds" not in requested

    def test_argv_token_closed_refusal(self, monkeypatch: Any, capsys: Any) -> None:
        # A malformed argv marker is a closed refusal, never held.
        self._as_subject(monkeypatch)
        self._anchor(monkeypatch, 120.0)
        requested = self._capture_sleep(monkeypatch)
        rc = standin.main(["standin", "--mode", "hold", "--hold-token", "A" * 32])
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "hold-token-invalid",
        }
        assert "seconds" not in requested


# ============================================================================
# 017-ai: the closed observe transport scenario grammar (pure standin layer)
# ============================================================================


class TestObserveMode:
    """The closed NON-CONSUMING observe transport's scenario
    grammar on the ACTUAL ``observe_mode`` with a bounded fake
    provider and the injected subject identity (no provider,
    no docker, no host read, no model POST — this pure
    standin-transport layer proves ONLY the carried-key
    grammar; the host's OWN-entry revalidation is proven in
    the ci suite, and the public owner composition in the
    handoff suite).  The owner-carried EXISTING container
    scenario key is transport data only: the unset default
    AND the explicitly carried historical values (the
    historical owners set the key explicitly at prepare
    time) keep the historical two-scenario set byte-for-byte,
    the canonical AJ transport selects its OWN closed
    format-capture expectation and nothing else, and any
    other carried value is a closed refusal BEFORE the
    /state read."""

    STATE = {
        "record": "slaif-fixture-state-v1",
        "scenario": "diagnostic",
        "wire_requests": 0,
        "diagnostic": "unobserved",
    }

    @staticmethod
    def _as_subject(monkeypatch: Any) -> None:
        monkeypatch.setattr(standin.os, "getuid", lambda: standin.SUBJECT_UID)
        monkeypatch.setattr(standin.os, "getgid", lambda: standin.SUBJECT_UID)
        monkeypatch.setattr(standin.os, "getgroups", lambda: [standin.SUBJECT_UID])
        # The identity-expectation READ seam is injected with the
        # faithful explicit default (None = the original-mode
        # absent image file): the ACTUAL subject-identity
        # validator stays live, but this pure transport fixture
        # never premises on the real host's /opt/slaif-fixture
        # state (no real-host read in this layer).
        monkeypatch.setattr(standin, "_image_identity_profile_raw", lambda: None)

    @staticmethod
    def _anchor(monkeypatch: Any) -> None:
        monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() + 120.0))

    def _run(
        self, monkeypatch: Any, capsys: Any, scenario: str | None, state: dict[str, object]
    ) -> tuple[int, dict[str, object]]:
        self._as_subject(monkeypatch)
        self._anchor(monkeypatch)
        if scenario is None:
            monkeypatch.delenv("SLAIF_FIXTURE_SCENARIO", raising=False)
        else:
            monkeypatch.setenv("SLAIF_FIXTURE_SCENARIO", scenario)
        monkeypatch.setattr(
            standin,
            "_provider_get",
            lambda path, deadline: (200, "application/json", json.dumps(state).encode("ascii")),
        )
        rc = standin.observe_mode()
        record = json.loads(capsys.readouterr().out.strip())
        return rc, record

    @pytest.mark.parametrize("carried", [None, "diagnostic", "tool-cycle"])
    def test_unset_and_carried_historical_keep_closed_set(
        self, carried: str | None, monkeypatch: Any, capsys: Any
    ) -> None:
        # the unset default AND the explicit historical
        # transport values accept the historical two-scenario
        # set (diagnostic shown; tool-cycle below)
        rc, record = self._run(monkeypatch, capsys, carried, dict(self.STATE))
        assert rc == 0
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "pass",
            "mode": "observe",
            "uid": standin.SUBJECT_UID,
            "scenario": "diagnostic",
            "wire_requests": 0,
            "diagnostic_state": "unobserved",
            "raw_content_retained": False,
        }

    @pytest.mark.parametrize("carried", [None, "diagnostic", "tool-cycle"])
    def test_historical_set_accepts_tool_cycle_report(
        self, carried: str | None, monkeypatch: Any, capsys: Any
    ) -> None:
        state = dict(self.STATE, scenario="tool-cycle", diagnostic="observed")
        rc, record = self._run(monkeypatch, capsys, carried, state)
        assert rc == 0
        assert record["scenario"] == "tool-cycle"
        assert record["diagnostic_state"] == "observed"

    @pytest.mark.parametrize("carried", [None, "diagnostic", "tool-cycle"])
    def test_historical_grammar_refuses_format_report(
        self, carried: str | None, monkeypatch: Any, capsys: Any
    ) -> None:
        state = dict(self.STATE, scenario="format-capture")
        rc, record = self._run(monkeypatch, capsys, carried, state)
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "observe-shape",
        }

    def test_aj_transport_accepts_only_format_report(self, monkeypatch: Any, capsys: Any) -> None:
        state = dict(self.STATE, scenario="format-capture")
        rc, record = self._run(monkeypatch, capsys, "format-capture", state)
        assert rc == 0
        assert record["scenario"] == "format-capture"
        assert record["raw_content_retained"] is False

    @pytest.mark.parametrize("scenario", ["diagnostic", "tool-cycle"])
    def test_aj_transport_refuses_legacy_reports(
        self, scenario: str, monkeypatch: Any, capsys: Any
    ) -> None:
        state = dict(self.STATE, scenario=scenario)
        rc, record = self._run(monkeypatch, capsys, "format-capture", state)
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "observe-shape",
        }

    @pytest.mark.parametrize(
        "carried",
        ["tool-cycle ", "diagnostic-x", "FORMAT-CAPTURE", "format-capture-extra"],
    )
    def test_foreign_carried_value_refused_before_state_read(
        self, carried: str, monkeypatch: Any, capsys: Any
    ) -> None:
        self._as_subject(monkeypatch)
        self._anchor(monkeypatch)
        monkeypatch.setenv("SLAIF_FIXTURE_SCENARIO", carried)

        def _boom(path: str, deadline: float) -> None:
            raise AssertionError("the /state read must never happen")

        monkeypatch.setattr(standin, "_provider_get", _boom)
        rc = standin.observe_mode()
        record = json.loads(capsys.readouterr().out.strip())
        assert rc == 2
        assert record == {
            "record": "slaif-fixture-standin-v1",
            "status": "fail",
            "reason": "observe-transport",
        }
