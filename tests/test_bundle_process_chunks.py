"""D09 process/chunk observation: native wrapper, chain law, composition.

Covers the pinned ``codex-native-exec-wrapper/v1`` parser, the closed
empty-stdin poll law, the session-ownership and chain-invalidation laws,
the no-retention bounds preflight, the earned region mapping back onto
the original pieces, the occurrence-hash law, and operational privacy.
Fixtures under ``tests/fixtures/cache_bundles/v1/process_*.json`` are
SYNTHETIC-DERIVED from the qualified 017-aj reference-fixture capture
(pinned 0.164.0); inline payloads are synthetic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    NATIVE_TOOL_WRAPPER_FORMAT,
    Limitation,
    ObservationBounds,
    PathContext,
    ProcessObservation,
    ProcessOutcome,
    observe_processes,
    observe_request,
    parse_native_wrapper,
    sha256_hex,
)

V1 = Path(__file__).parent / "fixtures" / "cache_bundles" / "v1"
_CTX = PathContext(workspace="/work")
_B = ObservationBounds()


def load(name: str) -> dict[str, Any]:
    value = json.loads((V1 / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _running(session: int, chunk: str, wall: str, tokens: int, body: str) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        f"Wall time: {wall} seconds\n"
        f"Process running with session ID {session}\n"
        f"Original token count: {tokens}\n"
        f"Output:\n{body}"
    )


def _final(chunk: str, wall: str, code: int, tokens: int, body: str) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        f"Wall time: {wall} seconds\n"
        f"Process exited with code {code}\n"
        f"Original token count: {tokens}\n"
        f"Output:\n{body}"
    )


def _exec(cid: str, cmd: str) -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}),
    }


def _out(cid: str, text: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": cid, "output": text}


def _poll(cid: str, session: int, chars: str = "") -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "write_stdin",
        "arguments": json.dumps({"session_id": session, "chars": chars}),
    }


def _poll_raw(cid: str, arguments: Any) -> dict[str, Any]:
    args: Any = arguments if isinstance(arguments, str) else json.dumps(arguments)
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "write_stdin",
        "arguments": args,
    }


def _payload(*items: dict[str, Any]) -> dict[str, Any]:
    return {"model": "synthetic-bundle-model", "input": list(items)}


def _proc(payload: dict[str, Any], **bounds: Any) -> tuple[ProcessObservation, ...]:
    return observe_processes(
        payload, _CTX, ObservationBounds(**bounds), selected_endpoint="responses"
    )


def _only(payload: dict[str, Any], **bounds: Any) -> ProcessObservation:
    observations = _proc(payload, **bounds)
    assert len(observations) == 1
    return observations[0]


def _digest(*parts: str) -> str:
    return sha256_hex("".join(parts))


class TestNativeWrapperParser:
    def test_valid_running_frame_parses_facts_and_span(self) -> None:
        body = "line one\r\nline two\r\n"
        text = _running(9203, "0a1b2c", "0.1234", 41, body)
        facts = parse_native_wrapper(text, _B)
        assert facts.reasons == ()
        assert facts.session_id == 9203
        assert facts.exit_code is None
        assert facts.original_token_count == 41
        assert facts.chunk_id_present is True
        assert facts.wall_time_present is True
        assert facts.output_present is True
        assert facts.truncated is False
        assert facts.output_char_length == len(body)
        assert facts.output_byte_length == len(body.encode("utf-8"))
        assert facts.output_span is not None
        start = text.index("\nOutput:\n") + len("\nOutput:\n")
        assert (facts.output_span.start, facts.output_span.end) == (start, len(text))
        assert facts.output_span.slice(text) == body

    def test_valid_final_frame_omits_session(self) -> None:
        text = _final("3d4e5f", "0.6789", 0, 88, "done\n")
        facts = parse_native_wrapper(text, _B)
        assert facts.reasons == ()
        assert facts.exit_code == 0
        assert facts.session_id is None

    def test_empty_output_is_exact_not_missing(self) -> None:
        text = _running(9203, "0a1b2c", "0.0001", 0, "")
        facts = parse_native_wrapper(text, _B)
        assert facts.reasons == ()
        assert facts.output_present is True
        assert facts.output_char_length == 0
        assert facts.output_byte_length == 0
        assert facts.output_span is not None
        assert facts.output_span.start == facts.output_span.end

    def test_non_ascii_byte_length_is_exact(self) -> None:
        text = _final("3d4e5f", "0.0001", 0, 1, "\u00e9\U0001f600")
        facts = parse_native_wrapper(text, _B)
        assert facts.output_char_length == 2
        assert facts.output_byte_length == 2 + 4

    def test_over_bound_body_is_typed(self) -> None:
        text = _final("3d4e5f", "0.0001", 0, 1, "x" * 101)
        facts = parse_native_wrapper(text, ObservationBounds(max_output_chars=100))
        assert facts.reasons == (Limitation.OUTPUT_OVER_BOUND,)
        assert facts.output_present is False

    def test_missing_body_and_missing_delimiter(self) -> None:
        assert parse_native_wrapper("", _B).reasons == (Limitation.MISSING_OUTPUT_BODY,)
        assert parse_native_wrapper("Wall time: 1.0000 seconds", _B).reasons == (
            Limitation.MALFORMED_WRAPPER,
        )

    def test_lone_surrogate_is_typed_unicode(self) -> None:
        text = _final("3d4e5f", "0.0001", 0, 1, "bad\ud800byte")
        assert parse_native_wrapper(text, _B).reasons == (Limitation.MALFORMED_UNICODE,)

    def test_exit_and_running_are_mutually_exclusive(self) -> None:
        text = (
            "Wall time: 1.0000 seconds\n"
            "Process exited with code 0\n"
            "Process running with session ID 9203\n"
            "Output:\nx"
        )
        assert parse_native_wrapper(text, _B).reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_unknown_section_is_malformed(self) -> None:
        text = "Wall time: 1.0000 seconds\nExtra: 1\nOutput:\nx"
        assert parse_native_wrapper(text, _B).reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_session_zero_is_rejected(self) -> None:
        text = "Wall time: 1.0000 seconds\nProcess running with session ID 0\nOutput:\nx"
        assert parse_native_wrapper(text, _B).reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_configured_header_line_bound_is_enforced(self) -> None:
        text = _running(9203, "0a1b2c", "0.1234", 41, "x")
        tight = ObservationBounds(max_wrapper_header_lines=1)
        # The first delimiter lies beyond the configured cap: a fixed
        # resource refusal, distinct from a grammar verdict.
        assert parse_native_wrapper(text, tight).reasons == (Limitation.WRAPPER_HEADER_OVER_BOUND,)
        assert (
            parse_native_wrapper(text, ObservationBounds(max_wrapper_header_lines=8)).reasons == ()
        )
        # A header with more lines than the cap even though the delimiter
        # lies within the window is the same fixed resource refusal.
        lines = "\n".join(["Wall time: 1.0000 seconds"] + [f"line {i}" for i in range(8)])
        text_lines = f"{lines}\nOutput:\nx"
        assert parse_native_wrapper(text_lines, _B).reasons == (
            Limitation.WRAPPER_HEADER_OVER_BOUND,
        )

    def test_warning_prefix_at_body_start_marks_truncated(self) -> None:
        warning = (
            "Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n"
        )
        text = _final("3d4e5f", "0.0001", 0, 512, warning + "head\ntail\n")
        assert parse_native_wrapper(text, _B).truncated is True

    def test_warning_like_text_mid_body_is_not_a_header(self) -> None:
        warning = (
            "Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n"
        )
        text = _final("3d4e5f", "0.0001", 0, 10, "content\n" + warning)
        assert parse_native_wrapper(text, _B).truncated is False

    def test_omission_markers_mark_truncated(self) -> None:
        for marker in ("\u2026123 tokens truncated\u2026", "... 456 bytes omitted ..."):
            text = _final("3d4e5f", "0.0001", 0, 10, "head\n" + marker + "\ntail")
            assert parse_native_wrapper(text, _B).truncated is True, marker


class TestPollArgumentLaw:
    """The closed empty-stdin law, exercised through chain collection."""

    def _chain(self, *polls: dict[str, Any], exit_body: str = "done\n") -> dict[str, Any]:
        items: list[dict[str, Any]] = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
        ]
        for index, poll in enumerate(polls):
            items.append(poll)
            if index == len(polls) - 1:
                items.append(_out(poll["call_id"], _final("3d4e5f", "0.6789", 0, 1, exit_body)))
            else:
                items.append(_out(poll["call_id"], _running(9203, "445566", "0.0202", 1, "mid\n")))
        return _payload(*items)

    def test_nonempty_matching_chars_invalidate_even_with_later_clean_poll(self) -> None:
        payload = self._chain(_poll("call_p1", 9203, "x"), _poll("call_p2", 9203))
        obs = _only(payload)
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_POLL_INVALID,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_extra_key_matching_arguments_invalidate(self) -> None:
        payload = self._chain(_poll_raw("call_p1", {"session_id": 9203, "chars": "", "extra": 1}))
        obs = _only(payload)
        assert obs.reasons == (Limitation.PROCESS_POLL_INVALID,)

    def test_non_string_chars_invalidate(self) -> None:
        payload = self._chain(_poll_raw("call_p1", {"session_id": 9203, "chars": 5}))
        assert _only(payload).reasons == (Limitation.PROCESS_POLL_INVALID,)

    def test_absent_chars_invalidate(self) -> None:
        payload = self._chain(_poll_raw("call_p1", {"session_id": 9203}))
        assert _only(payload).reasons == (Limitation.PROCESS_POLL_INVALID,)

    def test_unrelated_sessions_neither_join_nor_poison(self) -> None:
        # Honest unrelated controls: each foreign poll's own result
        # either names its own (unclaimed) session or carries no
        # parseable native claim at all — no explicit known-native
        # claim touches the chain session, so none may join or poison.
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll_raw("call_o1", {"session_id": 7777, "chars": "junk"}),
            _out("call_o1", _running(7777, "777777", "0.0303", 1, "other\n")),
            _poll_raw("call_o2", {"chars": ""}),
            _out("call_o2", "plain tool output, no native header\n"),
            _poll_raw("call_o3", {"session_id": True, "chars": ""}),
            _out(
                "call_o3",
                "legacy wrapper\nWall time: 0.5000 seconds\nProcess is still running\nOutput:\n",
            ),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert len(obs.pieces) == 2

    def test_malformed_session_args_with_explicit_running_header_poison_negatively(self) -> None:
        # A write_stdin with malformed session identity (a string) whose
        # own result is a clean running frame for the chain session: the
        # explicit known-native claim invalidates the session negatively.
        # No execution is inferred from the malformed arguments, and the
        # later clean poll never repairs the chain.
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll_raw("call_o", {"session_id": "9203", "chars": ""}),
            _out("call_o", _running(9203, "777777", "0.0303", 1, "mid\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_SESSION_CONFLICT,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_contradictory_poll_header_invalidates_claimed_session(self) -> None:
        # A closed poll addressed to 9203 whose own result is a clean
        # running frame for 7777 (which a second exec claims): the
        # explicit foreign claim invalidates 7777 negatively while the
        # addressed chain conflicts on its own frame.  Neither session
        # acquires.
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "a one\n")),
            _exec("call_e2", "cat B.md"),
            _out("call_e2", _running(7777, "112233", "0.1235", 1, "b one\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _running(7777, "445566", "0.0202", 1, "cross\n")),
            _poll("call_p2", 9203),
            _out("call_p2", _final("3d4e5f", "0.6789", 0, 1, "a two\n")),
            _poll("call_p3", 7777),
            _out("call_p3", _final("5f6a7b", "0.6790", 0, 1, "b two\n")),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 2
        by_id = {o.exec_call_id: o for o in observations}
        assert set(by_id) == {"call_e1", "call_e2"}
        assert by_id["call_e1"].outcome is ProcessOutcome.UNSUPPORTED
        assert by_id["call_e1"].reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)
        assert by_id["call_e2"].outcome is ProcessOutcome.UNSUPPORTED
        assert by_id["call_e2"].reasons == (Limitation.PROCESS_SESSION_CONFLICT,)
        assert all(o.bundle_digest is None and o.pieces == () for o in observations)

    def test_string_arguments_are_decoded_before_classification(self) -> None:
        payload = self._chain(_poll_raw("call_p1", json.dumps({"session_id": 9203, "chars": ""})))
        assert _only(payload).outcome is ProcessOutcome.COMPLETE


class TestUnidentifiedPollLaw:
    """Unassignable-argument native polls: negative uncertainty only.

    A write_stdin whose closed argument session is UNASSIGNABLE
    (malformed/absent/non-int identity, undecodable arguments) and
    whose bounded own result record carries a well-formed native
    header — running, final, or unknown-status — is negative
    uncertainty: a poll ISSUED after the exec issue and before the
    chain's terminal result (no terminal result: the chain is still
    open) is potentially associated and its native record prevents
    complete-source proof even when delivered late; the affected
    chain is negatively invalidated.  The SID is never coerced, no
    execution or owner is inferred, duplicated results never repair,
    and numeric call/result chronology isolates polls issued before
    the exec issue or after the terminal result.  Every case below
    runs through the PUBLIC ``observe_request`` composition entry.
    """

    def _items(self) -> list[dict[str, Any]]:
        return [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
        ]

    def _tail(self) -> list[dict[str, Any]]:
        return [
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]

    def _orphan(
        self,
        arguments: Any,
        body: str = _final("6a7b8c", "0.6791", 0, 1, "B\n"),
        cid: str = "call_o",
    ) -> list[dict[str, Any]]:
        return [_poll_raw(cid, arguments), _out(cid, body)]

    @staticmethod
    def _pub(
        payload: dict[str, Any], endpoint: str = "responses"
    ) -> tuple[ProcessObservation, ...]:
        # Public composition entry — the same surface the ROOT
        # 15-case probe exercises (envelope/endpoint validation
        # included), so CI retains the exact public guarantees.
        return observe_request(payload, _CTX, _B, endpoint=endpoint).processes

    def _only_pub(self, payload: dict[str, Any], endpoint: str = "responses") -> ProcessObservation:
        observations = self._pub(payload, endpoint)
        assert len(observations) == 1
        return observations[0]

    def _conflict_obs(self, payload: dict[str, Any]) -> None:
        obs = self._only_pub(payload)
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_malformed_string_session_native_final_invalidates(self) -> None:
        self._conflict_obs(
            _payload(
                *(self._items() + self._orphan({"session_id": "9203", "chars": ""}) + self._tail())
            )
        )

    def test_missing_session_native_final_invalidates(self) -> None:
        self._conflict_obs(_payload(*(self._items() + self._orphan({"chars": ""}) + self._tail())))

    def test_boolean_session_native_final_invalidates(self) -> None:
        self._conflict_obs(
            _payload(
                *(self._items() + self._orphan({"session_id": True, "chars": ""}) + self._tail())
            )
        )

    def test_unknown_status_native_frame_invalidates(self) -> None:
        body = "Wall time: 0.0000 seconds\nOutput:\nB\n"
        self._conflict_obs(
            _payload(*(self._items() + self._orphan({"chars": ""}, body) + self._tail()))
        )

    def test_duplicated_orphan_native_results_never_repair(self) -> None:
        items = self._items() + self._orphan({"chars": ""})
        items.append(_out("call_o", _final("6a7b8c", "0.6791", 0, 1, "D\n")))
        self._conflict_obs(_payload(*(items + self._tail())))

    def test_orphan_issued_before_final_delivered_late_still_invalidates(self) -> None:
        # The orphan was ISSUED while the chain was still open (before
        # the terminal result); its late delivery must not disappear.
        items = self._items() + [
            _poll("call_end", 9203),
            _poll_raw("call_o", {"chars": ""}),
        ]
        items.append(_out("call_end", _final("3d4e5f", "0.6789", 0, 1, "done\n")))
        items.append(_out("call_o", _final("6a7b8c", "0.6791", 0, 1, "B\n")))
        self._conflict_obs(_payload(*items))

    def test_orphan_issued_before_future_exec_is_isolated(self) -> None:
        # A poll issued before the exec issue can never belong to that
        # chain, even when its native result is delivered after the
        # chain's terminal result (numeric call chronology).
        items = [_poll_raw("call_o", {"chars": ""})] + self._items() + self._tail()
        items.append(_out("call_o", _final("6a7b8c", "0.6791", 0, 1, "B\n")))
        obs = self._only_pub(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert len(obs.pieces) == 2

    def test_strict_different_session_final_is_isolated(self) -> None:
        obs = self._only_pub(
            _payload(
                *(self._items() + self._orphan({"session_id": 7777, "chars": ""}) + self._tail())
            )
        )
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert len(obs.pieces) == 2

    def test_orphan_native_before_exec_issue_is_isolated(self) -> None:
        obs = self._only_pub(
            _payload(*(self._orphan({"chars": ""}) + self._items() + self._tail()))
        )
        assert obs.outcome is ProcessOutcome.COMPLETE

    def test_orphan_native_after_completed_chain_is_isolated(self) -> None:
        obs = self._only_pub(
            _payload(*(self._items() + self._tail() + self._orphan({"chars": ""})))
        )
        assert obs.outcome is ProcessOutcome.COMPLETE

    def test_orphan_between_exec_issue_and_initial_result_invalidates(self) -> None:
        head = self._items()
        items = [head[0]] + self._orphan({"chars": ""}) + [head[1]] + self._tail()
        self._conflict_obs(_payload(*items))

    def test_plain_non_native_error_is_isolated(self) -> None:
        obs = self._only_pub(
            _payload(
                *(
                    self._items()
                    + self._orphan({"chars": ""}, "ordinary non-native tool error\n")
                    + self._tail()
                )
            )
        )
        assert obs.outcome is ProcessOutcome.COMPLETE

    def test_unknown_opaque_family_is_isolated(self) -> None:
        items = self._items()
        items.append(
            {
                "type": "function_call",
                "call_id": "call_o",
                "name": "opaque_tool",
                "arguments": json.dumps({"chars": ""}),
            }
        )
        items.append(_out("call_o", _final("6a7b8c", "0.6791", 0, 1, "B\n")))
        items.extend(self._tail())
        assert self._only_pub(_payload(*items)).outcome is ProcessOutcome.COMPLETE

    def test_two_potentially_open_chains_both_invalidated(self) -> None:
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "a one\n")),
            _exec("call_e2", "cat B.md"),
            _out("call_e2", _running(7777, "112233", "0.1235", 1, "b one\n")),
            _poll_raw("call_o", {"chars": ""}),
            _out("call_o", _final("6a7b8c", "0.6791", 0, 1, "B\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "a two\n")),
            _poll("call_p2", 7777),
            _out("call_p2", _final("5f6a7b", "0.6790", 0, 1, "b two\n")),
        ]
        observations = self._pub(_payload(*items))
        assert len(observations) == 2
        assert all(o.outcome is ProcessOutcome.UNSUPPORTED for o in observations)
        assert all(o.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,) for o in observations)
        assert all(o.pieces == () and o.bundle_digest is None for o in observations)

    def test_chat_endpoint_orphan_invalidates(self) -> None:
        items = self._items() + self._orphan({"chars": ""}) + self._tail()
        messages = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": item["call_id"],
                        "function": {"name": item["name"], "arguments": item["arguments"]},
                    }
                ],
            }
            if item["type"] == "function_call"
            else {
                "role": "tool",
                "tool_call_id": item["call_id"],
                "content": item["output"],
            }
            for item in items
        ]
        observations = self._pub({"messages": messages}, endpoint="chat")
        assert len(observations) == 1
        assert observations[0].outcome is ProcessOutcome.UNSUPPORTED
        assert observations[0].reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)


class TestChainLaw:
    def test_missing_poll_result_invalidates(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_duplicated_poll_result_invalidates(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _running(9203, "445566", "0.0202", 1, "mid\n")),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_after_final_poll_invalidates(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
            _poll("call_p2", 9203),
            _out("call_p2", _running(9203, "445566", "0.0202", 1, "late\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_overlapping_polls_invalidates(self) -> None:
        # pollB (position 2) is accepted first with its result at 5;
        # pollA (position 3) was issued before that result: serial
        # causality is broken.
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_b", 9203),
            _poll("call_a", 9203),
            _out("call_a", _running(9203, "445566", "0.0202", 1, "mid\n")),
            _out("call_b", _running(9203, "556677", "0.0303", 1, "late\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_unknown_status_middle_frame_invalidates(self) -> None:
        unknown = "Wall time: 0.0202 seconds\nOutput:\nno status here\n"
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", unknown),
            _poll("call_p2", 9203),
            _out("call_p2", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_foreign_session_result_frame_invalidates(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _running(7777, "445566", "0.0202", 1, "foreign\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_session_reuse_conflicts_all_claimants(self) -> None:
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "start one\n")),
            _exec("call_e2", "echo hello"),
            _out("call_e2", _running(9203, "112233", "0.1235", 1, "start two\n")),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 2
        assert all(o.reasons == (Limitation.PROCESS_SESSION_CONFLICT,) for o in observations)

    def test_duplicate_initial_results_are_negative_ambiguity(self) -> None:
        # A duplicated result on the exec-family call never acquires,
        # but its clean running header stays observable: the good
        # chain's session can no longer be established cleanly.
        items = [
            _exec("call_dup", "cat A.md"),
            _out("call_dup", _running(9203, "0a1b2c", "0.1234", 1, "x one\n")),
            _out("call_dup", _running(9203, "112233", "0.1235", 1, "x two\n")),
            _exec("call_e", "cat B.md"),
            _out("call_e", _running(9203, "445566", "0.1236", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.exec_call_id == "call_e"
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_SESSION_CONFLICT,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_precall_known_native_claim_is_negative_ambiguity(self) -> None:
        # A pre-call result with a clean running header for the good
        # chain's session: the explicit claim stays observable as
        # negative ambiguity; the record never acquires and the session
        # is never established.
        items = [
            _out("call_future", _running(9203, "0a1b2c", "0.1234", 1, "early\n")),
            _exec("call_future", "cat A.md"),
            _exec("call_e", "cat B.md"),
            _out("call_e", _running(9203, "445566", "0.1236", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.exec_call_id == "call_e"
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_SESSION_CONFLICT,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_non_earned_read_command_still_claims_session(self) -> None:
        # A competing owner whose command is not an earned read (echo)
        # still claims the session; the good-looking chain never acquires.
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _exec("call_e2", "echo hello"),
            _out("call_e2", _running(9203, "112233", "0.1235", 1, "other\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 2
        assert all(o.outcome is ProcessOutcome.UNSUPPORTED for o in observations)
        assert all(o.reasons == (Limitation.PROCESS_SESSION_CONFLICT,) for o in observations)

    def test_different_session_is_an_independent_chain(self) -> None:
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _exec("call_e2", "echo hello"),
            _out("call_e2", _running(7777, "112233", "0.1235", 1, "other\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 2
        complete = [o for o in observations if o.outcome is ProcessOutcome.COMPLETE]
        running = [o for o in observations if o.outcome is ProcessOutcome.RUNNING]
        assert len(complete) == 1 and len(running) == 1

    def test_running_without_final_is_honest_running(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _running(9203, "445566", "0.0202", 1, "mid\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.RUNNING
        assert obs.reasons == (Limitation.PROCESS_RUNNING,)
        assert obs.final_wrapper is None
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()

    def test_nonzero_exit_is_preserved(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 2, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.NONZERO_EXIT
        assert obs.bundle_digest is None

    def test_truncated_final_never_complete(self) -> None:
        warning = (
            "Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n"
        )
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 512, warning + "head\ntail\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.TRUNCATED
        assert obs.reasons == (Limitation.PROCESS_TRUNCATED,)
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()

    def test_forged_header_in_source_never_dispatches(self) -> None:
        body = "content with Process running with session ID 7777 inside\n"
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, body)),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 1
        assert observations[0].outcome is ProcessOutcome.COMPLETE

    def test_position_based_causality_not_lexical_ids(self) -> None:
        # The poll ID is lexicographically smaller than the exec ID;
        # causality comes from exact structural positions only.
        items = [
            _exec("call_z_exec", "cat A.md"),
            _out("call_z_exec", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_a_poll", 9203),
            _out("call_a_poll", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE

    def test_interleaved_independent_sessions_do_not_poison(self) -> None:
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "a one\n")),
            _exec("call_e2", "cat B.md"),
            _out("call_e2", _running(7777, "112233", "0.1235", 1, "b one\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "a two\n")),
            _poll("call_p2", 7777),
            _out("call_p2", _final("5f6a7b", "0.6790", 0, 1, "b two\n")),
        ]
        observations = _proc(_payload(*items))
        assert len(observations) == 2
        assert all(o.outcome is ProcessOutcome.COMPLETE for o in observations)
        assert {o.exec_call_id for o in observations} == {"call_e1", "call_e2"}


class TestIdentityCollisions:
    def test_unknown_call_id_collision_invalidates_exec(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            {"type": "custom_tool_call", "call_id": "call_e", "input": "opaque"},
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)

    def test_poll_id_collision_with_other_family_invalidates(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            {
                "type": "function_call",
                "call_id": "call_p1",
                "name": "unknown_tool",
                "arguments": "{}",
            },
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.reasons == (Limitation.PROCESS_CHAIN_CONFLICT,)


class TestBounds:
    def test_sole_over_bound_owner_is_fixed_over_bound(self) -> None:
        body = "x" * 150
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, body)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        obs = _only(_payload(*items), max_output_chars=100)
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.OVER_BOUND,)
        assert obs.pieces == ()
        assert obs.piece_count == 0
        assert obs.total_byte_length == 0
        assert obs.initial_wrapper.reasons == (Limitation.OUTPUT_OVER_BOUND,)

    def test_over_bound_competing_owner_still_conflicts(self) -> None:
        items = [
            _exec("call_e1", "cat A.md"),
            _out("call_e1", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _exec("call_e2", "cat B.md"),
            _out("call_e2", _running(9203, "112233", "0.1235", 1, "x" * 150)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items), max_output_chars=100)
        assert len(observations) == 2
        assert all(
            o.outcome is ProcessOutcome.UNSUPPORTED
            and o.reasons == (Limitation.PROCESS_SESSION_CONFLICT,)
            for o in observations
        )

    def test_header_cap_blocks_incomplete_owner_inventory(self) -> None:
        # A competing owner whose closed 4-line header lies beyond the
        # configured cap-2 character window is unclassifiable: the
        # bounds prevent a complete owner inventory, so BOTH the
        # good-looking claimant and the exec-origin anchor carry the
        # fixed non-acquiring OVER_BOUND — never a selection from an
        # incomplete inventory.
        def _short(sid: int, body: str) -> str:
            return (
                f"Wall time: 0.1234 seconds\nProcess running with session ID {sid}\nOutput:\n{body}"
            )

        items = [
            _exec("call_good", "cat A.md"),
            _out("call_good", _short(9203, "start\n")),
            _exec("call_other", "echo ignored"),
            _out("call_other", _running(9203, "112233", "0.1235", 1, "hidden\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items), max_wrapper_header_lines=2)
        assert len(observations) == 2
        assert all(
            o.outcome is ProcessOutcome.UNSUPPORTED
            and o.reasons == (Limitation.OVER_BOUND,)
            and o.pieces == ()
            and o.bundle_digest is None
            for o in observations
        )
        assert {o.exec_call_id for o in observations} == {"call_good", "call_other"}

    def test_line_count_owner_bound_cap_three(self) -> None:
        # LINE-COUNT exhaustion (the delimiter is inside the character
        # window): a full 4-line same-SID contender under cap-3 is
        # unclassifiable and must block, not silently drop.
        def _short(sid: int, body: str) -> str:
            return (
                f"Wall time: 0.1234 seconds\nProcess running with session ID {sid}\nOutput:\n{body}"
            )

        items = [
            _exec("call_good", "cat A.md"),
            _out("call_good", _short(9203, "start\n")),
            _exec("call_other", "echo ignored"),
            _out("call_other", _running(9203, "112233", "0.1235", 1, "hidden\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items), max_wrapper_header_lines=3)
        assert len(observations) == 2
        assert all(
            o.outcome is ProcessOutcome.UNSUPPORTED and o.reasons == (Limitation.OVER_BOUND,)
            for o in observations
        )
        assert {o.exec_call_id for o in observations} == {"call_good", "call_other"}

    def test_line_count_owner_bound_cap_two(self) -> None:
        # LINE-COUNT exhaustion inside the 88-char cap-2 window: a
        # 3-line same-SID contender (wall + running + tokens, 86 chars)
        # is unclassifiable and must block, not silently drop.
        def _short(sid: int, body: str) -> str:
            return (
                f"Wall time: 0.1234 seconds\nProcess running with session ID {sid}\nOutput:\n{body}"
            )

        def _three(sid: int, body: str) -> str:
            return (
                f"Wall time: 0.1235 seconds\n"
                f"Process running with session ID {sid}\n"
                f"Original token count: 1\nOutput:\n{body}"
            )

        items = [
            _exec("call_good", "cat A.md"),
            _out("call_good", _short(9203, "start\n")),
            _exec("call_other", "echo ignored"),
            _out("call_other", _three(9203, "hidden\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        observations = _proc(_payload(*items), max_wrapper_header_lines=2)
        assert len(observations) == 2
        assert all(
            o.outcome is ProcessOutcome.UNSUPPORTED and o.reasons == (Limitation.OVER_BOUND,)
            for o in observations
        )
        assert {o.exec_call_id for o in observations} == {"call_good", "call_other"}

    def test_sole_blocked_exec_anchor_keeps_honest_record(self) -> None:
        # A blocked exec-origin anchor with no valid claimant keeps its
        # honest non-acquiring record (the exec occurrence cannot be
        # classified within the cap); no selection, no fabrication.
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "112233", "0.1235", 1, "hidden\n")),
        ]
        obs = _only(_payload(*items), max_wrapper_header_lines=2)
        assert obs.outcome is ProcessOutcome.UNSUPPORTED
        assert obs.reasons == (Limitation.OVER_BOUND,)
        assert obs.exec_call_id == "call_e"
        assert obs.initial_wrapper.reasons == (Limitation.WRAPPER_HEADER_OVER_BOUND,)
        assert obs.pieces == ()
        assert obs.bundle_digest is None

    def test_orphan_poll_blocked_anchor_invents_no_origin(self) -> None:
        # An orphan write_stdin with an over-bound header (NO exec
        # exists) invents no process origin: no process observation at
        # all, and the read surface keeps its honest bookkeeping.
        items = [
            _poll("call_o", 9203),
            _out("call_o", _running(9203, "112233", "0.1235", 1, "hidden\n")),
        ]
        payload = _payload(*items)
        assert (
            observe_processes(
                payload,
                _CTX,
                ObservationBounds(max_wrapper_header_lines=2),
                selected_endpoint="responses",
            )
            == ()
        )
        report = observe_request(
            payload,
            _CTX,
            ObservationBounds(max_wrapper_header_lines=2),
            endpoint="responses",
        )
        assert report.processes == ()
        assert len(report.reads) + len(report.unpaired) > 0

    def test_session_bound_at_limit_and_one_over(self) -> None:
        def build(count: int) -> dict[str, Any]:
            items: list[dict[str, Any]] = []
            for i in range(count):
                items.append(_exec(f"call_e{i}", f"cat F{i}.md"))
                items.append(
                    _out(
                        f"call_e{i}",
                        _running(9000 + i, "0a1b2c", "0.1234", 1, f"n{i}\n"),
                    )
                )
            return _payload(*items)

        assert all(o.outcome is ProcessOutcome.RUNNING for o in _proc(build(4)))
        over = _proc(build(5))
        assert len(over) == 5
        assert all(
            o.outcome is ProcessOutcome.UNSUPPORTED and o.reasons == (Limitation.OVER_BOUND,)
            for o in over
        )

    def test_poll_and_piece_bounds(self) -> None:
        def build(polls: int) -> dict[str, Any]:
            items: list[dict[str, Any]] = [
                _exec("call_e", "cat A.md"),
                _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            ]
            for i in range(polls):
                items.append(_poll(f"call_p{i}", 9203))
                if i == polls - 1:
                    items.append(_out(f"call_p{i}", _final("3d4e5f", "0.6789", 0, 1, "done\n")))
                else:
                    items.append(
                        _out(
                            f"call_p{i}",
                            _running(9203, "445566", "0.0202", 1, f"m{i}\n"),
                        )
                    )
            return _payload(*items)

        at_limit = _only(build(12))
        assert at_limit.outcome is ProcessOutcome.COMPLETE
        assert at_limit.piece_count == 13
        over = _only(build(13))
        assert over.outcome is ProcessOutcome.UNSUPPORTED
        assert over.reasons == (Limitation.OVER_BOUND,)

    def test_cumulative_char_bound_is_decided_before_retention(self) -> None:
        body = "y" * 40
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, body)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, body)),
        ]
        in_bound = _only(_payload(*items), max_process_source_chars=80)
        assert in_bound.outcome is ProcessOutcome.COMPLETE
        over = _only(_payload(*items), max_process_source_chars=79)
        assert over.outcome is ProcessOutcome.UNSUPPORTED
        assert over.reasons == (Limitation.OVER_BOUND,)
        assert over.pieces == ()

    def test_cumulative_exact_byte_bound_is_decided_before_retention(self) -> None:
        # 40 four-byte characters: 40 chars (under the char bound) but
        # 320 bytes (over the byte bound).
        body = "\U0001f600" * 40
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, body)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, body)),
        ]
        over = _only(
            _payload(*items),
            max_process_source_chars=1000,
            max_process_source_bytes=100,
        )
        assert over.outcome is ProcessOutcome.UNSUPPORTED
        assert over.reasons == (Limitation.OVER_BOUND,)
        assert over.pieces == ()
        assert over.total_byte_length == 0


class TestRegionAndDigests:
    def test_complete_chain_earns_region_and_digests(self) -> None:
        body0 = "First chunk line one\r\nSecond chunk line two\r\n"
        body1 = "Final chunk line one\r\nFinal chunk line two\r\n"
        text0 = _running(9203, "0a1b2c", "0.1234", 41, body0)
        text1 = _final("3d4e5f", "0.6789", 0, 88, body1)
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", text0),
            _poll("call_p1", 9203),
            _out("call_p1", text1),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.reasons == ()
        assert obs.proven_executed == ("A.md",)
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1
        assert obs.piece_count == 2
        assert obs.nonempty_piece_count == 2
        total = len(body0) + len(body1)
        assert obs.total_char_length == total
        assert obs.total_byte_length == total
        expected = _digest(body0, body1)
        assert obs.bundle_digest == expected
        assert obs.member_digests == (expected,)
        assert obs.proven_region_char_length == total
        # Per-piece spans are absolute in each own result string.
        span0, span1 = obs.pieces[0].char_span, obs.pieces[1].char_span
        assert text0[span0.start : span0.end] == body0
        assert text1[span1.start : span1.end] == body1
        # Region mapped back: each piece carries the full clipped span.
        r0, r1 = obs.region_piece_spans
        assert r0 is not None and r1 is not None
        assert text0[r0.start : r0.end] == body0
        assert text1[r1.start : r1.end] == body1
        # The poll is causally bound to its own result.
        assert len(obs.polls) == 1
        assert obs.polls[0].result_position == 3
        assert obs.final_wrapper is not None
        assert obs.final_wrapper.exit_code == 0
        assert obs.final_result_position == 3

    def test_repeated_file_occurrence_keeps_two_unknown_hashes(self) -> None:
        body0 = "piece one\n"
        body1 = "piece two\n"
        items = [
            _exec("call_e", "cat A.md A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, body0)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, body1)),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "A.md")
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1
        assert obs.member_digests == (None, None)
        assert obs.bundle_digest == _digest(body0, body1)

    def test_two_distinct_files_stay_unknown_per_member(self) -> None:
        body0 = "piece one\n"
        body1 = "piece two\n"
        items = [
            _exec("call_e", "cat A.md B.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, body0)),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, body1)),
        ]
        obs = _only(_payload(*items))
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.distinct_member_count == 2
        assert obs.member_digests == (None, None)

    def test_non_earned_command_completes_without_attribution(self) -> None:
        items = [
            _exec("call_e", "echo hello"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "hello\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "bye\n")),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert obs.region_piece_spans == ()
        assert obs.distinct_member_count is None
        assert obs.slot_width is None

    def test_empty_complete_chain_keeps_zero_width_carrier_spans(self) -> None:
        text0 = _running(9203, "0a1b2c", "0.1234", 0, "")
        text1 = _final("3d4e5f", "0.6789", 0, 0, "")
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", text0),
            _poll("call_p1", 9203),
            _out("call_p1", text1),
        ]
        obs = _only(_payload(*items))
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.piece_count == 2
        assert obs.nonempty_piece_count == 0
        assert all(piece.empty for piece in obs.pieces)
        assert obs.bundle_digest == EMPTY_SOURCE_SHA256
        assert obs.member_digests == (EMPTY_SOURCE_SHA256,)
        assert obs.proven_region_char_length == 0
        r0, r1 = obs.region_piece_spans
        assert r0 is not None and r1 is not None
        assert r0.start == r0.end == obs.pieces[0].char_span.start
        assert r1.start == r1.end == obs.pieces[1].char_span.start

    def test_payload_is_unchanged_by_observation(self) -> None:
        items = [
            _exec("call_e", "cat A.md"),
            _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            _poll("call_p1", 9203),
            _out("call_p1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        payload = _payload(*items)
        before = json.dumps(payload, sort_keys=True)
        _proc(payload)
        assert json.dumps(payload, sort_keys=True) == before


class TestComposition:
    def test_fixture_complete_chain_through_observe_request(self) -> None:
        payload = load("process_running_complete_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "responses"
        assert len(report.processes) == 1
        obs = report.processes[0]
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.exec_call_id == "call_proc_exec_1"
        assert obs.nonempty_piece_count == 2
        # Legacy single-result surface stays untouched and honest: the
        # native frame is non-acquiring there (unknown section) and the
        # deferred poll is typed WRITE_STDIN_CHUNK.
        by_call = {r.call_id: r for r in report.reads}
        assert by_call["call_proc_exec_1"].outcome.value == "unsupported"
        assert Limitation.MALFORMED_WRAPPER in by_call["call_proc_exec_1"].reasons
        assert Limitation.WRITE_STDIN_CHUNK in by_call["call_proc_poll_1"].reasons

    def test_fixture_multi_poll_chain(self) -> None:
        payload = load("process_multi_poll_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.processes[0]
        assert obs.outcome is ProcessOutcome.COMPLETE
        assert obs.piece_count == 3
        assert obs.nonempty_piece_count == 2
        assert obs.pieces[1].empty is True
        # The empty middle piece keeps its real zero-width carrier span.
        middle = obs.region_piece_spans[1]
        assert middle is not None
        assert middle.start == middle.end

    def test_fixture_truncated_chain(self) -> None:
        payload = load("process_native_truncated_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.processes[0]
        assert obs.outcome is ProcessOutcome.TRUNCATED
        assert obs.reasons == (Limitation.PROCESS_TRUNCATED,)
        assert obs.bundle_digest is None

    def test_fixture_single_final_has_no_chain_and_legacy_gap(self) -> None:
        payload = load("process_single_final_no_chain_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.processes == ()
        # The unchanged legacy surface types the pinned native frame
        # non-acquiring (it does not recognize the Original token count
        # section): the recorded C6 gap for already-exited native execs.
        assert len(report.reads) == 1
        assert Limitation.MALFORMED_WRAPPER in report.reads[0].reasons

    def test_fixture_chat_endpoint_chain(self) -> None:
        payload = load("process_chat_running_complete.json")
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "chat"
        assert len(report.processes) == 1
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE

    def test_mixed_envelope_carries_no_process_observation(self) -> None:
        payload = {
            "model": "synthetic-bundle-model",
            "input": [
                _exec("call_e", "cat A.md"),
                _out("call_e", _running(9203, "0a1b2c", "0.1234", 1, "start\n")),
            ],
            "messages": [{"role": "user", "content": "hi"}],
        }
        assert observe_processes(payload, _CTX, _B, selected_endpoint="mixed") == ()
        report = observe_request(payload, context=_CTX)
        assert report.processes == ()

    def test_unknown_endpoint_carries_no_process_observation(self) -> None:
        payload = {"model": "synthetic-bundle-model", "foo": 1}
        assert observe_processes(payload, _CTX, _B, selected_endpoint="unknown") == ()
        assert observe_processes(payload, _CTX, _B) == ()


class TestPrivacy:
    def test_operational_reprs_never_echo_private_ids(self) -> None:
        items = [
            _exec("call_private_exec_1", "cat A.md"),
            _out(
                "call_private_exec_1",
                _running(9203, "0a1b2c", "0.1234", 1, "start\n"),
            ),
            _poll("call_private_poll_1", 9203),
            _out("call_private_poll_1", _final("3d4e5f", "0.6789", 0, 1, "done\n")),
        ]
        report = observe_request(_payload(*items), context=_CTX)
        text = str(report) + repr(report.processes[0])
        assert "call_private_exec_1" not in text
        assert "call_private_poll_1" not in text
        assert "9203" not in text
        assert "<private-id>" in text
        # Nested models redact too.
        poll_text = str(report.processes[0].polls[0]) + repr(report.processes[0].polls[0])
        assert "call_private_poll_1" not in poll_text
        assert "9203" not in poll_text
        wrapper_text = str(report.processes[0].initial_wrapper) + repr(
            report.processes[0].initial_wrapper
        )
        assert "9203" not in wrapper_text

    def test_native_format_identity_is_versioned_and_distinct(self) -> None:
        assert NATIVE_TOOL_WRAPPER_FORMAT == "codex-native-exec-wrapper/v1"
        text = _final("3d4e5f", "0.6789", 0, 1, "x")
        facts = parse_native_wrapper(text, _B)
        assert facts.wrapper_format == NATIVE_TOOL_WRAPPER_FORMAT
        assert facts.chunk_id_present is True
        # Presence only: the chunk value is never retained.
        dump = facts.model_dump(mode="json")
        assert "0a1b2c" not in json.dumps(dump) and "3d4e5f" not in json.dumps(dump)
