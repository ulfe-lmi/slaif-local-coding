"""Fail-closed safe-evidence export and the Objective-008 historical audit.

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
    (exit status 2) on any violation.  A destination that already exists
    is refused, never overwritten.

``historical-audit``
    Inspect exactly the four literal historical paths pinned by the
    008-a/008-b work orders (and no other historical path).  All four
    authorities are retained: the final protected 1024 success, the
    decisive 32-token diagnostic, the final isolated fake target, and the
    AP37 fake machine-gate authority (closed ``full_fake_gate`` role,
    exported under the stable name ``reused_ap37_fake_gate.json``).
    Every retained authority is admitted through the full audit (bounded
    read, closed schema, privacy scan) and the accepted exact bytes are
    preserved under stable names in ``oap/evidence/005-ar/``.  A
    destination that already exists is only re-verified (byte-identical
    SHA-256 read-back); a byte deviation is refused fail-closed, never
    overwritten.  The strict post-hoc manifest
    ``oap/evidence/005-ar/manifest.json`` records all four authorities.
    Destination read-backs use the anchored (repository-root) bounded
    reader, so verification and replacement also work on hosts where the
    repository sits below execute-only mount points.  The 008-b one-shot
    replacement: if the manifest already exists it must match the exact
    pinned Objective-008-a byte identity (SHA-256 and byte count) to be
    replaced; any other pre-existing manifest is refused.  The
    replacement is therefore exactly once per host.  Prints exactly one
    JSON line containing classes, sizes, and hashes only.

No command ever prints raw artifact content, secrets, or exception detail.
"""

from __future__ import annotations

import argparse
import hashlib
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
    read_existing_evidence_destination_bounded,
    remove_verified_evidence_destination,
    safe_read_bounded,
    validate_value,
    verify_existing_evidence_destination,
)

EVIDENCE_SUBDIR: str = "005-ar"


@dataclass(frozen=True)
class Authority:
    """One exact retained historical authority for the 008 audit.

    ``authority_role`` is the closed manifest role (the stable evidence
    name); ``role`` is the closed export result schema the artifact must
    satisfy; ``relative_path`` is the exact stable repository destination.
    """

    authority_role: str
    role: str
    source: str
    relative_path: str


#: The four exact paths authorized by the 008-a/008-b work orders.
#: Nothing else is inspected; the list is exhaustive and literal.
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
        role="full_fake_gate",
        source="/tmp/slaif-005-ap-fake-gate.rHO7rQ",
        relative_path=f"{EVIDENCE_SUBDIR}/reused_ap37_fake_gate.json",
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


def _export_one(repo_root: Path, authority: Authority) -> dict[str, object]:
    """Admit one authority through the full content audit and preserve it.

    A destination that already exists is only re-verified: a byte-identical
    SHA-256 read-back records the acceptance without any write; any
    deviation is refused fail-closed (``destination_bytes_mismatch`` or a
    bounded read class) and the pre-existing file is never touched.
    """
    role = authority.role
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
    try:
        byte_count = verify_existing_evidence_destination(
            repo_root, authority.relative_path, original_sha
        )
    except UnsafeEvidenceError as exc:
        if exc.rejection_class != "destination_missing":
            # A pre-existing destination that does not carry the accepted
            # exact bytes is a conflict: refuse, never overwrite.
            raise
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
    return _entry(
        authority,
        availability="accepted",
        rejection_class=None,
        relative_path=authority.relative_path,
        original_sha256=original_sha,
        committed_sha256=original_sha,
        byte_count=byte_count,
    )


def _prepare_manifest_destination(repo_root: Path) -> None:
    """Gate the 008-b one-shot manifest replacement on exact identity.

    If the manifest destination does not exist, nothing is done (fresh
    export path).  If it exists, its complete bytes must equal the pinned
    Objective-008-a manifest identity (SHA-256 and byte count) to be
    removed through the anchored walk; any deviation is refused
    fail-closed and the pre-existing manifest is never touched.
    """
    manifest_relative = f"{EVIDENCE_SUBDIR}/manifest.json"
    try:
        raw = read_existing_evidence_destination_bounded(repo_root, manifest_relative)
    except UnsafeEvidenceError as exc:
        if exc.rejection_class == "destination_missing":
            return
        raise
    if (
        len(raw) != contracts.OBJECTIVE_008_A_MANIFEST_BYTE_COUNT
        or hashlib.sha256(raw).hexdigest() != contracts.OBJECTIVE_008_A_MANIFEST_SHA256
    ):
        raise UnsafeEvidenceError("destination_bytes_mismatch", manifest_relative)
    remove_verified_evidence_destination(repo_root, manifest_relative)


def _build_manifest(entries: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "schema": contracts.MANIFEST_SCHEMA,
        "classification": "post_hoc_durable_preservation",
        "preserved_during_objective_005": False,
        "authorities": list(entries),
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
    _prepare_manifest_destination(repo_root)
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
