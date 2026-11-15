"""018-a: bounded raw-reference scanner — forms, spans, target law, no-partial-token."""

from __future__ import annotations

import hashlib
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    CandidateStatus,
    CandidateSyntax,
    GraphBounds,
    GraphLimitation,
    ReferenceScan,
    resolve_reference,
    scan_references,
)

SK = "a" * 64


def scan(text: str, bounds: GraphBounds | None = None) -> ReferenceScan:
    return scan_references(
        text,
        referring_path="AGENTS.md",
        scoped_key=SK,
        referring_digest=hashlib.sha256(b"synthetic-root").hexdigest(),
        bounds=bounds or GraphBounds(),
    )


def targets(result: ReferenceScan) -> list[str]:
    return [c.target_chars for c in result.candidates]


def accepted(result: ReferenceScan) -> list[str]:
    return [c.target_chars for c in result.candidates if c.status is CandidateStatus.ACCEPTED]


class TestInlineForm:
    def test_inline_plain_target_with_exact_spans(self) -> None:
        text = "see [x](docs/A.md) here"
        r = scan(text)
        assert len(r.candidates) == 1
        c = r.candidates[0]
        assert c.status is CandidateStatus.ACCEPTED
        assert c.syntax is CandidateSyntax.INLINE_LINK
        assert c.target_chars == "docs/A.md"
        assert c.target_char_span.start == text.index("docs/A.md")
        assert c.target_char_span.end == c.target_char_span.start + len("docs/A.md")
        assert c.target_byte_span.end - c.target_byte_span.start == 9

    def test_inline_angle_and_fragment(self) -> None:
        r = scan("[x](<docs/A.md#part>)")
        assert len(r.candidates) == 1
        assert r.candidates[0].target_chars == "docs/A.md#part"
        assert r.candidates[0].status is CandidateStatus.ACCEPTED

    def test_inline_quoted_title(self) -> None:
        r = scan('[x](docs/A.md "Title here")')
        assert accepted(r) == ["docs/A.md"]

    def test_unicode_target_byte_span_law(self) -> None:
        text = "[x](docs/Ä.md)"
        r = scan(text)
        c = r.candidates[0]
        # 'Ä' is two UTF-8 bytes: char length 9, byte length 10.
        assert len(c.target_chars) == 9
        assert c.target_byte_span.end - c.target_byte_span.start == 10


class TestDefinitionForm:
    def test_definition_at_line_start(self) -> None:
        r = scan("[law]: docs/A.md")
        assert accepted(r) == ["docs/A.md"]
        assert r.candidates[0].syntax is CandidateSyntax.REFERENCE_DEFINITION

    def test_indented_definition_up_to_three_spaces(self) -> None:
        assert accepted(scan("   [law]: docs/A.md")) == ["docs/A.md"]
        # Deeper indentation is not a definition; the bare target still
        # scans as plain form on the same line.
        assert accepted(scan("    [law]: docs/A.md")) == ["docs/A.md"]

    def test_definition_crlf(self) -> None:
        r = scan("[law]: docs/A.md\r\nnext [x](docs/B.md)")
        assert accepted(r) == ["docs/A.md", "docs/B.md"]


class TestBacktickForm:
    def test_backtick_path(self) -> None:
        r = scan("use `docs/A.md` here")
        assert accepted(r) == ["docs/A.md"]
        assert r.candidates[0].syntax is CandidateSyntax.BACKTICK_CODE

    def test_backtick_space_inside_is_typed_not_split(self) -> None:
        r = scan("use `docs/A B.md` here")
        assert accepted(r) == []
        assert len(r.candidates) == 1
        assert r.candidates[0].status is CandidateStatus.UNSUPPORTED
        assert r.candidates[0].reasons == (GraphLimitation.MARKUP_QUOTED_SPACE,)

    def test_unclosed_backtick_yields_typed_region_and_recovers(self) -> None:
        r = scan("broken `docs/A.md\nnext [x](docs/SAFE.md)")
        assert accepted(r) == ["docs/SAFE.md"]
        assert any(c.reasons == (GraphLimitation.MARKUP_MISBALANCED,) for c in r.candidates)


