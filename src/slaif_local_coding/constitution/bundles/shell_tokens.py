"""Bounded literal shell-token lexing for the read grammar (D03/D04).

Token streams are **data**: lexing never executes, evaluates, or expands
anything (no environment/glob/substitution expansion, no external shell
parser dependency).  Each token separates its raw span (character offsets
into the exact command string) from its cooked value (the literal text
after removing the surrounding quotes of a fully-quoted token) and from
its classification (quote problems and shell operators).  Operational
representations (``__repr__``) carry spans and flags only — never raw or
cooked token text — and no limitation value ever echoes payload text.

Separator law: only ASCII whitespace (space, tab, vertical tab, form feed,
carriage return) separates tokens.  Arbitrary Unicode ``isspace``
characters (for example NBSP) are **not** POSIX shell separators: they stay
inside the token and are typed by the path layer under the agreed
no-spaces file convention (never silently split into two files).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..bundles.observation_models import Limitation

#: The only literal token separators (ASCII whitespace).
_ASCII_SEPARATORS = frozenset(" \t\x0b\x0c\r")


@dataclass(frozen=True)
class LiteralToken:
    """One bounded literal token; raw span and cooked value are distinct.

    ``value`` is the cooked literal: for a clean fully-quoted token the
    quoted inner text, otherwise the exact raw token text.  ``quoted`` is
    true only for a clean fully-quoted literal.  ``quote_limitation`` is
    set when the token is not a clean fully-quoted literal (partial,
    nested or concatenated quotes, or quoted inner text outside the literal
    surface); ``operator`` is the first shell-operator limitation for an
    unquoted token (quoted tokens are literal and carry ``None``).  The
    repr carries spans and flags only — never token text.
    """

    raw_start: int
    raw_end: int
    value: str
    quoted: bool
    quote_limitation: Limitation | None = None
    operator: Limitation | None = None

    def __repr__(self) -> str:
        return (
            f"LiteralToken(span=({self.raw_start},{self.raw_end}),"
            f" quoted={self.quoted},"
            f" quote_limitation={self.quote_limitation!r},"
            f" operator={self.operator!r})"
        )


def _spans(command: str) -> list[tuple[int, int]]:
    """Half-open character spans of the ASCII-whitespace-separated tokens."""

    spans: list[tuple[int, int]] = []
    index = 0
    length = len(command)
    while index < length:
        while index < length and command[index] in _ASCII_SEPARATORS:
            index += 1
        if index >= length:
            break
        start = index
        while index < length and command[index] not in _ASCII_SEPARATORS:
            index += 1
        spans.append((start, index))
    return spans


def _operator_limitation(raw: str) -> Limitation | None:
    """First shell-operator limitation for an unquoted token, else ``None``.

    Rule order is stable and matches the documented grammar: a leading
    ``#`` starts a comment (which terminates the line), then substitution,
    escape, glob, redirection, pipe, command separator, braces/parens and
    the remaining unearned metacharacters.  ``-``-leading tokens are NOT
    operators here: option/terminator/stdin decisions are cat-specific and
    belong to the grammar, which sees the cooked value.
    """

    if raw.startswith("#"):
        return Limitation.COMMENT_PRESENT
    if any(c in raw for c in "$`"):
        return Limitation.COMMAND_SUBSTITUTION
    if "\\" in raw:
        return Limitation.SHELL_ESCAPE
    if any(c in raw for c in "*?[[]"):
        return Limitation.GLOB_UNPROVEN
    if "<" in raw or ">" in raw:
        return Limitation.REDIRECTION
    if "|" in raw:
        return Limitation.PIPE
    if "&" in raw or ";" in raw:
        return Limitation.MULTIPLE_COMMANDS
    if raw.startswith("{") or raw.endswith("}") or "(" in raw or ")" in raw:
        return Limitation.COMMAND_UNSUPPORTED
    if "!" in raw or "^" in raw:
        return Limitation.COMMAND_UNSUPPORTED
    return None


def _quote_limitation(raw: str) -> Limitation | None:
    """Typed limitation when *raw* is not a clean fully-quoted literal.

    A clean fully-quoted token is exactly ``X<inner>X`` (``X`` one quote
    character) whose inner text is non-empty, carries no quote character,
    no shell metacharacter, and no whitespace character of any kind (the
    agreed no-spaces file convention).  Empty quoted tokens (``''``) are
    clean (the empty literal); the grammar/path layer types them as empty
    operands.  Everything else — partial, nested or concatenated quotes,
    quoted inner text with metacharacters or whitespace — is
    ``QUOTED_OPERAND`` (typed unsupported, never guessed).
    """

    if raw[0] not in "'\"" or len(raw) < 2 or raw[-1] != raw[0]:
        return Limitation.QUOTED_OPERAND
    inner = raw[1:-1]
    if inner and not any(c in "'\"" or c in "$`\\*?[]{}~^|&;<>()!" or c.isspace() for c in inner):
        return None
    if not inner:
        return None
    return Limitation.QUOTED_OPERAND


def _classify(raw: str, start: int, end: int) -> LiteralToken:
    if "'" in raw or '"' in raw:
        limitation = _quote_limitation(raw)
        if limitation is None:
            return LiteralToken(start, end, raw[1:-1], True)
        return LiteralToken(start, end, raw, False, quote_limitation=limitation)
    return LiteralToken(start, end, raw, False, operator=_operator_limitation(raw))


def tokenize_command(command: str) -> list[LiteralToken]:
    """Lex one command string into bounded literal tokens (pure, linear).

    No execution, no expansion, no environment/glob/substitution handling:
    operators and substitutions stay classified data inside tokens.  The
    input is assumed pre-validated (non-string and malformed-Unicode
    handling belongs to the grammar, which types it before lexing).
    """

    return [_classify(command[s:e], s, e) for s, e in _spans(command)]
