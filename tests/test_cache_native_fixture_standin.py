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
import sys
from pathlib import Path
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


def _mountinfo_line(root: str, fstype: str = "tmpfs", rw: bool = True, major: str = "0:45") -> str:
    opts = "rw,nosuid,nodev" if fstype == "tmpfs" and rw else "rw,nosuid" if rw else "ro,nosuid"
    return f"42 41 {major} / {root} {opts} - {fstype} none rw,seclabel"


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
        mounts, scanned = standin.measure_mounts(self._specs(dirs))
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
