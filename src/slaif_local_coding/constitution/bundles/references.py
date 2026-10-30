"""Bounded raw-reference scanner for the 018-a graph foundation.

Operates on raw proven document text (the exact observed source string)
BEFORE any compiler/ranking.  Pure and inert: no dependency/CommonMark
engine, no network, no filesystem, no model, no shell.  The scan is
linear and bounded: every position advances at least one character, all
spans are bounded by ``GraphBounds.max_path_bytes``, and the
per-document candidate count is decided before further retention.
Every delimiter search (label ``]``, line end, angle ``>``, title
quote) is bounded to the DECLARED window its grammar allows (the
destination/label/title allowance), never the whole remaining text:
a delimiter provably unreachable inside that window is the same typed
case as absence, so the work charged per lexeme is O(allowance) and
the total scan stays O(text length x allowance) for any input.

Maximal-lexeme law (R5): an unsafe enclosing lexeme is consumed and
classified BEFORE any safe substring can be scanned.  A full external
URL with ``.md`` is one typed ``EXTERNAL`` record — never a local
suffix edge; ``docs/A.md?query`` is one typed ``TARGET_QUERY`` record —
never a ``docs/A.md`` candidate.  Path-like unsupported backtick spans
and malformed markup containing an apparent ``.md`` target yield fixed
typed limitations with NO permissive plain fallback; genuinely
non-path content is not a reference and carries no diagnostic.  No
apparent unsupported ``.md`` target is silently dropped without its
typed record.

Target law: a literal POSIX repository reference ending lowercase
``.md`` before an optional ``#fragment``.  Fragments are stripped for
reference resolution ONLY (graph law); the scanner retains the exact
observed target characters as protected internal metadata and the exact
character/UTF-8 byte spans.  No percent/HTML/entity/backslash decoding,
no URL fetching, no path expansion, no query stripping.

Forms (exact):
(a) inline ``[label](target)`` — optional matching angle brackets
    around the target and an optional bounded single/double-quoted
    title; the label is bounded non-``]`` non-newline text (empty
    allowed);
(b) ``[label]: target`` definitions at line start with indent <= 3
    spaces, same bounded destination/title grammar;
(c) backtick code spans (matched run of exactly N backticks, no
    newline inside) containing exactly one no-spaces ``.md`` path; an
    apparent-``.md`` span whose content is not exactly one no-spaces
    path (a space or tab inside), or an unclosed run, yields ONE typed
    UNSUPPORTED record over the exact bounded span/region with NO plain
    fallback; genuinely non-path content yields nothing (not an error);
(d) plain no-spaces ``.md`` path tokens at token boundaries — the
    maximal ASCII reference-like lexeme (a non-ASCII ``.md`` target
    must use a bounded form), optionally surrounded by ordinary
    quotes/punctuation (at most three trailing prose dots are
    punctuation, never target).
(e) enclosing tokens: a double- or single-quoted span at a token
    boundary is one lexeme — a space/tab-bearing content with an
    apparent ``.md`` target earns ONE typed UNSUPPORTED record with NO
    inner plain scan; a clean (no-space) span leaves its interior
    available to form (d); a tilde-leading token (``~/...``) is one
    maximal lexeme classified as typed EXTERNAL (never dropped); an
    unclosed ``[`` whose line holds an apparent ``.md`` target is one
    typed malformed region with NO inner plain scan.

Destination-byte law: delimiter/label characters (brackets, backticks,
quotes) NEVER consume the destination byte allowance — only the
destination's own UTF-8 byte length counts against
``max_path_bytes`` (exactly-at-limit is at-limit; over-limit is a
typed ``PATH_TOO_LONG``).

No-partial-token law: a destination or maximal lexeme that provably
continues past the allowance is ONE typed ``PATH_TOO_LONG`` over the
bounded prefix (tilde tokens keep their typed EXTERNAL record) — its
capped prefix is never minted as a shorter file, and the scan resumes
after the full lexeme with no inner plain fallback.
"""

from __future__ import annotations

from pydantic import Field

from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    CandidateStatus,
    CandidateSyntax,
    GraphBounds,
    GraphLimitation,
    ReferenceCandidate,
)
from .observation_models import CharSpan, _Frozen, contains_lone_surrogates, utf8_byte_span

