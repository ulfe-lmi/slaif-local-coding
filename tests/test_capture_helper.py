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
    assert set(minimized) == {"model", "instructions", "input", "sanitized_provenance"}
    assert minimized["model"] == capture.MODEL
    assert "disposable/random" not in str(minimized)
    assert "unrelated sensitive" not in str(minimized)
    assert "discarded request" not in str(minimized)
    assert minimized["sanitized_provenance"]["marker_occurrences"] == 2
    assert minimized["sanitized_provenance"]["occurrences_agree"] is True


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "relocated", "mismatch"])
def test_minimizer_rejects_unproved_pair(mutation: str) -> None:
    payload = raw_like()
    if mutation == "missing":
        payload["instructions"] = "ordinary instructions"
    elif mutation == "duplicate":
        payload["instructions"] += "\n" + ENVELOPE
    elif mutation == "relocated":
        payload["metadata"]["marker"] = ENVELOPE
    else:
        payload["instructions"] = payload["instructions"].replace("NEVER", "MUST NOT")
    with pytest.raises(RuntimeError):
        capture.minimize(payload)
