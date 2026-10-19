"""D03/D04: bounded literal cat grammar — support and safe negatives."""

from __future__ import annotations

import json
import pathlib

import pytest

from slaif_local_coding.constitution.bundles import (
    Limitation,
    PathContext,
    ReadCommandParse,
    UnwrappedCommand,
    parse_read_command,
    raw_argument_bound,
    tokenize_literal,
    unwrap_call_arguments,
    unwrap_supported_arguments,
)

_CTX = PathContext(workspace="/work")


def parse(command: str, context: PathContext = _CTX) -> ReadCommandParse:
    return parse_read_command(command, context, 4096, 32, 256)


class TestSupportedForms:
    def test_single_relative_operand(self) -> None:
        result = parse("cat A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md"]
        assert result.reasons == ()

    def test_dash_dash_separator(self) -> None:
        result = parse("cat -- A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md"]

    def test_two_operands_in_order(self) -> None:
        result = parse("cat A.md B.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md", "B.md"]

    def test_repeated_operand_preserves_order(self) -> None:
        result = parse("cat A.md A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md", "A.md"]
        assert result.distinct_operands == 1

    def test_absolute_workspace_operands(self) -> None:
        result = parse("cat /work/A.md /work/docs/B.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md", "docs/B.md"]

    def test_fully_quoted_operands_under_no_spaces_convention(self) -> None:
        result = parse('cat "A.md"')
        assert result.complete is True
        assert result.operands[0].normalized == "A.md"
        assert result.operands[0].quoted is True

    def test_command_digest_and_length_are_recorded(self) -> None:
        result = parse("cat A.md")
        assert result.command_length == 8
        import hashlib

        assert result.command_digest == hashlib.sha256(b"cat A.md").hexdigest()


class TestSafeNegatives:
    @pytest.mark.parametrize(
        ("command", "reason"),
        [
            ("head -n 5 A.md", Limitation.FRAGMENT_COMMAND),
            ("tail A.md", Limitation.FRAGMENT_COMMAND),
            ("sed -n 1p A.md", Limitation.FRAGMENT_COMMAND),
            ("cat A.md | grep x", Limitation.PIPE),
            ("cat A.md > out", Limitation.REDIRECTION),
            ("cat A.md && cat B.md", Limitation.MULTIPLE_COMMANDS),
            ("cat A.md; echo hi", Limitation.MULTIPLE_COMMANDS),
            ("cat A.md & cat B.md", Limitation.MULTIPLE_COMMANDS),
            ("cat $A.md", Limitation.COMMAND_SUBSTITUTION),
            ("cat `ls`", Limitation.COMMAND_SUBSTITUTION),
            ("cat A*.md", Limitation.GLOB_UNPROVEN),
            ("cat A?.md", Limitation.GLOB_UNPROVEN),
            ("cat A.md # read A", Limitation.COMMENT_PRESENT),
            ("# cat A.md", Limitation.COMMENT_PRESENT),
            ('cat A.md "b', Limitation.QUOTED_OPERAND),
            ("cat A\\.md", Limitation.SHELL_ESCAPE),
            ("cat ~A.md", Limitation.NON_LITERAL_OPERAND),
            ("cat -n A.md", Limitation.COMMAND_UNSUPPORTED),
            ("/bin/cat A.md", Limitation.COMMAND_UNSUPPORTED),
            ("cat2 A.md", Limitation.COMMAND_UNSUPPORTED),
            ("cat", Limitation.COMMAND_EMPTY),
            ("cat --", Limitation.COMMAND_EMPTY),
            ("", Limitation.COMMAND_EMPTY),
            ("   ", Limitation.COMMAND_EMPTY),
        ],
    )
    def test_unsupported_shapes_are_typed_never_complete(
        self, command: str, reason: Limitation
    ) -> None:
        result = parse(command)
        assert result.complete is False
        assert reason in result.reasons
        # A fragment or compound is never a whole-file observation: no
        # member may be reported as normalized and proven.
        assert result.distinct_operands == 0 or result.complete is False

    def test_comment_terminates_the_command_line(self) -> None:
        result = parse("cat A.md # note")
        assert result.complete is False
        assert result.reasons == (Limitation.COMMENT_PRESENT,)
        # The comment itself terminates: no further reason is collected.
        assert len(result.reasons) == 1

    def test_unexecuted_branch_is_not_a_read(self) -> None:
        result = parse("if [ -f A.md ]; then cat A.md; fi")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons

    def test_loop_is_not_a_read_in_this_slice(self) -> None:
        result = parse("for f in A.md B.md; do cat $f; done")
        assert result.complete is False
        assert result.reasons

    def test_newline_is_a_compound_command(self) -> None:
        result = parse("cat A.md\ncat B.md")
        assert result.complete is False
        assert result.reasons == (Limitation.MULTIPLE_COMMANDS,)

    def test_over_bound_command_is_typed(self) -> None:
        command = "cat " + " ".join(f"F{i}.md" for i in range(2000))
        result = parse_read_command(command, _CTX, 4096, 32, 256)
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons

    def test_too_many_operands_is_typed(self) -> None:
        command = "cat " + " ".join(f"F{i}.md" for i in range(40))
        result = parse_read_command(command, _CTX, 4096, 32, 256)
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons


