from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

HELPER = Path(__file__).parent / "helpers" / "capture_codex_project_envelope.py"
SPEC = importlib.util.spec_from_file_location("capture_codex_project_envelope", HELPER)
assert SPEC is not None and SPEC.loader is not None
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)

CONTENT = "MUST read [security](docs/SECURITY.md).\nNEVER skip `TESTING.md`."
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
    assert set(minimized) == {"model", "input", "sanitized_provenance"}
    assert minimized["model"] == capture.MODEL
    assert "disposable/random" not in str(minimized)
    assert "unrelated sensitive" not in str(minimized)
    assert "discarded request" not in str(minimized)
    assert minimized["sanitized_provenance"]["marker_occurrences"] == 1


def test_optional_instructions_does_not_change_canonical_fixture() -> None:
    paired = raw_like()
    user_only = raw_like()
    user_only["instructions"] = "ordinary instructions"
    paired_fixture, paired_facts = capture.minimize_with_facts(paired)
    user_fixture, user_facts = capture.minimize_with_facts(user_only)
    assert paired_fixture == user_fixture
    assert paired_facts["instructions_corroborated"] is True
    assert user_facts["instructions_corroborated"] is False


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
