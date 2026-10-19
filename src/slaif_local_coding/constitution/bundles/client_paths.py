"""Literal client-workspace path normalization (pure, no filesystem access).

The client path domain is separate from the adapter host.  Normalization is
strictly lexical over the exact observed operand text: this module never
subprocesses, never expands environment variables or globs, never resolves
symlinks, and never stats or reads the client or adapter filesystem.  A path
that does not exist on the client still normalizes; existence is not an
observation fact.

Lexical policy (documented in ``docs/CACHE-OBSERVATION-CONTRACT.md``):

- operands are literal POSIX path strings; URL fragment/query characters are
  not special and are never stripped (``A.md#frag`` is a different file from
  ``A.md``);
- ``.`` and ``..`` segments are resolved lexically, but any resolution step
  whose prefix leaves the evidenced workspace is rejected as traversal;
- absolute client paths are accepted only when their component sequence
  begins with the evidenced workspace's component sequence (component
  comparison, never string-prefix comparison: ``/work-other/A.md`` is
  outside ``/work``);
- relative operands resolve against the explicit supported workdir, else the
  evidenced workspace (the evidenced default client cwd); with neither they
  are unproven, never resolved against an adapter-host cwd.
"""

from __future__ import annotations

from typing import TypeGuard

from ..bundles.observation_models import (
    Limitation,
    NormalizedPath,
    PathContext,
    PathForm,
    contains_lone_surrogates,
)

#: Shell metacharacters that make a token non-literal (per-token; whitespace
#: is handled by tokenization, a leading ``#`` is a comment, handled by the
#: grammar).  ``#`` and ``?`` mid-token are literal filename characters.
_META = set("$`\\*?[]{}~^|&;<>()!")


def validate_workspace(label: str, max_bytes: int) -> str | None:
    """Return the normalized absolute POSIX workspace, or ``None``.

    The label must be an exact literal absolute POSIX path: no relative form,
    no backslash/UNC/drive alternate roots, no ``..`` segments, no control
    characters, and bounded length.  Empty and ``.`` segments are collapsed.
    """

    if not label or any(ord(c) < 0x20 or ord(c) == 0x7F or c.isspace() for c in label):
        return None
    if contains_lone_surrogates(label):
        # Malformed Unicode is never UTF-8-encoded here (the byte checks
        # below would raise): the label is simply not a valid workspace.
        return None
    if "\\" in label or label.startswith("~"):
        return None
    if len(label.encode("utf-8")) > max_bytes:
        return None
    if not label.startswith("/") or label.startswith("//"):
        return None
    parts = label[1:].split("/")
    if any(part == ".." for part in parts):
        return None
    cleaned = [part for part in parts if part not in ("", ".")]
    if not cleaned:
        return None
    normalized = "/" + "/".join(cleaned)
    if len(normalized.encode("utf-8")) > max_bytes:
        return None
    return normalized


def _is_posix_workspace(value: str | None) -> TypeGuard[str]:
    return value is not None and value.startswith("/") and not value.startswith("//")


def _resolve(
    base_parts: list[str],
    segments: list[str],
    workspace_parts: list[str],
) -> tuple[list[str] | None, Limitation | None]:
    """Lexically resolve *segments* from *base_parts*, staying in workspace."""

    stack: list[str] = list(base_parts)
    used_dotdot = False
    for segment in segments:
        if segment in ("", "."):
            continue
        is_dotdot = segment == ".."
        if is_dotdot:
            used_dotdot = True
            if stack:
                stack.pop()
        else:
            stack.append(segment)
        if used_dotdot and len(stack) < len(workspace_parts):
            return None, Limitation.TRAVERSAL
        if len(stack) > len(workspace_parts) and stack[: len(workspace_parts)] != workspace_parts:
            return None, Limitation.OUTSIDE_WORKSPACE
    if len(stack) <= len(workspace_parts):
        # The workspace directory itself (or an ancestor): not a file path.
        return None, Limitation.AMBIGUOUS_PATH
    return stack, None


