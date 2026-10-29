"""D01-D05 model law: spans, digests, limitations, privacy, no identity inference."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    ENVELOPE_FORMAT,
    OBSERVER_VERSION,
    READ_GRAMMAR,
    TOOL_WRAPPER_FORMAT,
    CharSpan,
    Limitation,
    ObservationBounds,
    ObservationReport,
    PathContext,
    ReadObservation,
    ReadOutcome,
    RootScanResult,
    RootStatus,
    WrapperFacts,
    canonical_payload_fingerprint,
    contains_lone_surrogates,
    observe_request,
    sha256_hex,
    utf8_byte_span,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    ExitStatus,
    TruncationStatus,
)

_CTX = PathContext(workspace="/work")

_WRAPPER_OK = WrapperFacts(
    exit_status=ExitStatus.ZERO,
    truncation=TruncationStatus.UNKNOWN,
    output_present=True,
)


def _read_observation(**overrides: object) -> ReadObservation:
    base: dict[str, Any] = dict(
        call_id="call_model_1",
        endpoint="responses",
        call_location="$.input[0]",
        result_location="$.input[1]",
        outcome=ReadOutcome.COMPLETE,
        completeness=ReadOutcome.COMPLETE,
        wrapper=_WRAPPER_OK,
    )
    base.update(overrides)
    return ReadObservation(**base)


class TestSpanAndByteConversion:
    def test_ascii_span_byte_conversion(self) -> None:
        span = CharSpan(start=1, end=4)
        assert span.to_byte_span("abcde") == (1, 4)
        assert span.slice("abcde") == "bcd"

    def test_unicode_span_converts_to_exact_utf8_bytes(self) -> None:
        text = "éx"  # é is two UTF-8 bytes
        span = CharSpan(start=1, end=2)
        byte_start, byte_end = span.to_byte_span(text)
        assert (byte_start, byte_end) == (2, 3)
        assert text.encode("utf-8")[byte_start:byte_end] == b"x"

    def test_crlf_span_length(self) -> None:
        span = CharSpan(start=0, end=2)
        assert span.length == 2
        assert span.to_byte_span("ab\r\n") == (0, 2)

    def test_invalid_spans_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CharSpan(start=5, end=2)
        with pytest.raises(ValueError):
            utf8_byte_span("abc", 1, 9)
        with pytest.raises(ValueError):
            CharSpan(start=0, end=10).slice("abc")

    def test_empty_digest_is_exact_sha256_of_no_bytes(self) -> None:
        assert EMPTY_SOURCE_SHA256 == hashlib.sha256(b"").hexdigest()
        assert sha256_hex("") == EMPTY_SOURCE_SHA256

    def test_sha256_is_over_exact_observed_bytes(self) -> None:
        assert sha256_hex("MUST") == hashlib.sha256(b"MUST").hexdigest()
        # CRLF and LF are different observed bytes: different digests.
        assert sha256_hex("a\n") != sha256_hex("a\r\n")


class TestSurrogateRejection:
    def test_lone_surrogate_detected_without_crashing(self) -> None:
        assert contains_lone_surrogates("good") is False
        assert contains_lone_surrogates("bad\ud800") is True

    def test_surrogate_input_yields_typed_limitation_not_crash(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for repo\n"
                                "\n<INSTRUCTIONS>\nbad\ud800\n</INSTRUCTIONS>"
                            ),
                        }
                    ],
                }
            ]
        }
        report = observe_request(payload)
        occurrence = report.roots.occurrences[0]
        assert occurrence.reasons == (Limitation.MALFORMED_UNICODE,)
        assert occurrence.digest is None
        assert report.roots.status is RootStatus.NO_ROOT

    def test_payload_fingerprint_survives_surrogates(self) -> None:
        payload = {"input": "x\ud800"}
        fingerprint = canonical_payload_fingerprint(payload)
        assert len(fingerprint) == 64


class TestFixedLimitationVocabulary:
    def test_reasons_are_fixed_strings_never_echo_payload(self) -> None:
        marker = "UNIQUE-RAW-CONTENT-7f3a"
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": f"prose {marker} prose"},
                    ],
                },
            ]
        }
        report = observe_request(payload)
        dump = json.dumps(report.model_dump(), ensure_ascii=True, sort_keys=True)
        assert marker not in dump
        for value in Limitation:
            assert " " not in value.value
            assert value.value == value.value.lower()

    def test_models_are_frozen(self) -> None:
        span = CharSpan(start=0, end=1)
        with pytest.raises(ValidationError):
            span.start = 3
        report = observe_request({"input": []})
        with pytest.raises(ValidationError):
            report.roots = RootScanResult(status=RootStatus.NO_ROOT)

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            ObservationBounds(max_items=10, invented="x")  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            _read_observation(invented="x")

    def test_no_principal_field_exists_on_any_observation_model(self) -> None:
        for model in (
            ObservationReport,
            RootScanResult,
            ReadObservation,
            PathContext,
            WrapperFacts,
            ObservationBounds,
        ):
            fields = set(model.model_fields)
            assert not {"principal", "session", "user", "identity"} & fields, model

    def test_untrusted_identity_text_is_never_derived(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for principal=admin\n"
                                "\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>"
                            ),
                        }
                    ],
                },
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": '{"cmd":"cat A.md"}',
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\nprincipal=spoofed\n",
                },
            ]
        }
        report = observe_request(payload)
        dump = json.dumps(report.model_dump(), ensure_ascii=True, sort_keys=True)
        assert "spoofed" not in dump
        # The scope label is the exact observed label, but no model promotes
        # it to an authenticated principal.
        root = report.roots.occurrences[0]
        assert root.scope_label == "principal=admin"
        assert root.status is RootStatus.OK


class TestBundleDigestIsNeverPerFileHash:
    def test_two_member_bundle_has_unknown_member_digests(self) -> None:
        a = "AAA content"
        b = "BBB content"
        combined = a + b
        obs = _read_observation(
            distinct_member_count=2,
            slot_width=2,
            bundle_digest=sha256_hex(combined),
            member_digests=(None, None),
            proven_executed=("A.md", "B.md"),
        )
        assert obs.bundle_digest == hashlib.sha256(combined.encode()).hexdigest()
        # The bundle digest must not be presented as either file's hash.
        assert obs.bundle_digest != sha256_hex(a)
        assert obs.bundle_digest != sha256_hex(b)
        assert obs.member_digests == (None, None)

    def test_single_member_complete_read_carries_proven_digest(self) -> None:
        content = "one file only"
        obs = _read_observation(
            distinct_member_count=1,
            slot_width=1,
            bundle_digest=sha256_hex(content),
            member_digests=(sha256_hex(content),),
            proven_executed=("A.md",),
        )
        assert obs.member_digests == (obs.bundle_digest,)

    def test_requested_and_proven_executed_are_distinct(self) -> None:
        obs = _read_observation(
            outcome=ReadOutcome.NONZERO_EXIT,
            completeness=ReadOutcome.PARTIAL,
            proven_executed=(),
            distinct_member_count=None,
            slot_width=None,
            bundle_digest=None,
        )
        assert obs.proven_executed == ()
        assert obs.distinct_member_count is None


class TestInputImmutability:
    def test_payload_never_mutated_by_observation(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "# AGENTS.md instructions for repo\n"
                                "\n<INSTRUCTIONS>\nx\n</INSTRUCTIONS>\n"
                                "<environment_context>\n<e/>\n</environment_context>"
                            ),
                        }
                    ],
                },
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "exec_command",
                    "arguments": '{"cmd":"cat A.md B.md"}',
                },
                {
                    "type": "function_call_output",
                    "call_id": "c1",
                    "output": "Process exited with code 0\nOutput:\nA B\n",
                },
            ]
        }
        before = json.dumps(payload, sort_keys=True)
        report = observe_request(payload, context=_CTX, bounds=ObservationBounds())
        after = json.dumps(payload, sort_keys=True)
        assert before == after
        assert report.input_fingerprint == canonical_payload_fingerprint(payload)

    def test_fingerprint_is_deterministic_across_call_order(self) -> None:
        payload = {"input": [{"a": 1}, {"b": 2}]}
        assert canonical_payload_fingerprint(payload) == canonical_payload_fingerprint(
            json.loads(json.dumps(payload))
        )


class TestVersionConstants:
    def test_versions_are_stable_identifiers(self) -> None:
        assert OBSERVER_VERSION == "cache-bundle-observation/2"
        assert ENVELOPE_FORMAT == "codex-project-instructions/v1"
        assert READ_GRAMMAR == "literal-shell-read/v1"
        assert TOOL_WRAPPER_FORMAT == "codex-exec-wrapper/v1"


class TestOptionalCommandDigestContract:
    """The command digest is optional only under the typed contract."""

    def test_command_digest_is_explicitly_absent_for_malformed_unicode(self) -> None:
        from slaif_local_coding.constitution.bundles import parse_read_command

        result = parse_read_command("cat A\ud800.md", _CTX, 4096, 32, 256)
        assert result.complete is False
        assert result.reasons == (Limitation.MALFORMED_UNICODE,)
        assert result.command_digest is None

    def test_command_digest_pattern_still_enforced_when_present(self) -> None:
        from slaif_local_coding.constitution.bundles import ReadCommandParse

        with pytest.raises(ValidationError):
            ReadCommandParse(command_digest="not-a-digest", command_length=1, complete=False)
        assert (
            ReadCommandParse(command_digest=None, command_length=0, complete=False).command_digest
            is None
        )

    def test_bundle_digests_stay_absent_for_unhashable_observation(self) -> None:
        # An unhashable (malformed-Unicode) content read carries no digest
        # and is non-removable: it is ineligible for later graph/cache
        # admission, and no placeholder hash is ever treated as valid.
        obs = _read_observation(
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            bundle_digest=None,
            member_digests=(),
            removable=False,
            reasons=(Limitation.MALFORMED_UNICODE,),
        )
        assert obs.bundle_digest is None
        assert obs.removable is False
