"""Bounded literal loop grammar (D07).

Command syntax is **data**: this module parses, it never executes.  No
subprocess, no evaluation, no environment or glob expansion, no path
resolution against the client or adapter filesystem, no host cwd/stat/
resolve, and no external shell parser dependency.  The supported surface is
a finite typed loop (not a general shell interpreter):

    loop        := 'for' var 'in' list '; do' body '; done'
    var         := one of the earned ordinary literal names (``f``, ``d``)
    list        := literal+                  (bounded; clean literals only)
    body        := statement (';' statement)*
    statement   := cat_stmt | echo_stmt
    cat_stmt    := 'cat' operand+ ('|| exit 1')?
    echo_stmt   := 'echo' quoted_literal | quoted_echo_template

- The loop variable must be exactly one of the earned ordinary names of the
  human handoff 6.2 forms (``f``, ``d``).  Shell-special, dynamic, readonly
  or any other name (``RANDOM``, ``SECONDS``, ``LINENO``, ``_``, ``g``,
  ``file``, ...) is never a literal local binding: it is typed, and no
  runtime or environment oracle is consulted.  A variable reference inside
  a body template that is not the loop variable is typed the same way.
- List values are clean literals only (unquoted literal or fully-quoted
  literal under the agreed no-spaces file convention).  A locally bound
  ordinary loop variable may substitute **only its own known literal value**
  into a supported double-quoted filename template; the substituted
  expansion is then held to the exact earned cat option/terminator/stdin
  law (quoting never disables it): a dash-leading expansion is an option,
  never a file member, and the stdin special expansion is typed
  ``STDIN_OPERAND``.  Option-like list values never fabricate whole-file
  membership.
- A cat operand template is a double-quoted path whose segments are clean
  literal labels with exactly one segment equal to ``$<loopvar>`` (the
  reference must be a whole segment; the pure-variable form ``"$f"`` is the
  degenerate one-segment case).  Partial-segment references, repeated or
  unknown references and non-literal segment text are typed, never
  guessed.  The echoed form may carry at most one whole reference of the
  loop variable inside double-quoted text; any other ``$`` usage is typed.
- The earned per-iteration guard is exactly ``|| exit 1`` after a ``cat``
  statement.  A guard that is missing on some ``cat``, an exit-zero guard,
  another exit literal, a guard after the loop, or any ``break``/
  ``continue``/branch variant is not equivalent: the loop keeps its typed
  unsupported observation (``LOOP_GUARD_UNSUPPORTED`` /
  ``LOOP_FORM_UNSUPPORTED``).
- Loop body echo output is ordinary actual output, never source bytes: a
  loop whose body carries an ``echo`` statement interleaves printed text
  between the read output, so the source region is not attributable as a
  pure bundle (``OUTER_BOUNDARY_UNPROVEN``) — a labeled-loop positive is
  only earned later with exact multiple-span/collision/order proof, never
  assumed here.  Matching file bytes are not an echo-output oracle.
- Nesting is not earned: the loop is flat.  A nested ``for``/``while``/
  ``until``/``if``/``case``/``select``, a ``break``/``continue`` or any
  other control flow inside the body is typed (``LOOP_FORM_UNSUPPORTED``),
  and quoted command examples, comments, heredocs, redirections, writes,
  pipes and substitutions keep their shared typed reasons.
- Completion and attribution: the unguarded human forms do not prove that
  every earlier iteration succeeded from the final exit status, so an
  earned loop with an unguarded ``cat`` is a recognized read whose
  per-iteration execution is not proven (``LOOP_ITERATION_UNPROVEN``) —
  requested paths are not proven-executed paths.  Only an all-success
  guarded pure-cat loop (every ``cat`` guarded, no body echo, no member-
  level limitations) plus a wrapper-proven exit-zero, untruncated, present
  output is a complete ordered whole-source bundle: one concatenated
  region with an exact digest, no fabricated internal boundaries or
  member hashes.  Duplicate operand order is preserved; distinct
  represented members determine the slot width.  Requested, proven and
  complete stay separate facts for every outcome.
- Bounds are explicit and whole-loop: total command characters
  (``max_command_chars``), iteration count (``max_operands``), body
  statement count (``max_operands``) and — the key bound — the total
  expanded ``cat`` operands across **all** iterations (one shared
  ``max_operands`` budget, never re-applied per iteration; the whole-loop
  operand budget does not multiply per iteration).  Parsing is linear over
  the command string.
- Nothing here establishes workspace/principal/session authority: the
  evidenced client-workspace context and the per-call workdir (supplied by
  the caller) are the only path authorities, and no header or environment
  variable is ever read.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pydantic import Field

from ..bundles.client_paths import normalize_read_path
from ..bundles.observation_models import (
    CharSpan,
    Limitation,
    NormalizedPath,
    PathContext,
    _Frozen,
    contains_lone_surrogates,
    sha256_hex,
)
from ..bundles.read_grammar import _FRAGMENT_EXECUTABLES
from ..bundles.shell_tokens import _operator_limitation

#: Versioned finite literal loop grammar (distinct from
#: ``literal-read-plan/v1`` and ``literal-shell-read/v1``).
LOOP_GRAMMAR = "literal-loop/v1"

#: The earned ordinary loop variable names of this slice: exactly the two
#: names of the human handoff 6.2 loop forms.  Other ordinary names may be
#: earned only if explicitly bounded by a later round.
_EARNED_LOOP_VARIABLES = frozenset({"f", "d"})

#: Name characters of a ``$name`` parameter reference (finite ASCII set).
_NAME_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

#: Metacharacters that make quoted inner text non-literal (shared law).
_META = frozenset("$`\\*?[]{}~^|&;<>()!")

#: Control-flow / structural keywords that are not earned loop-body
#: statements (nested loops and branches stay typed, never guessed).
_CONTROL_KEYWORDS = frozenset(
    {"for", "while", "until", "if", "case", "select", "break", "continue"}
)

#: ASCII whitespace separators (CR/LF are rejected up front by the guard).
_ASCII_SEPARATORS = frozenset(" \t\x0b\x0c")


class _TokenKind(StrEnum):
    UNQUOTED = "unquoted"
    DQ = "dq"
    SQ = "sq"
    BROKEN = "broken"
    MIXED = "mixed"


@dataclass(frozen=True)
class _LoopToken:
    """One quote-aware token; the repr carries spans and flags only."""

    raw_start: int
    raw_end: int
    text: str
    kind: _TokenKind

    def __repr__(self) -> str:
        return f"_LoopToken(span=({self.raw_start},{self.raw_end}), kind={self.kind!r})"


def _scan_tokens(command: str) -> list[_LoopToken]:
    """Quote-aware linear scan of the loop command (pure, bounded).

    The shared literal lexer splits on ASCII whitespace only and cannot see
    quoted regions (a quoted template with inner whitespace would fragment).
    The loop grammar therefore scans the exact string itself: a double- or
    single-quoted region is one token whose ``text`` is the inner text, an
    unterminated quote runs to the end of the command (typed broken), and
    unquoted runs stop at whitespace, a quote, or an unquoted ``;``: the
    separator metacharacter terminates the current word and is emitted as
    its own standalone token, never as part of the preceding word.  A
    quoted prefix plus a literal suffix touching the separator
    (``"A".md;``) therefore stays one word (``A.md``) followed by the
    separator, and a semiterminated literal suffix can never become an
    extra list member.  No execution, no expansion; the input is assumed
    pre-validated (no CR/LF/control characters, bounded length).
    """

    tokens: list[_LoopToken] = []
    index = 0
    length = len(command)
    while index < length:
        while index < length and command[index] in _ASCII_SEPARATORS:
            index += 1
        if index >= length:
            break
        start = index
        if command[index] in "'\"":
            quote = command[index]
            end = index + 1
            while end < length and command[end] != quote:
                end += 1
            if end >= length:
                tokens.append(_LoopToken(start, length, command[start:length], _TokenKind.BROKEN))
                break
            kind = _TokenKind.DQ if quote == '"' else _TokenKind.SQ
            tokens.append(_LoopToken(start, end + 1, command[index + 1 : end], kind))
            index = end + 1
        else:
            end = index
            while (
                end < length
                and command[end] not in _ASCII_SEPARATORS
                and command[end] not in "'\""
                and command[end] != ";"
            ):
                end += 1
            if end > start:
                tokens.append(_LoopToken(start, end, command[start:end], _TokenKind.UNQUOTED))
            if end < length and command[end] == ";":
                # The unquoted ``;`` is its own syntactic element: it
                # terminates the current word without riding it, so a
                # mixed word touching the separator keeps its literal
                # prefix intact (never two members).
                tokens.append(_LoopToken(end, end + 1, ";", _TokenKind.UNQUOTED))
                end += 1
            index = end
    return _join_words(tokens)


def _is_word_join(previous: _LoopToken, following: _LoopToken) -> bool:
    """Whether two touching fragments are one shell word (never two words).

    A clean unquoted fragment touching a quoted region (either side), or two
    touching quoted regions, are one shell word (``A".md"``, ``pre"$f"`,
    ``"$f"".md"``).  An unquoted fragment carrying a shell metacharacter —
    a separator (``;``), an operator, a glob — is its own syntactic element
    and never joins (``"$f";``, ``1;`` stay separate).  A broken quote only
    extends a word that already started.
    """

    if previous.kind is _TokenKind.BROKEN:
        return False
    if following.kind is _TokenKind.BROKEN:
        return previous.kind is _TokenKind.UNQUOTED and _clean_unquoted(previous.text)
    previous_quoted = previous.kind in (_TokenKind.DQ, _TokenKind.SQ)
    following_quoted = following.kind in (_TokenKind.DQ, _TokenKind.SQ)
    if previous_quoted and following_quoted:
        return True
    if previous.kind is _TokenKind.UNQUOTED and _clean_unquoted(previous.text) and following_quoted:
        return True
    if (
        previous_quoted
        and following.kind is _TokenKind.UNQUOTED
        and _clean_unquoted(following.text)
    ):
        return True
    return False


def _join_words(tokens: list[_LoopToken]) -> list[_LoopToken]:
    """Collapse touching fragments of one shell word into a typed MIXED.

    The loop grammar earns only pure forms — a fully-quoted template or a
    clean unquoted literal — so a word that mixes quoting is typed (its
    shared ``QUOTED_OPERAND`` reason at the consumer), never reinterpreted
    as a clean literal or template.  The joined token's text is the
    concatenated fragment text (metadata only, never executed).
    """

    words: list[_LoopToken] = []
    for token in tokens:
        previous = words[-1] if words else None
        if (
            previous is not None
            and previous.raw_end == token.raw_start
            and _is_word_join(previous, token)
        ):
            words[-1] = _LoopToken(
                previous.raw_start, token.raw_end, previous.text + token.text, _TokenKind.MIXED
            )
        else:
            words.append(token)
    return words


class LoopStatementKind(StrEnum):
    """Fixed loop-body statement kinds (stable identifiers)."""

    CAT = "cat"
    ECHO = "echo"
    OTHER = "other"


class LoopOperand(_Frozen):
    """One earned ``cat`` operand descriptor of a loop body statement.

    ``raw`` is the exact observed token text (a bounded path label or
    double-quoted template, metadata only).  ``has_variable`` marks the
    earned double-quoted template that carries the loop-variable reference;
    a clean literal has no variable.
    """

    raw: str
    has_variable: bool = False
    quoted: bool = False

    def __repr__(self) -> str:
        # Repr privacy: spans/flags only — the raw token text is never
        # re-exposed (it is command text, not source).
        return f"LoopOperand(has_variable={self.has_variable!r}, quoted={self.quoted!r})"


class LoopStatement(_Frozen):
    """One typed statement of a loop body.

    ``raw_span`` is the half-open character span of the statement's tokens
    inside the exact command string.  ``cat_operands`` carries the
    descriptor of every ``cat`` operand token (with the earned templates);
    ``guarded`` is true only for the exact ``|| exit 1`` per-iteration
    guard; ``echo_text`` is the cooked inner text of an earned ``echo``
    (clean literal or echo template).  ``reasons`` are statement-level
    typed limitations; an earned statement has none.
    """

    kind: LoopStatementKind
    raw_span: CharSpan
    cat_operands: tuple[LoopOperand, ...] = ()
    guarded: bool = False
    echo_text: str | None = None
    reasons: tuple[Limitation, ...] = ()

    def __repr__(self) -> str:
        # Repr privacy: kind, span, counts, flags and typed reasons only —
        # the echoed literal (command text) is never re-exposed.
        return (
            f"LoopStatement(kind={self.kind!r}, raw_span={self.raw_span!r}, "
            f"operand_count={len(self.cat_operands)!r}, "
            f"operands={self.cat_operands!r}, guarded={self.guarded!r}, "
            f"echo={self.echo_text is not None!r}, reasons={self.reasons!r})"
        )


class LoopParse(_Frozen):
    """Bounded literal loop parse result; command syntax is data.

    ``is_loop_attempt`` marks the loop parser's domain (the command starts
    with the exact unquoted ``for`` keyword); a command outside the domain
    is evaluated by the finite-plan parser, whose reasons/identity apply.
    ``complete`` marks a structurally earned loop (header, variable, list,
    body and closure all within the finite grammar); completeness
    limitations (unguarded ``cat``, body echo, member-level limitations)
    are carried in ``reasons`` and keep ``complete`` true — a recognized
    read is still a read whose execution/attribution is not proven.
    ``requested_members`` is the deterministic iteration-expanded member
    order (iteration order, then statement order, then operand order),
    carrying per-member typed limitations where the shared path law types
    them; option-like and stdin expansions are never members.  The raw
    command is never retained (digest, length and typed data only).
    """

    grammar: str = LOOP_GRAMMAR
    command_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    command_length: int = Field(default=0, ge=0)
    is_loop_attempt: bool = False
    complete: bool = False
    loop_variable: str | None = None
    list_values: tuple[str, ...] = ()
    statements: tuple[LoopStatement, ...] = ()
    requested_members: tuple[NormalizedPath, ...] = ()
    all_cats_guarded: bool = False
    has_echo: bool = False
    cat_statement_count: int = Field(default=0, ge=0)
    reasons: tuple[Limitation, ...] = ()

    def __repr__(self) -> str:
        # Repr privacy: digest, lengths, widths, flags and typed reasons
        # only — no raw command text, list values or echoed literals are
        # ever re-exposed.
        return (
            "LoopParse("
            f"grammar={self.grammar!r}, command_digest={self.command_digest!r}, "
            f"command_length={self.command_length!r}, "
            f"is_loop_attempt={self.is_loop_attempt!r}, complete={self.complete!r}, "
            f"loop_variable={self.loop_variable!r}, list_width={len(self.list_values)!r}, "
            f"statements={self.statements!r}, "
            f"member_width={len(self.requested_members)!r}, "
            f"all_cats_guarded={self.all_cats_guarded!r}, has_echo={self.has_echo!r}, "
            f"cat_statement_count={self.cat_statement_count!r}, reasons={self.reasons!r})"
        )


def _clean_unquoted(text: str) -> bool:
    """A non-empty unquoted word with no typed shell operator (shared law)."""

    return text != "" and _operator_limitation(text) is None


def _is_separator(token: _LoopToken) -> bool:
    """The loop's statement separator: the exact unquoted ``;``.

    The scanner emits every unquoted ``;`` as its own standalone token, so
    the separator is a standalone word: it never rides a preceding word, a
    quoted prefix plus a literal suffix touching the separator stays one
    word, and a semiterminated literal suffix can never become an extra
    member.  A ``;`` inside a quoted region is literal text, never a
    separator.
    """

    if token.kind is not _TokenKind.UNQUOTED:
        return False
    text = token.text
    if text == ";":
        return True
    return text.endswith(";") and len(text) > 1


def _reference_problem(inner: str, variable: str) -> Limitation | None:
    """Classify ``$`` references in one quoted inner text (finite, linear).

    At most one maximal ``$name`` reference is permitted and its name must
    be exactly the loop variable: any other name — shell-special, dynamic,
    readonly or unknown (``RANDOM``, ``SECONDS``, ``LINENO``, ``_``,
    ``g``, ...) — is an unrelated variable reference, never a literal
    local binding, and no runtime or environment oracle is consulted.
    """

    references = 0
    index = 0
    length = len(inner)
    while index < length:
        if inner[index] != "$":
            index += 1
            continue
        references += 1
        if references > 1:
            return Limitation.LOOP_TEMPLATE_UNSUPPORTED
        end = index + 1
        while end < length and inner[end] in _NAME_CHARS:
            end += 1
        name = inner[index + 1 : end]
        if not name:
            return Limitation.LOOP_TEMPLATE_UNSUPPORTED
        if name != variable:
            return Limitation.LOOP_VARIABLE_UNSUPPORTED
        index = end
    return None


def _cat_template_problem(inner: str, variable: str, max_path_bytes: int) -> Limitation | None:
    """The supported double-quoted filename template (finite, linear).

    A sequence of literal segments separated by ``/`` in which exactly one
    segment is exactly ``$<variable>`` (the reference is a whole segment;
    the pure-variable form is the one-segment case); every other segment
    is a clean non-empty literal label (no metacharacters, no whitespace of
    any kind, no ``.``/``..``).  A leading ``/`` is allowed (an absolute
    client template decided by the shared path law).  Inner text without a
    reference at all is a plain clean literal (the segment checks already
    proved literalness).
    """

    problem = _reference_problem(inner, variable)
    if problem is not None:
        return problem
    if len(inner.encode("utf-8")) > max_path_bytes:
        return Limitation.PATH_TOO_LONG
    segments = inner.split("/")
    if inner.startswith("/"):
        segments = segments[1:]
    variable_seen = False
    for segment in segments:
        if segment == f"${variable}":
            if variable_seen:
                return Limitation.LOOP_TEMPLATE_UNSUPPORTED
            variable_seen = True
            continue
        if segment in ("", ".", ".."):
            return Limitation.LOOP_TEMPLATE_UNSUPPORTED
        if any(c in _META for c in segment) or any(c.isspace() for c in segment):
            return Limitation.LOOP_TEMPLATE_UNSUPPORTED
    return None


def _echo_template_problem(inner: str, variable: str) -> Limitation | None:
    """The supported double-quoted echo template (finite, linear).

    Double-quoted text with at most one maximal ``$<variable>`` reference
    and no other shell metacharacter; whitespace is allowed (echo text,
    not a path).  The echoed output is ordinary actual output, never
    source bytes: recognition here is structural only — any loop-body
    ``echo`` still keeps the source region unattributable.
    """

    problem = _reference_problem(inner, variable)
    if problem is not None:
        return problem
    # ``$`` is excluded: the reference check above already proved that any
    # ``$`` is the single permitted whole loop-variable reference.
    if any(c in _META and c != "$" for c in inner) or "'" in inner:
        return Limitation.LOOP_TEMPLATE_UNSUPPORTED
    return None


def _parse_cat_statement(
    toks: list[_LoopToken],
    start: int,
    end: int,
    variable: str | None,
    max_path_bytes: int,
) -> LoopStatement:
    """One loop-body ``cat`` statement: operands plus the exact guard."""

    def _statement(
        guarded: bool, reasons: list[Limitation], operands: list[LoopOperand]
    ) -> LoopStatement:
        return LoopStatement(
            kind=LoopStatementKind.CAT,
            raw_span=CharSpan(start=start, end=end),
            cat_operands=tuple(operands),
            guarded=guarded,
            reasons=tuple(dict.fromkeys(reasons)),
        )

    if not toks:
        # ``cat`` with no operand is not a read (the shared law).
        return _statement(False, [Limitation.COMMAND_EMPTY], [])

    reasons: list[Limitation] = []
    operands: list[LoopOperand] = []
    for index, token in enumerate(toks):
        if token.kind is _TokenKind.MIXED:
            # One shell word mixing quoting is not a clean literal or an
            # earned template (the shared quote law types it).
            reasons.append(Limitation.QUOTED_OPERAND)
            break
        if token.kind is _TokenKind.UNQUOTED and token.text == "||":
            # Candidate guard start: exactly ``|| exit 1`` follows.  The
            # earned guard operator is the exact unquoted ``||`` token; any
            # other exit literal, missing literal or branch variant is
            # typed, never guessed.
            rest = toks[index + 1 :]
            if (
                len(rest) == 2
                and all(t.kind is _TokenKind.UNQUOTED and _clean_unquoted(t.text) for t in rest)
                and rest[0].text == "exit"
                and rest[1].text == "1"
            ):
                return _statement(True, reasons, operands)
            reasons.append(Limitation.LOOP_GUARD_UNSUPPORTED)
            break
        if token.kind is not _TokenKind.UNQUOTED:
            if token.kind is _TokenKind.BROKEN:
                reasons.append(Limitation.QUOTED_OPERAND)
                break
            inner = token.text
            if token.kind is _TokenKind.DQ:
                if "$" in inner:
                    problem = _cat_template_problem(inner, variable or "", max_path_bytes)
                    if problem is not None:
                        reasons.append(problem)
                        break
                    operands.append(LoopOperand(raw=inner, has_variable=True, quoted=True))
                    continue
                if (
                    inner == ""
                    or any(c in _META for c in inner)
                    or any(c in "'\"" for c in inner)
                    or any(c.isspace() for c in inner)
                ):
                    reasons.append(
                        Limitation.EMPTY_OPERAND if inner == "" else Limitation.QUOTED_OPERAND
                    )
                    break
                operands.append(LoopOperand(raw=inner, quoted=True))
            else:  # SQ
                if (
                    inner == ""
                    or any(c in _META for c in inner)
                    or any(c in "'\"" for c in inner)
                    or any(c.isspace() for c in inner)
                ):
                    reasons.append(
                        Limitation.EMPTY_OPERAND if inner == "" else Limitation.QUOTED_OPERAND
                    )
                    break
                operands.append(LoopOperand(raw=inner, quoted=True))
            index += 1
            continue
        # Unquoted token.
        text = token.text
        if text == "":
            break
        operator = _operator_limitation(text)
        if operator is not None:
            # A typed operator inside the statement terminates member
            # collection (the shared law: later words are never members).
            reasons.append(operator)
            break
        operands.append(LoopOperand(raw=text))
    if not operands and not reasons:
        return _statement(False, [Limitation.COMMAND_EMPTY], [])
    return _statement(False, reasons, operands)


def _parse_echo_statement(
    toks: list[_LoopToken], start: int, end: int, variable: str | None
) -> LoopStatement:
    """One loop-body ``echo`` statement (structural recognition only).

    The earned target is exactly one quoted token: a clean fully-quoted
    literal (either quote kind, cooked value not dash-leading — quoting
    does not disable ``echo``'s option parser) or, double-quoted only, the
    finite echo template (at most one whole loop-variable reference, no
    other metacharacter, whitespace allowed).  The echoed output is
    ordinary actual output, never source bytes: a loop body echo keeps the
    source region unattributable (``OUTER_BOUNDARY_UNPROVEN`` at the loop
    level).
    """

    span = CharSpan(start=start, end=end)
    if len(toks) != 1:
        return LoopStatement(
            kind=LoopStatementKind.ECHO,
            raw_span=span,
            reasons=(Limitation.ECHO_TARGET_UNSUPPORTED,),
        )
    token = toks[0]
    if token.kind is _TokenKind.UNQUOTED or token.kind is _TokenKind.MIXED:
        # An unquoted or quoting-mixed echo target (option words included)
        # is never earned: the echo literal must be a pure quoted form,
        # and option parsing is command local, not a boundary.
        return LoopStatement(
            kind=LoopStatementKind.ECHO,
            raw_span=span,
            reasons=(Limitation.ECHO_TARGET_UNSUPPORTED,),
        )
    if token.kind is _TokenKind.BROKEN:
        return LoopStatement(
            kind=LoopStatementKind.ECHO,
            raw_span=span,
            reasons=(Limitation.ECHO_TARGET_UNSUPPORTED,),
        )
    inner = token.text
    if token.kind is _TokenKind.DQ:
        problem = _echo_template_problem(inner, variable or "")
        if problem is not None:
            return LoopStatement(kind=LoopStatementKind.ECHO, raw_span=span, reasons=(problem,))
    elif (
        inner == ""
        or any(c in _META for c in inner)
        or any(c in "'\"" for c in inner)
        or any(c.isspace() for c in inner)
    ):
        # A single-quoted echo literal must be a clean fully-quoted
        # literal (no metacharacter, no whitespace of any kind).
        return LoopStatement(
            kind=LoopStatementKind.ECHO,
            raw_span=span,
            reasons=(Limitation.ECHO_TARGET_UNSUPPORTED,),
        )
    if inner.startswith("-"):
        # Quoting does not disable echo's option parser: a dash-leading
        # cooked operand (either quote kind) is implementation-sensitive —
        # the actual ``echo '-n'`` writes nothing — so it never earns an
        # echo recognition boundary.
        return LoopStatement(
            kind=LoopStatementKind.ECHO,
            raw_span=span,
            reasons=(Limitation.ECHO_TARGET_UNSUPPORTED,),
        )
    return LoopStatement(kind=LoopStatementKind.ECHO, raw_span=span, echo_text=inner)


def _parse_loop_statement(
    chunk: list[_LoopToken],
    start: int,
    end: int,
    variable: str | None,
    max_path_bytes: int,
) -> LoopStatement:
    """Parse one loop-body statement chunk (tokens between separators)."""

    span = CharSpan(start=start, end=end)
    if not chunk:
        return LoopStatement(
            kind=LoopStatementKind.OTHER, raw_span=span, reasons=(Limitation.COMMAND_EMPTY,)
        )
    first = chunk[0]
    if first.kind is not _TokenKind.UNQUOTED or not _clean_unquoted(first.text):
        # A quoted or metacharacter-carrying first word is never an earned
        # statement executable (its shared typed reason is preserved).
        if first.kind is _TokenKind.UNQUOTED:
            reason = _operator_limitation(first.text) or Limitation.LOOP_FORM_UNSUPPORTED
        else:
            reason = Limitation.QUOTED_OPERAND
        return LoopStatement(kind=LoopStatementKind.OTHER, raw_span=span, reasons=(reason,))
    word = first.text
    if word == "cat":
        return _parse_cat_statement(chunk[1:], start, end, variable, max_path_bytes)
    if word == "echo":
        return _parse_echo_statement(chunk[1:], start, end, variable)
    if word in _FRAGMENT_EXECUTABLES:
        return LoopStatement(
            kind=LoopStatementKind.OTHER, raw_span=span, reasons=(Limitation.FRAGMENT_COMMAND,)
        )
    if word in _CONTROL_KEYWORDS or word in ("then", "else", "fi", "esac", "do", "done", "in"):
        # Nested loops and branches are control flow, not earned statements.
        return LoopStatement(
            kind=LoopStatementKind.OTHER, raw_span=span, reasons=(Limitation.LOOP_FORM_UNSUPPORTED,)
        )
    return LoopStatement(
        kind=LoopStatementKind.OTHER, raw_span=span, reasons=(Limitation.COMMAND_UNSUPPORTED,)
    )


def _expand_operand(
    operand: LoopOperand,
    value: str,
    variable: str,
    terminator_seen: bool,
    context: PathContext,
    max_path_bytes: int,
) -> tuple[NormalizedPath | None, Limitation | None, bool]:
    """Substitute the bound literal value and apply the exact shared law.

    A plain literal operand expands to itself; an earned template expands
    by substituting **only the bound literal value** of the loop variable.
    The expansion is then held to the exact earned cat option/terminator/
    stdin law (quoting never disables it): the option terminator is
    recognized by **cooked value in operand order** — the first cooked
    ``--`` is consumed as the terminator (even when produced by
    substitution), a later ``--`` is a literal member — an option-like
    pre-terminator expansion is an option, never a file member, and the
    stdin special expansion is typed ``STDIN_OPERAND``.  Option-like list
    values never fabricate whole-file membership.  A path-limited
    expansion stays a member with its typed limitation (the shared path
    law).  The returned state is the updated terminator flag.
    """

    if operand.has_variable:
        expanded = operand.raw.replace(f"${variable}", value)
    elif operand.quoted:
        expanded = operand.raw
    else:
        expanded = operand.raw
    if not terminator_seen and expanded == "--":
        # The option terminator: consumed once, not a member, no reason.
        return None, None, True
    if expanded == "-":
        return None, Limitation.STDIN_OPERAND, terminator_seen
    if not terminator_seen and expanded.startswith("-"):
        return None, Limitation.COMMAND_UNSUPPORTED, terminator_seen
    normalized = normalize_read_path(expanded, context, max_path_bytes)
    return (
        NormalizedPath(
            raw=expanded,
            form=normalized.form,
            quoted=False,
            normalized=normalized.normalized,
            limitation=normalized.limitation,
        ),
        normalized.limitation,
        terminator_seen,
    )


def parse_literal_loop(
    command: str,
    context: PathContext,
    max_command_chars: int,
    max_operands: int,
    max_path_bytes: int,
) -> LoopParse:
    """Parse one bounded literal command string into a typed loop (pure).

    Total and linear: the raw command is never retained (digest, length and
    typed data only), nothing is executed or expanded, and every unsupported
    shape is a typed limitation, never a guess.  See the module docstring
    for the earned surface, the variable/template/guard laws and the
    whole-loop bound law (the total expanded operand budget is one shared
    ``max_operands`` — it never multiplies per iteration).
    """

    def _finish(
        reasons: list[Limitation],
        *,
        digest: str | None = None,
        length: int = 0,
        attempt: bool = False,
        complete: bool = False,
        variable: str | None = None,
        list_values: tuple[str, ...] = (),
        statements: tuple[LoopStatement, ...] = (),
        members: tuple[NormalizedPath, ...] = (),
        guarded_all: bool = False,
        has_echo: bool = False,
        cat_count: int = 0,
    ) -> LoopParse:
        ordered: list[Limitation] = []
        for reason in reasons:
            if reason not in ordered:
                ordered.append(reason)
        return LoopParse(
            command_digest=digest,
            command_length=length,
            is_loop_attempt=attempt,
            complete=complete,
            loop_variable=variable,
            list_values=list_values,
            statements=statements,
            requested_members=members,
            all_cats_guarded=guarded_all,
            has_echo=has_echo,
            cat_statement_count=cat_count,
            reasons=tuple(ordered),
        )

    if not isinstance(command, str):
        return _finish([Limitation.COMMAND_UNSUPPORTED])
    if contains_lone_surrogates(command):
        # Malformed Unicode is rejected before any UTF-8 hashing; the
        # digest is explicitly absent, never a placeholder.
        return _finish([Limitation.MALFORMED_UNICODE], length=len(command))
    digest = sha256_hex(command)
    length = len(command)
    if not command.strip():
        return _finish([Limitation.COMMAND_EMPTY], digest=digest, length=length)
    if length > max_command_chars:
        return _finish([Limitation.COMMAND_OVER_BOUND], digest=digest, length=length)
    if "\n" in command or "\r" in command:
        return _finish([Limitation.MULTIPLE_COMMANDS], digest=digest, length=length)
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in command):
        # The control-character guard is not relaxed: POSIX blanks are not
        # interchangeable with CR/VT/FF anywhere in a loop.
        return _finish([Limitation.COMMAND_UNSUPPORTED], digest=digest, length=length)

    tokens = _scan_tokens(command)
    if not tokens:
        return _finish([Limitation.COMMAND_EMPTY], digest=digest, length=length)
    first = tokens[0]
    if (
        first.kind is not _TokenKind.UNQUOTED
        or not _clean_unquoted(first.text)
        or first.text != "for"
    ):
        # Outside the loop parser's domain: the finite-plan parser evaluates
        # this command (its reasons and identity apply unchanged).
        return _finish([], digest=digest, length=length)

    reasons: list[Limitation] = []
    structural_ok = True

    if len(tokens) < 4:
        reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
        structural_ok = False
        return _finish(reasons, digest=digest, length=length, attempt=True)

    var_token = tokens[1]
    variable: str | None = None
    if var_token.kind is not _TokenKind.UNQUOTED or not _clean_unquoted(var_token.text):
        reasons.append(Limitation.LOOP_VARIABLE_UNSUPPORTED)
        structural_ok = False
    elif var_token.text in _EARNED_LOOP_VARIABLES:
        variable = var_token.text
    else:
        # Not an earned ordinary name: shell-special, dynamic, readonly or
        # any other name is never a literal local binding.
        reasons.append(Limitation.LOOP_VARIABLE_UNSUPPORTED)
        structural_ok = False

    in_token = tokens[2]
    if (
        in_token.kind is not _TokenKind.UNQUOTED
        or in_token.text != "in"
        or not _clean_unquoted(in_token.text)
    ):
        reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
        structural_ok = False

    list_values: list[str] = []
    statements: tuple[LoopStatement, ...] = ()
    all_guarded = False
    has_echo = False
    cat_count = 0

    if structural_ok:
        # --- iteration list: clean literals up to the `;` separator -----
        index = 3
        list_closed = False
        while not list_closed and index < len(tokens):
            token = tokens[index]
            if _is_separator(token):
                # The standalone separator closes the list; the preceding
                # word was already classified as a complete word (no
                # semiterminated suffix can become an extra member).
                list_closed = True
                index += 1
                break
            if token.kind is _TokenKind.UNQUOTED:
                if not _clean_unquoted(token.text):
                    reasons.append(
                        _operator_limitation(token.text) or Limitation.LOOP_FORM_UNSUPPORTED
                    )
                    structural_ok = False
                else:
                    list_values.append(token.text)
            elif token.kind in (_TokenKind.DQ, _TokenKind.SQ):
                inner = token.text
                if (
                    inner == ""
                    or any(c in _META for c in inner)
                    or any(c in "'\"" for c in inner)
                    or any(c.isspace() for c in inner)
                ):
                    reasons.append(
                        Limitation.QUOTED_OPERAND if inner != "" else Limitation.EMPTY_OPERAND
                    )
                    structural_ok = False
                else:
                    list_values.append(inner)
            elif token.kind is _TokenKind.MIXED:
                # A word mixing quoting is not a clean list literal.
                reasons.append(Limitation.QUOTED_OPERAND)
                structural_ok = False
            else:
                reasons.append(Limitation.QUOTED_OPERAND)
                structural_ok = False
            index += 1
        if not list_closed:
            reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
            structural_ok = False
        if list_closed and not list_values:
            # An empty iteration list is not a complete source read.
            reasons.append(Limitation.COMMAND_EMPTY)
            structural_ok = False
        if list_closed and len(list_values) > max_operands:
            reasons.append(Limitation.OVER_BOUND)
            structural_ok = False

    if structural_ok:
        # --- `do`, then the body up to the `; done` closure --------------
        if index >= len(tokens):
            reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
            structural_ok = False
        else:
            do_token = tokens[index]
            if (
                do_token.kind is not _TokenKind.UNQUOTED
                or do_token.text != "do"
                or not _clean_unquoted(do_token.text)
            ):
                reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
                structural_ok = False

    if structural_ok:
        index += 1
        body: list[LoopStatement] = []
        current: list[_LoopToken] = []
        closed = False
        while index < len(tokens):
            token = tokens[index]
            if _is_separator(token):
                # The standalone separator closes the current statement;
                # every statement word was already a complete word.
                if current:
                    statement = _parse_loop_statement(
                        current,
                        current[0].raw_start,
                        current[-1].raw_end,
                        variable,
                        max_path_bytes,
                    )
                    body.append(statement)
                    if statement.reasons:
                        structural_ok = False
                        for reason in statement.reasons:
                            if reason not in reasons:
                                reasons.append(reason)
                    current = []
                nxt = tokens[index + 1] if index + 1 < len(tokens) else None
                if (
                    nxt is not None
                    and nxt.kind is _TokenKind.UNQUOTED
                    and nxt.text == "done"
                    and _clean_unquoted(nxt.text)
                    and index + 1 == len(tokens) - 1
                ):
                    closed = True
                    break
            else:
                current.append(token)
            index += 1
        if not closed:
            if current:
                statement = _parse_loop_statement(
                    current,
                    current[0].raw_start,
                    current[-1].raw_end,
                    variable,
                    max_path_bytes,
                )
                body.append(statement)
                for reason in statement.reasons:
                    if reason not in reasons:
                        reasons.append(reason)
            reasons.append(Limitation.LOOP_FORM_UNSUPPORTED)
            structural_ok = False
        if structural_ok:
            statements = tuple(body)
            if len(body) > max_operands:
                reasons.append(Limitation.OVER_BOUND)
                structural_ok = False
            cat_statements = [s for s in statements if s.kind is LoopStatementKind.CAT]
            has_cat = bool(cat_statements)
            has_echo = any(s.kind is LoopStatementKind.ECHO for s in statements)
            all_guarded = has_cat and all(s.guarded for s in cat_statements)
            cat_count = len(cat_statements)
            if not has_cat:
                # A loop without any cat statement is not a read at all:
                # typed, never a silent empty read.
                reasons.append(Limitation.COMMAND_UNSUPPORTED)
                structural_ok = False
            if has_cat and not all_guarded:
                # The unguarded human forms do not prove that every earlier
                # iteration succeeded from the final exit status.
                reasons.append(Limitation.LOOP_ITERATION_UNPROVEN)
            if has_cat and has_echo:
                # Body echo output interleaves printed text between the
                # read output: the source region is not attributable.
                reasons.append(Limitation.OUTER_BOUNDARY_UNPROVEN)

            # --- iteration-expanded members (deterministic order) --------
            members: list[NormalizedPath] = []
            if variable is not None and list_values:
                earned_cats = [s for s in cat_statements if not s.reasons]
                per_iteration = sum(len(s.cat_operands) for s in earned_cats)
                total = len(list_values) * per_iteration
                if per_iteration and total > max_operands:
                    # The whole-loop operand budget is one shared bound —
                    # it never multiplies per iteration.
                    reasons.append(Limitation.OVER_BOUND)
                    structural_ok = False
                if total <= max_operands:
                    for value in list_values:
                        for statement in earned_cats:
                            terminator_seen = False
                            iteration_members = 0
                            iteration_reasons: list[Limitation] = []
                            for operand in statement.cat_operands:
                                member, limitation, terminator_seen = _expand_operand(
                                    operand,
                                    value,
                                    variable,
                                    terminator_seen,
                                    context,
                                    max_path_bytes,
                                )
                                if limitation is not None:
                                    iteration_reasons.append(limitation)
                                if member is not None:
                                    iteration_members += 1
                                    members.append(member)
                            if iteration_members == 0 and not iteration_reasons:
                                # That iteration's cat read no file (an
                                # option terminator consumed every slot):
                                # its output is unknown (stdin), never a
                                # complete source read.
                                iteration_reasons.append(Limitation.COMMAND_EMPTY)
                            for limitation in iteration_reasons:
                                if limitation not in reasons:
                                    reasons.append(limitation)

            complete = structural_ok
            return _finish(
                reasons,
                digest=digest,
                length=length,
                attempt=True,
                complete=complete,
                variable=variable,
                list_values=tuple(list_values),
                statements=statements,
                members=tuple(members),
                guarded_all=all_guarded,
                has_echo=has_echo,
                cat_count=cat_count,
            )

    return _finish(
        reasons,
        digest=digest,
        length=length,
        attempt=True,
        complete=False,
        variable=variable,
        list_values=tuple(list_values),
        statements=statements,
        members=(),
    )
