"""022-b pure source replacement: carrier lookup and exact span law.

Saved chunk 1a (read-only carrier layer): the accepted 017 root
coordinates join to the ACTUAL decoded request.  The closed
Responses root location maps to the existing
``input[i].content[j].text`` carrier with its earned user/input_text
shape verified, and the EXACT content span (delimiters and
environment tail excluded by the 017 envelope law) is checked against
the original retained facts (character length, UTF-8 byte length and
the SHA-256 of the exact observed bytes).  The lookups are read-only:
the payload is never mutated and the slot references the payload's
own string.

Saved chunk 1b (the two accepted tool read carriers): the closed
Responses ``function_call_output`` and Chat ``role="tool"`` result
shapes resolve READ-ONLY to the payload's own decoded string, and
the paired call-identity lookup re-joins the ORIGINAL call ID
(constant-time; the identity never enters an operational
representation).

Saved chunk 1c (the closed replay scan gate): only a CURRENT
authority (verdict ``ok``) may enter the replayed set.  A stale live
reference -- a valid live tag for a retained entry that has left the
accepted selection -- ALWAYS refuses at the transaction gate; the
``stale`` verdict stays the marker layer's internal diagnostic.
Forged, malformed, unknown-kind, moved and kind-incompatible markers
refuse the same way; an accepted replay is recorded content-free.

All records are ACTUAL 017 observations over synthetic payloads
(Unicode/CRLF explicit, environment tail replayed at a shifted
index); every refusal is the fixed typed detail with no echoed
content.  The tool carrier shapes, the original-proof piece join and
the atomic application are later saved chunks of the same PR.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles.bundle_replace import (
    CarrierDetail,
    CarrierSlot,
    ExpectedTag,
    MarkerExpectations,
    RetainedSpan,
    SpanFacts,
    _ReplaceRefusal,
    _scan_replayed_markers,
    check_carrier_span,
    derive_evidence_tag,
    derive_live_tag,
    join_root_occurrence,
    lookup_call_identity,
    lookup_root_carrier,
    lookup_tool_result_carrier,
    make_evidence_marker,
    make_live_marker,
    verify_marker,
)
from slaif_local_coding.constitution.bundles.bundle_replace_models import (
    MarkerKind,
    MarkerRecord,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    OccurrenceKind,
    PathContext,
    RootOccurrence,
    RootStatus,
)
from slaif_local_coding.constitution.bundles.observe import observe_request

_CTX = PathContext(workspace="/work")

#: Exact inner root source (the content span): multibyte Unicode so the
#: UTF-8 byte length is strictly greater than the character length.
ROOT_CONTENT = "Follow `A.md` before mutation. ünïcode ✓\n"

ROOT_TEXT = (
    "# AGENTS.md instructions for /work\n"
    "\n"
    "<INSTRUCTIONS>\n" + ROOT_CONTENT + "\n" + "</INSTRUCTIONS>\n"
    "<environment_context>\n"
    "  <cwd>/work</cwd>\n"
    "</environment_context>"
)
#: The CRLF inner source (two lines): the internal CRLF line breaks
#: are part of the exact observed content; only the delimiter line
#: break is excluded by the envelope law.
ROOT_CONTENT_CRLF = "Follow `A.md` before mutation.\r\nünïcode ✓\r\n"

ROOT_TEXT_CRLF = (
    "# AGENTS.md instructions for /work\r\n"
    "\r\n"
    "<INSTRUCTIONS>\r\n" + ROOT_CONTENT_CRLF + "\r\n" + "</INSTRUCTIONS>\r\n"
    "<environment_context>\r\n"
    "  <cwd>/work</cwd>\r\n"
    "</environment_context>"
)


def root_item(text: str) -> dict[str, Any]:
    return {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
    }


def exec_call(cid: str, cmd: str) -> dict[str, Any]:
    return {
        "type": "function_call",
        "name": "exec_command",
        "call_id": cid,
        "arguments": f'{{"cmd": "{cmd}"}}',
    }


def out_item(cid: str, text: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": cid, "output": text}


def base_payload(root_text: str = ROOT_TEXT) -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope
    (with environment tail) plus one complete read pair."""
    return {
        "model": "synthetic-model",
        "input": [
            root_item(root_text),
            exec_call("synthetic-read-1", "cat /work/A.md"),
            out_item(
                "synthetic-read-1",
                "Chunk ID: 1\nWall time: 0.0001 seconds\n"
                "Process exited with code 0\nOutput:\n"
                "ALWAYS log the mutation.\n",
            ),
        ],
    }


