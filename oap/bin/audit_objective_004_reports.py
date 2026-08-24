#!/usr/bin/env python3
"""Audit immutable Objective-004 report publication relationships."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

HEX40 = r"[0-9a-f]{40}"
REPORT_SHA_RE = re.compile(r"(?m)^-\s+Implementation head SHA:\s+`?([0-9a-f]+)`?\.?\s*$")

EXPECTED_REPORT = "oap/reports/004-k-unship-and-consolidate-e2e-diagnostics.md"
EXPECTED_SELF = "a29f3f97e61ce3bf40de86259798a34cce8db2b8"
EXPECTED_MALFORMED = "349a0fda7777870adc79952f9a77201470565b3"
EXPECTED_PARENT = "349a0afda7777870adc79952f9a77201470565b3"


class AuditError(RuntimeError):
    """Raised when the immutable report history violates the audit contract."""


@dataclass(frozen=True)
class Correction:
    report: str
    self_commit: str
    malformed: str
    corrected_parent: str


def git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def one_match(index_text: str, label: str, pattern: str) -> str:
    matches = re.findall(pattern, index_text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise AuditError(f"correction index has {len(matches)} {label} entries")
    return matches[0]


def load_correction(repo_root: Path) -> Correction:
    index_path = repo_root / "oap" / "REPORT-CORRECTIONS.md"
    try:
        index_text = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"cannot read correction index: {exc}") from exc

    correction = Correction(
        report=one_match(
            index_text,
            "affected report",
            r"^- Affected report: `([^`]+)`$",
        ),
        self_commit=one_match(
            index_text,
            "affected SELF commit",
            rf"^- Affected SELF commit: `({HEX40})`$",
        ),
        malformed=one_match(
            index_text,
            "malformed implementation SHA",
            r"^- Malformed implementation SHA literal: `([0-9a-f]{39})`$",
        ),
        corrected_parent=one_match(
            index_text,
            "corrected parent",
            rf"^- Corrected actual sole parent: `({HEX40})`$",
        ),
    )
    expected = Correction(
        EXPECTED_REPORT,
        EXPECTED_SELF,
        EXPECTED_MALFORMED,
        EXPECTED_PARENT,
    )
    if correction != expected:
        raise AuditError(f"unexpected correction mapping: {correction!r}")
    return correction


def report_addition(repo_root: Path, report_path: str) -> list[str]:
    output = git(
        repo_root,
        "log",
        "--all",
        "--full-history",
        "--diff-filter=A",
        "--format=%H",
        "--",
        report_path,
    )
    return output.splitlines() if output else []


def changed_paths(repo_root: Path, commit: str) -> list[str]:
    output = git(
        repo_root,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        "--format=",
        commit,
    )
    return output.splitlines() if output else []


def implementation_sha(report_text: str, report_path: str) -> str:
    matches = REPORT_SHA_RE.findall(report_text)
    if len(matches) != 1:
        raise AuditError(
            f"{report_path}: expected exactly one implementation SHA literal, found {len(matches)}"
        )
    return matches[0]


def audit(repo_root: Path) -> tuple[int, int, int, int, int, Correction]:
    correction = load_correction(repo_root)
    report_dir = repo_root / "oap" / "reports"
    reports = sorted(
        path for path in report_dir.glob("004-*.md") if path.is_file() and not path.is_symlink()
    )
    if not reports:
        raise AuditError("no Objective-004 reports found")

    additions_checked = 0
    sole_parent_checked = 0
    report_only_checked = 0
    literal_parent_checked = 0
    for report in reports:
        relative = report.relative_to(repo_root).as_posix()
        additions = report_addition(repo_root, relative)
        if len(additions) != 1:
            raise AuditError(
                f"{relative}: expected exactly one adding commit, found {len(additions)}"
            )
        self_commit = additions[0]
        additions_checked += 1
        if self_commit == correction.self_commit and relative != correction.report:
            raise AuditError(f"{relative}: correction SELF is attached to another report")
        if relative == correction.report and self_commit != correction.self_commit:
            raise AuditError(f"{relative}: SELF commit differs from correction index")

        parents = git(repo_root, "show", "-s", "--format=%P", self_commit).split()
        if len(parents) != 1:
            raise AuditError(
                f"{relative}: publication commit has {len(parents)} parents, expected 1"
            )
        parent = parents[0]
        sole_parent_checked += 1

        paths = changed_paths(repo_root, self_commit)
        expected_diff = f"A\t{relative}"
        if paths != [expected_diff]:
            raise AuditError(f"{relative}: publication diff is not report-only: {paths!r}")
        report_only_checked += 1

        report_sha = implementation_sha(report.read_text(encoding="utf-8"), relative)
        if relative == correction.report:
            if report_sha != correction.malformed:
                raise AuditError(f"{relative}: malformed literal differs from correction index")
            expected_parent = correction.corrected_parent
        else:
            if not re.fullmatch(HEX40, report_sha):
                raise AuditError(f"{relative}: implementation SHA is not exactly 40 hex characters")
            expected_parent = parent
        if parent != expected_parent:
            raise AuditError(
                f"{relative}: implementation SHA/sole parent mismatch ({report_sha} vs {parent})"
            )
        literal_parent_checked += 1

    if correction.report not in {path.relative_to(repo_root).as_posix() for path in reports}:
        raise AuditError(f"correction report is absent: {correction.report}")
    return (
        len(reports),
        additions_checked,
        sole_parent_checked,
        report_only_checked,
        literal_parent_checked,
        correction,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root (defaults to the checkout containing this script)",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        reports, additions, parents, report_only, literals, correction = audit(repo_root)
    except (AuditError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Objective-004 report audit: FAILED — {exc}")
        return 1

    print("Objective-004 report audit: PASSED")
    print(f"Reports discovered: {reports}")
    print(f"Report additions checked: {additions}")
    print(f"Sole-parent checks: {parents}")
    print(f"Report-only publication diffs: {report_only}")
    print(f"Implementation-SHA/parent checks: {literals} (one explicit correction)")
    print(f"Correction applied: {correction.report} ({correction.self_commit})")
    print("Unresolved problems: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