class TestTokenization:
    def test_literal_whitespace_tokenization(self) -> None:
        tokens = tokenize_literal("cat  A.md\tB.md")
        assert [t for t, _s, _e in tokens] == ["cat", "A.md", "B.md"]

    def test_no_expansion_no_evaluation(self) -> None:
        # Environment, glob and substitution text are tokens, not commands.
        tokens = tokenize_literal("cat $HOME/A.md * `x`")
        assert [t for t, _s, _e in tokens] == ["cat", "$HOME/A.md", "*", "`x`"]


class TestArgumentUnwrapping:
    def test_json_string_cmd(self) -> None:
        assert unwrap_supported_arguments(json.dumps({"cmd": "cat A.md"})) == "cat A.md"

    def test_non_json_string_arguments_are_unsupported(self) -> None:
        # A raw non-JSON string argument is not a supported schema shape:
        # it is typed unsupported, never guessed.
        assert unwrap_supported_arguments("cat A.md") is None

    def test_command_string_alias(self) -> None:
        assert unwrap_supported_arguments({"command": "cat A.md"}) == "cat A.md"

    def test_argv_single_string(self) -> None:
        assert unwrap_supported_arguments({"command": ["cat A.md"]}) == "cat A.md"

    def test_argv_shell_wrappers(self) -> None:
        for shell in ("bash", "sh", "zsh"):
            for flag in ("-c", "-lc"):
                assert (
                    unwrap_supported_arguments({"command": [shell, flag, "cat A.md"]}) == "cat A.md"
                )

    @pytest.mark.parametrize(
        "arguments",
        [
            {"cmd": 123},
            {"command": ["bash", "cat A.md"]},  # missing -c
            {"command": ["bash", "-c"]},  # no command string
            {"command": ["bash", "-c", "cat A.md", "extra"]},  # extra argv
            {"command": ["bash", "script.sh"]},  # script, not -c
            {"command": ["cat", "A.md"]},  # direct argv cat: not earned
            "not json {",
            None,
            42,
        ],
    )
    def test_unsupported_argument_shapes(self, arguments: object) -> None:
        assert unwrap_supported_arguments(arguments) is None


class TestNoShellExecution:
    def test_module_imports_no_shell_facilities(self) -> None:
        import ast

        source = (
            pathlib.Path("src/slaif_local_coding/constitution/bundles/read_grammar.py")
            .resolve()
            .read_text()
        )
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        forbidden = {"subprocess", "os", "shlex", "glob", "pathlib", "tempfile"}
        assert not (imported & forbidden), imported & forbidden


class TestTerminatorMembership:
    """The option terminator is processed once; a later ``--`` is a literal
    operand and stays in the actual complete member list."""

    def test_second_terminator_is_literal_operand(self) -> None:
        result = parse("cat -- A.md -- B.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md", "--", "B.md"]
        assert result.reasons == ()

    def test_second_terminator_is_not_classified_as_flag(self) -> None:
        result = parse("cat -- A.md -- B.md")
        assert Limitation.COMMAND_UNSUPPORTED not in result.reasons

    def test_terminator_only_command_stays_empty(self) -> None:
        result = parse("cat --")
        assert result.complete is False
        assert result.reasons == (Limitation.COMMAND_EMPTY,)

    def test_second_terminator_alone_is_literal_operand(self) -> None:
        result = parse("cat -- --")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["--"]


