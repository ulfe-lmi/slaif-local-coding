from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import ObservationPolicy
from slaif_local_coding.constitution import ObservationContext, observe_request
from slaif_local_coding.constitution.models import (
    CandidateReference,
    EvidenceType,
    IncompleteReason,
    RejectionReason,
    TrustClass,
)
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
    payload = {"input": [{"type": "input_file", "filename": "AGENTS.md", "content": content}]}
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
        "Makefile",
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
    item = {"type": "input_file", "filename": "AGENTS.md", "content": "MUST read SECURITY.md"}
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
                        "type": "function",
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
            {"input": [{"type": "input_file", "filename": "AGENTS.md", "content": "abc"}]},
            IncompleteReason.SOURCE_TOO_LARGE,
        ),
        (
            ObservationPolicy(max_roots=1),
            {
                "input": [
                    {"type": "input_file", "filename": "AGENTS.md", "content": "a"},
                    {"type": "input_file", "filename": "x/AGENTS.md", "content": "b"},
                ]
            },
            IncompleteReason.TOO_MANY_ROOTS,
        ),
        (
            ObservationPolicy(max_candidates=1),
            {
                "input": [
                    {
                        "type": "input_file",
                        "filename": "AGENTS.md",
                        "content": "MUST read a.md and b.md",
                    }
                ]
            },
            IncompleteReason.TOO_MANY_CANDIDATES,
        ),
        (
            ObservationPolicy(max_total_evidence=1),
            {
                "input": [
                    {
                        "type": "input_file",
                        "filename": "AGENTS.md",
                        "content": "MUST read a.md and `a.md`",
                    }
                ]
            },
            IncompleteReason.EVIDENCE_BUDGET_EXCEEDED,
        ),
        (
            ObservationPolicy(max_path_bytes=10),
            {
                "input": [
                    {
                        "type": "input_file",
                        "filename": "AGENTS.md",
                        "content": "MUST read very-long.md",
                    }
                ]
            },
            IncompleteReason.PATH_TOO_LONG,
        ),
    ],
)
def test_every_limit_marks_manifest_incomplete(
    policy: ObservationPolicy, payload: dict[str, Any], reason: IncompleteReason
) -> None:
    result = observe_request(payload, context(), policy)
    assert not result.complete and reason in result.incomplete_reasons


def project_item(role: str = "developer", directory: str = "repo") -> dict[str, Any]:
    return {
        "role": role,
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# AGENTS.md instructions for {directory}\n\n"
                    "<INSTRUCTIONS>\nMUST read SECURITY.md.\n</INSTRUCTIONS>"
                ),
            }
        ],
    }


@pytest.mark.parametrize("role", ["assistant", "tool", "user"])
def test_project_envelope_requires_developer_role(role: str) -> None:
    assert (
        observe_request({"input": [project_item(role)]}, context(), ObservationPolicy()).roots == ()
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"metadata": project_item()},
        {
            "input": [
                {
                    "role": "developer",
                    "content": [
                        {"type": "output_text", "text": project_item()["content"][0]["text"]}
                    ],
                }
            ]
        },
        {
            "input": [
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "filename": "AGENTS.md", "text": "rules"}],
                }
            ]
        },
        {"input": [{"type": "input_text", "filename": "AGENTS.md", "content": "rules"}]},
        {"input": [{"filename": "AGENTS.md", "content": "rules"}]},
        {"input": [{"type": "input_file", "filename": "AGENTS.md", "file_id": "remote"}]},
        {
            "input": [
                {
                    "role": "assistant",
                    "content": [
                        {"type": "input_file", "filename": "AGENTS.md", "content": "rules"}
                    ],
                }
            ]
        },
        {"messages": [project_item()]},
    ],
)
def test_unsupported_parent_and_item_shapes_do_not_detect(payload: dict[str, Any]) -> None:
    assert observe_request(payload, context(), ObservationPolicy()).roots == ()


@pytest.mark.parametrize(
    "label",
    [
        "../AGENTS.md",
        "../outside/AGENTS.md",
        "/private/AGENTS.md",
        "C:\\private\\AGENTS.md",
        "\\\\server\\share\\AGENTS.md",
        "https://example/AGENTS.md",
        "bad%2FAGENTS.md",
        "AGENTS.md?q=1",
        "AGENTS.md#fragment",
        "MY_AGENTS.md",
        "agents.md",
        "folder/",
        "a" * 2000 + "/AGENTS.md",
    ],
)
def test_input_file_rejects_every_unsafe_logical_root(label: str) -> None:
    payload = {"input": [{"type": "input_file", "filename": label, "content": "rules"}]}
    assert observe_request(payload, context(), ObservationPolicy()).roots == ()


@pytest.mark.parametrize(
    "directory", ["../outside", "C:\\private", "https://example", "bad%2Fpath"]
)
def test_project_directory_rejects_unsafe_labels(directory: str) -> None:
    assert (
        observe_request(
            {"input": [project_item(directory=directory)]}, context(), ObservationPolicy()
        ).roots
        == ()
    )


