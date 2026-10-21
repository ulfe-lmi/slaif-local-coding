"""D10 adversarial composition matrix and pure D09 partial negatives (017-m).

Public composition tests over the inert bundle-observation stage:

- identity conflicts precede read eligibility: the schema-evidenced
  call-ID inventory is eligibility-independent, so a collision with an
  eligible call ID cannot disappear through filtering; unknown/ineligible
  calls never acquire; missing/empty/malformed IDs stay observable and
  never invent an ID;
- structural causality: a result attaches to its matching call only
  when its exact numeric structural position follows the call's
  (Responses ``input`` index; Chat ``messages`` index) — never from
  lexical call IDs or JSONPath string sorting;
- the D10 pairing matrix on Responses and Chat: valid reads amid
  unrelated calls, same-ID conflicts across supported/unsupported
  families, identical/conflicting duplicates, orphan/mismatched/
  pre-call outputs, duplicate same-call results (still unsupported
  absent later earned process-chain evidence), non-monotonic IDs and
  >=10 structural positions;
- the pure unsupported/partial acquisition matrix: command
  substitution, unexecuted branches, partial readers and known
  truncated/missing/running/unknown wrappers — typed
  unsupported/partial, never complete whole-file acquisitions,
  contrasted with the exact proven empty successful output.

No shell/filesystem/network execution: observed command strings are
data.  These synthetic fixtures are not actual-client-format evidence;
D09 multi-chunk/process association remains deferred and is never
marked delivered by these negatives.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    Limitation,
    ObservationBounds,
    PathContext,
    ReadOutcome,
    observe_request,
)

_CTX = PathContext(workspace="/work")
# Unicode + CRLF: exact source slicing must preserve the exact bytes.
TEXT = "synthetic whole file\r\nline two é\n"
DIGEST = hashlib.sha256(TEXT.encode()).hexdigest()


def _wrapper(text: str = TEXT, code: int = 0, extra: str = "") -> str:
    return (
        "Chunk ID: synthetic\nWall time: 0.01 seconds\n"
        f"Process exited with code {code}\n{extra}Output:\n{text}"
    )


def _rcall(call_id: Any, name: str = "exec_command", cmd: str = "cat A.md") -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": call_id,
        "name": name,
        "arguments": json.dumps({"cmd": cmd}),
    }


def _rcall_no_id() -> dict[str, Any]:
    return {
        "type": "function_call",
        "name": "exec_command",
        "arguments": json.dumps({"cmd": "cat A.md"}),
    }


def _rresult(call_id: Any, output: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": call_id, "output": output}


def _ccall(call_id: Any, name: str = "exec_command", cmd: str = "cat A.md") -> dict[str, Any]:
    tool: dict[str, Any] = {
        "type": "function",
        "function": {"name": name, "arguments": json.dumps({"cmd": cmd})},
    }
    tool["id"] = call_id
    return {"role": "assistant", "tool_calls": [tool]}


def _ccall_no_id() -> dict[str, Any]:
    return {
        "role": "assistant",
        "tool_calls": [
            {
                "type": "function",
                "function": {"name": "exec_command", "arguments": json.dumps({"cmd": "cat A.md"})},
            }
        ],
    }


def _cresult(call_id: Any, output: str) -> dict[str, Any]:
    return {"role": "tool", "tool_call_id": call_id, "content": output}


def _run(payload: dict[str, Any]) -> Any:
    before = copy.deepcopy(payload)
    report = observe_request(payload, context=_CTX)
    assert payload == before, "observer mutated its input"
    return report


def _complete(report: Any) -> list[Any]:
    return [
        r for r in report.reads if r.removable or r.bundle_digest is not None or r.proven_executed
    ]


def _assert_exact_read(obs: Any, expected_text: str = TEXT) -> None:
    assert obs.outcome is ReadOutcome.COMPLETE
    assert obs.completeness is ReadOutcome.COMPLETE
    assert obs.removable is True
    assert obs.bundle_digest == hashlib.sha256(expected_text.encode()).hexdigest()
    assert obs.content_span is not None
    assert obs.proven_executed == ("A.md",)
    assert obs.distinct_member_count == 1
    assert obs.slot_width == 1
    # Exactly one operand proves the member boundary: the member digest
    # equals the content digest.
    assert obs.member_digests == (hashlib.sha256(expected_text.encode()).hexdigest(),)


class TestIdentityConflictPrecedesEligibility:
    """Requirement 1: ID conflicts are inventoried before eligibility."""

    def test_responses_unknown_call_id_conflict_hides_nothing(self) -> None:
        unknown = _rcall("conflict", name="unrelated_function")
        call = _rcall("conflict")
        report = _run({"input": [unknown, call, _rresult("conflict", _wrapper())]})
        assert _complete(report) == []
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "conflict", Limitation.DUPLICATE_CALL_ID),
            ("$.input[1]", "conflict", Limitation.DUPLICATE_CALL_ID),
        ]

    def test_chat_unknown_call_id_conflict_hides_nothing(self) -> None:
        unknown = _ccall("conflict", name="unrelated_function")
        call = _ccall("conflict")
        report = _run({"messages": [unknown, call, _cresult("conflict", _wrapper())]})
        assert _complete(report) == []
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.messages[0].tool_calls[0]", "conflict", Limitation.DUPLICATE_CALL_ID),
            ("$.messages[1].tool_calls[0]", "conflict", Limitation.DUPLICATE_CALL_ID),
        ]

    def test_conflict_across_supported_families(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("fam", name="exec_command"),
                    _rcall("fam", name="shell_command"),
                    _rresult("fam", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert len(report.unpaired) == 2
        assert {u.limitation for u in report.unpaired} == {Limitation.DUPLICATE_CALL_ID}

    def test_conflicting_duplicate_calls_same_name(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("dup", cmd="cat A.md"),
                    _rcall("dup", cmd="cat B.md"),
                    _rresult("dup", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert len(report.unpaired) == 2
        assert {u.limitation for u in report.unpaired} == {Limitation.DUPLICATE_CALL_ID}

    def test_identical_duplicate_calls_rejected(self) -> None:
        first = _rcall("dup")
        report = _run({"input": [first, copy.deepcopy(first), _rresult("dup", _wrapper())]})
        assert _complete(report) == []
        assert len(report.unpaired) == 2
        assert {u.limitation for u in report.unpaired} == {Limitation.DUPLICATE_CALL_ID}

    def test_unknown_unique_id_does_not_poison_valid_chain(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("unrelated", name="web_search"),
                    {"role": "user", "content": "Synthetic filler"},
                    _rcall("valid"),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        # The unrelated unknown call is neither recorded nor allowed to
        # poison the separate valid chain.
        assert report.unpaired == ()

    def test_unrelated_unknown_call_result_stays_mismatched(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("unrelated", name="web_search"),
                    _rresult("unrelated", "Synthetic unrelated output"),
                    _rcall("valid"),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$.input[1]", Limitation.MISMATCHED_CALL_ID)
        ]

    def test_missing_call_id_is_observable_never_acquired(self) -> None:
        report = _run({"input": [_rcall_no_id(), _rresult("orphan", _wrapper())]})
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "", Limitation.MISSING_CALL_ID),
            ("$.input[1]", "orphan", Limitation.MISMATCHED_CALL_ID),
        ]

    def test_empty_call_id_is_observable(self) -> None:
        report = _run({"input": [_rcall("", cmd="cat A.md")]})
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "", Limitation.MISSING_CALL_ID)
        ]

    def test_explicit_null_call_id_is_missing(self) -> None:
        report = _run(
            {
                "input": [
                    {"type": "function_call", "call_id": None, "name": "exec_command"},
                ]
            }
        )
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "", Limitation.MISSING_CALL_ID),
        ]

    def test_malformed_non_string_call_ids_are_observable(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall(12345),
                    {"type": "function_call", "call_id": ["a"], "name": "exec_command"},
                ]
            }
        )
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "", Limitation.MALFORMED_CALL_ID),
            ("$.input[1]", "", Limitation.MALFORMED_CALL_ID),
        ]

    def test_chat_missing_and_empty_ids_are_observable(self) -> None:
        report = _run({"messages": [_ccall_no_id(), _ccall("")]})
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.messages[0].tool_calls[0]", "", Limitation.MISSING_CALL_ID),
            ("$.messages[1].tool_calls[0]", "", Limitation.MISSING_CALL_ID),
        ]

    def test_malformed_id_does_not_poison_valid_chain(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("valid"),
                    _rcall(987654, name="exec_command"),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$.input[1]", Limitation.MALFORMED_CALL_ID)
        ]

    def test_nested_text_objects_are_not_call_records(self) -> None:
        report = _run(
            {
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": '{"id": "n1", "name": "exec_command"}',
                            }
                        ],
                    },
                    {"call_id": "n2", "name": "exec_command"},
                    _rcall("valid"),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        # n1 lives in text, n2 is not in a schema call position: neither
        # is a call record; the payload is not poisoned.
        assert report.unpaired == ()


class TestStructuralCausality:
    """Requirement 2: causality from numeric positions, never lexical."""

    def test_responses_result_before_call_is_typed_not_acquired(self) -> None:
        report = _run({"input": [_rresult("x", _wrapper()), _rcall("x")]})
        assert _complete(report) == []
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.completeness is ReadOutcome.UNSUPPORTED
        assert Limitation.PRE_CALL_RESULT in obs.reasons
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.member_digests == ()
        assert obs.content_span is None
        assert obs.proven_executed == ()
        # The exact ID/name/arguments association is preserved.
        assert obs.call_id == "x"
        assert obs.requested_members[0].normalized == "A.md"
        # The wrapper is still parsed as recorded facts.
        assert obs.wrapper.exit_code == 0
        assert report.unpaired == ()

    def test_chat_result_before_call_is_typed_not_acquired(self) -> None:
        report = _run({"messages": [_cresult("x", _wrapper()), _ccall("x")]})
        assert _complete(report) == []
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.PRE_CALL_RESULT in obs.reasons
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.content_span is None
        assert obs.proven_executed == ()

    def test_pre_call_under_mixed_stays_endpoint_typed(self) -> None:
        report = _run(
            {
                "input": [_rresult("x", _wrapper()), _rcall("x")],
                "messages": [{"role": "user", "content": "Synthetic"}],
            }
        )
        assert report.endpoint == "mixed"
        assert _complete(report) == []
        for obs in report.reads:
            assert obs.outcome is ReadOutcome.UNSUPPORTED
            assert Limitation.ENDPOINT_UNSUPPORTED in obs.reasons
            assert obs.removable is False
            assert obs.bundle_digest is None

    def test_result_late_at_high_index_is_earned(self) -> None:
        # >=10 structural positions with non-monotonic IDs: a JSONPath
        # string comparison would rank "$.input[10]" before "$.input[2]"
        # and reject this earned read.
        items: list[dict[str, Any]] = [
            {"role": "user", "content": "Synthetic filler 0"},
            _rcall("z0", name="unrelated"),
            _rcall("id_b"),
            {"role": "user", "content": "Synthetic filler 3"},
            {"role": "user", "content": "Synthetic filler 4"},
            {"role": "user", "content": "Synthetic filler 5"},
            {"role": "user", "content": "Synthetic filler 6"},
            {"role": "user", "content": "Synthetic filler 7"},
            {"role": "user", "content": "Synthetic filler 8"},
            {"role": "user", "content": "Synthetic filler 9"},
            _rresult("id_b", _wrapper()),
        ]
        report = _run({"input": items})
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_location == "$.input[2]"
        assert complete[0].result_location == "$.input[10]"
        assert report.unpaired == ()

    def test_result_before_call_at_high_index_is_rejected(self) -> None:
        # The mirror of the case above: a string comparison would rank
        # "$.input[2]" after "$.input[10]" and wrongly attach the
        # pre-call result to the future call.
        items: list[dict[str, Any]] = [
            {"role": "user", "content": "Synthetic filler 0"},
            {"role": "user", "content": "Synthetic filler 1"},
            _rresult("id_a", _wrapper()),
            {"role": "user", "content": "Synthetic filler 3"},
            {"role": "user", "content": "Synthetic filler 4"},
            {"role": "user", "content": "Synthetic filler 5"},
            {"role": "user", "content": "Synthetic filler 6"},
            {"role": "user", "content": "Synthetic filler 7"},
            {"role": "user", "content": "Synthetic filler 8"},
            {"role": "user", "content": "Synthetic filler 9"},
            _rcall("id_a"),
        ]
        report = _run({"input": items})
        assert _complete(report) == []
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert Limitation.PRE_CALL_RESULT in obs.reasons
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.content_span is None
        assert obs.proven_executed == ()

    def test_ambiguous_chain_does_not_block_independent_valid_chain(self) -> None:
        items: list[dict[str, Any]] = [
            _rresult("amb", _wrapper()),
            _rcall("amb"),
            {"role": "user", "content": "Synthetic filler 2"},
            {"role": "user", "content": "Synthetic filler 3"},
            {"role": "user", "content": "Synthetic filler 4"},
            {"role": "user", "content": "Synthetic filler 5"},
            _rcall("ok"),
            _rresult("ok", _wrapper()),
        ]
        report = _run({"input": items})
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_id == "ok"
        pre = [o for o in report.reads if o is not complete[0]]
        assert len(pre) == 1
        assert pre[0].call_id == "amb"
        assert Limitation.PRE_CALL_RESULT in pre[0].reasons
        assert report.unpaired == ()

    def test_missing_initial_call_leaves_result_unsupported(self) -> None:
        report = _run({"input": [_rresult("ghost", _wrapper())]})
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "ghost", Limitation.MISMATCHED_CALL_ID)
        ]

    def test_chat_causality_uses_message_indices(self) -> None:
        earned = _run(
            {
                "messages": [
                    {"role": "user", "content": "Synthetic 0"},
                    {"role": "user", "content": "Synthetic 1"},
                    _ccall("c"),
                    {"role": "user", "content": "Synthetic 3"},
                    _cresult("c", _wrapper()),
                ]
            }
        )
        complete = _complete(earned)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_location == "$.messages[2].tool_calls[0]"
        assert complete[0].result_location == "$.messages[4]"

        rejected = _run(
            {
                "messages": [
                    {"role": "user", "content": "Synthetic 0"},
                    _cresult("c", _wrapper()),
                    {"role": "user", "content": "Synthetic 2"},
                    _ccall("c"),
                ]
            }
        )
        assert _complete(rejected) == []
        assert Limitation.PRE_CALL_RESULT in rejected.reads[0].reasons

    def test_non_monotonic_ids_structural_order_wins(self) -> None:
        # Lexical order of the IDs is the reverse of structural order:
        # "m" precedes "a" structurally while "a" sorts first.  Result
        # "m" follows its call (earned); result "a" precedes its call
        # (typed), regardless of the presentation order.
        items: list[dict[str, Any]] = [
            _rcall("m"),
            _rresult("a", _wrapper()),
            {"role": "user", "content": "Synthetic filler 2"},
            _rcall("a"),
            {"role": "user", "content": "Synthetic filler 4"},
            _rresult("m", _wrapper()),
        ]
        report = _run({"input": items})
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_id == "m"
        assert complete[0].call_location == "$.input[0]"
        assert complete[0].result_location == "$.input[5]"
        pre = [o for o in report.reads if o is not complete[0]]
        assert len(pre) == 1
        assert pre[0].call_id == "a"
        assert Limitation.PRE_CALL_RESULT in pre[0].reasons
        assert report.unpaired == ()


class TestD10MatrixComposition:
    """Requirement 3: matrix composition, immutability, repr privacy."""

    def test_valid_read_among_many_unrelated_calls(self) -> None:
        items: list[dict[str, Any]] = []
        for i in range(5):
            items.append(_rcall(f"unrelated-{i}", name=f"tool_{i}"))
        items.append(_rresult("unrelated-0", "Synthetic unrelated output"))
        items.append({"role": "user", "content": "Synthetic filler"})
        items.append(_rcall("the-read"))
        items.append({"role": "user", "content": "Synthetic filler 2"})
        items.append(_rresult("the-read", _wrapper()))
        report = _run({"input": items})
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        # Only the unrelated result is bookkept; the five unrelated
        # calls themselves are invisible.
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$.input[5]", Limitation.MISMATCHED_CALL_ID)
        ]
        assert complete[0].call_location == "$.input[7]"
        assert complete[0].result_location == "$.input[9]"

    def test_duplicate_results_stay_unsupported(self) -> None:
        report = _run(
            {
                "input": [
                    _rcall("multi"),
                    _rresult("multi", _wrapper("part one\n")),
                    _rresult("multi", _wrapper("part two\n")),
                ]
            }
        )
        assert _complete(report) == []
        assert len(report.unpaired) == 2
        assert {u.limitation for u in report.unpaired} == {Limitation.MULTI_CHUNK_DEFERRED}

    def test_unicode_crlf_source_slice_is_exact(self) -> None:
        report = _run({"input": [_rcall("u"), _rresult("u", _wrapper())]})
        complete = _complete(report)
        assert len(complete) == 1
        obs = complete[0]
        _assert_exact_read(obs)
        # Exact source text slice, Unicode and CRLF preserved byte-wise.
        output = _wrapper()
        assert output[obs.content_span.start : obs.content_span.end] == TEXT
        assert obs.bundle_digest == DIGEST

    def test_repr_never_echoes_source_or_command(self) -> None:
        payloads = [
            {"input": [_rresult("x", _wrapper()), _rcall("x")]},
            {
                "input": [
                    _rcall("x", name="unrelated_function"),
                    _rcall("x"),
                    _rresult("x", _wrapper()),
                ]
            },
            {"input": [_rcall("x"), _rresult("x", _wrapper())]},
        ]
        for payload in payloads:
            report = _run(payload)
            rendered = str(report)
            for obs in report.reads:
                rendered += repr(obs)
            for record in report.unpaired:
                rendered += repr(record)
            assert TEXT not in rendered
            assert "cat A.md" not in rendered
            assert "synthetic whole file" not in rendered

    def test_declared_command_bound_still_enforced(self) -> None:
        report = observe_request(
            {"input": [_rcall("b1"), _rcall("b2")]},
            context=_CTX,
            bounds=ObservationBounds(max_commands=1),
        )
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]


class TestUnsupportedAndPartialMatrix:
    """Requirement 4: pure D09 negatives — typed, never complete."""

    @staticmethod
    def _obs(cmd: str, output: str = _wrapper()) -> tuple[Any, Any]:
        report = _run({"input": [_rcall("p", cmd=cmd), _rresult("p", output)]})
        assert len(report.reads) == 1, (cmd, report.unpaired)
        return report.reads[0], report

    @classmethod
    def _assert_not_complete(cls, obs: Any, cmd: str) -> None:
        assert obs.outcome is not ReadOutcome.COMPLETE, cmd
        assert obs.removable is False, cmd
        assert obs.bundle_digest is None, cmd
        assert obs.member_digests == (), cmd
        assert obs.content_span is None or obs.removable is False, cmd
        assert obs.proven_executed == (), cmd
        assert obs.reasons != () or obs.wrapper.reasons != (), cmd

    def test_command_substitution_never_complete(self) -> None:
        for cmd in ("cat $(echo A).md", "cat `A.md`"):
            obs, _ = self._obs(cmd)
            self._assert_not_complete(obs, cmd)
            assert Limitation.COMMAND_SUBSTITUTION in obs.reasons, cmd

    def test_false_branch_never_complete(self) -> None:
        for cmd in ("false && cat A.md", "cat A.md && false"):
            obs, _ = self._obs(cmd)
            self._assert_not_complete(obs, cmd)
            assert Limitation.COMMAND_UNSUPPORTED in obs.reasons, cmd

    def test_unexecuted_conditional_never_complete(self) -> None:
        obs, _ = self._obs("if [ -f A.md ]; then cat A.md; fi")
        self._assert_not_complete(obs, "if")
        assert Limitation.COMMAND_UNSUPPORTED in obs.reasons

    def test_pipe_and_semicolon_never_complete(self) -> None:
        obs, _ = self._obs("cat A.md || cat B.md")
        self._assert_not_complete(obs, "||")
        assert Limitation.PIPE in obs.reasons
        obs, _ = self._obs("cat A.md; cat B.md")
        self._assert_not_complete(obs, ";")
        assert Limitation.MULTIPLE_COMMANDS in obs.reasons

    def test_head_is_not_a_whole_file(self) -> None:
        obs, _ = self._obs("head A.md")
        self._assert_not_complete(obs, "head")
        assert Limitation.FRAGMENT_COMMAND in obs.reasons

    def test_sed_is_not_a_whole_file(self) -> None:
        obs, _ = self._obs("sed -n '1,10p' A.md")
        self._assert_not_complete(obs, "sed")
        assert Limitation.FRAGMENT_COMMAND in obs.reasons

    def test_truncated_wrapper_never_complete(self) -> None:
        obs, _ = self._obs("cat A.md", output=_wrapper(extra="Truncated: true\n"))
        self._assert_not_complete(obs, "truncated")
        assert obs.outcome is ReadOutcome.TRUNCATED
        assert Limitation.TRUNCATED_OUTPUT in obs.wrapper.reasons

    def test_nonzero_exit_is_not_a_bundle(self) -> None:
        obs, _ = self._obs("cat A.md", output=_wrapper(code=1))
        self._assert_not_complete(obs, "nonzero")
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert Limitation.NONZERO_EXIT in obs.wrapper.reasons

    def test_missing_body_never_complete(self) -> None:
        obs, _ = self._obs("cat A.md", output="")
        self._assert_not_complete(obs, "missing body")
        assert obs.outcome is ReadOutcome.MISSING_BODY
        assert Limitation.MISSING_OUTPUT_BODY in obs.wrapper.reasons

    def test_running_wrapper_never_complete(self) -> None:
        obs, _ = self._obs("cat A.md", output="Chunk ID: synthetic\nProcess is still running\n")
        self._assert_not_complete(obs, "running")
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.PROCESS_RUNNING in obs.reasons

    def test_unknown_completion_never_complete(self) -> None:
        obs, _ = self._obs("cat A.md", output="just some plain text, no wrapper\n")
        self._assert_not_complete(obs, "unknown completion")
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.UNKNOWN_COMPLETION in obs.reasons

    def test_proven_empty_success_is_complete_empty(self) -> None:
        # The contrast: a proven exit-zero, untruncated, present output
        # with zero content bytes is a complete empty version.
        obs, _ = self._obs("cat A.md", output=_wrapper(text=""))
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        assert obs.bundle_digest == EMPTY_SOURCE_SHA256
        assert obs.member_digests == (EMPTY_SOURCE_SHA256,)
        assert obs.content_span is not None
        assert obs.content_span.length == 0
        assert obs.proven_executed == ("A.md",)
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1
