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
- wire-family and complete-inventory boundaries (017-n/017-o): the
  Responses ``custom_tool_call`` identity participates in the call
  inventory alongside ``function_call`` (exact colliding IDs make the
  ambiguous eligible chain typed/non-acquiring in both collision
  orderings, repeated or conflicting records included; a unique
  unrelated opaque custom call neither poisons nor echoes; a custom
  named like a supported tool still never acquires; no generic
  unknown-family recognition), ``max_commands``/``max_outputs`` bound
  the complete relevant inventory (unsupported names, opaque custom
  records, missing/empty/malformed IDs, invalid result IDs) while
  streaming — the bound is decided **before** any record tuple,
  location string, ID map or typed diagnostic is retained (bounded
  regression allocation proof on large prebuilt inventories at limit
  one, with at-limit useful reads keeping exact digest/span/member/
  width), fixed non-acquiring ``OVER_BOUND``, at-limit and one-over on
  Responses and Chat (including many ``tool_calls`` in one assistant
  message) and a late collision beyond any retained prefix — scoped to
  the selected domain under explicit endpoint selection, and
  absent/null/empty and non-string result IDs (Responses
  ``function_call_output``; Chat ``role=tool``) are fixed typed
  non-echoing unpaired limitations that never invent, hash, attach or
  acquire, with separate well-formed chains remaining useful within
  the total limits;
- private-ID representation (017-o): exact internal call/result IDs
  stay usable while operational ``str``/``repr`` of report/read/
  unpaired objects never echo private ID values (synthetic canaries
  only) — the observable no-ID state, fixed enums, counts, locations
  and digests remain visible;
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
import tracemalloc
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    PRIVATE_ID_PLACEHOLDER,
    Limitation,
    ObservationBounds,
    PathContext,
    ReadOutcome,
    UnpairedRecord,
    observe_reads,
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


def _rcustom(
    call_id: Any, name: str = "unrelated_custom", input_value: str = "opaque synthetic input"
) -> dict[str, Any]:
    return {
        "type": "custom_tool_call",
        "call_id": call_id,
        "name": name,
        "input": input_value,
    }


def _rresult_bad_id(value: Any, key_present: bool = True) -> dict[str, Any]:
    item: dict[str, Any] = {"type": "function_call_output", "output": _wrapper()}
    if key_present:
        item["call_id"] = value
    return item


def _cresult_bad_id(value: Any, key_present: bool = True) -> dict[str, Any]:
    item: dict[str, Any] = {"role": "tool", "content": _wrapper()}
    if key_present:
        item["tool_call_id"] = value
    return item


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


