"""Finite literal read plans and outer attribution (D06/D07/D08).

Synthetic pure-observation tests: no shell is executed, no filesystem is
touched, and every command string under test is data.  The plan grammar is
exercised directly (``parse_read_plan`` / ``plan_source_region``) and at
the composition level (``observe_request`` over full wrapper frames).
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from slaif_local_coding.constitution.bundles import (
    READ_GRAMMAR,
    READ_PLAN_GRAMMAR,
    TOOL_WRAPPER_FORMAT,
    Limitation,
    ObservationBounds,
    ObservationReport,
    PathContext,
    PlanStatementKind,
    ReadObservation,
    ReadOutcome,
    ReadPlanParse,
    observe_request,
    parse_read_plan,
    plan_source_region,
)

_CTX = PathContext(workspace="/work")
_BOUNDS = ObservationBounds()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def plan(
    command: str,
    context: PathContext = _CTX,
    max_operands: int = 32,
    max_command_chars: int = 4096,
) -> ReadPlanParse:
    return parse_read_plan(command, context, max_command_chars, max_operands, 256)


def members(plan_parse: ReadPlanParse) -> tuple[str | None, ...]:
    return tuple(m.normalized for m in plan_parse.requested_members)


class TestChainedReadPlans:
    """D06: all-cat '&&' plans are one ordered whole bundle."""

    def test_two_cat_statements_are_earned(self) -> None:
        result = plan("cat A.md && cat B.md")
        assert result.grammar == READ_PLAN_GRAMMAR
        assert result.complete is True
        assert result.reasons == ()
        assert [s.kind for s in result.statements] == [
            PlanStatementKind.CAT,
            PlanStatementKind.CAT,
        ]
        assert members(result) == ("A.md", "B.md")
        assert result.command_digest == _digest("cat A.md && cat B.md")

    def test_multi_operand_statement_then_single(self) -> None:
        result = plan("cat A.md B.md && cat C.md")
        assert result.complete is True
        assert members(result) == ("A.md", "B.md", "C.md")

    def test_reversed_order_preserves_actual_statement_order(self) -> None:
        result = plan("cat B.md && cat A.md")
        assert result.complete is True
        assert members(result) == ("B.md", "A.md")

    def test_repeated_operands_preserve_order(self) -> None:
        result = plan("cat A.md && cat A.md")
        assert result.complete is True
        assert members(result) == ("A.md", "A.md")

    def test_empty_cat_statement_is_typed(self) -> None:
        result = plan("cat && cat A.md")
        assert result.complete is False
        assert Limitation.COMMAND_EMPTY in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_trailing_separator_is_typed(self) -> None:
        result = plan("cat A.md &&")
        assert result.complete is False
        assert Limitation.COMMAND_EMPTY in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_adjacent_operator_variant_is_not_a_separator(self) -> None:
        result = plan("cat A.md &&& cat B.md")
        assert result.complete is False
        assert Limitation.MULTIPLE_COMMANDS in result.reasons
        # Words after the operator are later-command words: never
        # reinterpreted as requested cat filenames.
        assert members(result) == ("A.md",)


class TestLiteralCdTransitions:
    """D07: absolute literal cd transitions affect following reads."""

    def test_cd_workspace_root_then_two_operands(self) -> None:
        result = plan("cd /work && cat A.md B.md")
        assert result.complete is True
        assert result.cd_transitions == ("/work",)
        assert members(result) == ("A.md", "B.md")
        assert [s.kind for s in result.statements] == [
            PlanStatementKind.CD,
            PlanStatementKind.CAT,
        ]

    def test_cd_subdirectory_then_parent_relative(self) -> None:
        result = plan("cd /work/sub && cat A.md ../B.md")
        assert result.complete is True
        assert result.cd_transitions == ("/work/sub",)
        assert members(result) == ("sub/A.md", "B.md")

    def test_quoted_cd_target_is_earned(self) -> None:
        result = plan("cd '/work/sub' && cat A.md")
        assert result.complete is True
        assert result.cd_transitions == ("/work/sub",)
        assert members(result) == ("sub/A.md",)

    def test_consecutive_cd_transitions_are_recorded_in_order(self) -> None:
        result = plan("cd /work/sub && cd /work && cat A.md")
        assert result.complete is True
        assert result.cd_transitions == ("/work/sub", "/work")
        assert members(result) == ("A.md",)

    def test_per_call_workdir_precedes_cd_transitions(self) -> None:
        # The explicit supported workdir takes precedence over the batch
        # default before the first transition; the cd then moves on top.
        context = PathContext(workspace="/work", workdir="/work/other")
        result = plan("cd /work/sub && cat A.md", context=context)
        assert result.complete is True
        assert members(result) == ("sub/A.md",)

    def test_workdir_without_cd_resolves_relative_members(self) -> None:
        context = PathContext(workspace="/work", workdir="/work/other")
        result = plan("cat A.md", context=context)
        assert result.complete is True
        assert members(result) == ("other/A.md",)

    def test_sibling_workspace_cd_is_outside(self) -> None:
        result = plan("cd /work-other && cat A.md")
        assert result.complete is False
        assert Limitation.OUTSIDE_WORKSPACE in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_cd_ancestor_of_workspace_is_outside(self) -> None:
        context = PathContext(workspace="/work/sub")
        result = plan("cd /work && cat A.md", context=context)
        assert result.complete is False
        assert Limitation.OUTSIDE_WORKSPACE in result.reasons

    def test_relative_cd_is_explicitly_typed(self) -> None:
        result = plan("cd sub && cat A.md")
        assert result.complete is False
        assert Limitation.CD_TARGET_UNSUPPORTED in result.reasons

    def test_bare_cd_is_explicitly_typed(self) -> None:
        result = plan("cd && cat A.md")
        assert result.complete is False
        assert Limitation.CD_TARGET_UNSUPPORTED in result.reasons

    def test_multi_target_cd_is_explicitly_typed(self) -> None:
        result = plan("cd /work /work2 && cat A.md")
        assert result.complete is False
        assert Limitation.CD_TARGET_UNSUPPORTED in result.reasons

    def test_dotdot_cd_target_is_explicitly_typed(self) -> None:
        result = plan("cd /work/sub/../sub2 && cat A.md")
        assert result.complete is False
        assert Limitation.CD_TARGET_UNSUPPORTED in result.reasons

    def test_cd_with_unknown_workspace_is_typed(self) -> None:
        result = plan("cd /work && cat A.md", context=PathContext())
        assert result.complete is False
        assert Limitation.UNKNOWN_WORKSPACE in result.reasons

    def test_mid_chain_cd_failure_types_the_plan(self) -> None:
        result = plan("cat A.md && cd /work-other && cat B.md")
        assert result.complete is False
        assert Limitation.OUTSIDE_WORKSPACE in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons
        # Both requested cats are preserved in actual order.
        assert members(result) == ("A.md", "B.md")


class TestEchoOuterBoundaries:
    """Earned literal echo prefix/suffix boundaries (outer regions)."""

    def test_leading_echo_is_earned(self) -> None:
        result = plan("echo '===READ===' && cat A.md B.md")
        assert result.complete is True
        echo = result.statements[0]
        assert echo.kind is PlanStatementKind.ECHO
        assert echo.echo_literal == "===READ==="
        assert members(result) == ("A.md", "B.md")

    def test_trailing_echo_is_earned(self) -> None:
        result = plan("cat A.md && echo '===END==='")
        assert result.complete is True
        assert result.statements[1].echo_literal == "===END==="

    def test_both_echo_boundaries_are_earned(self) -> None:
        result = plan("echo '===READ===' && cat A.md && cat B.md && echo '===END==='")
        assert result.complete is True
        assert result.statements[0].echo_literal == "===READ==="
        assert result.statements[-1].echo_literal == "===END==="

    def test_unquoted_echo_literal_is_typed(self) -> None:
        result = plan("echo ===READ=== && cat A.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_multi_literal_echo_is_typed(self) -> None:
        result = plan("echo 'A' 'B' && cat A.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_empty_echo_literal_is_earned(self) -> None:
        result = plan("echo '' && cat A.md")
        assert result.complete is True
        assert result.statements[0].echo_literal == ""

    def test_internal_echo_is_an_unproven_boundary(self) -> None:
        result = plan("cat A.md && echo '===' && cat B.md")
        assert result.complete is False
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons


class TestPlanNegatives:
    """Unknown control flow and non-read statements stay typed."""

    def test_ls_family_is_not_a_read_and_mixes_output(self) -> None:
        result = plan("ls -la /work && cat /work/A.md")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons
        # The cat operand is requested evidence, but nothing is proven.
        assert members(result) == ("A.md",)

    def test_head_fragment_in_chain(self) -> None:
        result = plan("head -n 5 A.md && cat B.md")
        assert result.complete is False
        assert Limitation.FRAGMENT_COMMAND in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_semicolon_chain_is_typed_and_not_a_plan(self) -> None:
        result = plan("cat A.md ; cat B.md")
        assert result.complete is False
        assert result.reasons == (Limitation.MULTIPLE_COMMANDS,)
        # The semicolon statement is one chunk: no outer-boundary claim.
        assert Limitation.OUTER_BOUNDARY_UNPROVEN not in result.reasons
        assert members(result) == ("A.md",)

    def test_attached_semicolon_token_is_not_a_literal_file(self) -> None:
        # 'A.md;' carries the separator inside one token: it is a
        # non-literal label, never a fabricated file member.
        result = plan("cat A.md; cat B.md")
        assert result.complete is False
        assert Limitation.MULTIPLE_COMMANDS in result.reasons
        assert members(result) == ()

    def test_single_ampersand_chain_is_typed(self) -> None:
        result = plan("cat A.md & cat B.md")
        assert result.complete is False
        assert Limitation.MULTIPLE_COMMANDS in result.reasons
        assert members(result) == ("A.md",)

    def test_pipe_is_typed_and_later_words_are_not_operands(self) -> None:
        result = plan("cat A.md | cat B.md")
        assert result.complete is False
        assert Limitation.PIPE in result.reasons
        assert members(result) == ("A.md",)

    def test_redirection_is_typed(self) -> None:
        result = plan("cat A.md > out && cat B.md")
        assert result.complete is False
        assert Limitation.REDIRECTION in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons

    def test_substitution_is_typed_and_stops_member_collection(self) -> None:
        result = plan("cat $FILE.md && cat B.md")
        assert result.complete is False
        assert Limitation.COMMAND_SUBSTITUTION in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons
        assert members(result) == ("B.md",)

    def test_branch_is_typed_and_words_are_not_reinterpreted(self) -> None:
        result = plan("if [ -f A.md ]; then cat A.md; fi")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert members(result) == ()

    def test_loop_is_typed_and_words_are_not_reinterpreted(self) -> None:
        result = plan("for f in A.md B.md; do cat $f; done")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert members(result) == ()

    def test_quoted_separator_is_a_literal_not_a_separator(self) -> None:
        result = plan("cat '&&' && cat B.md")
        assert result.complete is False
        assert Limitation.QUOTED_OPERAND in result.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons
        assert members(result) == ("B.md",)

    def test_no_cat_statement_is_not_a_read(self) -> None:
        result = plan("cd /work")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert members(result) == ()

    def test_consecutive_cds_without_cat_are_not_a_read(self) -> None:
        result = plan("cd /work && cd /work/sub")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons

    def test_malformed_unicode_is_typed_without_digest(self) -> None:
        result = plan("cat A\ud800.md && cat B.md")
        assert result.complete is False
        assert result.reasons == (Limitation.MALFORMED_UNICODE,)
        assert result.command_digest is None

    def test_newline_is_a_compound_command(self) -> None:
        result = plan("cat A.md\ncat B.md")
        assert result.complete is False
        assert result.reasons == (Limitation.MULTIPLE_COMMANDS,)

    def test_tab_control_guard_is_not_relaxed(self) -> None:
        result = plan("cat A.md\tB.md")
        assert result.complete is False
        assert result.reasons == (Limitation.COMMAND_UNSUPPORTED,)

    def test_cr_control_guard_is_not_relaxed(self) -> None:
        result = plan("cat A.md\rB.md")
        assert result.complete is False
        assert Limitation.MULTIPLE_COMMANDS in result.reasons

    def test_over_bound_whole_plan_is_typed(self) -> None:
        result = plan("cat " + "A.md " * 1000, max_command_chars=4096)
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons


class TestLsFamily:
    """Bounded ls recognition (objective 017-am): a clean ls is a
    recognized non-read statement; the leading-clean-ls-then-cat shape
    is recorded for the final-cat evidence contract and never acquires
    by itself."""

    def test_bare_ls_forms_are_recognized_and_not_reads(self) -> None:
        for command in ("ls", "ls -la", "ls -la /work"):
            result = plan(command)
            assert len(result.statements) == 1
            statement = result.statements[0]
            assert statement.kind is PlanStatementKind.LS
            assert statement.reasons == ()
            # A plan without any cat statement is not a read at all.
            assert result.complete is False
            assert result.reasons == (Limitation.COMMAND_UNSUPPORTED,)
            assert result.ls_cat_shape is False
            assert members(result) == ()

    def test_out_of_shape_ls_forms_stay_other(self) -> None:
        for command in (
            "ls /work /work2",
            'ls "/work"',
            "ls -la --color=always /work /work2",
        ):
            result = plan(command)
            assert result.statements[0].kind is PlanStatementKind.OTHER
            assert Limitation.COMMAND_UNSUPPORTED in result.statements[0].reasons
            assert result.complete is False
            assert result.ls_cat_shape is False
            assert members(result) == ()

    def test_ls_cat_shape_is_recognized_and_structurally_mixed(self) -> None:
        result = plan("ls -la /work && cat /work/A.md")
        assert result.complete is False
        # The listing keeps the combined output unattributable and the
        # family typed as not a pure read.
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in result.reasons
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert members(result) == ("A.md",)
        assert result.ls_cat_shape is True

    def test_ls_cat_shape_negatives(self) -> None:
        for command in (
            "cat A.md",
            "ls /work && cd /work2 && cat A.md",
            "ls /work && cat $X.md",
            "cat A.md && ls",
            "ls /work && cat A.md && ls",
        ):
            result = plan(command)
            assert result.ls_cat_shape is False, command


class TestWholePlanBounds:
    """Whole-plan bounds, never per-segment multiplication."""

    def test_exact_operand_budget_across_statements_is_complete(self) -> None:
        left = " ".join(f"L{i}.md" for i in range(16))
        right = " ".join(f"R{i}.md" for i in range(16))
        result = plan(f"cat {left} && cat {right}")
        assert result.complete is True
        assert len(result.requested_members) == 32

    def test_one_over_operand_budget_across_statements_is_typed(self) -> None:
        left = " ".join(f"L{i}.md" for i in range(16))
        right = " ".join(f"R{i}.md" for i in range(17))
        result = plan(f"cat {left} && cat {right}")
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons

    def test_exact_statement_bound_is_complete(self) -> None:
        result = plan(" && ".join(f"cat F{i}.md" for i in range(32)))
        assert result.complete is True
        assert len(result.statements) == 32

    def test_one_over_statement_bound_is_typed(self) -> None:
        result = plan(" && ".join("ls" for _ in range(33)))
        assert result.complete is False
        assert Limitation.OVER_BOUND in result.reasons


class TestOuterSourceRegions:
    """plan_source_region: proven prefix/suffix boundaries only."""

    def test_no_echo_attributes_whole_content(self) -> None:
        result = plan("cat A.md && cat B.md")
        span, reasons = plan_source_region(result, "abcDEF")
        assert span is not None and reasons == ()
        assert (span.start, span.end) == (0, 6)

    def test_leading_echo_prefix_is_proven_at_exact_position(self) -> None:
        result = plan("echo '===READ===' && cat A.md B.md")
        span, reasons = plan_source_region(result, "===READ===\n<srcA><srcB>")
        assert span is not None and reasons == ()
        assert span.start == len("===READ===\n")
        assert span.end == len("===READ===\n<srcA><srcB>")

    def test_trailing_echo_suffix_is_proven_at_exact_position(self) -> None:
        result = plan("cat A.md && echo '===END==='")
        content = "<srcA>===END===\n"
        span, reasons = plan_source_region(result, content)
        assert span is not None and reasons == ()
        assert (span.start, span.end) == (0, len("<srcA>"))

    def test_both_boundaries_expose_only_the_pure_middle(self) -> None:
        result = plan("echo '===READ===' && cat A.md && cat B.md && echo '===END==='")
        content = "===READ===\n<srcA><srcB>===END===\n"
        span, reasons = plan_source_region(result, content)
        assert span is not None and reasons == ()
        assert content[span.start : span.end] == "<srcA><srcB>"

    def test_multiple_leading_echoes_accumulate_in_statement_order(self) -> None:
        result = plan("echo 'A' && echo 'B' && cat X.md")
        span, reasons = plan_source_region(result, "A\nB\n<body>")
        assert span is not None and reasons == ()
        assert (span.start, span.end) == (4, 10)

    def test_empty_source_between_proven_boundaries(self) -> None:
        result = plan("echo '===READ===' && cat A.md")
        span, reasons = plan_source_region(result, "===READ===\n")
        assert span is not None and reasons == ()
        assert span.length == 0

    def test_unicode_prefix_uses_exact_byte_conversion(self) -> None:
        result = plan("echo 'éé' && cat A.md")
        content = "éé\nbody"
        span, reasons = plan_source_region(result, content)
        assert span is not None and reasons == ()
        byte_start, byte_end = span.to_byte_span(content)
        assert content.encode("utf-8")[byte_start:byte_end] == b"body"

    def test_collision_shorter_than_boundaries_is_typed(self) -> None:
        result = plan("echo '===READ===' && cat A.md")
        span, reasons = plan_source_region(result, "===READ===")
        assert span is None
        assert reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)

    def test_extra_output_before_prefix_is_typed(self) -> None:
        result = plan("echo '===READ===' && cat A.md")
        span, reasons = plan_source_region(result, "extra\n===READ===\nbody")
        assert span is None
        assert reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)

    def test_mismatched_suffix_is_typed(self) -> None:
        result = plan("cat A.md && echo '===END==='")
        span, reasons = plan_source_region(result, "<srcA>OTHER\n")
        assert span is None
        assert reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)

    def test_incomplete_plan_never_attributes(self) -> None:
        result = plan("ls -la /work && cat /work/A.md")
        span, reasons = plan_source_region(result, "listing...<src>")
        assert span is None
        assert reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)


def _chain_payload(
    command: str,
    output: str,
    exit_code: int = 0,
    extra_args: dict[str, Any] | None = None,
    truncated: bool = False,
) -> dict[str, Any]:
    """One Responses request: exec_command call plus wrapper result frame."""

    arguments: dict[str, Any] = {"cmd": command}
    if extra_args is not None:
        arguments.update(extra_args)
    body = f"Process exited with code {exit_code}\n"
    if truncated:
        body += "Truncated: true\n"
    body += "Output:\n" + output
    return {
        "input": [
            {
                "type": "function_call",
                "call_id": "synthetic-plan-1",
                "name": "exec_command",
                "arguments": json.dumps(arguments),
            },
            {"type": "function_call_output", "call_id": "synthetic-plan-1", "output": body},
        ]
    }


def _observe(payload: dict[str, Any], **kwargs: Any) -> ObservationReport:
    before = copy.deepcopy(payload)
    report = observe_request(payload, context=_CTX, **kwargs)
    assert payload == before, "observer mutated its input"
    return report


class TestChainedPlanComposition:
    """D06 at the composition level: real source slicing, one bundle."""

    def test_two_cat_chain_is_one_complete_ordered_bundle(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md", "source A\nsource B\n")
        report = _observe(payload)
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.completeness is ReadOutcome.COMPLETE
        assert obs.removable is True
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.distinct_member_count == 2
        assert obs.slot_width == 2
        assert obs.member_digests == (None, None)
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == ("source A\nsource B\n")
        assert obs.bundle_digest == _digest("source A\nsource B\n")

    def test_three_members_across_two_statements_preserve_order(self) -> None:
        payload = _chain_payload("cat C.md && cat A.md B.md", "C\nA\nB\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("C.md", "A.md", "B.md")
        assert obs.distinct_member_count == 3
        assert obs.bundle_digest == _digest("C\nA\nB\n")

    def test_repeated_operands_preserve_order_and_distinct_width(self) -> None:
        payload = _chain_payload("cat A.md && cat A.md", "aa\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "A.md")
        assert obs.distinct_member_count == 1
        assert obs.member_digests == (None,)

    def test_cd_then_reads_resolves_against_transition(self) -> None:
        payload = _chain_payload("cd /work/sub && cat A.md ../B.md", "subA\nB\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("sub/A.md", "B.md")
        assert obs.bundle_digest == _digest("subA\nB\n")

    def test_per_call_workdir_then_cd_transition(self) -> None:
        payload = _chain_payload(
            "cd /work/sub && cat A.md", "sA\n", extra_args={"workdir": "/work/other"}
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("sub/A.md",)

    def test_single_member_chain_proves_member_digest(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md && cat C.md", "abc")
        # Three distinct members: no member digest may be fabricated.
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "B.md", "C.md")
        assert obs.member_digests == (None, None, None)
        assert obs.bundle_digest == _digest("abc")

    def test_unicode_crlf_chain_bytes_are_exact(self) -> None:
        content = "éé\r\nünïcode\r\n"
        payload = _chain_payload("cat A.md && cat B.md", content)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        byte_start, byte_end = obs.content_span.to_byte_span(output)
        assert output.encode("utf-8")[byte_start:byte_end] == content.encode("utf-8")
        assert obs.bundle_digest == _digest(content)

    def test_zero_byte_member_still_one_complete_bundle(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md", "onlyA\n")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.bundle_digest == _digest("onlyA\n")


class TestOuterRegionComposition:
    """Known outer regions: proven prefix/suffix, pure file span only."""

    def test_echo_prefix_exposes_only_the_pure_file_span(self) -> None:
        payload = _chain_payload("echo '===READ===' && cat A.md B.md", "===READ===\n<srcA><srcB>")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        output = payload["input"][1]["output"]
        middle = "<srcA><srcB>"
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == middle
        # The label stays at its original position in the wrapper output
        # region, untouched, and the digest is over the pure file span —
        # never a whole mixed-output digest.
        assert obs.content_span is not None
        assert obs.wrapper.output_span is not None
        wrapper_output = output[obs.wrapper.output_span.start : obs.wrapper.output_span.end]
        assert wrapper_output.startswith("===READ===\n")
        assert obs.bundle_digest == _digest(middle)
        assert obs.bundle_digest != _digest("===READ===\n" + middle)
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.member_digests == (None, None)

    def test_echo_prefix_and_suffix(self) -> None:
        payload = _chain_payload(
            "echo '===READ===' && cat A.md && echo '===END==='",
            "===READ===\n<srcA>===END===\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == "<srcA>"
        assert obs.bundle_digest == _digest("<srcA>")
        assert obs.proven_executed == ("A.md",)
        # Exactly one member: the pure middle is that one file.
        assert obs.member_digests == (
            _digest(
                "<srcA>",
            ),
        )

    def test_label_inside_source_remains_source(self) -> None:
        # The file content itself contains the suffix literal: the suffix
        # anchors at the very end of the output, so the file's own bytes
        # stay source.
        payload = _chain_payload(
            "echo '===READ===' && cat A.md && echo '===END==='",
            "===READ===\n===END===\nx\n===END===\n",
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == ("===END===\nx\n")

    def test_boundary_collision_is_typed_not_attributed(self) -> None:
        # Output shorter than prefix plus suffix: unprovable.
        payload = _chain_payload("echo '===READ===' && cat A.md", "===READ===")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons

    def test_extra_output_before_prefix_is_typed(self) -> None:
        payload = _chain_payload("echo '===READ===' && cat A.md", "extra line\n===READ===\nbody")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons

    def test_internal_echo_is_typed_not_attributed(self) -> None:
        payload = _chain_payload("cat A.md && echo '===' && cat B.md", "<srcA>===\n<srcB>")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons


class TestMixedOutputNegatives:
    """ls-family and mixed plans: no acquisition, typed, status preserved."""

    def test_ls_family_exit_zero_is_not_support(self) -> None:
        payload = _chain_payload(
            "ls -la /work && cat /work/A.md",
            "total 4\ndrwxr-xr-x A.md\n<src>",
            exit_code=0,
        )
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert Limitation.COMMAND_UNSUPPORTED in obs.reasons
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons

    def test_ls_before_read_nonzero_is_not_support(self) -> None:
        payload = _chain_payload("ls -la /work && cat /work/A.md", "", exit_code=1)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.bundle_digest is None

    def test_semicolon_chain_exit_zero_acquires_nothing(self) -> None:
        # A later successful command in a semicolon chain does not prove
        # an earlier cat succeeded.
        payload = _chain_payload("cat A.md; cat B.md", "srcA\nsrcB\n", exit_code=0)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.proven_executed == ()
        assert Limitation.MULTIPLE_COMMANDS in obs.reasons


class TestPerReadVersusGlobalExit:
    """D08: global exit status is not per-read proof."""

    def test_nonzero_chain_proves_no_read_and_no_digest(self) -> None:
        # Earlier read could have completed, but the global nonzero in an
        # && chain identifies no per-read failure and proves no earlier
        # source complete: nothing is proven, no digest is issued.
        payload = _chain_payload("cat A.md && cat /work/missing.md", "srcA\n", exit_code=1)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.completeness is ReadOutcome.PARTIAL
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.member_digests == ()
        assert obs.proven_executed == ()
        # Requested members stay recorded in actual order.
        assert tuple(m.normalized for m in obs.requested_members) == (
            "A.md",
            "missing.md",
        )
        # The original wrapper/global status is preserved as recorded.
        assert obs.wrapper.exit_status.value == "nonzero"
        assert obs.wrapper.exit_code == 1

    def test_earlier_failure_later_success_nonzero(self) -> None:
        payload = _chain_payload("cat /work/missing.md && cat A.md", "", exit_code=1)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.proven_executed == ()
        assert obs.bundle_digest is None

    def test_truncated_chain_is_not_a_bundle(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md", "partial", truncated=True)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.TRUNCATED
        assert obs.completeness is ReadOutcome.PARTIAL
        assert obs.removable is False
        assert obs.bundle_digest is None

    def test_process_running_chain_is_deferred(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "synthetic-plan-1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md && cat B.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-plan-1",
                    "output": "Process is still running",
                },
            ]
        }
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.PROCESS_RUNNING in obs.reasons

    def test_malformed_unicode_chain_content_is_typed(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md", "synthetic\ud800")
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.bundle_digest is None
        assert Limitation.MALFORMED_UNICODE in obs.reasons

    def test_chat_endpoint_chain_composition(self) -> None:
        frame = "Process exited with code 0\nOutput:\ncA\ncB\n"
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "type": "function",
                            "id": "synthetic-chat-plan",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat A.md && cat B.md"}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "synthetic-chat-plan", "content": frame},
            ]
        }
        report = _observe(payload)
        assert report.endpoint == "chat"
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.proven_executed == ("A.md", "B.md")
        assert obs.bundle_digest == _digest("cA\ncB\n")

    def test_mixed_envelope_still_suppresses_plan_acquisition(self) -> None:
        payload = _chain_payload("cat A.md && cat B.md", "a\nb\n")
        payload["messages"] = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": "mix-plan",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat C.md"}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "mix-plan",
                "content": "Process exited with code 0\nOutput:\nc\n",
            },
        ]
        report = _observe(payload)
        assert report.endpoint == "mixed"
        for obs in report.reads:
            assert obs.outcome is ReadOutcome.UNSUPPORTED
            assert obs.removable is False
            assert obs.bundle_digest is None


class TestEchoOptionSemantics:
    """Quoting does not disable echo's option parser (017-e correction).

    Option-like cooked operands are implementation-sensitive: the actual
    ``echo '-n'`` writes nothing, so a dash-leading quoted literal never
    earns a literal+newline boundary (either quote kind).  The exclusion
    is narrow: non-dash-leading literals (including a dash inside the
    literal or the empty literal) stay earned.
    """

    def test_single_quoted_option_prefix_is_typed(self) -> None:
        result = plan("echo '-n' && cat A.md B.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons
        # The cat request stays recorded data; nothing is attributed.
        assert members(result) == ("A.md", "B.md")
        span, reasons = plan_source_region(result, "-n\nsource")
        assert span is None
        assert reasons == (Limitation.OUTER_BOUNDARY_UNPROVEN,)

    def test_double_quoted_option_prefix_is_typed(self) -> None:
        result = plan('echo "-n" && cat A.md B.md')
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_option_combinations_are_typed(self) -> None:
        for command in (
            "echo '-ne' && cat A.md",
            'echo "-ne" && cat A.md',
            "echo '-e' && cat A.md",
            'echo "-E" && cat A.md',
            "echo '-nE' && cat A.md",
        ):
            result = plan(command)
            assert result.complete is False, command
            assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons, command

    def test_repeated_option_literals_are_typed(self) -> None:
        result = plan("echo '-n' '-n' && cat A.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_unquoted_option_is_typed(self) -> None:
        result = plan("echo -n && cat A.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_dash_alone_is_conservatively_typed(self) -> None:
        result = plan("echo '-' && cat A.md")
        assert result.complete is False
        assert Limitation.ECHO_TARGET_UNSUPPORTED in result.reasons

    def test_non_option_literals_stay_earned(self) -> None:
        # The exclusion is dash-leading only: markers and dash-inside or
        # empty literals keep the earned boundary contract.
        result = plan("echo '===READ===' && cat A.md")
        assert result.complete is True
        assert result.statements[0].echo_literal == "===READ==="
        result = plan("echo 'A-n' && cat A.md")
        assert result.complete is True
        assert result.statements[0].echo_literal == "A-n"
        result = plan("echo '' && cat A.md")
        assert result.complete is True
        assert result.statements[0].echo_literal == ""


class TestEchoOptionSemanticsComposition:
    """Public observe_request: option-like echo never strips source."""

    BODY = "Synthetic A\r\nSynthetic B \u00e9\n"

    def _unsupported(self, command: str, source: str) -> ReadObservation:
        payload = _chain_payload(command, source)
        report = _observe(payload)
        assert len(report.reads) == 1
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.completeness is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.member_digests == ()
        assert obs.content_span is None
        assert obs.proven_executed == ()
        assert Limitation.ECHO_TARGET_UNSUPPORTED in obs.reasons
        return obs

    def test_quoted_n_prefix_never_strips_source(self) -> None:
        # The source deliberately begins with the fake boundary '-n\n';
        # the echo is typed before boundary matching, so no span and no
        # digest can be invented.
        obs = self._unsupported("echo '-n' && cat A.md B.md", "-n\n" + self.BODY)
        assert tuple(m.normalized for m in obs.requested_members) == ("A.md", "B.md")
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_double_quoted_n_suffix_never_strips_source(self) -> None:
        obs = self._unsupported('cat A.md B.md && echo "-n"', self.BODY + "-n\n")
        assert tuple(m.normalized for m in obs.requested_members) == ("A.md", "B.md")
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_ne_prefix_with_fake_boundary_inside_source(self) -> None:
        # The source contains the fake boundary twice (outer and inside):
        # both are source, and nothing is removable or attributable.
        obs = self._unsupported("echo '-ne' && cat A.md B.md", "-ne\n" + "-ne\n" + self.BODY)
        assert obs.removable is False
        assert obs.bundle_digest is None

    def test_source_containing_real_marker_stays_typed(self) -> None:
        # Even when the source carries a real marker-like line, an
        # option-like echo command stays typed unsupported: matching file
        # bytes cannot establish that an echo printed them.
        marker = "===READ===\n"
        obs = self._unsupported("echo '-n' && cat A.md B.md", "-n\n" + marker + self.BODY)
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.content_span is None

    def test_single_quoted_marker_still_earned_in_source(self) -> None:
        # Control: the earned marker contract is unchanged — only the
        # dash-leading exclusion is new.
        marker = "===READ===\n"
        payload = _chain_payload("echo '===READ===' && cat A.md B.md", marker + self.BODY)
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.removable is True
        output = payload["input"][1]["output"]
        assert obs.content_span is not None
        assert output[obs.content_span.start : obs.content_span.end] == self.BODY
        assert obs.bundle_digest == _digest(self.BODY)


class TestPlanGrammarIdentity:
    """The actual parser grammar is carried on every plan observation.

    Grammar-identity fallback law: the single-command grammar is primary;
    a command it does not complete is evaluated by the finite-plan parser,
    and every observation that parser produces carries ``READ_PLAN_GRAMMAR``
    (complete, unsupported, nonzero, missing/truncated/running, malformed
    or outer-boundary-unproven).  Observations the single grammar actually
    earned keep ``READ_GRAMMAR``.  The label never changes outcome.
    """

    def test_complete_chain_carries_plan_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md && cat B.md", "a\nb\n"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.read_grammar == READ_PLAN_GRAMMAR
        assert obs.wrapper_format == TOOL_WRAPPER_FORMAT

    def test_unsupported_plan_carries_plan_grammar(self) -> None:
        report = _observe(_chain_payload("head A.md && cat B.md", "frag\n"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_nonzero_chain_carries_plan_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md && cat B.md", "a\n", exit_code=1))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_truncated_chain_carries_plan_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md && cat B.md", "a\n", truncated=True))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.TRUNCATED
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_missing_body_chain_carries_plan_grammar(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "synthetic-plan-1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md && cat B.md"}),
                },
                {"type": "function_call_output", "call_id": "synthetic-plan-1", "output": ""},
            ]
        }
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.MISSING_BODY
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_process_running_chain_carries_plan_grammar(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "synthetic-plan-1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md && cat B.md"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "synthetic-plan-1",
                    "output": "Process is still running",
                },
            ]
        }
        report = _observe(payload)
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.PROCESS_RUNNING in obs.reasons
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_malformed_unicode_chain_carries_plan_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md && cat B.md", "synthetic\ud800"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.MALFORMED_UNICODE in obs.reasons
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_outer_boundary_collision_carries_plan_grammar(self) -> None:
        # A complete plan whose echo boundary does not match the output:
        # the grammar that evaluated the plan is still the plan grammar.
        report = _observe(_chain_payload("echo '===READ===' && cat A.md", "Unexpected\nsrcA\n"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert Limitation.OUTER_BOUNDARY_UNPROVEN in obs.reasons
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_single_complete_read_keeps_single_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md", "a\n"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.COMPLETE
        assert obs.read_grammar == READ_GRAMMAR
        assert obs.read_grammar != READ_PLAN_GRAMMAR

    def test_single_unsupported_read_is_never_a_successful_plan(self) -> None:
        # Fallback selection: the plan parser evaluates the unsupported
        # single command and labels it, but the outcome stays unsupported
        # (never a complete/earned plan).
        report = _observe(_chain_payload("head A.md", "frag\n"))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.UNSUPPORTED
        assert obs.removable is False
        assert obs.bundle_digest is None
        assert obs.read_grammar == READ_PLAN_GRAMMAR

    def test_single_nonzero_read_keeps_single_grammar(self) -> None:
        report = _observe(_chain_payload("cat A.md", "a\n", exit_code=1))
        obs = report.reads[0]
        assert obs.outcome is ReadOutcome.NONZERO_EXIT
        assert obs.read_grammar == READ_GRAMMAR
