"""D05: call/result pairing, exec-wrapper facts, ordered whole bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    Limitation,
    ObservationBounds,
    PathContext,
    ReadOutcome,
    observe_request,
    parse_wrapper,
)

V1 = Path(__file__).parent / "fixtures" / "cache_bundles" / "v1"
_CTX = PathContext(workspace="/work")


def load(name: str) -> dict[str, Any]:
    value = json.loads((V1 / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def output_of(payload: dict[str, Any], index: int = 0) -> str:
    for item in payload["input"]:
        if item.get("type") == "function_call_output":
            value = item["output"]
            assert isinstance(value, str)
            return value
    raise AssertionError("no output item")


class TestWrapperParsing:
    def test_complete_wrapper_facts(self) -> None:
        facts = parse_wrapper(
            "Chunk Id: abc\nWall time: 0.1 seconds\n"
            "Process exited with code 0\nOutput:\ncontent here",
            ObservationBounds(),
        )
        assert facts.reasons == ()
        assert facts.exit_code == 0
        assert facts.output_present is True
        assert facts.output_span is not None
        assert facts.header_span is not None
        # The content region is exact: header untouched, source exact.
        text = (
            "Chunk Id: abc\nWall time: 0.1 seconds\n"
            "Process exited with code 0\nOutput:\ncontent here"
        )
        assert text[facts.output_span.start : facts.output_span.end] == "content here"
        assert text[: facts.header_span.end].endswith("Output:\n")

    def test_nonzero_exit_is_typed(self) -> None:
        facts = parse_wrapper("Process exited with code 1\nOutput:\npartial", ObservationBounds())
        assert facts.reasons == (Limitation.NONZERO_EXIT,)
        assert facts.exit_code == 1

    def test_recorded_truncation_is_typed(self) -> None:
        facts = parse_wrapper(
            "Truncated: true\nProcess exited with code 0\nOutput:\npart",
            ObservationBounds(),
        )
        assert facts.reasons == (Limitation.TRUNCATED_OUTPUT,)

    def test_explicit_no_truncation_marker(self) -> None:
        facts = parse_wrapper(
            "Truncated: false\nProcess exited with code 0\nOutput:\nall",
            ObservationBounds(),
        )
        assert facts.reasons == ()

    def test_unknown_completion_for_plain_output(self) -> None:
        facts = parse_wrapper(
            "MUST read docs/OPERATIONS.md before deployment.\n", ObservationBounds()
        )
        assert facts.reasons == (Limitation.UNKNOWN_COMPLETION,)
        assert facts.output_span is None

    def test_missing_body_is_distinct_from_proven_empty(self) -> None:
        missing = parse_wrapper("", ObservationBounds())
        assert missing.reasons == (Limitation.MISSING_OUTPUT_BODY,)
        empty = parse_wrapper("Process exited with code 0\nOutput:\n", ObservationBounds())
        assert empty.reasons == ()
        assert empty.output_span is not None
        assert empty.output_span.length == 0

    def test_torn_marker_line_is_malformed(self) -> None:
        facts = parse_wrapper("Process exited with code 0\nOutput:", ObservationBounds())
        assert facts.reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_unknown_header_line_after_header_is_malformed(self) -> None:
        facts = parse_wrapper("Chunk Id: abc\nMystery: x\nOutput:\nx", ObservationBounds())
        assert facts.reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_process_running_is_typed(self) -> None:
        facts = parse_wrapper("Chunk Id: abc\nProcess is still running\n", ObservationBounds())
        assert facts.reasons == (Limitation.PROCESS_RUNNING,)

    def test_over_bound_output_is_typed(self) -> None:
        facts = parse_wrapper("x" * 2_000_000, ObservationBounds(max_output_chars=1000))
        assert facts.reasons == (Limitation.OUTPUT_OVER_BOUND,)

    def test_source_metadata_lookalike_does_not_redefine_wrapper(self) -> None:
        # Source after Output: that looks like execution metadata stays
        # source: the wrapper status comes from the header only.
        facts = parse_wrapper(
            "Process exited with code 0\nOutput:\nProcess exited with code 1\n"
            "Truncated: true\nstill source",
            ObservationBounds(),
        )
        assert facts.reasons == ()
        assert facts.exit_code == 0


class TestPairing:
    def test_duplicate_call_ids_are_typed_conflict(self) -> None:
        payload = load("read_duplicate_call_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert {u.limitation for u in report.unpaired} == {Limitation.DUPLICATE_CALL_ID}
        assert len(report.unpaired) == 2  # both call occurrences observed

    def test_missing_result_is_typed(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "call_missing",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                }
            ]
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert report.unpaired[0].limitation is Limitation.MISSING_CALL_RESULT

    def test_mismatched_result_is_typed(self) -> None:
        payload = load("read_mismatched_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert report.unpaired[0].limitation is Limitation.MISMATCHED_CALL_ID

    def test_multi_chunk_results_are_deferred(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\npart one",
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\npart two",
                },
            ]
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert {u.limitation for u in report.unpaired} == {Limitation.MULTI_CHUNK_DEFERRED}
        assert len(report.unpaired) == 2

    def test_unsupported_tool_names_are_not_eligible(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "web_search",
                    "arguments": json.dumps({"query": "A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "results",
                },
            ]
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        # The result is unpaired: its call is not a supported read call.
        assert report.unpaired[0].limitation is Limitation.MISMATCHED_CALL_ID

    def test_namespace_name_without_envelope_evidence_never_suffix_guessed(self) -> None:
        payload = load("read_namespace_unproven_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert report.unpaired[0].limitation is Limitation.MISMATCHED_CALL_ID

    def test_namespace_name_with_envelope_evidence_is_supported(self) -> None:
        payload = load("read_namespace_proven_responses.json")
        report = observe_request(payload, context=_CTX)
        assert len(report.reads) == 1
        assert report.reads[0].outcome is ReadOutcome.COMPLETE

    def test_suffix_resemblance_alone_is_never_evidence(self) -> None:
        # A name ending in exec_command without an envelope declaration is
        # not a supported tool, even though it resembles the real one.
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "weird_exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\nx",
                },
            ]
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()

    def test_process_running_is_deferred(self) -> None:
        payload = load("read_process_running_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.reads[0].outcome is ReadOutcome.UNSUPPORTED
        assert report.reads[0].reasons == (Limitation.PROCESS_RUNNING,)

    def test_write_stdin_is_deferred(self) -> None:
        payload = load("read_write_stdin_responses.json")
        report = observe_request(payload, context=_CTX)
        assert report.reads[0].outcome is ReadOutcome.UNSUPPORTED
        assert report.reads[0].reasons == (Limitation.WRITE_STDIN_CHUNK,)


class TestWholeBundles:
    def test_single_complete_read(self) -> None:
        payload = load("read_single_complete_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        output = output_of(payload)
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        assert obs.content_span is not None
        content = output[obs.content_span.start : obs.content_span.end]
        assert content == "MUST read docs/SECURITY.md before mutation.\n"
        assert obs.bundle_digest == hashlib.sha256(content.encode()).hexdigest()
        assert obs.member_digests == (obs.bundle_digest,)
        assert obs.proven_executed == ("A.md",)
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1
        # The wrapper header stays untouched: prefix + suffix reconstruction.
        prefix = output[: obs.content_span.start]
        middle = output[obs.content_span.start : obs.content_span.end]
        suffix = output[obs.content_span.end :]
        assert prefix.endswith("Output:\n")
        assert "Process exited with code 0" in prefix
        assert output == prefix + middle + suffix

    def test_two_members_without_separators_is_one_ordered_bundle(self) -> None:
        payload = load("read_two_members_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        output = output_of(payload)
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.content_span is not None
        content = output[obs.content_span.start : obs.content_span.end]
        assert content == "AAA first file content\nBBB second file content\n"
        # One bundle digest, never per-file hashes: member digests unknown.
        assert obs.bundle_digest == hashlib.sha256(content.encode()).hexdigest()
        assert obs.member_digests == (None, None)
        assert obs.distinct_member_count == 2
        assert obs.slot_width == 2
        assert obs.proven_executed == ("A.md", "B.md")

    def test_reversed_order_changes_observed_member_order(self) -> None:
        payload = load("read_two_members_reversed_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.proven_executed == ("B.md", "A.md")
        assert obs.distinct_member_count == 2

    def test_repeated_operands_do_not_fabricate_files(self) -> None:
        payload = load("read_repeated_operand_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "A.md")
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1  # repeated operands do not inflate width
        # The combined body is the bundle; the member boundary is unproven.
        assert obs.member_digests == (None,)

    def test_unicode_crlf_bytes_are_exact(self) -> None:
        payload = load("read_unicode_crlf_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        output = output_of(payload)
        assert obs.content_span is not None
        content = output[obs.content_span.start : obs.content_span.end]
        assert content == "Caf\u00e9 r\u00e9sum\u00e9 \u2603\r\nline two\r\n"
        assert obs.bundle_digest == hashlib.sha256(content.encode("utf-8")).hexdigest()
        byte_start, byte_end = obs.content_span.to_byte_span(output)
        assert output.encode("utf-8")[byte_start:byte_end] == content.encode("utf-8")

    def test_empty_file_is_complete_empty_version(self) -> None:
        payload = load("read_empty_file_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.bundle_digest == EMPTY_SOURCE_SHA256
        assert obs.member_digests == (EMPTY_SOURCE_SHA256,)
        assert obs.content_span is not None
        assert obs.content_span.length == 0

    def test_nonzero_exit_is_not_a_bundle(self) -> None:
        payload = load("read_nonzero_exit_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.completeness is ReadOutcome.PARTIAL
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert obs.removable is False
        assert Limitation.NONZERO_EXIT in obs.reasons

    def test_truncated_output_is_not_a_bundle(self) -> None:
        payload = load("read_truncated_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.TRUNCATED
        assert obs.bundle_digest is None
        assert Limitation.TRUNCATED_OUTPUT in obs.reasons

    def test_missing_body_is_not_a_bundle(self) -> None:
        payload = load("read_missing_body_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.MISSING_BODY
        assert obs.bundle_digest is None
        assert Limitation.MISSING_OUTPUT_BODY in obs.reasons


class TestCommandAndPathNegatives:
    def test_substitution_never_executed_or_expanded(self) -> None:
        payload = load("read_substitution_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.COMMAND_SUBSTITUTION in obs.reasons
        assert obs.bundle_digest is None

    def test_fragment_command_is_not_a_whole_file(self) -> None:
        payload = load("read_fragment_responses.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.FRAGMENT_COMMAND in obs.reasons
        assert obs.bundle_digest is None

    def test_unnormalized_operand_keeps_read_unsupported(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat /elsewhere/A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\nbytes",
                },
            ]
        }
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.OUTSIDE_WORKSPACE in obs.reasons
        assert obs.bundle_digest is None
        # Requested members remain observable with their typed limitation.
        assert obs.requested_members[0].normalized is None
        assert obs.requested_members[0].limitation is Limitation.OUTSIDE_WORKSPACE

    def test_relative_without_context_is_unproven(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\nbytes",
                },
            ]
        }
        report = observe_request(payload, context=PathContext())
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.UNPROVEN_CWD in obs.reasons


class TestChatEquivalent:
    def test_chat_tool_calls_and_tool_messages_pair(self) -> None:
        payload = load("read_chat_single_complete.json")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.endpoint == "chat"
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.call_location == "$.messages[0].tool_calls[0]"
        assert obs.result_location == "$.messages[1]"
        assert obs.proven_executed == ("A.md",)


def call_payload(
    command: str = "cat A.md",
    output: str | None = None,
    tool: str = "exec_command",
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    args = arguments if arguments is not None else {"cmd": command}
    return {
        "input": [
            {
                "type": "function_call",
                "name": tool,
                "call_id": "synthetic-r1",
                "arguments": json.dumps(args),
            },
            {
                "type": "function_call_output",
                "call_id": "synthetic-r1",
                "output": output
                if output is not None
                else ("Process exited with code 0\nOutput:\nsynthetic body\n"),
            },
        ]
    }


class TestRealFormatWrapper:
    """Human handoff 6.2 real format plus the explicitly earned variant."""

    def test_handoff_chunk_id_frame_is_complete_with_exact_span(self) -> None:
        text = (
            "Chunk ID: handoff-1\n"
            "Wall time: 0.010 seconds\n"
            "Process exited with code 0\n"
            "Output:\nExact source.\n"
        )
        facts = parse_wrapper(text, ObservationBounds())
        assert facts.reasons == ()
        assert facts.exit_code == 0
        assert facts.output_present is True
        assert facts.output_span is not None
        assert text[facts.output_span.start : facts.output_span.end] == "Exact source.\n"
        assert facts.header_span is not None
        assert text[: facts.header_span.end].endswith("Output:\n")

    def test_handoff_fixture_parses_end_to_end(self) -> None:
        payload = load("read_handoff_wrapper_format_responses.json")
        report = observe_request(payload, context=_CTX)
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        output = output_of(payload)
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == (
            "MUST follow the exact source bytes.\n"
        )
        assert obs.proven_executed == ("A.md",)
        assert report.unpaired == ()

    def test_earned_chunk_id_variant_still_supported(self) -> None:
        facts = parse_wrapper(
            "Chunk Id: variant\nProcess exited with code 0\nOutput:\nx", ObservationBounds()
        )
        assert facts.reasons == ()
        assert facts.exit_code == 0

    def test_zero_byte_read_under_real_format_stays_exact(self) -> None:
        facts = parse_wrapper(
            "Chunk ID: z\nProcess exited with code 0\nOutput:\n", ObservationBounds()
        )
        assert facts.reasons == ()
        assert facts.output_span is not None
        assert facts.output_span.length == 0


class TestContradictoryWrapperStatus:
    """Repeated status fields are typed malformed — never last-field-wins."""

    def test_contradictory_exit_headers_are_malformed(self) -> None:
        facts = parse_wrapper(
            "Process exited with code 1\nProcess exited with code 0\nOutput:\nx",
            ObservationBounds(),
        )
        assert facts.reasons == (Limitation.MALFORMED_WRAPPER,)
        assert facts.output_present is False
        assert facts.exit_code is None

    def test_contradictory_exit_headers_not_complete_at_composition(self) -> None:
        payload = call_payload(
            output="Process exited with code 1\nProcess exited with code 0\nOutput:\nx"
        )
        report = observe_request(payload, context=_CTX)
        assert report.reads, "the read is still observed with its typed limitation"
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.MALFORMED_WRAPPER in obs.reasons

    def test_contradictory_truncation_headers_are_malformed(self) -> None:
        facts = parse_wrapper(
            "Truncated: true\nTruncated: false\nProcess exited with code 0\nOutput:\nx",
            ObservationBounds(),
        )
        assert facts.reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_repeated_identical_exit_header_is_malformed(self) -> None:
        # The versioned wrapper carries each status field exactly once;
        # even an identical repeat is out-of-contract, not a completion
        # proof by the last occurrence.
        facts = parse_wrapper(
            "Process exited with code 0\nProcess exited with code 0\nOutput:\nx",
            ObservationBounds(),
        )
        assert facts.reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_single_status_fields_remain_complete(self) -> None:
        facts = parse_wrapper(
            "Chunk ID: a\nWall time: 0.1 seconds\nProcess exited with code 0\n"
            "Truncated: false\nOutput:\nx",
            ObservationBounds(),
        )
        assert facts.reasons == ()
        assert facts.exit_code == 0


class TestWrapperBoundsAndGrammar:
    def test_header_line_bound_enforced_before_frame(self) -> None:
        text = "Wall time: synthetic\n" * 9 + "Process exited with code 0\nOutput:\nx"
        facts = parse_wrapper(text, ObservationBounds(max_wrapper_header_lines=8))
        assert facts.reasons == (Limitation.OVER_BOUND,)
        assert facts.output_present is False

    def test_header_line_bound_exact_limit_is_accepted(self) -> None:
        # 7 metadata lines + the exit line = 8 header lines: at the limit.
        text = "Wall time: synthetic\n" * 7 + "Process exited with code 0\nOutput:\nx"
        facts = parse_wrapper(text, ObservationBounds(max_wrapper_header_lines=8))
        assert facts.reasons == ()
        assert facts.exit_code == 0

    def test_header_line_bound_over_bound_at_composition(self) -> None:
        text = "Wall time: synthetic\n" * 9 + "Process exited with code 0\nOutput:\nx"
        payload = call_payload(output=text)
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert Limitation.OVER_BOUND in obs.reasons

    def test_unicode_digit_exit_is_typed_not_crash(self) -> None:
        facts = parse_wrapper(
            "Process exited with code \u00b2\nOutput:\nsynthetic", ObservationBounds()
        )
        assert facts.output_present is False
        assert facts.reasons  # typed limitation, never a crash
        # After a recognized header the same line is malformed wrapper.
        facts2 = parse_wrapper(
            "Chunk ID: a\nProcess exited with code \u00b2\nOutput:\nx", ObservationBounds()
        )
        assert facts2.reasons == (Limitation.MALFORMED_WRAPPER,)

    def test_excessive_digit_exit_is_typed_not_crash(self) -> None:
        facts = parse_wrapper(
            "Process exited with code " + "9" * 5000 + "\nOutput:\nsynthetic",
            ObservationBounds(),
        )
        assert facts.output_present is False
        assert facts.reasons  # bounded ASCII grammar rejects it without int()

    def test_three_digit_exit_at_range_edge_is_valid_grammar(self) -> None:
        facts = parse_wrapper("Process exited with code 255\nOutput:\nx", ObservationBounds())
        assert facts.reasons == (Limitation.NONZERO_EXIT,)
        assert facts.exit_code == 255

    def test_zero_padded_exit_is_not_the_documented_grammar(self) -> None:
        # "007" is not the documented <0-255> ASCII numeric form; the
        # bounded grammar rejects it instead of guessing a value.
        facts = parse_wrapper("Process exited with code 007\nOutput:\nx", ObservationBounds())
        assert facts.reasons != ()


class TestPerCallWorkdir:
    def test_per_call_workdir_resolves_relative_operands(self) -> None:
        payload = call_payload(arguments={"cmd": "cat A.md", "workdir": "/work/sub"})
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("sub/A.md",)
        assert obs.removable is True

    def test_per_call_workdir_outside_workspace_is_not_complete(self) -> None:
        payload = call_payload(arguments={"cmd": "cat A.md", "workdir": "/work-other"})
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is not ReadOutcome.COMPLETE
        assert obs.removable is False
        assert Limitation.OUTSIDE_WORKSPACE in obs.reasons

    def test_per_call_workdir_does_not_shadow_absolute_operands(self) -> None:
        payload = call_payload(arguments={"cmd": "cat /work/A.md", "workdir": "/work/sub"})
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md",)

    def test_relative_workdir_is_typed_not_complete(self) -> None:
        payload = call_payload(arguments={"cmd": "cat A.md", "workdir": "sub"})
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is not ReadOutcome.COMPLETE
        assert obs.removable is False

    def test_control_character_workdir_is_typed_not_crash(self) -> None:
        payload = call_payload(arguments={"cmd": "cat A.md", "workdir": "/work/s\x00ub"})
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.UNSUPPORTED_TOOL in obs.reasons


class TestToolEligibilityEvidence:
    def _declared_payload(self, tool: str) -> dict[str, Any]:
        payload = call_payload(tool=tool)
        payload["tools"] = [
            {
                "type": "function",
                "name": tool,
                "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}},
            }
        ]
        return payload

    def test_declared_unrelated_bare_cmd_tool_is_not_exec(self) -> None:
        payload = self._declared_payload("synthetic_summarizer")
        report = observe_request(payload, context=_CTX)
        assert report.reads == (), "a cmd-shaped declaration never makes a bare tool exec"
        assert report.unpaired[0].limitation is Limitation.MISMATCHED_CALL_ID

    def test_namespaced_unknown_leaf_with_declaration_is_not_exec(self) -> None:
        payload = self._declared_payload("ns/synthetic_summarizer")
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert report.unpaired[0].limitation is Limitation.MISMATCHED_CALL_ID

    def test_namespaced_known_leaf_still_supported_with_declaration(self) -> None:
        payload = self._declared_payload("ns/exec_command")
        report = observe_request(payload, context=_CTX)
        assert len(report.reads) == 1
        assert report.reads[0].outcome is ReadOutcome.COMPLETE

    def test_namespaced_known_leaf_without_declaration_is_not_exec(self) -> None:
        payload = call_payload(tool="ns/exec_command")
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()


class TestEndpointScopedPairing:
    def test_responses_call_with_chat_result_is_not_mixed(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "name": "exec_command",
                    "call_id": "synthetic-r1",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                }
            ],
            "messages": [
                {
                    "role": "tool",
                    "tool_call_id": "synthetic-r1",
                    "content": "Process exited with code 0\nOutput:\nchat body\n",
                }
            ],
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == (), "a cross-endpoint ID match is never evidence"
        assert {u.limitation for u in report.unpaired} == {
            Limitation.MISSING_CALL_RESULT,
            Limitation.MISMATCHED_CALL_ID,
        }

    def test_chat_call_with_responses_result_is_not_mixed(self) -> None:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "type": "function",
                            "id": "synthetic-r2",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat A.md"}),
                            },
                        }
                    ],
                }
            ],
            "input": [
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-r2",
                    "output": "Process exited with code 0\nOutput:\nresponses body\n",
                }
            ],
        }
        report = observe_request(payload, context=_CTX)
        assert report.reads == ()
        assert {u.limitation for u in report.unpaired} == {
            Limitation.MISSING_CALL_RESULT,
            Limitation.MISMATCHED_CALL_ID,
        }

    def test_same_endpoint_pairing_preserved_for_both_envelopes(self) -> None:
        responses = load("read_single_complete_responses.json")
        assert observe_request(responses, context=_CTX).reads[0].outcome is ReadOutcome.COMPLETE
        chat = load("read_chat_single_complete.json")
        report = observe_request(chat, context=_CTX)
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.reads[0].endpoint == "chat"


class TestMalformedUnicodeComposition:
    def test_surrogate_command_is_typed_not_crash(self) -> None:
        payload = call_payload(command="cat A\ud800.md")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert Limitation.MALFORMED_UNICODE in obs.reasons

    def test_surrogate_output_is_typed_not_crash(self) -> None:
        payload = call_payload(output="Process exited with code 0\nOutput:\nsynthetic\ud800\n")
        report = observe_request(payload, context=_CTX)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.member_digests == ()
        assert Limitation.MALFORMED_UNICODE in obs.reasons

    def test_fingerprint_is_stable_for_surrogate_payload(self) -> None:
        payload = call_payload(command="cat A\ud800.md")
        first = observe_request(payload, context=_CTX)
        second = observe_request(payload, context=_CTX)
        assert first.input_fingerprint == second.input_fingerprint