#: Path characters of the strict plain/inline POSIX shape.
_PATH_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-/")
#: Characters that make an enclosing lexeme unsafe/reference-like.
_UNSAFE_LEXEME = frozenset(":%\\?&=+!;@*")
#: Full reference-like lexeme (path chars + unsafe chars + fragment).
_LEXEME = _PATH_CHARS | _UNSAFE_LEXEME | frozenset("#")
#: Preceding characters that still count as a plain-token boundary.
_BOUNDARY_BEFORE = frozenset(" \t\r\n([{<'\"`")
#: Lexeme set for a tilde-leading maximal token (external law).
_TILDE_LEXEME = _LEXEME | frozenset("~")
_SCHEME_PREFIX = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.-")
_TITLE_MAX = 4096


def _plain_lexeme_char(char: str) -> bool:
    """One maximal plain-lexeme character: the ASCII reference set or
    one non-ASCII name character (literal Unicode filename law)."""
    return char in _LEXEME or (ord(char) > 0x7E and not char.isspace())


def _tilde_lexeme_char(char: str) -> bool:
    """One maximal tilde-lexeme character (the plain set plus ``~``)."""
    return char in _TILDE_LEXEME or (ord(char) > 0x7E and not char.isspace())


class ReferenceScan(_Frozen):
    """Bounded scan result for one acquired document.

    ``limitation`` is set only for whole-document typed refusals
    (``MALFORMED_UNICODE`` before any scan, or
    ``CANDIDATES_PER_DOCUMENT_OVER_BOUND`` once the per-document budget
    is exhausted; the scan then stops and retains nothing further).
    """

    candidates: tuple[ReferenceCandidate, ...] = ()
    limitation: GraphLimitation | None = None
    scanned_chars: int = Field(default=0, ge=0)


def _is_md_like(token: str) -> bool:
    return ".md" in token


def _strict_path_shape(path_portion: str) -> bool:
    """Strict literal POSIX ``.md`` path shape (relative or absolute).

    Path characters are the ASCII set plus any non-ASCII character that
    is not a space (unicode filename law); control characters, ASCII
    whitespace and every typed-refusal character keep their exact
    classification.  No normalization, decoding or expansion.
    """
    if not path_portion:
        return False
    if any(not _path_char_ok(c) for c in path_portion):
        return False
    if path_portion.endswith("/"):
        return False
    body = path_portion[1:] if path_portion.startswith("/") else path_portion
    if not body:
        return False
    if any(segment == "" for segment in body.split("/")):
        return False
    return path_portion.endswith(".md")


def _path_char_ok(char: str) -> bool:
    """One literal POSIX path character (ASCII set or non-ASCII name char)."""
    if char in _PATH_CHARS:
        return True
    code = ord(char)
    return code > 0x7E and not char.isspace()


def classify_target(
    target: str, max_path_bytes: int
) -> tuple[CandidateStatus, GraphLimitation | None]:
    """Classify one delimited reference target under the target law.

    Returns ``(status, reason)``: ``ACCEPTED`` for the strict shape,
    ``EXTERNAL`` for scheme/``//host``/tilde/drive forms, otherwise
    ``UNSUPPORTED`` with the exact typed reason.  No decoding, no
    expansion, no fetching; the caller retains the exact characters.
    """
    if not target:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_EMPTY
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in target):
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_CONTROL_CHAR
    if contains_lone_surrogates(target):
        return CandidateStatus.UNSUPPORTED, GraphLimitation.MALFORMED_UNICODE
    if target.startswith("~"):
        return CandidateStatus.EXTERNAL, GraphLimitation.TARGET_TILDE_OR_DRIVE
    if target.startswith("//"):
        return CandidateStatus.EXTERNAL, GraphLimitation.TARGET_EXTERNAL_HOST
    for index, char in enumerate(target):
        if char != ":":
            continue
        if index == 0:
            return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_UNSUPPORTED_CHAR
        if index == 1 and target[0].isascii() and target[0].isalpha():
            return CandidateStatus.EXTERNAL, GraphLimitation.TARGET_TILDE_OR_DRIVE
        if all(c in _SCHEME_PREFIX for c in target[:index]):
            return CandidateStatus.EXTERNAL, GraphLimitation.TARGET_EXTERNAL_SCHEME
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_UNSUPPORTED_CHAR
    if "%" in target:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_PERCENT_ENCODING
    if "\\" in target:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_BACKSLASH
    if "?" in target:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_QUERY
    if target.count("#") > 1:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_UNSUPPORTED_CHAR
    path_portion = target.split("#", 1)[0]
    if not _strict_path_shape(path_portion):
        return CandidateStatus.UNSUPPORTED, GraphLimitation.TARGET_UNSUPPORTED_CHAR
    if len(path_portion.encode("utf-8")) > max_path_bytes:
        return CandidateStatus.UNSUPPORTED, GraphLimitation.PATH_TOO_LONG
    return CandidateStatus.ACCEPTED, None


