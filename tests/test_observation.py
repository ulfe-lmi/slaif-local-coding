from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.config import ObservationPolicy
from slaif_local_coding.constitution import ObservationContext, observe_request
from slaif_local_coding.constitution.models import EvidenceType, IncompleteReason, TrustClass
from slaif_local_coding.constitution.references import extract_references

FIXTURES = Path(__file__).parent / "fixtures" / "codex" / "0.149.0"


def context() -> ObservationContext:
    return ObservationContext(
        endpoint="/v1/responses",
        route_id="vision",
        model="qwen",
        streaming=False,
        session="spoofable-hint",
        discriminator_trust=TrustClass.UNTRUSTED_CLIENT_HINT,
    )


@pytest.mark.parametrize(
    ("name", "evidence", "path"),
    [
        ("project_instructions_responses.json", EvidenceType.PROJECT_INSTRUCTIONS, "AGENTS.md"),
        ("input_file_responses.json", EvidenceType.INPUT_FILE, "services/api/AGENTS.md"),
        ("paired_tool_responses.json", EvidenceType.PAIRED_TOOL_RESULT, "services/api/AGENTS.md"),
    ],
)
def test_supported_captured_and_synthetic_shapes(
    name: str, evidence: EvidenceType, path: str
) -> None:
    payload = json.loads((FIXTURES / name).read_text())
    result = observe_request(payload, context(), ObservationPolicy())
    assert len(result.roots) == 1
    assert result.roots[0].logical_path == path
    assert result.roots[0].evidence[0].type is evidence


@pytest.mark.parametrize(
    "payload",
    [
        {"input": "AGENTS.md says things"},
        {"input": "example: '# AGENTS.md instructions for repo'"},
        {"tools": [{"description": "cat AGENTS.md"}]},
        {"input": [{"type": "function_call_output", "call_id": "x", "output": "rules"}]},
        {"input": [{"filename": "MY_AGENTS.md", "content": "rules"}]},
        {"input": [{"filename": "https://example.test/AGENTS.md", "content": "rules"}]},
        {"role": "assistant", "content": "I read AGENTS.md"},
    ],
)
def test_false_positives_are_not_roots(payload: dict[str, Any]) -> None:
    assert observe_request(payload, context(), ObservationPolicy()).roots == ()


@pytest.mark.parametrize("content", ["x\n", "x\r\n", "x \n", "ž\n"])
def test_exact_utf8_hash_and_length(content: str) -> None:
    payload = {"input": [{"filename": "AGENTS.md", "content": content}]}
    root = observe_request(payload, context(), ObservationPolicy()).roots[0]
    encoded = content.encode()
    assert root.byte_length == len(encoded)
    assert root.content_sha256 == hashlib.sha256(encoded).hexdigest()


def test_reference_kinds_normalization_duplicates_offsets_and_rejections() -> None:
    source = (
        "MUST read [law](./docs//LAW.md#binding).\n"
        "[ops]: .github/workflows/check.yml\n"
        'NEVER skip `docs/LAW.md` or "config/app.toml".\n'
        "REQUIRED before scripts/check.sh and Makefile.\n"
        "Reject https://example.test/x.md /etc/passwd.md C:\\secret.md ../up.md "
        "//server/share.md docs/a.md?q=1 bad%2Fname.md.\n"
    )
    result = extract_references(source, ObservationPolicy())
    assert [candidate.path for candidate in result.candidates] == [
        "docs/LAW.md",
        ".github/workflows/check.yml",
        "config/app.toml",
        "scripts/check.sh",
    ]
    law = result.candidates[0]
    assert len(law.evidence) == 3
    for evidence in law.evidence:
        encoded = source.encode()
        assert encoded[evidence.start_byte : evidence.end_byte].decode() in {
            "./docs//LAW.md#binding",
            "docs/LAW.md",
        }
    assert result.rejected >= 7
    assert result == extract_references(source, ObservationPolicy())


def test_multiple_roots_dedup_and_all_evidence_stable() -> None:
    item = {"filename": "AGENTS.md", "content": "MUST read SECURITY.md"}
    result = observe_request(
        {"input": [item, item, {**item, "content": "different"}]}, context(), ObservationPolicy()
    )
    assert len(result.roots) == 2
    assert len(result.roots[0].evidence) == 2
    assert (
        result.model_dump_json()
        == observe_request(
            {"input": [item, item, {**item, "content": "different"}]},
            context(),
            ObservationPolicy(),
        ).model_dump_json()
    )


def test_chat_tool_call_and_output_pairing() -> None:
    payload = {
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "tool_call",
                        "id": "chat_call",
                        "function": {
                            "name": "exec_command",
                            "arguments": '{"cmd":"cat nested/AGENTS.md"}',
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "chat_call", "content": "MUST read law.md"},
        ]
    }
    result = observe_request(payload, context(), ObservationPolicy())
    assert result.roots[0].logical_path == "nested/AGENTS.md"
    assert result.roots[0].evidence[0].type is EvidenceType.PAIRED_TOOL_RESULT


@pytest.mark.parametrize(
    ("policy", "payload", "reason"),
    [
        (
            ObservationPolicy(max_source_bytes=2),
            {"input": [{"filename": "AGENTS.md", "content": "abc"}]},
            IncompleteReason.SOURCE_TOO_LARGE,
        ),
        (
            ObservationPolicy(max_roots=1),
            {
                "input": [
                    {"filename": "AGENTS.md", "content": "a"},
                    {"filename": "x/AGENTS.md", "content": "b"},
                ]
            },
            IncompleteReason.TOO_MANY_ROOTS,
        ),
        (
            ObservationPolicy(max_candidates=1),
            {"input": [{"filename": "AGENTS.md", "content": "MUST read a.md and b.md"}]},
            IncompleteReason.TOO_MANY_CANDIDATES,
        ),
        (
            ObservationPolicy(max_total_evidence=1),
            {"input": [{"filename": "AGENTS.md", "content": "MUST read a.md and `a.md`"}]},
            IncompleteReason.EVIDENCE_BUDGET_EXCEEDED,
        ),
        (
            ObservationPolicy(max_path_bytes=4),
            {"input": [{"filename": "AGENTS.md", "content": "MUST read long.md"}]},
            IncompleteReason.PATH_TOO_LONG,
        ),
    ],
)
def test_every_limit_marks_manifest_incomplete(
    policy: ObservationPolicy, payload: dict[str, Any], reason: IncompleteReason
) -> None:
    result = observe_request(payload, context(), policy)
    assert not result.complete and reason in result.incomplete_reasons
