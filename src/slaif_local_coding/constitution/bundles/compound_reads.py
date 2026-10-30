"""Bounded literal read-plan grammar and outer attribution (D06/D07/D08).

Command syntax is **data**: this module parses, it never executes.  No
subprocess, no evaluation, no environment or glob expansion, no path
resolution against the client or adapter filesystem, no host cwd/stat/
resolve, and no external shell parser dependency (the supported surface is
a finite typed plan, not a general shell interpreter).

The earned plan surface is exactly:

    plan        := statement ('&&' statement)*
    statement   := cat_stmt | cd_stmt | echo_stmt
    cat_stmt    := 'cat' operand ...        (the exact earned cat option law)
    cd_stmt     := 'cd' absolute_literal_dir
    echo_stmt   := 'echo' 'quoted_literal'    (cooked value not dash-leading)

- Statements are joined only by the unquoted two-character ``&&`` operator
  token.  Adjacent-operator variants (``&&&``), semicolons, a single
  ``&``, pipes, redirections, substitutions, comments, heredocs, branches
  and any other metacharacter typed by the literal lexer keep the plan
  typed unsupported — an operator is earned only outside quotes; quoted
  operator text is a literal token, never a separator.  Unknown branch/
  control flow stays typed; later-command words are never reinterpreted
  as requested ``cat`` filenames.
- ``cat`` statements follow the exact earned option/terminator/stdin law
  (shared with the single-command grammar).  ``cd`` earns exactly one
  absolute literal directory that validates inside the evidenced
  workspace; relative, bare or multi-target ``cd`` forms are explicitly
  typed (``CD_TARGET_UNSUPPORTED``), never guessed.  ``echo`` earns
  exactly one clean fully-quoted literal whose cooked value is not
  dash-leading (``ECHO_TARGET_UNSUPPORTED`` otherwise): quoting does not
  disable ``echo``'s own option parser, so option-like cooked operands
  (``-n``, ``-e``, ``-E``, combinations and repetitions, in either quote
  kind) are implementation-sensitive and never earn a literal+newline
  boundary — the actual ``echo '-n'`` writes nothing.  Other
  executables are typed (``COMMAND_UNSUPPORTED`` / ``FRAGMENT_COMMAND``)
  and make the output structurally unattributable.
- Bounds are whole-plan, not per-segment: total characters
  (``max_command_chars``), total ``cat`` operands across all statements
  (``max_operands``, one shared budget), statement count (``max_operands``:
  every earned statement carries at least one operand-like token), output
  (wrapper ``max_output_chars``) and nesting (the plan is flat; any
  nesting metacharacter is typed unsupported).
- A complete plan plus a wrapper-proven exit-zero, untruncated, present
  output proves each requested read succeeded: the entire attributable
  content region is ONE ordered bundle, even without inner separators —
  repeated operands preserve observed order, distinct member width is
  recorded separately, and individual member hashes are never fabricated.
  Requested versus proven execution stay distinct, and the plan never
  invents per-command exit metadata: a global nonzero in an ``&&`` chain
  identifies no per-read failure and proves no earlier source complete;
  a semicolon/mixed chain never proves an earlier ``cat`` succeeded.
- ``cd`` transitions affect following reads only; the explicit supported
  per-call workdir takes precedence over the batch default before the
  first transition.  Absolute literal directory transitions suffice in
  this slice; other forms are explicitly typed.
- Outer regions: an earned leading/trailing ``echo`` literal is a
  deterministic prefix/suffix boundary proven at its exact position in
  the output; only the pure file-source span between them is attributable
  (its digest is never a whole mixed-output digest).  Printed delimiters
  are not a universal boundary oracle: collisions, unknown internal
  boundaries (an ``echo`` between reads) and extra output stay typed
  ``OUTER_BOUNDARY_UNPROVEN`` where proof is insufficient.  Non-read
  statements (``ls``, …) make the output structurally mixed: whole-
  request acquisition never claims support merely because ``cat``
  appears, and no listing rows or diagnostics are swallowed into a file
  bundle (no saved snapshot is a runtime oracle).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from ..bundles.client_paths import validate_workspace
from ..bundles.observation_models import (
    CharSpan,
    Limitation,
    NormalizedPath,
    PathContext,
    _Frozen,
    contains_lone_surrogates,
    sha256_hex,
)
from ..bundles.read_grammar import _FRAGMENT_EXECUTABLES, parse_cat_operands
from ..bundles.shell_tokens import LiteralToken, tokenize_command

#: Versioned finite read-plan grammar (distinct from the single-command
#: ``literal-shell-read/v1`` grammar it is built from).
READ_PLAN_GRAMMAR = "literal-read-plan/v1"


class PlanStatementKind(StrEnum):
    """Fixed plan-statement kinds (stable identifiers)."""

    CAT = "cat"
    CD = "cd"
    ECHO = "echo"
    #: Bounded listing statement (objective 017-am): the exact earned
    #: ``ls`` form (see ``_parse_statement``).  A recognized non-read:
    #: it never acquires a source, and a mixed plan carrying it keeps
    #: its structurally-mixed typing.
    LS = "ls"
    OTHER = "other"


class PlanStatement(_Frozen):
    """One typed statement of a finite read plan.

    ``raw_span`` is the half-open character span of the statement's tokens
    inside the exact command string.  ``cat_operands`` carries the
    requested cat members (with their typed path limitations, when any);
    ``cd_target`` is the validated absolute normalized directory of an
    earned ``cd``; ``echo_literal`` is the cooked fully-quoted literal of
    an earned ``echo``.  ``reasons`` are statement-level typed
    limitations; an earned statement has none.
    """

    kind: PlanStatementKind
    raw_span: CharSpan
    cat_operands: tuple[NormalizedPath, ...] = ()
    cd_target: str | None = None
    cd_target_raw: str | None = None
    echo_literal: str | None = None
    reasons: tuple[Limitation, ...] = ()


class ReadPlanParse(_Frozen):
    """Bounded literal read-plan parse result; command syntax is data.

    ``command_digest`` is the SHA-256 of the exact observed command bytes
    and is explicitly absent (``None``) only under the typed
    ``MALFORMED_UNICODE`` / non-string contract.  ``requested_members``
    preserves the actual statement/operand order of all ``cat`` operands
    (never a lexical or location sort).  ``cd_transitions`` records the
    validated absolute directory of each earned ``cd`` in statement
    order.  ``complete`` is true only for the exact earned all-cat/cd/
    bounded-echo surface with whole-plan bounds satisfied.
    """

    grammar: str = READ_PLAN_GRAMMAR
    command_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    command_length: int = Field(default=0, ge=0)
    complete: bool = False
    statements: tuple[PlanStatement, ...] = ()
    requested_members: tuple[NormalizedPath, ...] = ()
    cd_transitions: tuple[str, ...] = ()
    #: Objective 017-am (additive): true when the statements are exactly
    #: one or more clean ``ls`` statements followed by one or more clean
    #: ``cat`` statements (the bounded ``ls … && cat …`` shape).
    #: Recognition only — the mixed plan stays non-acquiring.
    ls_cat_shape: bool = False
    reasons: tuple[Limitation, ...] = ()


def _is_separator(token: LiteralToken) -> bool:
    """The earned statement separator: the exact unquoted ``&&`` token.

    Operators are earned only outside quotes: a quoted ``&&`` token is a
    literal (and carries its own quote limitation), never a separator;
    adjacent-operator variants such as ``&&&`` are not the separator.
    """

    return (
        not token.quoted
        and token.quote_limitation is None
        and token.operator is Limitation.MULTIPLE_COMMANDS
        and token.value == "&&"
    )


def _cd_target_ok(
    token: LiteralToken, context: PathContext, max_path_bytes: int
) -> tuple[str | None, Limitation | None]:
    """Validate one literal ``cd`` target inside the evidenced workspace."""

    workspace = context.workspace
    if not (isinstance(workspace, str) and workspace.startswith("/")):
        return None, Limitation.UNKNOWN_WORKSPACE
    workspace_parts = [part for part in workspace[1:].split("/") if part]
    normalized = validate_workspace(token.value, max_bytes=max_path_bytes)
    if normalized is None:
        # Relative, bare, ``..``-carrying, empty or over-bound targets:
        # absolute literal directory transitions suffice in this slice.
        return None, Limitation.CD_TARGET_UNSUPPORTED
    target_parts = [part for part in normalized[1:].split("/") if part]
    if len(target_parts) >= len(workspace_parts) and (
        target_parts[: len(workspace_parts)] == workspace_parts
    ):
        return normalized, None
    return None, Limitation.OUTSIDE_WORKSPACE


def _parse_statement(
    chunk: list[LiteralToken],
    command: str,
    context: PathContext,
    remaining_operands: int,
    max_path_bytes: int,
    start: int,
    end: int,
) -> tuple[PlanStatement, int]:
    """Parse one statement chunk; returns the statement and operands used."""

    if not chunk:
        return (
            PlanStatement(
                kind=PlanStatementKind.OTHER,
                raw_span=CharSpan(start=start, end=end),
                reasons=(Limitation.COMMAND_EMPTY,),
            ),
            0,
        )

    def _other(reason: Limitation) -> PlanStatement:
        return PlanStatement(
            kind=PlanStatementKind.OTHER,
            raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
            reasons=(reason,),
        )

    executable = chunk[0]
    if (
        executable.operator is not None
        or executable.quote_limitation is not None
        or executable.quoted
    ):
        reason = (
            executable.operator or executable.quote_limitation or Limitation.COMMAND_UNSUPPORTED
        )
        return _other(reason), 0
    rest = chunk[1:]
    value = executable.value

    if value == "cat":
        operands, reasons = parse_cat_operands(
            rest,
            command,
            context,
            remaining_operands,
            max_path_bytes,
            stop_at_operator=True,
        )
        if not operands and not reasons:
            # ``cat`` with no operand is not a read (same law as the
            # single-command grammar).
            return (
                PlanStatement(
                    kind=PlanStatementKind.CAT,
                    raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
                    reasons=(Limitation.COMMAND_EMPTY,),
                ),
                0,
            )
        return (
            PlanStatement(
                kind=PlanStatementKind.CAT,
                raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
                cat_operands=tuple(operands),
                reasons=tuple(reasons),
            ),
            len(operands),
        )

    if value == "cd":
        if len(rest) != 1:
            return _other(Limitation.CD_TARGET_UNSUPPORTED), 0
        target = rest[0]
        if target.operator is not None or target.quote_limitation is not None:
            return _other(Limitation.CD_TARGET_UNSUPPORTED), 0
        if not target.value.startswith("/") or target.value.startswith("//"):
            # Absolute literal directory transitions suffice in this
            # slice; relative and malformed forms are explicitly typed.
            return _other(Limitation.CD_TARGET_UNSUPPORTED), 0
        normalized, limitation = _cd_target_ok(target, context, max_path_bytes)
        if limitation is not None:
            return (
                PlanStatement(
                    kind=PlanStatementKind.CD,
                    raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
                    cd_target_raw=target.value,
                    reasons=(limitation,),
                ),
                0,
            )
        return (
            PlanStatement(
                kind=PlanStatementKind.CD,
                raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
                cd_target=normalized,
                cd_target_raw=target.value,
            ),
            0,
        )

    if value == "echo":
        if len(rest) != 1:
            return _other(Limitation.ECHO_TARGET_UNSUPPORTED), 0
        literal = rest[0]
        # Exactly one clean fully-quoted literal (the empty literal is
        # deterministic and earned); unquoted or quote-limited text is
        # explicitly typed, never a boundary.
        if not literal.quoted or literal.quote_limitation is not None:
            return _other(Limitation.ECHO_TARGET_UNSUPPORTED), 0
        if literal.value.startswith("-"):
            # Quoting does not disable echo's option parser: a
            # dash-leading cooked operand (either quote kind) is
            # implementation-sensitive — the actual ``echo '-n'`` writes
            # nothing — so it never earns a literal+newline boundary.
            # Command-local grammar semantics precede boundary matching:
            # matching file bytes cannot establish that an echo printed
            # them.
            return _other(Limitation.ECHO_TARGET_UNSUPPORTED), 0
        return (
            PlanStatement(
                kind=PlanStatementKind.ECHO,
                raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
                echo_literal=literal.value,
            ),
            0,
        )

    if value == "ls":
        # The exact bounded ls form (objective 017-am): a bare unquoted
        # ``ls`` (the executable checks above already reject operators,
        # quote limitations and quoting), zero or more unquoted literal
        # dash options, and at most one unquoted literal non-dash path.
        # Anything else stays typed exactly as today (OTHER /
        # COMMAND_UNSUPPORTED).  Recognition only: a listing never
        # acquires a source and contributes no members.
        non_dash = 0
        for token in rest:
            if token.operator is not None or token.quote_limitation is not None or token.quoted:
                return _other(Limitation.COMMAND_UNSUPPORTED), 0
            if token.value.startswith("-"):
                continue
            non_dash += 1
            if non_dash > 1:
                return _other(Limitation.COMMAND_UNSUPPORTED), 0
        return (
            PlanStatement(
                kind=PlanStatementKind.LS,
                raw_span=CharSpan(start=chunk[0].raw_start, end=chunk[-1].raw_end),
            ),
            0,
        )

    reason = (
        Limitation.FRAGMENT_COMMAND
        if value in _FRAGMENT_EXECUTABLES
        else Limitation.COMMAND_UNSUPPORTED
    )
    return _other(reason), 0


def parse_read_plan(
    command: str,
    context: PathContext,
    max_command_chars: int,
    max_operands: int,
    max_path_bytes: int,
) -> ReadPlanParse:
    """Parse one bounded literal command string into a typed read plan.

    Pure and total: the raw command is never retained (digest, length and
    typed statements only), nothing is executed or expanded, and every
    unsupported shape is a typed limitation, never a guess.  See the
    module docstring for the earned surface and the whole-plan bound law.
    """

    def _ls_cat_shape(statements_: tuple[PlanStatement, ...]) -> bool:
        """The bounded shape: one or more clean LS then one or more
        clean CAT (objective 017-am; recognition only)."""

        i = 0
        while (
            i < len(statements_)
            and statements_[i].kind is PlanStatementKind.LS
            and not statements_[i].reasons
        ):
            i += 1
        if i < 1 or i >= len(statements_):
            return False
        return all(
            statement.kind is PlanStatementKind.CAT and not statement.reasons
            for statement in statements_[i:]
        )

    def _finish(
        reasons: list[Limitation],
        statements: tuple[PlanStatement, ...] = (),
        digest: str | None = None,
        requested: tuple[NormalizedPath, ...] = (),
        cd_transitions: tuple[str, ...] = (),
        length: int = 0,
        ls_cat_shape: bool = False,
    ) -> ReadPlanParse:
        ordered: list[Limitation] = []
        for reason in reasons:
            if reason not in ordered:
                ordered.append(reason)
        complete = not ordered and any(
            statement.kind is PlanStatementKind.CAT and not statement.reasons
            for statement in statements
        )
        return ReadPlanParse(
            command_digest=digest,
            command_length=length,
            complete=complete,
            statements=statements,
            requested_members=requested,
            cd_transitions=cd_transitions,
            ls_cat_shape=ls_cat_shape,
            reasons=tuple(ordered),
        )

    if not isinstance(command, str):
        return _finish([Limitation.COMMAND_UNSUPPORTED])
    if contains_lone_surrogates(command):
        # Malformed Unicode is rejected before any UTF-8 hashing; the
        # digest is explicitly absent, never a placeholder.
        return _finish([Limitation.MALFORMED_UNICODE], length=len(command))
    digest = sha256_hex(command)
    if not command.strip():
        return _finish([Limitation.COMMAND_EMPTY], digest=digest, length=len(command))
    if len(command) > max_command_chars:
        return _finish([Limitation.COMMAND_OVER_BOUND], digest=digest, length=len(command))
    if "\n" in command or "\r" in command:
        return _finish([Limitation.MULTIPLE_COMMANDS], digest=digest, length=len(command))
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in command):
        # The control-character guard is not relaxed: POSIX blanks are not
        # interchangeable with CR/VT/FF anywhere in a plan.
        return _finish([Limitation.COMMAND_UNSUPPORTED], digest=digest, length=len(command))

    tokens = tokenize_command(command)
    # Split on the exact unquoted '&&' operator tokens; everything else
    # (including '&&&' and quoted '&&') stays inside a statement.
    chunks: list[list[LiteralToken]] = [[]]
    for token in tokens:
        if _is_separator(token):
            chunks.append([])
        else:
            chunks[-1].append(token)
    if len(chunks) > max_operands:
        # Whole-plan statement bound (every earned statement carries at
        # least one operand-like token); never a per-segment
        # multiplication.
        return _finish([Limitation.OVER_BOUND], digest=digest, length=len(command))

    statements: list[PlanStatement] = []
    requested: list[NormalizedPath] = []
    cd_transitions: list[str] = []
    reasons: list[Limitation] = []
    remaining = max_operands
    # The plan's starting directory is the explicit supported per-call
    # workdir (precedence over the batch default); literal cd
    # transitions then affect following reads only.
    current_workdir = context.workdir
    for chunk in chunks:
        start = chunk[0].raw_start if chunk else 0
        end = chunk[-1].raw_end if chunk else start
        statement, used = _parse_statement(
            chunk,
            command,
            PathContext(workspace=context.workspace, workdir=current_workdir),
            remaining,
            max_path_bytes,
            start,
            end,
        )
        statements.append(statement)
        remaining -= used
        if statement.kind is PlanStatementKind.CAT:
            requested.extend(statement.cat_operands)
        if (
            statement.kind is PlanStatementKind.CD
            and not statement.reasons
            and statement.cd_target is not None
        ):
            cd_transitions.append(statement.cd_target)
            current_workdir = statement.cd_target
        if statement.reasons:
            reasons.extend(statement.reasons)

    # A plan without any cat statement is not a read at all: typed, never
    # silently empty — unless a statement already carries its own typed
    # reason (the single-statement fragment law is preserved unchanged).
    if not any(statement.kind is PlanStatementKind.CAT for statement in statements) and not any(
        statement.reasons for statement in statements
    ):
        reasons.append(Limitation.COMMAND_UNSUPPORTED)

    multi = len(chunks) > 1
    if multi:
        # Any structurally mixed statement in a multi-statement plan
        # makes the combined output unattributable as pure file bytes:
        # listing rows, diagnostics and label lines are never swallowed
        # into a file bundle.  An earned LS statement is structurally
        # mixed exactly like an OTHER one (the listing extent is not
        # proven) and additionally marks the command family as not a
        # pure read: both reasons are kept for LS-containing plans.
        if any(
            statement.reasons
            or statement.kind is PlanStatementKind.OTHER
            or statement.kind is PlanStatementKind.LS
            for statement in statements
        ):
            reasons.append(Limitation.OUTER_BOUNDARY_UNPROVEN)
        if any(statement.kind is PlanStatementKind.LS for statement in statements):
            reasons.append(Limitation.COMMAND_UNSUPPORTED)
        # An echo strictly between reads is an unknown internal boundary:
        # a printed delimiter is not a universal boundary oracle.
        cat_indexes = [
            i for i, statement in enumerate(statements) if statement.kind is PlanStatementKind.CAT
        ]
        if cat_indexes and any(
            statements[i].kind is PlanStatementKind.ECHO
            for i in range(cat_indexes[0] + 1, cat_indexes[-1])
        ):
            reasons.append(Limitation.OUTER_BOUNDARY_UNPROVEN)
    return _finish(
        reasons,
        statements=tuple(statements),
        digest=digest,
        requested=tuple(requested),
        cd_transitions=tuple(cd_transitions),
        length=len(command),
        ls_cat_shape=_ls_cat_shape(tuple(statements)),
    )


def plan_source_region(
    plan: ReadPlanParse, content: str
) -> tuple[CharSpan | None, tuple[Limitation, ...]]:
    """Attributable source region of one complete plan's exact output content.

    Offsets are character offsets relative to *content* (the wrapper
    output region), with exact UTF-8 conversion available via
    ``CharSpan.to_byte_span``.  A plan without echo boundaries attributes
    the whole content; earned leading/trailing echo literals are proven at
    their exact positions (the echo newline terminator included) and only
    the pure file-source span between them is returned — a label inside a
    file stays source.  A collision (content shorter than prefix plus
    suffix), a mismatched boundary, an unknown internal boundary or extra
    output returns ``(None, (OUTER_BOUNDARY_UNPROVEN,))`` where proof is
    insufficient.  Incomplete plans never attribute.
    """

    if not plan.complete:
        return None, (Limitation.OUTER_BOUNDARY_UNPROVEN,)
    cat_indexes = [
        i for i, statement in enumerate(plan.statements) if statement.kind is PlanStatementKind.CAT
    ]
    if not cat_indexes:
        return None, (Limitation.OUTER_BOUNDARY_UNPROVEN,)
    first_cat, last_cat = cat_indexes[0], cat_indexes[-1]
    prefix_parts: list[str] = []
    suffix_parts: list[str] = []
    for index, statement in enumerate(plan.statements):
        if statement.kind is not PlanStatementKind.ECHO:
            continue
        literal = statement.echo_literal
        if literal is None:
            # An earned echo always carries its literal; missing is a
            # parser contract violation — fail typed, never attribute.
            return None, (Limitation.OUTER_BOUNDARY_UNPROVEN,)
        if index < first_cat:
            prefix_parts.append(literal + "\n")
        elif index > last_cat:
            suffix_parts.append(literal + "\n")
        else:
            # An echo between reads is an unknown internal boundary.
            return None, (Limitation.OUTER_BOUNDARY_UNPROVEN,)
    prefix = "".join(prefix_parts)
    suffix = "".join(suffix_parts)
    if not prefix and not suffix:
        return CharSpan(start=0, end=len(content)), ()
    if (
        len(content) < len(prefix) + len(suffix)
        or not content.startswith(prefix)
        or not content.endswith(suffix)
    ):
        return None, (Limitation.OUTER_BOUNDARY_UNPROVEN,)
    return CharSpan(start=len(prefix), end=len(content) - len(suffix)), ()
