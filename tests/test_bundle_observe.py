"""Composition-level D01-D05: observe_request over combined payloads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from slaif_local_coding.constitution.bundles import (
    ENVELOPE_FORMAT,
    OBSERVER_VERSION,
    READ_GRAMMAR,
    TOOL_WRAPPER_FORMAT,
    Limitation,
    ObservationBounds,
    ObservationReport,
    OccurrenceKind,
    PathContext,
    ReadObservation,
    ReadOutcome,
    RootOccurrence,
    RootStatus,
    canonical_payload_fingerprint,
    observe_request,
)

V1 = Path(__file__).parent / "fixtures" / "cache_bundles" / "v1"
_CTX = PathContext(workspace="/work")


def load(name: str) -> dict[str, Any]:
    value = json.loads((V1 / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def combined_payload() -> dict[str, Any]:
    """One request: evidenced root plus a complete two-member cat."""

    return {
        "model": "synthetic-bundle-model",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "# AGENTS.md instructions for /work\n\n"
                            "<INSTRUCTIONS>\n"
                            "Follow ARCHITECTURE.md and docs/PROCESS.md.\n"
                            "</INSTRUCTIONS>\n"
                            "<environment_context>\n<synthetic-discarded />\n"
                            "</environment_context>"
                        ),
                    }
                ],
            },
            {
                "type": "function_call",
                "call_id": "call_combined_1",
                "name": "exec_command",
                "arguments": json.dumps({"cmd": "cat ARCHITECTURE.md docs/PROCESS.md"}),
            },
            {
                "type": "function_call_output",
                "call_id": "call_combined_1",
                "output": (
                    "Chunk Id: synthetic-chunk-c\n"
                    "Wall time: 0.020 seconds\n"
                    "Process exited with code 0\n"
                    "Output:\n"
                    "Architecture document content.\n"
                    "Process document content.\n"
                ),
            },
        ],
    }


class TestComposition:
    def test_root_and_read_are_observed_together(self) -> None:
        payload = combined_payload()
        report = observe_request(payload, context=_CTX)
        assert report.observer_version == OBSERVER_VERSION
        assert report.endpoint == "responses"
        assert report.input_fingerprint == canonical_payload_fingerprint(payload)
        # Root: evidenced directory scope with the exact source span.
        assert report.roots.status is RootStatus.OK
        root = report.roots.roots[0]
        assert root.scope_label == "/work"
        assert root.content_span is not None
        text = payload["input"][0]["content"][0]["text"]
        content = text[root.content_span.start : root.content_span.end]
        # Single-line content: the tag's line-start newline is a delimiter,
        # not source (documented versioned delimiter contract).
        assert content == "Follow ARCHITECTURE.md and docs/PROCESS.md."
        assert root.digest == hashlib.sha256(content.encode()).hexdigest()
        # Read: complete two-member bundle with unknown member digests.
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.content_span is not None
        assert obs.proven_executed == ("ARCHITECTURE.md", "docs/PROCESS.md")
        assert obs.member_digests == (None, None)
        assert obs.distinct_member_count == 2
        output = payload["input"][2]["output"]
        assert output[obs.content_span.start : obs.content_span.end] == (
            "Architecture document content.\nProcess document content.\n"
        )
        assert report.unpaired == ()

    def test_report_versions_record_parser_identity(self) -> None:
        report = observe_request(combined_payload(), context=_CTX)
        assert report.roots.envelope_format == ENVELOPE_FORMAT
        assert report.reads[0].read_grammar == READ_GRAMMAR
        assert report.reads[0].wrapper_format == TOOL_WRAPPER_FORMAT

    def test_deterministic_repeated_observation(self) -> None:
        payload = combined_payload()
        first = observe_request(payload, context=_CTX)
        second = observe_request(payload, context=_CTX)
        assert first.model_dump() == second.model_dump()

    def test_payload_is_unchanged_by_observation(self) -> None:
        payload = combined_payload()
        before = json.dumps(payload, sort_keys=True)
        observe_request(payload, context=_CTX, bounds=ObservationBounds())
        assert json.dumps(payload, sort_keys=True) == before

    def test_raw_content_never_entered_the_report(self) -> None:
        payload = combined_payload()
        report = observe_request(payload, context=_CTX)
        dump = json.dumps(report.model_dump(), ensure_ascii=True, sort_keys=True)
        assert "Architecture document content" not in dump
        assert "Process document content" not in dump
        assert "Follow ARCHITECTURE.md" not in dump
        # Scope labels and normalized path labels are observable metadata.
        assert "/work" in dump
        assert "ARCHITECTURE.md" in dump


class TestWorkspaceContextInterplay:
    def test_explicit_validated_context_normalizes_absolute_paths(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat /work/docs/A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\ndocs A\n",
                },
            ]
        }
        report = observe_request(payload, context=PathContext(workspace="/work"))
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.reads[0].proven_executed == ("docs/A.md",)

    def test_logical_root_scope_never_maps_host_paths(self) -> None:
        # The root scope label "repo" is directory identity, not a host
        # mapping: without an explicit validated context, absolute paths stay
        # unknown and relative paths stay unproven.
        payload = combined_payload()
        report = observe_request(payload, context=PathContext(workspace="repo"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        # Relative operands under a logical (non-POSIX) scope: unproven cwd;
        # an absolute operand would be unknown workspace.
        assert Limitation.UNPROVEN_CWD in obs.reasons
        absolute = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "c2",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat /work/A.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "c2",
                    "output": "Process exited with code 0\nOutput:\nbytes",
                },
            ]
        }
        report2 = observe_request(absolute, context=PathContext(workspace="repo"))
        assert Limitation.UNKNOWN_WORKSPACE in report2.reads[0].reasons

    def test_no_context_at_all_is_unproven(self) -> None:
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
        report = observe_request(payload)
        assert report.reads[0].outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.UNPROVEN_CWD in report.reads[0].reasons


class TestBoundsAtComposition:
    def test_over_bound_request_is_typed_and_finite(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "# AGENTS.md instructions for repo\n\n"
                            "<INSTRUCTIONS>\n" + "a" * 2_000_000,
                        }
                    ],
                }
            ]
        }
        report = observe_request(payload, bounds=ObservationBounds())
        assert report.roots.status is RootStatus.NO_ROOT
        assert report.roots.occurrences[0].reasons == (Limitation.OVER_BOUND,)

    def test_too_many_calls_is_typed(self) -> None:
        calls = [
            {
                "type": "function_call",
                "call_id": f"c{i}",
                "name": "exec_command",
                "arguments": json.dumps({"cmd": f"cat F{i}.md"}),
            }
            for i in range(130)
        ]
        report = observe_request(
            {"input": calls}, context=_CTX, bounds=ObservationBounds(max_commands=128)
        )
        assert report.reads == ()
        assert report.unpaired[0].limitation is Limitation.OVER_BOUND


class TestFixtureSelfIdentification:
    def test_every_fixture_is_synthetic_and_versioned(self) -> None:
        for path in sorted(V1.glob("*.json")):
            payload = load(path.name)
            meta = payload.get("_fixture")
            assert meta is not None, path.name
            assert meta["synthetic"] is True
            authority = meta["observed_format_authority"]
            # Legacy fixtures cite the codex-0.149.0 API-boundary record;
            # D09 process fixtures are SYNTHETIC-DERIVED from the pinned
            # 0.164.0 qualified AJ capture.
            assert "codex-0.149.0" in authority or "0.164.0" in authority, path.name
            # Fixtures are immutable qualified artifacts: each records the
            # observer version it was created/verified under (the /2
            # fixtures keep their /2 self-identification; 017-am fixtures
            # record /3).  The law is a known versioned lineage, not tip
            # equality.
            assert meta["parser_versions"]["observer"] in {
                "cache-bundle-observation/1",
                "cache-bundle-observation/2",
                "cache-bundle-observation/3",
            }
            assert meta["parser_versions"]["observer"].startswith("cache-bundle-observation/")
            assert meta["parser_versions"]["envelope"] == ENVELOPE_FORMAT
            assert meta["parser_versions"]["read_grammar"] == READ_GRAMMAR
            assert meta["parser_versions"]["tool_wrapper"] == TOOL_WRAPPER_FORMAT

    def test_fixture_files_parse_end_to_end(self) -> None:
        # Every read fixture yields either a typed observation or typed
        # unpaired records; nothing crashes and nothing is silently complete.
        expectations = {
            "read_single_complete_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_handoff_wrapper_format_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_two_members_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_two_members_reversed_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_repeated_operand_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_unicode_crlf_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_empty_file_responses.json": (ReadOutcome.COMPLETE, ()),
            "read_nonzero_exit_responses.json": (
                ReadOutcome.NONZERO_EXIT,
                (Limitation.NONZERO_EXIT,),
            ),
            "read_truncated_responses.json": (
                ReadOutcome.TRUNCATED,
                (Limitation.TRUNCATED_OUTPUT,),
            ),
            "read_missing_body_responses.json": (
                ReadOutcome.MISSING_BODY,
                (Limitation.MISSING_OUTPUT_BODY,),
            ),
            "read_process_running_responses.json": (
                ReadOutcome.UNSUPPORTED,
                (Limitation.PROCESS_RUNNING,),
            ),
            "read_write_stdin_responses.json": (
                ReadOutcome.UNSUPPORTED,
                (Limitation.WRITE_STDIN_CHUNK,),
            ),
            "read_substitution_responses.json": (
                ReadOutcome.UNSUPPORTED,
                (Limitation.COMMAND_SUBSTITUTION,),
            ),
            "read_fragment_responses.json": (
                ReadOutcome.UNSUPPORTED,
                (Limitation.FRAGMENT_COMMAND,),
            ),
        }
        for name, (outcome, reasons) in expectations.items():
            payload = load(name)
            report = observe_request(payload, context=_CTX)
            assert len(report.reads) == 1, name
            assert report.reads[0].outcome is outcome, name
            assert report.reads[0].reasons == reasons, name
        unpaired_expectations = {
            "read_duplicate_call_responses.json": (Limitation.DUPLICATE_CALL_ID,),
            "read_mismatched_responses.json": (Limitation.MISMATCHED_CALL_ID,),
            "read_namespace_unproven_responses.json": (Limitation.MISMATCHED_CALL_ID,),
        }
        for name, limitations in unpaired_expectations.items():
            payload = load(name)
            report = observe_request(payload, context=_CTX)
            assert report.reads == (), name
            assert tuple(sorted({u.limitation for u in report.unpaired})) == limitations, name
        proven = load("read_namespace_proven_responses.json")
        report = observe_request(proven, context=_CTX)
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        chat = load("read_chat_single_complete.json")
        report = observe_request(chat, context=_CTX)
        assert report.reads[0].outcome is ReadOutcome.COMPLETE


class TestEndpointDomainAtComposition:
    def test_mixed_envelope_is_typed_mixed_and_non_removable(self) -> None:
        payload = combined_payload()
        payload["messages"] = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": "mix-c",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "chat/OTHER.md"}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "mix-c",
                "content": "Process exited with code 0\nOutput:\nchat body\n",
            },
        ]
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "mixed"
        # Root-domain law: a mixed selection establishes no valid root from
        # the unused Responses input (supersedes the 017-c expectation that
        # root scanning stayed independent of endpoint selection): the
        # result is typed unsupported and every root-shaped occurrence is
        # demoted to non-authoritative typed evidence.
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert Limitation.UNSUPPORTED_ENDPOINT in report.roots.conflicts
        assert report.roots.roots == ()
        for occurrence in report.roots.occurrences:
            if occurrence.kind is OccurrenceKind.ROOT:
                assert occurrence.status is RootStatus.UNSUPPORTED
                assert occurrence.digest is None
                assert Limitation.UNSUPPORTED_ENDPOINT in occurrence.reasons
        # And no read is acquired from either container.
        for obs in report.reads:
            assert obs.outcome is not ReadOutcome.COMPLETE
            assert obs.removable is False
            assert obs.bundle_digest is None

    def test_explicit_endpoint_at_composition(self) -> None:
        payload = combined_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        assert report.endpoint == "responses"
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        mismatch = observe_request(payload, context=_CTX, endpoint="chat")
        assert mismatch.endpoint == "unknown"
        assert mismatch.reads == ()
        assert [u.limitation for u in mismatch.unpaired] == [Limitation.ENDPOINT_UNSUPPORTED]


def _root_text() -> str:
    return (
        "# AGENTS.md instructions for /work\n\n"
        "<INSTRUCTIONS>\n"
        "Synthetic root rule.\n"
        "</INSTRUCTIONS>"
    )


def _input_root_container() -> dict[str, Any]:
    return {"input": [{"role": "user", "content": [{"type": "input_text", "text": _root_text()}]}]}


def _chat_user_container() -> dict[str, Any]:
    return {"messages": [{"role": "user", "content": "Synthetic request"}]}


def _chat_read_container() -> dict[str, Any]:
    return {
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": "synthetic-chat",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat B.md"}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "synthetic-chat",
                "content": "Process exited with code 0\nOutput:\nSynthetic source\n",
            },
        ]
    }


def _valid_roots(report: ObservationReport) -> list[RootOccurrence]:
    return [
        r
        for r in report.roots.occurrences
        if r.kind is OccurrenceKind.ROOT and r.status is RootStatus.OK
    ]


def _complete_reads(report: ObservationReport) -> list[ReadObservation]:
    return [r for r in report.reads if r.outcome is ReadOutcome.COMPLETE and r.removable]


class TestRootDomainGating:
    """Only the actual selected Responses domain can establish a root."""

    def test_inferred_responses_root_positive_preserved(self) -> None:
        payload = _input_root_container()
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "responses"
        valid = _valid_roots(report)
        assert len(valid) == 1
        assert valid[0].scope_label == "/work"
        assert valid[0].digest is not None

    def test_explicit_responses_root_positive_preserved(self) -> None:
        payload = {**_input_root_container(), **_chat_user_container()}
        report = observe_request(payload, context=_CTX, endpoint="responses")
        assert report.endpoint == "responses"
        assert len(_valid_roots(report)) == 1

    def test_explicit_chat_cannot_mint_root_from_unused_input(self) -> None:
        payload = {**_input_root_container(), **_chat_user_container()}
        report = observe_request(payload, context=_CTX, endpoint="chat")
        assert report.endpoint == "chat"
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert _valid_roots(report) == []
        # Non-authoritative typed evidence is preserved without authority.
        demoted = [o for o in report.roots.occurrences if o.kind is OccurrenceKind.ROOT]
        assert len(demoted) == 1
        assert demoted[0].status is RootStatus.UNSUPPORTED
        assert demoted[0].digest is None
        assert demoted[0].scope_label == "/work"
        assert demoted[0].content_span is not None
        assert Limitation.UNSUPPORTED_ENDPOINT in demoted[0].reasons

    def test_mixed_without_endpoint_cannot_mint_root(self) -> None:
        payload = {**_input_root_container(), **_chat_user_container()}
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "mixed"
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert _valid_roots(report) == []

    def test_invalid_explicit_endpoint_cannot_mint_root(self) -> None:
        payload = _input_root_container()
        report = observe_request(payload, context=_CTX, endpoint="invalid")
        assert report.endpoint == "unknown"
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert _valid_roots(report) == []
        assert [u.limitation for u in report.unpaired] == [Limitation.ENDPOINT_UNSUPPORTED]

    def test_malformed_root_in_unused_container_stays_typed(self) -> None:
        text = "# AGENTS.md instructions for /work\n\n<INSTRUCTIONS>\nnever closed"
        payload = {
            "input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}],
            **_chat_user_container(),
        }
        report = observe_request(payload, context=_CTX, endpoint="chat")
        assert _valid_roots(report) == []
        occurrence = report.roots.occurrences[0]
        assert occurrence.kind is OccurrenceKind.ROOT
        assert occurrence.status is RootStatus.UNSUPPORTED
        assert occurrence.reasons == (
            Limitation.UNCLOSED_TAIL,
            Limitation.UNSUPPORTED_ENDPOINT,
        )

    def test_chat_only_payload_root_result_unchanged(self) -> None:
        report = observe_request(_chat_user_container(), context=_CTX)
        assert report.endpoint == "chat"
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert report.roots.conflicts == (Limitation.UNSUPPORTED_ENDPOINT,)
        assert report.roots.occurrences == ()
        assert report.roots.scanned_items == 0

    def test_string_input_with_chat_messages_is_mixed_not_chat(self) -> None:
        # An input string is a valid Responses API form: with messages also
        # present, inference must not call this unambiguous Chat.
        payload = {
            "input": "Synthetic Responses input",
            **_chat_read_container(),
        }
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "mixed"
        assert _complete_reads(report) == []
        assert _valid_roots(report) == []

    def test_string_input_alone_is_responses_without_root_container(self) -> None:
        payload = {"input": "Synthetic Responses input"}
        report = observe_request(payload, context=_CTX)
        assert report.endpoint == "responses"
        assert report.roots.status is RootStatus.NO_ROOT
        assert report.roots.occurrences == ()
        assert report.roots.scanned_items == 0
        assert report.reads == ()
        assert report.unpaired == ()

    def test_input_not_mutated_under_root_gating(self) -> None:
        payload = {**_input_root_container(), **_chat_user_container()}
        before = json.dumps(payload, sort_keys=True)
        observe_request(payload, context=_CTX)
        observe_request(payload, context=_CTX, endpoint="chat")
        assert json.dumps(payload, sort_keys=True) == before