class TestMalformedUnicodeCommand:
    def test_surrogate_command_is_typed_without_digest(self) -> None:
        result = parse_read_command("cat A\ud800.md", _CTX, 4096, 32, 256)
        assert result.complete is False
        assert result.reasons == (Limitation.MALFORMED_UNICODE,)
        # No placeholder digest: the digest is explicitly absent.
        assert result.command_digest is None
        assert result.operands == ()

    def test_valid_command_digest_still_recorded(self) -> None:
        import hashlib

        result = parse("cat A.md")
        assert result.command_digest == hashlib.sha256(b"cat A.md").hexdigest()


class TestCallArgumentShapes:
    def test_cmd_object_with_workdir(self) -> None:
        unwrapped = unwrap_call_arguments(json.dumps({"cmd": "cat A.md", "workdir": "/work/sub"}))
        assert unwrapped == UnwrappedCommand(command="cat A.md", workdir="/work/sub")

    def test_command_alias_with_workdir(self) -> None:
        unwrapped = unwrap_call_arguments({"command": "cat A.md", "workdir": "/work/sub"})
        assert unwrapped == UnwrappedCommand(command="cat A.md", workdir="/work/sub")

    def test_argv_form_carries_no_workdir(self) -> None:
        unwrapped = unwrap_call_arguments({"command": ["bash", "-c", "cat A.md"]})
        assert unwrapped == UnwrappedCommand(command="cat A.md", workdir=None)

    def test_workdir_without_command_is_unsupported(self) -> None:
        assert unwrap_call_arguments({"workdir": "/work/sub"}) is None

    @pytest.mark.parametrize(
        "arguments",
        [
            {"cmd": "cat A.md", "workdir": 42},
            {"cmd": "cat A.md", "workdir": ""},
            {"cmd": "cat A.md", "workdir": None},
            {"cmd": "cat A.md", "workdir": ["/work"]},
        ],
    )
    def test_non_string_or_empty_workdir_is_unsupported(self, arguments: object) -> None:
        assert unwrap_call_arguments(arguments) is None

    def test_over_bound_argument_string_is_unsupported_without_parsing(self) -> None:
        # The documented raw cap (12 * bound + 128) is the conservative
        # worst case of the supported JSON encoding; beyond it the shape
        # is typed unsupported without being parsed.
        big = json.dumps({"cmd": "cat " + " ".join(f"F{i:015d}.md" for i in range(3000))})
        assert len(big) > raw_argument_bound(4096)
        assert unwrap_call_arguments(big, 4096) is None
        # Within the bound it still parses (the command itself is later
        # typed over-bound by the grammar, not by a decode failure).
        within = json.dumps({"cmd": "cat " + "A.md " * 30})
        assert unwrap_call_arguments(within, 4096) is not None

    def test_unicode_command_within_documented_cap_still_decodes(self) -> None:
        # Worst-case JSON escaping (six characters per character) of an
        # in-bounds non-ASCII command stays inside the documented raw cap;
        # the earlier 2x+128 cap wrongly rejected such valid commands.
        command = "cat " + "\u00e9" * 4092  # exactly 4096 characters
        assert len(command) <= 4096
        raw = json.dumps({"cmd": command})
        assert raw_argument_bound(4096) >= len(raw) > 2 * 4096 + 128
        assert unwrap_call_arguments(raw, 4096) is not None

    def test_repr_omits_raw_command_and_workdir(self) -> None:
        marker = "SYNTHETIC_PRIVATE_MARKER"
        unwrapped = unwrap_call_arguments(
            {"cmd": f"cat A.md # {marker}", "workdir": f"/work/{marker}"}
        )
        assert unwrapped is not None
        assert marker not in repr(unwrapped)


