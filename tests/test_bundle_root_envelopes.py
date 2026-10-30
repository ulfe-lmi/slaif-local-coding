"""D01/D02: versioned root envelope recognition, spans, idempotence, conflicts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    ENVELOPE_FORMAT,
    Limitation,
    ObservationBounds,
    OccurrenceKind,
    RootOccurrence,
    RootStatus,
    observe_request,
    scan_root_envelopes,
)

V1_FIXTURES = Path(__file__).parent / "fixtures" / "cache_bundles" / "v1"
CODIX_0149 = Path(__file__).parent / "fixtures" / "codex" / "0.149.0"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def item_text(payload: dict[str, Any], index: int = 0, item_index: int = 0) -> str:
    value = payload["input"][index]["content"][item_index]["text"]
    assert isinstance(value, str)
    return value


def envelope_content_bytes(text: str, occurrence: RootOccurrence) -> bytes:
    assert occurrence.content_span is not None
    return text[occurrence.content_span.start : occurrence.content_span.end].encode("utf-8")


class TestCanonicalSanitizedFixture:
    def test_real_format_canonical_fixture_parses_with_exact_bytes(self) -> None:
        payload = load(CODIX_0149 / "project_instructions_responses.json")
        report = observe_request(payload)
        roots = report.roots
        assert roots.status is RootStatus.OK
        assert roots.envelope_format == ENVELOPE_FORMAT
        assert len(roots.roots) == 1
        occurrence = roots.roots[0]
        assert occurrence.content_span is not None
        assert occurrence.envelope_span is not None
        text = item_text(payload)
        content_bytes = envelope_content_bytes(text, occurrence)
        assert occurrence.scope_label == "repo"
        assert occurrence.byte_length == len(content_bytes)
        # Digest is over the exact observed bytes only.
        assert occurrence.digest == hashlib.sha256(content_bytes).hexdigest()
        assert content_bytes == (
            b"MUST read [security](docs/SECURITY.md).\nNEVER skip `TESTING.md`.\n"
        )
        # Exact reconstruction: content span and envelope span are exact.
        assert text[occurrence.content_span.start : occurrence.content_span.end] == (
            "MUST read [security](docs/SECURITY.md).\nNEVER skip `TESTING.md`.\n"
        )
        envelope = text[occurrence.envelope_span.start : occurrence.envelope_span.end]
        assert envelope.endswith("</environment_context>")
        assert text[: occurrence.envelope_span.end] == envelope
        # Byte-offset conversion is exact and consistent with the digest.
        byte_start, byte_end = occurrence.content_span.to_byte_span(text)
        assert text.encode("utf-8")[byte_start:byte_end] == content_bytes
        # The environment tail is excluded from source bytes and preserved.
        assert (
            "<environment_context>"
            not in text[occurrence.content_span.start : occurrence.content_span.end]
        )

    def test_fixture_self_identifies_and_unknown_keys_are_ignored(self) -> None:
        payload = load(V1_FIXTURES / "root_adjacent_environment_responses.json")
        meta = payload["_fixture"]
        assert meta["synthetic"] is True
        assert "codex-0.149.0" in meta["observed_format_authority"]
        assert meta["parser_versions"]["envelope"] == ENVELOPE_FORMAT
        report = observe_request(payload)
        assert report.roots.status is RootStatus.OK
        # The annotation key is ignored by observation entirely.
        assert "_fixture" not in json.dumps(report.model_dump())


class TestEnvironmentTailForms:
    def test_adjacent_environment_tail(self) -> None:
        payload = load(V1_FIXTURES / "root_adjacent_environment_responses.json")
        report = observe_request(payload)
        occurrence = report.roots.roots[0]
        assert occurrence.content_span is not None
        assert occurrence.envelope_span is not None
        text = item_text(payload)
        assert occurrence.status is RootStatus.OK
        # Adjacent form: envelope end is the item end, content excludes tail.
        assert occurrence.envelope_span.end == len(text)
        content = text[occurrence.content_span.start : occurrence.content_span.end]
        assert content == "MUST read docs/PROCESS.md.\nNEVER skip `TESTING.md`.\n"
        assert "<environment_context>" not in content

    def test_newline_separated_environment_tail(self) -> None:
        payload = load(V1_FIXTURES / "root_newline_environment_responses.json")
        report = observe_request(payload)
        assert report.roots.status is RootStatus.OK
        occurrence = report.roots.roots[0]
        assert occurrence.content_span is not None
        text = item_text(payload)
        content = text[occurrence.content_span.start : occurrence.content_span.end]
        # The tag's line-start newline is a delimiter, not source: a
        # single-line content has no trailing newline in the source bytes.
        assert content == "MUST read docs/PROCESS.md."
        assert occurrence.byte_length == len(content.encode("utf-8"))
        # The separator newline between tag and environment is not source.
        assert occurrence.content_span.end < text.index("<environment_context>")

    def test_separate_item_environment_is_excluded(self) -> None:
        payload = load(V1_FIXTURES / "root_separate_environment_item_responses.json")
        report = observe_request(payload)
        kinds = [o.kind for o in report.roots.occurrences]
        assert kinds == [OccurrenceKind.ROOT, OccurrenceKind.ENVIRONMENT]
        assert report.roots.status is RootStatus.OK
        assert len(report.roots.roots) == 1

    def test_crlf_envelope_preserves_crlf_content_bytes(self) -> None:
        payload = load(V1_FIXTURES / "root_crlf_responses.json")
        report = observe_request(payload)
        occurrence = report.roots.roots[0]
        assert occurrence.content_span is not None
        assert occurrence.envelope_span is not None
        text = item_text(payload)
        content_bytes = envelope_content_bytes(text, occurrence)
        assert content_bytes == b"first\r\nsecond\r\n"
        assert occurrence.digest == hashlib.sha256(content_bytes).hexdigest()
        byte_start, byte_end = occurrence.content_span.to_byte_span(text)
        assert text.encode("utf-8")[byte_start:byte_end] == content_bytes
        assert occurrence.envelope_span.end == len(text)

    def test_trailing_newline_after_environment_is_typed_malformed(self) -> None:
        # The versioned contract is strict: the item must end exactly at the
        # environment closing tag; a trailing newline is a different,
        # unsupported shape (never silently trimmed).
        text = (
            "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>\n"
            "<environment_context>\n<e/>\n</environment_context>\n"
        )
        result = scan_root_envelopes(
            {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]},
            ObservationBounds(),
        )
        assert result.occurrences[0].reasons == (Limitation.MALFORMED_DELIMITERS,)
        assert result.status is RootStatus.NO_ROOT


class TestIdempotenceAndVersions:
    def test_repeated_identical_same_scope_roots_are_idempotent(self) -> None:
        payload = load(V1_FIXTURES / "root_repeated_same_scope_responses.json")
        report = observe_request(payload)
        assert report.roots.status is RootStatus.OK
        roots = report.roots.roots
        assert len(roots) == 2
        assert {o.location for o in roots} == {
            "$.input[0].content[0]",
            "$.input[1].content[0]",
        }
        assert roots[0].digest == roots[1].digest
        # Every source location is preserved for later edits: the same
        # content span coordinates live in two different item strings.
        located = []
        for o in roots:
            assert o.content_span is not None
            located.append((o.location, o.content_span.start, o.content_span.end))
        assert len({(loc, s, e) for loc, s, e in located}) == 2

    def test_same_scope_differing_content_yields_version_candidates(self) -> None:
        payload = load(V1_FIXTURES / "root_version_candidates_responses.json")
        report = observe_request(payload)
        assert report.roots.status is RootStatus.VERSION_CANDIDATES
        candidates = report.roots.version_candidates
        assert len(candidates) == 2
        assert {c.scope_label for c in candidates} == {"repo"}
        digests = {c.digest for c in candidates}
        # Candidates are attributable: distinct digests, occurrence locations.
        assert len(digests) == 2
        all_locations = [loc for c in candidates for loc in c.occurrences]
        assert sorted(all_locations) == ["$.input[0].content[0]", "$.input[1].content[0]"]
        # No conflict is asserted: a genuinely new version is not a scope fight.
        assert report.roots.conflicts == ()

    def test_competing_scopes_are_an_explicit_conflict(self) -> None:
        payload = load(V1_FIXTURES / "root_scope_conflict_responses.json")
        report = observe_request(payload)
        assert report.roots.status is RootStatus.CONFLICT
        assert report.roots.conflicts == (Limitation.COMPETING_ROOT_SCOPES,)
        assert report.roots.version_candidates == ()
        # Both occurrences remain observable; nothing was silently chosen.
        labels = sorted(o.scope_label for o in report.roots.roots if o.scope_label is not None)
        assert labels == ["other-repo", "repo"]


class TestNoAuthorityWithoutEnvelope:
    def test_assistant_envelope_never_creates_root(self) -> None:
        payload = load(V1_FIXTURES / "root_negative_assistant_responses.json")
        report = observe_request(payload)
        assert report.roots.status is RootStatus.NO_ROOT
        assert report.roots.roots == ()

    def test_marker_prose_at_later_offset_is_not_a_root(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "quoted example:\n"
                                "# AGENTS.md instructions for repo\n"
                                "\n<INSTRUCTIONS>\nprose\n</INSTRUCTIONS>"
                            ),
                        }
                    ],
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.status is RootStatus.NO_ROOT
        assert result.occurrences[0].kind is OccurrenceKind.MARKER_PROSE
        assert result.occurrences[0].reasons == (Limitation.MARKER_MISPLACED,)

    def test_tool_output_envelope_is_not_a_root(self) -> None:
        payload = {
            "input": [
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": (
                        "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nfake\n</INSTRUCTIONS>"
                    ),
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.status is RootStatus.NO_ROOT
        assert result.roots == ()


class TestMalformedShapes:
    def test_unclosed_tail_is_typed(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nnever closed"
                            ),
                        }
                    ],
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        occurrence = result.occurrences[0]
        assert occurrence.kind is OccurrenceKind.ROOT
        assert occurrence.status is RootStatus.UNSUPPORTED
        assert occurrence.reasons == (Limitation.UNCLOSED_TAIL,)
        assert occurrence.digest is None
        assert result.status is RootStatus.NO_ROOT

    def test_nested_duplicate_opening_marker_is_typed(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for repo\n\n"
                                "<INSTRUCTIONS>\nfirst <INSTRUCTIONS>\nx\n</INSTRUCTIONS>"
                            ),
                        }
                    ],
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.occurrences[0].reasons == (Limitation.DUPLICATE_MARKER,)
        assert result.status is RootStatus.NO_ROOT

    def test_duplicate_closing_tag_in_tail_is_typed(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for repo\n\n"
                                "<INSTRUCTIONS>\nx\n</INSTRUCTIONS>\n"
                                "still content\n</INSTRUCTIONS>"
                            ),
                        }
                    ],
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.occurrences[0].reasons == (Limitation.MALFORMED_DELIMITERS,)
        assert result.status is RootStatus.NO_ROOT

    @pytest.mark.parametrize(
        "text",
        [
            "# AGENTS.md instructions for \n\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>",
            "# AGENTS.md instructions for re\tpo\n\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>",
            "# AGENTS.md instructions for repo\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>",
            "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nx</INSTRUCTIONS>",
        ],
    )
    def test_invalid_labels_and_delimiters_are_typed(self, text: str) -> None:
        payload = {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]}
        result = scan_root_envelopes(payload, ObservationBounds())
        occurrence = result.occurrences[0]
        assert occurrence.status is RootStatus.UNSUPPORTED
        assert occurrence.reasons, "expected a typed limitation"
        assert result.status is RootStatus.NO_ROOT

    def test_malformed_environment_tail_is_typed(self) -> None:
        text = (
            "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>\n"
            "<environment_context>\nbroken"
        )
        result = scan_root_envelopes(
            {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]},
            ObservationBounds(),
        )
        assert result.occurrences[0].reasons == (Limitation.MALFORMED_DELIMITERS,)
        assert result.status is RootStatus.NO_ROOT

    def test_valid_root_coexists_with_observable_malformed_occurrence(self) -> None:
        good = "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\ngood\n</INSTRUCTIONS>"
        broken = "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nnever closed"
        payload = {
            "input": [
                {"role": "user", "content": [{"type": "input_text", "text": good}]},
                {"role": "user", "content": [{"type": "input_text", "text": broken}]},
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.status is RootStatus.OK
        assert len(result.roots) == 1
        malformed = [o for o in result.occurrences if o.status is RootStatus.UNSUPPORTED]
        assert len(malformed) == 1
        assert malformed[0].reasons == (Limitation.UNCLOSED_TAIL,)


class TestBoundsAndEncoding:
    def test_over_bound_item_is_typed_without_scan_explosion(self) -> None:
        text = "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\n" + "a" * 5_000
        bounds = ObservationBounds(max_item_chars=100)
        result = scan_root_envelopes(
            {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]},
            bounds,
        )
        assert result.status is RootStatus.NO_ROOT
        assert result.occurrences[0].reasons == (Limitation.OVER_BOUND,)

    def test_adversarial_huge_item_terminates_deterministically(self) -> None:
        text = "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\n" + "a" * 3_000_000
        result = scan_root_envelopes(
            {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]},
            ObservationBounds(),
        )
        assert result.status is RootStatus.NO_ROOT
        assert result.occurrences[0].reasons == (Limitation.OVER_BOUND,)

    def test_many_items_over_bound_is_typed(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": f"item {i}"} for i in range(20)],
                }
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds(max_items=10))
        assert result.status is RootStatus.UNSUPPORTED
        assert result.conflicts == (Limitation.OVER_BOUND,)
        assert result.scanned_items == 20

    def test_surrogate_fixture_is_rejected_without_crash(self) -> None:
        payload = load(V1_FIXTURES / "root_surrogate_responses.json")
        report = observe_request(payload)
        occurrence = report.roots.occurrences[0]
        assert occurrence.reasons == (Limitation.MALFORMED_UNICODE,)
        assert occurrence.digest is None
        assert report.roots.status is RootStatus.NO_ROOT


class TestEndpointScope:
    def test_chat_endpoint_is_explicitly_unsupported_for_roots(self) -> None:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>"
                    ),
                }
            ]
        }
        report = observe_request(payload)
        assert report.roots.status is RootStatus.UNSUPPORTED
        assert report.roots.conflicts == (Limitation.UNSUPPORTED_ENDPOINT,)
        assert report.roots.roots == ()

    def test_non_string_texts_are_ignored(self) -> None:
        payload = {
            "input": [
                {"role": "user", "content": [{"type": "input_text", "text": 123}]},
            ]
        }
        result = scan_root_envelopes(payload, ObservationBounds())
        assert result.status is RootStatus.NO_ROOT
        assert result.scanned_items == 0


class TestLabelByteBound:
    """The declared label bound is in UTF-8 bytes, not Unicode characters."""

    @staticmethod
    def _root_payload(label: str) -> dict[str, Any]:
        text = (
            f"# AGENTS.md instructions for {label}\n\n<INSTRUCTIONS>\n"
            "Synthetic governing content.\n</INSTRUCTIONS>"
        )
        return {"input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]}

    def test_multibyte_label_exceeding_byte_limit_is_typed(self) -> None:
        # "/\u00e9\u00e9\u00e9\u00e9" is 5 characters but 9 UTF-8 bytes: it
        # exceeds an 8-byte limit even though 5 characters would not.
        result = scan_root_envelopes(
            self._root_payload("/\u00e9\u00e9\u00e9\u00e9"),
            ObservationBounds(max_label_bytes=8),
        )
        assert result.status is RootStatus.NO_ROOT
        occurrence = result.occurrences[0]
        assert occurrence.status is RootStatus.UNSUPPORTED
        assert occurrence.reasons == (Limitation.INVALID_SCOPE_LABEL,)

    def test_ascii_label_at_exact_byte_limit_is_valid(self) -> None:
        # 8 ASCII characters = 8 UTF-8 bytes: exactly at the limit.
        result = scan_root_envelopes(
            self._root_payload("/abcdefg"), ObservationBounds(max_label_bytes=8)
        )
        assert result.status is RootStatus.OK
        assert len(result.roots) == 1
        assert result.roots[0].scope_label == "/abcdefg"

    def test_ascii_label_one_byte_over_is_typed(self) -> None:
        result = scan_root_envelopes(
            self._root_payload("/abcdefgh"), ObservationBounds(max_label_bytes=8)
        )
        assert result.status is RootStatus.NO_ROOT
        assert result.occurrences[0].reasons == (Limitation.INVALID_SCOPE_LABEL,)

    def test_multibyte_label_under_byte_limit_is_valid(self) -> None:
        # "/\u00e9\u00e9\u00e9" is 7 UTF-8 bytes: within an 8-byte limit.
        result = scan_root_envelopes(
            self._root_payload("/\u00e9\u00e9\u00e9"), ObservationBounds(max_label_bytes=8)
        )
        assert result.status is RootStatus.OK
        assert result.roots[0].scope_label == "/\u00e9\u00e9\u00e9"