def _strip_prose_dots(core: str) -> tuple[str, int]:
    """Strip at most three trailing prose dots (sentence punctuation)."""
    stripped = 0
    while stripped < 3 and core.endswith("."):
        core = core[:-1]
        stripped += 1
    return core, stripped


def _utf8_char_len(char: str) -> int:
    """UTF-8 byte length of one code point (input is surrogate-free)."""
    cp = ord(char)
    if cp < 0x80:
        return 1
    if cp < 0x800:
        return 2
    if cp < 0x10000:
        return 3
    return 4


def _parse_destination(
    text: str, start: int, limit: int, max_path_bytes: int, close_char: str | None
) -> tuple[str, int, int, int, GraphLimitation | None, bool]:
    """Parse one bounded destination (inline or definition).

    ``close_char`` is ``")"`` for inline links and ``None`` for
    definitions.  Returns ``(target, target_start, target_end,
    consumed_end, reason, close_consumed)``: ``target`` is the exact
    destination characters (brackets excluded for angle form),
    ``consumed_end`` the first position after the destination (before
    any title), ``reason`` a grammar refusal (``None`` when the
    destination itself is well-formed; target-law classification
    happens afterwards), and ``close_consumed`` whether the exact
    closing delimiter was already consumed (no title can follow).

    No-partial-token: a destination that provably continues past
    ``max_path_bytes`` returns ``PATH_TOO_LONG`` over the bounded
    prefix (never a minted shorter file); for the angle form
    ``consumed_end`` resumes after the closing ``>``.
    """
    if start >= limit:
        return "", start, start, start, GraphLimitation.TARGET_EMPTY, False
    if text[start] == "<":
        # Declared destination window: the delimiters never consume the
        # allowance, so a well-formed angle destination of at most
        # ``max_path_bytes`` characters closes at index
        # ``start + 1 + max_path_bytes`` at the latest; both delimiter
        # searches are bounded to that window (searching the whole tail
        # is unowned work, quadratic over repeated unclosed angle
        # starts).
        window_end = start + 1 + max_path_bytes
        close = text.find(">", start + 1, window_end + 1)
        newline = text.find("\n", start + 1, window_end + 1)
        if close < 0 and newline < 0:
            if window_end >= limit:
                # The text ends before any delimiter: a missing
                # delimiter (the allowance was never exceeded), same
                # typed malformed case as a far search would find.
                return "", start, start, start + 1, GraphLimitation.MARKUP_MISBALANCED, False
            # Neither delimiter inside the declared window while the
            # text continues past it: the destination provably
            # continues past the allowance.  ONE typed PATH_TOO_LONG
            # over the bounded prefix (no-partial-token law); resume
            # after the bounded prefix.  ``window_end < limit`` keeps
            # the walk inside the actual text.
            byte_count = 0
            cut = start + 1
            k = start + 1
            while k < window_end:
                blen = _utf8_char_len(text[k])
                if byte_count + blen > max_path_bytes:
                    break
                byte_count += blen
                cut = k + 1
                k += 1
            return (
                text[start + 1 : cut],
                start + 1,
                cut,
                window_end,
                GraphLimitation.PATH_TOO_LONG,
                False,
            )
        if close < 0 or (newline >= 0 and newline < close):
            # Missing delimiter or a line break inside: malformed.
            return "", start, start, start + 1, GraphLimitation.MARKUP_MISBALANCED, False
        # The angle delimiters never consume the destination byte
        # allowance.  Measure the destination's own UTF-8 byte length
        # up to allowance+1 without slicing the overlong tail:
        # exactly-at-limit is at-limit; a destination that provably
        # continues past the allowance is ONE typed PATH_TOO_LONG over
        # the bounded prefix, never a minted shorter file.
        byte_count = 0
        cut = start + 1
        k = start + 1
        while k < close:
            blen = _utf8_char_len(text[k])
            if byte_count + blen > max_path_bytes:
                break
            byte_count += blen
            cut = k + 1
            k += 1
        if k < close:
            return (
                text[start + 1 : cut],
                start + 1,
                cut,
                close + 1,
                GraphLimitation.PATH_TOO_LONG,
                False,
            )
        return text[start + 1 : close], start + 1, close, close + 1, None, False
    j = start
    byte_count = 0
    while j < limit and text[j] not in " \t\r\n" and (close_char is None or text[j] != close_char):
        blen = _utf8_char_len(text[j])
        if byte_count + blen > max_path_bytes:
            break
        byte_count += blen
        j += 1
    if j == start:
        if (
            j < limit
            and text[j] not in " \t\r\n"
            and (close_char is None or text[j] != close_char)
            and _utf8_char_len(text[j]) > max_path_bytes
        ):
            # One destination character alone exceeds the whole byte
            # allowance: the same typed overlong refusal (no minted
            # prefix).
            return "", start, start, start, GraphLimitation.PATH_TOO_LONG, False
        return "", start, start, start, GraphLimitation.TARGET_EMPTY, False
    # No-partial-token law: the destination provably continues past
    # the BYTE allowance (the next character is still destination
    # material).  The WHOLE token is overlong: ONE typed
    # PATH_TOO_LONG over the bounded prefix — its capped prefix is
    # never minted as a shorter file, and no plain fallback scans
    # the remainder of the same lexeme.
    if j < limit and text[j] not in " \t\r\n" and (close_char is None or text[j] != close_char):
        return "", start, j, j, GraphLimitation.PATH_TOO_LONG, False
    target = text[start:j]
    if j < limit and close_char is not None and text[j] == close_char:
        return target, start, j, j + 1, None, True
    if j < limit and text[j] in " \t":
        # A bare destination may be followed by whitespace, then an
        # optional quoted title and the exact closing bracket (inline).
        return target, start, j, j, None, False
    # The run ended at end-of-text or a newline: a definition target
    # ends its line there (complete); an inline target never does.
    if close_char is None:
        return target, start, j, j, None, True
    return "", start, j, j, GraphLimitation.MARKUP_MISBALANCED, False


