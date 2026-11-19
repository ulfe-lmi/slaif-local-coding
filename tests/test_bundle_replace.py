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

All records are ACTUAL 017 observations over synthetic payloads
(Unicode/CRLF explicit, environment tail replayed at a shifted
index); every refusal is the fixed typed detail with no echoed
content.  The tool carrier shapes, the original-proof piece join and
the atomic application are later saved chunks of the same PR.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles.bundle_replace import (
    CarrierDetail,
    CarrierSlot,
    SpanFacts,
    _ReplaceRefusal,
    check_carrier_span,
    join_root_occurrence,
    lookup_root_carrier,
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
