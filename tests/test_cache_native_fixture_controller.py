"""Pure/loopback tests for the fixture controller (017-r).

These tests exercise the ACTUAL receiver/response wire path over real
loopback sockets with bounded synthetic scenarios (admission gating,
exact HTTP grammar, causal-position issuance, forged/replayed/out-of-
order refusals, unknown offered tools, SSE envelope shape, peer
trust ABI, ordered quiesce/export states, corruption and deadline
paths).  No controller main against the fixed /run fixture paths, no
real keyring/namespace/Docker: the actual complete fixture runs only
in the disposable hosted CI job.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import socket
import struct
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_model.py"
CTRL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_controller.py"

model_spec = importlib.util.spec_from_file_location("cache_native_fixture_model", MODEL_PATH)
assert model_spec is not None and model_spec.loader is not None
model = importlib.util.module_from_spec(model_spec)
sys.modules["cache_native_fixture_model"] = model
model_spec.loader.exec_module(model)

ctrl_spec = importlib.util.spec_from_file_location("cache_native_fixture_controller", CTRL_PATH)
assert ctrl_spec is not None and ctrl_spec.loader is not None
ctrl = importlib.util.module_from_spec(ctrl_spec)
sys.modules["cache_native_fixture_controller"] = ctrl
ctrl_spec.loader.exec_module(ctrl)


class _Clock:
    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def make_provider(
    budgets: Any = None,
    clock: _Clock | None = None,
    scenario: str = "tool-cycle",
    originals_dir: str | None = None,
    exporter_uid: int | None = None,
) -> Any:
    budgets = budgets or model.FixtureBudgets()
    clock = clock or _Clock()
    ledger = model.FixtureLedger(budgets=budgets, clock=clock)
    ledger.set_deadline(min(30, ledger.budgets.lifetime_seconds))
    lock = threading.Lock()
    registry = model.IssuedRegistry(ledger.budgets.max_requests)
    provider = ctrl.Provider(
        0,
        ledger,
        registry,
        lock,
        scenario=scenario,
        originals_dir=originals_dir or f"/tmp/slaif-fixture-originals-{os.getpid()}",
        exporter_uid=exporter_uid,
    )
    thread = threading.Thread(target=provider.serve, daemon=True)
    provider.accept_thread = thread
    thread.start()
    return ledger, lock, registry, provider, thread, clock


def http_exchange(
    host: str, port: int, raw: bytes, timeout: float = 2.0
) -> tuple[int | None, bytes, str]:
    """Send raw bytes, return (status, body, content-type) or
    (None, b"", "closed"|"reset") when the server closes the
    connection (clean EOF) or RSTs it (unread-data close) without a
    reply — both are the legitimate no-fake-completion proofs; a
    timeout is a real failure and propagates."""

    def _recv_all(sock: socket.socket) -> tuple[str, list[str], bytes] | str | None:
        data = b""
        try:
            while b"\r\n\r\n" not in data:
                chunk = sock.recv(65536)
                if not chunk:
                    return None
                data += chunk
            header, _, rest = data.partition(b"\r\n\r\n")
            lines = header.decode("ascii", "replace").split("\r\n")
            length = 0
            for line in lines[1:]:
                if line.lower().startswith("content-length:"):
                    length = int(line.split(":", 1)[1].strip())
            body = rest
            while len(body) < length:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                body += chunk
            return (lines[0], lines, body)
        except ConnectionResetError:
            return "reset"

    sock = socket.create_connection((host, port), timeout=timeout)
    try:
        sock.sendall(raw)
        got = _recv_all(sock)
        if got is None:
            return None, b"", "closed"
        if got == "reset":
            return None, b"", "reset"
        if not isinstance(got, tuple):
            return None, b"", "closed"
        status_line, lines, body = got
        ctype = ""
        for line in lines[1:]:
            if line.lower().startswith("content-type:"):
                ctype = line.split(":", 1)[1].strip()
        code = int(status_line.split(" ")[1]) if " " in status_line else 0
        return code, body, ctype
    finally:
        sock.close()


def post_json(
    port: int, payload: dict[str, Any], raw: bytes | None = None
) -> tuple[int | None, bytes, str]:
    body = raw if raw is not None else json.dumps(payload).encode()
    raw_request = (
        b"POST /v1/responses HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(body)}\r\n".encode()
        + b"\r\n"
        + body
    )
    return http_exchange("127.0.0.1", port, raw_request)


SYNTHETIC_TOOLS = [
    {
        "type": "function",
        "name": "exec_command",
        "description": "synthetic exec stand-in",
        "parameters": {
            "type": "object",
            "required": ["cmd"],
            "properties": {"cmd": {"type": "string"}},
        },
    },
    {
        "type": "function",
        "name": "write_stdin",
        "description": "synthetic stdin stand-in",
        "parameters": {
            "type": "object",
            "required": ["session_id"],
            "properties": {"session_id": {"type": "integer"}, "chars": {"type": "string"}},
        },
    },
]


def base_request(
    tools: list[dict[str, Any]] | None = None, extra_input: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    input_items = [{"role": "user", "content": "slaif synthetic"}]
    if extra_input:
        input_items.extend(extra_input)
    return {
        "model": "slaif-synthetic-model",
        "instructions": "slaif synthetic fixture flow",
        "input": input_items,
        "tools": tools if tools is not None else SYNTHETIC_TOOLS,
    }


def parse_sse(body: bytes) -> list[dict[str, Any]]:
    events = []
    for block in body.decode("utf-8").split("\n\n"):
        event_type, data = None, None
        for line in block.split("\n"):
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data = line[5:].strip()
        if event_type is not None:
            assert data is not None
            events.append({"event": event_type, "data": json.loads(data)})
    return events


# -- peer trust ABI ----------------------------------------------------------------
class TestPeerTrust:
    def make_cred(self, pid: int = 42, uid: int = 21001, gid: int = 21001) -> bytes:
        return struct.pack("iii", pid, uid, gid)

    def test_trusted_21001(self) -> None:
        assert ctrl.peer_trusted(self.make_cred(), 21001) is True

    def test_denied_21002(self) -> None:
        assert ctrl.peer_trusted(self.make_cred(uid=21002, gid=21002), 21001) is False

    def test_denied_pid_zero(self) -> None:
        assert ctrl.peer_trusted(self.make_cred(pid=0), 21001) is False

    def test_malformed_length_rejected(self) -> None:
        assert ctrl.peer_trusted(b"\x00" * 16, 21001) is False
        assert ctrl.peer_trusted(b"\x00" * 8, 21001) is False
        assert ctrl.peer_trusted(b"", 21001) is False

    def test_negative_uid_rejected(self) -> None:
        assert ctrl.peer_trusted(self.make_cred(uid=-1), 21001) is False


# -- exact HTTP grammar ---------------------------------------------------------------
class TestHttpGrammar:
    def test_health_exact_bytes(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, body, ctype = http_exchange(
                "127.0.0.1", provider.port, b"GET /healthz HTTP/1.1\r\nHost: x\r\n\r\n"
            )
            assert code == 200 and body == ctrl.HEALTH_BODY
            assert ctype == "application/json"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_bad_method_closes_without_reply(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, _, how = http_exchange(
                "127.0.0.1", provider.port, b"PUT /v1/responses HTTP/1.1\r\nHost: x\r\n\r\n"
            )
            assert code is None and how == "closed"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_transfer_encoding_rejected(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, _, how = http_exchange(
                "127.0.0.1",
                provider.port,
                b"POST /v1/responses HTTP/1.1\r\n"
                b"Transfer-Encoding: chunked\r\nContent-Length: 2\r\n\r\n{}",
            )
            assert code is None and how == "closed"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_conflicting_duplicate_length_rejected(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, _, how = http_exchange(
                "127.0.0.1",
                provider.port,
                b"POST /v1/responses HTTP/1.1\r\nContent-Length: 2\r\nContent-Length: 3\r\n\r\nabc",
            )
            assert code is None and how == "closed"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_truncated_body_closes_without_fake_completion(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, _, how = http_exchange(
                "127.0.0.1",
                provider.port,
                b"POST /v1/responses HTTP/1.1\r\nContent-Length: 100\r\n\r\nshort",
                timeout=6.0,
            )
            # No HTTP reply of any kind: clean EOF or RST both prove
            # the truncation was refused without fake completion.
            assert code is None and how in ("closed", "reset")
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_coalesced_32kib_body_accepted(self) -> None:
        provider, thread, _ = self._up()
        try:
            # A valid 32KiB body arriving TOGETHER with its small
            # header must not be mistaken for an overbound header.
            padding = [{"role": "user", "content": "slaif coalesced filler " * 800}] * 2
            payload = {
                "model": "slaif-synthetic-model",
                "instructions": "slaif synthetic fixture flow",
                "input": padding,
                "tools": SYNTHETIC_TOOLS,
            }
            body = json.dumps(payload).encode()
            assert len(body) >= 32 * 1024
            code, body_out, ctype = http_exchange(
                "127.0.0.1",
                provider.port,
                b"POST /v1/responses HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Type: application/json\r\n"
                + f"Content-Length: {len(body)}\r\n".encode()
                + b"\r\n"
                + body,
            )
            assert code == 200 and ctype == "text/event-stream"
            events = parse_sse(body_out)
            assert events[-1]["event"] == "response.completed"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_overbound_header_still_refused(self) -> None:
        provider, thread, _ = self._up()
        try:
            long_header = b"X-Pad: " + b"a" * (16 * 1024) + b"\r\n"
            code, _, how = http_exchange(
                "127.0.0.1",
                provider.port,
                b"GET /healthz HTTP/1.1\r\nHost: x\r\n" + long_header + b"\r\n",
            )
            assert code is None and how in ("closed", "reset")
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_unknown_route_fixed_error(self) -> None:
        provider, thread, _ = self._up()
        try:
            code, body, _ = http_exchange(
                "127.0.0.1", provider.port, b"GET /v1/other HTTP/1.1\r\nHost: x\r\n\r\n"
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "route"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def _up(self) -> Any:
        ledger, lock, registry, provider, thread, _clock = make_provider(scenario="diagnostic")
        return provider, thread, lock


# -- causal issuance law (real wire) ---------------------------------------------------
class TestCausalIssuance:
    def _up(self) -> Any:
        return make_provider()

    def test_issue_at_controller_position_and_validate(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            unknown_tool = {"type": "synthetic_unknown_type", "name": "x"}
            code, body, ctype = post_json(
                provider.port, base_request(SYNTHETIC_TOOLS + [unknown_tool])
            )
            assert code == 200 and ctype == "text/event-stream"
            events = parse_sse(body)
            types = [e["event"] for e in events]
            assert types == [
                "response.created",
                "response.output_item.added",
                "response.output_item.done",
                "response.output_item.added",
                "response.output_item.done",
                "response.completed",
            ]
            # The DISTINCT added/done paths carry the same completed
            # item at the exact output indexes.
            pairs = [
                (e["data"]["output_index"], e["data"]["item"])
                for e in events
                if e["event"].startswith("response.output_item.")
            ]
            assert [p[0] for p in pairs] == [0, 0, 1, 1]
            assert pairs[0][1] == pairs[1][1]
            assert pairs[2][1] == pairs[3][1]
            items = [p[1] for p in pairs[1::2]]
            assert all(i["type"] == "function_call" for i in items)
            assert sorted(i["name"] for i in items) == ["exec_command", "write_stdin"]
            # unknown offered mode: NOT issued, NOT aliased
            assert registry.count() == 2
            assert provider.diagnostic is not None
            kinds = [u["kind"] for u in provider.diagnostic["unknown_modes"]]
            assert "unknown-tool-type" in kinds
            # use step: reference the issued ids
            refs = [
                {"type": "function_call_output", "call_id": i["call_id"], "output": "synthetic"}
                for i in items
            ]
            code, body, _ = post_json(provider.port, base_request(extra_input=refs))
            assert code == 200
            events = parse_sse(body)
            item = [e["data"]["item"] for e in events if e["event"] == "response.output_item.done"][
                0
            ]
            assert item["type"] == "message"
            assert item["role"] == "assistant"
            texts = [c["text"] for c in item["content"] if c["type"] == "output_text"]
            assert texts == [ctrl.FIXED_FINAL_TEXT]
            # the completed envelope carries the same terminal item
            completed = events[-1]["data"]["response"]
            assert completed["status"] == "completed"
            assert completed["output"] == [item]
            # third request: bounded scenario
            code, body, _ = post_json(provider.port, base_request(extra_input=refs))
            assert code == 400
            assert json.loads(body)["error"]["code"] == "scenario-bounded"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_forged_reference_refused_unissued(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            code, body, _ = post_json(
                provider.port,
                base_request(
                    extra_input=[
                        {
                            "type": "function_call_output",
                            "call_id": "slaif-never-issued",
                            "output": "synthetic",
                        }
                    ]
                ),
            )
            assert code == 400
            error = json.loads(body)["error"]
            assert error["code"] == "slaif_fixture_unissued"
            # the refusal did not advance the scenario: a complete
            # valid result set is still accepted after it
            issued = {e["call_id"] for e in registry.entries()}
            refs = [
                {"type": "function_call_output", "call_id": c, "output": "synthetic"}
                for c in sorted(issued)
            ]
            code, body, _ = post_json(provider.port, base_request(extra_input=refs))
            assert code == 200
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_preloaded_results_refused_before_issuance(self) -> None:
        # A forged use-phase payload on the first request is REFUSED,
        # not ignored-while-issuing: no issuance, no state advance;
        # the next clean request still issues from the tools region.
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(
                provider.port,
                base_request(
                    extra_input=[
                        {
                            "type": "function_call_output",
                            "call_id": "slaif-forged",
                            "output": "synthetic",
                        }
                    ]
                ),
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "preloaded-result"
            assert registry.count() == 0
            assert provider.scenario_state == "awaiting-issue"
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            events = parse_sse(body)
            items = [e["data"]["item"] for e in events if e["event"] == "response.output_item.done"]
            assert all(i["type"] == "function_call" for i in items)
            assert registry.count() == 2
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_replayed_issue_cannot_reissue(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            first = registry.count()
            # request two without results is refused, not a reissue
            code, body, _ = post_json(provider.port, base_request())
            assert code == 400
            assert json.loads(body)["error"]["code"] == "missing-calls"
            assert registry.count() == first
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_no_known_tools_refused(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(
                provider.port, base_request([{"type": "synthetic_unknown_type"}])
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "no-issuable-tools"
            assert registry.count() == 0
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_malformed_body_fixed_error(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, {}, raw=b"not json")
            assert code == 400
            assert json.loads(body)["error"]["code"] == "malformed-request"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_partial_result_set_refused(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            issued = sorted(e["call_id"] for e in registry.entries())
            assert len(issued) == 2
            # only ONE of the two issued calls referenced: partial
            code, body, _ = post_json(
                provider.port,
                base_request(
                    extra_input=[
                        {
                            "type": "function_call_output",
                            "call_id": issued[0],
                            "output": "synthetic",
                        }
                    ]
                ),
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "slaif_fixture_partial"
            assert provider.scenario_state == "awaiting-results"
            # duplicate reference: partial, not progress
            code, body, _ = post_json(
                provider.port,
                base_request(
                    extra_input=[
                        {"type": "function_call_output", "call_id": c, "output": "synthetic"}
                        for c in (issued[0], issued[0])
                    ]
                ),
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "slaif_fixture_partial"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_result_must_come_after_issuance_position(self) -> None:
        # Five junk requests consume positions 0-4 (budgets advance,
        # semantic state never does); issuance lands at position 5.
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            for _ in range(5):
                code, _body, _ = post_json(provider.port, {}, raw=b"not json")
                assert code == 400
            code, _body, _ = post_json(provider.port, base_request())
            assert code == 200
            issued = {e["call_id"]: e["request_position"] for e in registry.entries()}
            assert all(p == 5 for p in issued.values())
            refs = [
                {"type": "function_call_output", "call_id": c, "output": "synthetic"}
                for c in sorted(issued)
            ]
            result_body = json.dumps(base_request(extra_input=refs)).encode()
            # Deterministic order negatives through the actual seam:
            # same position as issuance and EARLIER positions are
            # refused even with the exact matching ids.
            for pos in (5, 4, 3):
                status, _ctype, body = provider._route(
                    "POST", ctrl.ROUTE_RESPONSES, result_body, pos
                )
                assert status == "400 Bad Request"
                assert json.loads(body)["error"]["code"] == "causal-order"
                assert provider.scenario_state == "awaiting-results"
            # invalid positions are refused as closed, not guessed
            payload = json.loads(result_body)
            for bad in (True, -1):
                status, _ctype, body = provider._validate_step(payload, bad)
                assert status == "400 Bad Request"
                assert json.loads(body)["error"]["code"] == "causal-position"
            status, _ctype, body = provider._route("POST", ctrl.ROUTE_RESPONSES, result_body, None)
            assert status == "400 Bad Request"
            assert json.loads(body)["error"]["code"] == "route"
            # the real later request (position 6) is the valid control
            code, body, _ = post_json(provider.port, base_request(extra_input=refs))
            assert code == 200
            assert provider.scenario_state == "done"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_concurrent_first_requests_issue_exactly_once(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            results = []

            def _post() -> int | None:
                code, _body, _ctype = post_json(provider.port, base_request())
                return code

            threads = [threading.Thread(target=lambda: results.append(_post())) for _ in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=5)
            codes = [code for code in results if code is not None]
            assert len(codes) == 2
            assert sorted(codes) == [200, 400]
            # exactly one issuance at exactly one causal position
            assert registry.count() == 2
            positions = {e["request_position"] for e in registry.entries()}
            assert len(positions) == 1
            assert provider.scenario_state == "awaiting-results"
        finally:
            provider.closed = True
            thread.join(timeout=2)


class TestDiagnosticScenario:
    def _up(self) -> Any:
        return make_provider(scenario="diagnostic")

    def test_first_request_fixed_text_no_tools(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            unknown_tool = {"type": "synthetic_unknown_type", "name": "x"}
            code, body, ctype = post_json(
                provider.port, base_request(SYNTHETIC_TOOLS + [unknown_tool])
            )
            assert code == 200 and ctype == "text/event-stream"
            events = parse_sse(body)
            types = [e["event"] for e in events]
            assert types == [
                "response.created",
                "response.output_item.added",
                "response.output_item.done",
                "response.completed",
            ]
            item = [e["data"]["item"] for e in events if e["event"] == "response.output_item.done"][
                0
            ]
            assert item["type"] == "message"
            assert item["role"] == "assistant"
            texts = [c["text"] for c in item["content"] if c["type"] == "output_text"]
            assert texts == [ctrl.FIXED_FINAL_TEXT]
            # NO issuance, even though known tools were offered
            assert registry.count() == 0
            # the ACTUAL offered tools region was observed, unknown
            # mode kept typed unsupported
            assert provider.diagnostic is not None
            kinds = [u["kind"] for u in provider.diagnostic["unknown_modes"]]
            assert "unknown-tool-type" in kinds
            assert provider.observed_at_position == 0
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_second_request_bounded(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, _body, _ = post_json(provider.port, base_request())
            assert code == 200
            code, body, _ = post_json(provider.port, base_request())
            assert code == 400
            assert json.loads(body)["error"]["code"] == "scenario-bounded"
        finally:
            provider.closed = True
            thread.join(timeout=2)

    def test_preloaded_refused_then_diagnostic_still_safe(self) -> None:
        ledger, lock, registry, provider, thread, _ = self._up()
        try:
            code, body, _ = post_json(
                provider.port,
                base_request(
                    extra_input=[
                        {
                            "type": "function_call_output",
                            "call_id": "slaif-forged",
                            "output": "synthetic",
                        }
                    ]
                ),
            )
            assert code == 400
            assert json.loads(body)["error"]["code"] == "preloaded-result"
            assert registry.count() == 0
            assert provider.scenario_state == "awaiting-issue"
            code, _body, _ = post_json(provider.port, base_request())
            assert code == 200
            assert registry.count() == 0
        finally:
            provider.closed = True
            thread.join(timeout=2)


# -- admission gating -------------------------------------------------------------------
class TestAdmissionGating:
    def test_thread_cap_refuses_admission_before_spawn(self) -> None:
        budgets = model.FixtureBudgets(max_threads=1, max_connections=8)
        ledger, lock, registry, provider, thread, _ = make_provider(budgets)
        try:
            # two silent connections: the first reserves the only
            # handler thread, the second must be refused.
            s1 = socket.create_connection(("127.0.0.1", provider.port), 2)
            s2 = socket.create_connection(("127.0.0.1", provider.port), 2)
            time.sleep(0.5)
            # the second connection is closed by the server (refused);
            # a clean EOF or a RST are BOTH legitimate refusal proofs
            # (a timeout would be a real failure)
            s2.settimeout(2)
            try:
                data = s2.recv(1)
            except ConnectionResetError:
                data = b""
            assert data == b""
            with lock:
                live = [t for t in provider.handlers if t is not None and t.is_alive()]
            assert len(live) == 1
            s1.close()
        finally:
            provider.closed = True
            thread.join(timeout=2)


# -- ordered quiesce / export states ------------------------------------------------------
class TestExporterStates:
    """Real-socket exporter tests: the peer check runs the ACTUAL
    SO_PEERCRED path with the expected uid injected as the local test
    uid (the production default stays CONTROLLER_UID), so every
    refusal/success below travels the real wire.  Originals are
    seeded in an OWNED tmpdir via the explicit seam, never the
    controller's fixed /run paths on the protected host."""

    def _up(self, mode: str = "main", scenario: str = "tool-cycle") -> Any:
        unique = f"{os.getpid()}-{threading.get_ident()}"
        originals = f"/tmp/slaif-fixture-originals-{unique}"
        ledger, lock, registry, provider, thread, _ = make_provider(
            scenario=scenario, originals_dir=originals, exporter_uid=model.CONTROLLER_UID
        )
        provider.seed_originals()
        exporter = ctrl.Exporter(
            provider,
            ledger,
            lock,
            mode,
            socket_path=(f"/tmp/slaif-fixture-exporter-{unique}.sock"),
            trusted_uid=os.getuid(),
        )
        xthread = threading.Thread(target=exporter.serve_forever, daemon=True)
        xthread.start()
        return provider, thread, exporter, xthread, lock

    def _teardown(self, provider: Any, thread: Any, exporter: Any, xthread: Any) -> None:
        exporter.server.close()
        xthread.join(timeout=3)
        provider.closed = True
        thread.join(timeout=3)

    def _cmd(self, exporter: Any, command: str) -> bytes:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        # AF_UNIX getsockname() already returns the str path
        sock.connect(exporter.server.getsockname())
        try:
            sock.sendall(command.encode() + b"\n")
            data = b""
            if command == "quiesce":
                while b"\n" not in data:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                return data
            # export: closed framing — 4B BE length + payload +
            # 64-hex digest, or a plain closed error line when the
            # export is refused (not quiesced / repeated).
            header = b""
            while len(header) < 4:
                chunk = sock.recv(4 - len(header))
                if not chunk:
                    raise OSError("truncated")
                header += chunk
            if header.startswith(b"err"):
                line = header
                while b"\n" not in line:
                    chunk = sock.recv(4096)
                    if not chunk:
                        raise OSError("truncated")
                    line += chunk
                return line
            (length,) = struct.unpack(">I", header)
            payload = b""
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk:
                    raise OSError("truncated")
                payload += chunk
            digest = b""
            while len(digest) < 64:
                chunk = sock.recv(64 - len(digest))
                if not chunk:
                    raise OSError("truncated")
                digest += chunk
            return header + payload + digest
        finally:
            sock.close()

    def test_export_before_quiesce_refused_on_real_wire(self) -> None:
        provider, thread, exporter, xthread, _ = self._up()
        try:
            # ACTUAL command attempt over the trusted peer channel:
            # refused with the exact closed bytes, no state advance
            reply = self._cmd(exporter, "export")
            assert reply == b"error export-before-quiesce\n"
            assert exporter.state == "running"
            assert exporter._payload is None
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_unknown_command_refused_closed(self) -> None:
        provider, thread, exporter, xthread, _ = self._up()
        try:
            # an out-of-enum command gets no reply and no state change
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(exporter.server.getsockname())
            try:
                sock.sendall(b"selfdestruct\n")
                assert sock.recv(1) == b""
            finally:
                sock.close()
            assert exporter.state == "running"
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_quiesce_measured_final_state(self) -> None:
        provider, thread, exporter, xthread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            record = provider.quiesce(None, subject_scan=lambda: 0, tools_scan=lambda p: 0)
            model.validate_quiesce_record(record)
            assert record["provider_sockets_closed"] is True
            assert record["handlers_stopped"] is True
            assert record["active_connections"] == 0
            # no admission after quiesce
            time.sleep(0.3)
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_snapshot_binds_seeded_originals(self) -> None:
        provider, thread, exporter, xthread, _ = self._up()
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            snapshot = provider.snapshot_record()
            model.validate_snapshot_record(snapshot)
            assert len(snapshot["issued_calls"]) == 2
            assert snapshot["originals_bytes"] == 3 * 512
            # REAL tamper negative: mutate one owned original and the
            # snapshot must fail closed
            with open(f"{provider.originals_dir}/1", "ab") as handle:
                handle.write(b"slaif tamper")
            with pytest.raises(ctrl.ControllerError) as excinfo:
                provider.snapshot_record()
            assert excinfo.value.args[0] == "originals-mutated"
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_ordered_quiesce_export_once_real_wire(self) -> None:
        provider, thread, exporter, xthread, _ = self._up()
        try:
            code, _body, _ = post_json(provider.port, base_request())
            assert code == 200
            reply = self._cmd(exporter, "quiesce")
            assert reply.startswith(b"quiesce-ok ")
            quiesce_record = json.loads(reply[len(b"quiesce-ok ") : -1])
            model.validate_quiesce_record(quiesce_record)
            assert quiesce_record["handlers_stopped"] is True
            assert exporter.state == "quiesced"
            # a second quiesce is refused on the real wire
            assert self._cmd(exporter, "quiesce") == b"error quiesce-not-running\n"
            # exact frame: 4B BE length + payload + 64-hex digest
            frame = self._cmd(exporter, "export")
            (length,) = struct.unpack(">I", frame[:4])
            payload_bytes = frame[4 : 4 + length]
            digest = frame[4 + length :]
            assert len(payload_bytes) == length
            assert len(digest) == 64
            payload = json.loads(payload_bytes.decode())
            assert set(payload) == {
                "quiesce",
                "snapshot",
                "diagnostic",
                "observed_at_position",
                "originals",
                "originals_count",
            }
            assert payload["quiesce"] == quiesce_record
            model.validate_snapshot_record(payload["snapshot"])
            assert payload["originals_count"] == ctrl.ORIGINALS_COUNT
            assert [len(base64.b64decode(o)) for o in payload["originals"]] == [512, 512, 512]
            assert digest.decode("ascii") == hashlib.sha256(payload_bytes).hexdigest()
            # repeated export refused on the real wire
            assert self._cmd(exporter, "export") == b"error export-repeated\n"
            assert exporter.state == "exported"
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_unobserved_diagnostic_marker(self) -> None:
        provider, thread, exporter, xthread, _ = self._up(scenario="diagnostic")
        try:
            assert provider.diagnostic is None
            # the export payload must carry the closed unobserved
            # marker, never a canned tool mode
            provider.quiesce(None, subject_scan=lambda: 0, tools_scan=lambda p: 0)
            exporter._quiesce_record = {
                "record": model.SCHEMA_QUIESCE,
                "provider_sockets_closed": True,
                "handlers_stopped": True,
                "owned_subject_stopped": True,
                "owned_tools_stopped": True,
                "active_connections": 0,
                "residual_writers": 0,
            }
            payload = json.loads(exporter._build_payload().decode())
            assert payload["diagnostic"] == {"state": "unobserved"}
            assert payload["observed_at_position"] is None
            assert payload["originals_count"] == ctrl.ORIGINALS_COUNT
        finally:
            self._teardown(provider, thread, exporter, xthread)

    def test_deadline_expires_requests(self) -> None:
        clock = _Clock()
        ledger, lock, registry, provider, thread, clock_ref = make_provider(clock=clock)
        try:
            code, body, _ = post_json(provider.port, base_request())
            assert code == 200
            clock.now += 31  # past the 30s deadline
            code, _, how = post_json(provider.port, base_request())
            assert code is None and how in ("closed", "reset")
        finally:
            provider.closed = True
            thread.join(timeout=2)
