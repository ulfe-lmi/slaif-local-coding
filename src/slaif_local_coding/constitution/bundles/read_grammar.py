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
"""

from __future__ import annotations

import json

from ..bundles.client_paths import normalize_read_path
from ..bundles.observation_models import (
    Limitation,
    NormalizedPath,
    PathContext,
    ReadCommandParse,
    sha256_hex,
)

#: Executables that are explicit fragments, not whole-file reads.
_FRAGMENT_EXECUTABLES = {"head", "tail", "sed", "less", "more", "grep", "rg"}
#: Shell wrapper prefixes for a literal command string (Codex argv schema).
_SHELL_WRAPPERS = {"bash", "sh", "zsh"}


def tokenize_literal(command: str) -> list[tuple[str, int, int]]:
    """Split *command* on literal whitespace runs; return (token, start, end)."""

    tokens: list[tuple[str, int, int]] = []
    index = 0
    length = len(command)
    while index < length:
        while index < length and command[index].isspace():
            index += 1
        if index >= length:
            break
        start = index
        while index < length and not command[index].isspace():
            index += 1
        tokens.append((command[start:index], start, index))
    return tokens


def _classify_token(token: str) -> Limitation | None:
    """Return the first typed limitation for a non-operand token, else None."""

    if token == "--":
        return None
    if token.startswith("-"):
        return Limitation.COMMAND_UNSUPPORTED
    if token.startswith("#"):
        return Limitation.COMMENT_PRESENT
    if any(c in "$`" for c in token):
        return Limitation.COMMAND_SUBSTITUTION
    if "\\" in token:
        return Limitation.SHELL_ESCAPE
    if any(c in token for c in "*?[[]"):
        return Limitation.GLOB_UNPROVEN
    if "<" in token or ">" in token:
        return Limitation.REDIRECTION
    if "|" in token:
        return Limitation.PIPE
    if "&" in token or ";" in token:
        return Limitation.MULTIPLE_COMMANDS
    if token.startswith("{") or token.endswith("}") or "(" in token or ")" in token:
        return Limitation.COMMAND_UNSUPPORTED
    if "!" in token or "^" in token:
        return Limitation.COMMAND_UNSUPPORTED
    return None


def parse_read_command(
    command: str,
    context: PathContext,
    max_command_chars: int,
    max_operands: int,
    max_path_bytes: int,
) -> ReadCommandParse:
    """Parse one bounded literal command string into a read observation.

    The raw command is never retained in the result; only its digest, length,
    operand tokens (bounded path labels) and exact token spans are exposed.
    """

    def _unsupported(
        reasons: list[Limitation],
        command_length: int,
        operands: tuple[NormalizedPath, ...] = (),
    ) -> ReadCommandParse:
        ordered: list[Limitation] = []
        for reason in reasons:
            if reason not in ordered:
                ordered.append(reason)
        return ReadCommandParse(
            command_digest=sha256_hex(command),
            command_length=command_length,
            complete=False,
            operands=operands,
            reasons=tuple(ordered),
        )

    if not isinstance(command, str):
        return _unsupported([Limitation.COMMAND_UNSUPPORTED], 0)
    if not command.strip():
        return _unsupported([Limitation.COMMAND_EMPTY], len(command))
    if len(command) > max_command_chars:
        return _unsupported([Limitation.COMMAND_OVER_BOUND], len(command))
    if "\n" in command or "\r" in command:
        return _unsupported([Limitation.MULTIPLE_COMMANDS], len(command))
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in command):
        return _unsupported([Limitation.COMMAND_UNSUPPORTED], len(command))

    tokens = tokenize_literal(command)
    if not tokens:
        return _unsupported([Limitation.COMMAND_EMPTY], len(command))
    executable = tokens[0][0]
    if executable.startswith("#"):
        return _unsupported([Limitation.COMMENT_PRESENT], len(command))
    if executable not in {"cat"}:
        reason = (
            Limitation.FRAGMENT_COMMAND
            if executable in _FRAGMENT_EXECUTABLES
            else Limitation.COMMAND_UNSUPPORTED
        )
        return _unsupported([reason], len(command))

    reasons: list[Limitation] = []
    operands: list[NormalizedPath] = []
    for token, _start, _end in tokens[1:]:
        if token == "--":
            continue
        token_reason = _classify_token(token)
        if token_reason is not None:
            reasons.append(token_reason)
            if token_reason is Limitation.COMMENT_PRESENT:
                break  # a comment terminates the command line
            continue
        operand = normalize_read_path(token, context, max_path_bytes)
        if operand.limitation is not None:
            reasons.append(operand.limitation)
        operands.append(
            NormalizedPath(
                raw=token,
                form=operand.form,
                quoted=operand.quoted,
                normalized=operand.normalized,
                limitation=operand.limitation,
            )
        )
        if len(operands) >= max_operands:
            reasons.append(Limitation.COMMAND_OVER_BOUND)
            break

    if not operands and not reasons:
        return _unsupported([Limitation.COMMAND_EMPTY], len(command))
    if reasons:
        return _unsupported(reasons, len(command), tuple(operands))
    return ReadCommandParse(
        command_digest=sha256_hex(command),
        command_length=len(command),
        complete=True,
        operands=tuple(operands),
    )


def unwrap_supported_arguments(
    arguments: object,
) -> str | None:
    """Return the literal command string from a supported tool argument shape.

    Supported shapes (documented in the observation contract): a JSON string
    or object with a ``cmd``/``command`` string, and an argv list that is a
    single string or a ``bash|sh|zsh -c``/``-lc`` wrapper.  Unknown shapes
    return ``None`` (typed unsupported by the caller).
    """

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, RecursionError, ValueError):
            return None
    if not isinstance(arguments, dict):
        return None
    command = arguments.get("cmd", arguments.get("command"))
    if isinstance(command, str):
        return command
    argv = command
    if not isinstance(argv, list) or not argv:
        return None
    if len(argv) != len([part for part in argv if isinstance(part, str)]):
        return None
    if len(argv) == 1:
        head = argv[0]
        if isinstance(head, str):
            return head
        return None
    if len(argv) == 3 and argv[0] in _SHELL_WRAPPERS and argv[1] in {"-c", "-lc"}:
        body = argv[2]
        if isinstance(body, str):
            return body
    return None