class TestPlainForm:
    def test_plain_token_boundary(self) -> None:
        r = scan("Read docs/A.md now.")
        assert accepted(r) == ["docs/A.md"]
        assert r.candidates[0].syntax is CandidateSyntax.PLAIN_PATH

    def test_prose_dots_are_punctuation_not_target(self) -> None:
        r = scan("Read docs/A.md...")
        assert accepted(r) == ["docs/A.md"]

    def test_mid_token_never_rescanned(self) -> None:
        # A tilde mid-token is not a reference start, and the plain
        # lexeme that follows a non-boundary character is never
        # rescanned as its own reference (no suffix minting).
        assert accepted(scan("a~b/docs/A.md")) == []
        assert accepted(scan("Xdocs/A")) == []


class TestTargetLawNegatives:
    @pytest.mark.parametrize(
        ("text", "reason"),
        [
            ("[x](https://example.com/docs/A.md)", GraphLimitation.TARGET_EXTERNAL_SCHEME),
            ("[x](//host/docs/A.md)", GraphLimitation.TARGET_EXTERNAL_HOST),
            ("[x](file:///work/A.md)", GraphLimitation.TARGET_EXTERNAL_SCHEME),
            ("[x](docs/P.md%20q)", GraphLimitation.TARGET_PERCENT_ENCODING),
            ("[x](docs/Q.md\\z)", GraphLimitation.TARGET_BACKSLASH),
            ("[x](docs/A.md?q=1)", GraphLimitation.TARGET_QUERY),
            ("[x](docs/A.md#f#g)", GraphLimitation.TARGET_UNSUPPORTED_CHAR),
            ("Read ~docs/A.md now.", GraphLimitation.TARGET_TILDE_OR_DRIVE),
            ("Read C:/work/A.md now.", GraphLimitation.TARGET_TILDE_OR_DRIVE),
        ],
    )
    def test_typed_negatives_never_mint_local_suffix(
        self, text: str, reason: GraphLimitation
    ) -> None:
        r = scan(text)
        assert accepted(r) == []
        assert any(reason in c.reasons for c in r.candidates)

    def test_external_status_for_scheme_and_tilde(self) -> None:
        for text in ("[x](https://example.com/A.md)", "Read ~docs/A.md now."):
            r = scan(text)
            assert any(c.status is CandidateStatus.EXTERNAL for c in r.candidates), text

    def test_lone_surrogate_refuses_whole_document(self) -> None:
        r = scan("[x](docs/A.md) \ud800")
        assert r.candidates == ()
        assert r.limitation is GraphLimitation.MALFORMED_UNICODE

    def test_control_character_target_typed(self) -> None:
        r = scan("[x](docs/A\x01.md)")
        assert accepted(r) == []
        assert any(c.reasons == (GraphLimitation.TARGET_CONTROL_CHAR,) for c in r.candidates)


