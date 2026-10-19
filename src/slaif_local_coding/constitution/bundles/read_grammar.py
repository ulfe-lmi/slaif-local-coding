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

Membership law: the option terminator ``--`` is processed **once** (the first
``--`` after the executable).  A later ``--`` token is a literal operand —
the actual complete member list is preserved, never silently dropped.

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
    path-normalization time.
    """

    command: str
    workdir: str | None = None


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
        # A bare ``--`` token is a literal operand (the option terminator is
        # consumed once by the parser before classification).
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

    tokens = tokenize_literal(command)
    if not tokens:
        return _finish([Limitation.COMMAND_EMPTY], (), False, digest)
    executable = tokens[0][0]
    if executable.startswith("#"):
        return _finish([Limitation.COMMENT_PRESENT], (), False, digest)
    if executable not in {"cat"}:
        reason = (
            Limitation.FRAGMENT_COMMAND
            if executable in _FRAGMENT_EXECUTABLES
            else Limitation.COMMAND_UNSUPPORTED
        )
        return _finish([reason], (), False, digest)

    reasons: list[Limitation] = []
    operands: list[NormalizedPath] = []
    terminator_seen = False
    for token, _start, _end in tokens[1:]:
        # The option terminator is processed once; a later ``--`` is a
        # literal operand and stays in the actual complete member list.
        if token == "--" and not terminator_seen:
            terminator_seen = True
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
        return _finish([Limitation.COMMAND_EMPTY], (), False, digest)
    if reasons:
        return _finish(reasons, tuple(operands), False, digest)
    return _finish([], tuple(operands), True, digest)


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

    JSON decoding is bounded: a raw argument string longer than the worst
    case of the command bound plus JSON wrapper/escaping overhead is typed
    unsupported without being parsed, and decoding errors (including
    nesting-depth ``RecursionError``) return the same typed result.
    """

    if isinstance(arguments, str):
        if len(arguments) > 2 * max_argument_chars + 128:
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
