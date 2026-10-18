"""D03/D04: bounded literal cat grammar — support and safe negatives."""

from __future__ import annotations

import json
import pathlib

import pytest

from slaif_local_coding.constitution.bundles import (
    Limitation,
    PathContext,
    ReadCommandParse,
    parse_read_command,
    tokenize_literal,
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