class TestNoPartialTokenLaw:
    def test_bare_definition_overlong_refuses_whole_token(self) -> None:
        # ROOT exact case: 20-byte literal destination at 16-byte
        # allowance must not mint its 16-byte prefix as another file.
        target = "A" * 13 + ".mdX.md"
        r = scan("[law]: " + target + "\n", bounds=GraphBounds(max_path_bytes=16))
        assert accepted(r) == []
        assert len(r.candidates) == 1
        assert r.candidates[0].status is CandidateStatus.UNSUPPORTED
        assert r.candidates[0].reasons == (GraphLimitation.PATH_TOO_LONG,)
        assert len(r.candidates[0].target_chars) == 16

    def test_inline_overlong_destination_refused(self) -> None:
        r = scan("[x](" + "A" * 20 + ".md)", bounds=GraphBounds(max_path_bytes=16))
        assert accepted(r) == []
        assert any(c.reasons == (GraphLimitation.PATH_TOO_LONG,) for c in r.candidates)

    def test_angle_overlong_destination_bounded_prefix(self) -> None:
        r = scan("[x](<" + "A" * 30 + ".md>)", bounds=GraphBounds(max_path_bytes=16))
        assert accepted(r) == []
        assert len(r.candidates) == 1
        assert r.candidates[0].reasons == (GraphLimitation.PATH_TOO_LONG,)
        assert len(r.candidates[0].target_chars) == 16

    def test_plain_overlong_lexeme_refused_not_minted(self) -> None:
        r = scan("Read " + "A" * 20 + ".mdX.md now.", bounds=GraphBounds(max_path_bytes=16))
        assert accepted(r) == []
        assert any(c.reasons == (GraphLimitation.PATH_TOO_LONG,) for c in r.candidates)

    def test_overlong_tilde_keeps_typed_external(self) -> None:
        r = scan("Read ~" + "A" * 20 + ".mdX.md now.", bounds=GraphBounds(max_path_bytes=16))
        assert accepted(r) == []
        assert any(c.reasons == (GraphLimitation.TARGET_TILDE_OR_DRIVE,) for c in r.candidates)

    def test_exactly_at_limit_is_at_limit_all_forms(self) -> None:
        token = "A" * 5 + ".md"  # exactly 8 bytes at the 8-byte allowance
        bounds = GraphBounds(max_path_bytes=8)
        assert len(token.encode("utf-8")) == bounds.max_path_bytes
        for text in (
            "[law]: " + token,
            "[x](" + token + ")",
            "[x](<" + token + ">)",
            "Read " + token + " now.",
            "use `" + token + "`",
        ):
            assert accepted(scan(text, bounds)) == [token], text

    def test_one_byte_over_limit_refused(self) -> None:
        token = "A" * 6 + ".md"  # 9 bytes at 8-byte allowance
        bounds = GraphBounds(max_path_bytes=8)
        assert len(token.encode("utf-8")) == bounds.max_path_bytes + 1
        for text in (
            "[law]: " + token,
            "[x](" + token + ")",
            "Read " + token + " now.",
        ):
            assert accepted(scan(text, bounds)) == [], text

    def test_unicode_exactly_at_limit_is_at_limit_all_forms(self) -> None:
        # Literal Unicode filename law: the allowance is in ACTUAL
        # UTF-8 bytes, not characters.  A fullwidth letter (three
        # bytes) keeps the exact eight-byte destination at-limit in
        # every mandatory form (including a Unicode-leading token).
        bounds = GraphBounds(max_path_bytes=8)
        for token in ("d/\uff21.md", "\uff21aa.md"):
            assert len(token.encode("utf-8")) == bounds.max_path_bytes
            assert len(token) < bounds.max_path_bytes  # bytes, not chars
            for text in (
                "[law]: " + token,
                "[law]: <" + token + ">",
                "[x](" + token + ")",
                "[x](<" + token + ">)",
                "Read " + token + " now.",
                "use `" + token + "`",
            ):
                assert accepted(scan(text, bounds)) == [token], text

    def test_unicode_one_byte_over_limit_refused(self) -> None:
        # Nine actual bytes (seven chars) at the eight-byte allowance:
        # ONE typed PATH_TOO_LONG refusal in every form; the
        # byte-bounded prefix is never minted as a shorter file.
        token = "dd/\uff21.md"
        bounds = GraphBounds(max_path_bytes=8)
        assert len(token.encode("utf-8")) == bounds.max_path_bytes + 1
        assert len(token) < bounds.max_path_bytes  # bytes, not chars
        for text in (
            "[law]: " + token,
            "[law]: <" + token + ">",
            "[x](" + token + ")",
            "[x](<" + token + ">)",
            "Read " + token + " now.",
            "use `" + token + "`",
        ):
            r = scan(text, bounds)
            assert accepted(r) == [], text
            too_long = [c for c in r.candidates if c.reasons == (GraphLimitation.PATH_TOO_LONG,)]
            assert too_long, text
            prefix = too_long[0].target_chars
            if "`" in text:
                # backtick form records the full delimited content,
                # classified (never minted) as overlong
                assert prefix == token
                assert too_long[0].status is CandidateStatus.UNSUPPORTED
            else:
                # destination/plain forms carry the byte-bounded prefix
                assert prefix != token, text
                assert len(prefix.encode("utf-8")) <= bounds.max_path_bytes, text