def _refused_detail(fn: Any, *args: Any, **kwargs: Any) -> CarrierDetail:
    with pytest.raises(_ReplaceRefusal) as excinfo:
        fn(*args, **kwargs)
    return excinfo.value.detail


class TestRootCarrierLookup:
    """The closed root location maps to the existing carrier shape."""

    def test_valid_location_maps_to_input_text(self) -> None:
        payload = base_payload()
        slot = lookup_root_carrier(payload, "$.input[0].content[0]", max_text_chars=10_000)
        assert isinstance(slot, CarrierSlot)
        assert slot.endpoint == "responses"
        assert slot.location == "$.input[0].content[0]"
        assert slot.field == "text"
        # Read-only: the slot references the payload's own string.
        assert slot.text is payload["input"][0]["content"][0]["text"]
        assert slot.text == ROOT_TEXT

    def test_repr_is_content_free(self) -> None:
        payload = base_payload()
        slot = lookup_root_carrier(payload, "$.input[0].content[0]", max_text_chars=10_000)
        rendered = repr(slot)
        assert "ü" not in rendered
        assert "INSTRUCTIONS" not in rendered
        assert "protected" in rendered

    @pytest.mark.parametrize(
        ("location", "detail"),
        [
            # Tool shapes are NOT root locations (separate earned
            # surface): refused, never inferred as a root carrier.
            ("$.input[2]", CarrierDetail.LOCATION_MALFORMED),
            ("$.messages[0]", CarrierDetail.LOCATION_MALFORMED),
            ("$", CarrierDetail.LOCATION_MALFORMED),
            # Noncanonical spellings stay refused (no re-spelling law).
            ("$.input[01].content[0]", CarrierDetail.LOCATION_MALFORMED),
            ("$.input[0].content[0].text", CarrierDetail.LOCATION_MALFORMED),
            ("$.input[0].content[-1]", CarrierDetail.LOCATION_MALFORMED),
        ],
    )
    def test_nonmatching_location_spellings_refuse(
        self, location: str, detail: CarrierDetail
    ) -> None:
        payload = base_payload()
        got = _refused_detail(lookup_root_carrier, payload, location, max_text_chars=10_000)
        assert got is detail

    def test_root_spelling_over_tool_item_is_shape_unsupported(self) -> None:
        # A closed root spelling pointing at a non-user item (the
        # function_call at input[1]) is a shape conflict, not a
        # spelling refusal.
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[1].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_shape_unsupported_on_role_and_entry_type(self) -> None:
        payload = base_payload()
        payload["input"][0] = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "input_text", "text": ROOT_TEXT}],
        }
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )
        payload["input"][0]["role"] = "user"
        payload["input"][0]["content"][0] = {"type": "output_text", "text": ROOT_TEXT}
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_carrier_not_text_on_nonstring_field(self) -> None:
        payload = base_payload()
        payload["input"][0]["content"][0] = {"type": "input_text", "text": ["not", "a", "string"]}
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_TEXT
        )
        payload["input"][0]["content"][0] = {"type": "input_text"}
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_TEXT
        )

    def test_absent_index_is_carrier_not_found(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[9].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_FOUND
        )
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[9]", max_text_chars=10_000
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )
        # No input container at all (a Chat-shaped payload): no root
        # carrier exists, and Chat root acquisition is not earned.
        chat = {"messages": [{"role": "tool", "tool_call_id": "c", "content": "x"}]}
        assert (
            _refused_detail(
                lookup_root_carrier, chat, "$.input[0].content[0]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_FOUND
        )

    def test_over_bound_carrier_refuses_before_span_work(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_root_carrier, payload, "$.input[0].content[0]", max_text_chars=10
            )
            is CarrierDetail.OVER_BOUND
        )


