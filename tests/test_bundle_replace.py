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
    EntryClass,
)
from slaif_local_coding.constitution.bundles.bundle_budget import (
    BundleBudgetConfig,
    BundleBudgetPlan,
)
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    UNPROVEN_MEMBER_PROVENANCE_PREFIX,
    unproven_member_paths,
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
    payload_has_marker_candidates,
    replace_sources,
    unsplice_replayed_markers,
    verify_marker,
)
from slaif_local_coding.constitution.bundles.bundle_replace_models import (
    EVIDENCE_MARKER_TAG,
    LIVE_MARKER_TAG,
    MARKER_SUFFIX,
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
from slaif_local_coding.constitution.bundles.currentness_models import (
    CurrentnessReason,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    ExitStatus,
    Limitation,
    OccurrenceKind,
    PathContext,
    ReadOutcome,
    RootOccurrence,
    RootStatus,
    TruncationStatus,
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
    RootSelectionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    RootRegionCurrentnessOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    register_root_region_issuance,
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
    CHAIN_SESSION,
    chain_request,
    poll_arguments,
    read_request,
    running_frame,
    sha256_hex,
    terminal_frame,
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
# The evidence tag carries NO entry content key (the old entry key of a
# superseded original is never reconstructed): the binding slot is the
# empty string, exactly as ``_binding_key`` derives it from the
# expectation's ``content_key=None``.
_MK_EVIDENCE_BINDING_KEY: tuple[str, str, int, int, int, int, str] = (
    MK_ENDPOINT,
    "synthetic-read-1",
    1,
    2,
    0,
    0,
    "",
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
    replayed, _replayed_span = _scan_replayed_markers(
        {(MK_ENDPOINT, MK_LOCATION): carrier}, expectations, binding
    )
    return replayed


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
            {_MK_EVIDENCE_BINDING_KEY: ((span, frozenset({"evidence"})),)},
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


X_BODY = "Off-graph X notes outside the root reach.\n"
X_V2_BODY = "The revised X notes change the off-graph file.\n"
GATE_ROOT = "Follow `A.md` before mutation.\n"
GATE_CMD = "cat A.md && echo 'GATESEP' && cat X.md"
GATE_BODY = A_BODY + "GATESEP\n" + X_BODY


def _off_graph_state() -> tuple[Any, Any, str]:
    """The ACTUAL P/T state: the root reaches ONLY A.md (LEAN); the
    partitioned c1 read covers A.md and the off-graph X.md; genuine
    LATER descendant claims then supersede BOTH — A.md is readmitted
    by its descendant (admitted), X.md is never graph-eligible and
    never admitted (ordinary tool output)."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-offgraph", root_body=GATE_ROOT)
    i1 = r_issue(s0, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), GATE_CMD)
    o1 = r_observe(i1.state, ns, (read_request("responses", "c1", GATE_BODY, cmd=GATE_CMD),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    c1_occ = next(o for o in o1.state.d_state.occurrences if o.proof.call_id == "c1")
    i2 = r_issue(o1.state, ns, "c2", "responses", (c1_occ.occurrence_id,), "cat A.md")
    o2 = r_observe(
        i2.state,
        ns,
        (read_request("responses", "c2", SUPERSEDED_A_BODY, "cat A.md"),),
    )
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    i3 = r_issue(o2.state, ns, "c3", "responses", (c1_occ.occurrence_id,), "cat X.md")
    o3 = r_observe(
        i3.state,
        ns,
        (read_request("responses", "c3", X_V2_BODY, "cat X.md"),),
    )
    assert o3.outcome is RootLineageOutcome.ACCEPTED, o3.diagnostics
    t = derive_root_region_admission(o3.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    # Lean admits the root and the readmitted A.md singleton ONLY:
    # the off-graph X.md never earns a row in the reverse index.
    admission = t.admission
    assert admission is not None
    assert [_represented(t, e) for e in admission.entries] == [("A.md",)]
    admitted = {row.path for row in admission.path_associations if row.content_keys}
    assert "A.md" in admitted and "X.md" not in admitted
    return o3.state, t, c1_occ.occurrence_id


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
        admission = t.admission
        assert admission is not None
        return _SupersessionEvidence(
            overlay=t.r_result.e_overlay,
            root_currentness=t.r_result.q_result,
            authoritative_root_digests=frozenset(
                fact.source_digest for fact in state.root_facts if fact.authority
            ),
            admitted_paths=frozenset(
                row.path for row in admission.path_associations if row.content_keys
            ),
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

    def test_proven_change_on_unadmitted_path_is_not_superseded(self) -> None:
        state, t, c1_occ = _off_graph_state()
        evidence = self._evidence(state, t)
        # The ACTUAL derived records: the partitioned c1 read owns
        # TWO groups in segment order — the A.md segment (group 0)
        # and the off-graph X.md segment (group 1).  BOTH group rows
        # carry the proven change (genuine later descendant claims),
        # so the D occurrence plus PROVEN_CHANGE alone would remove
        # the X.md tool output ...
        a_group = next(
            g
            for g in t.r_result.e_overlay.groups
            if g.occurrence_id == c1_occ and g.group_index == 0
        )
        x_group = next(
            g
            for g in t.r_result.e_overlay.groups
            if g.occurrence_id == c1_occ and g.group_index == 1
        )
        assert a_group.members == ("A.md",)
        assert x_group.members == ("X.md",)
        for group in (a_group, x_group):
            assert any(
                reason is CurrentnessReason.PROVEN_CHANGE
                for row in group.path_rows
                for reason in row.reasons
            )
        # ... but only the path the PREPARED admission actually
        # represents (A.md, readmitted by the descendant) has
        # retained admission provenance.  The off-group X.md is
        # ordinary tool output: the exact-group eligibility gate
        # refuses the evidence splice for it ...
        assert not _positively_superseded(self._span(c1_occ, 1), evidence)
        # ... while the admitted A.md original stays positively
        # superseded.
        assert _positively_superseded(self._span(c1_occ, 0), evidence)


# ---------------------------------------------------------------------------
# The v1->v2 old-raw / evidence-replay / stale-live transaction (saved
# chunk 1h): the retained-D nonroot join.  A singleton A.md that is
# genuinely superseded by a later descendant read: the OLD v1 occurrence
# is ABSENT from the current admission, and the prepared T result's
# SAME-RUN E overlay group record positively proves the supersession, so
# the old original earns a NON-RESOLVING EVIDENCE marker tied to its
# original namespace and exact occurrence/source digest (the old entry
# key is never reconstructed).  The new v2 original earns a LIVE marker;
# an old v1 LIVE token in the old original's carrier is a stale live
# reference that ALWAYS refuses (no scan carve-out, no rollback).
# ---------------------------------------------------------------------------

ROOT_V1V2 = "Follow `A.md` before mutation.\n"


def _v1v2_records() -> dict[str, Any]:
    """The ACTUAL P/T fixture for the singleton v1->v2 supersession: the
    rooted bootstrap, the genuinely issued c1 read of A.md (v1), the
    genuinely LATER c2 read of A.md (v2) issued with the completed c1
    occurrence as its frozen frontier parent, admitted lean.

    The current admission carries ONLY the c2 singleton as the A.md
    entry: the c1 occurrence is ABSENT from the current admission, and
    its same-run E overlay group record carries the proven change on the
    A.md row (a genuinely later claim with a KNOWN different digest)."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-v1v2", root_body=ROOT_V1V2)
    i1 = r_issue(s0, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md")
    o1 = r_observe(i1.state, ns, (read_request("responses", "c1", A_BODY, "cat A.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    c1_occ = next(o for o in o1.state.d_state.occurrences if o.call_id == "c1")
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    # ---- The retained PREVIOUS v1 prepared stage -------------------
    # Derive the actual prepared context as it stood AFTER the v1 read
    # (before the v2 descendant): the A.md entry is the c1 singleton,
    # with its real entry content key and real compiled index.  A real
    # v1 transaction over the v1 raw payload emits the REAL v1 LIVE
    # marker for the c1 span — the genuine stale live reference the
    # final round must refuse.
    t1 = derive_root_region_admission(o1.state, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    admission1 = t1.admission
    assert admission1 is not None
    entry_a1 = _entry_for(t1, "A.md")
    assert all(w.occurrence_id == c1_occ.occurrence_id for w in entry_a1.witnesses)
    root_index = _root_index(
        admission1.root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
            _dep("C.md", "P2", 30, "background"),
        ),
    )
    index_a1 = _file_index(
        entry_a1,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure-v1",
        statement="The original A procedure.",
        location="A.md",
    )
    snapshot_v1 = RamStateSnapshot(
        namespace=ns, state=o1.state, result=t1, revision=o1.state.revision, epoch=1, owned_bytes=0
    )
    proof_v1 = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-v1"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot_v1,
    )
    ready_root_v1 = _ready(t1, admission1.root_entry, root_index, ("A.md", "B.md", "C.md"))
    ready_a1 = _ready(t1, entry_a1, index_a1, ())
    decision_v1 = select_working_set(ready_root_v1, (ready_a1,), plan)
    assert decision_v1.outcome is SelectionOutcome.OK
    v1_payload = {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_V1V2),
            _ch_exec_call("c1", "cat A.md"),
            _ch_out_item("c1", _ch_frame(A_BODY)),
        ],
    }
    obs_v1 = observe_request(v1_payload, endpoint="responses", context=_CTX)
    result_v1 = replace_sources(
        v1_payload,
        proof=proof_v1,
        current_snapshot=snapshot_v1,
        ready_entries=(ready_root_v1, ready_a1),
        decision=decision_v1,
        observation=obs_v1,
        root_occurrence=obs_v1.roots.roots[0],
        key=MARKER_KEY,
        max_text_chars=100_000,
    )
    assert result_v1.outcome is ReplacementOutcome.OK, result_v1
    v1_c1_edits = [e for e in result_v1.edits if e.carrier_location == "$.input[2]"]
    assert len(v1_c1_edits) == 1
    (v1_c1_edit,) = v1_c1_edits
    assert v1_c1_edit.kind is MarkerKind.LIVE_REFERENCE
    assert v1_c1_edit.target_content_key == entry_a1.content_key
    out_v1 = result_v1.transformed_payload
    assert out_v1 is not None
    # The frame's source span runs to the end of the frame: the
    # emitted marker is the exact rendered tail.
    v1_marker = out_v1["input"][2]["output"][v1_c1_edit.start :]
    assert v1_marker.startswith(LIVE_MARKER_TAG)
    assert v1_marker.endswith("]")
    i2 = r_issue(o1.state, ns, "c2", "responses", (c1_occ.occurrence_id,), "cat A.md")
    o2 = r_observe(i2.state, ns, (read_request("responses", "c2", SUPERSEDED_A_BODY, "cat A.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    r_result = t.r_result
    assert r_result is not None
    admission = t.admission
    assert admission is not None
    overlay = r_result.e_overlay
    assert overlay is not None
    # The same-run E overlay group record of the OLD occurrence carries
    # the proven change on the A.md row (the ACTUAL supersession proof;
    # the group index is the occurrence-local segment index).
    record = next(g for g in overlay.groups if g.occurrence_id == c1_occ.occurrence_id)
    assert record.group_index == 0
    assert any(
        reason.value == "proven_change" for row in record.path_rows for reason in row.reasons
    )
    # The current admission carries the v2 singleton only: the old
    # occurrence is ABSENT from the current admission (the whole point
    # of the retained-D nonroot join).
    entry_a2 = _entry_for(t, "A.md")
    assert entry_a2.witnesses
    assert all(w.occurrence_id != c1_occ.occurrence_id for w in entry_a2.witnesses)
    root_entry = admission.root_entry
    # The root source is unchanged between the two prepared stages:
    # the root entry keeps the same content key, so the compiled root
    # index (built from the v1 stage's identical root entry) serves
    # both ready sets.
    assert root_entry.content_key == admission1.root_entry.content_key
    index_a2 = _file_index(
        entry_a2,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The revised A procedure.",
        location="A.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o2.state, result=t, revision=o2.state.revision, epoch=1, owned_bytes=0
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
    ready_a2 = _ready(t, entry_a2, index_a2, ())
    decision = select_working_set(ready_root, (ready_a2,), plan)
    assert decision.outcome is SelectionOutcome.OK
    return {
        "snapshot": snapshot,
        "proof": proof,
        "ready": (ready_root, ready_a2),
        "decision": decision,
        "root_entry": root_entry,
        "entry_a2": entry_a2,
        "c1_occ": c1_occ,
        "v1_marker": v1_marker,
    }


def _v1v2_payload() -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope, the
    old c1 read pair (A.md v1) and the newer c2 read pair (A.md v2),
    plus an ordinary assistant message the transaction must preserve
    byte-for-byte (ordinary non-admitted output keeps its role)."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_V1V2),
            _ch_exec_call("c1", "cat A.md"),
            _ch_out_item("c1", _ch_frame(A_BODY)),
            _ch_exec_call("c2", "cat A.md"),
            _ch_out_item("c2", _ch_frame(SUPERSEDED_A_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Continuing with the mutation."}],
            },
        ],
    }


class TestTransactionV1V2Supersession:
    """The ACTUAL replace_sources entry point over the singleton
    v1->v2 supersession fixture: the old raw payload earns the root
    LIVE, the v2 LIVE and the non-resolving EVIDENCE edit (three
    rounds total: old raw, evidence replay fixed point, and the stale
    live refusal)."""

    def test_old_raw_evidence_replay_stale_live(self) -> None:
        rec = _v1v2_records()
        snapshot = rec["snapshot"]
        root_key = rec["root_entry"].content_key
        a2_key = rec["entry_a2"].content_key
        c1 = rec["c1_occ"]
        piece = c1.proof.pieces[0]
        segment = c1.proof.segments[0]
        assert piece.call_id == "c1"
        assert segment.digest == sha256_hex(A_BODY)

        # ---- Round 1: the honest OLD RAW payload -------------------
        payload1 = _v1v2_payload()
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
        # Exactly three edits: the root envelope LIVE, the v2 A.md LIVE,
        # the old v1 A.md NON-RESOLVING EVIDENCE (the old entry key is
        # never reconstructed).
        assert len(result1.edits) == 3
        assert result1.edits_planned == 3
        assert result1.edits_committed == 3
        assert result1.markers_emitted == 3
        assert result1.markers_replayed == 0
        root_edits = [e for e in result1.edits if e.carrier_location == "$.input[0].content[0]"]
        c1_edits = [e for e in result1.edits if e.carrier_location == "$.input[2]"]
        c2_edits = [e for e in result1.edits if e.carrier_location == "$.input[4]"]
        assert len(root_edits) == 1 and len(c1_edits) == 1 and len(c2_edits) == 1
        (root_edit,) = root_edits
        (c1_edit,) = c1_edits
        (c2_edit,) = c2_edits
        assert root_edit.kind is MarkerKind.LIVE_REFERENCE
        assert root_edit.target_content_key == root_key
        assert c2_edit.kind is MarkerKind.LIVE_REFERENCE
        assert c2_edit.target_content_key == a2_key
        assert c1_edit.kind is MarkerKind.EVIDENCE
        assert c1_edit.target_compiled_digest is None
        assert c1_edit.source_digest == sha256_hex(A_BODY)
        # The selected compiled pairing is the working set (root + v2
        # A); the old v1 content is not a selected entry.
        assert result1.selected_content_keys == tuple(
            row.content_key for row in rec["decision"].working_set
        )
        assert set(result1.selected_content_keys) == {root_key, a2_key}
        out1 = result1.transformed_payload
        assert out1 is not None
        # The emitted evidence marker is the EXACT re-derived tag:
        # original namespace + occurrence + source digest + segment
        # association, and NO entry content key.
        expected_ev = derive_evidence_tag(
            MARKER_KEY,
            namespace_key=snapshot.namespace.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=c1.occurrence_id,
            endpoint="responses",
            call_id=piece.call_id,
            call_position=piece.call_position,
            result_position=piece.result_position,
            piece_index=piece.piece_index,
            segment_index=0,
            source_digest=sha256_hex(A_BODY),
        )
        assert expected_ev.content_key is None
        original_c1_text = _ch_frame(A_BODY)
        c1_text = out1["input"][2]["output"]
        # The edit coordinates address the ORIGINAL source span (the
        # rendered marker has its own length, longer than the raw
        # span): the marker renders at the splice start, the prefix is
        # unchanged, and the suffix after the original span end is
        # preserved byte-for-byte (the frame wrapper stays intact).
        marker_len = len(expected_ev.marker)
        assert c1_text[c1_edit.start : c1_edit.start + marker_len] == expected_ev.marker
        assert c1_text[: c1_edit.start] == original_c1_text[: c1_edit.start]
        assert c1_text[c1_edit.start + marker_len :] == original_c1_text[c1_edit.end :]
        c2_text = out1["input"][4]["output"]
        assert c2_text[c2_edit.start : c2_edit.end + 10].startswith(LIVE_MARKER_TAG)
        root_text = out1["input"][0]["content"][0]["text"]
        assert root_text[root_edit.start : root_edit.end + 10].startswith(LIVE_MARKER_TAG)
        # The ordinary assistant message (non-admitted output) is
        # preserved byte-for-byte.
        assert out1["input"][5] == frozen["input"][5]

        # ---- Round 2: the already-transformed historical replay -----
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # The transformed history replays all three markers at their
        # current coordinates to the fixed point: no second edit, no
        # rollback, the non-resolving evidence marker neither changes
        # its authority nor resolves to stale compiled text.
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.transformed_payload == out1
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 3

        # ---- Round 3: a STALE LIVE token in the old carrier ---------
        # The GENUINE stale live reference: the marker ACTUALLY emitted
        # by the previous real v1 prepared transaction (its real v1
        # entry content key and compiled digest, valid at that stage).
        # That entry has now left the accepted selection: the tag
        # cannot re-derive against ANY current authority, so the
        # accepted-replay gate refuses it — the stale live reference
        # ALWAYS refuses (no scan carve-out, no rollback).
        payload3 = _v1v2_payload()
        payload3["input"][2]["output"] = _ch_frame(rec["v1_marker"])
        frozen3 = copy.deepcopy(payload3)
        obs3 = observe_request(payload3, endpoint="responses", context=_CTX)
        result3 = replace_sources(
            payload3,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs3,
            root_occurrence=obs3.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # The stale live reference ALWAYS refuses all-or-nothing (no
        # scan carve-out): no transformed payload, no partial edits,
        # the input is never mutated.
        assert result3.outcome is ReplacementOutcome.MARKER_INVALID, result3
        assert result3.http_status == 409
        assert result3.transformed_payload is None
        assert result3.edits == ()
        assert payload3 == frozen3


# ---------------------------------------------------------------------------
# 022-b saved chunk 1i (authority gate): the order's evidence law is
# gated on ACTUAL authority from the ready same-run P/Q lineage.  A
# retained root original that was never authoritative — a complete but
# UNISSUED read, retained as UNPROVEN source and never selectable — is
# insufficient for positive supersession: the envelope carrying the
# unissued digest earns NO evidence splice and the transaction refuses
# all-or-nothing.
# ---------------------------------------------------------------------------


def _unissued_gate_records() -> dict[str, Any]:
    """The ACTUAL P/T fixture for the authority gate: the rooted
    bootstrap on the OLD root, a complete but NEVER ISSUED AGENTS.md
    read carrying the NEW root (retained as UNPROVEN source —
    issued/authority False — and never selectable), plus the issued
    A.md read — admitted lean.

    The OLD bootstrap anchor remains the selected governing root
    (envelope provenance); the unissued NEW digest is retained but
    carries no ACTUAL authority."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-unissued-gate", root_body=READROOT_OLD)
    # The NEW root read is observed complete but is NEVER issued: it
    # is retained as UNPROVEN source and can never be selected.
    o1 = r_observe(s0, ns, (read_request("responses", "r1", READROOT_NEW, "cat AGENTS.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    read_fact = next(f for f in o1.state.root_facts if f.source_digest == sha256_hex(READROOT_NEW))
    assert read_fact.issued is False and read_fact.authority is False
    i2 = r_issue(o1.state, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md")
    o2 = r_observe(i2.state, ns, (read_request("responses", "c1", A_BODY, "cat A.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    r_result = t.r_result
    assert r_result is not None
    q_result = r_result.q_result
    assert q_result is not None
    assert q_result.outcome is RootRegionCurrentnessOutcome.READY
    p_selection = q_result.p_selection
    assert p_selection is not None
    assert p_selection.outcome is RootSelectionOutcome.OK
    # The UNISSUED read is never selected: the OLD anchor governs.
    assert p_selection.selected_source_digest == sha256_hex(READROOT_OLD)
    admission = t.admission
    assert admission is not None
    root_entry = admission.root_entry
    assert root_entry.root_digest == sha256_hex(READROOT_OLD)
    root_source = root_entry.root_source
    assert root_source is not None
    assert root_source.kind == "envelope"
    # Only the A.md file entry is admitted: while the root comes from
    # the anchor, the root-bearing AGENTS.md group never supplies root
    # text, so its read earns no FILE entry of its own.
    assert len(admission.entries) == 1
    entry_a = _entry_for(t, "A.md")
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o2.state, result=t, revision=o2.state.revision, epoch=1, owned_bytes=0
    )
    proof = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-unissued-gate"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot,
    )
    ready_root = _ready(t, root_entry, root_index, ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, index_a, ())
    decision = select_working_set(ready_root, (ready_a,), plan)
    assert decision.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    return {
        "ns": ns,
        "snapshot": snapshot,
        "proof": proof,
        "root_entry": root_entry,
        "entry_a": entry_a,
        "ready": (ready_root, ready_a),
        "decision": decision,
    }


class TestHistoricalAnchorAuthorityGate:
    """A retained UNISSUED root digest earns no evidence marker: the
    actual P/Q lineage gate fails closed (no tag, no splice, no
    partial edit) while the transaction refuses all-or-nothing and
    never mutates the input."""

    def test_unissued_retained_root_earns_no_evidence(self) -> None:
        rec = _unissued_gate_records()
        # The honest decoded request: the governing OLD envelope, the
        # envelope carrying the UNISSUED NEW original, the read
        # carriers and the assistant message.
        payload = {
            "model": "synthetic-model",
            "input": [
                _ch_root_item(READROOT_OLD),
                _ch_root_item(READROOT_NEW),
                _ch_exec_call("r1", "cat AGENTS.md"),
                _ch_out_item("r1", _ch_frame(READROOT_NEW)),
                _ch_exec_call("c1", "cat A.md"),
                _ch_out_item("c1", _ch_frame(A_BODY)),
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Proceeding."}],
                },
            ],
        }
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.location for o in obs.roots.roots] == [
            "$.input[0].content[0]",
            "$.input[1].content[0]",
        ]
        assert [o.digest for o in obs.roots.roots] == [
            sha256_hex(READROOT_OLD),
            sha256_hex(READROOT_NEW),
        ]
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # A retained UNISSUED digest proves no supersession: the
        # envelope carrying it is a recognized root field the
        # transaction cannot honestly replace — all-or-nothing
        # refusal, no evidence marker, no partial edits.
        assert result.outcome is ReplacementOutcome.SPAN_MISMATCH, result
        assert result.http_status == 409
        assert result.transformed_payload is None
        assert result.edits == ()
        assert result.edits_planned == 0
        assert result.markers_emitted == 0
        assert payload == frozen


# ---------------------------------------------------------------------------
# 022-b saved chunk 1j (native multi-piece): a native process read
# (initial EXEC + causally associated poll) of a CRLF/Unicode source
# through the ACTUAL transaction: each piece earns its own LIVE splice
# on its OWN carrier, the per-piece current coordinates come from the
# CURRENT process proof on the CURRENT decoded string (the retained
# coordinates stay the piece identity), the wrappers and the CRLF/
# Unicode outside the edits are preserved byte-for-byte, the transformed
# replay is a fixed point (every present tag occupies its full proved
# current splice), and a moved or residue-bearing tag refuses
# all-or-nothing.
# ---------------------------------------------------------------------------

A_NATIVE_PENDING = "Synthetic a content.\r\n"
A_NATIVE_TAIL = "ünïcode ✓ tail\r\n"
A_NATIVE = A_NATIVE_PENDING + A_NATIVE_TAIL


def _native_records() -> dict[str, Any]:
    """The ACTUAL P/T fixture for the native multi-piece read: the
    rooted bootstrap, the issued native exec of ``cat A.md`` with its
    running frame (the CRLF piece), the causally associated write_stdin
    poll and its terminal frame (the Unicode piece) — admitted lean.

    The A.md entry's single segment carries the two retained piece
    spans (one per piece carrier); the piece call/result positions are
    the chain-relative structural positions."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-native", root_body=ROOT_REQUIRED)
    i1 = r_issue(s0, ns, "n1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md")
    pend = r_observe(i1.state, ns, (chain_request("responses", "n1", A_NATIVE_PENDING),))
    assert pend.outcome is RootLineageOutcome.ACCEPTED, pend.diagnostics
    pi = register_root_region_issuance(
        pend.state,
        ns,
        "n1p",
        "responses",
        "write_stdin",
        poll_arguments(CHAIN_SESSION),
        (CAUSAL_ROOT_FACT,),
        pend.state.revision,
    )
    assert pi.outcome is RootLineageOutcome.ACCEPTED, pi.diagnostics
    full = r_observe(
        pi.state,
        ns,
        (chain_request("responses", "n1", A_NATIVE_PENDING, "n1p", terminal_frame(A_NATIVE_TAIL)),),
    )
    assert full.outcome is RootLineageOutcome.ACCEPTED, full.diagnostics
    t = derive_root_region_admission(full.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    admission = t.admission
    assert admission is not None
    entry_a = _entry_for(t, "A.md")
    n1_occ = next(o for o in full.state.d_state.occurrences if o.call_id == "n1")
    # The retained proof carries the two pieces, one per carrier.
    assert [p.piece_index for p in n1_occ.proof.pieces] == [0, 1]
    assert n1_occ.proof.pieces[0].call_id == "n1"
    assert n1_occ.proof.pieces[1].call_id == "n1p"
    assert n1_occ.proof.pieces[0].call_position == 0
    assert n1_occ.proof.pieces[0].result_position == 1
    assert n1_occ.proof.pieces[1].call_position == 2
    assert n1_occ.proof.pieces[1].result_position == 3
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_entry = admission.root_entry
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns,
        state=full.state,
        result=t,
        revision=full.state.revision,
        epoch=1,
        owned_bytes=0,
    )
    proof = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-native"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot,
    )
    ready_root = _ready(t, root_entry, root_index, ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, index_a, ())
    decision = select_working_set(ready_root, (ready_a,), plan)
    assert decision.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    return {
        "ns": ns,
        "snapshot": snapshot,
        "proof": proof,
        "root_entry": root_entry,
        "entry_a": entry_a,
        "n1_occ": n1_occ,
        "root_index": root_index,
        "index_a": index_a,
        "ready": (ready_root, ready_a),
        "decision": decision,
    }


def _native_payload() -> dict[str, Any]:
    """The honest decoded request: the root envelope, the native exec
    chain (running frame, poll call, terminal frame) and the assistant
    message (the CRLF/Unicode that lives OUTSIDE the edits)."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_REQUIRED),
            exec_call("n1", "cat A.md"),
            out_item("n1", running_frame(A_NATIVE_PENDING, CHAIN_SESSION)),
            {
                "type": "function_call",
                "call_id": "n1p",
                "name": "write_stdin",
                "arguments": poll_arguments(CHAIN_SESSION),
            },
            out_item("n1p", terminal_frame(A_NATIVE_TAIL)),
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": "Proceeding.\r\nÜnïcode ✓ check.\n",
                    }
                ],
            },
        ],
    }


class TestTransactionNativeMultiPiece:
    """The ACTUAL replace_sources entry point over the native
    multi-piece (initial-EXEC + poll) CRLF/Unicode read: per-piece
    splices from the CURRENT process proof, fixed-point replay, and
    moved/residue tag refusal."""

    def test_native_multi_piece_crlf_unicode_transaction(self) -> None:
        rec = _native_records()
        ns = rec["ns"]
        root_key = rec["root_entry"].content_key
        a_key = rec["entry_a"].content_key
        n1_occ = rec["n1_occ"]
        root_index = rec["root_index"]
        index_a = rec["index_a"]

        # ---- Round 1: the honest raw native payload ------------------
        payload = _native_payload()
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.location for o in obs.roots.roots] == ["$.input[0].content[0]"]
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        assert result.selected_content_keys == (root_key, a_key)
        # EXACTLY three edits: the root envelope splice and the TWO
        # native piece splices (initial EXEC piece, poll piece), each
        # on its OWN carrier.
        assert len(result.edits) == 3
        root_edit, exec_edit, poll_edit = sorted(result.edits, key=lambda e: e.carrier_location)
        assert root_edit.carrier_location == "$.input[0].content[0]"
        assert root_edit.field == "text"
        assert root_edit.kind is MarkerKind.LIVE_REFERENCE
        assert root_edit.target_entry_class == "root_entry"
        assert root_edit.target_content_key == root_key
        assert root_edit.target_compiled_digest == root_index.compile_key
        assert root_edit.source_digest == sha256_hex(ROOT_REQUIRED)
        assert root_edit.occurrence_identity == root_key
        assert (root_edit.start, root_edit.end) == (51, 51 + len(ROOT_REQUIRED))
        assert exec_edit.carrier_location == "$.input[2]"
        assert exec_edit.field == "output"
        assert exec_edit.kind is MarkerKind.LIVE_REFERENCE
        assert exec_edit.target_entry_class == "file_bundle_entry"
        assert exec_edit.target_content_key == a_key
        assert exec_edit.target_compiled_digest == index_a.compile_key
        assert exec_edit.source_digest == sha256_hex(A_NATIVE)
        assert exec_edit.occurrence_identity == n1_occ.occurrence_id
        assert (exec_edit.start, exec_edit.end) == (112, 134)
        assert poll_edit.carrier_location == "$.input[4]"
        assert (poll_edit.start, poll_edit.end) == (102, 118)
        assert result.edits_planned == 3
        assert result.edits_committed == 3
        assert result.markers_emitted == 3
        assert result.markers_replayed == 0
        assert result.carriers_touched == 3
        assert result.chars_replaced == len(ROOT_REQUIRED) + len(A_NATIVE_PENDING) + len(
            A_NATIVE_TAIL
        )
        out1 = result.transformed_payload
        assert out1 is not None
        # The input payload is never mutated.
        assert payload == frozen
        # The emitted markers are the EXACT re-derived tags: the root
        # envelope (root-source identity) and each piece under its OWN
        # retained piece identity (the chain-relative call/result
        # positions, the piece index, the occurrence).
        root_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=root_key,
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(ROOT_REQUIRED),
        )
        exec_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=n1_occ.occurrence_id,
            endpoint="responses",
            call_id="n1",
            call_position=0,
            result_position=1,
            piece_index=0,
            segment_index=0,
            entry_class="file_bundle_entry",
            content_key=a_key,
            compiled_digest=index_a.compile_key,
            source_digest=sha256_hex(A_NATIVE),
        )
        poll_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=n1_occ.occurrence_id,
            endpoint="responses",
            call_id="n1p",
            call_position=2,
            result_position=3,
            piece_index=1,
            segment_index=0,
            entry_class="file_bundle_entry",
            content_key=a_key,
            compiled_digest=index_a.compile_key,
            source_digest=sha256_hex(A_NATIVE),
        )
        f1 = frozen["input"]
        o1 = out1["input"]
        # Root envelope: the wrapper prefix and the environment tail
        # are preserved byte-for-byte around the splice.
        root_text = o1[0]["content"][0]["text"]
        root_orig = f1[0]["content"][0]["text"]
        assert root_text[:51] == root_orig[:51]
        assert root_text[51 : 51 + len(root_marker)] == root_marker
        assert root_text[51 + len(root_marker) :] == root_orig[51 + len(ROOT_REQUIRED) :]
        # Exec piece (running frame): the wrapper (headers, delimiters)
        # is preserved byte-for-byte around the splice.
        e1, e0 = o1[2]["output"], f1[2]["output"]
        assert e1[:112] == e0[:112]
        assert e1[112 : 112 + len(exec_marker)] == exec_marker
        assert e1[112 + len(exec_marker) :] == e0[112 + len(A_NATIVE_PENDING) :]
        # Poll piece (terminal frame): same wrapper law.
        p1, p0 = o1[4]["output"], f1[4]["output"]
        assert p1[:102] == p0[:102]
        assert p1[102 : 102 + len(poll_marker)] == poll_marker
        assert p1[102 + len(poll_marker) :] == p0[102 + len(A_NATIVE_TAIL) :]
        # The exec call, the poll call and the assistant message (the
        # CRLF/Unicode OUTSIDE the edits) are byte-identical.
        assert o1[1] == f1[1]
        assert o1[3] == f1[3]
        assert o1[5] == f1[5]
        assert "\r\n" in o1[5]["content"][0]["text"]

        # ---- Round 2: the transformed replay is a fixed point -------
        # Every present tag occupies its FULL proved current splice:
        # the per-piece positions are re-derived from the CURRENT
        # process proof on the CURRENT decoded string.
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out1,
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
        assert result2.edits == ()
        assert result2.edits_planned == 0
        assert result2.markers_replayed == 3
        assert result2.transformed_payload == out1

        # ---- Round 3: a MOVED tag (the poll marker shifted three
        # characters inside its body) ALWAYS refuses all-or-nothing.
        out3 = copy.deepcopy(out1)
        proc2 = next(pr for pr in obs2.processes if pr.exec_call_id == "n1")
        poll_piece = next(poll.piece for poll in proc2.polls if poll.poll_call_id == "n1p")
        s, e = poll_piece.char_span.start, poll_piece.char_span.end
        item3 = out3["input"][4]
        item3["output"] = item3["output"][:s] + "xyz" + item3["output"][s:e]
        frozen3 = copy.deepcopy(out3)
        obs3 = observe_request(out3, endpoint="responses", context=_CTX)
        result3 = replace_sources(
            out3,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs3,
            root_occurrence=obs3.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result3.outcome is ReplacementOutcome.MARKER_INVALID, result3
        assert result3.http_status == 409
        assert result3.transformed_payload is None
        assert result3.edits == ()
        assert out3 == frozen3

        # ---- Round 4: a RESIDUE-BEARING tag (one extra byte inside
        # the body after the exec marker) ALWAYS refuses all-or-
        # nothing: the tag no longer occupies its full proved current
        # splice.
        out4 = copy.deepcopy(out1)
        exec_piece = next(
            pr for pr in proc2.pieces if pr.result_location == proc2.initial_result_location
        )
        e4 = exec_piece.char_span.end
        item4 = out4["input"][2]
        item4["output"] = item4["output"][:e4] + "Z" + item4["output"][e4:]
        frozen4 = copy.deepcopy(out4)
        obs4 = observe_request(out4, endpoint="responses", context=_CTX)
        result4 = replace_sources(
            out4,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs4,
            root_occurrence=obs4.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result4.outcome is ReplacementOutcome.MARKER_INVALID, result4
        assert result4.http_status == 409
        assert result4.transformed_payload is None
        assert result4.edits == ()
        assert out4 == frozen4


# ---------------------------------------------------------------------------
# 022-b saved chunk 1i (read-root dispatch): the governing root selected
# through a READ — the T root row's ``witnesses`` stay empty (the read
# provenance lives in the resolved source), so the root join dispatches
# on ``root_entry.root_source.kind``: the root's OWN retained original
# witness is the splice, its carrier stays a tool result, and the FILE
# join skips that exact (occurrence, segment) coordinate so the same
# root-region bytes can never earn a second edit.  The historical
# envelope (the retained OLD root original present as a payload anchor)
# is a separate concern: it is not a joined carrier and stays untouched.
# ---------------------------------------------------------------------------

READROOT_OLD = "Follow `A.md` before mutation.\n"
READROOT_NEW = "Follow `A.md` and `B.md` before mutation.\n"


def _readroot_records() -> dict[str, Any]:
    """The ACTUAL P/T fixture for the governing read-root: the rooted
    bootstrap on the OLD root, the genuinely issued whole-singleton
    AGENTS.md read carrying the NEW root (the governing read
    provenance), plus the issued A.md read — admitted lean.

    The NEW root is selected; the OLD root fact stays retained (the
    historical anchor).  The AGENTS.md read is ALSO a FILE entry whose
    sole witness is the root read coordinate (the shared root-region
    bytes); the actual selection omits it as coverage-deduplicated."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-readroot", root_body=READROOT_OLD)
    i1 = r_issue(s0, ns, "r1", "responses", (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    o1 = r_observe(i1.state, ns, (read_request("responses", "r1", READROOT_NEW, "cat AGENTS.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    i2 = r_issue(o1.state, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md")
    o2 = r_observe(i2.state, ns, (read_request("responses", "c1", A_BODY, "cat A.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    r_result = t.r_result
    assert r_result is not None
    q_result = r_result.q_result
    assert q_result is not None
    assert q_result.outcome is RootRegionCurrentnessOutcome.READY
    p_selection = q_result.p_selection
    assert p_selection is not None
    assert p_selection.outcome is RootSelectionOutcome.OK
    assert p_selection.selected_source_digest == sha256_hex(READROOT_NEW)
    # Both root originals are ACTUAL retained root facts: the bootstrap
    # envelope (OLD) and the governing read (NEW).
    fact_digests = {f.source_digest for f in o2.state.root_facts}
    assert fact_digests == {sha256_hex(READROOT_OLD), sha256_hex(READROOT_NEW)}
    admission = t.admission
    assert admission is not None
    root_entry = admission.root_entry
    # The T law: the root row's witnesses stay EMPTY on every
    # provenance; the read provenance lives in the resolved source.
    assert root_entry.witnesses == ()
    root_source = root_entry.root_source
    assert root_source is not None
    assert root_source.kind == "read"
    r1_occ = next(o for o in o2.state.d_state.occurrences if o.call_id == "r1")
    root_occurrence = root_source.occurrence
    assert root_occurrence is not None
    assert root_occurrence is r1_occ
    assert root_source.proof is not None
    assert root_source.proof is r1_occ.proof
    entry_a = _entry_for(t, "A.md")
    agents_candidates = [
        e
        for e in admission.entries
        if any(w.occurrence_id == r1_occ.occurrence_id for w in e.witnesses)
    ]
    assert len(agents_candidates) == 1
    entry_agents = agents_candidates[0]
    assert all(w.occurrence_id == r1_occ.occurrence_id for w in entry_agents.witnesses)
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
    )
    index_agents = _file_index(
        entry_agents,
        (),
        config,
        tokenizer,
        plan,
        rule_id="root-reference",
        statement="The root reference.",
        location="AGENTS.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o2.state, result=t, revision=o2.state.revision, epoch=1, owned_bytes=0
    )
    proof = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-readroot"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot,
    )
    ready_root = _ready(t, root_entry, root_index, ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, index_a, ())
    ready_agents = _ready(t, entry_agents, index_agents, ())
    decision = select_working_set(ready_root, (ready_agents, ready_a), plan)
    assert decision.outcome is SelectionOutcome.OK
    # The ACTUAL selection covers the root itself: the AGENTS.md file
    # entry (the same bytes under a file member) is omitted as
    # coverage-deduplicated, leaving every required content in the
    # working set.
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    assert [(o.content_key, o.reason) for o in decision.omitted] == [
        (entry_agents.content_key, SelectionOmissionReason.COVERAGE_DEDUPLICATED)
    ]
    return {
        "ns": ns,
        "snapshot": snapshot,
        "proof": proof,
        "root_entry": root_entry,
        "entry_a": entry_a,
        "entry_agents": entry_agents,
        "r1_occ": r1_occ,
        "root_index": root_index,
        "ready": (ready_root, ready_agents, ready_a),
        "decision": decision,
    }


def _readroot_payload() -> dict[str, Any]:
    """The honest payload: the CURRENT root envelope, the HISTORICAL
    old-root envelope (the retained OLD original, still an accepted
    same-scope root occurrence), the two read pairs and the assistant
    message."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(READROOT_NEW),
            _ch_root_item(READROOT_OLD),
            _ch_exec_call("r1", "cat AGENTS.md"),
            _ch_out_item("r1", _ch_frame(READROOT_NEW)),
            _ch_exec_call("c1", "cat A.md"),
            _ch_out_item("c1", _ch_frame(A_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


class TestTransactionReadRootGoverning:
    """The ACTUAL replace_sources entry point over the governing
    read-root fixture: the root's OWN retained read witness earns the
    single root LIVE splice (a tool result), the A read earns its own
    LIVE splice, the historical old-root envelope anchor earns its
    non-resolving EVIDENCE splice (the order's evidence law), the
    current envelope stays separate, and a stale live form on the old
    anchor refuses."""

    def test_read_root_governing_carrier_with_historical_anchor(self) -> None:
        rec = _readroot_records()
        ns = rec["ns"]
        snapshot = rec["snapshot"]
        root_key = rec["root_entry"].content_key
        a_key = rec["entry_a"].content_key
        r1_occ = rec["r1_occ"]
        root_index = rec["root_index"]

        # ---- Round 1: the honest old raw payload -------------------
        payload1 = _readroot_payload()
        frozen1 = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        # The observer accepts BOTH envelopes (current + historical
        # anchor) as same-scope root occurrences.
        assert [o.location for o in obs1.roots.roots] == [
            "$.input[0].content[0]",
            "$.input[1].content[0]",
        ]
        assert [o.digest for o in obs1.roots.roots] == [
            sha256_hex(READROOT_NEW),
            sha256_hex(READROOT_OLD),
        ]
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert result1.http_status is None
        assert result1.selected_content_keys == (root_key, a_key)
        # EXACTLY three edits: the root splice on the READ carrier (a
        # tool result, the root's own occurrence), the A splice, and
        # the non-resolving EVIDENCE splice on the historical
        # old-root envelope anchor.
        assert len(result1.edits) == 3
        old_edit, root_edit, a_edit = sorted(result1.edits, key=lambda e: e.carrier_location)
        assert old_edit.carrier_location == "$.input[1].content[0]"
        assert old_edit.field == "text"
        assert old_edit.kind is MarkerKind.EVIDENCE
        assert old_edit.target_entry_class == "root_entry"
        assert old_edit.target_content_key == root_key
        assert old_edit.target_compiled_digest is None
        assert old_edit.source_digest == sha256_hex(READROOT_OLD)
        # The evidence identity is the OLD source's own digest in
        # the trusted workspace (immutable across later root
        # changes — a second genuine root change re-derives the same
        # tag), never the current root entry key.
        assert old_edit.occurrence_identity == sha256_hex(READROOT_OLD)
        assert (old_edit.start, old_edit.end) == (51, 51 + len(READROOT_OLD))
        assert root_edit.carrier_location == "$.input[3]"
        assert root_edit.field == "output"
        assert root_edit.kind is MarkerKind.LIVE_REFERENCE
        assert root_edit.target_entry_class == "root_entry"
        assert root_edit.target_content_key == root_key
        assert root_edit.target_compiled_digest == root_index.compile_key
        assert root_edit.source_digest == sha256_hex(READROOT_NEW)
        assert root_edit.occurrence_identity == r1_occ.occurrence_id
        assert (root_edit.start, root_edit.end) == (81, 81 + len(READROOT_NEW))
        assert a_edit.carrier_location == "$.input[5]"
        assert a_edit.kind is MarkerKind.LIVE_REFERENCE
        assert a_edit.target_entry_class == "file_bundle_entry"
        assert a_edit.target_content_key == a_key
        assert a_edit.source_digest == sha256_hex(A_BODY)
        assert result1.edits_planned == 3
        assert result1.edits_committed == 3
        assert result1.markers_emitted == 3
        assert result1.markers_replayed == 0
        assert result1.carriers_touched == 3
        assert result1.chars_replaced == len(READROOT_NEW) + len(A_BODY) + len(READROOT_OLD)
        out1 = result1.transformed_payload
        assert out1 is not None
        # The input payload is never mutated.
        assert payload1 == frozen1
        # The emitted root marker is the EXACT re-derived live tag for
        # the root's own read splice (tool-result role, the read
        # occurrence identity, the root entry class and content key,
        # the selected root source digest).
        expected_root_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=r1_occ.occurrence_id,
            endpoint="responses",
            call_id="r1",
            call_position=0,
            result_position=1,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(READROOT_NEW),
        )
        r1_text = out1["input"][3]["output"]
        frame1 = _ch_frame(READROOT_NEW)
        assert r1_text[:81] == frame1[:81]
        assert r1_text[81 : 81 + len(expected_root_marker)] == expected_root_marker
        assert r1_text[81 + len(expected_root_marker) :] == frame1[81 + len(READROOT_NEW) :]
        # The HISTORICAL old-root anchor earns the EXACT re-derived
        # non-resolving evidence marker (root-envelope role, the root
        # source identity, the OLD source digest; no content key —
        # the old entry key is never reconstructed), with the
        # envelope delimiters and tail preserved around the splice.
        expected_old_marker = make_evidence_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=sha256_hex(READROOT_OLD),
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            source_digest=sha256_hex(READROOT_OLD),
        )
        old_text = out1["input"][1]["content"][0]["text"]
        old_orig = _ch_root_item(READROOT_OLD)["content"][0]["text"]
        assert old_text[:51] == old_orig[:51]
        assert old_text[51 : 51 + len(expected_old_marker)] == expected_old_marker
        assert old_text[51 + len(expected_old_marker) :] == old_orig[51 + len(READROOT_OLD) :]
        # The CURRENT envelope of the governing digest stays separate
        # and byte-identical (the read splice is the root's only live
        # edit), as do both exec carriers and the assistant message.
        assert out1["input"][0] == payload1["input"][0]
        assert out1["input"][2] == payload1["input"][2]
        assert out1["input"][4] == payload1["input"][4]
        assert out1["input"][6] == payload1["input"][6]

        # ---- Round 2: the transformed replay is a fixed point -----
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out1,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.edits == ()
        assert result2.edits_planned == 0
        # ALL THREE markers replay at their own coordinates: the two
        # live splices and the old anchor's non-resolving evidence
        # marker (an accepted replay changes no authority).
        assert result2.markers_replayed == 3
        assert result2.transformed_payload == out1

        # ---- Round 3: a STALE LIVE form on the old anchor --------
        # The live-format marker bound to the OLD root original (the
        # exact tag a prior stage emitted when the OLD root was the
        # selected governing root) is a stale live reference: it
        # verifies against the retained-entry expectation, but that
        # entry has left the accepted selection — it ALWAYS refuses
        # (no replay, no carve-out).
        payload3 = copy.deepcopy(out1)
        stale_live = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=root_key,
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(READROOT_OLD),
        )
        old_body = payload3["input"][1]["content"][0]["text"]
        payload3["input"][1]["content"][0]["text"] = (
            old_body[:51] + stale_live + old_body[51 + len(expected_old_marker) :]
        )
        frozen3 = copy.deepcopy(payload3)
        obs3 = observe_request(payload3, endpoint="responses", context=_CTX)
        result3 = replace_sources(
            payload3,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs3,
            root_occurrence=obs3.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # The stale live form ALWAYS refuses all-or-nothing: no
        # transformed payload, no partial edits, the input is never
        # mutated.
        assert result3.outcome is ReplacementOutcome.MARKER_INVALID, result3
        assert result3.http_status == 409
        assert result3.transformed_payload is None
        assert result3.edits == ()
        assert payload3 == frozen3


# ---------------------------------------------------------------------------
# 022-b saved chunk 1k (shared entry + lean preservation): the
# reference fixture pattern
# tests/test_current_admission.py::test_f_isolated_b_different_proof_coordinates
# on the ACTUAL P/T path.  The root reaches only B.md; the proven
# partitioned [A,B] read puts B at segment 1 of its own proof and the
# identical standalone B read uses segment 0 -- ONE canonical B entry
# retaining BOTH original witnesses at their OWN distinct coordinates.
# Lean admits no A row (the root never reaches A.md), so the partition
# carrier must preserve the unadmitted A source and the printed
# delimiter byte-for-byte around the single B splice.  The original
# payload earns exactly THREE live edits (the root envelope and the two
# B splices: one compiled working set, two occurrence identities, two
# carriers), and the transformed output replays all three to a fixed
# point.
# ---------------------------------------------------------------------------

SHARED_ROOT = "Follow `B.md` before mutation.\n"
SHARED_CMD = "cat A.md && echo 'SHSEP' && cat B.md"
SHARED_BODY = A_BODY + "SHSEP\n" + B_BODY


def _shared_records() -> dict[str, Any]:
    """The ACTUAL P/T shared-entry fixture: the standalone B read is
    issued FIRST (the B entry's first compatible original proof), then
    the proven partitioned [A,B] read (the B entry's second witness).
    The root declares B.md ONLY, so LEAN admits the root and the ONE
    B entry; A.md never earns a row."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022b-shared", root_body=SHARED_ROOT)
    i1 = r_issue(s0, ns, "c2", "responses", (CAUSAL_ROOT_FACT,), "cat B.md")
    assert i1.outcome is RootLineageOutcome.ACCEPTED, i1.diagnostics
    o1 = r_observe(i1.state, ns, (read_request("responses", "c2", B_BODY, "cat B.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    i2 = r_issue(o1.state, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), SHARED_CMD)
    assert i2.outcome is RootLineageOutcome.ACCEPTED, i2.diagnostics
    o2 = r_observe(i2.state, ns, (read_request("responses", "c1", SHARED_BODY, cmd=SHARED_CMD),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    t = derive_root_region_admission(o2.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    admission = t.admission
    assert admission is not None
    # Lean: exactly ONE file entry, the B entry; A.md never earns a row.
    assert [_represented(t, e) for e in admission.entries] == [("B.md",)]
    entry_b = _entry_for(t, "B.md")
    c1_occ = next(o for o in o2.state.d_state.occurrences if o.call_id == "c1")
    c2_occ = next(o for o in o2.state.d_state.occurrences if o.call_id == "c2")
    # Shared entry, DISTINCT original coordinates: the standalone
    # witness at segment (0,) of its own proof, the partitioned
    # witness at segment (1,) of its own proof, in canonical
    # coordinate order, each the ACTUAL retained D occurrence.
    assert [(w.occurrence_id, w.segment_indices) for w in entry_b.witnesses] == [
        (c2_occ.occurrence_id, (0,)),
        (c1_occ.occurrence_id, (1,)),
    ]
    # FIRST compatible original proof = the standalone read; the
    # entry member origin is fully proven (no unproven member path).
    assert entry_b.proof.source_text == B_BODY
    assert unproven_member_paths(entry_b) == ()
    # The partitioned B segment is the SAME source bytes (the proven
    # per-member digest), which is what interns both witnesses under
    # the ONE canonical B key.
    c1_segment_b = c1_occ.proof.segments[1]
    assert c1_segment_b.digest == sha256_hex(B_BODY)
    assert c2_occ.proof.segments[0].digest == sha256_hex(B_BODY)

    root_entry = admission.root_entry
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (_dep("B.md", "P1", 90, "immediate"),),
    )
    index_b = _file_index(
        entry_b,
        (),
        config,
        tokenizer,
        plan,
        rule_id="b-procedure",
        statement="The B procedure.",
        location="B.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o2.state, result=t, revision=o2.state.revision, epoch=1, owned_bytes=0
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
    ready_root = _ready(t, root_entry, root_index, ("B.md",))
    ready_b = _ready(t, entry_b, index_b, ())
    decision = select_working_set(ready_root, (ready_b,), plan)
    assert decision.outcome is SelectionOutcome.OK
    # The root and the shared B entry are BOTH required (the root's
    # P1 binding closure is covered by the proven B origin).
    assert [row.required for row in decision.working_set] == [True, True]
    assert [row.entry_class for row in decision.working_set] == [
        EntryClass.ROOT_ENTRY,
        EntryClass.FILE_BUNDLE_ENTRY,
    ]
    return {
        "snapshot": snapshot,
        "proof": proof,
        "ready": (ready_root, ready_b),
        "decision": decision,
        "root_entry": root_entry,
        "entry_b": entry_b,
        "root_index": root_index,
        "index_b": index_b,
        "occ_split": c1_occ,
        "occ_standalone": c2_occ,
    }


def _shared_payload() -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope plus
    the two complete read pairs (the partitioned [A,B] read and the
    standalone B read) exactly as the P/T fixture observed them, and
    the ordinary assistant tail."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(SHARED_ROOT),
            _ch_exec_call("c1", SHARED_CMD),
            _ch_out_item("c1", _ch_frame(SHARED_BODY)),
            _ch_exec_call("c2", "cat B.md"),
            _ch_out_item("c2", _ch_frame(B_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


class TestTransactionSharedEntry:
    """Shared-entry distinct original coordinates + lean preservation
    through the ACTUAL replace_sources entry point (objective 022-b):
    one canonical B entry with two witnesses at distinct original
    coordinates, both spliced to the ONE compiled working set, while
    the unadmitted A source and its printed delimiter stay
    byte-for-byte in the partition carrier."""

    def test_shared_entry_lean_preservation_transaction(self) -> None:
        rec = _shared_records()
        ns = rec["snapshot"].namespace
        root_key = rec["root_entry"].content_key
        b_key = rec["entry_b"].content_key
        root_index = rec["root_index"]
        index_b = rec["index_b"]
        split_occ = rec["occ_split"]
        stand_occ = rec["occ_standalone"]
        split_piece = split_occ.proof.pieces[0]
        stand_piece = stand_occ.proof.pieces[0]
        assert split_piece.call_id == "c1"
        assert stand_piece.call_id == "c2"

        # ---- Round 1: the honest raw shared-entry payload ----------
        payload = _shared_payload()
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.location for o in obs.roots.roots] == ["$.input[0].content[0]"]
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        # The input payload is never mutated.
        assert payload == frozen
        # Exactly THREE live edits: the root envelope splice and the
        # TWO B splices on their OWN carriers (the shared entry is
        # spliced TWICE, once per retained original coordinate).
        assert result.edits_planned == 3
        assert result.edits_committed == 3
        assert result.markers_emitted == 3
        assert result.markers_replayed == 0
        assert result.carriers_touched == 3
        assert len(result.edits) == 3
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result.edits)
        by_loc = {e.carrier_location: e for e in result.edits}
        assert set(by_loc) == {"$.input[0].content[0]", "$.input[2]", "$.input[4]"}
        root_edit = by_loc["$.input[0].content[0]"]
        split_edit = by_loc["$.input[2]"]
        stand_edit = by_loc["$.input[4]"]
        # Root: the exact content span (the 017 envelope law excludes
        # the delimiters), the retained root key, its own compiled
        # digest.
        assert root_edit.field == "text"
        assert root_edit.target_entry_class == "root_entry"
        assert root_edit.target_content_key == root_key
        assert root_edit.occurrence_identity == root_key
        assert root_edit.target_compiled_digest == root_index.compile_key
        assert root_edit.source_digest == sha256_hex(SHARED_ROOT)
        assert (root_edit.start, root_edit.end) == (51, 51 + len(SHARED_ROOT))
        # Both B splices: the ONE shared content key and the SAME
        # compiled digest (the ONE selected working set) ...
        assert split_edit.field == "output"
        assert stand_edit.field == "output"
        assert split_edit.target_entry_class == "file_bundle_entry"
        assert stand_edit.target_entry_class == "file_bundle_entry"
        assert split_edit.target_content_key == b_key
        assert stand_edit.target_content_key == b_key
        assert split_edit.target_compiled_digest == index_b.compile_key
        assert stand_edit.target_compiled_digest == index_b.compile_key
        assert split_edit.source_digest == sha256_hex(B_BODY)
        assert stand_edit.source_digest == sha256_hex(B_BODY)
        # ... but DISTINCT occurrence identities: each splice is its
        # OWN retained original witness (the ACTUAL D occurrence IDs).
        assert split_edit.occurrence_identity == split_occ.occurrence_id
        assert stand_edit.occurrence_identity == stand_occ.occurrence_id
        assert split_edit.occurrence_identity != stand_edit.occurrence_identity
        # The exact original coordinates: the partition B piece at
        # segment 1 of its own proof, the standalone B at segment 0.
        assert (split_edit.start, split_edit.end) == (123, 123 + len(B_BODY))
        assert (stand_edit.start, stand_edit.end) == (81, 81 + len(B_BODY))
        # The selected compiled pairing is the working set (root + B)
        # and nothing is missing from the binding closure.
        assert result.selected_content_keys == (root_key, b_key)
        assert result.missing_bindings == ()
        assert len(result.compiled_blocks) == 2
        out = result.transformed_payload
        assert out is not None
        # The emitted markers are the EXACT re-derived tags: the root
        # envelope (root-source identity) and each B splice under its
        # OWN retained piece/segment identity (the chain-relative
        # call/result positions from the retained piece, the witness
        # segment index, the witness occurrence).
        root_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=root_key,
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(SHARED_ROOT),
        )
        split_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=split_occ.occurrence_id,
            endpoint="responses",
            call_id=split_piece.call_id,
            call_position=split_piece.call_position,
            result_position=split_piece.result_position,
            piece_index=split_piece.piece_index,
            segment_index=1,
            entry_class="file_bundle_entry",
            content_key=b_key,
            compiled_digest=index_b.compile_key,
            source_digest=sha256_hex(B_BODY),
        )
        stand_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=stand_occ.occurrence_id,
            endpoint="responses",
            call_id=stand_piece.call_id,
            call_position=stand_piece.call_position,
            result_position=stand_piece.result_position,
            piece_index=stand_piece.piece_index,
            segment_index=0,
            entry_class="file_bundle_entry",
            content_key=b_key,
            compiled_digest=index_b.compile_key,
            source_digest=sha256_hex(B_BODY),
        )
        f0, o0 = frozen["input"], out["input"]
        # Root envelope: the wrapper prefix is preserved byte-for-byte
        # around the splice; the suffix after the original span end is
        # untouched.
        root_orig, root_new = f0[0]["content"][0]["text"], o0[0]["content"][0]["text"]
        assert root_new[:51] == root_orig[:51]
        assert root_new[51 : 51 + len(root_marker)] == root_marker
        assert root_new[51 + len(root_marker) :] == root_orig[51 + len(SHARED_ROOT) :]
        # Partition carrier: the LEAN preservation law -- the frame
        # wrapper, the UNADMITTED A source and the printed delimiter
        # are all preserved byte-for-byte before the B splice, and the
        # marker renders at the splice start with its own length.
        split_orig, split_new = f0[2]["output"], o0[2]["output"]
        assert split_new[:123] == split_orig[:123]
        assert split_new[:123].endswith(A_BODY + "SHSEP\n")
        assert split_new[123 : 123 + len(split_marker)] == split_marker
        assert split_new[123 + len(split_marker) :] == split_orig[123 + len(B_BODY) :]
        assert A_BODY in split_new
        assert "SHSEP\n" in split_new
        # Standalone carrier: the wrapper prefix is preserved around
        # the splice too.
        stand_orig, stand_new = f0[4]["output"], o0[4]["output"]
        assert stand_new[:81] == stand_orig[:81]
        assert stand_new[81 : 81 + len(stand_marker)] == stand_marker
        assert stand_new[81 + len(stand_marker) :] == stand_orig[81 + len(B_BODY) :]
        # The two exec calls and the ordinary assistant tail (the
        # non-admitted output) are byte-identical.
        assert o0[1] == f0[1]
        assert o0[3] == f0[3]
        assert o0[5] == f0[5]

        # ---- Round 2: the transformed replay is a fixed point ------
        # Every present tag occupies its FULL proved current splice
        # (the replay scan re-verifies start and end); no second edit,
        # no rollback.
        obs2 = observe_request(out, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out,
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
        assert result2.transformed_payload == out
        assert result2.edits == ()
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 3
        assert result2.selected_content_keys == (root_key, b_key)


# ---------------------------------------------------------------------------
# 022-b eligible-source constraint on the historical D join: the E
# overlay can carry positively changed paths that were NEVER ADMITTED.
# A retained D occurrence plus PROVEN_CHANGE alone must not remove
# unrelated (off-graph) tool output: the exact group's member paths
# must have retained admission provenance in the PREPARED admission's
# reverse member index under the approved lean/greedy rules.  The
# admitted A.md original of the same partition still earns its
# non-resolving evidence marker; the off-graph X.md output stays
# byte-for-byte.
# ---------------------------------------------------------------------------


def _off_graph_records() -> dict[str, Any]:
    """The prepared transaction inputs over the ACTUAL off-graph
    supersession state (the root reaches only A.md; X.md is never
    admitted)."""
    state, t, _c1_id = _off_graph_state()
    ns = t.ns
    admission = t.admission
    root_entry = admission.root_entry
    entry_a = _entry_for(t, "A.md")
    c1_occ = next(o for o in state.d_state.occurrences if o.proof.call_id == "c1")
    c2_occ = next(o for o in state.d_state.occurrences if o.proof.call_id == "c2")
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P1", 90, "immediate"),),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
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
    ready_root = _ready(t, root_entry, root_index, ("A.md",))
    ready_a = _ready(t, entry_a, index_a, ())
    decision = select_working_set(ready_root, (ready_a,), plan)
    assert decision.outcome is SelectionOutcome.OK
    return {
        "snapshot": snapshot,
        "proof": proof,
        "ready": (ready_root, ready_a),
        "decision": decision,
        "root_entry": root_entry,
        "entry_a": entry_a,
        "root_index": root_index,
        "index_a": index_a,
        "c1_occ": c1_occ,
        "c2_occ": c2_occ,
    }


def _off_graph_payload() -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope plus
    the partitioned [A, X] read, the readmitted A.md singleton and the
    off-graph X.md singleton, exactly as the P/T fixture observed
    them, and the ordinary assistant tail."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(GATE_ROOT),
            _ch_exec_call("c1", GATE_CMD),
            _ch_out_item("c1", _ch_frame(GATE_BODY)),
            _ch_exec_call("c2", "cat A.md"),
            _ch_out_item("c2", _ch_frame(SUPERSEDED_A_BODY)),
            _ch_exec_call("c3", "cat X.md"),
            _ch_out_item("c3", _ch_frame(X_V2_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


class TestTransactionOffGraphSupersession:
    """The eligible-source constraint through the ACTUAL
    replace_sources entry point (objective 022-b): the off-group
    proven change keeps the X.md tool output byte-for-byte while the
    admitted A.md original earns its non-resolving evidence marker."""

    def test_unadmitted_proven_change_keeps_tool_output(self) -> None:
        rec = _off_graph_records()
        ns = rec["snapshot"].namespace
        root_key = rec["root_entry"].content_key
        a_key = rec["entry_a"].content_key
        root_index = rec["root_index"]
        index_a = rec["index_a"]
        c1_occ = rec["c1_occ"]
        c2_occ = rec["c2_occ"]

        # ---- Round 1: the honest raw off-graph payload -------------
        payload = _off_graph_payload()
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.location for o in obs.roots.roots] == ["$.input[0].content[0]"]
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        assert payload == frozen
        # Exactly THREE edits: the root envelope LIVE, the readmitted
        # A.md LIVE, and the OLD admitted A.md original's
        # non-resolving EVIDENCE marker.  The off-graph X.md output
        # earns NO edit (no entry, no retained admission provenance).
        assert result.edits_planned == 3
        assert result.edits_committed == 3
        assert result.markers_emitted == 3
        assert result.markers_replayed == 0
        assert len(result.edits) == 3
        by_loc = {e.carrier_location: e for e in result.edits}
        assert set(by_loc) == {"$.input[0].content[0]", "$.input[2]", "$.input[4]"}
        root_edit = by_loc["$.input[0].content[0]"]
        a2_edit = by_loc["$.input[4]"]
        a1_edit = by_loc["$.input[2]"]
        assert root_edit.kind is MarkerKind.LIVE_REFERENCE
        assert root_edit.target_content_key == root_key
        assert root_edit.target_compiled_digest == root_index.compile_key
        assert root_edit.source_digest == sha256_hex(GATE_ROOT)
        assert (root_edit.start, root_edit.end) == (51, 51 + len(GATE_ROOT))
        assert a2_edit.kind is MarkerKind.LIVE_REFERENCE
        assert a2_edit.target_content_key == a_key
        assert a2_edit.occurrence_identity == c2_occ.occurrence_id
        assert a2_edit.target_compiled_digest == index_a.compile_key
        assert a2_edit.source_digest == sha256_hex(SUPERSEDED_A_BODY)
        # The OLD A.md original: non-resolving EVIDENCE, the old entry
        # key never reconstructed (the content key is the retained
        # segment's own source digest), NO compiled digest.
        assert a1_edit.kind is MarkerKind.EVIDENCE
        assert a1_edit.occurrence_identity == c1_occ.occurrence_id
        assert a1_edit.target_compiled_digest is None
        assert a1_edit.source_digest == sha256_hex(A_BODY)
        assert (a1_edit.start, a1_edit.end) == (81, 81 + len(A_BODY))
        # The selected compiled pairing is the working set (root +
        # readmitted A); the off-graph X content is not a selected
        # entry.
        assert result.selected_content_keys == (root_key, a_key)
        assert result.missing_bindings == ()
        assert len(result.compiled_blocks) == 2
        out = result.transformed_payload
        assert out is not None
        # The exact re-derived evidence tag for the OLD A.md original
        # (original namespace + occurrence + source digest + segment
        # association, NO entry content key).
        a1_piece = c1_occ.proof.pieces[0]
        expected_ev = derive_evidence_tag(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=c1_occ.occurrence_id,
            endpoint="responses",
            call_id=a1_piece.call_id,
            call_position=a1_piece.call_position,
            result_position=a1_piece.result_position,
            piece_index=a1_piece.piece_index,
            segment_index=0,
            source_digest=sha256_hex(A_BODY),
        )
        # The exact re-derived live tag for the root envelope
        # (root-source identity).
        root_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=root_key,
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(GATE_ROOT),
        )
        f0, o0 = frozen["input"], out["input"]
        # Root envelope: the wrapper prefix preserved around the
        # splice, the exact marker at the splice start, and the
        # suffix after the original span end untouched.
        root_orig, root_new = f0[0]["content"][0]["text"], o0[0]["content"][0]["text"]
        assert root_new[:51] == root_orig[:51]
        assert root_new[51 : 51 + len(root_marker)] == root_marker
        assert root_new[51 + len(root_marker) :] == root_orig[51 + len(GATE_ROOT) :]
        # Partition carrier: the frame wrapper preserved before the
        # OLD A.md splice, the exact marker at the splice start, and
        # the ENTIRE suffix after the original A.md span end -- the
        # printed delimiter AND the off-graph X.md output --
        # preserved byte-for-byte (the eligible-source constraint).
        c1_orig, c1_new = f0[2]["output"], o0[2]["output"]
        assert c1_new[:81] == c1_orig[:81]
        assert c1_new[81 : 81 + len(expected_ev.marker)] == expected_ev.marker
        assert c1_new[81 + len(expected_ev.marker) :] == c1_orig[81 + len(A_BODY) :]
        assert "GATESEP\n" in c1_new
        assert X_BODY in c1_new
        assert A_BODY not in c1_new
        # The off-graph X.md singleton carrier is byte-identical
        # (never admitted, never spliced).
        assert o0[6] == f0[6]
        assert o0[5] == f0[5]
        assert o0[7] == f0[7]
        assert o0[1] == f0[1]
        assert o0[3] == f0[3]

        # ---- Round 2: the transformed replay is a fixed point ------
        obs2 = observe_request(out, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out,
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
        assert result2.transformed_payload == out
        assert result2.edits == ()
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 3
        assert result2.selected_content_keys == (root_key, a_key)


# ---------------------------------------------------------------------------
# 022-b boundaryless whole bundle: the earned all-cat read
# ``cat A.md B.md`` (NO internal member boundary) is admitted under
# GREEDY as ONE whole-bundle entry with unproven per-member origin.
# The selection carries it as OPTIONAL BACKGROUND provenance (never
# required, never binding coverage: the root's P1 A.md binding stays
# MISSING with its exact guidance), and the transaction splices the
# WHOLE bundle content as ONE span on the read carrier; the honest
# boundaryless provenance line stays in the carried compiled block.
# ---------------------------------------------------------------------------

BOUNDARYLESS_CMD = "cat A.md B.md"
BOUNDARYLESS_BODY = A_BODY + B_BODY


def _boundaryless_records() -> dict[str, Any]:
    """The ACTUAL P/T boundaryless whole-bundle fixture: one earned
    all-cat read of A.md and B.md with NO internal boundary,
    admitted under GREEDY as the ONE whole-bundle entry (unproven
    per-member origin)."""
    ns, s0 = r_bootstrap(AdmissionMode.GREEDY, "replace022b-boundaryless", root_body=ROOT_REQUIRED)
    i1 = r_issue(s0, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), BOUNDARYLESS_CMD)
    assert i1.outcome is RootLineageOutcome.ACCEPTED, i1.diagnostics
    o1 = r_observe(
        i1.state,
        ns,
        (read_request("responses", "c1", BOUNDARYLESS_BODY, cmd=BOUNDARYLESS_CMD),),
    )
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    t = derive_root_region_admission(o1.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    admission = t.admission
    assert admission is not None
    # GREEDY admits the ONE whole-bundle entry for the boundaryless
    # read; BOTH member paths are represented by the SAME content key
    # (a whole-bundle digest, never labeled as each member's hash).
    file_entries = [e for e in admission.entries if e.entry_class is EntryClass.FILE_BUNDLE_ENTRY]
    assert len(file_entries) == 1
    entry_ab = file_entries[0]
    assert _represented(t, entry_ab) == ("A.md", "B.md")
    assert len(entry_ab.witnesses) == 1
    assert entry_ab.witnesses[0].segment_indices == (0,)
    assert entry_ab.admitted_segments == (0,)
    c1_occ = next(o for o in o1.state.d_state.occurrences if o.call_id == "c1")
    assert entry_ab.witnesses[0].occurrence_id == c1_occ.occurrence_id
    # The retained proof is ONE boundaryless segment covering BOTH
    # member positions: it proves no per-member origin.
    assert len(c1_occ.proof.segments) == 1
    assert c1_occ.proof.segments[0].member_positions == (0, 1)
    assert c1_occ.proof.segments[0].digest is not None
    assert unproven_member_paths(entry_ab) == ("A.md", "B.md")
    a_row = next(row for row in admission.path_associations if row.path == "A.md")
    b_row = next(row for row in admission.path_associations if row.path == "B.md")
    assert set(a_row.content_keys) == set(b_row.content_keys) == {entry_ab.content_key}

    root_entry = admission.root_entry
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
            _dep("C.md", "P2", 30, "background"),
        ),
    )
    index_ab = _file_index(
        entry_ab,
        (),
        config,
        tokenizer,
        plan,
        rule_id="ab-procedure",
        statement="The boundaryless AB procedure.",
        location="",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o1.state, result=t, revision=o1.state.revision, epoch=1, owned_bytes=0
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
    ready_ab = _ready(t, entry_ab, index_ab, (), origin_proven=False)
    decision = select_working_set(ready_root, (ready_ab,), plan)
    assert decision.outcome is SelectionOutcome.OK
    # The root is required; the boundaryless bundle is OPTIONAL
    # BACKGROUND (unproven member origin is never classified
    # required), and the root's P1 A.md binding stays MISSING with
    # its exact acquisition guidance (an uncertain attribution never
    # substitutes for usable required content).
    assert [row.required for row in decision.working_set] == [True, False]
    assert [row.entry_class for row in decision.working_set] == [
        EntryClass.ROOT_ENTRY,
        EntryClass.FILE_BUNDLE_ENTRY,
    ]
    assert [b.path for b in decision.missing_bindings] == ["A.md"]
    return {
        "snapshot": snapshot,
        "proof": proof,
        "ready": (ready_root, ready_ab),
        "decision": decision,
        "root_entry": root_entry,
        "entry_ab": entry_ab,
        "root_index": root_index,
        "index_ab": index_ab,
        "c1_occ": c1_occ,
    }


def _boundaryless_payload() -> dict[str, Any]:
    """One decoded Responses request: the automatic root envelope plus
    the boundaryless whole-bundle read exactly as the P/T fixture
    observed it, and the ordinary assistant tail."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(ROOT_REQUIRED),
            _ch_exec_call("c1", BOUNDARYLESS_CMD),
            _ch_out_item("c1", _ch_frame(BOUNDARYLESS_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


class TestTransactionBoundarylessWholeBundle:
    """The boundaryless whole bundle through the ACTUAL
    replace_sources entry point (objective 022-b): ONE span for the
    whole bundle content, optional background provenance, the root's
    missing P1 binding carried, honest provenance line in the
    compiled block, fixed-point replay."""

    def test_boundaryless_whole_bundle_background_splice(self) -> None:
        rec = _boundaryless_records()
        ns = rec["snapshot"].namespace
        root_key = rec["root_entry"].content_key
        ab_key = rec["entry_ab"].content_key
        root_index = rec["root_index"]
        index_ab = rec["index_ab"]
        c1_occ = rec["c1_occ"]

        # ---- Round 1: the honest raw boundaryless payload ----------
        payload = _boundaryless_payload()
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.location for o in obs.roots.roots] == ["$.input[0].content[0]"]
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        assert payload == frozen
        # Exactly TWO live edits: the root envelope splice and the
        # WHOLE bundle content as ONE span (no internal member
        # boundary exists in the retained proof).
        assert result.edits_planned == 2
        assert result.edits_committed == 2
        assert result.markers_emitted == 2
        assert result.markers_replayed == 0
        assert len(result.edits) == 2
        assert all(e.kind is MarkerKind.LIVE_REFERENCE for e in result.edits)
        root_edit, ab_edit = sorted(result.edits, key=lambda e: e.carrier_location)
        assert root_edit.carrier_location == "$.input[0].content[0]"
        assert root_edit.target_content_key == root_key
        assert root_edit.target_compiled_digest == root_index.compile_key
        assert root_edit.source_digest == sha256_hex(ROOT_REQUIRED)
        assert (root_edit.start, root_edit.end) == (51, 51 + len(ROOT_REQUIRED))
        assert ab_edit.carrier_location == "$.input[2]"
        assert ab_edit.target_entry_class == "file_bundle_entry"
        assert ab_edit.target_content_key == ab_key
        assert ab_edit.occurrence_identity == c1_occ.occurrence_id
        assert ab_edit.target_compiled_digest == index_ab.compile_key
        # The span's source digest is the WHOLE boundaryless segment
        # digest (never labeled as each member's hash).
        assert ab_edit.source_digest == c1_occ.proof.segments[0].digest
        assert (ab_edit.start, ab_edit.end) == (81, 81 + len(BOUNDARYLESS_BODY))
        # The selected compiled pairing is the working set (root +
        # background bundle); the exact missing-binding guidance for
        # the root's P1 A.md is CARRIED in the same result.
        assert result.selected_content_keys == (root_key, ab_key)
        assert [b.path for b in result.missing_bindings] == ["A.md"]
        assert len(result.compiled_blocks) == 2
        # The honest boundaryless provenance line stays in the
        # carried compiled block (the unknown mixed origin is
        # emitted, never hidden).
        assert result.compiled_blocks[1].endswith(
            "\n" + UNPROVEN_MEMBER_PROVENANCE_PREFIX + "A.md,B.md"
        )
        out = result.transformed_payload
        assert out is not None
        # The exact re-derived tags: the root envelope and the whole
        # bundle under its own occurrence/segment identity.
        root_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="root_envelope",
            occurrence_identity=root_key,
            endpoint="responses",
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(ROOT_REQUIRED),
        )
        ab_piece = c1_occ.proof.pieces[0]
        assert ab_piece.call_id == "c1"
        ab_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=c1_occ.occurrence_id,
            endpoint="responses",
            call_id=ab_piece.call_id,
            call_position=ab_piece.call_position,
            result_position=ab_piece.result_position,
            piece_index=ab_piece.piece_index,
            segment_index=0,
            entry_class="file_bundle_entry",
            content_key=ab_key,
            compiled_digest=index_ab.compile_key,
            source_digest=c1_occ.proof.segments[0].digest,
        )
        f0, o0 = frozen["input"], out["input"]
        # Root envelope: the wrapper prefix preserved around the
        # splice; the suffix after the original span end untouched.
        root_orig, root_new = f0[0]["content"][0]["text"], o0[0]["content"][0]["text"]
        assert root_new[:51] == root_orig[:51]
        assert root_new[51 : 51 + len(root_marker)] == root_marker
        assert root_new[51 + len(root_marker) :] == root_orig[51 + len(ROOT_REQUIRED) :]
        # Bundle carrier: the frame wrapper preserved before the
        # splice; the WHOLE bundle content replaced by the ONE
        # marker; nothing after the original span end.
        ab_orig, ab_new = f0[2]["output"], o0[2]["output"]
        assert ab_new[:81] == ab_orig[:81]
        assert ab_new[81 : 81 + len(ab_marker)] == ab_marker
        assert ab_new[81 + len(ab_marker) :] == ab_orig[81 + len(BOUNDARYLESS_BODY) :]
        # The exec call and the ordinary assistant tail are
        # byte-identical.
        assert o0[1] == f0[1]
        assert o0[3] == f0[3]

        # ---- Round 2: the transformed replay is a fixed point ------
        obs2 = observe_request(out, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out,
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
        assert result2.transformed_payload == out
        assert result2.edits == ()
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_replayed == 2
        assert result2.selected_content_keys == (root_key, ab_key)


# ---------------------------------------------------------------------------
# Entry-point guard paths (objective 022-b)
# ---------------------------------------------------------------------------
#
# The remaining explicit guard paths of the ACTUAL replace_sources entry
# point, each exercised over the SAME prepared fixture (one
# _transaction_records snapshot / proof / ready / decision state):
#
# * missing/failed/mismatched durable generation or a mismatched
#   snapshot identity: the fixed GENERATION_NOT_DURABLE refusal (the
#   plan-13 503 family) with no transformed payload, no edit and the
#   input unmutated;
# * a VALID source-absent pairing: the payload carries neither the root
#   nor any retained read carrier; the transaction still earns OK with
#   zero edits and returns the exact prepared selected compiled blocks
#   and missing-binding guidance;
# * a genuinely unsupported / nonzero / truncated paired read: its exact
#   result stays unchanged (no proof, no edit) while the observer's own
#   limitation remains recorded and the rest of the transaction proceeds.
#
# The marker-side atomicity (stale/moved/forged live tokens) is the
# existing TestReplayedMarkerScan and transaction replay surface.

SOURCE_ABSENT_TEXT = "Summarize the protected fixture policy."


class TestEntryPointGuards:
    """The explicit entry-point guard paths over ONE prepared fixture."""

    def test_durable_guard_refusals_earn_nothing_and_keep_input(self) -> None:
        rec = _transaction_records()
        base = _transaction_payload()
        frozen = copy.deepcopy(base)
        base_obs = observe_request(base, endpoint="responses", context=_CTX)
        pointer = rec["proof"].publish.pointer
        good = rec["proof"].publish
        variants = (
            (
                "missing generation",
                RecoveryPublishResult(
                    limitation=RecoveryStoreLimitation.OK,
                    generation=None,
                    pointer=None,
                    actual_generation=0,
                ),
            ),
            (
                "failed publication",
                RecoveryPublishResult(
                    limitation=RecoveryStoreLimitation.IO_FAILURE,
                    generation=None,
                    pointer=None,
                    actual_generation=0,
                ),
            ),
            (
                "pointer generation mismatch",
                RecoveryPublishResult(
                    limitation=RecoveryStoreLimitation.OK,
                    generation=good.generation,
                    pointer=RecoveryPointer(
                        generation=2,
                        file_name=pointer.file_name,
                        file_digest=pointer.file_digest,
                        record_bytes=pointer.record_bytes,
                    ),
                    actual_generation=2,
                ),
            ),
            (
                "observed generation mismatch",
                RecoveryPublishResult(
                    limitation=RecoveryStoreLimitation.OK,
                    generation=good.generation,
                    pointer=pointer,
                    actual_generation=2,
                ),
            ),
        )
        for label, publish in variants:
            payload = copy.deepcopy(base)
            result = replace_sources(
                payload,
                proof=PreparedGenerationProof(publish=publish, snapshot=rec["snapshot"]),
                current_snapshot=rec["snapshot"],
                ready_entries=rec["ready"],
                decision=rec["decision"],
                observation=base_obs,
                root_occurrence=base_obs.roots.roots[0],
                key=MARKER_KEY,
                max_text_chars=100_000,
            )
            assert result.outcome is ReplacementOutcome.GENERATION_NOT_DURABLE, (label, result)
            assert result.http_status == 503
            assert result.diagnostics == (ReplacementOutcome.GENERATION_NOT_DURABLE,)
            assert result.transformed_payload is None
            assert result.edits == ()
            assert result.markers == ()
            assert result.edits_planned == 0
            assert result.chars_replaced == 0
            # The input is never touched by the refused transaction.
            assert payload == frozen
        # A MISMATCHED snapshot identity (the proof is bound to the
        # OTHER snapshot) refuses the same fixed way.
        snapshot = rec["snapshot"]
        other = RamStateSnapshot(
            namespace=snapshot.namespace,
            state=snapshot.state,
            result=snapshot.result,
            revision=snapshot.revision + 1,
            epoch=2,
            owned_bytes=0,
        )
        payload = copy.deepcopy(base)
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=other,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=base_obs,
            root_occurrence=base_obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.GENERATION_NOT_DURABLE, result
        assert result.http_status == 503
        assert result.transformed_payload is None
        assert result.edits == ()
        assert payload == frozen

    def test_source_absent_pairing_carries_prepared_context(self) -> None:
        rec = _transaction_records()
        # Ordinary user text only: neither the governing root nor any
        # retained read carrier is present in the current payload.
        plain = {
            "model": "synthetic-model",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": SOURCE_ABSENT_TEXT}],
                },
            ],
        }
        obs = observe_request(plain, endpoint="responses", context=_CTX)
        assert obs.roots.roots == ()
        assert obs.reads == ()
        result = replace_sources(
            plain,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=None,
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        # Nothing in the payload carries a retained source: zero edits,
        # zero markers, nothing touched.
        assert result.edits == ()
        assert result.markers == ()
        assert result.edits_planned == 0
        assert result.edits_committed == 0
        assert result.markers_emitted == 0
        assert result.markers_replayed == 0
        assert result.carriers_touched == 0
        assert result.chars_replaced == 0
        # The exact payload comes back unchanged (a new structure with
        # the same value; the input is never mutated).
        assert result.transformed_payload is not None
        assert result.transformed_payload == plain
        assert result.transformed_payload is not plain
        # The VALID pairing is still carried: the exact selected
        # compiled blocks and the actual missing-binding guidance of
        # the prepared decision.
        assert result.selected_content_keys == tuple(
            w.content_key for w in rec["decision"].working_set
        )
        assert result.compiled_blocks == tuple(
            w.rendered_block for w in rec["decision"].working_set
        )
        assert result.missing_bindings == rec["decision"].missing_bindings

    def test_noncomplete_paired_read_result_stays_unchanged(self) -> None:
        rec = _transaction_records()
        base = _transaction_payload()
        # The c2 pair is the retained COMPLETE C.md singleton: the
        # nonzero / truncated / unsupported variants break that read
        # itself (its own read-level outcome), while the c1 [A,B]
        # partition keeps the positive path (its 017 plan-level
        # OUTER_BOUNDARY_UNPROVEN state is unchanged, as in the
        # baseline) and the root stays edited.
        cases = (
            (
                "nonzero",
                "cat C.md",
                "Chunk ID: synthetic\nWall time: 0.0000 seconds\n"
                "Process exited with code 1\nOutput:\n"
                "cat: C.md: No such file or directory\n",
                ReadOutcome.NONZERO_EXIT,
                (Limitation.NONZERO_EXIT,),
            ),
            (
                "truncated",
                "cat C.md",
                "Chunk ID: synthetic\nWall time: 0.0000 seconds\n"
                "Process exited with code 0\nTruncated: true\nOutput:\n"
                "Background notes f",
                ReadOutcome.TRUNCATED,
                (Limitation.TRUNCATED_OUTPUT,),
            ),
            (
                "unsupported",
                "cat C.md; echo done",
                _ch_frame(C_BODY),
                ReadOutcome.UNSUPPORTED,
                (Limitation.MULTIPLE_COMMANDS,),
            ),
        )
        for label, cmd, frame, expected_outcome, expected_reasons in cases:
            payload = {
                "model": "synthetic-model",
                "input": [
                    base["input"][0],
                    base["input"][1],
                    base["input"][2],
                    _ch_exec_call("c2", cmd),
                    _ch_out_item("c2", frame),
                ],
            }
            frozen = copy.deepcopy(payload)
            obs = observe_request(payload, endpoint="responses", context=_CTX)
            # The observer's own limitation stays recorded on the
            # paired read (never erased, never reinterpreted).
            read_c2 = next(r for r in obs.reads if r.call_id == "c2")
            assert read_c2.outcome is expected_outcome, (label, read_c2)
            for reason in expected_reasons:
                assert reason in read_c2.reasons, (label, read_c2.reasons)
            if label == "nonzero":
                assert read_c2.wrapper.exit_status is ExitStatus.NONZERO
            if label == "truncated":
                assert read_c2.wrapper.truncation is TruncationStatus.TRUE
            read_c1 = next(r for r in obs.reads if r.call_id == "c1")
            assert Limitation.OUTER_BOUNDARY_UNPROVEN in read_c1.reasons
            result = replace_sources(
                payload,
                proof=rec["proof"],
                current_snapshot=rec["snapshot"],
                ready_entries=rec["ready"],
                decision=rec["decision"],
                observation=obs,
                root_occurrence=obs.roots.roots[0],
                key=MARKER_KEY,
                max_text_chars=100_000,
            )
            assert result.outcome is ReplacementOutcome.OK, (label, result)
            # The non-complete paired read earns no proof and no edit:
            # exactly the root and the c1 [A,B] splices are applied.
            assert [(e.carrier_location, e.kind) for e in result.edits] == [
                ("$.input[0].content[0]", MarkerKind.LIVE_REFERENCE),
                ("$.input[2]", MarkerKind.LIVE_REFERENCE),
                ("$.input[2]", MarkerKind.LIVE_REFERENCE),
            ]
            out = result.transformed_payload
            assert out is not None
            # The c2 result is byte-for-byte the exact input result.
            assert out["input"][4]["output"] == payload["input"][4]["output"]
            assert out["input"][4]["output"] == frame
            # The input is never mutated; the prepared pairing is
            # still carried unchanged.
            assert payload == frozen
            assert result.selected_content_keys == tuple(
                w.content_key for w in rec["decision"].working_set
            )
            assert result.compiled_blocks == tuple(
                w.rendered_block for w in rec["decision"].working_set
            )
            assert result.missing_bindings == rec["decision"].missing_bindings


# ---------------------------------------------------------------------------
# 022-c section 1 (the historical read-root gap): the approved
# evidence-marker policy applies to a SUPERSEDED AUTHORITATIVE WHOLE
# ROOT READ (and root region) as well as the bootstrap envelope.  The
# ACTUAL r2 descendant of the accepted read-root fixture: the rooted
# bootstrap (BOOT v0) -> the genuinely issued whole-singleton read r1
# (MID v1) -> the genuinely issued DESCENDANT read r2 (NEW v2) -> the
# issued A read c1.  Under the r1-GOVERNING prepared stage (retained in
# the same fixture) r1's own carrier was the governing root and the
# ACTUAL transaction minted its live tag; under the r2-governing
# prepared stage the replayed r1 RAW carrier must earn the
# non-resolving EVIDENCE splice with the current working set and
# durable snapshot, its transformed evidence must replay, and the
# previously minted live tag must refuse with no output or partial
# edit.  The bootstrap envelope anchor stays the separate historical
# envelope path; a genuinely new old-bytes read r3 re-establishes MID
# under normal currentness (no reclassification).
# ---------------------------------------------------------------------------

READROOT2_BOOT = "Follow `A.md`.\n"
READROOT2_MID = "Follow `A.md` before mutation.\n"
READROOT2_NEW = "Follow `A.md` and `B.md` before mutation.\n"


def _readroot_r2_records() -> dict[str, Any]:
    """The ACTUAL single-lineage r2-descendant fixture over the
    accepted P/D issuances, selected root provenance and T results.

    Stage 1 (retained): the r1-GOVERNING prepared snapshot and its
    ACTUAL prior transaction (the actual previously minted root live
    tag on the r1 carrier is extracted from its transformed payload,
    exactly re-derived).  Stage 2: the r2-GOVERNING prepared snapshot
    (the transaction under test).  Stage 3: the authoritative REVERT
    (a genuinely new complete read r3 of the old bytes, descended
    from r2) re-establishing MID under normal currentness."""
    ns, s0 = r_bootstrap(AdmissionMode.LEAN, "replace022c-readroot2", root_body=READROOT2_BOOT)

    # r1: the genuinely issued whole-singleton AGENTS.md read (MID).
    i1 = r_issue(s0, ns, "r1", "responses", (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    o1 = r_observe(i1.state, ns, (read_request("responses", "r1", READROOT2_MID, "cat AGENTS.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    r1_fact = next(
        f
        for f in o1.state.root_facts
        if f.provenance.kind == "read" and f.provenance.call_id == "r1"
    )
    # The issuance outcome is proven BEFORE the descendant is observed.
    assert r1_fact.issued and r1_fact.authority
    assert r1_fact.source_digest == sha256_hex(READROOT2_MID)

    # ---- Stage 1: the r1-GOVERNING prepared stage ---------------
    t1 = derive_root_region_admission(o1.state, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    r_result_1 = t1.r_result
    assert r_result_1 is not None
    q1 = r_result_1.q_result
    assert q1 is not None
    assert q1.outcome is RootRegionCurrentnessOutcome.READY
    p1 = q1.p_selection
    assert p1 is not None
    assert p1.outcome is RootSelectionOutcome.OK
    assert p1.selected_source_digest == sha256_hex(READROOT2_MID)
    admission_1 = t1.admission
    assert admission_1 is not None
    root_entry_1 = admission_1.root_entry
    assert root_entry_1.root_source is not None
    assert root_entry_1.root_source.kind == "read"
    assert root_entry_1.root_digest == sha256_hex(READROOT2_MID)
    r1_occ_1 = next(o for o in o1.state.d_state.occurrences if o.call_id == "r1")
    root_occurrence_1 = root_entry_1.root_source.occurrence
    assert root_occurrence_1 is not None
    assert root_occurrence_1 is r1_occ_1
    entry_agents_1 = next(
        e
        for e in admission_1.entries
        if any(w.occurrence_id == r1_occ_1.occurrence_id for w in e.witnesses)
    )
    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=TRANSACTION_BUDGET))
    root_index_1 = _root_index(
        root_entry_1,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P1", 90, "immediate"),),
    )
    index_agents_1 = _file_index(
        entry_agents_1,
        (),
        config,
        tokenizer,
        plan,
        rule_id="root-reference",
        statement="The root reference.",
        location="AGENTS.md",
    )
    snapshot_1 = RamStateSnapshot(
        namespace=ns, state=o1.state, result=t1, revision=o1.state.revision, epoch=1, owned_bytes=0
    )
    proof_1 = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-readroot2-r1"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot_1,
    )
    ready_root_1 = _ready(t1, root_entry_1, root_index_1, ("A.md",))
    ready_agents_1 = _ready(t1, entry_agents_1, index_agents_1, ())
    decision_1 = select_working_set(ready_root_1, (ready_agents_1,), plan)
    assert decision_1.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision_1.working_set] == [root_entry_1.content_key]
    assert [(o.content_key, o.reason) for o in decision_1.omitted] == [
        (entry_agents_1.content_key, SelectionOmissionReason.COVERAGE_DEDUPLICATED)
    ]
    payload_1 = {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(READROOT2_BOOT),
            _ch_exec_call("r1", "cat AGENTS.md"),
            _ch_out_item("r1", _ch_frame(READROOT2_MID)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }
    obs1 = observe_request(payload_1, endpoint="responses", context=_CTX)
    assert [o.digest for o in obs1.roots.roots] == [sha256_hex(READROOT2_BOOT)]
    result_1 = replace_sources(
        payload_1,
        proof=proof_1,
        current_snapshot=snapshot_1,
        ready_entries=(ready_root_1, ready_agents_1),
        decision=decision_1,
        observation=obs1,
        root_occurrence=obs1.roots.roots[0],
        key=MARKER_KEY,
        max_text_chars=100_000,
    )
    assert result_1.outcome is ReplacementOutcome.OK, result_1
    assert len(result_1.edits) == 2
    env_edit_1, live_edit_1 = sorted(result_1.edits, key=lambda e: e.carrier_location)
    assert env_edit_1.carrier_location == "$.input[0].content[0]"
    assert env_edit_1.kind is MarkerKind.EVIDENCE
    assert env_edit_1.source_digest == sha256_hex(READROOT2_BOOT)
    assert live_edit_1.carrier_location == "$.input[2]"
    assert live_edit_1.kind is MarkerKind.LIVE_REFERENCE
    assert live_edit_1.source_digest == sha256_hex(READROOT2_MID)
    out_1 = result_1.transformed_payload
    assert out_1 is not None
    # The ACTUAL previously minted live tag: valid MAC under the
    # session key, minted by the ACTUAL prior prepared selection (r1
    # governing).  Extracted from the transformed carrier and exactly
    # re-derived.
    old_live_marker = out_1["input"][2]["output"][81:]
    assert old_live_marker.startswith(LIVE_MARKER_TAG)
    assert old_live_marker.endswith(MARKER_SUFFIX)
    assert old_live_marker == make_live_marker(
        MARKER_KEY,
        namespace_key=ns.lineage_key,
        original_role="file_tool_result",
        occurrence_identity=r1_occ_1.occurrence_id,
        endpoint="responses",
        call_id="r1",
        call_position=0,
        result_position=1,
        piece_index=0,
        segment_index=0,
        entry_class="root_entry",
        content_key=root_entry_1.content_key,
        compiled_digest=root_index_1.compile_key,
        source_digest=sha256_hex(READROOT2_MID),
    )

    # ---- Stage 2: the r2-GOVERNING prepared stage ---------------
    i2 = r_issue(
        o1.state, ns, "r2", "responses", (r1_fact.provenance.occurrence_id,), "cat AGENTS.md"
    )
    o2 = r_observe(i2.state, ns, (read_request("responses", "r2", READROOT2_NEW, "cat AGENTS.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    r2_fact = next(
        f
        for f in o2.state.root_facts
        if f.provenance.kind == "read" and f.provenance.call_id == "r2"
    )
    assert r2_fact.issued and r2_fact.authority
    assert r2_fact.source_digest == sha256_hex(READROOT2_NEW)
    # The superseded old read fact stays retained and authoritative
    # (no reclassification of issued data).
    r1_fact_2 = next(
        f
        for f in o2.state.root_facts
        if f.provenance.kind == "read" and f.provenance.call_id == "r1"
    )
    assert r1_fact_2.issued and r1_fact_2.authority
    assert r1_fact_2.source_digest == sha256_hex(READROOT2_MID)

    i3 = r_issue(o2.state, ns, "c1", "responses", (CAUSAL_ROOT_FACT,), "cat A.md")
    o3 = r_observe(i3.state, ns, (read_request("responses", "c1", A_BODY, "cat A.md"),))
    assert o3.outcome is RootLineageOutcome.ACCEPTED, o3.diagnostics
    t = derive_root_region_admission(o3.state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    r_result = t.r_result
    assert r_result is not None
    q = r_result.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    p_sel = q.p_selection
    assert p_sel is not None
    assert p_sel.outcome is RootSelectionOutcome.OK
    assert p_sel.selected_source_digest == sha256_hex(READROOT2_NEW)
    admission = t.admission
    assert admission is not None
    root_entry = admission.root_entry
    assert root_entry.root_source is not None
    assert root_entry.root_source.kind == "read"
    assert root_entry.root_digest == sha256_hex(READROOT2_NEW)
    r1_occ = next(o for o in o3.state.d_state.occurrences if o.call_id == "r1")
    r2_occ = next(o for o in o3.state.d_state.occurrences if o.call_id == "r2")
    root_occurrence = root_entry.root_source.occurrence
    assert root_occurrence is not None
    assert root_occurrence is r2_occ
    root_proof = root_entry.root_source.proof
    assert root_proof is not None
    assert root_proof is r2_occ.proof
    entry_a = _entry_for(t, "A.md")
    entry_agents = next(
        e
        for e in admission.entries
        if any(w.occurrence_id == r2_occ.occurrence_id for w in e.witnesses)
    )
    assert all(w.occurrence_id == r2_occ.occurrence_id for w in entry_agents.witnesses)
    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
    )
    index_agents = _file_index(
        entry_agents,
        (),
        config,
        tokenizer,
        plan,
        rule_id="root-reference",
        statement="The root reference.",
        location="AGENTS.md",
    )
    snapshot = RamStateSnapshot(
        namespace=ns, state=o3.state, result=t, revision=o3.state.revision, epoch=1, owned_bytes=0
    )
    proof = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=1,
            pointer=RecoveryPointer(
                generation=1,
                file_name="recovery-0001.bin",
                file_digest=sha256_hex("synthetic-recovery-record-readroot2-r2"),
                record_bytes=64,
            ),
            actual_generation=1,
        ),
        snapshot=snapshot,
    )
    ready_root = _ready(t, root_entry, root_index, ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, index_a, ())
    ready_agents = _ready(t, entry_agents, index_agents, ())
    decision = select_working_set(ready_root, (ready_agents, ready_a), plan)
    assert decision.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    assert [(o.content_key, o.reason) for o in decision.omitted] == [
        (entry_agents.content_key, SelectionOmissionReason.COVERAGE_DEDUPLICATED)
    ]

    # ---- Stage 3: the authoritative REVERT (normal currentness) --
    i4 = r_issue(
        o3.state, ns, "r3", "responses", (r2_fact.provenance.occurrence_id,), "cat AGENTS.md"
    )
    o4 = r_observe(i4.state, ns, (read_request("responses", "r3", READROOT2_MID, "cat AGENTS.md"),))
    assert o4.outcome is RootLineageOutcome.ACCEPTED, o4.diagnostics
    t3 = derive_root_region_admission(o4.state, ns)
    assert t3.outcome is RootRegionAdmissionOutcome.READY, t3.diagnostics
    r_result3 = t3.r_result
    assert r_result3 is not None
    q3 = r_result3.q_result
    assert q3 is not None
    assert q3.outcome is RootRegionCurrentnessOutcome.READY
    p3 = q3.p_selection
    assert p3 is not None
    assert p3.outcome is RootSelectionOutcome.OK
    assert p3.selected_source_digest == sha256_hex(READROOT2_MID)
    admission3 = t3.admission
    assert admission3 is not None
    root_entry3 = admission3.root_entry
    assert root_entry3.root_source is not None
    assert root_entry3.root_source.kind == "read"
    assert root_entry3.root_digest == sha256_hex(READROOT2_MID)
    r3_occ = next(o for o in o4.state.d_state.occurrences if o.call_id == "r3")
    root_occurrence3 = root_entry3.root_source.occurrence
    assert root_occurrence3 is not None
    assert root_occurrence3 is r3_occ
    entry_a3 = _entry_for(t3, "A.md")
    entry_agents3 = next(
        e
        for e in admission3.entries
        if any(w.occurrence_id == r3_occ.occurrence_id for w in e.witnesses)
    )
    root_index3 = _root_index(
        root_entry3,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P1", 90, "immediate"),),
    )
    index_a3 = _file_index(
        entry_a3,
        (),
        config,
        tokenizer,
        plan,
        rule_id="a-procedure",
        statement="The A procedure.",
        location="A.md",
    )
    index_agents3 = _file_index(
        entry_agents3,
        (),
        config,
        tokenizer,
        plan,
        rule_id="root-reference",
        statement="The root reference.",
        location="AGENTS.md",
    )
    snapshot3 = RamStateSnapshot(
        namespace=ns, state=o4.state, result=t3, revision=o4.state.revision, epoch=1, owned_bytes=0
    )
    proof3 = PreparedGenerationProof(
        publish=RecoveryPublishResult(
            limitation=RecoveryStoreLimitation.OK,
            generation=2,
            pointer=RecoveryPointer(
                generation=2,
                file_name="recovery-0002.bin",
                file_digest=sha256_hex("synthetic-recovery-record-readroot2-r3"),
                record_bytes=64,
            ),
            actual_generation=2,
        ),
        snapshot=snapshot3,
    )
    ready_root3 = _ready(t3, root_entry3, root_index3, ("A.md",))
    ready_a3 = _ready(t3, entry_a3, index_a3, ())
    ready_agents3 = _ready(t3, entry_agents3, index_agents3, ())
    decision3 = select_working_set(ready_root3, (ready_agents3, ready_a3), plan)
    assert decision3.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision3.working_set] == [
        root_entry3.content_key,
        entry_a3.content_key,
    ]
    return {
        "ns": ns,
        "snapshot": snapshot,
        "proof": proof,
        "root_entry": root_entry,
        "entry_a": entry_a,
        "r1_occ": r1_occ,
        "r2_occ": r2_occ,
        "root_index": root_index,
        "ready": (ready_root, ready_agents, ready_a),
        "decision": decision,
        "old_live_marker": old_live_marker,
        "snapshot3": snapshot3,
        "proof3": proof3,
        "root_entry3": root_entry3,
        "r3_occ": r3_occ,
        "root_index3": root_index3,
        "ready3": (ready_root3, ready_agents3, ready_a3),
        "decision3": decision3,
    }


def _readroot_r2_payload(*, r1_output: str) -> dict[str, Any]:
    """The r2-stage replayed history: the original envelope, the
    superseded r1 read (its carrier content is the test parameter),
    the current r2 read, the A read and the assistant message."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(READROOT2_BOOT),
            _ch_exec_call("r1", "cat AGENTS.md"),
            _ch_out_item("r1", r1_output),
            _ch_exec_call("r2", "cat AGENTS.md"),
            _ch_out_item("r2", _ch_frame(READROOT2_NEW)),
            _ch_exec_call("c1", "cat A.md"),
            _ch_out_item("c1", _ch_frame(A_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


def _readroot_r3_payload() -> dict[str, Any]:
    """The revert-stage replayed history: everything of the r2 stage
    plus the genuinely new old-bytes read r3."""
    return {
        "model": "synthetic-model",
        "input": [
            _ch_root_item(READROOT2_BOOT),
            _ch_exec_call("r1", "cat AGENTS.md"),
            _ch_out_item("r1", _ch_frame(READROOT2_MID)),
            _ch_exec_call("r2", "cat AGENTS.md"),
            _ch_out_item("r2", _ch_frame(READROOT2_NEW)),
            _ch_exec_call("r3", "cat AGENTS.md"),
            _ch_out_item("r3", _ch_frame(READROOT2_MID)),
            _ch_exec_call("c1", "cat A.md"),
            _ch_out_item("c1", _ch_frame(A_BODY)),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Proceeding."}],
            },
        ],
    }


class TestTransactionReadRootHistorical:
    """022-c section 1 over the ACTUAL replace_sources entry point and
    the single-lineage r2-descendant fixture: the superseded
    authoritative whole-root READ earns its non-resolving EVIDENCE
    splice (the old raw carrier, with the current working set and the
    durable snapshot), the transformed evidence replays to a fixed
    point, the previously minted live tag refuses all-or-nothing, the
    old carrier role/wrappers and the other mixed-read members are
    preserved, and the genuine authoritative revert follows normal
    currentness (the envelope anchor stays the separate path)."""

    def test_superseded_read_root_raw_evidence_and_replay(self) -> None:
        rec = _readroot_r2_records()
        ns = rec["ns"]
        snapshot = rec["snapshot"]
        root_key = rec["root_entry"].content_key
        a_key = rec["entry_a"].content_key
        r1_occ = rec["r1_occ"]
        r2_occ = rec["r2_occ"]
        root_index = rec["root_index"]

        # ---- Round 1: the honest replayed RAW r1 carrier ---------
        payload1 = _readroot_r2_payload(r1_output=_ch_frame(READROOT2_MID))
        frozen1 = copy.deepcopy(payload1)
        obs1 = observe_request(payload1, endpoint="responses", context=_CTX)
        assert [o.location for o in obs1.roots.roots] == ["$.input[0].content[0]"]
        assert [o.digest for o in obs1.roots.roots] == [sha256_hex(READROOT2_BOOT)]
        result1 = replace_sources(
            payload1,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs1,
            root_occurrence=obs1.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result1.outcome is ReplacementOutcome.OK, result1
        assert result1.http_status is None
        assert result1.selected_content_keys == (root_key, a_key)
        # EXACTLY four edits: the separate bootstrap envelope anchor
        # EVIDENCE, the superseded READ root EVIDENCE (022-c section
        # 1), the current governing read LIVE and the A read LIVE.
        assert len(result1.edits) == 4
        env_edit, r1_edit, r2_edit, a_edit = sorted(result1.edits, key=lambda e: e.carrier_location)
        assert env_edit.carrier_location == "$.input[0].content[0]"
        assert env_edit.field == "text"
        assert env_edit.kind is MarkerKind.EVIDENCE
        assert env_edit.target_entry_class == "root_entry"
        assert env_edit.target_content_key == root_key
        assert env_edit.source_digest == sha256_hex(READROOT2_BOOT)
        assert env_edit.occurrence_identity == sha256_hex(READROOT2_BOOT)
        assert (env_edit.start, env_edit.end) == (51, 51 + len(READROOT2_BOOT))
        # The superseded authoritative whole-root READ: the old raw
        # carrier earns its non-resolving EVIDENCE splice, its carrier
        # stays a tool result and the evidence identity is the OLD
        # source's own digest in the trusted workspace (never the
        # current root entry key, no compiled binding).
        assert r1_edit.carrier_location == "$.input[2]"
        assert r1_edit.field == "output"
        assert r1_edit.kind is MarkerKind.EVIDENCE
        assert r1_edit.target_entry_class == "root_entry"
        assert r1_edit.target_content_key == sha256_hex(READROOT2_MID)
        assert r1_edit.source_digest == sha256_hex(READROOT2_MID)
        assert r1_edit.occurrence_identity == r1_occ.occurrence_id
        assert r1_edit.target_compiled_digest is None
        assert (r1_edit.start, r1_edit.end) == (81, 81 + len(READROOT2_MID))
        # The current governing read keeps its OWN live splice.
        assert r2_edit.carrier_location == "$.input[4]"
        assert r2_edit.field == "output"
        assert r2_edit.kind is MarkerKind.LIVE_REFERENCE
        assert r2_edit.target_entry_class == "root_entry"
        assert r2_edit.target_content_key == root_key
        assert r2_edit.source_digest == sha256_hex(READROOT2_NEW)
        assert r2_edit.occurrence_identity == r2_occ.occurrence_id
        assert r2_edit.target_compiled_digest == root_index.compile_key
        assert (r2_edit.start, r2_edit.end) == (81, 81 + len(READROOT2_NEW))
        assert a_edit.carrier_location == "$.input[6]"
        assert a_edit.kind is MarkerKind.LIVE_REFERENCE
        assert a_edit.target_entry_class == "file_bundle_entry"
        assert a_edit.target_content_key == a_key
        assert a_edit.source_digest == sha256_hex(A_BODY)
        assert (a_edit.start, a_edit.end) == (81, 81 + len(A_BODY))
        assert result1.edits_planned == 4
        assert result1.edits_committed == 4
        assert result1.markers_emitted == 4
        assert result1.markers_replayed == 0
        assert result1.carriers_touched == 4
        assert result1.chars_replaced == (
            len(READROOT2_BOOT) + len(READROOT2_MID) + len(READROOT2_NEW) + len(A_BODY)
        )
        out1 = result1.transformed_payload
        assert out1 is not None
        # The input payload is never mutated.
        assert payload1 == frozen1
        # The r1 splice carries EXACTLY the re-derived non-resolving
        # evidence tag (tool-result role, the read occurrence
        # identity, the OLD source digest); the rendered marker is
        # compared by its own length and the edit end is the
        # original-source end.
        expected_r1_marker = make_evidence_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=r1_occ.occurrence_id,
            endpoint="responses",
            call_id="r1",
            call_position=0,
            result_position=1,
            piece_index=0,
            segment_index=0,
            source_digest=sha256_hex(READROOT2_MID),
        )
        r1_text = out1["input"][2]["output"]
        r1_orig = _ch_frame(READROOT2_MID)
        assert r1_text[:81] == r1_orig[:81]
        assert r1_text[81 : 81 + len(expected_r1_marker)] == expected_r1_marker
        assert r1_text[81 + len(expected_r1_marker) :] == r1_orig[81 + len(READROOT2_MID) :]
        # The wrappers, the other mixed-read members, the exec
        # carriers and the assistant message are preserved exactly.
        expected_r2_marker = make_live_marker(
            MARKER_KEY,
            namespace_key=ns.lineage_key,
            original_role="file_tool_result",
            occurrence_identity=r2_occ.occurrence_id,
            endpoint="responses",
            call_id="r2",
            call_position=0,
            result_position=1,
            piece_index=0,
            segment_index=0,
            entry_class="root_entry",
            content_key=root_key,
            compiled_digest=root_index.compile_key,
            source_digest=sha256_hex(READROOT2_NEW),
        )
        r2_text = out1["input"][4]["output"]
        assert r2_text[:81] == _ch_frame(READROOT2_NEW)[:81]
        assert r2_text[81 : 81 + len(expected_r2_marker)] == expected_r2_marker
        assert (
            r2_text[81 + len(expected_r2_marker) :]
            == _ch_frame(READROOT2_NEW)[81 + len(READROOT2_NEW) :]
        )
        assert out1["input"][1] == frozen1["input"][1]
        assert out1["input"][3] == frozen1["input"][3]
        assert out1["input"][5] == frozen1["input"][5]
        assert out1["input"][7] == frozen1["input"][7]

        # ---- Round 2: the transformed evidence replays -----------
        payload2 = out1
        frozen2 = copy.deepcopy(payload2)
        obs2 = observe_request(payload2, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            payload2,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.http_status is None
        assert result2.selected_content_keys == (root_key, a_key)
        # The fixed point: no new edit, every marker replays at its
        # own coordinates (an accepted replay changes no authority).
        assert result2.edits == ()
        assert result2.edits_planned == 0
        assert result2.edits_committed == 0
        assert result2.markers_emitted == 0
        assert result2.markers_replayed == 4
        assert result2.carriers_touched == 4
        assert result2.transformed_payload == payload2
        assert payload2 == frozen2
        replays = sorted(result2.markers, key=lambda m: m.carrier_location)
        assert [(m.carrier_location, m.kind, m.replayed) for m in replays] == [
            ("$.input[0].content[0]", MarkerKind.EVIDENCE, True),
            ("$.input[2]", MarkerKind.EVIDENCE, True),
            ("$.input[4]", MarkerKind.LIVE_REFERENCE, True),
            ("$.input[6]", MarkerKind.LIVE_REFERENCE, True),
        ]
        r1_replay = next(m for m in result2.markers if m.carrier_location == "$.input[2]")
        assert r1_replay.source_digest == sha256_hex(READROOT2_MID)
        assert r1_replay.target_content_key == sha256_hex(READROOT2_MID)
        r2_replay = next(m for m in result2.markers if m.carrier_location == "$.input[4]")
        assert r2_replay.source_digest == sha256_hex(READROOT2_NEW)
        assert r2_replay.target_content_key == root_key

    def test_superseded_read_root_stale_live_refuses(self) -> None:
        rec = _readroot_r2_records()
        snapshot = rec["snapshot"]
        # The r1 carrier's original bytes are replaced by the ACTUAL
        # previously minted live tag (the valid-MAC tag the r1-
        # governing prepared stage emitted); the rest of the replayed
        # history stays raw.
        prefix = _ch_frame(READROOT2_MID)[:81]
        suffix = _ch_frame(READROOT2_MID)[81 + len(READROOT2_MID) :]
        payload = _readroot_r2_payload(r1_output=prefix + rec["old_live_marker"] + suffix)
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        result = replace_sources(
            payload,
            proof=rec["proof"],
            current_snapshot=snapshot,
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # The previously minted live tag for the superseded read root
        # is a stale live reference: it ALWAYS refuses all-or-nothing
        # (no transformed payload, no partial edit, no replay).
        assert result.outcome is ReplacementOutcome.MARKER_INVALID, result
        assert result.http_status == 409
        assert result.transformed_payload is None
        assert result.edits == ()
        assert result.markers == ()
        assert payload == frozen

    def test_authoritative_revert_follows_normal_currentness(self) -> None:
        rec = _readroot_r2_records()
        snapshot3 = rec["snapshot3"]
        root_key3 = rec["root_entry3"].content_key
        a_key3 = rec["decision3"].working_set[1].content_key
        r1_occ = rec["r1_occ"]
        r2_occ = rec["r2_occ"]
        r3_occ = rec["r3_occ"]
        root_index3 = rec["root_index3"]

        payload = _readroot_r3_payload()
        frozen = copy.deepcopy(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        assert [o.digest for o in obs.roots.roots] == [sha256_hex(READROOT2_BOOT)]
        result = replace_sources(
            payload,
            proof=rec["proof3"],
            current_snapshot=snapshot3,
            ready_entries=rec["ready3"],
            decision=rec["decision3"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result.outcome is ReplacementOutcome.OK, result
        assert result.http_status is None
        # The genuine new old-bytes read r3 is the governing root
        # again (normal currentness): its carrier earns the LIVE root
        # splice; the superseded r2 read (NEW) earns its non-resolving
        # EVIDENCE splice through the same lineage law; the r1 raw
        # carrier (the same MID bytes the omitted AGENTS.md file
        # entry represents) earns its omission EVIDENCE splice; the
        # envelope anchor and the A read are unchanged in kind.
        assert len(result.edits) == 5
        env_edit, r1_edit, r2_edit, r3_edit, a_edit = sorted(
            result.edits, key=lambda e: e.carrier_location
        )
        assert env_edit.carrier_location == "$.input[0].content[0]"
        assert env_edit.kind is MarkerKind.EVIDENCE
        assert env_edit.source_digest == sha256_hex(READROOT2_BOOT)
        assert r1_edit.carrier_location == "$.input[2]"
        assert r1_edit.kind is MarkerKind.EVIDENCE
        assert r1_edit.source_digest == sha256_hex(READROOT2_MID)
        assert r1_edit.occurrence_identity == r1_occ.occurrence_id
        assert r2_edit.carrier_location == "$.input[4]"
        assert r2_edit.kind is MarkerKind.EVIDENCE
        assert r2_edit.target_entry_class == "root_entry"
        assert r2_edit.source_digest == sha256_hex(READROOT2_NEW)
        assert r2_edit.occurrence_identity == r2_occ.occurrence_id
        assert r2_edit.target_compiled_digest is None
        assert r3_edit.carrier_location == "$.input[6]"
        assert r3_edit.kind is MarkerKind.LIVE_REFERENCE
        assert r3_edit.target_entry_class == "root_entry"
        assert r3_edit.target_content_key == root_key3
        assert r3_edit.source_digest == sha256_hex(READROOT2_MID)
        assert r3_edit.occurrence_identity == r3_occ.occurrence_id
        assert r3_edit.target_compiled_digest == root_index3.compile_key
        assert a_edit.carrier_location == "$.input[8]"
        assert a_edit.kind is MarkerKind.LIVE_REFERENCE
        assert a_edit.target_content_key == a_key3
        assert a_edit.source_digest == sha256_hex(A_BODY)
        assert result.edits_planned == 5
        assert result.edits_committed == 5
        assert result.markers_emitted == 5
        assert result.markers_replayed == 0
        out = result.transformed_payload
        assert out is not None
        assert payload == frozen
        # The transformed revert replays to the same fixed point.
        obs2 = observe_request(out, endpoint="responses", context=_CTX)
        result2 = replace_sources(
            out,
            proof=rec["proof3"],
            current_snapshot=snapshot3,
            ready_entries=rec["ready3"],
            decision=rec["decision3"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert result2.outcome is ReplacementOutcome.OK, result2
        assert result2.edits == ()
        assert result2.markers_replayed == 5
        assert result2.transformed_payload == out


# ---------------------------------------------------------------------------
# 022-c: the pure replay unsplice seam (the marker-shaped source replay
# is detected and authenticated BEFORE any raw state acquisition;
# verified replays unsplice to the retained originals, and stale /
# forged / moved markers refuse at the marker layer).
# ---------------------------------------------------------------------------


class TestReplayUnsplice:
    """The unsplice seam over the ACTUAL fixtures: the transformed
    payload (live and evidence markers in place of the source bytes)
    unsplices byte-for-byte to the originals the transition must
    observe; a previously minted live tag for a superseded read root,
    a forged tag and a moved tag each refuse all-or-nothing with the
    fixed marker-side outcome (no shadow, no raw acquisition); and a
    marker-shaped string outside a recognized source field is ordinary
    data (the closed-location scan never sees it)."""

    def test_readroot_transformed_payload_unsplices_to_the_originals(self) -> None:
        rec = _readroot_r2_records()
        payload1 = _readroot_r2_payload(r1_output=_ch_frame(READROOT2_MID))
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
        out1 = result1.transformed_payload
        assert out1 is not None
        frozen_out = copy.deepcopy(out1)
        # The transformed payload carries marker candidates (the cheap
        # detector fires); the input was never mutated.
        assert payload_has_marker_candidates(out1)
        assert payload1 == frozen
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            out1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # Every one of the four markers is exactly verified and
        # unspliced: the shadow IS the raw original payload
        # byte-for-byte (the root envelope body from the bootstrap
        # anchor's retained root text; the r1 / r2 / A carriers from
        # the retained read proofs' self-contained segment text).
        assert unspliced.outcome is ReplacementOutcome.OK, unspliced
        assert unspliced.markers_replayed == 4
        assert unspliced.carriers_unspliced == 4
        assert unspliced.shadow_payload == payload1
        # The transformed input is never mutated by the unsplice.
        assert out1 == frozen_out

    def test_previously_minted_live_tag_refuses_before_unsplice(self) -> None:
        rec = _readroot_r2_records()
        # The ACTUAL live tag minted when r1 was the governing root
        # (extracted from the stage-1 transformed payload by the
        # fixture): under the r2-governing stage it matches NO
        # expected tag (the old entry key is never reconstructed and
        # the evidence identity is the OLD source's own digest).
        r1_carrier = _ch_frame(READROOT2_MID)
        prefix = r1_carrier[:81]
        suffix = r1_carrier[81 + len(READROOT2_MID) :]
        payload = _readroot_r2_payload(r1_output=prefix + rec["old_live_marker"] + suffix)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # The fixed marker-side refusal BEFORE any raw acquisition:
        # no shadow, no partial unsplice.
        assert unspliced.outcome is ReplacementOutcome.MARKER_INVALID
        assert unspliced.shadow_payload is None
        assert unspliced.markers_replayed == 0
        assert unspliced.carriers_unspliced == 0

    def test_forged_marker_refuses(self) -> None:
        rec = _readroot_r2_records()
        r1_carrier = _ch_frame(READROOT2_MID)
        prefix = r1_carrier[:81]
        suffix = r1_carrier[81 + len(READROOT2_MID) :]
        # A marker of the exact wire shape under a DIFFERENT key
        # (unknown-key / cross-namespace material): fixed forged.
        forged = make_evidence_marker(
            b"other-key-material-0123456789abcd",
            namespace_key=rec["ns"].lineage_key,
            original_role="file_tool_result",
            occurrence_identity=rec["r1_occ"].occurrence_id,
            endpoint="responses",
            call_id="r1",
            call_position=0,
            result_position=1,
            piece_index=0,
            segment_index=0,
            source_digest=sha256_hex(READROOT2_MID),
        )
        assert forged != rec["old_live_marker"]
        payload = _readroot_r2_payload(r1_output=prefix + forged + suffix)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert unspliced.outcome is ReplacementOutcome.MARKER_INVALID
        assert unspliced.shadow_payload is None

    def test_moved_marker_refuses(self) -> None:
        rec = _readroot_r2_records()
        # The honest round one: the VALID current r1 evidence tag at
        # its splice start.
        payload1 = _readroot_r2_payload(r1_output=_ch_frame(READROOT2_MID))
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
        out1 = result1.transformed_payload
        assert out1 is not None
        r1_text = out1["input"][2]["output"]
        r1_carrier = _ch_frame(READROOT2_MID)
        header = r1_carrier[:81]
        # Shift the valid tag ONE character right inside the content:
        # the wrapper stays intact (the carrier remains a recognized
        # source) and the MAC is genuine, but the tag no longer
        # occupies the span's proved splice start (a shifted tag
        # refuses; a broken wrapper would merely leave the carrier
        # unrecognized -- the separate zero-edit law).
        marker = r1_text[81:]
        assert marker.startswith(EVIDENCE_MARKER_TAG) and marker.endswith(MARKER_SUFFIX)
        shifted = header + "X" + marker
        out1["input"][2]["output"] = shifted
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            out1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert unspliced.outcome is ReplacementOutcome.MARKER_INVALID
        assert unspliced.shadow_payload is None

    def test_non_source_marker_text_stays_data(self) -> None:
        rec = _readroot_r2_records()
        payload = _readroot_r2_payload(r1_output=_ch_frame(READROOT2_MID))
        # A marker-shaped string inside ORDINARY (non-source) text:
        # the cheap detector fires, but the closed-location carrier
        # scan never reads it -- the payload unsplices to ITSELF by
        # equality (no marker accounting, no edit made).
        payload["input"][7]["content"][0]["text"] = "Note: " + rec["old_live_marker"]
        assert payload_has_marker_candidates(payload)
        obs = observe_request(payload, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            payload,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs,
            root_occurrence=obs.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        assert unspliced.outcome is ReplacementOutcome.OK
        assert unspliced.markers_replayed == 0
        assert unspliced.carriers_unspliced == 0
        assert unspliced.shadow_payload == payload

    def test_envelope_transformed_payload_unsplices_to_the_originals(self) -> None:
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
        out1 = result1.transformed_payload
        assert out1 is not None
        frozen_out = copy.deepcopy(out1)
        obs2 = observe_request(out1, endpoint="responses", context=_CTX)
        unspliced = unsplice_replayed_markers(
            out1,
            proof=rec["proof"],
            current_snapshot=rec["snapshot"],
            ready_entries=rec["ready"],
            decision=rec["decision"],
            observation=obs2,
            root_occurrence=obs2.roots.roots[0],
            key=MARKER_KEY,
            max_text_chars=100_000,
        )
        # Four live markers (the root envelope, the two proven [A,B]
        # splices, the C singleton) unsplice from THREE carriers to
        # the exact original payload byte-for-byte: the envelope body
        # is the bootstrap anchor's retained root text, the file
        # splices the retained partitioned/singleton proof text.
        assert unspliced.outcome is ReplacementOutcome.OK, unspliced
        assert unspliced.markers_replayed == 4
        assert unspliced.carriers_unspliced == 3
        assert unspliced.shadow_payload == payload1
        assert payload1 == frozen
        assert out1 == frozen_out