class TestBudgetAndDedup:
    def test_per_document_at_limit_has_no_limitation(self) -> None:
        text = "[x](docs/A.md) [y](docs/B.md)"
        r = scan(text, bounds=GraphBounds(max_reference_candidates_per_document=2))
        assert len(r.candidates) == 2
        assert r.limitation is None

    def test_per_document_one_over_stops_and_limits(self) -> None:
        text = "[x](docs/A.md) [y](docs/B.md) [z](docs/C.md)"
        r = scan(text, bounds=GraphBounds(max_reference_candidates_per_document=2))
        assert len(r.candidates) == 2
        assert r.limitation is GraphLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND

    def test_repeated_targets_preserve_occurrence_evidence(self) -> None:
        r = scan("[x](docs/A.md) and again [y](docs/A.md)")
        assert len(r.candidates) == 2
        assert [c.occurrence_index for c in r.candidates] == [0, 1]
        assert all(c.target_chars == "docs/A.md" for c in r.candidates)

    def test_markup_plain_overlap_same_span_deduped(self) -> None:
        # The inline link span and a plain-looking interior never emit
        # two records over the same span.
        r = scan("[x](docs/A.md)")
        spans = [(c.target_char_span.start, c.target_char_span.end) for c in r.candidates]
        assert len(spans) == len(set(spans))


class TestResolverBoundary:
    def test_fragment_stripped_for_resolution_only(self) -> None:
        assert resolve_reference("AGENTS.md", "docs/A.md#frag", "/work", 4096) == (
            "docs/A.md",
            None,
        )

    def test_safe_parent_reference_inside_workspace(self) -> None:
        assert resolve_reference("docs/A.md", "../SECURITY.md", "/work", 4096) == (
            "SECURITY.md",
            None,
        )

    def test_traversal_below_workspace_refused(self) -> None:
        assert resolve_reference("docs/A.md", "../../EVIL.md", "/work", 4096)[1] is (
            GraphLimitation.PATH_TRAVERSAL
        )

    def test_workspace_lookalike_refused(self) -> None:
        assert resolve_reference("docs/A.md", "/work-other/EVIL.md", "/work", 4096)[1] is (
            GraphLimitation.PATH_OUTSIDE_WORKSPACE
        )

    def test_absolute_inside_workspace_accepted(self) -> None:
        assert resolve_reference("docs/A.md", "/work/ROOT.md", "/work", 4096) == (
            "ROOT.md",
            None,
        )


