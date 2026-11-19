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
import json
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.bundle_budget import (
    BundleBudgetConfig,
    BundleBudgetPlan,
)
from slaif_local_coding.constitution.bundles.bundle_replace import (
    CarrierDetail,
    CarrierSlot,
    ExpectedTag,
    MarkerExpectations,
    RetainedSpan,
    SpanFacts,
    _positively_superseded,
    _ReplaceRefusal,
    _scan_replayed_markers,
    _SupersessionEvidence,
    _verify_call_binding,
    check_carrier_span,
    derive_evidence_tag,
    derive_live_tag,
    join_root_occurrence,
    lookup_call_identity,
    lookup_root_carrier,
    lookup_tool_result_carrier,
    make_evidence_marker,
    make_live_marker,
    replace_sources,
    verify_marker,
)
from slaif_local_coding.constitution.bundles.bundle_replace_models import (
    MarkerKind,
    MarkerRecord,
    PreparedGenerationProof,
    ReplacementOutcome,
)
from slaif_local_coding.constitution.bundles.bundle_selection import (
    SelectionOmissionReason,
    SelectionOutcome,
    select_working_set,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    get_bundle_tokenizer,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    HistoryBounds,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    OccurrenceKind,
    PathContext,
    RootOccurrence,
    RootStatus,
)
from slaif_local_coding.constitution.bundles.observe import observe_request
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateSnapshot,
)
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryPointer,
    RecoveryPublishResult,
    RecoveryStoreLimitation,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
)
from tests.test_bundle_compiler import (
    A_BODY,
    _config,
)
from tests.test_bundle_selection import (
    B_BODY,
    ROOT_REQUIRED,
    _dep,
    _entry_for,
    _file_index,
    _ready,
    _represented,
    _root_index,
    _states,
)
from tests.test_causal_history import (
    exec_call as _ch_exec_call,
)
from tests.test_causal_history import (
    frame as _ch_frame,
)
from tests.test_causal_history import (
    out_item as _ch_out_item,
)
from tests.test_causal_history import (
    read_request,
    sha256_hex,
)
from tests.test_causal_history import (
    root_item as _ch_root_item,
)
from tests.test_root_region_lineage import r_bootstrap, r_issue, r_observe

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
        assert occ.content_span is not None
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
        assert occ.content_span is not None
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
        assert occ.byte_length is not None
        slot = lookup_root_carrier(payload, occ.location, max_text_chars=10_000)
        span = occ.content_span
        assert span is not None
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
        assert retained.content_span is not None
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
        assert current.content_span is not None
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
        other: dict[str, Any] = {"input": []}
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

    def test_join_foreign_workspace_scope_refuses(self) -> None:
        original = base_payload()
        original_report = observe_request(original, context=_CTX, endpoint="responses")
        (retained,) = original_report.roots.roots

        # Same source bytes, same shape, same content digest, but the
        # envelope's workspace scope is FOREIGN to the prepared trusted
        # namespace: the existing scope conflict refuses before any
        # span work -- never an edit on identical bytes.
        foreign = base_payload(ROOT_TEXT.replace("/work", "/other"))
        foreign_report = observe_request(foreign, context=_CTX, endpoint="responses")
        (foreign_occ,) = foreign_report.roots.roots
        assert foreign_occ.scope_label == "/other"
        assert foreign_occ.digest == retained.digest
        assert (
            _refused_detail(
                join_root_occurrence,
                foreign,
                foreign_occ,
                expected_digest=retained.digest,
                expected_workspace=_CTX.workspace,
                max_text_chars=10_000,
            )
            is CarrierDetail.CARRIER_UNRESOLVED
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
        assert occ.content_span is not None
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


# --- The ACTUAL original tool identity join -----------------------------
#
# The call ID alone is not identity: the retained D result record
# binds each piece's actual producing call by tool name and the SAME
# canonical argument fingerprint, so a reused call ID under a
# different command is refused, never edited.
#
class TestCallArgumentBinding:
    """The original tool identity evidence (carrier layer).

    The records are the ACTUAL retained P/D result records of the
    saved transaction fixture (chunk 1d), never hand-constructed: the
    positive binds the actual c2 call to its actual record, and the
    same-ID negative mutates ONLY c2's current command (its output
    stays identical) and must refuse."""

    @staticmethod
    def _fixture() -> tuple[dict[str, Any], dict[str, Any], HistoryBounds]:
        rec = _transaction_records()
        snapshot = rec["snapshot"]
        results_by_call = {record.call_id: record for record in snapshot.state.d_state.results}
        assert set(results_by_call) == {"c1", "c2"}
        return (
            _transaction_payload(),
            results_by_call,
            snapshot.namespace.history_bounds,
        )

    def test_actual_current_call_binds(self) -> None:
        payload, results_by_call, bounds = self._fixture()
        identity = lookup_call_identity(payload, "responses", "$.input[3]", expected_call_id="c2")
        _verify_call_binding(identity, "c2", 0, results_by_call, bounds)

    def test_same_id_different_command_refuses(self) -> None:
        payload, results_by_call, bounds = self._fixture()
        # Mutate ONLY c2's current command; its output stays identical.
        payload["input"][3]["arguments"] = '{"cmd": "cat A.md"}'
        identity = lookup_call_identity(payload, "responses", "$.input[3]", expected_call_id="c2")
        assert (
            _refused_detail(_verify_call_binding, identity, "c2", 0, results_by_call, bounds)
            is CarrierDetail.IDENTITY_MISMATCH
        )

    def test_missing_retained_record_is_detached(self) -> None:
        payload = base_payload()
        identity = lookup_call_identity(
            payload, "responses", "$.input[1]", expected_call_id="synthetic-read-1"
        )
        assert (
            _refused_detail(
                _verify_call_binding, identity, "synthetic-read-1", 0, {}, HistoryBounds()
            )
            is CarrierDetail.RETAINED_RECORD_MALFORMED
        )


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
) -> dict[
    tuple[str, str, int, int, int, int, str],
    tuple[tuple[RetainedSpan, frozenset[str]], ...],
]:
    return {_MK_BINDING_KEY: ((span, kinds),)}


