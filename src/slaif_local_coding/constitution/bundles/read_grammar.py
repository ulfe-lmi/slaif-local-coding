"""Bounded literal shell-read grammar (D03/D04).

Command syntax is **data**: this module parses, it never executes.  No
subprocess, no evaluation, no environment or glob expansion, no path
resolution against the client or adapter filesystem, and no external shell
parser dependency (the supported surface is a literal token grammar).

The earned surface in this slice is exactly:

    cat <operand>
    cat -- <operand>
    cat <operand> <operand> ...

where each operand is a literal path token (or a fully-quoted literal token
under the agreed no-spaces file convention).  Every other shape — flags,
compounds, pipes, redirections, heredocs, substitutions, globs, comments,
``head``/``tail``/``sed`` fragments, loops, unknown executables — yields a
typed limitation and is never a complete whole-file observation.

Option-parser law: quoting does **not** disable ``cat``'s own argument
parser.  A token whose cooked value starts with ``-`` before the terminator
(``-n``, ``--number`` — quoted or not) is an option, never a file member.
The option terminator is recognized by cooked value: the first token whose
cooked value is exactly ``--`` (quoted or not) is processed **once**; a
later ``--`` token (quoted or not) is a literal operand and stays in the
actual complete member list — the complete member list is preserved, never
silently dropped.  The stdin special operand ``-`` (cooked value, quoted or
not, before or after the terminator) is never a file member: a command that
would read stdin is typed ``STDIN_OPERAND``, not a whole-file observation.
A literal path that merely ends in ``-`` (``./-``, ``/work/-``) is a path
operand, distinguished from the special operand.

Separator law: only ASCII whitespace separates tokens; arbitrary Unicode
``isspace`` characters (e.g. NBSP) are not shell separators — a token that
carries one is a single literal path label, typed ambiguous under the
agreed no-spaces file convention, never split into two fabricated files.

Privacy law: raw command and workdir text never appears in operational
representations (``UnwrappedCommand`` repr carries lengths/presence only)
and no exception echo of raw bodies, sources or arguments is produced.

Malformed-Unicode law: a command string that cannot be encoded as UTF-8
(lone surrogates) is rejected with ``MALFORMED_UNICODE`` before any hashing;
its ``command_digest`` is explicitly absent (never a placeholder digest).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from ..bundles.client_paths import normalize_read_path
from ..bundles.observation_models import (
    Limitation,
    NormalizedPath,
    PathContext,
    ReadCommandParse,
    contains_lone_surrogates,
    sha256_hex,
)
from ..bundles.shell_tokens import _spans, tokenize_command

#: Executables that are explicit fragments, not whole-file reads.
_FRAGMENT_EXECUTABLES = {"head", "tail", "sed", "less", "more", "grep", "rg"}
#: Shell wrapper prefixes for a literal command string (Codex argv schema).
_SHELL_WRAPPERS = {"bash", "sh", "zsh"}


@dataclass(frozen=True)
class UnwrappedCommand:
    """A supported tool-argument envelope unwrapped to its command string.

    ``workdir`` is the explicit per-call client working directory carried by
    the supported argument object (when present); it is data, never an
    adapter-host cwd, and it is validated against the evidenced workspace at
    path-normalization time.  The operational repr carries lengths and
    presence only: the raw command/workdir text is never re-exposed.
    """

    command: str
    workdir: str | None = None

    def __repr__(self) -> str:
        if self.workdir is not None:
            workdir = f"workdir_length={len(self.workdir)}"
        else:
            workdir = "workdir=None"
        return f"UnwrappedCommand(command_length={len(self.command)}, {workdir})"


def tokenize_literal(command: str) -> list[tuple[str, int, int]]:
    """Split *command* on literal whitespace runs; return (token, start, end).

    Only ASCII whitespace separates tokens: arbitrary Unicode ``isspace``
    characters (e.g. NBSP) are not shell separators and stay inside the
    token (the path layer types them under the no-spaces convention).
    """

    return [(command[s:e], s, e) for s, e in _spans(command)]


def parse_read_command(
    command: str,
    context: PathContext,
    max_command_chars: int,
    max_operands: int,
    max_path_bytes: int,
) -> ReadCommandParse:
    """Parse one bounded literal command string into a read observation.

    The raw command is never retained in the result; only its digest (absent
    under the typed malformed-Unicode contract), length, operand tokens
    (bounded path labels) and exact token spans are exposed.
    """

    def _finish(
        reasons: list[Limitation],
        operands: tuple[NormalizedPath, ...],
        complete: bool,
        digest: str | None,
    ) -> ReadCommandParse:
        ordered: list[Limitation] = []
        for reason in reasons:
            if reason not in ordered:
                ordered.append(reason)
        return ReadCommandParse(
            command_digest=digest,
            command_length=len(command),
            complete=complete,
            operands=operands,
            reasons=tuple(ordered),
        )

    if not isinstance(command, str):
        return ReadCommandParse(
            command_digest=None,
            command_length=0,
            complete=False,
            reasons=(Limitation.COMMAND_UNSUPPORTED,),
        )
    if contains_lone_surrogates(command):
        # Malformed Unicode is rejected before any UTF-8 hashing; the digest
        # is explicitly absent, never a placeholder treated as valid.
        return _finish([Limitation.MALFORMED_UNICODE], (), False, None)
    digest = sha256_hex(command)
    if not command.strip():
        return _finish([Limitation.COMMAND_EMPTY], (), False, digest)
    if len(command) > max_command_chars:
        return _finish([Limitation.COMMAND_OVER_BOUND], (), False, digest)
    if "\n" in command or "\r" in command:
        return _finish([Limitation.MULTIPLE_COMMANDS], (), False, digest)
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in command):
        return _finish([Limitation.COMMAND_UNSUPPORTED], (), False, digest)

    tokens = tokenize_command(command)
    if not tokens:
        return _finish([Limitation.COMMAND_EMPTY], (), False, digest)
    executable = tokens[0]
    if executable.operator is Limitation.COMMENT_PRESENT:
        return _finish([Limitation.COMMENT_PRESENT], (), False, digest)
    # The executable must be the exact unquoted literal word ``cat``: a
    # quoted or otherwise limited token is not the earned surface.
    if (
        executable.value != "cat"
        or executable.quoted
        or executable.quote_limitation is not None
        or executable.operator is not None
    ):
        reason = (
            Limitation.FRAGMENT_COMMAND
            if executable.value in _FRAGMENT_EXECUTABLES
            else Limitation.COMMAND_UNSUPPORTED
        )
        return _finish([reason], (), False, digest)

    reasons: list[Limitation] = []
    operands: list[NormalizedPath] = []
    terminator_seen = False
    for token in tokens[1:]:
        if token.quote_limitation is not None:
            # Partial/nested/concatenated quotes or quoted inner text
            # outside the literal surface: typed, never guessed.
            reasons.append(token.quote_limitation)
            continue
        if token.operator is not None:
            reasons.append(token.operator)
            if token.operator is Limitation.COMMENT_PRESENT:
                break  # a comment terminates the command line
            continue
        # The option terminator is recognized by cooked value (quoting
        # does not disable cat's option parser) and processed once; a
        # later ``--`` is a literal operand kept in the member list.
        if token.value == "--" and not terminator_seen:
            terminator_seen = True
            continue
        if token.value == "-":
            # The stdin special operand (cooked value, before or after
            # the terminator): cat would read stdin as well, so no
            # whole-file membership can be proven for this call.
            reasons.append(Limitation.STDIN_OPERAND)
            continue
        if not terminator_seen and token.value.startswith("-"):
            # A formatting option, quoted or not: never a file member.
            reasons.append(Limitation.COMMAND_UNSUPPORTED)
            continue
        raw_token = command[token.raw_start : token.raw_end]
        operand = normalize_read_path(raw_token, context, max_path_bytes)
        if operand.limitation is not None:
            reasons.append(operand.limitation)
        operands.append(
            NormalizedPath(
                raw=raw_token,
                form=operand.form,
                quoted=operand.quoted,
                normalized=operand.normalized,
                limitation=operand.limitation,
            )
        )
        # The documented operand bound is exact: up to max_operands
        # operands are complete; one over is typed over-bound.
        if len(operands) > max_operands:
            reasons.append(Limitation.COMMAND_OVER_BOUND)
            break

    if not operands and not reasons:
        return _finish([Limitation.COMMAND_EMPTY], (), False, digest)
    if reasons:
        return _finish(reasons, tuple(operands), False, digest)
    return _finish([], tuple(operands), True, digest)


def raw_argument_bound(max_argument_chars: int) -> int:
    """Documented conservative raw JSON-argument cap (finite encoding).

    The supported argument shapes carry at most two string fields (the
    ``cmd``/``command`` and the optional ``workdir``), each bounded by
    *max_argument_chars* Unicode characters.  In a JSON document one
    character encodes to at most 6 characters (``\\uXXXX``), plus two
    quotes per field and a bounded object/wrapper overhead.  The declared
    cap is therefore ``12 * max_argument_chars + 128``: a finite,
    conservative worst case of the supported encoding — any raw string
    beyond it cannot encode a supported in-bounds argument.  (The earlier
    ``2 * max_argument_chars + 128`` was not a Unicode JSON-escaping bound
    and wrongly rejected valid in-bounds non-ASCII commands.)
    """

    return 12 * max_argument_chars + 128


def unwrap_call_arguments(
    arguments: object,
    max_argument_chars: int = 4096,
) -> UnwrappedCommand | None:
    """Unwrap a supported tool argument envelope to command + optional workdir.

    Supported shapes (documented in the observation contract): a JSON string
    or object with a ``cmd``/``command`` string (and an optional ``workdir``
    string), and an argv list that is exactly one string or exactly
    ``[bash|sh|zsh, -c|-lc, <string>]`` (with the same optional ``workdir``
    in the enclosing object).  Unknown shapes return ``None`` (typed
    unsupported by the caller).

    JSON decoding is bounded: a raw argument string longer than the
    documented conservative cap :func:`raw_argument_bound` is typed
    unsupported without being parsed, and decoding errors (including
    nesting-depth ``RecursionError``) return the same typed result.  No
    decode error is re-raised with raw argument text.
    """

    if isinstance(arguments, str):
        if len(arguments) > raw_argument_bound(max_argument_chars):
            return None
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, RecursionError, ValueError):
            return None
    if not isinstance(arguments, dict):
        return None
    workdir = arguments.get("workdir")
    if "workdir" in arguments and not isinstance(workdir, str):
        return None
    if isinstance(workdir, str) and not workdir:
        return None
    command = arguments.get("cmd", arguments.get("command"))
    if isinstance(command, str):
        return UnwrappedCommand(command=command, workdir=workdir)
    argv = command
    if not isinstance(argv, list) or not argv:
        return None
    if len(argv) != len([part for part in argv if isinstance(part, str)]):
        return None
    if len(argv) == 1:
        head = argv[0]
        if isinstance(head, str):
            return UnwrappedCommand(command=head, workdir=workdir)
        return None
    if len(argv) == 3 and argv[0] in _SHELL_WRAPPERS and argv[1] in {"-c", "-lc"}:
        body = argv[2]
        if isinstance(body, str):
            return UnwrappedCommand(command=body, workdir=workdir)
    return None


def unwrap_supported_arguments(
    arguments: object,
    max_argument_chars: int = 4096,
) -> str | None:
    """Return the literal command string from a supported tool argument shape.

    Compatibility wrapper over :func:`unwrap_call_arguments` (the supported
    ``workdir`` field is ignored here); unknown shapes return ``None``
    (typed unsupported by the caller).
    """

    unwrapped = unwrap_call_arguments(arguments, max_argument_chars)
    return unwrapped.command if unwrapped is not None else None