class TestExactSpanChecking:
    """The exact content span verified against the original facts."""

    def test_span_facts_match_retained_root_facts(self) -> None:
        payload = base_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (occ,) = report.roots.roots
        assert occ.status is RootStatus.OK
        slot = lookup_root_carrier(payload, occ.location, max_text_chars=10_000)
        facts = check_carrier_span(
            slot,
            occ.content_span.start,
            occ.content_span.end,
            expected_char_length=len(ROOT_CONTENT),
            expected_byte_length=len(ROOT_CONTENT.encode("utf-8")),
            expected_digest=occ.digest,
        )
        assert isinstance(facts, SpanFacts)
        assert facts.char_length == len(ROOT_CONTENT)
        # Multibyte: the UTF-8 byte length is strictly larger.
        assert facts.byte_length > facts.char_length
        assert facts.byte_length == len(ROOT_CONTENT.encode("utf-8"))
        assert facts.digest == occ.digest
        assert payload["input"][0]["content"][0]["text"][
            occ.content_span.start : occ.content_span.end
        ] == (ROOT_CONTENT)
        # The exact span excludes the delimiters and the environment
        # tail (the 017 envelope law): the slice is the inner source
        # only, and the byte offsets cover exactly that source.
        encoded = slot.text.encode("utf-8")
        assert encoded[: facts.byte_start].endswith(b"<INSTRUCTIONS>\n")
        # The delimiter line break before the closing tag belongs to
        # the delimiter, not the content (the envelope law).
        assert encoded[facts.byte_end :].startswith(b"\n</INSTRUCTIONS>")
        assert b"<environment_context>" not in encoded[facts.byte_start : facts.byte_end]

    def test_crlf_root_span_excludes_carriage_returns(self) -> None:
        payload = base_payload(ROOT_TEXT_CRLF)
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (occ,) = report.roots.roots
        slot = lookup_root_carrier(payload, occ.location, max_text_chars=10_000)
        facts = check_carrier_span(
            slot,
            occ.content_span.start,
            occ.content_span.end,
            expected_digest=occ.digest,
            expected_byte_length=occ.byte_length,
        )
        slice_text = slot.text[occ.content_span.start : occ.content_span.end]
        assert slice_text == ROOT_CONTENT_CRLF
        assert facts.byte_length == occ.byte_length
        assert "\r" in slice_text

    @pytest.mark.parametrize(
        ("start", "end"),
        [
            (5, 2),  # end precedes start
            (-1, 3),  # negative start
            (0, 10**9),  # beyond the carrier
        ],
    )
    def test_span_out_of_bounds(self, start: int, end: int) -> None:
        payload = base_payload()
        slot = lookup_root_carrier(payload, "$.input[0].content[0]", max_text_chars=10_000)
        assert (
            _refused_detail(check_carrier_span, slot, start, end)
            is CarrierDetail.SPAN_OUT_OF_BOUNDS
        )

    def test_length_and_digest_mismatches_refuse(self) -> None:
        payload = base_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (occ,) = report.roots.roots
        slot = lookup_root_carrier(payload, occ.location, max_text_chars=10_000)
        span = occ.content_span
        assert (
            _refused_detail(
                check_carrier_span,
                slot,
                span.start,
                span.end,
                expected_char_length=len(ROOT_CONTENT) + 1,
            )
            is CarrierDetail.SPAN_LENGTH_MISMATCH
        )
        assert (
            _refused_detail(
                check_carrier_span,
                slot,
                span.start,
                span.end,
                expected_byte_length=occ.byte_length + 1,
            )
            is CarrierDetail.SPAN_LENGTH_MISMATCH
        )
        other_digest = "0" * 64
        assert (
            _refused_detail(
                check_carrier_span,
                slot,
                span.start,
                span.end,
                expected_digest=other_digest,
            )
            is CarrierDetail.SPAN_DIGEST_MISMATCH
        )