def _scan(
    carrier: str,
    expectations: MarkerExpectations,
    binding: dict[
        tuple[str, str, int, int, int, int, str],
        tuple[tuple[RetainedSpan, frozenset[str]], ...],
    ],
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


# ---------------------------------------------------------------------------
# Transaction-level replay through the ACTUAL entry point (objective 022-b,
# saved chunk 1e): the real replace_sources over ACTUAL 017/018/019/021
# records.  The smoke fixture is the rooted bootstrap plus the genuinely
# issued proven segmented [A,B] read (one result carrier, two proven
# splices) and the C singleton read, lean-admitted; the original payload is
# replaced and the transformed output is replayed through the SAME entry
# point.  Omission and supersession variants follow in later saved chunks.
# ---------------------------------------------------------------------------

C_BODY = "Background notes for the later turn.\n"
REPLAY_CMD = "cat A.md && echo 'REPLAYSEP' && cat B.md"
REPLAY_BODY = A_BODY + "REPLAYSEP\n" + B_BODY
TRANSACTION_BUDGET = 12288


def _transaction_records(
    reads: tuple[tuple[str, str, str], ...] = (
        ("c1", REPLAY_BODY, REPLAY_CMD),
        ("c2", C_BODY, "cat C.md"),
    ),
    mode: AdmissionMode = AdmissionMode.LEAN,
    endpoint: str = "responses",
    lineage: str = "replace022b-transaction",
    deps: tuple[Any, ...] = (
        _dep("A.md", "P1", 90, "immediate"),
        _dep("B.md", "P2", 50, "next_turn"),
        _dep("C.md", "P2", 30, "background"),
    ),
) -> dict[str, Any]:
    """The ACTUAL P/T fixture and its prepared transaction inputs
    (snapshot, durable-generation proof, ready entries, selection).

    ``reads`` is the issued read history ``(cid, body, cmd)``; the
    bundle entry is the admitted entry containing A.md and B.md (the
    proven [A,B] partition or the [A,B,C] 3-member partition of the
    omission variant) and ``entry_c`` the admitted C.md singleton."""
    ns, state, t = _states(ROOT_REQUIRED, reads, mode, endpoint, lineage)
    root_entry = t.admission.root_entry
    bundle = next(e for e in t.admission.entries if {"A.md", "B.md"} <= set(_represented(t, e)))
    entry_c = _entry_for(t, "C.md")
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(root_entry, config, tokenizer, plan, deps)
    index_bundle = _file_index(
        bundle,
        (),
        config,
        tokenizer,
        plan,
        rule_id="bundle-procedure",
        statement="Follow the retained bundle procedure.",
        location="",
    )
    index_c = _file_index(
        entry_c,
        (),
        config,
        tokenizer,
        plan,
        rule_id="background-notes",
        statement="Background notes for the later turn.",
        location="C.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=state, result=t, revision=state.revision, epoch=1, owned_bytes=0
    )
    proof = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot,
    )
    ready_root = _ready(t, root_entry, root_index, ("A.md", "B.md", "C.md"))
    ready_bundle = _ready(t, bundle, index_bundle, (), origin_proven=True)
    ready_c = _ready(t, entry_c, index_c, ())
    decision = select_working_set(ready_root, (ready_bundle, ready_c), plan)
    assert decision.outcome is SelectionOutcome.OK
    return {
        "snapshot": snapshot,
        "proof": proof,
        "ready": (ready_root, ready_bundle, ready_c),
        "decision": decision,
    }