def _parse_title_and_close(
    text: str, pos: int, limit: int, inline: bool
) -> tuple[int, GraphLimitation | None]:
    """Optional bounded quoted title, then the exact closing delimiter.

    ``inline`` requires exactly ``)`` after the optional title; a
    definition line must end (trailing spaces allowed) after it.
    """
    j = pos
    if j < limit and inline and text[j] == ")":
        return j + 1, None
    if j < limit and text[j] in " \t":
        while j < limit and text[j] in " \t":
            j += 1
        if j < limit and text[j] in "\"'":
            quote = text[j]
            # A valid title closes within ``_TITLE_MAX`` characters
            # (longer is malformed by length): bound the search to the
            # declared title window; a quote only beyond it is the
            # same malformed case as -1.
            close = text.find(quote, j + 1, j + 1 + _TITLE_MAX)
            if close < 0 or close - j > _TITLE_MAX or "\n" in text[j : close + 1]:
                return j, GraphLimitation.MARKUP_MISBALANCED
            j = close + 1
            if inline:
                if j < limit and text[j] == ")":
                    return j + 1, None
                return j, GraphLimitation.MARKUP_MISBALANCED
        while j < limit and text[j] in " \t":
            j += 1
        if j < limit and text[j] != "\n":
            return j, GraphLimitation.MARKUP_MISBALANCED
        return j, None
    if inline:
        return j, GraphLimitation.MARKUP_MISBALANCED
    if j < limit and text[j] != "\n" and not text[j].isspace():
        return j, GraphLimitation.MARKUP_MISBALANCED
    return j, None


