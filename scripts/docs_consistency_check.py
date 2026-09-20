"""Documentation consistency gate (order 013-i, B8).

Scoped, mechanical checks over the CURRENT user-facing docs only. This is a
small gate, not a style linter, and it deliberately does not touch the
immutable OAP transcripts (``oap/``) or the historical objective ledgers.

Checks:

1. required root documents exist (README/QUICKSTART/INSTALL/LICENSE/NOTICE
   plus the docs index);
2. README.md links to QUICKSTART.md and INSTALL.md;
3. every relative repository markdown link in the scoped docs resolves to a
   file or directory inside the repository (pure anchors and absolute
   URLs/mailto links are skipped);
4. no stale current-claim wording: 'this PR', 'pre-merge', 'benchmark
   pending', a claim that 0.1.0 (non-RC) is already released/available, or a
   claim that the final public release is already done/ready;
5. the primary Compose file (compose.yaml) is pull-based: no ``build:`` key;
6. QUICKSTART.md (the primary operator path) contains no Python/uv/pip/venv
   build instructions;
7. INSTALL.md contains those build instructions only after the advanced
   direct-host section marker (the Docker primary path stays
   Python/uv/build-free).

Usage:

    python scripts/docs_consistency_check.py [--repo-root PATH]

Prints one line per violation (``<file>:<line>: <check>: <detail>``); exits 0
iff no violations were found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The current user-facing doc set (order 013-i, B8 scope). OAP transcripts
# and historical ledgers are intentionally excluded.
SCOPED_DOCS: tuple[str, ...] = (
    "README.md",
    "QUICKSTART.md",
    "INSTALL.md",
    "docs/README.md",
    "docs/RC-HANDOFF.md",
    "docs/DOCKER-INSTALL.md",
    "docs/DEPLOYMENT.md",
    "docs/ADAPTER-CONFIGURATION.md",
    "docs/TOPOLOGY.md",
    "docs/DOCKER-SECURITY-DELTA.md",
    "docs/RELEASE-ARTIFACT-POLICY.md",
)
REQUIRED_ROOT_FILES: tuple[str, ...] = (
    "README.md",
    "QUICKSTART.md",
    "INSTALL.md",
    "LICENSE",
    "NOTICE",
    "docs/README.md",
)
COMPOSE_FILE = "compose.yaml"
# INSTALL.md: Python/uv build tokens are allowed only at or after this line.
ADVANCED_MARKER = "## Advanced: direct-host (systemd) installation"
# Build-toolchain tokens that must not appear on the primary operator path.
BUILD_TOKENS: tuple[str, ...] = (
    "uv build",
    "uv venv",
    "uv sync",
    "uv lock",
    "pip install",
    "python -m venv",
)
URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
COMPOSE_BUILD_KEY_RE = re.compile(r"^[ \t]+build:")
STALE_CLAIM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("current-prose 'this PR'", re.compile(r"\bthis PR\b")),
    ("current-prose 'pre-merge'", re.compile(r"\bpre-merge\b", re.IGNORECASE)),
    ("stale 'benchmark pending'", re.compile(r"benchmark\s+pending", re.IGNORECASE)),
    (
        "claim that 0.1.0 (non-RC) is already released/available",
        re.compile(
            r"0\.1\.0(?![\w.-])[^\n]{0,120}?"
            r"\b(?:is released|was released|has been released|is now available"
            r"|released to (?:ghcr|users))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "claim that the final public release is already done/ready",
        re.compile(
            r"final\s+(?:public\s+)?release\s+(?:is|has been|was|will be)\s+"
            r"(?:available|ready|done|final|shipped|complete)\b",
            re.IGNORECASE,
        ),
    ),
)


def _strip_code_fences(lines: list[str]) -> list[str | None]:
    """Return per-line text with fenced code blocks masked (None)."""
    out: list[str | None] = []
    in_fence = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(None)
            continue
        out.append(None if in_fence else line)
    return out


def _link_targets(text: str) -> list[tuple[int, str]]:
    """(line number, raw target) for markdown links, skipping code fences."""
    targets: list[tuple[int, str]] = []
    visible = _strip_code_fences(text.splitlines())
    for number, line in enumerate(visible, start=1):
        if line is None:
            continue
        for match in MARKDOWN_LINK_RE.finditer(line):
            raw = match.group(1).strip()
            # Drop an optional link title: (target "title").
            target = re.match(r"^\S+", raw)
            if target is None:
                continue
            targets.append((number, target.group(0)))
    return targets


def _check_required_files(root: Path, violations: list[str]) -> set[Path]:
    present: set[Path] = set()
    for rel in REQUIRED_ROOT_FILES:
        path = root / rel
        if path.is_file():
            present.add(Path(rel))
        else:
            violations.append(f"{rel}: required-file: missing required document")
    return present


def _check_readme_links(root: Path, violations: list[str]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        return  # already reported by the required-file check
    targets = [t for _, t in _link_targets(readme.read_text(encoding="utf-8"))]
    normalized: set[str] = set()
    for target in targets:
        base = target.split("#", 1)[0]
        if base:
            normalized.add(base)
    for expected in ("QUICKSTART.md", "INSTALL.md"):
        if expected not in normalized:
            violations.append(f"README.md: readme-links: missing link to {expected}")


def _check_links(root: Path, violations: list[str]) -> None:
    for rel in SCOPED_DOCS:
        path = root / rel
        if not path.is_file():
            continue  # missing files are reported separately (or out of scope)
        for line_no, target in _link_targets(path.read_text(encoding="utf-8")):
            if target.startswith("#"):
                continue  # pure in-document anchor
            if URL_SCHEME_RE.match(target):
                continue  # http/https/mailto/... absolute link
            base = target.split("#", 1)[0]
            if not base:
                continue
            resolved = (path.parent / base).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                violations.append(
                    f"{rel}:{line_no}: link-escapes-repo: {target!r} resolves "
                    "outside the repository"
                )
                continue
            if not resolved.exists():
                violations.append(f"{rel}:{line_no}: broken-link: {target!r}")


def _check_stale_claims(root: Path, violations: list[str]) -> None:
    for rel in SCOPED_DOCS:
        path = root / rel
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for label, pattern in STALE_CLAIM_PATTERNS:
                if pattern.search(line):
                    violations.append(f"{rel}:{line_no}: stale-claim: {label}")


def _check_compose_pull_only(root: Path, violations: list[str]) -> None:
    compose = root / COMPOSE_FILE
    if not compose.is_file():
        violations.append(f"{COMPOSE_FILE}: compose-missing: primary compose file absent")
        return
    for line_no, line in enumerate(compose.read_text(encoding="utf-8").splitlines(), start=1):
        if COMPOSE_BUILD_KEY_RE.match(line):
            violations.append(
                f"{COMPOSE_FILE}:{line_no}: compose-build-key: "
                "the primary compose file must stay pull-based (no build key)"
            )


def _find_build_token(line: str) -> str | None:
    lowered = line.lower()
    for token in BUILD_TOKENS:
        if token in lowered:
            return token
    return None


def _check_quickstart_no_build(root: Path, violations: list[str]) -> None:
    quickstart = root / "QUICKSTART.md"
    if not quickstart.is_file():
        return
    for line_no, line in enumerate(quickstart.read_text(encoding="utf-8").splitlines(), start=1):
        token = _find_build_token(line)
        if token is not None:
            violations.append(
                f"QUICKSTART.md:{line_no}: quickstart-build-token: "
                f"primary path must not require local build tooling ({token!r})"
            )


def _check_install_marker_gating(root: Path, violations: list[str]) -> None:
    install = root / "INSTALL.md"
    if not install.is_file():
        return
    lines = install.read_text(encoding="utf-8").splitlines()
    marker_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == ADVANCED_MARKER:
            marker_index = index
            break
    if marker_index is None:
        violations.append(
            f"INSTALL.md: install-marker: missing advanced marker line {ADVANCED_MARKER!r}"
        )
        return
    for line_no in range(marker_index):
        token = _find_build_token(lines[line_no])
        if token is not None:
            violations.append(
                f"INSTALL.md:{line_no + 1}: install-pre-marker-build-token: "
                "build tooling is allowed only in the advanced direct-host "
                f"section ({token!r})"
            )


def check_repo(root: Path) -> list[str]:
    """Run every scoped check; return the violation list (empty = pass)."""
    violations: list[str] = []
    _check_required_files(root, violations)
    _check_readme_links(root, violations)
    _check_links(root, violations)
    _check_stale_claims(root, violations)
    _check_compose_pull_only(root, violations)
    _check_quickstart_no_build(root, violations)
    _check_install_marker_gating(root, violations)
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root to check (default: this repository)",
    )
    args = parser.parse_args(argv)
    violations = check_repo(args.repo_root.resolve())
    if violations:
        for violation in violations:
            print(f"VIOLATION: {violation}")
        print(f"docs consistency: FAILED ({len(violations)} violation(s))")
        return 1
    print(f"docs consistency: OK ({len(SCOPED_DOCS)} scoped docs checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