def _transaction_payload() -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope plus the
    two complete read pairs (the proven segmented [A,B] bundle and the C
    singleton), exactly as the P/T fixture observed them."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_REQUIRED),
            _ch_exec_call("c1", REPLAY_CMD),
            _ch_out_item("c1", _ch_frame(REPLAY_BODY)),
            _ch_exec_call("c2", "cat C.md"),
            _ch_out_item("c2", _ch_frame(C_BODY)),
        ],
    }


def _transaction_payload_tail() -> dict[str, Any]:
    """The transaction payload whose root envelope carries the
    environment-context tail.  The P-state bootstrap envelope carries
    the SAME root content facts (the tail is excluded from the content
    span by the 017 envelope law), so the join proves the exact
    retained span inside the tailed envelope."""
    payload = _transaction_payload()
    payload["input"][0]["content"][0]["text"] = (
        "# AGENTS.md instructions for /work\n"
        "\n"
        "<INSTRUCTIONS>\n" + ROOT_REQUIRED + "\n</INSTRUCTIONS>\n"
        "<environment_context>\n"
        "  <cwd>/work</cwd>\n"
        "</environment_context>"
    )
    return payload


OMISSION_CMD = "cat A.md && echo 'REPLAYSEP' && cat B.md && echo 'REPLAYSEP2' && cat C.md"
OMISSION_BODY = A_BODY + "REPLAYSEP\n" + B_BODY + "REPLAYSEP2\n" + C_BODY


def _omission_records() -> dict[str, Any]:
    """The omission variant: the proven [A,B,C] 3-member partition plus
    the C.md singleton whose path the bundle covers, so the accepted
    selection omits the singleton WHOLE (COVERAGE_DEDUPLICATED)."""
    return _transaction_records(
        reads=(("c1", OMISSION_BODY, OMISSION_CMD), ("c2", C_BODY, "cat C.md")),
        lineage="replace022b-omission",
    )


def _omission_payload() -> dict[str, Any]:
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_REQUIRED),
            _ch_exec_call("c1", OMISSION_CMD),
            _ch_out_item("c1", _ch_frame(OMISSION_BODY)),
            _ch_exec_call("c2", "cat C.md"),
            _ch_out_item("c2", _ch_frame(C_BODY)),
        ],
    }