def test_safe_nested_root_normalizes_separators_and_absolute_project_is_private() -> None:
    file_result = observe_request(
        {
            "input": [
                {"type": "input_file", "filename": "./services//api/AGENTS.md", "content": "rules"}
            ]
        },
        context(),
        ObservationPolicy(),
    )
    assert file_result.roots[0].logical_path == "services/api/AGENTS.md"
    project_result = observe_request(
        {"input": [project_item(directory="/synthetic/private")]}, context(), ObservationPolicy()
    )
    assert project_result.roots[0].logical_path == "AGENTS.md"


def tool_pair(
    name: str = "exec_command", command: str = "cat AGENTS.md", call_id: str = "c"
) -> dict[str, Any]:
    return {
        "input": [
            {
                "type": "function_call",
                "call_id": call_id,
                "name": name,
                "arguments": json.dumps({"cmd": command}),
            },
            {"type": "function_call_output", "call_id": call_id, "output": "rules"},
        ]
    }


@pytest.mark.parametrize(
    "payload",
    [
        tool_pair(name="delete_all"),
        tool_pair(name="write_file"),
        tool_pair(name="unknown"),
        tool_pair(command="cat AGENTS.md; echo bad"),
        tool_pair(command="cat ../AGENTS.md"),
        {
            "input": [
                {"type": "function_call", "call_id": "c", "name": "exec_command", "arguments": "{"},
                {"type": "function_call_output", "call_id": "c", "output": "rules"},
            ]
        },
        {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "a",
                    "name": "exec_command",
                    "arguments": '{"cmd":"cat AGENTS.md"}',
                },
                {"type": "function_call_output", "call_id": "b", "output": "rules"},
            ]
        },
        {"input": tool_pair()["input"] + [tool_pair()["input"][0]]},
        {
            "input": tool_pair()["input"]
            + [{"type": "function_call", "call_id": "c", "name": "delete_all", "arguments": "{}"}]
        },
        {"input": tool_pair()["input"] + [tool_pair()["input"][1]]},
        {"tools": [{"name": "exec_command", "arguments": {"cmd": "cat AGENTS.md"}}]},
    ],
)
def test_tool_pairing_rejects_wrong_ambiguous_or_unsupported_shapes(
    payload: dict[str, Any],
) -> None:
    assert observe_request(payload, context(), ObservationPolicy()).roots == ()


def test_sentence_final_bare_paths_have_exact_utf8_spans() -> None:
    source = "ž MUST read SECURITY.md.\nREQUIRED before Makefile."
    result = extract_references(source, ObservationPolicy())
    assert [item.path for item in result.candidates] == ["SECURITY.md", "Makefile"]
    encoded = source.encode()
    assert [
        encoded[item.evidence[0].start_byte : item.evidence[0].end_byte].decode()
        for item in result.candidates
    ] == ["SECURITY.md", "Makefile"]


def test_evidence_boundaries_and_non_empty_invariant() -> None:
    source = "MUST read `a.md` and a.md and a.md and b.md"
    per_candidate = extract_references(source, ObservationPolicy(max_evidence_per_candidate=2))
    assert len(per_candidate.candidates[0].evidence) == 2
    assert IncompleteReason.EVIDENCE_BUDGET_EXCEEDED in per_candidate.reasons
    total = extract_references(source, ObservationPolicy(max_total_evidence=1))
    assert len(total.candidates) == 1 and len(total.candidates[0].evidence) == 1
    with pytest.raises(ValidationError):
        CandidateReference(path="x.md", first_seen=0, evidence=())


@pytest.mark.parametrize(
    ("source", "reason"),
    [
        ("[x](https://example/x.md)", RejectionReason.UNSAFE_LOCATION),
        ("[x]: /private/x.md", RejectionReason.UNSAFE_LOCATION),
        ("`C:\\private\\x.md`", RejectionReason.UNSAFE_LOCATION),
        ('"\\\\server\\share\\x.md"', RejectionReason.UNSAFE_LOCATION),
        ("`../x.md`", RejectionReason.TRAVERSAL),
        ("`bad%2Fx.md`", RejectionReason.AMBIGUOUS),
        ("`x.md?q=1`", RejectionReason.AMBIGUOUS),
        ("`folder/`", RejectionReason.AMBIGUOUS),
        ("`MY_AGENTS`", RejectionReason.UNSUPPORTED_FILE),
        ("`bad\x00name.md`", RejectionReason.AMBIGUOUS),
        (f"`{'a' * 2000}.md`", RejectionReason.PATH_TOO_LONG),
    ],
)
def test_each_structured_invalid_candidate_has_exact_fixed_reason(
    source: str, reason: RejectionReason
) -> None:
    result = extract_references(source, ObservationPolicy())
    assert result.candidates == () and result.rejected == 1
    assert [(item.reason, item.count) for item in result.rejection_counts] == [(reason, 1)]
