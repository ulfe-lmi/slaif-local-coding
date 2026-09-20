"""Documentation consistency gate (order 013-i, B8; extended by order 013-j, J2).

Scoped, mechanical checks over the CURRENT user-facing docs only. This is a
small gate, not a style linter, and it deliberately does not touch the
immutable OAP transcripts (``oap/``) or the historical objective ledgers.
Truthful prose stating that Docker users need no Python/uv is NOT banned;
required build-tool COMMANDS are.

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
   Python/uv/build-free);
8. order 013-j, J2: README.md is release-state-free (no '## Release status'
   heading, no 'being prepared and frozen', no Objective-013 history);
9. order 013-j, J2: QUICKSTART.md and INSTALL.md are coherent operator
   sessions — the three ``export SLAIF_...`` session variables are present,
   and no command-local ``SLAIF_CONFIG_FILE=``/``SLAIF_ENV_FILE=``
   assignments survive;
10. order 013-j, J2: the minimal Docker path is self-contained — no
    ``readyz-wait`` helper reference in QUICKSTART.md or in INSTALL.md
    before the advanced marker;
11. order 013-j, J2: no "stop whatever owns the port"-style instruction in
    the scoped docs;
12. order 013-j, J2: QUICKSTART.md and INSTALL.md document the actual
    qualified platform (``linux/amd64``), the external GHCR reader scope
    (``read:packages``), and registry-manifest-digest verification
    (``RepoDigests``);
13. order 013-j, J2: the three secret roles are guarded fail-closed with
    ``${VAR:?...}`` in the QUICKSTART.md and INSTALL.md env-file creation;
14. order 013-j, J1: the "content-addressed source tag" terminology does
    not survive in current docs, the compose file, or the release workflow
    (``sha-<S>`` is a MUTABLE source alias; the digest is
    content-addressed);
15. order 013-j, J2: file-specific stale current-claim patterns for
    ARCHITECTURE.md (the R18 Gateway-peer-hold / 'PENDING as of this PR'
    publication state) and docs/RELEASE-CUTOVER-RUNBOOK.md (the 013-b
    publication attribution and the release_record.json current claim).

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
# Order 013-j, J2: the stale-claim wording check additionally covers the
# current architecture sections and the cutover runbook (both carry
# historical blocks that must stay unmistakably historical).
CLAIM_DOCS: tuple[str, ...] = SCOPED_DOCS + (
    "ARCHITECTURE.md",
    "docs/RELEASE-CUTOVER-RUNBOOK.md",
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
RELEASE_WORKFLOW = ".github/workflows/release-image.yml"
# INSTALL.md: Python/uv build tokens are allowed only at or after this line.
ADVANCED_MARKER = "## Advanced: direct-host (systemd) installation"
# Build-toolchain tokens that must not appear on the primary operator path.
# These are required build-tool COMMANDS; truthful prose such as "no Python,
# no uv, and no local build on this path" does not contain them.
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
# Order 013-j, J2: README is the stable landing page — no release-state
# section, no transient freeze prose, no Objective-013 history (that history
# lives in the OAP transcript and docs/RELEASE-ARTIFACT-POLICY.md).
README_RELEASE_STATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("README '## Release status' section", re.compile(r"^##\s+Release status\s*$", re.MULTILINE)),
    (
        "README transient 'being prepared and frozen' prose",
        re.compile(r"being prepared and frozen", re.IGNORECASE),
    ),
    ("README Objective-013 history on the landing page", re.compile(r"Objective 013")),
)
# Order 013-j, J2: the coherent operator session (QUICKSTART.md, INSTALL.md).
SESSION_EXPORTS: tuple[str, ...] = (
    "export SLAIF_LOCAL_CODING_IMAGE=",
    "export SLAIF_CONFIG_FILE=",
    "export SLAIF_ENV_FILE=",
)
COMMAND_LOCAL_ENV_RE = re.compile(r"^\s*SLAIF_(?:CONFIG_FILE|ENV_FILE)=")
# Order 013-j, J2: fail-closed guards for the three secret roles.
SECRET_GUARDS: tuple[str, ...] = (
    "${QWEN3090_API_KEY:?",
    "${SLAIF_ADAPTER_SERVICE_TOKEN:?",
    "${SLAIF_ADAPTER_SIGNING_SECRET:?",
)
# Order 013-j, J2: facts the minimal Docker path must document.
OPERATOR_FACTS: tuple[tuple[str, str], ...] = (
    ("linux/amd64", "supported image platform"),
    ("read:packages", "external GHCR reader scope"),
    ("RepoDigests", "registry-manifest-digest verification"),
)
# Order 013-j, J1: the sha-<S> tag is a MUTABLE source alias, never a
# "content-addressed source tag"; the digest is the content-addressed
# identity.
CONTENT_ADDRESSED_SOURCE_TAG_RE = re.compile(r"content-addressed source tag", re.IGNORECASE)
# Order 013-j, J2: "stop whatever owns the port" style instructions.
STOP_WHOEVER_RE = re.compile(r"stop\s+whatever", re.IGNORECASE)
# Order 013-j, J2: file-specific stale current-claim patterns.
ARCHITECTURE_STALE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ARCHITECTURE.md R18 Gateway-peer-hold publication state",
        re.compile(r"\bR18\b"),
    ),
    (
        "ARCHITECTURE.md 'PENDING as of this PR' publication state",
        re.compile(r"PENDING as of this PR", re.IGNORECASE),
    ),
)
RUNBOOK_STALE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "RELEASE-CUTOVER-RUNBOOK.md 013-b current publication attribution",
        re.compile(r"publication has since been performed", re.IGNORECASE),
    ),
    (
        "RELEASE-CUTOVER-RUNBOOK.md release_record.json current-claim",
        re.compile(r"recorded in (?:`|)packaging/release_record\.json"),
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
    for rel in CLAIM_DOCS:
        path = root / rel
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for label, pattern in STALE_CLAIM_PATTERNS:
                if pattern.search(line):
                    violations.append(f"{rel}:{line_no}: stale-claim: {label}")


def _check_readme_release_state(root: Path, violations: list[str]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8")
    for label, pattern in README_RELEASE_STATE_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            violations.append(f"README.md:{line_no}: readme-release-state: {label}")


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
    marker_index = _advanced_marker_index(lines, violations)
    if marker_index is None:
        return
    for line_no in range(marker_index):
        token = _find_build_token(lines[line_no])
        if token is not None:
            violations.append(
                f"INSTALL.md:{line_no + 1}: install-pre-marker-build-token: "
                "build tooling is allowed only in the advanced direct-host "
                f"section ({token!r})"
            )


def _advanced_marker_index(lines: list[str], violations: list[str]) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == ADVANCED_MARKER:
            return index
    violations.append(
        f"INSTALL.md: install-marker: missing advanced marker line {ADVANCED_MARKER!r}"
    )
    return None


def _check_operator_session(root: Path, rel: str, violations: list[str]) -> None:
    """Order 013-j, J2: one coherent exported session per operator doc."""
    path = root / rel
    if not path.is_file():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    joined = "\n".join(lines)
    for export in SESSION_EXPORTS:
        if not any(line.lstrip().startswith(export) for line in lines):
            violations.append(
                f"{rel}: session-export: missing session variable "
                f"export {export!r} (every compose command must run in the "
                "same exported session)"
            )
    for line_no, line in enumerate(lines, start=1):
        if COMMAND_LOCAL_ENV_RE.match(line):
            violations.append(
                f"{rel}:{line_no}: command-local-env: command-local "
                "SLAIF_CONFIG_FILE/SLAIF_ENV_FILE assignment; export the "
                "session variables once instead"
            )
        if "readyz-wait" in line:
            violations.append(
                f"{rel}:{line_no}: readyz-wait-helper: the minimal Docker "
                "path must wait on the compose healthcheck directly (no "
                "packaging/readyz-wait.sh prerequisite)"
            )
        if STOP_WHOEVER_RE.search(line):
            violations.append(
                f"{rel}:{line_no}: stop-whatever: never instruct stopping a "
                "service the operator does not own"
            )
    for token, label in OPERATOR_FACTS:
        if token not in joined:
            violations.append(f"{rel}: operator-fact: missing {label} fact {token!r}")
    for guard in SECRET_GUARDS:
        if guard not in joined:
            violations.append(
                f"{rel}: secret-guard: missing fail-closed guard {guard!r} "
                "for the required secret input"
            )


def _check_content_addressed_terminology(root: Path, violations: list[str]) -> None:
    """Order 013-j, J1: no 'content-addressed source tag' in current prose."""
    for rel in CLAIM_DOCS + (COMPOSE_FILE, RELEASE_WORKFLOW):
        path = root / rel
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if CONTENT_ADDRESSED_SOURCE_TAG_RE.search(line):
                violations.append(
                    f"{rel}:{line_no}: content-addressed-source-tag: sha-<S> "
                    "is a MUTABLE source alias tag; the digest is the "
                    "content-addressed identity"
                )


def _check_file_specific_stale(root: Path, violations: list[str]) -> None:
    """Order 013-j, J2: the specific corrected claims must not return."""
    for rel, patterns in (
        ("ARCHITECTURE.md", ARCHITECTURE_STALE_PATTERNS),
        ("docs/RELEASE-CUTOVER-RUNBOOK.md", RUNBOOK_STALE_PATTERNS),
    ):
        path = root / rel
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for label, pattern in patterns:
                if pattern.search(line):
                    violations.append(f"{rel}:{line_no}: file-stale-claim: {label}")


def check_repo(root: Path) -> list[str]:
    """Run every scoped check; return the violation list (empty = pass)."""
    violations: list[str] = []
    _check_required_files(root, violations)
    _check_readme_links(root, violations)
    _check_links(root, violations)
    _check_stale_claims(root, violations)
    _check_readme_release_state(root, violations)
    _check_compose_pull_only(root, violations)
    _check_quickstart_no_build(root, violations)
    _check_install_marker_gating(root, violations)
    _check_operator_session(root, "QUICKSTART.md", violations)
    _check_operator_session(root, "INSTALL.md", violations)
    _check_content_addressed_terminology(root, violations)
    _check_file_specific_stale(root, violations)
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
    print(f"docs consistency: OK ({len(CLAIM_DOCS)} claim docs checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