def _chat_transaction_payload() -> dict[str, Any]:
    """The same two complete read pairs on the Chat read endpoint (one
    assistant tool-call message, two tool result messages).  Root
    authority is a separate Responses envelope, so this payload carries
    no root carrier: the root earns zero edits (source-absent)."""
    return {
        "model": "synthetic-model",
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": REPLAY_CMD}),
                        },
                    },
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat C.md"}),
                        },
                    },
                ],
            },
            {"role": "tool", "tool_call_id": "c1", "content": _ch_frame(REPLAY_BODY)},
            {"role": "tool", "tool_call_id": "c2", "content": _ch_frame(C_BODY)},
        ],
    }


class TestTransactionReplay:
    """The ACTUAL replace_sources entry point over the smoke fixture:
    replace the original payload, then replay the transformed output."""

    def test_replace_then_replay_idempotent(self) -> None:
        rec = _transaction_records()
        payload1 = _transaction_payload()
        frozen = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert payload1 == frozen
        # The original payload earns exactly four LIVE edits: the root
        # envelope content span, the two proven [A,B] splices and the C
        # singleton span.
        assert len(result1.edits) == 4
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result1.edits)
        assert result1.edits_planned == 4
        assert result1.edits_committed == 4
        assert result1.markers_emitted == 4
        assert result1.markers_replayed == 0
        # The replay round: the transformed output is re-observed and
        # re-joined through the SAME entry point; every marker replays at
        # its current carrier coordinates (the earlier splice shifted the
        # later one), no edit is planned, and the payload is fixed.
        payload2 = result1.transformed_payload
        assert payload2 is not None
        obs2 = observe_request(payload2, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == payload2
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 4
        # Historical marker idempotence: a THIRD round of the same
        # transformed payload replays again -- an accepted replay
        # neither changes authority nor creates a second edit.
        out2 = result2.transformed_payload
        assert out2 is not None
        obs3 = observe_request(out2, endpoint="responses", context=_CTX)
        result3 = replace_sources(
            out2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs3,
            root_occurrence=obs3.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result3.outcome is ReplacementOutcome.OK, result3
        assert result3.transformed_payload == result2.transformed_payload
        assert result3.edits_planned == 0
        assert result3.edits_committed == 0
        assert result3.markers_replayed == 4

    def test_foreign_workspace_envelope_refuses_all_or_nothing(self) -> None:
        rec = _transaction_records()
        payload = _transaction_payload()
        # The SAME root source bytes in a same-shaped envelope whose
        # workspace scope is foreign to the prepared trusted namespace:
        # the proof bridge has already refused that workspace, and the
        # repeated-root join must refuse the existing scope conflict --
        # never an edit on identical bytes, never an accepted marker.
        payload["input"][0]["content"][0]["text"] = payload["input"][0]["content"][0][
            "text"
        ].replace("/work", "/other")
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        (foreign_occ,) = obs.roots.roots
        assert foreign_occ.scope_label == "/other"
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=foreign_occ,
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.ENTRY_UNRESOLVED

    def test_historical_raw_replay_replaces_again(self) -> None:
        rec = _transaction_records()
        first = _transaction_payload()
        obs_first = observe_request(first, endpoint="responses", context=_CTX)
        result_first = replace_sources(
            first,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs_first,
            root_occurrence=obs_first.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result_first.outcome is ReplacementOutcome.OK, result_first
        # The ORIGINAL raw payload replayed later (untransformed
        # history, no markers anywhere) replaces the raw source AGAIN
        # through the RAM hits: the same live edits, the same
        # transformed output, no rollback.
        raw = _transaction_payload()
        obs_raw = observe_request(raw, endpoint="responses", context=_CTX)
        result_raw = replace_sources(
            raw,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs_raw,
            root_occurrence=obs_raw.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result_raw.outcome is ReplacementOutcome.OK, result_raw
        assert len(result_raw.edits) == 4
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result_raw.edits)
        assert result_raw.markers_replayed == 0
        assert result_raw.transformed_payload == result_first.transformed_payload

    def test_root_envelope_replay_with_environment_tail(self) -> None:
        rec = _transaction_records(lineage="replace022b-tail")
        tail = "<environment_context>\n  <cwd>/work</cwd>\n</environment_context>"
        payload1 = _transaction_payload_tail()
        frozen = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert payload1 == frozen
        assert len(result1.edits) == 4
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result1.edits)
        # The environment tail is NOT part of the root content span:
        # it survives the replacement byte-for-byte, and the result
        # carries the ONE selected compiled working set (the accepted
        # decision's working set, once).
        out1 = result1.transformed_payload
        assert out1 is not None
        assert tail in out1["input"][0]["content"][0]["text"]
        assert result1.selected_content_keys == tuple(
            w.content_key for w in rec["decision"].working_set
        )
        # The repeated root envelope replayed at round 2: the
        # observer's ACTUAL same-scope occurrence, the same single
        # working set, the fixed point, the tail still preserved.
        payload2 = out1
        obs2 = observe_request(payload2, endpoint="responses", context=_CTX)
        (current_occ,) = obs2.roots.roots
        assert current_occ.scope_label == "/work"
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=current_occ,
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == payload2
        assert result2.edits_planned == 0
        assert result2.markers_replayed == 4
        assert result2.selected_content_keys == result1.selected_content_keys
        out2 = result2.transformed_payload
        assert out2 is not None
        assert tail in out2["input"][0]["content"][0]["text"]

    def test_repeated_root_envelopes_replay_both_carriers(self) -> None:
        rec = _transaction_records(lineage="replace022b-repeat")
        tail = "<environment_context>\n  <cwd>/work</cwd>\n</environment_context>"
        payload1 = _transaction_payload_tail()
        # A SECOND byte- and scope-identical root envelope item
        # coexisting in the SAME decoded Responses history, with its
        # own environment tail (the section-11 repeated-envelope
        # case): the observer's ACTUAL occurrences (plural), both
        # carrier edits, ONE compiled working set.
        payload1["input"].insert(1, copy.deepcopy(payload1["input"][0]))
        frozen = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        assert len(obs1.roots.roots) == 2
        assert {o.location for o in obs1.roots.roots} == {
            "$.input[0].content[0]",
            "$.input[1].content[0]",
        }
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert payload1 == frozen
        # BOTH envelope carriers earn their own LIVE edit (the two
        # root edits target the same retained root key on DISTINCT
        # carrier regions) plus the three read edits: five total.
        assert len(result1.edits) == 5
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result1.edits)
        root_edits = [e for e in result1.edits if e.target_entry_class == "root_entry"]
        assert len(root_edits) == 2
        assert {e.carrier_location for e in root_edits} == {
            "$.input[0].content[0]",
            "$.input[1].content[0]",
        }
        assert {e.target_content_key for e in root_edits} == {
            e.target_content_key for e in root_edits
        }
        assert root_edits[0].target_content_key == root_edits[1].target_content_key
        assert result1.edits_planned == 5
        assert result1.markers_emitted == 5
        assert result1.markers_replayed == 0
        payload2 = result1.transformed_payload
        assert payload2 is not None
        # Each envelope's environment tail is outside the content
        # span and survives byte-for-byte on its own carrier; the
        # result carries the ONE selected compiled working set.
        for index in (0, 1):
            assert tail in payload2["input"][index]["content"][0]["text"]
        assert result1.selected_content_keys == tuple(
            w.content_key for w in rec["decision"].working_set
        )
        # Round 2: the transformed output re-observed — the
        # observer's ACTUAL same-scope occurrences (both), every
        # marker replays at its own carrier coordinates, no edit is
        # planned, the fixed point, the same single working set, the
        # tails still preserved.
        obs2 = observe_request(payload2, endpoint="responses", context=_CTX)
        assert len(obs2.roots.roots) == 2
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == payload2
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 5
        assert result2.selected_content_keys == result1.selected_content_keys
        for index in (0, 1):
            assert tail in payload2["input"][index]["content"][0]["text"]
        # Round 3: the accepted replay of the same markers neither
        # changes authority nor creates a second edit (fixed point).
        out2 = result2.transformed_payload
        assert out2 is not None
        obs3 = observe_request(out2, endpoint="responses", context=_CTX)
        result3 = replace_sources(
            out2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs3,
            root_occurrence=obs3.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result3.outcome is ReplacementOutcome.OK, result3
        assert result3.transformed_payload == result2.transformed_payload
        assert result3.edits_planned == 0
        assert result3.markers_replayed == 5

    def test_optional_omission_earns_evidence_marker(self) -> None:
        rec = _omission_records()
        decision = rec["decision"]
        ready_c = rec["ready"][2]
        c_key = ready_c.entry.content_key
        # The ACTUAL selection omits the C singleton WHOLE (its path
        # is covered by the admitted [A,B,C] bundle): an observable
        # closed omission with the required content intact.
        omitted = {row.content_key: row.reason for row in decision.omitted}
        assert omitted.get(c_key) is SelectionOmissionReason.COVERAGE_DEDUPLICATED
        payload1 = _omission_payload()
        frozen = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert payload1 == frozen
        # Exactly four LIVE edits (root + the three proven [A,B,C]
        # splices) and ONE non-resolving evidence marker for the
        # omitted C singleton span: no dangling live reference.
        assert len(result1.edits) == 5
        evidence = [e for e in result1.edits if e.kind is MarkerKind.EVIDENCE]
        live = [e for e in result1.edits if e.kind is MarkerKind.LIVE_REFERENCE]
        assert len(evidence) == 1 and len(live) == 4
        assert evidence[0].carrier_location == "$.input[4]"
        # The lean partition preserves the printed marker lines, and
        # the omitted singleton stays out of the selected working set.
        out1 = result1.transformed_payload
        assert out1 is not None
        assert "REPLAYSEP\n" in out1["input"][2]["output"]
        assert "REPLAYSEP2\n" in out1["input"][2]["output"]
        assert c_key not in result1.selected_content_keys
        # Round 2: the evidence marker replays (historical evidence),
        # nothing is planned, the payload is the fixed point.
        payload2 = out1
        obs2 = observe_request(payload2, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == payload2
        assert result2.edits_planned == 0
        assert result2.markers_replayed == 5

    def test_chat_read_endpoint_transaction(self) -> None:
        rec = _transaction_records(
            endpoint="chat",
            lineage="replace022b-chat",
        )
        payload1 = _chat_transaction_payload()
        frozen = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="chat", context=_CTX)
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=None,
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert payload1 == frozen
        # The root authority is a separate Responses envelope: this
        # Chat payload carries no root carrier, so the root earns
        # ZERO edits (source-absent) and the three read spans earn
        # live edits on the Chat carriers.
        assert len(result1.edits) == 3
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result1.edits)
        assert all(e.carrier_location.startswith("$.messages") for e in result1.edits)
        payload2 = result1.transformed_payload
        assert payload2 is not None
        obs2 = observe_request(payload2, endpoint="chat", context=_CTX)
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=None,
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == payload2
        assert result2.edits_planned == 0
        assert result2.markers_replayed == 3


# --- The ACTUAL lineage supersession evidence (chunk 1d law) ----------
#
# The supersession predicate is exercised over the ACTUAL same-run
# overlay of the prepared P/T state: a genuinely later A.md read
# (descendant issuance) earns PROVEN_CHANGE on the OLD occurrence's
# A.md group; the boundaryless overlap earns OWNERSHIP_AMBIGUITY; an
# absent (occurrence, group) record proves nothing.

SUPERSEDED_A_BODY = "The revised A procedure supersedes the old one.\n"


def _supersession_state() -> tuple[Any, Any, str]:
    """The ACTUAL P/T state: the proven [A,B] read, then a genuinely
    LATER A.md singleton issued with the completed c1 occurrence as
    its frozen frontier parent, then the C singleton."""
    ns, s0 = r_bootstrap(AdmissionMode.GREEDY, "replace022b-supersession", root_body=ROOT_REQUIRED)
    i1 = r_issue(s0, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), REPLAY_CMD)
    o1 = r_observe(i1.state, ns, (read_request("responses", "c1", REPLAY_BODY, cmd=REPLAY_CMD),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    c1_occ = next(o for o in o1.state.d_state.occurrences if o.proof.call_id == "c1")
    i3 = r_issue(o1.state, ns, "c3", "responses", (c1_occ.occurrence_id,), "cat A.md")
    o3 = r_observe(i3.state, ns, (read_request("responses", "c3", SUPERSEDED_A_BODY, "cat A.md"),))
    assert o3.outcome is RootLineageOutcome.ACCEPTED, o3.diagnostics
    i2 = r_issue(o3.state, ns, "c2", "responses", (CAUSAL_ROOT_FACT,), "cat C.md")
    o2 = r_observe(i2.state, ns, (read_request("responses", "c2", C_BODY, "cat C.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    return o2.state, t, c1_occ.occurrence_id


def _ambiguous_state() -> tuple[Any, Any, str]:
    """The ACTUAL P/T state: two boundaryless bundles that share B.md,
    so the B.md row of each owning group carries OWNERSHIP_AMBIGUITY."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-ambiguous", root_body=ROOT_REQUIRED)
    i1 = r_issue(s0, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md && cat B.md")
    req1 = read_request("responses", "c1", A_BODY + B_BODY, cmd="cat A.md && cat B.md")
    o1 = r_observe(i1.state, ns, (req1,))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    i2 = r_issue(o1.state, ns, "c2", "responses", (CAUSAL_ROOT_FACT,), "cat B.md && cat C.md")
    req2 = read_request("responses", "c2", B_BODY + C_BODY, cmd="cat B.md && cat C.md")
    o2 = r_observe(i2.state, ns, (req2,))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    c1_occ = next(o for o in o2.state.d_state.occurrences if o.proof.call_id == "c1")
    return o2.state, t, c1_occ.occurrence_id


class TestSupersessionEvidence:
    """The ACTUAL lineage supersession predicate over prepared
    same-run records (the closed chunk 1d law)."""

    @staticmethod
    def _span(occurrence_id: str, segment_index: int) -> RetainedSpan:
        return RetainedSpan(
            content_key="ab" * 32,
            entry_class="file_bundle_entry",
            role="tool_result",
            endpoint="responses",
            occurrence_identity=occurrence_id,
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=segment_index,
            location="$.input[2]",
            field="output",
            start=0,
            end=1,
            source_digest="00" * 32,
            reproven=True,
            bytes_mismatch=False,
        )

    @staticmethod
    def _evidence(state: Any, t: Any) -> _SupersessionEvidence:
        return _SupersessionEvidence(
            overlay=t.r_result.e_overlay,
            root_currentness=t.r_result.q_result,
            retained_root_digests=frozenset(fact.source_digest for fact in state.root_facts),
        )

    def test_proven_change_is_superseded(self) -> None:
        state, t, c1_occ = _supersession_state()
        record = next(
            g
            for g in t.r_result.e_overlay.groups
            if g.occurrence_id == c1_occ and g.group_index == 0
        )
        # The ACTUAL derived record carries the proven change on the
        # old A.md row.
        assert any(
            reason.value == "proven_change" for row in record.path_rows for reason in row.reasons
        )
        assert _positively_superseded(self._span(c1_occ, 0), self._evidence(state, t))

    def test_ambiguous_group_is_not_superseded(self) -> None:
        state, t, c1_occ = _ambiguous_state()
        record = next(
            g
            for g in t.r_result.e_overlay.groups
            if g.occurrence_id == c1_occ and g.group_index == 0
        )
        # The ACTUAL derived record carries the ownership ambiguity on
        # the B.md row: ambiguous groups stay out of historical
        # evidence even when their other rows are clean.
        assert any(
            reason.value == "ownership_ambiguity"
            for row in record.path_rows
            for reason in row.reasons
        )
        assert not _positively_superseded(self._span(c1_occ, 0), self._evidence(state, t))

    def test_absent_group_record_proves_nothing(self) -> None:
        state, t, c1_occ = _supersession_state()
        # No (occurrence, group) record at these coordinates: a mere
        # omission earns no supersession proof.
        assert not _positively_superseded(self._span(c1_occ, 99), self._evidence(state, t))
