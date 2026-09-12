"""Path and subprocess guards for repository-owned diagnostics.

These checks are intentionally small and fail closed.  Diagnostic callers must
create a disposable root first and explicitly allow every executable they run;
no helper in this module searches the host filesystem.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from pathlib import Path


class UnsafeDiagnosticPath(ValueError):
    """Raised before a diagnostic can access an unapproved path or command."""


_FORBIDDEN_EXPANSIONS = ("$HOME", "${HOME}", "$CODEX_HOME", "${CODEX_HOME}")


def _raw_path(value: Path | str) -> str:
    raw = os.fspath(value)
    if isinstance(raw, bytes):
        raise UnsafeDiagnosticPath("diagnostic path must be text")
    return raw


def _resolved(path: Path | str) -> Path:
    raw = _raw_path(path)
    if not raw or raw in {"/", "~", ".", ".."}:
        raise UnsafeDiagnosticPath("broad diagnostic path")
    if any(marker in raw for marker in _FORBIDDEN_EXPANSIONS):
        raise UnsafeDiagnosticPath("environment path expansion is not allowed")
    if raw.startswith("~"):
        raise UnsafeDiagnosticPath("home-relative diagnostic path")
    if ".." in Path(raw).parts:
        raise UnsafeDiagnosticPath("unresolved traversal")
    return Path(raw).expanduser().resolve(strict=False)


def require_driver_path(
    path: Path | str,
    *,
    disposable_root: Path,
    allow_root: bool = False,
) -> Path:
    """Return a path only when it is beneath the caller-owned temp root."""

    root = Path(disposable_root).resolve(strict=False)
    candidate = _resolved(path)
    if candidate == root:
        if allow_root:
            return candidate
        raise UnsafeDiagnosticPath("disposable root is not a file target")
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise UnsafeDiagnosticPath("path is outside disposable root") from exc
    return candidate


def require_allowlisted_executable(
    executable: Path | str,
    *,
    allowed_executables: Iterable[Path | str],
) -> Path:
    """Require an executable path to match one explicitly supplied by caller."""

    candidate = Path(_raw_path(executable)).resolve(strict=False)
    allowed = {Path(_raw_path(item)).resolve(strict=False) for item in allowed_executables}
    if candidate not in allowed:
        raise UnsafeDiagnosticPath("diagnostic executable is not allowlisted")
    return candidate


def assert_allowlisted_diagnostic_argv(
    argv: Sequence[str],
    *,
    allowed_commands: Iterable[str],
    allowed_executables: Iterable[Path | str] = (),
    disposable_root: Path | None = None,
    path_arguments: Iterable[Path | str] = (),
) -> None:
    """Validate a fixed diagnostic command before subprocess creation.

    ``allowed_commands`` is an explicit command allowlist.  ``path_arguments``
    are separately named paths and must be inside ``disposable_root``; this
    avoids guessing whether arbitrary diagnostic text is a filesystem path.
    """

    if not argv:
        raise UnsafeDiagnosticPath("empty diagnostic argv")
    command = Path(argv[0]).name
    if command not in set(allowed_commands):
        raise UnsafeDiagnosticPath("diagnostic command is not allowlisted")
    if Path(argv[0]).is_absolute():
        require_allowlisted_executable(argv[0], allowed_executables=allowed_executables)
    for argument in argv:
        if any(marker in argument for marker in _FORBIDDEN_EXPANSIONS) or argument.startswith("~"):
            raise UnsafeDiagnosticPath("host path expansion in diagnostic argv")
    if disposable_root is None:
        if tuple(path_arguments):
            raise UnsafeDiagnosticPath("path arguments require disposable root")
        return
    for path in path_arguments:
        require_driver_path(path, disposable_root=disposable_root)
