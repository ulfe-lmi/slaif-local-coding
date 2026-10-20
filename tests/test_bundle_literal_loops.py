"""Bounded literal loops (D07) — parser and public composition.

Synthetic pure-observation tests: no shell is executed, no filesystem is
touched, and every command string under test is data.  The loop grammar is
exercised directly (``parse_literal_loop``) and at the composition level
(``observe_request`` over full wrapper frames).  The loop parser is inert:
nothing here is wired into the legacy request execution path.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    LOOP_GRAMMAR,
    READ_GRAMMAR,
    READ_PLAN_GRAMMAR,
    Limitation,
    LoopParse,
    LoopStatementKind,
    ObservationBounds,
    ObservationReport,
    PathContext,
    ReadOutcome,
    observe_request,
    parse_literal_loop,
)

_CTX = PathContext(workspace="/work")
_BOUNDS = ObservationBounds()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def loop(
    command: str,
    context: PathContext = _CTX,
    max_operands: int = 32,
    max_command_chars: int = 4096,
) -> LoopParse:
    return parse_literal_loop(command, context, max_command_chars, max_operands, 256)


def members(plan_parse: LoopParse) -> tuple[str | None, ...]:
    return tuple(m.normalized for m in plan_parse.requested_members)


def _loop_payload(
    command: str,
    output: str,
    exit_code: int = 0,
    extra_args: dict[str, Any] | None = None,
    truncated: bool = False,
    wrapper: str | None = None,
) -> dict[str, Any]:
    """One Responses request: exec_command call plus wrapper result frame."""

    arguments: dict[str, Any] = {"cmd": command}
    if extra_args is not None:
        arguments.update(extra_args)
    if wrapper is not None:
        body = wrapper
    else:
        body = (
            f"Chunk ID: synthetic\nWall time: 0.01 seconds\nProcess exited with code {exit_code}\n"
        )
        if truncated:
            body += "Truncated: true\n"
        body += "Output:\n" + output
    return {
        "input": [
            {
                "type": "function_call",
                "call_id": "synthetic-loop-1",
                "name": "exec_command",
                "arguments": json.dumps(arguments),
            },
            {"type": "function_call_output", "call_id": "synthetic-loop-1", "output": body},
        ]
    }


def _observe(payload: dict[str, Any], **kwargs: Any) -> ObservationReport:
    before = copy.deepcopy(payload)
    report = observe_request(payload, context=_CTX, **kwargs)
    assert payload == before, "observer mutated its input"
    return report


class TestHumanForms:
    """The human 6.2 loop forms: membership is finite parsed data."""

    def test_unguarded_echo_form_membership_is_recognized(self) -> None:
        result = loop('for f in A.md B.md; do echo "=== $f ==="; cat "$f"; done')
        assert result.is_loop_attempt is True
        assert result.grammar == LOOP_GRAMMAR
        assert result.complete is True
        assert result.loop_variable == "f"
        assert result.list_values == ("A.md", "B.md")
        assert result.has_echo is True
        assert result.all_cats_guarded is False
        assert [s.kind for s in result.statements] == [
            LoopStatementKind.ECHO,
            LoopStatementKind.CAT,
        ]
        assert members(result) == ("A.md", "B.md")
        # Accurate typed execution/attribution limitations, non-removable:
        # no valid bundle digest where proof is missing.
        assert Limitation.LOOP_ITERATION_UNPROVEN in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_unguarded_template_form_membership_is_recognized(self) -> None:
        result = loop('for d in alpha beta; do cat "policies/$d/AGENTS.md"; done')
        assert result.is_loop_attempt is True
        assert result.complete is True
        assert result.loop_variable == "d"
        assert result.list_values == ("alpha", "beta")
        assert result.has_echo is False
        assert result.all_cats_guarded is False
        assert members(result) == ("policies/alpha/AGENTS.md", "policies/beta/AGENTS.md")
        assert result.reasons == (Limitation.LOOP_ITERATION_UNPROVEN,)

    def test_guarded_echoless_forms_are_earned(self) -> None:
        for command, expected in [
            ('for f in A.md B.md; do cat "$f" || exit 1; done', ("A.md", "B.md")),
            (
                'for d in alpha beta; do cat "policies/$d/AGENTS.md" || exit 1; done',
                ("policies/alpha/AGENTS.md", "policies/beta/AGENTS.md"),
            ),
        ]:
            result = loop(command)
            assert result.complete is True
            assert result.all_cats_guarded is True
            assert result.has_echo is False
            assert result.reasons == ()
            assert members(result) == expected
            assert result.command_digest == _digest(command)

    def test_unguarded_echo_form_is_not_removable_at_composition(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do echo "=== $f ==="; cat "$f"; done',
            "=== A.md ===\nsrcA\n=== B.md ===\nsrcB\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.read_grammar == LOOP_GRAMMAR
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.completeness is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        # Deterministic requested members are exposed; requested paths are
        # not proven-executed paths.
        assert [m.normalized for m in obs.requested_members] == ["A.md", "B.md"]
        assert Limitation.LOOP_ITERATION_UNPROVEN in obs.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons
        # Echo labels are ordinary actual output, not source bytes: the
        # mixed output is exposed as the raw attributable region but never
        # swallowed into a digested source bundle.
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == (
            "=== A.md ===\nsrcA\n=== B.md ===\nsrcB\n"
        )

    def test_unguarded_template_form_is_not_removable_at_composition(self) -> None:
        payload = _loop_payload(
            'for d in alpha beta; do cat "policies/$d/AGENTS.md"; done', "<alpha><beta>"
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert [m.normalized for m in obs.requested_members] == [
            "policies/alpha/AGENTS.md",
            "policies/beta/AGENTS.md",
        ]
        # A final exit 0 does not prove every earlier iteration succeeded.
        assert obs.reasons == (Limitation.LOOP_ITERATION_UNPROVEN,)

    def test_guarded_echo_body_is_outer_boundary_unproven(self) -> None:
        # All cats guarded (per-iteration proven) but the body echo still
        # interleaves printed labels: the source region is not attributable.
        payload = _loop_payload(
            'for f in A.md B.md; do echo "=== $f ==="; cat "$f" || exit 1; done',
            "=== A.md ===\nsrcA\n=== B.md ===\nsrcB\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)
        assert [m.normalized for m in obs.requested_members] == ["A.md", "B.md"]


class TestGuardedPositiveComposition:
    """All-success guarded variants: one ordered whole-source bundle."""

    def test_guarded_loop_is_one_complete_ordered_bundle(self) -> None:
        payload = _loop_payload('for f in A.md B.md; do cat "$f" || exit 1; done', "srcA\nsrcB\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.read_grammar == LOOP_GRAMMAR
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.completeness is ReadOutcome.COMPLETE
        assert obs.removable is True
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.distinct_member_count == 2
        assert obs.slot_width == 2
        assert obs.member_digests == (None, None)
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == "srcA\nsrcB\n"
        assert obs.bundle_digest == _digest("srcA\nsrcB\n")

    def test_guarded_template_loop_proves_ordered_policy_files(self) -> None:
        payload = _loop_payload(
            'for d in alpha beta; do cat "policies/$d/AGENTS.md" || exit 1; done',
            "<alphaPolicy><betaPolicy>",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("policies/alpha/AGENTS.md", "policies/beta/AGENTS.md")
        assert obs.bundle_digest == _digest("<alphaPolicy><betaPolicy>")

    def test_reversed_membership_preserves_observed_order(self) -> None:
        command = 'for f in B.md A.md; do cat "$f" || exit 1; done'
        payload = _loop_payload(command, "Bfirst\nAsecond\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("B.md", "A.md")
        assert obs.bundle_digest == _digest("Bfirst\nAsecond\n")

    def test_duplicate_membership_preserves_order_and_distinct_width(self) -> None:
        payload = _loop_payload('for f in A.md A.md; do cat "$f" || exit 1; done', "aa\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "A.md")
        assert obs.distinct_member_count == 1
        assert obs.slot_width == 1
        assert obs.member_digests == (None,)
        assert obs.bundle_digest == _digest("aa\n")

    def test_single_member_loop_proves_member_digest(self) -> None:
        payload = _loop_payload('for f in A.md; do cat "$f" || exit 1; done', "onlyA\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md",)
        assert obs.member_digests == (_digest("onlyA\n"),)
        assert obs.bundle_digest == _digest("onlyA\n")

    def test_zero_byte_source_is_complete_empty_version(self) -> None:
        payload = _loop_payload('for f in A.md; do cat "$f" || exit 1; done', "")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        assert obs.bundle_digest == EMPTY_SOURCE_SHA256
        assert obs.member_digests == (EMPTY_SOURCE_SHA256,)

    def test_unicode_crlf_source_bytes_are_exact(self) -> None:
        content = "éé\r\nünïcode\r\n"
        payload = _loop_payload('for f in A.md B.md; do cat "$f" || exit 1; done', content)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        byte_start, byte_end = obs.content_span.to_byte_span(output)
        assert output.encode("utf-8")[byte_start:byte_end] == content.encode("utf-8")
        assert obs.bundle_digest == _digest(content)

    def test_multi_operand_iteration_preserves_interleaved_order(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" next.md || exit 1; done', "A\nn\nB\nn\n"
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "next.md", "B.md", "next.md")
        assert obs.distinct_member_count == 3
        assert obs.bundle_digest == _digest("A\nn\nB\nn\n")


class TestLoopWorkdirAndWorkspace:
    """Expanded filenames resolve lexically in the client domain."""

    def test_per_call_workdir_resolves_expanded_relative_members(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" || exit 1; done',
            "sA\nsB\n",
            extra_args={"workdir": "/work/other"},
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("other/A.md", "other/B.md")

    def test_absolute_template_under_workspace_is_earned(self) -> None:
        result = loop('for f in A.md; do cat "/work/$f/x.md" || exit 1; done')
        assert result.complete is True
        assert members(result) == ("A.md/x.md",)

    def test_sibling_workspace_escape_is_typed(self) -> None:
        result = loop('for f in /work-other/A.md; do cat "$f" || exit 1; done')
        assert result.complete is True
        assert result.reasons == (Limitation.OUTSIDE_WORKSPACE,)
        assert members(result) == (None,)
        payload = _loop_payload('for f in /work-other/A.md; do cat "$f" || exit 1; done', "x")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None

    def test_absolute_template_outside_workspace_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "/etc/$f/passwd" || exit 1; done')
        assert result.reasons == (Limitation.OUTSIDE_WORKSPACE,)
        assert members(result) == (None,)

    def test_ambiguous_cwd_without_workspace_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f" || exit 1; done', context=PathContext())
        assert result.complete is True
        assert result.reasons == (Limitation.UNPROVEN_CWD,)
        assert members(result) == (None, None)

    def test_traversal_template_segment_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "../$f.md" || exit 1; done')
        assert result.reasons == (Limitation.LOOP_TEMPLATE_UNSUPPORTED,)


class TestWrapperNegatives:
    """Wrapper status is separate from loop structure; no false bundles."""

    def test_nonzero_guarded_loop_proves_no_earlier_source(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" || exit 1; done', "srcA\n", exit_code=1
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.completeness is ReadOutcome.PARTIAL
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        # Do not infer which earlier file succeeded; no silent trimming.
        assert [m.normalized for m in obs.requested_members] == ["A.md", "B.md"]
        assert Limitation.NONZERO_EXIT in obs.reasons

    def test_truncated_guarded_loop_is_partial(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" || exit 1; done', "srcA\n", truncated=True
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.TRUNCATED
        assert obs.completeness is ReadOutcome.PARTIAL
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.TRUNCATED_OUTPUT in obs.reasons

    def test_missing_body_is_missing_body(self) -> None:
        payload = _loop_payload('for f in A.md B.md; do cat "$f" || exit 1; done', "", wrapper="")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.MISSING_BODY
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.MISSING_OUTPUT_BODY in obs.reasons

    def test_unknown_completion_is_typed(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" || exit 1; done',
            "",
            wrapper="plain unstructured output\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.completeness is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.content_span is None
        assert Limitation.UNKNOWN_COMPLETION in obs.reasons

    def test_process_running_is_typed(self) -> None:
        payload = _loop_payload(
            'for f in A.md B.md; do cat "$f" || exit 1; done',
            "x",
            wrapper="Process is still running\nOutput:\nx\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert Limitation.PROCESS_RUNNING in obs.reasons

    def test_malformed_unicode_content_is_typed_without_digest(self) -> None:
        payload = _loop_payload('for f in A.md; do cat "$f" || exit 1; done', "synthetic\ud800")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.MALFORMED_UNICODE in obs.reasons

    def test_source_status_lookalike_stays_source(self) -> None:
        payload = _loop_payload(
            'for f in A.md; do cat "$f" || exit 1; done',
            "Process exited with code 9\nOutput:\nSynthetic\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.bundle_digest == _digest("Process exited with code 9\nOutput:\nSynthetic\n")


class TestVariableLaw:
    """Only the earned ordinary names are literal local bindings."""

    def test_other_ordinary_names_are_typed(self) -> None:
        for name in ("g", "x", "file", "F"):
            result = loop(f'for {name} in A.md; do cat "${name}"; done')
            assert result.complete is False, name
            assert result.loop_variable is None
            assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons
            assert members(result) == ()

    def test_shell_special_dynamic_readonly_names_are_typed(self) -> None:
        for name in ("RANDOM", "SECONDS", "LINENO", "_"):
            result = loop(f'for {name} in A.md; do cat "${name}"; done')
            assert result.complete is False, name
            assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons
            assert members(result) == ()

    def test_unknown_variable_reference_is_typed(self) -> None:
        for ref in ("g", "file", "HOME"):
            result = loop(f'for f in A.md; do cat "${ref}"; done')
            assert result.complete is False, ref
            assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons
            assert members(result) == ()

    def test_special_variable_reference_is_typed(self) -> None:
        for ref in ("RANDOM", "SECONDS", "LINENO", "_"):
            result = loop(f'for f in A.md; do cat "${ref}"; done')
            assert result.complete is False, ref
            assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons
            assert members(result) == ()

    def test_echo_reference_to_other_variable_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do echo "x $g y"; cat "$f"; done')
        assert result.complete is False
        assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons

    def test_quoted_variable_name_is_typed(self) -> None:
        result = loop('for "f" in A.md; do cat "$f"; done')
        assert result.complete is False
        assert Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons


class TestTemplateLaw:
    """Supported double-quoted filename templates, nothing else."""

    def test_partial_segment_reference_is_typed(self) -> None:
        for template in ('"pre$f.md"', '"$f.md"', '"a$b"'):
            result = loop(f"for f in A.md; do cat {template}; done")
            assert result.complete is False, template
            assert Limitation.LOOP_TEMPLATE_UNSUPPORTED in result.reasons or (
                Limitation.LOOP_VARIABLE_UNSUPPORTED in result.reasons
            )

    def test_repeated_reference_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "$f/$f"; done')
        assert result.complete is False
        assert Limitation.LOOP_TEMPLATE_UNSUPPORTED in result.reasons

    def test_unquoted_variable_is_substitution_not_template(self) -> None:
        result = loop("for f in A.md B.md; do cat $f; done")
        assert result.complete is False
        assert Limitation.COMMAND_SUBSTITUTION in result.reasons
        assert members(result) == ()

    def test_dotted_dot_template_segment_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "policies/../$f/x"; done')
        assert result.complete is False
        assert Limitation.LOOP_TEMPLATE_UNSUPPORTED in result.reasons

    def test_whitespace_template_segment_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "policies/$f x/A.md"; done')
        assert result.complete is False
        assert Limitation.LOOP_TEMPLATE_UNSUPPORTED in result.reasons


class TestCatOptionStdinSemantics:
    """Quoting never disables cat option/terminator/stdin parsing."""

    def test_option_like_list_value_never_a_member(self) -> None:
        result = loop('for f in -n; do cat "$f"; done')
        assert result.complete is True
        assert result.reasons == (
            Limitation.LOOP_ITERATION_UNPROVEN,
            Limitation.COMMAND_UNSUPPORTED,
        )
        assert members(result) == ()

    def test_stdin_list_value_is_typed(self) -> None:
        result = loop('for f in -; do cat "$f"; done')
        assert result.complete is True
        assert Limitation.STDIN_OPERAND in result.reasons
        assert members(result) == ()

    def test_terminator_list_value_read_no_file(self) -> None:
        result = loop('for f in --; do cat "$f" || exit 1; done')
        assert result.complete is True
        assert result.all_cats_guarded is True
        assert result.reasons == (Limitation.COMMAND_EMPTY,)
        assert members(result) == ()

    def test_terminator_statement_with_literal_after(self) -> None:
        # After the terminator, dash-leading expansions are literal file
        # labels, not options.
        result = loop('for f in -- -x; do cat -- "$f"; done')
        assert result.complete is True
        assert members(result) == ("--", "-x")
        assert Limitation.LOOP_ITERATION_UNPROVEN in result.reasons

    def test_substituted_terminator_is_consumed_once(self) -> None:
        # The substituted expansion is the first cooked ``--``: it is the
        # option terminator (consumed once); the later literal ``--`` is a
        # file label and ``B.md`` a plain member — the single-command cat
        # law applied in operand order per iteration.
        result = loop('for f in --; do cat "$f" -- B.md || exit 1; done')
        assert result.complete is True
        assert result.all_cats_guarded is True
        assert result.reasons == ()
        assert members(result) == ("--", "B.md")

    def test_substituted_terminator_is_earned_at_composition(self) -> None:
        payload = _loop_payload('for f in --; do cat "$f" -- B.md || exit 1; done', "src--\nsrcB\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("--", "B.md")
        assert obs.bundle_digest is not None

    def test_literal_terminator_before_template(self) -> None:
        result = loop('for f in A.md B.md; do cat -- "$f" || exit 1; done')
        assert result.complete is True
        assert result.all_cats_guarded is True
        assert result.reasons == ()
        assert members(result) == ("A.md", "B.md")

    def test_substituted_stdin_is_typed(self) -> None:
        result = loop('for f in -; do cat "$f" B.md || exit 1; done')
        assert result.complete is True
        assert result.all_cats_guarded is True
        assert result.reasons == (Limitation.STDIN_OPERAND,)
        assert members(result) == ("B.md",)

    def test_terminator_only_iteration_is_typed_at_composition(self) -> None:
        payload = _loop_payload('for f in -- A.md; do cat "$f" || exit 1; done', "srcA\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.COMMAND_EMPTY in obs.reasons
        assert [m.normalized for m in obs.requested_members] == ["A.md"]


class TestGuardLaw:
    """The exact per-iteration guard; false and late guards are typed."""

    def test_exit_zero_guard_is_not_equivalent(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f" || exit 0; done')
        assert result.complete is False
        assert Limitation.LOOP_GUARD_UNSUPPORTED in result.reasons

    def test_other_exit_literals_are_typed(self) -> None:
        for code in ("2", "11", "01"):
            result = loop(f'for f in A.md; do cat "$f" || exit {code}; done')
            assert result.complete is False, code
            assert Limitation.LOOP_GUARD_UNSUPPORTED in result.reasons

    def test_non_exit_guard_is_typed(self) -> None:
        for tail in ("true", "break", "exit"):
            result = loop(f'for f in A.md; do cat "$f" || {tail}; done')
            assert result.complete is False, tail
            assert Limitation.LOOP_GUARD_UNSUPPORTED in result.reasons

    def test_guard_after_the_loop_is_not_equivalent(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f"; done || exit 1')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_single_pipe_is_not_a_guard(self) -> None:
        result = loop('for f in A.md; do cat "$f" | exit 1; done')
        assert result.complete is False
        assert Limitation.PIPE in result.reasons
        assert members(result) == ()


class TestLoopFormNegatives:
    """Unsupported loop forms stay typed, never guessed."""

    def test_nested_loop_is_typed(self) -> None:
        result = loop('for f in A.md; do for x in B.md; do cat "$f"; done; done')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_while_until_if_case_are_typed(self) -> None:
        for keyword in ("while", "until", "if", "case"):
            result = loop(f'for f in A.md; do {keyword} true; do cat "$f"; done; done')
            assert result.complete is False, keyword
            assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_break_continue_are_typed(self) -> None:
        for keyword in ("break", "continue"):
            result = loop(f"for f in A.md; do {keyword}; done")
            assert result.complete is False, keyword
            assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_glob_list_is_typed(self) -> None:
        result = loop('for f in *.md; do cat "$f"; done')
        assert result.complete is False
        assert Limitation.GLOB_UNPROVEN in result.reasons
        assert members(result) == ()

    def test_substitution_list_is_typed(self) -> None:
        result = loop('for f in $(ls); do cat "$f"; done')
        assert result.complete is False
        assert Limitation.COMMAND_SUBSTITUTION in result.reasons
        assert members(result) == ()

    def test_quoted_example_list_value_is_typed(self) -> None:
        result = loop("for f in 'A.md'; do cat '$f'; done")
        assert result.complete is False
        assert Limitation.LOOP_TEMPLATE_UNSUPPORTED in result.reasons or (
            Limitation.QUOTED_OPERAND in result.reasons
        )

    def test_comment_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f" # note; done')
        assert result.complete is False
        assert Limitation.COMMENT_PRESENT in result.reasons

    def test_heredoc_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "$f" <<EOF; done')
        assert result.complete is False
        assert Limitation.REDIRECTION in result.reasons or (
            Limitation.LOOP_FORM_UNSUPPORTED in result.reasons
        )

    def test_redirection_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f" > out; done')
        assert result.complete is False
        assert Limitation.REDIRECTION in result.reasons

    def test_write_command_in_body_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do echo hi > "$f"; done')
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_branch_in_body_is_typed(self) -> None:
        result = loop('for f in A.md; do if [ -f "$f" ]; then cat "$f"; fi; done')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_head_tail_sed_bodies_are_fragments(self) -> None:
        for executable in ("head", "tail", "sed"):
            result = loop(f'for f in A.md; do {executable} "$f"; done')
            assert result.complete is False, executable
            assert Limitation.FRAGMENT_COMMAND in result.reasons

    def test_unknown_executable_is_typed(self) -> None:
        result = loop('for f in A.md; do less "$f"; done')
        assert result.complete is False
        assert Limitation.FRAGMENT_COMMAND in result.reasons

    def test_missing_closure_is_typed(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f";')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_adjacent_quote_list_word_is_typed(self) -> None:
        # One shell word mixing an unquoted fragment with a quoted region
        # is not a clean list literal (the shared quote law); no member is
        # fabricated from either fragment.
        for command in (
            'for f in A".md" B.md; do cat "$f" || exit 1; done',
            "for f in A'.md' B.md; do cat \"$f\" || exit 1; done",
        ):
            result = loop(command)
            assert result.complete is False, command
            assert Limitation.QUOTED_OPERAND in result.reasons, command
            assert members(result) == ()

    def test_adjacent_quote_template_is_typed(self) -> None:
        # Quoting-mixed operand words are not earned templates or clean
        # literals.
        for command in (
            'for f in A.md B.md; do cat "$f"".md" || exit 1; done',
            'for f in A.md B.md; do cat pre"$f" || exit 1; done',
        ):
            result = loop(command)
            assert result.complete is False, command
            assert Limitation.QUOTED_OPERAND in result.reasons, command
            assert members(result) == ()

    def test_adjacent_quote_echo_target_is_typed(self) -> None:
        result = loop('for f in A.md; do echo "=== $f ==="X; done')
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_separator_after_quote_stays_separate(self) -> None:
        # A metacharacter word never joins its quoted neighbor: the
        # standard guarded form with a quoted list value still earns.
        result = loop('for f in "A.md"; do cat "$f" || exit 1; done')
        assert result.complete is True
        assert result.all_cats_guarded is True
        assert result.reasons == ()
        assert members(result) == ("A.md",)

    def test_tokens_after_done_are_typed(self) -> None:
        result = loop('for f in A.md B.md; do cat "$f"; done && cat X.md')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_missing_in_keyword_is_typed(self) -> None:
        result = loop('for f A.md B.md; do cat "$f"; done')
        assert result.complete is False
        assert Limitation.LOOP_FORM_UNSUPPORTED in result.reasons

    def test_loop_with_no_cat_is_not_a_read(self) -> None:
        result = loop('for f in A.md B.md; do echo "x $f"; done')
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert members(result) == ()

    def test_non_loop_command_is_outside_the_domain(self) -> None:
        result = loop("cat A.md && cat B.md")
        assert result.is_loop_attempt is False
        assert result.complete is False


class TestListBounds:
    """Empty and over-bound lists are typed; exact limits are earned."""

    def test_empty_iteration_list_is_not_a_read(self) -> None:
        for command in ('for f in; do cat "$f"; done', 'for f in ; do cat "$f"; done'):
            result = loop(command)
            assert result.complete is False, command
            assert Limitation.COMMAND_EMPTY in result.reasons
            assert members(result) == ()

    def test_over_bound_list_is_typed(self) -> None:
        command = "for f in " + " ".join(f"F{i}.md" for i in range(3))
        command += '; do cat "$f" || exit 1; done'
        result = loop(command, max_operands=2)
        assert result.complete is False
        assert Limitation.OVER_BOUND in result.reasons

    def test_exactly_at_limit_list_is_earned(self) -> None:
        command = "for f in " + " ".join(f"F{i}.md" for i in range(2))
        command += '; do cat "$f" || exit 1; done'
        result = loop(command, max_operands=2)
        assert result.complete is True
        assert members(result) == ("F0.md", "F1.md")

    def test_whole_loop_operand_budget_does_not_multiply(self) -> None:
        # Two iterations x two operands = four expanded operands: over the
        # shared bound of three, typed even though each part is in bound.
        result = loop('for f in A.md B.md; do cat "$f" x.md || exit 1; done', max_operands=3)
        assert result.complete is False
        assert Limitation.OVER_BOUND in result.reasons
        result = loop('for f in A.md B.md; do cat "$f" || exit 1; done', max_operands=2)
        assert result.complete is True
        assert members(result) == ("A.md", "B.md")

    def test_over_bound_command_is_typed(self) -> None:
        result = loop('for f in A.md; do cat "$f"; done', max_command_chars=12)
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons


class TestLoopIdentityAndComposition:
    """Grammar identity, endpoint/domain, call-ID and ordering law."""

    def test_every_loop_observation_carries_loop_grammar(self) -> None:
        guarded = 'for f in A.md; do cat "$f" || exit 1; done'
        cases: list[tuple[str, dict[str, Any]]] = [
            # complete
            (guarded, {}),
            # unguarded
            ('for f in A.md; do cat "$f"; done', {}),
            # nonzero
            (guarded, {"exit_code": 1}),
            # truncated
            (guarded, {"truncated": True}),
            # structurally unsupported
            ('for g in A.md; do cat "$g"; done', {}),
        ]
        for command, kwargs in cases:
            report = _observe(_loop_payload(command, "x", **kwargs))
            assert report.reads[0].read_grammar == LOOP_GRAMMAR, command

    def test_reprs_never_echo_raw_command_literals(self) -> None:
        marker = "SYNTHETIC_PRIVATE_COMMAND_LITERAL"
        result = loop(f'for f in A.md B.md; do echo "{marker}"; cat "$f"; done')
        assert marker not in repr(result)
        for statement in result.statements:
            assert marker not in repr(statement)
            for operand in statement.cat_operands:
                assert marker not in repr(operand)

    def test_prior_family_grammars_are_unchanged(self) -> None:
        simple = _observe(_loop_payload("cat A.md", "x"))
        assert simple.reads[0].read_grammar == READ_GRAMMAR
        chain = _observe(_loop_payload("cat A.md && cat B.md", "xy"))
        assert chain.reads[0].read_grammar == READ_PLAN_GRAMMAR

    def test_chat_endpoint_loop_composition(self) -> None:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "synthetic-loop-chat",
                            "type": "function",
                            "function": {
                                "name": "shell_command",
                                "arguments": json.dumps(
                                    {"cmd": 'for f in A.md B.md; do cat "$f" || exit 1; done'}
                                ),
                            },
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "synthetic-loop-chat",
                    "content": (
                        "Chunk Id: synthetic\nProcess exited with code 0\nOutput:\nsrcA\nsrcB\n"
                    ),
                },
            ]
        }
        report = _observe(payload)
        obs = report.reads[0]
        assert report.endpoint == "chat"
        assert obs.endpoint == "chat"
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.read_grammar == LOOP_GRAMMAR

    def test_call_id_pairing_and_ordering_preserved(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "name": "exec_command",
                    "call_id": "synthetic-loop-b",
                    "arguments": json.dumps({"cmd": 'for f in B.md; do cat "$f" || exit 1; done'}),
                },
                {
                    "type": "function_call",
                    "name": "exec_command",
                    "call_id": "synthetic-loop-a",
                    "arguments": json.dumps({"cmd": 'for f in A.md; do cat "$f" || exit 1; done'}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-loop-a",
                    "output": "Process exited with code 0\nOutput:\nsrcA\n",
                },
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-loop-b",
                    "output": "Process exited with code 0\nOutput:\nsrcB\n",
                },
            ]
        }
        report = _observe(payload)
        assert len(report.reads) == 2
        # Pairing is by exact call ID; results are reported in stable
        # call-ID order regardless of input order.
        assert [r.call_id for r in report.reads] == ["synthetic-loop-a", "synthetic-loop-b"]
        assert report.reads[0].proven_executed == ("A.md",)
        assert report.reads[1].proven_executed == ("B.md",)
        assert report.reads[0].bundle_digest == _digest("srcA\n")
        assert report.reads[1].bundle_digest == _digest("srcB\n")

    def test_mixed_endpoint_suppresses_loop_acquisition(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "name": "exec_command",
                    "call_id": "synthetic-loop-mixed",
                    "arguments": json.dumps({"cmd": 'for f in A.md; do cat "$f" || exit 1; done'}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-loop-mixed",
                    "output": "Process exited with code 0\nOutput:\nsrcA\n",
                },
            ],
            "messages": [
                {"role": "user", "content": "synthetic"},
            ],
        }
        report = _observe(payload)
        assert report.endpoint == "mixed"
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert Limitation.ENDPOINT_UNSUPPORTED in obs.reasons