class TestRootOccurrenceJoin:
    """Accepted 017 coordinates joined to the actual payload."""

    def test_join_replayed_envelope_at_shifted_index(self) -> None:
        # Original request: retained root facts from the actual 017
        # observation.
        original = base_payload()
        original_report = observe_request(original, context=_CTX, endpoint="responses")
        (retained,) = original_report.roots.roots
        retained_digest = retained.digest
        retained_char_length = retained.content_span.length
        retained_byte_length = retained.byte_length

        # Resent history: the same envelope replayed at a SHIFTED
        # structural index (a new item precedes it), environment tail
        # included.
        resent = base_payload()
        resent["input"].insert(0, exec_call("synthetic-other", "ls /work"))
        resent_report = observe_request(resent, context=_CTX, endpoint="responses")
        (current,) = resent_report.roots.roots
        assert current.location == "$.input[1].content[0]"
        assert current.digest == retained_digest

        slot, facts = join_root_occurrence(
            resent,
            current,
            expected_digest=retained_digest,
            expected_char_length=retained_char_length,
            expected_byte_length=retained_byte_length,
            max_text_chars=10_000,
        )
        assert slot.location == "$.input[1].content[0]"
        assert facts.digest == retained_digest
        assert facts.char_length == retained_char_length
        assert facts.byte_length == retained_byte_length
        start = current.content_span.start
        assert slot.text[start : start + retained_char_length] == ROOT_CONTENT

    def test_join_changed_root_content_is_digest_mismatch(self) -> None:
        original = base_payload()
        original_report = observe_request(original, context=_CTX, endpoint="responses")
        (retained,) = original_report.roots.roots

        changed = base_payload(ROOT_TEXT.replace("before mutation", "after mutation"))
        changed_report = observe_request(changed, context=_CTX, endpoint="responses")
        (current,) = changed_report.roots.roots
        assert current.digest != retained.digest
        assert (
            _refused_detail(
                join_root_occurrence,
                changed,
                current,
                expected_digest=retained.digest,
                max_text_chars=10_000,
            )
            is CarrierDetail.SPAN_DIGEST_MISMATCH
        )

    def test_join_carrier_leaving_payload_is_scope_conflict(self) -> None:
        original = base_payload()
        original_report = observe_request(original, context=_CTX, endpoint="responses")
        (retained,) = original_report.roots.roots

        # The observed location exists in the ORIGINAL payload, not in
        # this one: the observed coordinates leave the decoded request.
        other = {"input": []}
        assert (
            _refused_detail(
                join_root_occurrence,
                other,
                retained,
                expected_digest=retained.digest,
                max_text_chars=10_000,
            )
            is CarrierDetail.CARRIER_NOT_FOUND
        )

    def test_join_refuses_non_root_and_non_ok_occurrences(self) -> None:
        payload = base_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (root_occ,) = report.roots.roots
        non_root = RootOccurrence(
            kind=OccurrenceKind.NON_ROOT,
            location="$.input[0].content[0]",
            status=RootStatus.OK,
        )
        assert (
            _refused_detail(
                join_root_occurrence,
                payload,
                non_root,
                expected_digest=root_occ.digest or "0" * 64,
                max_text_chars=10_000,
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )
        bad_status = root_occ.model_copy(update={"status": RootStatus.UNSUPPORTED})
        assert (
            _refused_detail(
                join_root_occurrence,
                payload,
                bad_status,
                expected_digest=root_occ.digest or "0" * 64,
                max_text_chars=10_000,
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_join_is_read_only_and_payload_unchanged(self) -> None:
        payload = base_payload()
        snapshot = copy.deepcopy(payload)
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (occ,) = report.roots.roots
        join_root_occurrence(payload, occ, expected_digest=occ.digest, max_text_chars=10_000)
        check_carrier_span(
            lookup_root_carrier(payload, occ.location, max_text_chars=10_000),
            occ.content_span.start,
            occ.content_span.end,
        )
        assert payload == snapshot


# --- Saved chunk 1b: the two tool carrier shapes --------------------------

CHAT_RESULT_TEXT = (
    "Chunk ID: 1\nWall time: 0.0001 seconds\n"
    "Process exited with code 0\nOutput:\n"
    "ALWAYS log the mutation.\n"
)


def chat_payload() -> dict[str, Any]:
    """One decoded Chat request: one assistant tool call plus its tool
    result message (the accepted 017 Chat read shapes)."""
    return {
        "model": "synthetic-model",
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "synthetic-read-1",
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": '{"cmd": "cat /work/A.md"}',
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "synthetic-read-1", "content": CHAT_RESULT_TEXT},
        ],
    }


class TestToolResultCarrierLookup:
    """The accepted Responses and Chat result carrier shapes."""

    def test_responses_result_carrier_from_accepted_coordinates(self) -> None:
        payload = base_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (read,) = report.reads
        assert read.outcome is not None
        slot = lookup_tool_result_carrier(
            payload, "responses", read.result_location, max_text_chars=10_000
        )
        assert slot.endpoint == "responses"
        assert slot.location == "$.input[2]"
        assert slot.field == "output"
        assert slot.text is payload["input"][2]["output"]
        assert slot.text.startswith("Chunk ID: 1\n")

    def test_chat_result_carrier_from_accepted_coordinates(self) -> None:
        payload = chat_payload()
        report = observe_request(payload, context=_CTX, endpoint="chat")
        (read,) = report.reads
        slot = lookup_tool_result_carrier(
            payload, "chat", read.result_location, max_text_chars=10_000
        )
        assert slot.endpoint == "chat"
        assert slot.location == "$.messages[1]"
        assert slot.field == "content"
        assert slot.text is payload["messages"][1]["content"]
        assert slot.text == CHAT_RESULT_TEXT

    def test_dynamically_constructed_endpoint_string_dispatches_by_value(self) -> None:
        # Endpoint membership and dispatch are VALUE equality: a
        # dynamically constructed string equal to the domain dispatches
        # exactly like the constant (no identity-dependent fallthrough
        # into the other endpoint branch).
        dyn_responses = "res" + "ponses"
        dyn_chat = "ch" + "at"
        payload = base_payload()
        slot = lookup_tool_result_carrier(
            payload, dyn_responses, "$.input[2]", max_text_chars=10_000
        )
        assert slot.endpoint == "responses"
        assert slot.field == "output"
        chat = chat_payload()
        slot = lookup_tool_result_carrier(chat, dyn_chat, "$.messages[1]", max_text_chars=10_000)
        assert slot.endpoint == "chat"
        assert slot.field == "content"

    def test_call_item_is_not_a_result_carrier(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_tool_result_carrier,
                payload,
                "responses",
                "$.input[1]",
                max_text_chars=10_000,
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_nonstring_result_field(self) -> None:
        payload = base_payload()
        payload["input"][2]["output"] = 123
        assert (
            _refused_detail(
                lookup_tool_result_carrier,
                payload,
                "responses",
                "$.input[2]",
                max_text_chars=10_000,
            )
            is CarrierDetail.CARRIER_NOT_TEXT
        )
        chat = chat_payload()
        del chat["messages"][1]["content"]
        assert (
            _refused_detail(
                lookup_tool_result_carrier, chat, "chat", "$.messages[1]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_TEXT
        )

    def test_non_tool_message_is_shape_unsupported(self) -> None:
        chat = chat_payload()
        chat["messages"][1] = {"role": "user", "content": CHAT_RESULT_TEXT}
        assert (
            _refused_detail(
                lookup_tool_result_carrier, chat, "chat", "$.messages[1]", max_text_chars=10_000
            )
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_absent_index_and_over_bound(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_tool_result_carrier,
                payload,
                "responses",
                "$.input[9]",
                max_text_chars=10_000,
            )
            is CarrierDetail.CARRIER_NOT_FOUND
        )
        chat = chat_payload()
        assert (
            _refused_detail(
                lookup_tool_result_carrier, chat, "chat", "$.messages[9]", max_text_chars=10_000
            )
            is CarrierDetail.CARRIER_NOT_FOUND
        )
        assert (
            _refused_detail(
                lookup_tool_result_carrier, payload, "responses", "$.input[2]", max_text_chars=5
            )
            is CarrierDetail.OVER_BOUND
        )

    def test_closed_spelling_of_other_endpoint_domain(self) -> None:
        payload = base_payload()
        chat = chat_payload()
        assert (
            _refused_detail(
                lookup_tool_result_carrier,
                chat,
                "responses",
                "$.messages[1]",
                max_text_chars=10_000,
            )
            is CarrierDetail.ENDPOINT_MISMATCH
        )
        assert (
            _refused_detail(
                lookup_tool_result_carrier, payload, "chat", "$.input[2]", max_text_chars=10_000
            )
            is CarrierDetail.ENDPOINT_MISMATCH
        )

    @pytest.mark.parametrize(
        "location",
        [
            "$",
            "$.input[01]",
            "$.input[2].output",
            "$.input[2].content[0]",  # the root shape: not a result spelling
            "$.messages[0].tool_calls[0]",  # the Chat CALL shape: not a result spelling
            "$.messages[1].content",
        ],
    )
    def test_nonmatching_spellings_refuse(self, location: str) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_tool_result_carrier, payload, "responses", location, max_text_chars=10_000
            )
            is CarrierDetail.LOCATION_MALFORMED
        )


class TestCallIdentityLookup:
    """The paired call-identity lookups (original association join)."""

    def test_responses_call_identity_rejoined(self) -> None:
        payload = base_payload()
        report = observe_request(payload, context=_CTX, endpoint="responses")
        (read,) = report.reads
        identity = lookup_call_identity(
            payload, "responses", read.call_location, expected_call_id="synthetic-read-1"
        )
        assert identity.endpoint == "responses"
        assert identity.location == "$.input[1]"
        assert identity.wire_family == "function_call"
        assert identity.call_id == "synthetic-read-1"
        # The private ID never enters the operational representation.
        assert "synthetic-read-1" not in repr(identity)

    def test_responses_custom_tool_call_family_is_identity_only(self) -> None:
        payload = base_payload()
        payload["input"][1] = {
            "type": "custom_tool_call",
            "call_id": "synthetic-opaque-1",
            "input": "opaque",
        }
        identity = lookup_call_identity(
            payload, "responses", "$.input[1]", expected_call_id="synthetic-opaque-1"
        )
        assert identity.wire_family == "custom_tool_call"
        assert identity.call_id == "synthetic-opaque-1"

    def test_chat_call_identity_rejoined(self) -> None:
        chat = chat_payload()
        report = observe_request(chat, context=_CTX, endpoint="chat")
        (read,) = report.reads
        identity = lookup_call_identity(
            chat, "chat", read.call_location, expected_call_id="synthetic-read-1"
        )
        assert identity.endpoint == "chat"
        assert identity.location == "$.messages[0].tool_calls[0]"
        assert identity.wire_family == "function"
        assert identity.call_id == "synthetic-read-1"
        assert "synthetic-read-1" not in repr(identity)

    def test_dynamically_constructed_endpoint_string_dispatches_by_value(self) -> None:
        payload = base_payload()
        identity = lookup_call_identity(
            payload, "res" + "ponses", "$.input[1]", expected_call_id="synthetic-read-1"
        )
        assert identity.wire_family == "function_call"
        chat = chat_payload()
        identity = lookup_call_identity(
            chat, "ch" + "at", "$.messages[0].tool_calls[0]", expected_call_id="synthetic-read-1"
        )
        assert identity.wire_family == "function"

    def test_identity_mismatch_on_diverging_call_id(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(
                lookup_call_identity,
                payload,
                "responses",
                "$.input[1]",
                expected_call_id="other-call",
            )
            is CarrierDetail.IDENTITY_MISMATCH
        )
        chat = chat_payload()
        assert (
            _refused_detail(
                lookup_call_identity,
                chat,
                "chat",
                "$.messages[0].tool_calls[0]",
                expected_call_id="other-call",
            )
            is CarrierDetail.IDENTITY_MISMATCH
        )

    def test_result_item_is_not_a_call(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(lookup_call_identity, payload, "responses", "$.input[2]")
            is CarrierDetail.SHAPE_UNSUPPORTED
        )
        chat = chat_payload()
        assert (
            _refused_detail(lookup_call_identity, chat, "chat", "$.messages[1]")
            is CarrierDetail.LOCATION_MALFORMED
        )

    @pytest.mark.parametrize(
        ("item", "detail"),
        [
            ({"type": "function_call", "name": "exec_command"}, CarrierDetail.CALL_NOT_FOUND),
            (
                {"type": "function_call", "name": "exec_command", "call_id": ""},
                CarrierDetail.CALL_NOT_FOUND,
            ),
            (
                {"type": "function_call", "name": "exec_command", "call_id": 7},
                CarrierDetail.CALL_NOT_FOUND,
            ),
            (
                {"type": "function_call", "name": "exec_command", "call_id": "ok"},
                CarrierDetail.CALL_NOT_FOUND,
            )
            if False
            else (
                {"type": "user_message", "call_id": "ok"},
                CarrierDetail.SHAPE_UNSUPPORTED,
            ),
        ],
    )
    def test_call_id_and_family_laws(self, item: dict[str, Any], detail: CarrierDetail) -> None:
        payload = base_payload()
        payload["input"][1] = item
        assert _refused_detail(lookup_call_identity, payload, "responses", "$.input[1]") is detail

    def test_absent_indexes(self) -> None:
        payload = base_payload()
        assert (
            _refused_detail(lookup_call_identity, payload, "responses", "$.input[9]")
            is CarrierDetail.CARRIER_NOT_FOUND
        )
        chat = chat_payload()
        assert (
            _refused_detail(lookup_call_identity, chat, "chat", "$.messages[9].tool_calls[0]")
            is CarrierDetail.CARRIER_NOT_FOUND
        )
        assert (
            _refused_detail(lookup_call_identity, chat, "chat", "$.messages[0].tool_calls[9]")
            is CarrierDetail.SHAPE_UNSUPPORTED
        )

    def test_closed_spelling_of_other_endpoint_domain(self) -> None:
        payload = base_payload()
        chat = chat_payload()
        assert (
            _refused_detail(lookup_call_identity, chat, "responses", "$.messages[0].tool_calls[0]")
            is CarrierDetail.ENDPOINT_MISMATCH
        )
        assert (
            _refused_detail(lookup_call_identity, payload, "chat", "$.input[1]")
            is CarrierDetail.ENDPOINT_MISMATCH
        )

    def test_lookups_are_read_only(self) -> None:
        payload = base_payload()
        snapshot = copy.deepcopy(payload)
        lookup_tool_result_carrier(payload, "responses", "$.input[2]", max_text_chars=10_000)
        lookup_call_identity(
            payload, "responses", "$.input[1]", expected_call_id="synthetic-read-1"
        )
        assert payload == snapshot


# --- Saved chunk 1c: the closed replay scan gate -------------------------
#
# The transaction-level closed gate (``_scan_replayed_markers``):
# only a CURRENT authority (verdict ``ok``) enters the replayed set.
# A stale live reference (a valid live tag for a retained entry that
# has left the accepted selection) ALWAYS refuses; the ``stale``
# verdict stays the marker layer's internal diagnostic.  Forged,
# cross-namespace, malformed, unknown-version, moved and
# kind-incompatible markers refuse the same way; an accepted replay
# is recorded content-free.

MARKER_KEY = b"synthetic-session-key-022b"
MK_CONTENT_KEY = "ab" * 32
MK_SOURCE_DIGEST = "cd" * 32
MK_COMPILED_DIGEST = "ef" * 32
MK_ENDPOINT = "responses"
MK_LOCATION = "$.input[2]"
MK_PREFIX = "P" * 10
MK_SUFFIX = "Q" * 4
_MK_BINDING_KEY: tuple[str, str, int, int, int, int, str] = (
    MK_ENDPOINT,
    "synthetic-read-1",
    1,
    2,
    0,
    0,
    MK_CONTENT_KEY,
)


def _mk_live_marker(key: bytes = MARKER_KEY, namespace: str = "synthetic-namespace") -> str:
    return make_live_marker(
        key,
        namespace_key=namespace,
        original_role="file_tool_result",
        occurrence_identity="synthetic-occurrence",
        endpoint=MK_ENDPOINT,
        call_id="synthetic-read-1",
        call_position=1,
        result_position=2,
        piece_index=0,
        segment_index=0,
        entry_class="file_entry",
        content_key=MK_CONTENT_KEY,
        compiled_digest=MK_COMPILED_DIGEST,
        source_digest=MK_SOURCE_DIGEST,
    )


def _mk_live_tag(
    key: bytes = MARKER_KEY,
    namespace: str = "synthetic-namespace",
    stale: bool = False,
) -> ExpectedTag:
    return derive_live_tag(
        key,
        namespace_key=namespace,
        original_role="file_tool_result",
        occurrence_identity="synthetic-occurrence",
        endpoint=MK_ENDPOINT,
        call_id="synthetic-read-1",
        call_position=1,
        result_position=2,
        piece_index=0,
        segment_index=0,
        entry_class="file_entry",
        content_key=MK_CONTENT_KEY,
        compiled_digest=MK_COMPILED_DIGEST,
        source_digest=MK_SOURCE_DIGEST,
        stale=stale,
    )


def _mk_evidence_marker(key: bytes = MARKER_KEY) -> str:
    return make_evidence_marker(
        key,
        namespace_key="synthetic-namespace",
        original_role="file_tool_result",
        occurrence_identity="synthetic-occurrence",
        endpoint=MK_ENDPOINT,
        call_id="synthetic-read-1",
        call_position=1,
        result_position=2,
        piece_index=0,
        segment_index=0,
        source_digest=MK_SOURCE_DIGEST,
        content_key=MK_CONTENT_KEY,
    )


def _mk_evidence_tag(key: bytes = MARKER_KEY) -> ExpectedTag:
    return derive_evidence_tag(
        key,
        namespace_key="synthetic-namespace",
        original_role="file_tool_result",
        occurrence_identity="synthetic-occurrence",
        endpoint=MK_ENDPOINT,
        call_id="synthetic-read-1",
        call_position=1,
        result_position=2,
        piece_index=0,
        segment_index=0,
        source_digest=MK_SOURCE_DIGEST,
        content_key=MK_CONTENT_KEY,
    )


def _mk_span(start: int, end: int) -> RetainedSpan:
    return RetainedSpan(
        content_key=MK_CONTENT_KEY,
        entry_class="file_entry",
        role="file_tool_result",
        endpoint=MK_ENDPOINT,
        occurrence_identity="synthetic-occurrence",
        call_id="synthetic-read-1",
        call_position=1,
        result_position=2,
        piece_index=0,
        segment_index=0,
        location=MK_LOCATION,
        field="output",
        start=start,
        end=end,
        source_digest=MK_SOURCE_DIGEST,
        reproven=True,
        bytes_mismatch=False,
    )


def _mk_binding(
    span: RetainedSpan, kinds: frozenset[str]
) -> dict[tuple[str, str, int, int, int, int, str], tuple[RetainedSpan, frozenset[str]]]:
    return {_MK_BINDING_KEY: (span, kinds)}


def _scan(
    carrier: str,
    expectations: MarkerExpectations,
    binding: dict[tuple[str, str, int, int, int, int, str], tuple[RetainedSpan, frozenset[str]]],
) -> dict[tuple[str, str, int], MarkerRecord]:
    return _scan_replayed_markers({(MK_ENDPOINT, MK_LOCATION): carrier}, expectations, binding)


class TestReplayedMarkerScan:
    """The closed gate: only the ``ok`` verdict enters the replayed set."""

    def test_stale_live_token_always_refuses(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(stale=True),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                MK_PREFIX + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"live"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_stale_token_refuses_even_with_stale_kind_bound(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(stale=True),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                MK_PREFIX + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"stale", "live"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_stale_verdict_stays_internal_diagnostic(self) -> None:
        marker = _mk_live_marker()
        stale = MarkerExpectations((_mk_live_tag(stale=True),))
        verdict = verify_marker(marker, 10, expectations=stale)
        assert verdict.valid is False
        assert verdict.reason == "stale"
        current = MarkerExpectations((_mk_live_tag(stale=False),))
        verdict = verify_marker(marker, 10, expectations=current)
        assert verdict.valid is True
        assert verdict.reason == "ok"

    def test_current_live_token_replay_accepted_content_free(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(),))
        replayed = _scan(
            MK_PREFIX + marker + MK_SUFFIX,
            expectations,
            _mk_binding(span, frozenset({"live"})),
        )
        ((key, record),) = replayed.items()
        assert key == (MK_ENDPOINT, MK_LOCATION, 10)
        assert record.replayed is True
        assert record.kind is MarkerKind.LIVE_REFERENCE
        assert record.carrier_location == MK_LOCATION
        assert record.field == "output"
        assert record.start == 10
        assert record.end == 10 + len(marker)
        assert record.marker_bytes == len(marker.encode("utf-8"))
        assert record.marker_sha256 == hashlib.sha256(marker.encode("utf-8")).hexdigest()
        assert record.target_content_key == MK_CONTENT_KEY
        assert record.source_digest == MK_SOURCE_DIGEST
        # The private call identity never enters the representation.
        assert "synthetic-read-1" not in repr(record)

    def test_evidence_token_accepted_when_evidence_kind_bound(self) -> None:
        marker = _mk_evidence_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_evidence_tag(),))
        replayed = _scan(
            MK_PREFIX + marker + MK_SUFFIX,
            expectations,
            _mk_binding(span, frozenset({"evidence"})),
        )
        ((key, record),) = replayed.items()
        assert key == (MK_ENDPOINT, MK_LOCATION, 10)
        assert record.replayed is True
        assert record.kind is MarkerKind.EVIDENCE

    def test_forged_token_refuses(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(key=b"other-session-key"),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                MK_PREFIX + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"live"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_cross_namespace_token_refuses(self) -> None:
        marker = _mk_live_marker(namespace="other-namespace")
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                MK_PREFIX + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"live"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_moved_token_refuses(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                "P" * 12 + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"live"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_kind_incompatible_token_refuses(self) -> None:
        marker = _mk_live_marker()
        span = _mk_span(10, 10 + len(marker))
        expectations = MarkerExpectations((_mk_live_tag(),))
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(
                MK_PREFIX + marker + MK_SUFFIX,
                expectations,
                _mk_binding(span, frozenset({"evidence"})),
            )
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_unknown_version_refuses(self) -> None:
        span = _mk_span(10, 53)
        expectations = MarkerExpectations((_mk_live_tag(),))
        unknown = MK_PREFIX + "[slaif-live:v9:" + "A" * 43 + "]" + MK_SUFFIX
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(unknown, expectations, _mk_binding(span, frozenset({"live"})))
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_malformed_tag_refuses(self) -> None:
        span = _mk_span(10, 53)
        expectations = MarkerExpectations((_mk_live_tag(),))
        malformed = MK_PREFIX + "[slaif-live:v1:" + "A" * 40 + "]" + MK_SUFFIX
        with pytest.raises(_ReplaceRefusal) as excinfo:
            _scan(malformed, expectations, _mk_binding(span, frozenset({"live"})))
        assert excinfo.value.detail is CarrierDetail.MARKER_INVALID

    def test_plain_text_without_markers_replays_nothing(self) -> None:
        span = _mk_span(10, 16)
        expectations = MarkerExpectations((_mk_live_tag(),))
        replayed = _scan(
            MK_PREFIX + "plain text" + MK_SUFFIX,
            expectations,
            _mk_binding(span, frozenset({"live"})),
        )
        assert replayed == {}
