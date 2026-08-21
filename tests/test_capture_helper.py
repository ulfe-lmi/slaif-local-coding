from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

HELPER = Path(__file__).parent / "helpers" / "capture_codex_project_envelope.py"
FIXTURES = Path(__file__).parent / "fixtures" / "codex" / "0.149.0"
SPEC = importlib.util.spec_from_file_location("capture_codex_project_envelope", HELPER)
assert SPEC is not None and SPEC.loader is not None
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)

CONTENT = "MUST read [security](docs/SECURITY.md).\nNEVER skip `TESTING.md`.\n"
ENVELOPE = (
    "# AGENTS.md instructions for /disposable/random/repository\n\n"
    f"<INSTRUCTIONS>\n{CONTENT}\n</INSTRUCTIONS>"
)


def raw_like() -> dict[str, Any]:
    return {
        "model": "ignored-real-slug",
        "instructions": ENVELOPE,
        "tools": [{"description": "unrelated sensitive material"}],
        "metadata": {"session": "discard-me"},
        "input": [
            {"role": "developer", "content": [{"type": "input_text", "text": "discard"}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": ENVELOPE
                        + "\n<environment_context>\n<discarded />\n</environment_context>",
                    },
                    {"type": "input_text", "text": "discarded request"},
                ],
            },
        ],
    }


def test_minimizer_emits_only_synthetic_paired_structure() -> None:
    minimized = capture.minimize(raw_like())
    assert set(minimized) == {"model", "input"}
    assert minimized["model"] == capture.MODEL
    assert "disposable/random" not in str(minimized)
    assert "unrelated sensitive" not in str(minimized)
    assert "discarded request" not in str(minimized)
    assert "provenance" not in str(minimized).lower()


def test_request_fixture_is_exactly_provider_payload_and_provenance_is_separate() -> None:
    request = json.loads((FIXTURES / "project_instructions_responses.json").read_text())
    provenance = json.loads((FIXTURES / "project_instructions_provenance.json").read_text())
    assert set(request) == {"model", "input"}
    assert not ({"auth", "id", "tools", "metadata", "provenance", "instructions"} & request.keys())
    assert set(provenance) == {
        "marker_occurrences",
        "logical_label",
        "content_byte_length",
        "content_sha256",
        "synthetic_only",
    }
    assert provenance["synthetic_only"] is True
    assert capture.minimize(raw_like()) == request


def test_optional_instructions_does_not_change_canonical_fixture() -> None:
    paired = raw_like()
    user_only = raw_like()
    user_only["instructions"] = "ordinary instructions"
    paired_fixture, paired_facts = capture.minimize_with_facts(paired)
    user_fixture, user_facts = capture.minimize_with_facts(user_only)
    assert paired_fixture == user_fixture
    assert paired_facts["instructions_corroborated"] is True
    assert user_facts["instructions_corroborated"] is False


@pytest.mark.parametrize(("input_index", "content_index"), [(0, 0), (1, 0), (1, 2)])
def test_actual_location_is_distinct_from_canonical_fixture(
    input_index: int, content_index: int
) -> None:
    payload = raw_like()
    marker = payload["input"][1]["content"][0]
    parents = [
        {"role": "developer", "content": [{"type": "input_text", "text": "x"}]}
        for _ in range(input_index)
    ]
    content = [{"type": "input_text", "text": "x"} for _ in range(content_index)] + [marker]
    parents.append({"role": "user", "content": content})
    payload["input"] = parents

    fixture, facts = capture.minimize_with_facts(payload)

    assert fixture == capture.minimize(raw_like())
    assert facts["actual_user_marker_location"] == (
        f"$.input[{input_index}].content[{content_index}].text"
    )
    assert facts["canonical_user_marker_location"] == "$.input[0].content[0].text"
    assert facts["marker_occurrences"] == 1
    assert len(facts["canonical_request_sha256"]) == 64


@pytest.mark.parametrize("label", ["../outside", "https://example.test", "C:\\private"])
def test_minimizer_rejects_unsafe_label(label: str) -> None:
    payload = raw_like()
    payload["instructions"] = payload["instructions"].replace(
        "/disposable/random/repository", label
    )
    payload["input"][1]["content"][0]["text"] = payload["input"][1]["content"][0]["text"].replace(
        "/disposable/random/repository", label
    )
    with pytest.raises(RuntimeError, match="privacy-safe"):
        capture.minimize(payload)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "relocated", "mismatch"])
def test_minimizer_rejects_unproved_pair(mutation: str) -> None:
    payload = raw_like()
    if mutation == "missing":
        payload["input"][1]["content"][0]["text"] = "ordinary instructions"
    elif mutation == "duplicate":
        payload["instructions"] += "\n" + ENVELOPE
    elif mutation == "relocated":
        payload["metadata"]["marker"] = ENVELOPE
    else:
        payload["instructions"] = payload["instructions"].replace("NEVER", "MUST NOT")
    with pytest.raises(RuntimeError):
        capture.minimize(payload)