class TestBoundedSearchWork:
    """Tiny deterministic scanner search-work regressions (no timing claim).

    A str-subclass spy records every ``find``/``rfind`` window executed
    on the ORIGINAL text object and every ``text[0:stop]`` prefix copy.
    These are minimal input-size work bounds (linear, not quadratic),
    not a full work proof and never a wall-clock measurement.
    """

    class _Spy(str):
        def __init__(self, value: str) -> None:
            self.windows: list[tuple[str, int]] = []
            self.prefix_slices: list[int] = []

        def find(self, sub: str, start: Any = None, end: Any = None) -> int:
            s = 0 if start is None else int(start)
            e = len(self) if end is None else int(end)
            stop = min(e, len(self))
            self.windows.append((repr(sub), max(0, stop - s)))
            return super().find(sub, s) if end is None else super().find(sub, s, e)

        def rfind(self, sub: str, start: Any = None, end: Any = None) -> int:
            s = 0 if start is None else int(start)
            e = len(self) if end is None else int(end)
            stop = min(e, len(self))
            self.windows.append(("rfind" + repr(sub), max(0, stop - s)))
            return super().rfind(sub, s) if end is None else super().rfind(sub, s, e)

        def __getitem__(self, key: Any) -> str:
            if isinstance(key, slice) and key.start == 0 and key.stop is not None:
                self.prefix_slices.append(key.stop)
            return super().__getitem__(key)

    def _scan(self, text: _Spy, bounds: GraphBounds) -> ReferenceScan:
        return scan_references(
            text,
            referring_path="ROOT.md",
            scoped_key=SK,
            referring_digest=hashlib.sha256(text.encode()).hexdigest(),
            bounds=bounds,
        )

    def test_unclosed_labels_search_bounded_label_windows(self) -> None:
        # 64 unmatched '[': every closing-bracket search stays inside
        # the declared label window (the old unbounded full-tail search
        # was quadratic in the document length).
        bounds = GraphBounds(max_path_bytes=16)
        n = 64
        text = self._Spy("[" * n)
        r = self._scan(text, bounds)
        assert r.limitation is None
        assert len(r.candidates) == 0
        close = [w for sub, w in text.windows if sub == "']'"]
        assert close, "the label form must perform bracket searches"
        assert max(close) <= bounds.max_path_bytes + 1
        assert sum(close) <= n * (bounds.max_path_bytes + 1)
        assert max(w for _, w in text.windows) <= bounds.max_path_bytes + 1

    def test_definition_lines_copy_no_quadratic_prefix(self) -> None:
        # Repeated '[x]:' lines: the indent check must not copy the
        # growing text prefix (the old text[0:pos] charged O(n^2)).
        bounds = GraphBounds(max_path_bytes=16)
        for n in (64, 128):
            text = self._Spy("[x]:" * n)
            r = self._scan(text, bounds)
            assert r.limitation is None
            assert len(r.candidates) == 0
            assert sum(text.prefix_slices) <= n  # linear, not quadratic
            assert max(w for _, w in text.windows) <= bounds.max_path_bytes + 1

    def test_short_unclosed_angle_is_typed_not_a_crash(self) -> None:
        # No closing delimiter at all inside the bounded window: a
        # fixed typed refusal at the bounded prefix, never an exception
        # or an unbounded tail search.
        text = self._Spy("[x](<A.md")
        r = self._scan(text, GraphBounds())
        assert r.limitation is None
        assert accepted(r) == []

    def test_overlong_angle_mints_no_safe_prefix(self) -> None:
        # A 9-byte destination at the 8-byte cap: ONE typed
        # path-too-long record over the whole destination — the bounded
        # prefix is never minted as another accepted file.
        bounds = GraphBounds(max_path_bytes=8)
        r = self._scan(self._Spy("[x](<Aaaaaa.md>)"), bounds)
        assert accepted(r) == []
        assert len(r.candidates) == 1
        c = r.candidates[0]
        assert c.status is CandidateStatus.UNSUPPORTED
        assert c.reasons == (GraphLimitation.PATH_TOO_LONG,)
        assert c.target_chars == "Aaaaaa.m"

    def test_absolute_workspace_directory_itself_refused(self) -> None:
        assert resolve_reference("docs/A.md", "/work", "/work", 4096)[1] is (
            GraphLimitation.PATH_OUTSIDE_WORKSPACE
        )

    def test_fragment_only_target_refused(self) -> None:
        assert resolve_reference("AGENTS.md", "#only", "/work", 4096)[1] is (
            GraphLimitation.TARGET_UNSUPPORTED_CHAR
        )

    def test_overlong_target_refused_at_resolver(self) -> None:
        assert resolve_reference("AGENTS.md", "d" * 5000 + ".md", "/work", 4096)[1] is (
            GraphLimitation.PATH_TOO_LONG
        )
