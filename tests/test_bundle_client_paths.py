"""D03/D04 client-path law: literal lexical normalization, no host access."""

from __future__ import annotations

import ast
import pathlib

import pytest

from slaif_local_coding.constitution.bundles import (
    Limitation,
    PathContext,
    normalize_read_path,
    validate_workspace,
)

_CTX = PathContext(workspace="/work")
_SUB_CTX = PathContext(workspace="/work", workdir="/work/sub")


class TestWorkspaceValidation:
    def test_valid_absolute_workspace(self) -> None:
        assert validate_workspace("/work", 256) == "/work"
        assert validate_workspace("/work/", 256) == "/work"
        assert validate_workspace("/work/./docs", 256) == "/work/docs"
        assert validate_workspace("/work/a/b", 256) == "/work/a/b"

    @pytest.mark.parametrize(
        "label",
        [
            "",
            "work",  # relative
            "//work",  # network-style alternate root
            "/work/../x",  # traversal in the workspace itself
            "C:\\work",  # drive root
            "\\\\server\\share",  # UNC
            "/work\\docs",  # backslash alternate syntax
            "~/work",  # tilde, never expanded
            "/work\n",  # control character
            "/wo rk",  # no-spaces convention
        ],
    )
    def test_invalid_workspace_forms_rejected(self, label: str) -> None:
        assert validate_workspace(label, 256) is None

    def test_workspace_bound_enforced(self) -> None:
        assert validate_workspace("/" + "a" * 300, 256) is None


class TestAbsolutePaths:
    def test_simple_absolute_under_workspace(self) -> None:
        result = normalize_read_path("/work/A.md", _CTX, 256)
        assert result.normalized == "A.md"
        assert result.limitation is None
        assert result.form.value == "absolute"

    def test_lexical_dotdot_staying_inside_is_allowed(self) -> None:
        # Documented lexical policy: .. resolves as long as every step stays
        # inside the evidenced workspace.
        result = normalize_read_path("/work/docs/../A.md", _CTX, 256)
        assert result.normalized == "A.md"

    def test_lexical_dotdot_escaping_is_traversal(self) -> None:
        assert normalize_read_path("/work/../etc/A.md", _CTX, 256).limitation is (
            Limitation.TRAVERSAL
        )
        assert normalize_read_path("/work/a/../../A.md", _CTX, 256).limitation is (
            Limitation.TRAVERSAL
        )
        # Escapes and re-enters: still a traversal (a step left the workspace).
        assert normalize_read_path("/work/../work/A.md", _CTX, 256).limitation is (
            Limitation.TRAVERSAL
        )

    def test_sibling_prefix_is_outside(self) -> None:
        # Component comparison, never string-prefix comparison.
        result = normalize_read_path("/work-other/A.md", _CTX, 256)
        assert result.normalized is None
        assert result.limitation is Limitation.OUTSIDE_WORKSPACE

    def test_outside_absolute_path(self) -> None:
        result = normalize_read_path("/etc/A.md", _CTX, 256)
        assert result.limitation is Limitation.OUTSIDE_WORKSPACE

    def test_workspace_root_itself_is_not_a_file(self) -> None:
        assert normalize_read_path("/work", _CTX, 256).limitation is (Limitation.AMBIGUOUS_PATH)


class TestRelativePaths:
    def test_relative_against_evidenced_workspace(self) -> None:
        assert normalize_read_path("A.md", _CTX, 256).normalized == "A.md"
        assert normalize_read_path("./A.md", _CTX, 256).normalized == "A.md"
        assert normalize_read_path("docs/A.md", _CTX, 256).normalized == "docs/A.md"

    def test_relative_with_explicit_supported_workdir(self) -> None:
        assert normalize_read_path("A.md", _SUB_CTX, 256).normalized == "sub/A.md"
        assert normalize_read_path("../A.md", _SUB_CTX, 256).normalized == "A.md"

    def test_relative_without_workspace_is_unproven(self) -> None:
        # No evidenced default client cwd: never an adapter-host cwd.
        assert normalize_read_path("A.md", PathContext(), 256).limitation is (
            Limitation.UNPROVEN_CWD
        )
        assert (
            normalize_read_path("./A.md", PathContext(), 256).limitation is Limitation.UNPROVEN_CWD
        )

    def test_relative_traversal_escape(self) -> None:
        # A .. step at the workspace boundary is traversal, not mere
        # outside-workspace: the resolution step itself left the workspace.
        assert normalize_read_path("../A.md", _CTX, 256).limitation is (Limitation.TRAVERSAL)
        assert normalize_read_path("docs/../../A.md", _CTX, 256).limitation is (
            Limitation.TRAVERSAL
        )

    def test_workdir_must_be_inside_workspace(self) -> None:
        outside = PathContext(workspace="/work", workdir="/elsewhere")
        assert normalize_read_path("A.md", outside, 256).limitation is (
            Limitation.OUTSIDE_WORKSPACE
        )
        bad = PathContext(workspace="/work", workdir="/work/..")
        assert validate_workspace(bad.workdir or "", 256) is None
        result = normalize_read_path("A.md", PathContext(workspace="/work", workdir="sub"), 256)
        assert result.limitation is Limitation.OUTSIDE_WORKSPACE


