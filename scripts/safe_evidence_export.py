"""Fail-closed safe-evidence export and the Objective-008-a historical audit.

This is acceptance/OAP tooling only (expected production ``src/`` delta:
none).  It performs zero network, provider, model, service, credential, Git
staging/commit, or GitHub operations: it is stdlib-only plus the
repository-owned safe-evidence machinery under ``tests/helpers``.

Commands
--------

``export``
    Read one exact already-sanitized result file through the bounded
    symlink-proof reader, validate it against one closed role schema, and
    atomically export it (exact or deterministic bytes) into the
    repository ``oap/evidence`` root.  Prints exactly one JSON line: the
    bounded provenance record on success, or ``{"rejected": "<class>"}``
    (exit status 2) on any violation.  A destination that already exists is
    refused, never overwritten.

``historical-audit``
    Inspect exactly the four literal historical paths pinned by the
    008-a work order (and no other historical path).  The three retained
    authorities (final protected 1024 success, decisive 32-token
    diagnostic, final isolated fake target) are admitted through the full
    audit (bounded read, closed schema, privacy scan) and accepted exact
    bytes are preserved under stable names in ``oap/evidence/005-ar/``.
    The fourth (AP37) authority is an optional source that is *not*
    retained: it is classified by bounded stat-only preflight under one
    fixed content-free classification (``optional_not_retained`` when
    present and path-safe, the availability class when absent, a fixed
    rejection class when path-unsafe) and no content, size, or hash fact
    is produced for it.  The strict post-hoc manifest
    ``oap/evidence/005-ar/manifest.json`` records all four authorities
    plus the fixed non-retention decision.  Prints exactly one JSON line
    containing classes, sizes, and hashes only.

No command ever prints raw artifact content, secrets, or exception detail.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.helpers import safe_evidence_contracts as contracts  # noqa: E402
from tests.helpers.safe_evidence import (  # noqa: E402
    UnsafeEvidenceError,
    accept_evidence_bytes,
    export_safe_result,
    safe_read_bounded,
    safe_stat_bounded,
    validate_value,
)

EVIDENCE_SUBDIR: str = "005-ar"


@dataclass(frozen=True)
class Authority:
    """One exact historical authority for the 008-a audit.

    ``authority_role`` is the closed manifest role (the stable evidence
    name); ``role`` is the closed export result schema a retained artifact
    must satisfy (``None`` for the not-retained AP37 authority);
    ``retained`` marks whether the artifact is admitted through the full
    content audit and exported, or only classified by bounded stat-only
    preflight under the fixed non-retention classification.
    """

    authority_role: str
    role: str | None
    source: str
    relative_path: str
    retained: bool = True


#: The four exact paths authorized by the 008-a work order.  Nothing else
#: is inspected; the list is exhaustive and literal.
HISTORICAL_AUTHORITIES: tuple[Authority, ...] = (
    Authority(
        authority_role="protected_final_1024_success",
        role="protected_target",
        source="/tmp/slaif-005-ar-protected-1024.O7Zsxd/protected-result.json",
        relative_path=f"{EVIDENCE_SUBDIR}/protected_final_1024_success.json",
    ),
    Authority(
        authority_role="protected_32_token_diagnostic",
        role="protected_target",
        source="/tmp/slaif-005-ar-protected.GjMeEO/protected-result.json",
        relative_path=f"{EVIDENCE_SUBDIR}/protected_32_token_diagnostic.json",
    ),
    Authority(
        authority_role="fake_isolated_target",
        role="fake_target",
        source="/tmp/slaif-005-ar-isolated-fake-1024.aipZdW/isolated-fake-target.json",
        relative_path=f"{EVIDENCE_SUBDIR}/fake_isolated_target_1024.json",
    ),
    Authority(
        authority_role="fake_ap37_gate_authority",
        role=None,
        source="/tmp/slaif-005-ap-fake-gate.rHO7rQ",
        relative_path=f"{EVIDENCE_SUBDIR}/fake_ap37_gate_authority.json",
        retained=False,
    ),
)

UNAVAILABLE_CLASS: str = "historical_temp_artifact_unavailable_on_this_host"


def _entry(
    authority: Authority,
    *,
    availability: str,
    rejection_class: str | None,
    relative_path: str | None,
    original_sha256: str | None,
    committed_sha256: str | None,
    byte_count: int | None,
) -> dict[str, object]:
    return {
        "role": authority.authority_role,
        "availability": availability,
        "rejection_class": rejection_class,
        "relative_path": relative_path,
        "original_sha256": original_sha256,
        "committed_sha256": committed_sha256,
        "byte_count": byte_count,
    }


def _classify_not_retained(repo_root: Path, authority: Authority) -> dict[str, object]:
    """Classify the not-retained authority by bounded stat-only preflight.

    No content is read, hashed, or scanned: the result carries the exact
    fixed availability classification with null path/hash/count facts.
    """
    try:
        safe_stat_bounded(Path(authority.source))
    except UnsafeEvidenceError as exc:
        if exc.rejection_class == "unsafe_path_missing":
            return _entry(
                authority,
                availability="unavailable",
                rejection_class=UNAVAILABLE_CLASS,
                relative_path=None,
                original_sha256=None,
                committed_sha256=None,
                byte_count=None,
            )
        return _entry(
            authority,
            availability="rejected",
            rejection_class=exc.rejection_class,
            relative_path=None,
            original_sha256=None,
            committed_sha256=None,
            byte_count=None,
        )
    return _entry(
        authority,
        availability="optional_not_retained",
        rejection_class=None,
        relative_path=None,
        original_sha256=None,
        committed_sha256=None,
        byte_count=None,
    )


def _export_one(repo_root: Path, authority: Authority) -> dict[str, object]:
    """Admit one authority: full audit for retained, preflight otherwise."""
    if not authority.retained:
        return _classify_not_retained(repo_root, authority)
    role = authority.role
    if role is None:
        # Unreachable for the closed historical authorities: every retained
        # authority names a closed export role.  Fail closed regardless.
        raise UnsafeEvidenceError("role_unknown", authority.authority_role)
    result_spec = contracts.result_spec_for_role(role)
    preflight_spec = contracts.preflight_spec_for_role(role)
    try:
        raw = safe_read_bounded(Path(authority.source))
    except UnsafeEvidenceError as exc:
        if exc.rejection_class == "unsafe_path_missing":
            return _entry(
                authority,
                availability="unavailable",
                rejection_class=UNAVAILABLE_CLASS,
                relative_path=None,
                original_sha256=None,
                committed_sha256=None,
                byte_count=None,
            )
        return _entry(
            authority,
            availability="rejected",
            rejection_class=exc.rejection_class,
            relative_path=None,
            original_sha256=None,
            committed_sha256=None,
            byte_count=None,
        )
    try:
        _document, original_sha = accept_evidence_bytes(
            raw, result_spec, preflight_spec=preflight_spec
        )
    except UnsafeEvidenceError as exc:
        return _entry(
            authority,
            availability="rejected",
            rejection_class=exc.rejection_class,
            relative_path=None,
            original_sha256=None,
            committed_sha256=None,
            byte_count=None,
        )
    provenance = export_safe_result(
        repo_root,
        role=role,
        schema=contracts.ROLE_SCHEMAS[role],
        raw=raw,
        result_spec=result_spec,
        preflight_spec=preflight_spec,
        relative_path=authority.relative_path,
        mode="exact",
    )
    return _entry(
        authority,
        availability="accepted",
        rejection_class=None,
        relative_path=authority.relative_path,
        original_sha256=original_sha,
        committed_sha256=provenance.committed_sha256,
        byte_count=provenance.byte_count,
    )


def _build_manifest(entries: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "schema": contracts.MANIFEST_SCHEMA,
        "classification": "post_hoc_durable_preservation",
        "preserved_during_objective_005": False,
        "authorities": list(entries),
        "optional_not_retained": {
            "role": "fake_ap37_gate_authority",
            "classification": contracts.MANIFEST_OPTIONAL_NOT_RETAINED,
            "reason": contracts.MANIFEST_NOT_RETAINED_REASON,
        },
        "historical_authority": {
            "objective_005_merged_local_sha": contracts.OBJECTIVE_005_MERGED_LOCAL_SHA,
            "objective_005_tested_local_sha": contracts.OBJECTIVE_005_TESTED_LOCAL_SHA,
            "objective_005_implementation_parent_sha": (
                contracts.OBJECTIVE_005_IMPLEMENTATION_PARENT_SHA
            ),
            "objective_005_immutable_report_path": (contracts.OBJECTIVE_005_IMMUTABLE_REPORT_PATH),
            "objective_005_immutable_report_sha": contracts.OBJECTIVE_005_IMMUTABLE_REPORT_SHA,
            "historical_gateway_sha": contracts.GATEWAY_MAIN_SHA,
        },
        "acceptance_relationship": {
            "objective_005_acceptance": "accepted",
            "pr7_strategic_correction": "cited_not_rewritten",
        },
    }


def run_audit(
    repo_root: Path,
    authorities: tuple[Authority, ...] = HISTORICAL_AUTHORITIES,
) -> dict[str, object]:
    """Run the full audit; return the bounded machine-readable summary."""
    entries = tuple(_export_one(repo_root, authority) for authority in authorities)
    manifest = _build_manifest(entries)
    manifest_document = json.loads(json.dumps(manifest, sort_keys=True, separators=(",", ":")))
    validate_value(contracts.MANIFEST_SPEC, manifest_document, "manifest")
    manifest_bytes = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    manifest_provenance = export_safe_result(
        repo_root,
        role="manifest",
        schema=contracts.ROLE_SCHEMAS["manifest"],
        raw=manifest_bytes,
        result_spec=contracts.result_spec_for_role("manifest"),
        preflight_spec=contracts.preflight_spec_for_role("manifest"),
        relative_path=f"{EVIDENCE_SUBDIR}/manifest.json",
        mode="deterministic",
    )
    return {
        "authorities": list(entries),
        "manifest": {
            "relative_path": manifest_provenance.relative_path,
            "sha256": manifest_provenance.committed_sha256,
            "byte_count": manifest_provenance.byte_count,
        },
    }


def _cmd_export(args: argparse.Namespace) -> int:
    repo_root: Path = args.repo_root
    raw = safe_read_bounded(Path(args.source))
    role = args.role
    result_spec = contracts.result_spec_for_role(role)
    preflight_spec = contracts.preflight_spec_for_role(role)
    provenance = export_safe_result(
        repo_root,
        role=role,
        schema=contracts.ROLE_SCHEMAS[role],
        raw=raw,
        result_spec=result_spec,
        preflight_spec=preflight_spec,
        relative_path=args.destination,
        mode=args.mode,
    )
    print(provenance.to_json())
    return 0


def _cmd_historical_audit(args: argparse.Namespace) -> int:
    summary = run_audit(args.repo_root)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed safe-evidence export (acceptance/OAP tooling only)."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root containing oap/evidence (default: this repository)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser("export", help="export one exact sanitized result")
    export.add_argument("--source", required=True, help="exact source file path")
    export.add_argument(
        "--role",
        required=True,
        choices=sorted(contracts.ROLES - {"manifest"}),
        help="closed result role",
    )
    export.add_argument(
        "--destination",
        required=True,
        help="relative destination inside oap/evidence",
    )
    export.add_argument(
        "--mode",
        required=True,
        choices=("exact", "deterministic"),
        help="exact accepted bytes or deterministic re-serialization",
    )
    export.set_defaults(func=_cmd_export)

    audit = sub.add_parser(
        "historical-audit",
        help="audit and preserve the four exact 008-a historical paths",
    )
    audit.set_defaults(func=_cmd_historical_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Callable[[argparse.Namespace], int] = args.func
    try:
        return handler(args)
    except UnsafeEvidenceError as exc:
        print(json.dumps({"rejected": exc.rejection_class}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