def _line_start_with_indent(text: str, pos: int) -> int | None:
    """Return ``pos`` if a definition line starts there (indent <= 3).

    The line starts after the last newline (or at 0); every character
    between the line start and ``pos`` must be a plain space, at most
    three of them.  Tabs or deeper indentation disqualify the line as a
    definition (its text remains available to the plain form).
    """
    # The indent allowance (<= 3 spaces) bounds both the backwards
    # search and the inspected characters: a newline further back than
    # four characters can only disqualify, so at most four characters
    # are inspected and the indent is checked in place (never copied —
    # a ``text[0:pos]`` prefix copy charged O(pos) per candidate
    # definition line on newline-free text).
    line_start = 0
    for offset in range(1, 5):
        if pos - offset >= 0 and text[pos - offset] == "\n":
            line_start = pos - offset + 1
            break
    if line_start == 0 and pos > 3:
        # No nearby newline and the prefix already exceeds the three-
        # space allowance: disqualified without inspecting it.
        return None
    for char_index in range(line_start, pos):
        if text[char_index] != " ":
            return None
    return pos


def scan_references(
    text: str,
    *,
    referring_path: str | None,
    scoped_key: str,
    referring_digest: str | None,
    bounds: GraphBounds,
) -> ReferenceScan:
    """Scan one acquired document for the four bounded reference forms.

    ``referring_path`` / ``referring_digest`` are ``None`` only for
    boundaryless multi-member bundles (unresolved-origin candidates
    with no attributable referring document).
    """
    if contains_lone_surrogates(text):
        return ReferenceScan(limitation=GraphLimitation.MALFORMED_UNICODE, scanned_chars=0)

    limit = len(text)
    max_path_bytes = bounds.max_path_bytes
    per_doc_limit = bounds.max_reference_candidates_per_document
    emitted: list[ReferenceCandidate] = []
    emitted_spans: list[tuple[int, int]] = []
    occurrence_index = 0
    budget_exceeded = False
    i = 0

    def emit(
        start: int,
        end: int,
        syntax: CandidateSyntax,
        raw_target: str,
        reason: GraphLimitation | None = None,
    ) -> bool:
        """Emit one candidate record; enforce the per-document budget.

        At-limit is at-limit: a document with exactly the configured
        number of candidates carries NO limitation.  ``False`` (with
        the over-bound flag set) is returned only when a further
        distinct candidate would exceed the budget.
        """
        nonlocal occurrence_index, budget_exceeded
        if (start, end) in emitted_spans:
            return True  # same-occurrence dedup (markup/plain overlap)
        if len(emitted) >= per_doc_limit:
            budget_exceeded = True
            return False
        status, classified = classify_target(raw_target, max_path_bytes)
        if reason is not None:
            status = (
                CandidateStatus.EXTERNAL
                if reason
                in (
                    GraphLimitation.TARGET_EXTERNAL_SCHEME,
                    GraphLimitation.TARGET_EXTERNAL_HOST,
                    GraphLimitation.TARGET_TILDE_OR_DRIVE,
                )
                else CandidateStatus.UNSUPPORTED
            )
            classified = reason
        if classified is None:
            classified = (
                GraphLimitation.TARGET_UNSUPPORTED_CHAR
                if status is CandidateStatus.UNSUPPORTED
                else None
            )
        byte_start, byte_end = utf8_byte_span(text, start, end)
        byte_span = CharSpan(start=byte_start, end=byte_end)
        emitted_spans.append((start, end))
        emitted.append(
            ReferenceCandidate(
                referring_path=referring_path,
                scoped_key=scoped_key,
                referring_digest=referring_digest,
                syntax=syntax,
                target_chars=raw_target,
                target_char_span=CharSpan(start=start, end=end),
                target_byte_span=byte_span,
                resolved_path=None,
                status=status,
                reasons=(classified,) if classified is not None else (),
                occurrence_index=occurrence_index,
                graph_version=GRAPH_CONTRACT_VERSION,
            )
        )
        occurrence_index += 1
        return True

    def malformed_region(
        start: int,
        syntax: CandidateSyntax,
        reason: GraphLimitation,
        region_end: int | None = None,
    ) -> int:
        """Typed record over the bounded apparent-reference region.

        The PROVEN region end is the end of the current line (or end of
        text) capped by ``max_path_bytes``; the caller resumes scanning
        there so independent references after the malformed region are
        still found.  Returns the next scan position, or ``-1`` when
        the per-document budget is exhausted (the caller stops).  No
        permissive plain fallback inside the region (R5 law).
        """
        if region_end is None:
            # The proven region is capped at ``start + max_path_bytes``:
            # a newline beyond that cap cannot change ``region_end``.
            line_end = text.find("\n", start, start + max_path_bytes)
            boundary = line_end if line_end >= 0 else limit
            region_end = min(boundary, start + max_path_bytes)
        region_end = max(min(region_end, limit), start + 1)
        if _is_md_like(text[start:region_end]):
            keep = emit(start, region_end, syntax, text[start:region_end], reason)
            if not keep:
                return -1
        return region_end

    while i < limit:
        char = text[i]
        if char == "[":
            # Declared label window: a valid label span (brackets
            # inclusive) is at most ``max_path_bytes`` characters and
            # cannot cross a newline, so the closing bracket is
            # provably inside this window.  A bracket only reachable
            # beyond it is the same unclosed/overlong case as -1, so
            # the bounded search keeps the decision while charging
            # bounded work (the unbounded tail search was quadratic
            # over repeated unmatched '[').
            label_end = text.find("]", i + 1, i + max_path_bytes + 1)
            label_ok = (
                label_end >= i + 1
                and label_end - i <= max_path_bytes
                and "\n" not in text[i : label_end + 1]
            )
            if not label_ok:
                # An unclosed or overlong label whose line holds an
                # apparent .md target is ONE typed malformed region
                # (R5 law: no permissive plain fallback inside it);
                # otherwise the bracket is not a reference.
                # The proven region is capped at ``i + max_path_bytes``,
                # so a newline beyond that cap cannot change
                # ``region_end``: bound the search to the same window.
                line_end = text.find("\n", i, i + max_path_bytes)
                boundary = line_end if line_end >= 0 else limit
                region_end = min(boundary, i + max_path_bytes)
                if _is_md_like(text[i:region_end]):
                    new_i = malformed_region(
                        i,
                        CandidateSyntax.INLINE_LINK,
                        GraphLimitation.MARKUP_MISBALANCED,
                        region_end,
                    )
                    if new_i < 0:
                        break
                    i = new_i
                    continue
                i += 1
                continue
            j = label_end + 1
            if j < limit and text[j] == "(":
                target, t_start, t_end, consumed, grammar_reason, close_consumed = (
                    _parse_destination(text, j + 1, limit, max_path_bytes, ")")
                )
                if grammar_reason is None and not close_consumed:
                    final, close_reason = _parse_title_and_close(text, consumed, limit, True)
                    grammar_reason = close_reason
                    if close_reason is None:
                        consumed = final
                if grammar_reason is None:
                    if _is_md_like(target):
                        keep = emit(t_start, t_end, CandidateSyntax.INLINE_LINK, target)
                        i = max(consumed, i + 2)
                        if not keep:
                            break
                        continue
                    i = max(consumed, i + 2)
                    continue
                if grammar_reason is GraphLimitation.PATH_TOO_LONG:
                    # The WHOLE delimited destination is overlong: one
                    # typed record over the bounded destination prefix
                    # (never minted as a shorter file); resume after
                    # the delimited token, no inner plain fallback.
                    keep = emit(
                        t_start,
                        t_end,
                        CandidateSyntax.INLINE_LINK,
                        text[t_start:t_end],
                        GraphLimitation.PATH_TOO_LONG,
                    )
                    if not keep:
                        break
                    i = max(consumed, i + 2)
                    continue
                new_i = malformed_region(i, CandidateSyntax.INLINE_LINK, grammar_reason)
                if new_i < 0:
                    break
                i = new_i
                continue
            if j < limit and text[j] == ":":
                def_start = _line_start_with_indent(text, i)
                if def_start is not None and j + 1 < limit and text[j + 1] in " \t":
                    k = j + 1
                    while k < limit and text[k] in " \t":
                        k += 1
                    target, t_start, t_end, consumed, grammar_reason, close_consumed = (
                        _parse_destination(text, k, limit, max_path_bytes, None)
                    )
                    if grammar_reason is None and not close_consumed:
                        final, close_reason = _parse_title_and_close(text, consumed, limit, False)
                        grammar_reason = close_reason
                    if grammar_reason is None:
                        if _is_md_like(target):
                            keep = emit(
                                t_start, t_end, CandidateSyntax.REFERENCE_DEFINITION, target
                            )
                            i = max(consumed, i + 2)
                            if not keep:
                                break
                            continue
                        i = max(consumed, i + 2)
                        continue
                    if grammar_reason is GraphLimitation.PATH_TOO_LONG:
                        # The WHOLE delimited destination is overlong:
                        # one typed record over the bounded destination
                        # prefix (never minted as a shorter file);
                        # resume after the destination, no inner plain
                        # fallback.
                        keep = emit(
                            t_start,
                            t_end,
                            CandidateSyntax.REFERENCE_DEFINITION,
                            text[t_start:t_end],
                            GraphLimitation.PATH_TOO_LONG,
                        )
                        if not keep:
                            break
                        i = max(consumed, i + 2)
                        continue
                    new_i = malformed_region(
                        i, CandidateSyntax.REFERENCE_DEFINITION, grammar_reason
                    )
                    if new_i < 0:
                        break
                    i = new_i
                    continue
                i = j + 1
                continue
            i = j
            continue
        if char == "`":
            # Form (c): backtick run of exactly N, matched close.
            n = 0
            while i + n < limit and text[i + n] == "`":
                n += 1
            search_from = i + n
            # The closing run starts after the destination; the
            # destination's own byte allowance (at most max_path_bytes
            # characters) plus the closing run of n backticks bounds
            # the search — the delimiters do not consume the
            # destination byte allowance.
            scan_bound = min(limit, search_from + max_path_bytes + n)
            close = -1
            k = search_from
            while k < scan_bound:
                if text[k] == "`":
                    run = 0
                    while k + run < limit and text[k + run] == "`":
                        run += 1
                    if run == n and "\n" not in text[search_from:k]:
                        close = k
                        break
                    k += run
                else:
                    k += 1
            if close < 0:
                # Unclosed run: malformed; a backtick span cannot cross
                # a newline, so the proven boundary is the next newline
                # (or end of text), capped by max_path_bytes — so the
                # newline search is bounded to the same window.  An
                # apparent .md target inside earns one typed record;
                # NO plain fallback over the malformed region.
                line_end = text.find("\n", search_from, search_from + max_path_bytes)
                boundary = line_end if line_end >= 0 else limit
                region_end = max(min(boundary, search_from + max_path_bytes), search_from + 1)
                if _is_md_like(text[search_from:region_end]):
                    new_i = malformed_region(
                        search_from,
                        CandidateSyntax.BACKTICK_CODE,
                        GraphLimitation.MARKUP_MISBALANCED,
                        region_end,
                    )
                    if new_i < 0:
                        break
                    i = new_i
                    continue
                i = region_end
                continue
            content = text[search_from:close]
            if content and _is_md_like(content):
                if " " in content or "\t" in content:
                    keep = emit(
                        search_from,
                        close,
                        CandidateSyntax.BACKTICK_CODE,
                        content,
                        GraphLimitation.MARKUP_QUOTED_SPACE,
                    )
                    if not keep:
                        break
                else:
                    keep = emit(search_from, close, CandidateSyntax.BACKTICK_CODE, content)
                    if not keep:
                        break
            i = close + n
            continue
        if char in "\"'":
            # Form (e): one enclosing quoted lexeme at a token boundary.
            if i == 0 or text[i - 1] in _BOUNDARY_BEFORE:
                q_limit = min(limit, i + 1 + max_path_bytes)
                j = i + 1
                while j < q_limit and text[j] != char and text[j] != "\n":
                    j += 1
                if j < q_limit and text[j] == char:
                    content = text[i + 1 : j]
                    if " " in content or "\t" in content:
                        # A space/tab-bearing quoted span with an
                        # apparent .md target is ONE typed UNSUPPORTED
                        # record; no inner plain scan.
                        if _is_md_like(content):
                            keep = emit(
                                i + 1,
                                j,
                                CandidateSyntax.PLAIN_PATH,
                                content,
                                GraphLimitation.MARKUP_QUOTED_SPACE,
                            )
                            if not keep:
                                break
                        i = j + 1
                        continue
                    # Clean quoted span: the interior stays available
                    # to the plain form (ordinary surrounding quotes).
                    i += 1
                    continue
                # Unclosed quote: the proven boundary is the next
                # newline (or end of text) capped by the destination
                # byte allowance (``q_limit``); an apparent .md target
                # inside earns ONE typed malformed region, no plain
                # fallback — bound the newline search to that cap.
                line_end = text.find("\n", i + 1, q_limit)
                boundary = min(line_end if line_end >= 0 else limit, q_limit)
                boundary = max(boundary, i + 1)
                if _is_md_like(text[i + 1 : boundary]):
                    new_i = malformed_region(
                        i + 1,
                        CandidateSyntax.PLAIN_PATH,
                        GraphLimitation.MARKUP_MISBALANCED,
                        boundary,
                    )
                    if new_i < 0:
                        break
                    i = new_i
                    continue
                i = boundary
                continue
            i += 1
            continue
        if _plain_lexeme_char(char):
            # Form (d): maximal reference-like lexeme, classified
            # whole.  The lexeme may carry literal Unicode name
            # characters (unicode filename law), so its length is
            # measured in ACTUAL UTF-8 bytes: a lexeme over the byte
            # allowance is ONE typed PATH_TOO_LONG over the byte-
            # bounded prefix (when reference-like), never a minted
            # shorter file, and the scan resumes after the FULL
            # lexeme (no inner plain fallback).
            if i == 0 or text[i - 1] in _BOUNDARY_BEFORE:
                j = i
                byte_len = 0
                while j < limit and _plain_lexeme_char(text[j]):
                    byte_len += _utf8_char_len(text[j])
                    j += 1
                if byte_len > max_path_bytes:
                    if text.find(".md", i, j) >= 0:
                        cut = i
                        acc = 0
                        m = i
                        while m < j:
                            blen = _utf8_char_len(text[m])
                            if acc + blen > max_path_bytes:
                                break
                            acc += blen
                            cut = m + 1
                            m += 1
                        keep = emit(
                            i,
                            cut,
                            CandidateSyntax.PLAIN_PATH,
                            text[i:cut],
                            GraphLimitation.PATH_TOO_LONG,
                        )
                        if not keep:
                            break
                    i = j
                    continue
                token = text[i:j]
                core, _stripped = _strip_prose_dots(token)
                if _is_md_like(core):
                    keep = emit(i, i + len(core), CandidateSyntax.PLAIN_PATH, core)
                    i = j
                    if not keep:
                        break
                    continue
                i = j
                continue
            i += 1
            continue
        if char == "~":
            # A tilde at a token boundary starts one maximal lexeme
            # (form d, external law; the lexeme may carry literal
            # Unicode name characters, so its length is measured in
            # ACTUAL UTF-8 bytes); a mid-token tilde is not a
            # reference start and keeps its previous behavior.  An
            # overlong tilde token keeps its typed EXTERNAL record
            # over the byte-bounded prefix, resume after the FULL
            # lexeme.
            if i == 0 or text[i - 1] in _BOUNDARY_BEFORE:
                j = i
                byte_len = 0
                while j < limit and _tilde_lexeme_char(text[j]):
                    byte_len += _utf8_char_len(text[j])
                    j += 1
                if byte_len > max_path_bytes:
                    if text.find(".md", i, j) >= 0:
                        cut = i
                        acc = 0
                        m = i
                        while m < j:
                            blen = _utf8_char_len(text[m])
                            if acc + blen > max_path_bytes:
                                break
                            acc += blen
                            cut = m + 1
                            m += 1
                        keep = emit(
                            i,
                            cut,
                            CandidateSyntax.PLAIN_PATH,
                            text[i:cut],
                            GraphLimitation.TARGET_TILDE_OR_DRIVE,
                        )
                        if not keep:
                            break
                    i = j
                    continue
                token = text[i:j]
                core, _stripped = _strip_prose_dots(token)
                if _is_md_like(core):
                    keep = emit(i, i + len(core), CandidateSyntax.PLAIN_PATH, core)
                    i = j
                    if not keep:
                        break
                    continue
                i = j
                continue
            i += 1
            continue
        i += 1

    limitation: GraphLimitation | None = None
    if budget_exceeded:
        limitation = GraphLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND
    return ReferenceScan(
        candidates=tuple(emitted), limitation=limitation, scanned_chars=min(i, limit)
    )