class TestUnknownWorkspace:
    def test_absolute_with_unknown_workspace(self) -> None:
        assert normalize_read_path("/work/A.md", PathContext(), 256).limitation is (
            Limitation.UNKNOWN_WORKSPACE
        )

    def test_logical_scope_is_not_a_posix_workspace(self) -> None:
        # A root scope label like "repo" is directory identity evidence, not a
        # host mapping: normalization must not invent one.
        logical = PathContext(workspace="repo")
        assert normalize_read_path("/work/A.md", logical, 256).limitation is (
            Limitation.UNKNOWN_WORKSPACE
        )
        assert normalize_read_path("A.md", logical, 256).limitation is (Limitation.UNPROVEN_CWD)


class TestLiteralSemantics:
    def test_url_fragment_is_literal_never_stripped(self) -> None:
        # Preserving literal read-operand semantics: A.md#frag is a different
        # file from A.md; stripping it would map a different read to A.md.
        result = normalize_read_path("A.md#frag", _CTX, 256)
        assert result.normalized == "A.md#frag"

    def test_query_syntax_is_never_mapped_to_the_plain_file(self) -> None:
        # ``?`` is shell glob syntax: the operand is non-literal and typed,
        # never stripped to map a different read onto A.md.
        result = normalize_read_path("A.md?x=1", _CTX, 256)
        assert result.normalized is None
        assert result.limitation is Limitation.NON_LITERAL_OPERAND

    def test_fully_quoted_literal_operand_under_no_spaces_convention(self) -> None:
        result = normalize_read_path('"/work/A.md"', _CTX, 256)
        assert result.normalized == "A.md"
        assert result.quoted is True
        single = normalize_read_path("'/work/A.md'", _CTX, 256)
        assert single.normalized == "A.md"
        assert single.quoted is True

    def test_partial_or_nested_quotes_are_ambiguous(self) -> None:
        assert normalize_read_path('"A.md', _CTX, 256).limitation is (Limitation.QUOTED_OPERAND)
        assert normalize_read_path('A."md"', _CTX, 256).limitation is (Limitation.QUOTED_OPERAND)
        assert normalize_read_path("'A\".md'", _CTX, 256).limitation is (Limitation.QUOTED_OPERAND)

    def test_comment_leading_token_rejected(self) -> None:
        assert normalize_read_path("# A.md", _CTX, 256).limitation is (Limitation.COMMENT_PRESENT)

    def test_metacharacters_make_operands_non_literal(self) -> None:
        for token in ("A*.md", "A?.md", "[A]md", "A$B.md", "A`B`.md", "A\\B.md"):
            result = normalize_read_path(token, _CTX, 256)
            assert result.normalized is None, token
            assert result.limitation is not None, token

    def test_unicode_path_preserved(self) -> None:
        assert normalize_read_path("A\u00e9.md", _CTX, 256).normalized == "A\u00e9.md"
        assert normalize_read_path("/work/A\u00e9.md", _CTX, 256).normalized == ("A\u00e9.md")

    def test_path_bound_enforced(self) -> None:
        long = "A" * 300 + ".md"
        assert normalize_read_path(long, _CTX, 256).limitation is Limitation.PATH_TOO_LONG
        long_abs = "/work/" + "A" * 300 + ".md"
        assert normalize_read_path(long_abs, _CTX, 256).limitation is (Limitation.PATH_TOO_LONG)


class TestNoFilesystemAccess:
    def test_nonexistent_client_paths_still_normalize(self) -> None:
        # Pure lexical normalization: no stat/resolve/read, ever.
        result = normalize_read_path("/work/definitely/not/here.md", _CTX, 256)
        assert result.normalized == "definitely/not/here.md"

    def test_module_imports_no_filesystem_or_shell_facilities(self) -> None:
        source = (
            pathlib.Path("src/slaif_local_coding/constitution/bundles/client_paths.py")
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
        forbidden = {"subprocess", "os", "glob", "shlex", "pathlib", "tempfile", "socket"}
        assert not (imported & forbidden), imported & forbidden


class TestMalformedUnicodeAndSpaces:
    def test_workspace_label_with_lone_surrogate_never_raises(self) -> None:
        # The byte check must not be reached: no UnicodeEncodeError.
        assert validate_workspace("/work/\ud800", 256) is None

    def test_nbsp_path_label_is_typed_ambiguous(self) -> None:
        result = normalize_read_path("A.md\u00a0B.md", _CTX, 256)
        assert result.limitation is Limitation.AMBIGUOUS_PATH
        assert result.normalized is None

    def test_valid_unicode_path_still_normalizes(self) -> None:
        assert normalize_read_path("A\u00e9.md", _CTX, 256).normalized == "A\u00e9.md"
        assert (
            normalize_read_path("/work/\u00fcbers/B.md", _CTX, 256).normalized == "\u00fcbers/B.md"
        )