def normalize_read_path(
    raw: str,
    context: PathContext,
    max_path_bytes: int,
) -> NormalizedPath:
    """Normalize one literal read operand under an evidenced context.

    ``raw`` is expected to be a clean literal token from the read grammar;
    this function re-validates literalness defensively (including fully-
    quoted operands under the no-spaces convention) and never touches any
    filesystem.  Quoted operands keep a ``quoted`` mark; the inner path text
    is what normalizes.
    """

    def _reject(limitation: Limitation, form: PathForm, quoted: bool) -> NormalizedPath:
        return NormalizedPath(raw=raw, form=form, quoted=quoted, limitation=limitation)

    if not raw:
        return _reject(Limitation.EMPTY_OPERAND, PathForm.RELATIVE, False)
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in raw) or raw != raw.strip():
        return _reject(Limitation.AMBIGUOUS_PATH, PathForm.RELATIVE, False)

    if any(c in raw for c in "'\"") and not (
        len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"')
    ):
        # Quote characters that do not form a clean fully-quoted literal.
        return _reject(Limitation.QUOTED_OPERAND, PathForm.RELATIVE, False)

    quoted = False
    token = raw
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        inner = raw[1:-1]
        if not inner or any(c in _META or c in "'\"" or c.isspace() for c in inner):
            return _reject(Limitation.QUOTED_OPERAND, PathForm.RELATIVE, False)
        token = inner
        quoted = True

    if token.startswith("#"):
        return _reject(Limitation.COMMENT_PRESENT, PathForm.RELATIVE, quoted)
    if any(c.isspace() for c in token):
        # Agreed no-spaces file convention: a path label carrying any
        # whitespace character (including non-ASCII such as NBSP) is not a
        # representable literal member.  It is typed ambiguous — never
        # silently split into fabricated files.
        form = PathForm.ABSOLUTE if token.startswith("/") else PathForm.RELATIVE
        return _reject(Limitation.AMBIGUOUS_PATH, form, quoted)
    if any(c in _META for c in token):
        return _reject(Limitation.NON_LITERAL_OPERAND, PathForm.RELATIVE, quoted)
    if "\\" in token or token.startswith("~"):
        return _reject(Limitation.UNSUPPORTED_PATH_FORM, PathForm.RELATIVE, quoted)

    form = PathForm.ABSOLUTE if token.startswith("/") else PathForm.RELATIVE
    if form is PathForm.ABSOLUTE and token.startswith("//"):
        return _reject(Limitation.UNSUPPORTED_PATH_FORM, form, quoted)
    if len(token.encode("utf-8")) > max_path_bytes:
        return _reject(Limitation.PATH_TOO_LONG, form, quoted)

    workspace = context.workspace
    if not _is_posix_workspace(workspace):
        # No evidenced POSIX workspace: never guess, never use a host cwd.
        return _reject(
            Limitation.UNKNOWN_WORKSPACE if form is PathForm.ABSOLUTE else Limitation.UNPROVEN_CWD,
            form,
            quoted,
        )
    workspace_parts = [p for p in workspace[1:].split("/") if p]

    if form is PathForm.ABSOLUTE:
        segments = token[1:].split("/")
        resolved, limitation = _resolve([], segments, workspace_parts)
    else:
        if context.workdir is not None:
            base = validate_workspace(context.workdir, max_bytes=max_path_bytes)
            base_parts = [p for p in base[1:].split("/") if p] if base else []
            if (
                not base
                or len(base_parts) < len(workspace_parts)
                or base_parts[: len(workspace_parts)] != workspace_parts
            ):
                return _reject(Limitation.OUTSIDE_WORKSPACE, form, quoted)
        else:
            base_parts = workspace_parts
        resolved, limitation = _resolve(base_parts, token.split("/"), workspace_parts)

    if resolved is None:
        return _reject(limitation or Limitation.AMBIGUOUS_PATH, form, quoted)
    normalized = "/".join(resolved[len(workspace_parts) :])
    if not normalized:
        return _reject(Limitation.AMBIGUOUS_PATH, form, quoted)
    if len(normalized.encode("utf-8")) > max_path_bytes:
        return _reject(Limitation.PATH_TOO_LONG, form, quoted)
    return NormalizedPath(raw=raw, form=form, quoted=quoted, normalized=normalized)