class TestQuotedOptionSemantics:
    """Quoting does not disable cat's option parser: options and the stdin
    special operand are never file members; the terminator is recognized by
    cooked value."""

    def test_quoted_short_option_is_not_a_file_member(self) -> None:
        result = parse("cat '-n' A.md")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert all(o.normalized != "-n" for o in result.operands)

    def test_quoted_long_option_is_not_a_file_member(self) -> None:
        result = parse("cat '--number' A.md")
        assert result.complete is False
        assert Limitation.COMMAND_UNSUPPORTED in result.reasons
        assert all(o.normalized != "--number" for o in result.operands)

    def test_quoted_stdin_is_not_a_file_member(self) -> None:
        result = parse("cat '-' A.md")
        assert result.complete is False
        assert Limitation.STDIN_OPERAND in result.reasons
        assert all(o.normalized != "-" for o in result.operands)

    def test_unquoted_stdin_is_not_a_file_member(self) -> None:
        result = parse("cat - A.md")
        assert result.complete is False
        assert Limitation.STDIN_OPERAND in result.reasons

    def test_stdin_after_terminator_is_not_a_file_member(self) -> None:
        for command in ("cat -- '-' A.md", "cat -- - A.md"):
            result = parse(command)
            assert result.complete is False, command
            assert Limitation.STDIN_OPERAND in result.reasons, command
            assert all(o.normalized != "-" for o in result.operands), command

    def test_quoted_terminator_proves_only_the_operand(self) -> None:
        result = parse("cat '--' A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md"]
        # The terminator is consumed, never a member: no '--' file invented.
        assert all(o.normalized != "--" for o in result.operands)

    def test_unquoted_terminator_positive_preserved(self) -> None:
        result = parse("cat -- A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md"]

    def test_quoted_file_positive_preserved(self) -> None:
        result = parse("cat 'A.md'")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md"]
        assert result.operands[0].quoted is True

    def test_second_quoted_terminator_retains_literal_members(self) -> None:
        result = parse("cat -- A.md '--' B.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A.md", "--", "B.md"]

    def test_option_like_name_after_terminator_is_literal(self) -> None:
        # After the terminator the option parser is off: '-n' is a file
        # label, distinct from the stdin special operand.
        result = parse("cat -- -n")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["-n"]

    def test_literal_dash_paths_are_distinguished_from_stdin(self) -> None:
        result = parse("cat ./- A.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["-", "A.md"]
        absolute = parse("cat /work/-")
        assert absolute.complete is True
        assert [o.normalized for o in absolute.operands] == ["-"]


class TestNonAsciiWhitespaceNotASeparator:
    """Arbitrary Unicode isspace characters are not shell separators."""

    def test_nbsp_token_is_one_ambiguous_label_not_two_files(self) -> None:
        result = parse("cat A.md\u00a0B.md")
        assert result.complete is False
        assert Limitation.AMBIGUOUS_PATH in result.reasons
        normalized = [o.normalized for o in result.operands if o.normalized is not None]
        assert normalized != ["A.md", "B.md"]  # never two fabricated files

    def test_quoted_nbsp_inner_is_typed(self) -> None:
        result = parse('cat "A.md\u00a0B.md"')
        assert result.complete is False
        assert Limitation.QUOTED_OPERAND in result.reasons

    def test_ascii_tab_remains_explicitly_unsupported(self) -> None:
        result = parse("cat A.md\tB.md")
        assert result.complete is False
        assert result.reasons

    def test_carriage_return_remains_typed(self) -> None:
        result = parse("cat A.md\rB.md")
        assert result.complete is False
        assert result.reasons

    def test_valid_unicode_path_preserved(self) -> None:
        result = parse("cat A\u00e9.md")
        assert result.complete is True
        assert [o.normalized for o in result.operands] == ["A\u00e9.md"]


class TestExactOperandLimit:
    """The documented operand bound is exact: up to the limit complete,
    one over typed over-bound."""

    def test_exact_limit_is_complete(self) -> None:
        command = "cat " + " ".join(f"A{i}.md" for i in range(32))
        result = parse(command)
        assert result.complete is True
        assert len(result.operands) == 32
        assert result.distinct_operands == 32
        assert result.reasons == ()

    def test_one_over_limit_is_typed(self) -> None:
        command = "cat " + " ".join(f"A{i}.md" for i in range(33))
        result = parse(command)
        assert result.complete is False
        assert Limitation.COMMAND_OVER_BOUND in result.reasons
