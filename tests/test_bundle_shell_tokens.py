"""D03/D04: bounded literal token lexing — spans, cooked values, privacy."""

from __future__ import annotations

import pathlib

from slaif_local_coding.constitution.bundles import (
    Limitation,
    LiteralToken,
    tokenize_command,
)


class TestTokenRepresentation:
    def test_spans_and_cooked_values_are_separated(self) -> None:
        command = "cat 'A.md' B.md"
        tokens = tokenize_command(command)
        assert [t.value for t in tokens] == ["cat", "A.md", "B.md"]
        assert [t.quoted for t in tokens] == [False, True, False]
        assert all(t.quote_limitation is None and t.operator is None for t in tokens)
        # Raw spans are exact character offsets into the command string;
        # the quoted token's span includes its quote characters.
        assert (tokens[1].raw_start, tokens[1].raw_end) == (4, 10)
        assert command[4:10] == "'A.md'"
        assert (tokens[2].raw_start, tokens[2].raw_end) == (11, 15)

    def test_repr_carries_no_token_text(self) -> None:
        marker = "SYNTHETIC_PRIVATE_MARKER"
        tokens = tokenize_command(f"cat {marker} '{marker}'")
        assert all(isinstance(t, LiteralToken) for t in tokens)
        for token in tokens:
            assert marker not in repr(token)

    def test_ascii_whitespace_only_separates(self) -> None:
        # NBSP is not a shell separator: the label stays one token.
        tokens = tokenize_command("cat A.md\u00a0B.md")
        assert len(tokens) == 2
        assert tokens[1].raw_end - tokens[1].raw_start == len("A.md\u00a0B.md")
        # ASCII tab still separates at the token level (the grammar keeps
        # its explicit control-character rejection).
        tabbed = tokenize_command("cat A.md\tB.md")
        assert [t.value for t in tabbed] == ["cat", "A.md", "B.md"]

    def test_empty_and_whitespace_command_yield_no_tokens(self) -> None:
        assert tokenize_command("") == []
        assert tokenize_command("   ") == []


class TestQuoting:
    def test_clean_single_and_double_quotes(self) -> None:
        for command in ("'A.md'", '"A.md"'):
            token = tokenize_command(command)[0]
            assert token.value == "A.md"
            assert token.quoted is True
            assert token.quote_limitation is None

    def test_empty_quoted_token_is_clean(self) -> None:
        token = tokenize_command("''")[0]
        assert token.value == ""
        assert token.quoted is True
        assert token.quote_limitation is None

    def test_partial_nested_concatenated_quotes_are_typed(self) -> None:
        for command in ('"A.md', 'A"md"', "'A\"md'", "A'md'", "'A.md'x"):
            token = tokenize_command(command)[0]
            assert token.quote_limitation is Limitation.QUOTED_OPERAND, command
            assert token.quoted is False, command

    def test_quoted_inner_metachar_or_space_is_typed(self) -> None:
        for command in ("'A$B.md'", "'A B.md'", '"A*B.md"'):
            token = tokenize_command(command)[0]
            assert token.quote_limitation is Limitation.QUOTED_OPERAND, command


class TestOperatorClassification:
    def test_operators_are_classified_not_executed(self) -> None:
        # Operators are classified per token (whitespace is a separator):
        # each case puts the operator character inside the first token.
        cases = [
            ("A.md|grep x", Limitation.PIPE),
            ("A.md>out", Limitation.REDIRECTION),
            ("A.md&&B.md", Limitation.MULTIPLE_COMMANDS),
            ("A.md;echo hi", Limitation.MULTIPLE_COMMANDS),
            ("A.md&B.md", Limitation.MULTIPLE_COMMANDS),
            ("$A.md", Limitation.COMMAND_SUBSTITUTION),
            ("`ls`", Limitation.COMMAND_SUBSTITUTION),
            ("A*.md", Limitation.GLOB_UNPROVEN),
            ("A?.md", Limitation.GLOB_UNPROVEN),
            ("A#frag", None),  # a mid-token # is a literal filename char
        ]
        for command, expected in cases:
            token = tokenize_command(command)[0]
            assert token.operator is expected, command
        # A standalone pipe token classifies on its own.
        tokens = tokenize_command("cat A.md | grep x")
        assert tokens[2].operator is Limitation.PIPE

    def test_dash_tokens_are_not_operators(self) -> None:
        for value in ("-", "--", "-n", "--number"):
            token = tokenize_command(value)[0]
            assert token.operator is None, value
            assert token.value == value

    def test_leading_hash_is_a_comment(self) -> None:
        assert tokenize_command("# note")[0].operator is Limitation.COMMENT_PRESENT

    def test_backslash_and_braces_are_typed(self) -> None:
        assert tokenize_command("A\\B.md")[0].operator is Limitation.SHELL_ESCAPE
        assert tokenize_command("(A.md)")[0].operator is Limitation.COMMAND_UNSUPPORTED


class TestNoShellExecution:
    def test_module_imports_no_shell_facilities(self) -> None:
        import ast

        source = (
            pathlib.Path("src/slaif_local_coding/constitution/bundles/shell_tokens.py")
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