class TestWireFamilyInventoryAndBounds:
    """017-n: wire-family inventory, complete-inventory bounds, result IDs.

    - the Responses ``custom_tool_call`` identity is inventoried
      alongside ``function_call`` (eligibility stays restricted: the
      custom family never acquires, whatever its name, and its opaque
      input is never captured or reinterpreted);
    - ``max_commands``/``max_outputs`` bound the **complete** relevant
      inventory (unsupported names, opaque custom records,
      missing/empty/malformed IDs, invalid result IDs) before any
      identity map or diagnostic is retained: a fixed non-acquiring
      ``OVER_BOUND``, never a truncated acquisition missing a later
      collision;
    - absent/null/empty and non-string result IDs are fixed typed
      non-echoing unpaired limitations, never invented, hashed,
      attached or acquired.

    No shell/filesystem/network execution: observed command strings and
    opaque inputs are data.
    """

    # -- Requirement 1: custom_tool_call in the call inventory ----------

    def test_custom_collision_custom_first_never_acquires(self) -> None:
        report = _run(
            {
                "input": [
                    _rcustom("coll"),
                    _rcall("coll"),
                    _rresult("coll", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "coll", Limitation.DUPLICATE_CALL_ID),
            ("$.input[1]", "coll", Limitation.DUPLICATE_CALL_ID),
        ]

    def test_custom_collision_call_first_never_acquires(self) -> None:
        # Both collision orderings: the later custom occurrence is just
        # as blocking as the earlier one (never first-match).
        report = _run(
            {
                "input": [
                    _rcall("coll"),
                    _rcustom("coll"),
                    _rresult("coll", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert report.reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", "coll", Limitation.DUPLICATE_CALL_ID),
            ("$.input[1]", "coll", Limitation.DUPLICATE_CALL_ID),
        ]

    def test_repeated_custom_collisions_all_observable(self) -> None:
        first = _rcustom("dupc")
        report = _run(
            {
                "input": [
                    first,
                    copy.deepcopy(first),
                    _rcall("dupc"),
                    _rresult("dupc", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$.input[0]", Limitation.DUPLICATE_CALL_ID),
            ("$.input[1]", Limitation.DUPLICATE_CALL_ID),
            ("$.input[2]", Limitation.DUPLICATE_CALL_ID),
        ]

    def test_custom_collision_among_conflicting_calls(self) -> None:
        report = _run(
            {
                "input": [
                    _rcustom("cx"),
                    _rcall("cx", cmd="cat A.md"),
                    _rcall("cx", cmd="cat B.md"),
                    _rresult("cx", _wrapper()),
                ]
            }
        )
        assert _complete(report) == []
        assert report.reads == ()
        assert len(report.unpaired) == 3
        assert {u.limitation for u in report.unpaired} == {Limitation.DUPLICATE_CALL_ID}

    def test_custom_named_like_supported_tool_never_acquires(self) -> None:
        # Family gates acquisition: even an exact supported name on a
        # custom_tool_call earns nothing, and its wrapper-shaped result
        # is only a mismatched result, never a read.
        report = _run(
            {
                "input": [
                    _rcustom("named", name="exec_command"),
                    _rresult("named", _wrapper()),
                ]
            }
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[1]", "named", Limitation.MISMATCHED_CALL_ID)
        ]

    def test_custom_unique_does_not_poison_valid_chain(self) -> None:
        report = _run(
            {
                "input": [
                    _rcustom("unrelated-custom"),
                    _rcall("the-read"),
                    _rresult("the-read", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_location == "$.input[1]"
        assert complete[0].result_location == "$.input[2]"
        # The unique unrelated opaque custom call is neither recorded
        # nor allowed to poison the separate valid chain.
        assert report.unpaired == ()

    def test_custom_opaque_input_never_echoed(self) -> None:
        canary = "CANARY-OPAQUE-INPUT-9f3c1"
        report = _run(
            {
                "input": [
                    _rcustom("opq", input_value=canary),
                    _rcall("ok"),
                    _rresult("ok", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        rendered = str(report)
        for obs in report.reads:
            rendered += repr(obs)
        for record in report.unpaired:
            rendered += repr(record)
        assert canary not in rendered
        # The opaque input is never reinterpreted as a shell/source
        # oracle: it is not a requested member anywhere.
        for obs in report.reads:
            for member in obs.requested_members:
                assert canary not in (member.raw or "")

    def test_custom_shape_in_text_or_untyped_item_is_not_a_record(self) -> None:
        report = _run(
            {
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": '{"type": "custom_tool_call", "call_id": "t1"}',
                            }
                        ],
                    },
                    # No type field: not a schema call position.
                    {"call_id": "t2", "name": "unrelated_custom"},
                    _rcall("valid"),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    # -- Requirement 2: complete-inventory bounds -----------------------

    def test_at_limit_unknown_and_valid_still_acquires(self) -> None:
        # Two relevant call records (one unsupported, one eligible) at
        # exactly max_commands: the useful unknown+valid control holds.
        report = observe_request(
            {
                "input": [
                    _rcall("other", name="unrelated_function"),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_one_over_with_unknown_calls_is_fixed_over_bound(self) -> None:
        report = observe_request(
            {
                "input": [
                    _rcall("other", name="unrelated_function"),
                    _rcall("third", name="unrelated_function"),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$", "", Limitation.OVER_BOUND)
        ]

    def test_malformed_call_ids_count_toward_bound(self) -> None:
        report = observe_request(
            {
                "input": [
                    _rcall([]),
                    _rcall({}),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_missing_call_ids_count_toward_bound(self) -> None:
        report = observe_request(
            {
                "input": [
                    _rcall_no_id(),
                    _rcall_no_id(),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_custom_records_count_toward_bound(self) -> None:
        report = observe_request(
            {
                "input": [
                    _rcustom("c1"),
                    _rcustom("c2"),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_chat_at_limit_many_tool_calls_one_message(self) -> None:
        # Two tool_calls inside ONE assistant message at exactly
        # max_commands: the valid read still acquires.
        report = observe_request(
            {
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "u1",
                                "type": "function",
                                "function": {
                                    "name": "unrelated_function",
                                    "arguments": "{}",
                                },
                            },
                            {
                                "id": "read",
                                "type": "function",
                                "function": {
                                    "name": "exec_command",
                                    "arguments": json.dumps({"cmd": "cat A.md"}),
                                },
                            },
                        ],
                    },
                    _cresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_chat_one_over_many_tool_calls_one_message(self) -> None:
        # Three tool_calls inside ONE assistant message, one over the
        # limit: fixed OVER_BOUND, nothing acquired.
        report = observe_request(
            {
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "u1",
                                "type": "function",
                                "function": {
                                    "name": "unrelated_function",
                                    "arguments": "{}",
                                },
                            },
                            {
                                "id": "u2",
                                "type": "function",
                                "function": {
                                    "name": "unrelated_function",
                                    "arguments": "{}",
                                },
                            },
                            {
                                "id": "read",
                                "type": "function",
                                "function": {
                                    "name": "exec_command",
                                    "arguments": json.dumps({"cmd": "cat A.md"}),
                                },
                            },
                        ],
                    },
                    _cresult("read", _wrapper()),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_late_collision_beyond_retained_prefix(self) -> None:
        # A collision at index 5 with a limit of 4: a truncated
        # inventory that only retained the first four call records
        # would have acquired the eligible call at index 3.  The
        # complete inventory is bounded first, so nothing acquires.
        items = [_rcall(f"unrelated-{i}", name=f"tool_{i}") for i in range(3)]
        items.append(_rcall("late-read"))
        items.append(_rresult("late-read", _wrapper()))
        items.append(_rcall("late-read", name="unrelated_function"))
        report = observe_request(
            {"input": items},
            context=_CTX,
            bounds=ObservationBounds(max_commands=4),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_outputs_bound_counts_invalid_result_ids(self) -> None:
        # One valid plus one invalid-ID result record is already one
        # over max_outputs=1: fixed OVER_BOUND, nothing acquired.
        report = observe_request(
            {
                "input": [
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                    _rresult_bad_id(["x"]),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_outputs=1),
        )
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_outputs_at_limit_including_defects_still_acquires(self) -> None:
        report = observe_request(
            {
                "input": [
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                    _rresult_bad_id({"x": 1}),
                ]
            },
            context=_CTX,
            bounds=ObservationBounds(max_outputs=2),
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[2]", "", Limitation.MALFORMED_RESULT_ID)
        ]

    def test_explicit_selection_scopes_responses_bound(self) -> None:
        # The ignored Chat container is over the bound; the selected
        # Responses domain is within it: only the selected domain
        # contributes, so the valid read acquires.
        report = observe_request(
            {
                "input": [_rcall("read"), _rresult("read", _wrapper())],
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": f"u{i}",
                                "type": "function",
                                "function": {
                                    "name": "unrelated_function",
                                    "arguments": "{}",
                                },
                            }
                            for i in range(3)
                        ],
                    },
                    _cresult("u0", _wrapper()),
                ],
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
            endpoint="responses",
        )
        assert report.endpoint == "responses"
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_explicit_selection_scopes_chat_bound(self) -> None:
        # Mirror: the ignored Responses container is over the bound;
        # the selected Chat domain is within it.
        report = observe_request(
            {
                "input": [_rcall(f"u{i}", name="unrelated_function") for i in range(3)]
                + [_rcall("read"), _rresult("read", _wrapper())],
                "messages": [
                    _ccall("chat-read"),
                    _cresult("chat-read", _wrapper()),
                ],
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=2),
            endpoint="chat",
        )
        assert report.endpoint == "chat"
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_mixed_input_bounded_across_inspected_domains(self) -> None:
        # No explicit endpoint: both containers are inspected, and the
        # combined inventory is over the bound: fixed OVER_BOUND, no
        # acquisition from either container.
        report = observe_request(
            {
                "input": [
                    _rcall("u1", name="unrelated_function"),
                    _rcall("u2", name="unrelated_function"),
                    _rcall("read"),
                    _rresult("read", _wrapper()),
                ],
                "messages": [_ccall("chat-read"), _cresult("chat-read", _wrapper())],
            },
            context=_CTX,
            bounds=ObservationBounds(max_commands=3),
        )
        assert report.endpoint == "mixed"
        assert report.reads == ()
        assert _complete(report) == []
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_over_long_container_is_fixed_over_bound(self) -> None:
        # The scan itself is bounded by the existing item bound before
        # any record is retained.
        filler = [_rcall(f"unrelated-{i}", name=f"tool_{i}") for i in range(5)]
        report = observe_request(
            {"input": filler},
            context=_CTX,
            bounds=ObservationBounds(max_items=4),
        )
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    # -- Requirement 3: result-ID observability -------------------------

    def test_responses_result_id_defects_are_typed(self) -> None:
        cases = [
            (_rresult_bad_id(None), Limitation.MISSING_RESULT_ID),
            (_rresult_bad_id(""), Limitation.MISSING_RESULT_ID),
            (_rresult_bad_id([], key_present=True), Limitation.MALFORMED_RESULT_ID),
            (_rresult_bad_id({"x": 1}), Limitation.MALFORMED_RESULT_ID),
            (_rresult_bad_id(7), Limitation.MALFORMED_RESULT_ID),
            (_rresult_bad_id(3.5), Limitation.MALFORMED_RESULT_ID),
            (_rresult_bad_id(True), Limitation.MALFORMED_RESULT_ID),
            (_rresult_bad_id("ignored", key_present=False), Limitation.MISSING_RESULT_ID),
        ]
        for item, limitation in cases:
            report = _run({"input": [item]})
            assert report.reads == ()
            assert _complete(report) == []
            assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
                ("$.input[0]", "", limitation)
            ], item

    def test_chat_result_id_defects_are_typed(self) -> None:
        cases = [
            (_cresult_bad_id(None), Limitation.MISSING_RESULT_ID),
            (_cresult_bad_id(""), Limitation.MISSING_RESULT_ID),
            (_cresult_bad_id([1]), Limitation.MALFORMED_RESULT_ID),
            (_cresult_bad_id({"x": 1}), Limitation.MALFORMED_RESULT_ID),
            (_cresult_bad_id(0), Limitation.MALFORMED_RESULT_ID),
            (_cresult_bad_id("ignored", key_present=False), Limitation.MISSING_RESULT_ID),
        ]
        for item, limitation in cases:
            report = _run({"messages": [item]})
            assert report.reads == ()
            assert _complete(report) == []
            assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
                ("$.messages[0]", "", limitation)
            ], item

    def test_malformed_result_never_attached_hashed_or_acquired(self) -> None:
        # The malformed-ID result is observable, but the independent
        # well-formed chain stays useful within the total limits and is
        # never disturbed (no MULTI_CHUNK, no attachment, no ID
        # invention).
        report = _run(
            {
                "input": [
                    _rcall("valid"),
                    _rresult_bad_id({"secret": "CANARY-RESULT-ID-77ab2"}),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert complete[0].call_location == "$.input[0]"
        assert complete[0].result_location == "$.input[2]"
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[1]", "", Limitation.MALFORMED_RESULT_ID)
        ]
        rendered = str(report) + repr(report.reads) + repr(report.unpaired)
        assert "CANARY-RESULT-ID-77ab2" not in rendered

    def test_result_id_defects_coexist_with_mismatch_typing(self) -> None:
        # Existing duplicate/missing/mismatched typing is preserved
        # alongside the new result-ID defects.
        report = _run(
            {
                "input": [
                    _rcall("valid"),
                    _rresult("orphan", _wrapper()),
                    _rresult_bad_id(None),
                    _rresult("valid", _wrapper()),
                ]
            }
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert [(u.location, u.call_id, u.limitation) for u in report.unpaired] == [
            ("$.input[2]", "", Limitation.MISSING_RESULT_ID),
            ("$.input[1]", "orphan", Limitation.MISMATCHED_CALL_ID),
        ]


class TestInventoryAllocationAndIdRepresentation:
    """017-o: pre-retention bounded inventory work and private-ID reprs.

    - complete relevant call/result inventory bounds are enforced while
      streaming — before any record tuple, location string, ID map or
      typed diagnostic is retained: large prebuilt Responses calls,
      nested Chat calls, Responses results and Chat results at limit
      one are a fixed non-acquiring ``OVER_BOUND`` whose measured
      allocation stays under the generous regression ceiling (inputs,
      imports and full-payload fingerprinting excluded), while at-limit
      useful reads keep their exact digest/span/member/width proof and
      one-over/late-collision/invalid-ID/ignored-domain/mixed shapes
      keep their typed behavior;
    - exact internal call/result IDs stay usable while operational
      ``str``/``repr`` of report/read/unpaired objects never echo
      private ID values (synthetic canaries only): the observable
      no-ID state, fixed enums, counts, locations and digests remain
      visible.
    """

    _TOKEN = "SYNTH-PRIVATE-CALL-ID-017o"
    # Generous independent allocation regression ceiling (bytes) at
    # inventory budget one; not a total-process RSS guarantee.
    _CEILING = 2 * 1024 * 1024

    @staticmethod
    def _read_pair() -> tuple[str, dict[str, Any], dict[str, Any]]:
        text = "synthetic allocation body é\r\n"
        return text, _rcall("alloc-control"), _rresult("alloc-control", _wrapper(text))

    @staticmethod
    def _assistant_with_tools(ids: list[str]) -> dict[str, Any]:
        tools: list[dict[str, Any]] = []
        for call_id in ids:
            tool: dict[str, Any] = {
                "type": "function",
                "function": {"name": "exec_command", "arguments": json.dumps({"cmd": "cat A.md"})},
            }
            tool["id"] = call_id
            tools.append(tool)
        return {"role": "assistant", "tool_calls": tools}

    @staticmethod
    def _assert_over_bound(unpaired: Any) -> None:
        assert unpaired == (
            UnpairedRecord(location="$", call_id="", limitation=Limitation.OVER_BOUND),
        )

    def _measured_reads(
        self,
        payload: dict[str, Any],
        bounds: ObservationBounds,
        endpoint: str,
    ) -> tuple[Any, Any, int]:
        before = copy.deepcopy(payload)
        tracemalloc.start()
        try:
            reads, unpaired = observe_reads(payload, _CTX, bounds, selected_endpoint=endpoint)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert payload == before, "observer mutated its input"
        return reads, unpaired, peak

    # -- Requirement 1: pre-retention bounded allocation/work ----------

    def test_large_inventories_bounded_before_retention(self) -> None:
        big = 50_000
        bound = ObservationBounds(max_items=100_000, max_commands=1, max_outputs=1)
        unknown = _rcall("u", name="unrelated_function")
        chat_tool: dict[str, Any] = {
            "type": "function",
            "id": "u",
            "function": {"name": "unrelated_function", "arguments": "{}"},
        }
        cases = [
            ({"input": [unknown] * big}, "responses"),
            ({"messages": [{"role": "assistant", "tool_calls": [chat_tool] * big}]}, "chat"),
            ({"input": [_rresult("u", "")] * big}, "responses"),
            ({"messages": [_cresult("u", "")] * big}, "chat"),
        ]
        for payload, endpoint in cases:
            reads, unpaired, peak = self._measured_reads(payload, bound, endpoint)
            assert reads == ()
            self._assert_over_bound(unpaired)
            assert peak < self._CEILING, (endpoint, peak)

    def test_public_entry_fixed_over_bound_large_inventory(self) -> None:
        payload = {"input": [_rcall("u", name="unrelated_function")] * 50_000}
        before = copy.deepcopy(payload)
        report = observe_request(
            payload,
            context=_CTX,
            bounds=ObservationBounds(max_items=100_000, max_commands=1, max_outputs=1),
            endpoint="responses",
        )
        assert payload == before
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_at_limit_useful_keeps_exact_proof_responses_and_chat(self) -> None:
        text, call, result = self._read_pair()
        bound = ObservationBounds(max_commands=1, max_outputs=1)
        payloads = [
            ({"input": [call, result]}, "responses"),
            (
                {
                    "messages": [
                        _ccall("alloc-control"),
                        _cresult("alloc-control", _wrapper(text)),
                    ]
                },
                "chat",
            ),
        ]
        for payload, endpoint in payloads:
            reads, unpaired, peak = self._measured_reads(payload, bound, endpoint)
            assert unpaired == ()
            assert len(reads) == 1
            obs = reads[0]
            assert obs.removable is True
            assert obs.bundle_digest == hashlib.sha256(text.encode()).hexdigest()
            assert obs.content_span is not None
            assert obs.proven_executed == ("A.md",)
            assert obs.distinct_member_count == 1
            assert obs.slot_width == 1
            assert peak < self._CEILING, (endpoint, peak)

    def test_one_over_responses_and_nested_chat(self) -> None:
        bound = ObservationBounds(max_commands=2, max_outputs=8)
        responses_payload = {
            "input": [
                _rcall("u1", name="unrelated_function"),
                _rcall("u2", name="unrelated_function"),
                _rcall("ok"),
                _rresult("ok", _wrapper()),
            ]
        }
        reads, unpaired, _ = self._measured_reads(responses_payload, bound, "responses")
        assert reads == ()
        self._assert_over_bound(unpaired)
        chat_payload = {"messages": [self._assistant_with_tools(["a", "b", "c"])]}
        reads, unpaired, _ = self._measured_reads(chat_payload, bound, "chat")
        assert reads == ()
        self._assert_over_bound(unpaired)

    def test_invalid_ids_count_toward_pre_retention_bound(self) -> None:
        command_bound = ObservationBounds(max_commands=2)
        missing = _rcall_no_id()
        payload = {
            "input": [
                missing,
                missing,
                _rcall("ok"),
                _rresult("ok", _wrapper()),
            ]
        }
        reads, unpaired, _ = self._measured_reads(payload, command_bound, "responses")
        assert reads == ()
        self._assert_over_bound(unpaired)
        output_bound = ObservationBounds(max_outputs=2)
        bad = _rresult_bad_id(None)
        payload = {
            "input": [
                bad,
                bad,
                _rresult("ok", _wrapper()),
            ]
        }
        reads, unpaired, _ = self._measured_reads(payload, output_bound, "responses")
        assert reads == ()
        self._assert_over_bound(unpaired)

    def test_ignored_domain_inventory_is_not_counted(self) -> None:
        big = 50_000
        text, call, result = self._read_pair()
        bound = ObservationBounds(max_items=100_000, max_commands=1, max_outputs=1)
        unknown_tool: dict[str, Any] = {
            "type": "function",
            "id": "u",
            "function": {"name": "unrelated_function", "arguments": "{}"},
        }
        responses_selection = {
            "input": [call, result],
            "messages": [{"role": "assistant", "tool_calls": [unknown_tool] * big}],
        }
        reads, unpaired, peak = self._measured_reads(responses_selection, bound, "responses")
        assert unpaired == ()
        assert len(reads) == 1 and reads[0].removable is True
        assert peak < self._CEILING
        chat_selection = {
            "input": [_rcall("u", name="unrelated_function")] * big,
            "messages": [_ccall("c-ok"), _cresult("c-ok", _wrapper(text))],
        }
        reads, unpaired, peak = self._measured_reads(chat_selection, bound, "chat")
        assert unpaired == ()
        assert len(reads) == 1 and reads[0].removable is True
        assert peak < self._CEILING

    def test_mixed_aggregate_counts_both_domains(self) -> None:
        payload = {
            "input": [_rcall("x"), _rresult("x", _wrapper())],
            "messages": [_ccall("y"), _cresult("y", _wrapper())],
        }
        report = observe_request(
            payload, context=_CTX, bounds=ObservationBounds(max_commands=1, max_outputs=8)
        )
        assert report.endpoint == "mixed"
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_late_collision_at_limit_and_one_over_beyond_prefix(self) -> None:
        text, call, result = self._read_pair()
        custom = _rcustom("alloc-control", name="exec_command")
        bound = ObservationBounds(max_commands=3, max_outputs=1)
        at_limit = {"input": [call, result, _rcall("u", name="unrelated_function"), custom]}
        reads, unpaired, _ = self._measured_reads(at_limit, bound, "responses")
        assert reads == ()
        assert [(u.location, u.call_id, u.limitation) for u in unpaired] == [
            ("$.input[0]", "alloc-control", Limitation.DUPLICATE_CALL_ID),
            ("$.input[3]", "alloc-control", Limitation.DUPLICATE_CALL_ID),
        ]
        one_over = {
            "input": [
                call,
                result,
                _rcall("u", name="unrelated_function"),
                custom,
                _rcall("v", name="unrelated_function"),
            ]
        }
        reads, unpaired, _ = self._measured_reads(one_over, bound, "responses")
        assert reads == ()
        self._assert_over_bound(unpaired)
        del text

    # -- Requirement 2: non-echoing operational representations -------

    @staticmethod
    def _assert_non_echoing(report: Any, token: str) -> None:
        for value in (report, *report.reads, *report.unpaired):
            assert token not in repr(value)
            assert token not in str(value)

    def test_paired_ids_internal_exact_repr_private(self) -> None:
        token = self._TOKEN
        text = "synthetic repr body\n"
        payloads = [
            {"input": [_rcall(token), _rresult(token, _wrapper(text))]},
            {"messages": [_ccall(token), _cresult(token, _wrapper(text))]},
        ]
        for payload in payloads:
            report = _run(payload)
            complete = _complete(report)
            assert len(complete) == 1
            assert complete[0].call_id == token  # internal field stays exact
            assert complete[0].removable is True
            self._assert_non_echoing(report, token)
            assert PRIVATE_ID_PLACEHOLDER in repr(report.reads[0])
            # fixed enums/counts/digests remain observable
            assert report.endpoint in repr(report)
            assert '"bundle_digest"' in repr(report)

    def test_orphan_result_ids_internal_exact_repr_private(self) -> None:
        token = self._TOKEN
        payloads = [
            {"input": [_rresult(token, _wrapper())]},
            {"messages": [_cresult(token, _wrapper())]},
        ]
        for payload in payloads:
            report = _run(payload)
            assert len(report.unpaired) == 1
            record = report.unpaired[0]
            assert record.limitation is Limitation.MISMATCHED_CALL_ID
            assert record.call_id == token  # internal field stays exact
            assert record.call_id == token and token not in repr(record)
            self._assert_non_echoing(report, token)
            assert PRIVATE_ID_PLACEHOLDER in repr(record)
            # the structural location stays observable
            assert '"location"' in repr(record)

    def test_duplicate_call_ids_internal_exact_repr_private(self) -> None:
        token = self._TOKEN
        payloads = [
            {"input": [_rcall(token), _rcall(token), _rresult(token, _wrapper())]},
            {
                "messages": [
                    _ccall(token),
                    _ccall(token),
                    _cresult(token, _wrapper()),
                ]
            },
        ]
        for payload in payloads:
            report = _run(payload)
            assert _complete(report) == []
            assert len(report.unpaired) == 2
            for record in report.unpaired:
                assert record.limitation is Limitation.DUPLICATE_CALL_ID
                assert record.call_id == token  # internal field stays exact
            self._assert_non_echoing(report, token)
            assert PRIVATE_ID_PLACEHOLDER in repr(report.unpaired[0])

    def test_missing_result_ids_internal_exact_repr_private(self) -> None:
        token = self._TOKEN
        payloads = [
            {"input": [_rcall(token)]},
            {"messages": [_ccall(token)]},
        ]
        for payload in payloads:
            report = _run(payload)
            assert _complete(report) == []
            assert len(report.unpaired) == 1
            record = report.unpaired[0]
            assert record.limitation is Limitation.MISSING_CALL_RESULT
            assert record.call_id == token  # internal field stays exact
            self._assert_non_echoing(report, token)
            assert PRIVATE_ID_PLACEHOLDER in repr(record)

    def test_repr_keeps_enums_counts_and_empty_id_state(self) -> None:
        report = _run({"input": [_rcall_no_id(), _rresult("orphan-x", _wrapper())]})
        assert len(report.unpaired) == 2
        missing = [u for u in report.unpaired if u.limitation is Limitation.MISSING_CALL_ID][0]
        mismatched = [u for u in report.unpaired if u.limitation is Limitation.MISMATCHED_CALL_ID][
            0
        ]
        assert missing.call_id == ""  # observable no-ID state stays exact
        assert '"call_id":""' in repr(missing)
        assert '"missing_call_id"' in repr(missing)
        assert '"location":"$.input[0]"' in repr(missing)
        assert '"mismatched_call_id"' in repr(mismatched)
        assert '"observer_version"' in repr(report)
        assert '"input_fingerprint"' in repr(report)


class TestNestedScanBounds:
    """017-p: per-container ``max_items`` bound on nested ``tool_calls``.

    - each inspected assistant ``tool_calls`` list is individually
      length-tested against ``max_items`` BEFORE it is iterated (counting
      every raw entry regardless of schema, type or ID); ``max_items`` is
      a per-container bound, never a total across all lists — the
      at-limit nested list (4 entries + tool result under ``max_items`` 4)
      still earns the useful read;
    - one-over nested arrays (unknown/non-schema entries, with or without
      a valid call inside) are the fixed single non-acquiring
      ``OVER_BOUND`` — no truncated-prefix acquisition;
    - non-assistant ``tool_calls`` fields and the ignored domain under
      explicit endpoint selection remain uninspected; mixed input keeps
      the fixed ``OVER_BOUND`` priority;
    - malformed JSON ``type`` fields (list/dict/null/number) never crash
      and are safely ignored while the valid read is still earned;
    - the early-work claim is proven with measured bounded allocation on
      a large prebuilt nested list (no fragile time/RSS-total assertions,
      no full-payload fingerprinting dependency).
    """

    _CEILING = 2 * 1024 * 1024  # generous regression ceiling (bytes)

    @staticmethod
    def _noise() -> dict[str, Any]:
        return {"opaque": True}

    @staticmethod
    def _cc_tool(call_id: str = "valid") -> dict[str, Any]:
        tool: dict[str, Any] = {
            "type": "function",
            "function": {"name": "exec_command", "arguments": json.dumps({"cmd": "cat A.md"})},
        }
        tool["id"] = call_id
        return tool

    @staticmethod
    def _assistant(tools: list[dict[str, Any]]) -> dict[str, Any]:
        return {"role": "assistant", "tool_calls": tools}

    @staticmethod
    def _run_bounded(
        payload: dict[str, Any],
        bounds: ObservationBounds,
        endpoint: str | None = None,
    ) -> Any:
        before = copy.deepcopy(payload)
        report = observe_request(payload, context=_CTX, bounds=bounds, endpoint=endpoint)
        assert payload == before, "observer mutated its input"
        return report

    def test_nested_at_limit_useful(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        messages = [
            self._assistant([self._noise(), self._noise(), self._noise(), self._cc_tool()]),
            _cresult("valid", _wrapper()),
        ]
        report = self._run_bounded({"messages": messages}, bound)
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_nested_one_over_non_schema_over_bound(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        payload = {
            "messages": [
                self._assistant(
                    [self._noise(), self._noise(), self._noise(), self._noise(), self._noise()]
                ),
                _ccall("valid"),
                _cresult("valid", _wrapper()),
            ]
        }
        report = self._run_bounded(payload, bound)
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_nested_one_over_with_valid_call_no_truncated_prefix(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        tools = [self._noise(), self._noise(), self._cc_tool(), self._noise(), self._noise()]
        payload = {"messages": [self._assistant(tools), _cresult("valid", _wrapper())]}
        report = self._run_bounded(payload, bound)
        assert report.reads == ()  # the in-list valid call never acquires
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    def test_explicit_selected_domain_ignores_nested_overflow(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        overflow = self._assistant([self._noise() for _ in range(5)])
        report = self._run_bounded(
            {"input": [_rcall("valid"), _rresult("valid", _wrapper())], "messages": [overflow]},
            bound,
            endpoint="responses",
        )
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])
        assert report.unpaired == ()

    def test_mixed_nested_overflow_fixed_over_bound(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        overflow = self._assistant([self._noise() for _ in range(5)])
        report = self._run_bounded(
            {"input": [_rcall("valid"), _rresult("valid", _wrapper())], "messages": [overflow]},
            bound,
        )
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]

    @pytest.mark.parametrize("bad_type", [[], {}, None, 1], ids=["list", "dict", "null", "number"])
    def test_malformed_nested_types_ignored_and_safe(self, bad_type: Any) -> None:
        tool = self._cc_tool()
        tool["type"] = bad_type
        payload = {
            "messages": [
                self._assistant([tool, self._cc_tool()]),
                _cresult("valid", _wrapper()),
            ]
        }
        report = self._run_bounded(payload, ObservationBounds())
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])

    def test_non_assistant_tool_calls_uninspected(self) -> None:
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        payload = {
            "messages": [
                {"role": "user", "tool_calls": [self._noise() for _ in range(50)]},
                _ccall("valid"),
                _cresult("valid", _wrapper()),
            ]
        }
        report = self._run_bounded(payload, bound)
        complete = _complete(report)
        assert len(complete) == 1
        _assert_exact_read(complete[0])

    def test_per_container_not_total_across_lists(self) -> None:
        # Outer messages list: 4 entries; each nested tool_calls list: 2.
        # 8 inspected entries in total — a total-across-lists reading of
        # max_items would OVER_BOUND here; the per-container law observes
        # both lists normally.
        bound = ObservationBounds(max_items=4, max_commands=2, max_outputs=2)
        payload = {
            "messages": [
                self._assistant([self._cc_tool("one"), self._noise()]),
                self._assistant([self._cc_tool("two"), self._noise()]),
                _cresult("one", _wrapper()),
                _cresult("two", _wrapper()),
            ]
        }
        report = self._run_bounded(payload, bound)
        complete = _complete(report)
        assert len(complete) == 2  # 2 per nested list, at-limit individually
        for obs in complete:
            _assert_exact_read(obs)

    def test_nested_over_bound_early_work_measured(self) -> None:
        big = 50_000
        bound = ObservationBounds(max_items=1024, max_commands=1, max_outputs=1)
        payload = {"messages": [self._assistant([self._noise() for _ in range(big)])]}
        before = copy.deepcopy(payload)
        tracemalloc.start()
        try:
            report = observe_request(payload, context=_CTX, bounds=bound, endpoint="chat")
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert payload == before, "observer mutated its input"
        assert report.reads == ()
        assert [(u.location, u.limitation) for u in report.unpaired] == [
            ("$", Limitation.OVER_BOUND)
        ]
        assert peak < self._CEILING, peak
