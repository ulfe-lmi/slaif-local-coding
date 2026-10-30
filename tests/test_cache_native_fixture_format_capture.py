"""Selected native format-capture law tests (order 017-ai, the
canonical FUTURE 017-aj entry).

Pure/synthetic layer ONLY: no actual native startup, no fixture,
no Docker operation, no host scan and no admission.  The DURABLE
port of the private 22 ad-hoc controls (parser/formatter vectors,
the full synthetic positive snapshot, the C1 dual-coordinate
causality boundaries, C2 global issued call-ID uniqueness, C3
non-bool bounded truncation budget, per-result association
negatives) plus the review-3 integration controls: the exact
TYPED expected issued-argument identity (a bool or float standing
in for a required integer is refused, never coerced; the digest
binds the canonical bytes of the typed expected shape, not the
provided arguments' own bytes) and the 256 KiB TOTAL SERIALIZED
selected-capture bound INCLUDING the outer tag/binding/identity/
CID at the real consumer seam (the nested snapshot's own bound is
necessary but is not the total).  A malformed nested snapshot
must surface the fixed prep refusal token through the REAL
consumer (the model validator's own distinct error class is
translated, never leaked).
The F2 PINNED offered-schema law is durable: the pinned
native advertises its numeric arguments as JSON schema
``number`` with the parent object closed by a boolean
``additionalProperties`` form (the built-in uses false); the
strict integer emitted/echoed argument identity, the closed
parent/property keyword law, the typed scalar bounds (length
bounds are nonnegative non-bool integers; huge integers never
float-widen or leak OverflowError) and the explicit-null
constraint refusal all hold as closed refusals.  The F5
deadline-anchor law is durable: the SAME original owner
absolute END is clamped at ONE clock reading, stored as the
ledger deadline itself (never re-anchored at a later clock
reading), set-once, and the truthful count law binds the
ledger request total to the model-POST count plus the
exporter's two closed charged commands with every recorded
numeric position strictly below the model-POST count.  The
F4 RECEIVER TRANSACTION layer drives the REAL Provider over
real loopback sockets with a FAKE subject client: a refused
staged continuation (missing poll/next-exec offer, expired
original END after verification but before commit, expired
END at the initial offer) adopts no result/session/offset/
registry progress, the frozen history stays valid for a
later POST, and the post-commit issuance performs no
fallible re-check (a BEHAVIORAL offer-predicate count bound
under a spy-driven monotonic clock that crosses the original
END only if a late post-commit second verification is
observed; an expired POST closes WITHOUT a response because
the output ledger is expired, never a required 400 after
budget expiry; each expired boundary pairs with a separately
owned fresh unexpired world); the end-to-end positive asserts
the ACTUAL
separate counters (8 model POSTs, 10 ledger requests, 2
polls, 6 issued calls) through the real exporter and export
validator.  The F3/F5 RECEPTION BOUNDARY layer drives the
same REAL Provider for the format receiver's closed causal
guard at the real _route seam (equal/earlier result
positions refuse with the state unchanged; the route-level
ALLOCATOR law is already proven in the tool-cycle
controller suite and referenced, not re-proven), the
tentative stream-frame refusal states (a bad initial seed
adopts no session/offset; an insufficient nonempty piece
count and a partial final advance nothing; the frozen
history still commits), the ACTUAL route accounting of
early refusals (wrong auth and malformed JSON consume
model-POST and ledger-request counts before any semantic
step; the 21st POST refuses at the format bound with the
owner/controller caps unchanged), and the durable
history/identity adversarial negatives at the real
receiver (foreign/duplicated/mutated retained results, a
typed-argument mutation and a mismatched poll session all
refuse with the retained history, first-accepted positions
and single retention unchanged).  The positive exporter
test closes and joins its OWN exporter thread and server
with bounded deadline receives.  The T6 PARTIAL
producer/export seam layer drives the same REAL Provider and
the REAL Unix-socket exporter over every closed PARTIAL state
(zero POSTs, a consumed refused POST, the first exec pending,
the stream exec with zero frames, the running initial with its
outstanding poll, the whole source observed under running
wrappers without completion, and the completed stream with the
next case pending) with the closed partial export tag and the
tag-pair dispatch refusals.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import socket
import stat as stat_mod
import struct
import sys
import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load_canonical(name: str, path: Path) -> Any:
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Combined fixture collection loads the script modules under canonical names
# in suite order; already-loaded consumers (provider/producer/exporter) hold
# the exact model/binding module instances they imported, and a later fresh
# canonical exec replaces the sys.modules entries without rebinding them.
# Bind this suite to the ACTUAL provider/producer dependencies so monkeypatch
# targets, ledger/registry construction, the owned seed root and exception
# classes stay instance-coherent under any collection order.
ctl = _load_canonical(
    "cache_native_fixture_controller", SCRIPTS / "cache_native_fixture_controller.py"
)
model = ctl.model
prep = _load_canonical(
    "cache_native_fixture_native_prep", SCRIPTS / "cache_native_fixture_native_prep.py"
)
fbinding = prep.binding
exp = _load_canonical(
    "cache_native_fixture_export_client", SCRIPTS / "cache_native_fixture_export_client.py"
)
fidentity = sys.modules["cache_native_fixture_identity"]

SEED = dict(model.FORMAT_SEED_FILES)
_READ0 = SEED["read-0"].decode()
_P0 = SEED["stream-piece-0"].decode()
_P1 = SEED["stream-piece-1"].decode()
_P2 = SEED["stream-piece-2"].decode()
_T0 = SEED["trunc-0"].decode()

# The coherent closed trace: seven model POSTs (0..6) — POST0
# issues e0; each later POST validates the prior result and
# issues the next closed call at its own position (equality of
# a result position with the NEXT issue position is legal); the
# eighth and ninth ledger requests are the exporter's closed
# quiesce/export commands, which carry no recorded positions.
_POS = {"e0": 0, "e1": 1, "poll1": 2, "poll2": 3, "e2": 4, "e3": 5}
_RES = {"e0": 1, "e1": 2, "poll1": 3, "poll2": 4, "e2": 5, "e3": 6}
_IDS = {
    "e0": "aj-exec-read-0001",
    "e1": "aj-exec-stream-0002",
    "poll1": "aj-poll-stream-0003",
    "poll2": "aj-poll-stream-0004",
    "e2": "aj-exec-empty-0005",
    "e3": "aj-exec-trunc-0006",
}


def _wrapper(
    chunk: str,
    wall: str,
    exit_code: int | None = None,
    session: int | None = None,
    tokens: int | None = None,
    output: str = "",
) -> str:
    sections = []
    if chunk:
        sections.append(f"Chunk ID: {chunk}")
    sections.append(f"Wall time: {wall} seconds")
    if exit_code is not None:
        sections.append(f"Process exited with code {exit_code}")
    if session is not None:
        sections.append(f"Process running with session ID {session}")
    if tokens is not None:
        sections.append(f"Original token count: {tokens}")
    return "\n".join(sections) + "\nOutput:\n" + output


def _trunc_output(effective: int) -> str:
    out = model.format_truncate_text(_T0, effective)
    assert isinstance(out, str)
    return out


def _frame(call_id: str, issued: int, result: int, text: str) -> dict[str, Any]:
    return {
        "call_id": call_id,
        "issued_position": issued,
        "result_position": result,
        "wrapper": text,
    }


def _issued(name: str, call_id: str, position: int, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": "function",
        "name": name,
        "call_id": call_id,
        "position": position,
        "arguments_sha256": model.sha256_bytes(model.canonical_bytes(arguments)),
        "arguments": arguments,
    }


def _case_record(
    spec: dict[str, Any],
    call_id: str,
    position: int,
    results: list[dict[str, Any]],
    session_id: int | None,
    polls: int,
    truncated_effective: int | None,
) -> dict[str, Any]:
    output = b"".join(
        model.parse_native_tool_wrapper(entry["wrapper"])["output"].encode() for entry in results
    )
    nonempty = sum(
        1 for entry in results if model.parse_native_tool_wrapper(entry["wrapper"])["output"] != ""
    )
    arguments = model.format_expected_exec_arguments(spec)
    return {
        "case": spec["case"],
        "kind": spec["kind"],
        "seed_files": list(spec["seed_files"]),
        "command": spec["command"],
        "call_id": call_id,
        "call_position": position,
        "arguments_sha256": model.sha256_bytes(model.canonical_bytes(arguments)),
        "status": "completed",
        "exit": 0,
        "session_id": session_id,
        "results": results,
        "output_bytes": len(output),
        "output_sha256": model.sha256_bytes(output),
        "nonempty_pieces": nonempty,
        "polls": polls,
        "truncated": spec["kind"] == "truncated",
        "truncated_effective_tokens": truncated_effective,
        "crlf": b"\r\n" in output,
        "non_ascii": any(b >= 0x80 for b in output),
        "verified": True,
    }


def build_positive(session: int = 7) -> dict[str, Any]:
    """The coherent synthetic positive snapshot: the four closed
    cases in the closed order, the six issued calls (four exec +
    two empty-stdin polls of the ONE running process) and the
    retained verified wrappers re-parseable against the immutable
    pre-launch seed identity."""
    specs = model.FORMAT_CASES
    effective = model.FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS
    trunc_bytes = _trunc_output(effective).encode()
    results_read = [
        _frame(
            _IDS["e0"],
            _POS["e0"],
            _RES["e0"],
            _wrapper(
                "d4e5f6",
                "0.0200",
                exit_code=0,
                tokens=model._approx_token_count_bytes(len(SEED["read-0"])),
                output=_READ0,
            ),
        )
    ]
    results_stream = [
        _frame(
            _IDS["e1"],
            _POS["e1"],
            _RES["e1"],
            _wrapper(
                "a1b2c3",
                "0.5000",
                session=session,
                tokens=model._approx_token_count_bytes(len(SEED["stream-piece-0"])),
                output=_P0,
            ),
        ),
        _frame(
            _IDS["poll1"],
            _POS["poll1"],
            _RES["poll1"],
            _wrapper(
                "b2c3d4",
                "2.5000",
                session=session,
                tokens=model._approx_token_count_bytes(len(SEED["stream-piece-1"])),
                output=_P1,
            ),
        ),
        _frame(
            _IDS["poll2"],
            _POS["poll2"],
            _RES["poll2"],
            # the completion poll may omit the session ID (pinned)
            _wrapper(
                "c3d4e5",
                "4.5000",
                exit_code=0,
                tokens=model._approx_token_count_bytes(len(SEED["stream-piece-2"])),
                output=_P2,
            ),
        ),
    ]
    results_empty = [
        _frame(
            _IDS["e2"],
            _POS["e2"],
            _RES["e2"],
            _wrapper("e5f6a7", "0.0050", exit_code=0, output=""),
        )
    ]
    results_trunc = [
        _frame(
            _IDS["e3"],
            _POS["e3"],
            _RES["e3"],
            _wrapper(
                "f6a7b8",
                "0.0300",
                exit_code=0,
                tokens=model._approx_token_count_bytes(len(SEED["trunc-0"])),
                output=trunc_bytes.decode(),
            ),
        )
    ]
    calls = [
        _issued(
            model.FORMAT_EXEC_TOOL,
            _IDS["e0"],
            _POS["e0"],
            model.format_expected_exec_arguments(specs[0]),
        ),
        _issued(
            model.FORMAT_EXEC_TOOL,
            _IDS["e1"],
            _POS["e1"],
            model.format_expected_exec_arguments(specs[1]),
        ),
        _issued(
            model.FORMAT_POLL_TOOL,
            _IDS["poll1"],
            _POS["poll1"],
            {"session_id": session, "chars": ""},
        ),
        _issued(
            model.FORMAT_POLL_TOOL,
            _IDS["poll2"],
            _POS["poll2"],
            {"session_id": session, "chars": ""},
        ),
        _issued(
            model.FORMAT_EXEC_TOOL,
            _IDS["e2"],
            _POS["e2"],
            model.format_expected_exec_arguments(specs[2]),
        ),
        _issued(
            model.FORMAT_EXEC_TOOL,
            _IDS["e3"],
            _POS["e3"],
            model.format_expected_exec_arguments(specs[3]),
        ),
    ]
    total_output = (
        len(SEED["read-0"])
        + len(SEED["stream-piece-0"])
        + len(SEED["stream-piece-1"])
        + len(SEED["stream-piece-2"])
        + 0
        + len(trunc_bytes)
    )
    return {
        "record": model.SCHEMA_FORMAT_SNAPSHOT,
        "synthetic": True,
        "issued_calls": calls,
        "cases": [
            _case_record(specs[0], _IDS["e0"], _POS["e0"], results_read, None, 0, None),
            _case_record(specs[1], _IDS["e1"], _POS["e1"], results_stream, session, 2, None),
            _case_record(specs[2], _IDS["e2"], _POS["e2"], results_empty, None, 0, None),
            _case_record(specs[3], _IDS["e3"], _POS["e3"], results_trunc, None, 0, effective),
        ],
        "seed": [
            [name, model.sha256_bytes(data), len(data)] for name, data in model.FORMAT_SEED_FILES
        ],
        "seed_total_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_sha256": model.sha256_bytes(b"".join(d for _n, d in model.FORMAT_SEED_FILES)),
        "exporter_uid": model.CONTROLLER_UID,
        "exported_before_teardown": True,
        "model_posts": 7,
        "controller_ledger": {"requests": 9, "output_bytes": total_output},
        "polls": 2,
        "final_state": "done",
    }


def expect_refusal(mutate: Callable[[dict[str, Any]], None], reason: str, session: int = 7) -> None:
    rec = build_positive(session)
    mutate(rec)
    with pytest.raises(model.FixtureError) as excinfo:
        model.validate_format_snapshot_record(rec)
    assert reason in str(excinfo.value)


# -- parser layer (pinned wrapper grammar) ------------------------------------


def test_parser_exact_empty_output_with_delimiter_lf() -> None:
    # the Output: line is followed by LF even when the output is
    # empty (pinned format(header + LF + output))
    facts = model.parse_native_tool_wrapper(
        "Wall time: 0.0000 seconds\nProcess exited with code 0\nOutput:\n"
    )
    assert facts["output"] == ""
    assert facts["exit_code"] == 0


def test_parser_lone_surrogate_typed_refusal() -> None:
    with pytest.raises(model.FixtureError) as excinfo:
        model.parse_native_tool_wrapper("Wall time: 0.0000 seconds\nOutput:\n\ud800")
    assert "format-wrapper-encoding" in str(excinfo.value)


def test_parser_overlong_i32_typed_refusal() -> None:
    with pytest.raises(model.FixtureError) as excinfo:
        model.parse_native_tool_wrapper(
            "Wall time: 0.0000 seconds\nProcess exited with code -21474836480\nOutput:\nx"
        )
    assert "format-wrapper-section" in str(excinfo.value)


def test_parser_overbound_wall_time_typed_refusal() -> None:
    with pytest.raises(model.FixtureError) as excinfo:
        model.parse_native_tool_wrapper("Wall time: 2048.0001 seconds\nOutput:\nx")
    assert "format-wrapper-bound" in str(excinfo.value)


# -- formatter layer (pinned truncation mirror) --------------------------------


def test_formatter_head_tail_marker_vector() -> None:
    expected_trunc = "a" * 20 + "\u202615 tokens truncated\u2026" + "a" * 20
    assert model.truncate_middle_with_token_budget("a" * 100, 10) == expected_trunc
    expected_wrap = (
        "Warning: truncated output (original token count: 25)\n"
        "Total output lines: 1\n\n" + expected_trunc
    )
    assert model.format_truncate_text("a" * 100, 10) == expected_wrap


def test_formatter_zero_budget_marker_only_vector() -> None:
    assert model.format_truncate_text("abc", 0) == (
        "Warning: truncated output (original token count: 1)\n"
        "Total output lines: 1\n\n\u20261 tokens truncated\u2026"
    )


def _pinned_truncation_expected(text: str, max_tokens: int) -> str:
    """INDEPENDENT re-derivation of the pinned
    plan_token_truncation law (str-trunc.rs, exact pinned commit):
    max_bytes = 4 * max_tokens, the left budget is max_bytes // 2,
    the head is the longest prefix whose UTF-8 byte length stays
    within the left budget (floor character boundary), the tail is
    the longest suffix within the right budget (ceil character
    boundary), and the marker counts the removed bytes as
    ceil((total - max_bytes) / 4) approximate tokens.  The test
    compares the module mirror against THIS character walk, never
    against the module's own output."""
    total_bytes = len(text.encode("utf-8"))
    max_bytes = max_tokens * 4
    assert total_bytes > max_bytes
    left_budget = max_bytes // 2
    right_budget = max_bytes - left_budget
    head_chars = 0
    head_bytes = 0
    for char in text:
        char_bytes = len(char.encode("utf-8"))
        if head_bytes + char_bytes <= left_budget:
            head_chars += 1
            head_bytes += char_bytes
        else:
            break
    tail_chars = 0
    tail_bytes = 0
    for char in reversed(text):
        char_bytes = len(char.encode("utf-8"))
        if tail_bytes + char_bytes <= right_budget:
            tail_chars += 1
            tail_bytes += char_bytes
        else:
            break
    head = text[:head_chars]
    tail = text[len(text) - tail_chars :] if tail_chars else ""
    removed_tokens = (total_bytes - max_bytes + 3) // 4
    return head + f"\u2026{removed_tokens} tokens truncated\u2026" + tail


def test_formatter_utf8_byte_boundary_full_expectation() -> None:
    # UTF-8 byte, not character, slicing: the FULL result must
    # equal the independently derived head + marker + tail.  The
    # first vector is boundary-aligned (a decodability-only check
    # would also pass the original character-slicing bug), the
    # second vector is deliberately MISALIGNED on BOTH the floor
    # head boundary and the ceil tail boundary (2-byte then 3-byte
    # characters against half-byte budgets that land mid-character).
    aligned = "\u00e9" * 100  # 2 bytes each, 200 bytes
    assert model.truncate_middle_with_token_budget(aligned, 10) == (
        _pinned_truncation_expected(aligned, 10)
    )
    assert model.truncate_middle_with_token_budget(aligned, 10) == (
        "\u00e9" * 10 + "\u202640 tokens truncated\u2026" + "\u00e9" * 10
    )
    misaligned = "\u00e9" * 9 + "\u4e2d" * 60  # 18 + 180 = 198 bytes
    assert model.truncate_middle_with_token_budget(misaligned, 13) == (
        _pinned_truncation_expected(misaligned, 13)
    )
    # the independent derivation pins the exact misaligned cut:
    # head 24 bytes (floor of the 26-byte budget), tail 24 bytes
    # (ceil of the 172-byte target), 37 removed approximate tokens
    assert model.truncate_middle_with_token_budget(misaligned, 13) == (
        "\u00e9" * 9 + "\u4e2d" * 2 + "\u202637 tokens truncated\u2026" + "\u4e2d" * 8
    )


# -- positive synthetic snapshot (full closed law) ------------------------------


def test_snapshot_positive_four_cases_six_issued() -> None:
    positive = build_positive()
    model.validate_format_snapshot_record(positive)


def test_supplied_snapshot_coordinate_preservation_pure() -> None:
    # PURE coordinate preservation of ONE supplied snapshot
    # record: the validator re-checks the retained dual numeric
    # coordinates exactly as supplied (a historical replay keeps
    # the original accepted positions, never relabeled to the
    # issue positions).  This is NOT a receiver history-dedup
    # proof: the controller's historical replay verification
    # (byte-identical re-sent results retained exactly once,
    # refused duplicates/foreign ids) is proven in the
    # controller/coupled layer.
    positive = build_positive()
    model.validate_format_snapshot_record(positive)
    assert [r["result_position"] for r in positive["cases"][0]["results"]] == [1]
    assert [r["result_position"] for r in positive["cases"][1]["results"]] == [2, 3, 4]
    assert [r["issued_position"] for r in positive["cases"][1]["results"]] == [1, 2, 3]


# -- chain multi-chunk qualification --------------------------------------------


def test_chain_only_one_nonempty_piece_refused() -> None:
    # the multi-chunk qualification requires at least TWO
    # nonempty observed output pieces: an initial and an
    # intermediate EMPTY running frame plus only ONE final
    # nonempty (completion) frame must be refused, even though
    # the concatenated output byte law and the per-chunk token
    # metadata are otherwise coherent

    def mutate(rec: dict[str, Any]) -> None:
        specs = model.FORMAT_CASES
        full = _P0 + _P1 + _P2
        results = [
            _frame(
                _IDS["e1"],
                _POS["e1"],
                _RES["e1"],
                _wrapper("a1b2c3", "0.5000", session=7, output=""),
            ),
            _frame(
                _IDS["poll1"],
                _POS["poll1"],
                _RES["poll1"],
                _wrapper("b2c3d4", "2.5000", session=7, output=""),
            ),
            _frame(
                _IDS["poll2"],
                _POS["poll2"],
                _RES["poll2"],
                _wrapper(
                    "c3d4e5",
                    "4.5000",
                    exit_code=0,
                    tokens=model._approx_token_count_bytes(len(full.encode("utf-8"))),
                    output=full,
                ),
            ),
        ]
        rec["cases"][1] = _case_record(specs[1], _IDS["e1"], _POS["e1"], results, 7, 2, None)

    expect_refusal(mutate, "format-case-multichunk")


# -- C1 dual-coordinate causality ----------------------------------------------


def _set_first_result_position(value: int, case_index: int = 0) -> Callable[[dict[str, Any]], None]:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][case_index]["results"][0]["result_position"] = value

    return mutate


def test_c1_equal_own_issuance_refused() -> None:
    # e0 is issued at position 0: a result AT its own issuance
    # position is not strictly after it
    expect_refusal(_set_first_result_position(0), "format-result-causality")


def test_c1_pre_call_result_refused() -> None:
    # case 0 is issued at position 0, so its pre-call boundary is
    # exercised on case 1 (e1 issued at 1): a result at position
    # 0 arrives before e1's own issuance
    expect_refusal(_set_first_result_position(0, case_index=1), "format-result-causality")


def test_c1_result_after_next_issuance_refused() -> None:
    # e0's result at 5 is strictly after its own issuance (0)
    # but AFTER the next issued call's position (1): over the
    # complete ordered registry (one outstanding call at a time)
    # the prior result can never arrive past the next issue
    expect_refusal(_set_first_result_position(5), "format-result-causality")


def test_c1_result_equal_next_issued_position_legal() -> None:
    # the same POST may validate the prior result and issue the
    # next call at that very position: equality with the NEXT
    # issued position is legal
    rec = build_positive()
    rec["cases"][0]["results"][0]["result_position"] = 1
    model.validate_format_snapshot_record(rec)


# -- C2 global issued call-ID uniqueness ----------------------------------------


def test_c2_cross_case_reused_id_changed_args_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][4]["call_id"] = _IDS["e0"]  # case-2 exec, case-0 ID
        rec["cases"][2]["call_id"] = _IDS["e0"]
        rec["cases"][2]["results"][0]["call_id"] = _IDS["e0"]

    expect_refusal(mutate, "format-issued-duplicate")


def test_c2_reused_id_within_registry_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][5]["call_id"] = _IDS["e2"]  # trunc exec reuses empty-exec ID
        rec["cases"][3]["call_id"] = _IDS["e2"]
        rec["cases"][3]["results"][0]["call_id"] = _IDS["e2"]

    expect_refusal(mutate, "format-issued-duplicate")


# -- C3 non-bool bounded truncation budget ---------------------------------------


def test_c3_boolean_budget_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][3]["truncated_effective_tokens"] = True

    expect_refusal(mutate, "format-case-truncation")


def test_c3_over_bound_budget_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][3]["truncated_effective_tokens"] = model.FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS + 1

    expect_refusal(mutate, "format-case-truncation")


def test_c3_non_matching_effective_budget_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][3]["truncated_effective_tokens"] = 23

    expect_refusal(mutate, "format-case-truncation")


# -- per-result association -------------------------------------------------------


def test_association_swapped_poll_results_refused() -> None:
    # association identity only (wrapper content unchanged, so the
    # closed frame/source laws stay satisfied and the association
    # law itself is the check under test)

    def mutate(rec: dict[str, Any]) -> None:
        a, b = rec["cases"][1]["results"][1], rec["cases"][1]["results"][2]
        a["call_id"], b["call_id"] = b["call_id"], a["call_id"]
        a["issued_position"], b["issued_position"] = b["issued_position"], a["issued_position"]

    expect_refusal(mutate, "format-result-association")


def test_association_foreign_first_result_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][0]["results"][0]["call_id"] = _IDS["e2"]

    expect_refusal(mutate, "format-result-association")


def test_wrong_poll_session_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][2]["arguments"] = {"session_id": 8, "chars": ""}
        rec["issued_calls"][2]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][2]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments")


def test_missing_poll_call_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"] = [c for c in rec["issued_calls"] if c["call_id"] != _IDS["poll2"]]

    expect_refusal(mutate, "format-issued-polls")


# -- review-3: exact typed expected issued-argument identity ----------------------


def test_typed_identity_unit_law() -> None:
    # loose dict equality would accept True for 1 and 1.0 for 1;
    # the typed-strict law must not
    expected_poll = {"session_id": 1, "chars": ""}
    assert model.format_arguments_exact(expected_poll, expected_poll)
    assert not model.format_arguments_exact({"session_id": True, "chars": ""}, expected_poll)
    assert not model.format_arguments_exact({"session_id": 1.0, "chars": ""}, expected_poll)
    assert not model.format_arguments_exact({"session_id": "1", "chars": ""}, expected_poll)
    assert not model.format_arguments_exact({"session_id": 1, "chars": "", "x": 0}, expected_poll)
    assert not model.format_arguments_exact({"chars": ""}, expected_poll)
    assert not model.format_arguments_exact(None, expected_poll)


def test_typed_poll_session_one_with_true_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][2]["arguments"] = {"session_id": True, "chars": ""}
        rec["issued_calls"][2]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][2]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments", session=1)


def test_typed_poll_session_one_with_float_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][3]["arguments"] = {"session_id": 1.0, "chars": ""}
        rec["issued_calls"][3]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][3]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments", session=1)


def test_typed_poll_missing_chars_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][2]["arguments"] = {"session_id": 1}
        rec["issued_calls"][2]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][2]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments", session=1)


def test_typed_exec_float_budget_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][5]["arguments"] = {
            "cmd": model.FORMAT_CASES[3]["command"],
            "max_output_tokens": 24.0,
        }
        rec["issued_calls"][5]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][5]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments")


def test_typed_exec_float_yield_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        args = dict(model.format_expected_exec_arguments(model.FORMAT_CASES[1]))
        args["yield_time_ms"] = 500.0
        rec["issued_calls"][1]["arguments"] = args
        rec["issued_calls"][1]["arguments_sha256"] = model.sha256_bytes(
            model.canonical_bytes(rec["issued_calls"][1]["arguments"])
        )

    expect_refusal(mutate, "format-issued-arguments")


def test_typed_poll_session_one_valid_int_accepted() -> None:
    # the valid integer 1 (the typed expected shape) passes the
    # WHOLE snapshot law
    positive = build_positive(session=1)
    model.validate_format_snapshot_record(positive)


def test_digest_bound_to_typed_expected_shape() -> None:
    # a well-typed argument set with a foreign 64-hex digest is
    # refused: the digest binds the canonical bytes of the TYPED
    # EXPECTED shape, not the provided arguments' own bytes

    def mutate(rec: dict[str, Any]) -> None:
        rec["issued_calls"][2]["arguments_sha256"] = "0" * 64

    expect_refusal(mutate, "format-issued-digest")


# -- review-3: TOTAL serialized outer capture bound at the consumer seam ---------


def _aj_identity() -> dict[str, Any]:
    desc = fidentity.FixtureIdentityDescription(
        profile=fidentity.PROFILE_OWNER_UID,
        controller_uid=fidentity.CONTROLLER_UID,
        controller_gid=fidentity.CONTROLLER_GID,
        subject_uid=1001,
        subject_gid=1001,
        subject_groups=(1001,),
    )
    return {
        "profile": desc.profile,
        "fingerprint": fidentity.fingerprint_description(desc),
        "subject_uid": 1001,
        "subject_gid": 1001,
        "subject_groups": [1001],
        "profile_data_sha256": hashlib.sha256(fidentity.encode_description(desc)).hexdigest(),
    }


def _aj_binding(repo_identity: str = "slaif-aj-synthetic-repo") -> dict[str, Any]:
    return {
        "record": prep.BINDING_RECORD_SCHEMA,
        "order_id": "017-aj",
        "order_path": "oap/orders/017-aj-native-process-format-qualification.md",
        "order_sha256": "1" * 64,
        "active_sha256": "2" * 64,
        "source_head": "3" * 40,
        "repo_identity": repo_identity,
        "run_id": "4" * 32,
    }


def _outer_record(repo_identity: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "record": "slaif-017aj-native-format-capture-v1",
        "binding": _aj_binding(repo_identity),
        "identity": _aj_identity(),
        "cid": "5" * 64,
        "snapshot": snapshot,
    }


def test_consumer_outer_record_under_total_bound_accepted() -> None:
    snapshot = build_positive()
    rec = _outer_record("slaif-aj-synthetic-repo", snapshot)
    assert prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo")) == snapshot


def test_consumer_outer_record_over_total_bound_refused() -> None:
    big_repo = "r" * (300 * 1024)
    rec = _outer_record(big_repo, build_positive())
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding(big_repo))
    assert "prep-format-capture-bound" in str(excinfo.value)


def test_consumer_nested_bound_is_not_the_total() -> None:
    # the nested snapshot is far under its own bound while the
    # WHOLE canonical record (outer metadata included) is over:
    # the total, not the nested size, is the refusal trigger
    big_repo = "r" * (300 * 1024)
    snapshot = build_positive()
    rec = _outer_record(big_repo, snapshot)
    assert len(model.canonical_bytes(snapshot)) < model.FORMAT_SNAPSHOT_MAX_BYTES
    assert len(model.canonical_bytes(rec)) > model.FORMAT_SNAPSHOT_MAX_BYTES


def test_consumer_malformed_nested_snapshot_fixed_prep_token() -> None:
    # a malformed nested snapshot must surface the FIXED prep
    # refusal token through the REAL consumer: the model
    # validator's own distinct error class (a ValueError) is
    # translated, never leaked
    snapshot = build_positive()
    snapshot["final_state"] = "not-done"
    rec = _outer_record("slaif-aj-synthetic-repo", snapshot)
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)
    assert not isinstance(excinfo.value, model.FixtureError)


def test_consumer_foreign_order_binding_refused() -> None:
    # the AJ format-capture tag is the record of the AJ canonical
    # entry ONLY: a well-formed foreign (AF) binding is a
    # mismatch, never a silent rebind
    binding = _aj_binding()
    binding = dict(binding)
    binding["order_id"] = "017-af"
    binding["order_path"] = "oap/orders/017-af-owner-uid-native-pty-qualification.md"
    snapshot = build_positive()
    rec = _outer_record("slaif-aj-synthetic-repo", snapshot)
    rec["binding"] = binding
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, binding)
    assert "prep-format-capture-mismatch" in str(excinfo.value)


def test_consumer_bad_cid_refused() -> None:
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    rec["cid"] = "not-a-64-hex-cid"
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_partial_sourceless_zero_accepted() -> None:
    # the DISTINCT partial dispatch through the REAL consumer:
    # the empty safe partial (no POSTs, no issued calls, no
    # cases) is accepted and returned unchanged, still
    # explicitly not-qualified
    partial = _partial_record([], [], 0)
    rec = _outer_record("slaif-aj-synthetic-repo", partial)
    out = prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert out is partial
    assert out["qualification"] == "not-qualified"


def test_consumer_partial_running_initial_accepted() -> None:
    # the nonempty safe partial (complete read prefix plus the
    # running stream case with ONE outstanding issued poll)
    # passes the REAL consumer through the partial validator
    partial = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
        (len(SEED["read-0"]) + len(SEED["stream-piece-0"])),
    )
    rec = _outer_record("slaif-aj-synthetic-repo", partial)
    out = prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert out is partial
    assert out["qualification"] == "not-qualified"
    assert out["polls"] == 1


def test_consumer_partial_malformed_nested_fixed_prep_token() -> None:
    # a malformed nested PARTIAL snapshot (qualification
    # laundered to a non-closed value) must surface the FIXED
    # prep refusal token through the real consumer — the model
    # error class is translated, never leaked
    partial = _partial_record([], [], 0)
    partial["qualification"] = "qualified"
    rec = _outer_record("slaif-aj-synthetic-repo", partial)
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)
    assert not isinstance(excinfo.value, model.FixtureError)


def test_consumer_nested_tag_unknown_refused() -> None:
    # a nested snapshot carrying an unknown record tag is a
    # closed refusal at the consumer dispatch, never a guess
    snapshot = build_positive()
    snapshot["record"] = "slaif-fixture-format-capture-snapshot-v2"
    rec = _outer_record("slaif-aj-synthetic-repo", snapshot)
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_nested_tag_untagged_refused() -> None:
    snapshot = build_positive()
    del snapshot["record"]
    rec = _outer_record("slaif-aj-synthetic-repo", snapshot)
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_partial_tag_flipped_to_full_refused() -> None:
    # a partial snapshot re-tagged with the STRICT full tag is
    # refused by the full validator's own closed grammar — the
    # dispatch never launders a partial into a full
    partial = _partial_record([], [], 0)
    partial["record"] = model.SCHEMA_FORMAT_SNAPSHOT
    rec = _outer_record("slaif-aj-synthetic-repo", partial)
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, _aj_binding("slaif-aj-synthetic-repo"))
    assert "prep-format-capture-malformed" in str(excinfo.value)


def _aj_typed_as(cls: Any, **overrides: object) -> Any:
    # a directly constructed typed binding (DATA validation
    # only — the dataclass carries no __post_init__ validation
    # and no measured authority)
    fields: dict[str, Any] = {
        "order_id": "017-aj",
        "order_path": "oap/orders/017-aj-native-process-format-qualification.md",
        "order_sha256": "1" * 64,
        "active_bytes": b"017-aj",
        "source_head": "3" * 40,
        "repo_identity": "slaif-aj-synthetic-repo",
        "run_id": "4" * 32,
    }
    fields.update(overrides)
    return cls(**fields)


class _to_record_spy(fbinding.OrderRunBinding):  # type: ignore[name-defined,misc]
    # fail-fast spy: ANY consumer reach to to_record fails the
    # control (the bounded pre-hash law must refuse BEFORE
    # hashing work; an early-hash implementation fails it)

    def to_record(self) -> dict[str, str]:
        raise AssertionError("to_record must not be reached")


class _type_error_to_record_spy(fbinding.OrderRunBinding):  # type: ignore[name-defined,misc]
    # synthetic to_record TypeError with otherwise VALID
    # active data: the fixed prep-token conversion is the law
    # under test

    def to_record(self) -> dict[str, str]:
        raise TypeError("synthetic to_record failure")


def _aj_typed_binding(**overrides: object) -> Any:
    return _aj_typed_as(fbinding.OrderRunBinding, **overrides)


def test_consumer_typed_binding_full_accepted() -> None:
    # a well-formed typed binding is accepted: the consumer
    # holds the to_record output to the SAME closed
    # binding-record grammar as a supplied dict and requires
    # the embedded binding to equal it exactly
    typed = _aj_typed_binding()
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    rec["binding"] = typed.to_record()
    assert prep.parse_format_capture_record(rec, typed) is rec["snapshot"]


def test_consumer_typed_binding_partial_accepted() -> None:
    typed = _aj_typed_binding()
    partial = _partial_record([], [], 0)
    rec = _outer_record("slaif-aj-synthetic-repo", partial)
    rec["binding"] = typed.to_record()
    assert prep.parse_format_capture_record(rec, typed) is partial


def test_consumer_typed_binding_malformed_head_refused() -> None:
    # a directly constructed typed object with a malformed
    # source_head is a closed refusal through the same
    # binding-record grammar — never trusted through to_record
    typed = _aj_typed_binding(source_head="not-a-head")
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    rec["binding"] = typed.to_record()
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_typed_binding_malformed_run_id_refused() -> None:
    typed = _aj_typed_binding(run_id="not-a-run-id")
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    rec["binding"] = typed.to_record()
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_typed_binding_malformed_order_hash_refused() -> None:
    typed = _aj_typed_binding(order_sha256="x" * 64)
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    rec["binding"] = typed.to_record()
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_typed_binding_overbound_active_bytes_refused() -> None:
    # an over-bound active_bytes is refused BEFORE any hashing
    # work: the fail-fast to_record spy proves the consumer
    # never reaches to_record (an early-hash implementation
    # fails this control); the embedded binding stays the
    # default synthetic dict
    typed = _aj_typed_as(_to_record_spy, active_bytes=b"r" * (prep._ACTIVE_BYTES_MAX + 1))
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_typed_binding_nonbytes_active_refused() -> None:
    # a non-bytes active field type is refused by the bounded
    # pre-hash check BEFORE to_record is reached (fail-fast
    # spy: an early-hash implementation fails this control)
    typed = _aj_typed_as(_to_record_spy, active_bytes="017-aj")
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)


def test_consumer_typed_to_record_type_error_converted() -> None:
    # otherwise VALID active data but a synthetic to_record
    # TypeError: the consumer converts it to the FIXED prep
    # refusal token (bounded handling, the raw exception is
    # never leaked)
    typed = _aj_typed_as(_type_error_to_record_spy)
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-malformed" in str(excinfo.value)
    assert not isinstance(excinfo.value, TypeError)


def test_consumer_typed_binding_unequal_embedded_refused() -> None:
    # a well-formed typed object whose to_record differs from
    # the embedded binding (the synthetic dict's active hash)
    # is a mismatch, never a silent rebind
    typed = _aj_typed_binding()
    rec = _outer_record("slaif-aj-synthetic-repo", build_positive())
    with pytest.raises(prep.FixtureError) as excinfo:
        prep.parse_format_capture_record(rec, typed)
    assert "prep-format-capture-mismatch" in str(excinfo.value)


# ----------------------------------------------------------------------
# F1 seam: the ACTUAL seed_format_seeds exercised on owned nonroot
# roots (tmp_path + monkeypatched model.FORMAT_SEED_DIR).  Public law:
# REJECT-ALL-PREEXISTING — the fresh creation seals 0555/0444
# byte-exact and ANY pre-existing root (even a correctly sealed one)
# is the public refusal format-seed-untrusted, never adopted.
# Whitebox law: the held-fd per-file verification refuses mutated
# bytes (copy-mismatch) and non-regular/linked/missing/foreign-mode
# entries (untrusted) — FIFO included, without blocking.  No actual
# native startup, fixture, Docker, admission or host scan occurs.
# ----------------------------------------------------------------------


def _unseal_tree(root: Path) -> None:
    """Test-owned cleanup: lstat-classify and unseal 0555 dirs /
    0444 files so pytest's tmp cleanup can remove them; NEVER
    follow or chmod a symlink (unlink only is rmtree's job)."""
    if not root.is_dir():
        return
    for e in root.iterdir():  # iterdir yields Path objects
        st = os.lstat(e)
        if stat_mod.S_ISDIR(st.st_mode):
            _unseal_tree(e)
            try:
                os.chmod(e, 0o700)
            except OSError:
                pass
        elif not stat_mod.S_ISLNK(st.st_mode):
            try:
                os.chmod(e, 0o600)
            except OSError:
                pass
    if root.is_dir() and not root.is_symlink():
        try:
            os.chmod(root, 0o700)
        except OSError:
            pass


class TestFormatSeedSeam:
    @pytest.fixture()
    def seed_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> Iterator[tuple[Any, Path]]:
        seed_root = tmp_path / "seed"
        monkeypatch.setattr(model, "FORMAT_SEED_DIR", str(seed_root))
        # The provider's actual model dependency must be this module's
        # instance and the owned seed root must be configured BEFORE any
        # seed I/O: a misbound dependency would silently seed elsewhere
        # (the repository default root) instead of the test's owned tmp
        # root, so assert the configuration coherence up front.
        assert model is ctl.model
        assert model.FORMAT_SEED_DIR == str(seed_root)
        ledger = model.FixtureLedger()
        ledger.set_deadline(600)
        provider = ctl.Provider(
            0,
            ledger,
            model.IssuedRegistry(ledger.budgets.max_requests),
            threading.Lock(),
            scenario="format-capture",
            originals_dir=str(tmp_path / "orig"),
        )
        yield provider, tmp_path
        provider.closed = True
        try:
            provider.listener.close()
        except OSError:
            pass
        _unseal_tree(tmp_path)

    def _provider(self, seed_env: tuple[Any, Path]) -> Any:
        return seed_env[0]

    def _build_root(
        self,
        root: Path,
        tamper: Callable[[Path], object] | None = None,
        extra: dict[str, str | bytes] | None = None,
        dir_mode: int = 0o555,
        file_mode: int = 0o444,
    ) -> None:
        root.mkdir(mode=0o700)
        for name, data in SEED.items():
            (root / name).write_bytes(data)
        if extra is not None:
            for name, kind in extra.items():
                p = root / name
                if kind == "fifo":
                    os.mkfifo(str(p), 0o600)
                elif kind == "dir":
                    p.mkdir()
                elif kind == "symlink":
                    os.symlink(str(root.parent / "symlink-target.txt"), str(p))
                else:
                    assert isinstance(kind, (bytes, bytearray))
                    p.write_bytes(kind)
        for e in os.scandir(root):
            st = os.lstat(e.path)
            if stat_mod.S_ISLNK(st.st_mode):
                continue  # link mode is irrelevant: O_NOFOLLOW -> ELOOP
            os.chmod(e.path, file_mode)
        if tamper is not None:  # defect LAST, after normalizing chmod
            tamper(root)
        os.chmod(root, dir_mode)

    def test_fresh_creation_seals_owned_byte_exact(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        provider.seed_format_seeds()
        root = tmp_path / "seed"
        assert stat_mod.S_IMODE(os.lstat(root).st_mode) == 0o555
        assert os.stat(root).st_uid == os.getuid()
        for name, data in SEED.items():
            f = root / name
            assert stat_mod.S_IMODE(os.lstat(f).st_mode) == 0o444
            assert f.read_bytes() == data

    def test_second_call_refused_preexisting_sealed(self, seed_env: tuple[Any, Path]) -> None:
        provider, _ = seed_env
        provider.seed_format_seeds()
        with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
            provider.seed_format_seeds()

    def test_seal_holds_owner_cannot_write(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        provider.seed_format_seeds()
        with pytest.raises(PermissionError):
            with open(str(tmp_path / "seed" / "read-0"), "wb") as h:
                h.write(b"no")

    def test_preexisting_partial_root_refused(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        root = tmp_path / "seed"
        root.mkdir(mode=0o700)
        (root / "read-0").write_bytes(SEED["read-0"])
        with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
            provider.seed_format_seeds()

    def test_preexisting_foreign_mode_root_refused(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        (tmp_path / "seed").mkdir(mode=0o755)
        with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
            provider.seed_format_seeds()

    def test_preexisting_symlink_root_refused(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        os.symlink(str(tmp_path), str(tmp_path / "seed"))
        with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
            provider.seed_format_seeds()

    @pytest.mark.parametrize(
        ("kind",),
        [
            ("mutated",),
            ("fifo",),
            ("extra",),
            ("symlink-entry",),
            ("missing",),
            ("nonregular",),
        ],
    )
    def test_preexisting_sealed_defect_refused_public(
        self, seed_env: tuple[Any, Path], kind: str
    ) -> None:
        """Every pre-existing sealed shape carries the SAME public
        refusal — the internal per-file tokens are whitebox-only."""
        provider, tmp_path = seed_env
        root = tmp_path / "seed"
        if kind == "mutated":

            def t(d: Path) -> None:
                f = d / "read-0"
                # the defect is constructed while the entry is
                # still writable: the sealed 0444 mode cannot be
                # rewritten by the nonroot test user
                os.chmod(str(f), 0o600)
                f.write_bytes(b"x" * 10)

            self._build_root(root, t)
        elif kind == "fifo":

            def t(d: Path) -> None:
                f = d / "read-0"
                f.unlink()
                os.mkfifo(str(f), 0o444)

            self._build_root(root, t)
        elif kind == "extra":
            self._build_root(root, extra={"extra-entry": b"planted"})
        elif kind == "symlink-entry":

            def t(d: Path) -> None:
                f = d / "stream-piece-0"
                f.unlink()
                os.symlink(str(tmp_path / "symlink-target.txt"), str(f))

            (tmp_path / "symlink-target.txt").write_bytes(b"owned target")
            self._build_root(root, t)
        elif kind == "missing":

            def t(d: Path) -> None:
                (d / "stream-piece-1").unlink()

            self._build_root(root, t)
        elif kind == "nonregular":

            def t(d: Path) -> None:
                f = d / "read-0"
                f.unlink()
                f.mkdir()

            self._build_root(root, t)
        with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
            provider.seed_format_seeds()

    def _wb_root(
        self, tmp_path: Path, name: str, tamper: Callable[[Path], object] | None = None
    ) -> tuple[Path, int]:
        root = tmp_path / f"wb-{name}"
        self._build_root(root, tamper, dir_mode=0o700, file_mode=0o600)
        return root, os.open(str(root), os.O_RDONLY | os.O_DIRECTORY)

    def test_wb_verify_mutated_bytes_copy_mismatch(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        root, fd = self._wb_root(
            tmp_path, "mutate", lambda d: (d / "read-0").write_bytes(b"x" * 10)
        )
        try:
            with pytest.raises(ctl.ControllerError, match="format-seed-copy-mismatch"):
                provider._format_verify_sealed_set(fd, want_file_mode=0o600)
        finally:
            os.close(fd)

    def test_wb_verify_overlong_file_copy_mismatch(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env
        root, fd = self._wb_root(
            tmp_path, "overlong", lambda d: (d / "trunc-0").write_bytes(SEED["trunc-0"] + b"X")
        )
        try:
            with pytest.raises(ctl.ControllerError, match="format-seed-copy-mismatch"):
                provider._format_verify_sealed_set(fd, want_file_mode=0o600)
        finally:
            os.close(fd)

    def test_wb_verify_fifo_entry_untrusted_bounded(self, seed_env: tuple[Any, Path]) -> None:
        provider, tmp_path = seed_env

        def t(d: Path) -> None:
            f = d / "read-0"
            f.unlink()
            os.mkfifo(str(f), 0o444)

        root, fd = self._wb_root(tmp_path, "fifo", t)
        t0 = time.monotonic()
        try:
            with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
                provider._format_verify_sealed_set(fd, want_file_mode=0o600)
        finally:
            os.close(fd)
        assert time.monotonic() - t0 < 10.0  # O_NONBLOCK open: no hang

    @pytest.mark.parametrize(
        ("kind",), [("nonregular",), ("symlink-entry",), ("missing",), ("fmode",)]
    )
    def test_wb_verify_entry_defects_refused(self, seed_env: tuple[Any, Path], kind: str) -> None:
        provider, tmp_path = seed_env
        if kind == "nonregular":

            def t(d: Path) -> None:
                f = d / "read-0"
                f.unlink()
                f.mkdir()

            tamper = t
        elif kind == "symlink-entry":
            (tmp_path / "wb-symlink-target.txt").write_bytes(b"owned target")

            def t(d: Path) -> None:
                f = d / "stream-piece-0"
                f.unlink()
                os.symlink(str(tmp_path / "wb-symlink-target.txt"), str(f))

            tamper = t
        elif kind == "missing":

            def t(d: Path) -> None:
                (d / "stream-piece-1").unlink()

            tamper = t
        elif kind == "fmode":

            def t(d: Path) -> None:
                (d / "stream-piece-0").chmod(0o644)

            tamper = t
        root, fd = self._wb_root(tmp_path, kind, tamper)
        try:
            with pytest.raises(ctl.ControllerError, match="format-seed-untrusted"):
                provider._format_verify_sealed_set(fd, want_file_mode=0o600)
        finally:
            os.close(fd)


# ---------------------------------------------------------------------------
# F2 offered-schema law (durable, pinned native source shape)
# ---------------------------------------------------------------------------

_AP_ABSENT = object()


def _tool_offer(
    name: str,
    properties: dict[str, Any],
    required: list[str],
    additional: Any = _AP_ABSENT,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "required": list(required),
    }
    if additional is not _AP_ABSENT:
        params["additionalProperties"] = additional
    return [{"type": "function", "name": name, "parameters": params}]


# The pinned native shell_spec builders (tag 6aaac694) advertise the
# numeric arguments as JSON schema ``number`` with the parent object
# closed by ``additionalProperties: false`` — the EXACT valid offer
# shape the receiver must accept.
_PINNED_EXEC = _tool_offer(
    "exec_command",
    {
        "cmd": {"type": "string"},
        "yield_time_ms": {"type": "number"},
        "max_output_tokens": {"type": "number"},
    },
    ["cmd"],
    additional=False,
)
_PINNED_POLL = _tool_offer(
    "write_stdin",
    {
        "session_id": {"type": "number"},
        "yield_time_ms": {"type": "number"},
        "max_output_tokens": {"type": "number"},
        "chars": {"type": "string"},
    },
    ["session_id"],
    additional=False,
)
_PINNED_TOOLS = list(_PINNED_EXEC) + list(_PINNED_POLL)

# The legacy synthetic shape (integer types, no additionalProperties)
# must stay accepted: the closed law supports the pinned number form
# AND the integer form.
_INTEGER_EXEC = _tool_offer(
    "exec_command",
    {
        "cmd": {"type": "string"},
        "yield_time_ms": {"type": "integer"},
        "max_output_tokens": {"type": "integer"},
    },
    ["cmd"],
)
_INTEGER_POLL = _tool_offer(
    "write_stdin",
    {
        "session_id": {"type": "integer"},
        "chars": {"type": "string"},
    },
    ["session_id"],
)


def test_f2_pinned_number_exec_offer_accepted() -> None:
    # every closed case's strict integer argument shape is
    # expressible under the pinned number offer
    for spec in model.FORMAT_CASES:
        expected = model.format_expected_exec_arguments(spec)
        assert model.format_offered_tool_available(
            _PINNED_EXEC, model.FORMAT_EXEC_TOOL, expected
        ), spec["case"]


def test_f2_pinned_number_poll_offer_accepted() -> None:
    assert model.format_offered_tool_available(
        _PINNED_POLL, model.FORMAT_POLL_TOOL, model.format_expected_poll_arguments(77)
    )


def test_f2_integer_offer_still_accepted() -> None:
    for spec in model.FORMAT_CASES:
        assert model.format_offered_tool_available(
            _INTEGER_EXEC, model.FORMAT_EXEC_TOOL, model.format_expected_exec_arguments(spec)
        ), spec["case"]
    assert model.format_offered_tool_available(
        _INTEGER_POLL, model.FORMAT_POLL_TOOL, model.format_expected_poll_arguments(77)
    )


def test_f2_additional_properties_true_accepted() -> None:
    # either BOOLEAN form can exclude none of the exactly declared
    # closed keys
    tools = _tool_offer(
        "exec_command",
        {
            "cmd": {"type": "string"},
            "yield_time_ms": {"type": "number"},
            "max_output_tokens": {"type": "number"},
        },
        ["cmd"],
        additional=True,
    )
    for spec in model.FORMAT_CASES:
        assert model.format_offered_tool_available(
            tools, model.FORMAT_EXEC_TOOL, model.format_expected_exec_arguments(spec)
        ), spec["case"]


@pytest.mark.parametrize("bad", [{"type": "object"}, "false", None, 0, 1, 1.0, [False]])
def test_f2_additional_properties_non_boolean_refused(bad: Any) -> None:
    tools = _tool_offer(
        "exec_command",
        {"cmd": {"type": "string"}},
        ["cmd"],
        additional=bad,
    )
    assert not model.format_offered_tool_available(
        tools, model.FORMAT_EXEC_TOOL, model.format_expected_exec_arguments(model.FORMAT_CASES[0])
    )


@pytest.mark.parametrize(
    "keyword, value",
    [
        ("not", {}),
        ("allOf", [{}]),
        ("anyOf", [{}]),
        ("oneOf", [{}]),
        ("$ref", "#"),
        ("maxProperties", 1),
        ("patternProperties", {}),
        ("dependentRequired", {}),
    ],
)
def test_f2_parent_constraint_keyword_refused(keyword: str, value: Any) -> None:
    # an unsupported parent validation keyword could exclude the
    # closed call without any property-level trace: refused
    tools = _tool_offer(
        "exec_command",
        {"cmd": {"type": "string"}},
        ["cmd"],
    )
    tools[0]["parameters"][keyword] = value
    assert not model.format_offered_tool_available(
        tools, model.FORMAT_EXEC_TOOL, model.format_expected_exec_arguments(model.FORMAT_CASES[0])
    )


@pytest.mark.parametrize("bound", [4.5, 4.0, None, True, "2", -1])
def test_f2_malformed_length_bound_refused(bound: Any) -> None:
    # fractional float, explicit null, bool, string or negative
    # length bounds are malformed schema, never a compatible
    # rounding of the closed length
    prop = {"type": "string", "minLength": bound}
    assert not model._format_offered_property_ok(prop, "abcd")
    prop = {"type": "string", "maxLength": bound}
    assert not model._format_offered_property_ok(prop, "abcd")


def test_f2_integer_length_bound_accepted() -> None:
    assert model._format_offered_property_ok(
        {"type": "string", "minLength": 2, "maxLength": 10}, "abcd"
    )
    assert not model._format_offered_property_ok({"type": "string", "minLength": 5}, "abcd")
    assert not model._format_offered_property_ok({"type": "string", "maxLength": 3}, "abcd")


def test_f2_huge_integer_bound_closed() -> None:
    # huge JSON integers stay in their type: closed refuse/accept
    # decisions, never an OverflowError leak
    assert not model._format_offered_property_ok({"type": "integer", "minimum": 10**400}, 500)
    assert not model._format_offered_property_ok(
        {"type": "integer", "exclusiveMinimum": 10**400}, 500
    )
    assert model._format_offered_property_ok({"type": "integer", "maximum": 10**400}, 500)
    assert not model._format_offered_property_ok({"type": "integer", "multipleOf": 10**400}, 500)
    assert model._format_offered_property_ok({"type": "string", "maxLength": 10**400}, "abcd")


@pytest.mark.parametrize("bound", [float("nan"), float("inf"), float("-inf"), True, "1"])
def test_f2_nonfinite_or_nonscalar_numeric_bound_refused(bound: Any) -> None:
    for key in (
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
    ):
        assert not model._format_offered_property_ok({"type": "integer", key: bound}, 500)


def test_f2_explicit_null_const_enum_refused() -> None:
    # key presence, never .get() absence: an explicit null
    # constraint is malformed, not a vacuous constraint
    assert not model._format_offered_property_ok({"type": "string", "const": None}, "abcd")
    assert not model._format_offered_property_ok({"type": "string", "enum": None}, "abcd")
    assert not model._format_offered_property_ok({"type": "integer", "const": None}, 500)
    assert not model._format_offered_property_ok({"type": "integer", "enum": None}, 500)


def test_f2_const_enum_type_strict() -> None:
    # a float standing in for the strict integer closed value is
    # a different JSON type, never a compatible member
    assert model._format_offered_property_ok({"type": "string", "const": "abcd"}, "abcd")
    assert not model._format_offered_property_ok({"type": "string", "const": "abce"}, "abcd")
    assert model._format_offered_property_ok({"type": "string", "enum": ["abcd", "x"]}, "abcd")
    assert not model._format_offered_property_ok({"type": "string", "enum": ["abce"]}, "abcd")
    assert not model._format_offered_property_ok({"type": "integer", "const": 5.0}, 5)
    assert not model._format_offered_property_ok({"type": "integer", "enum": [5.0, 4]}, 5)
    assert model._format_offered_property_ok({"type": "integer", "const": 5}, 5)
    assert model._format_offered_property_ok({"type": "integer", "enum": [5, 4]}, 5)


def test_f2_enum_unbounded_refused() -> None:
    enum = ["a"] * (model.DIAGNOSTIC_MAX_REQUIRED_FIELDS + 1)
    assert not model._format_offered_property_ok({"type": "string", "enum": enum}, "abcd")
    assert model._format_offered_property_ok(
        {"type": "string", "enum": ["abcd"] + ["b"] * (model.DIAGNOSTIC_MAX_REQUIRED_FIELDS - 1)},
        "abcd",
    )


def test_f2_number_integer_type_law() -> None:
    # the pinned number form admits the strict integer closed
    # value; a bool is never the closed integer value
    assert model._format_offered_property_ok({"type": "number"}, 500)
    assert model._format_offered_property_ok({"type": "integer"}, 500)
    assert not model._format_offered_property_ok({"type": "boolean"}, 500)
    assert not model._format_offered_property_ok({"type": "string"}, 500)
    assert not model._format_offered_property_ok({"type": None}, 500)
    assert not model._format_offered_property_ok({"type": "number"}, True)
    assert not model._format_offered_property_ok({"type": "integer"}, True)
    assert not model._format_offered_property_ok({"type": "number"}, 5.5)


def test_f2_unknown_tool_name_fails_closed() -> None:
    assert not model.format_offered_tool_available(_PINNED_TOOLS, "run_command", {"cmd": "true"})


def test_f2_duplicate_tool_entry_refused() -> None:
    tools = list(_PINNED_TOOLS) + [dict(_PINNED_EXEC[0])]
    assert not model.format_offered_tool_available(
        tools, model.FORMAT_EXEC_TOOL, model.format_expected_exec_arguments(model.FORMAT_CASES[0])
    )


@pytest.mark.parametrize(
    "required, spec_index, accepted",
    [
        ([], 0, False),  # the known closed required argument is demanded
        (["cmd", "nonexistent"], 0, False),  # beyond the closed shape
        (["cmd", "cmd"], 0, False),  # duplicate
        ([1], 0, False),  # non-string entry
        (["cmd", "yield_time_ms"], 0, False),  # not a closed key of the read case
        (["cmd", "yield_time_ms"], 1, True),  # a closed key of the stream case
    ],
)
def test_f2_required_core_law(required: list[Any], spec_index: int, accepted: bool) -> None:
    tools = _tool_offer(
        "exec_command",
        {
            "cmd": {"type": "string"},
            "yield_time_ms": {"type": "number"},
            "max_output_tokens": {"type": "number"},
        },
        required,
    )
    assert (
        model.format_offered_tool_available(
            tools,
            model.FORMAT_EXEC_TOOL,
            model.format_expected_exec_arguments(model.FORMAT_CASES[spec_index]),
        )
        is accepted
    )


# ---------------------------------------------------------------------------
# F5 deadline-anchor and truthful count law (pure)
# ---------------------------------------------------------------------------


def test_f5_anchor_missing_env_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLAIF_FIXTURE_DEADLINE_ABS", raising=False)
    with pytest.raises(ctl.ControllerError, match="format-deadline-unbound"):
        ctl.format_clamped_deadline_anchor(600)


@pytest.mark.parametrize("raw", ["abc", "nan", "inf", "-inf", "-5", "0", "1e999"])
def test_f5_anchor_malformed_refused(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", raw)
    with pytest.raises(ctl.ControllerError, match="format-deadline-unbound"):
        ctl.format_clamped_deadline_anchor(600)


def test_f5_anchor_past_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() - 10))
    with pytest.raises(ctl.ControllerError, match="format-deadline-expired"):
        ctl.format_clamped_deadline_anchor(600)


def test_f5_anchor_clamped_at_one_clock_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = time.monotonic()
    anchor = now + 100
    monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(anchor))
    # the relative bound is looser: the anchor itself is returned,
    # exactly, with no re-derivation at a later clock reading
    assert ctl.format_clamped_deadline_anchor(600) == anchor
    # the relative bound is tighter: ONE clock read plus the
    # relative seconds, strictly between now and the anchor
    clamped = ctl.format_clamped_deadline_anchor(50)
    assert now + 49 < clamped < anchor


def test_f5_set_deadline_absolute_stores_anchor_no_extension() -> None:
    t = {"v": 1000.0}
    ledger = model.FixtureLedger(clock=lambda: t["v"])
    ledger.set_deadline_absolute(1100.0)
    # the anchor IS the deadline: a later clock reading re-derives
    # nothing
    assert ledger.deadline_monotonic() == 1100.0
    t["v"] = 1090.0
    assert ledger.remaining_seconds() == 10.0
    ledger.require_within_deadline()
    t["v"] = 1100.0
    with pytest.raises(model.BudgetExceeded):
        ledger.require_within_deadline()


def test_f5_set_deadline_absolute_set_once() -> None:
    t = {"v": 0.0}
    ledger = model.FixtureLedger(clock=lambda: t["v"])
    ledger.set_deadline_absolute(100.0)
    with pytest.raises(model.FixtureError, match="set once"):
        ledger.set_deadline_absolute(200.0)


def test_f5_set_deadline_absolute_past_refused() -> None:
    t = {"v": 100.0}
    ledger = model.FixtureLedger(clock=lambda: t["v"])
    with pytest.raises(model.FixtureError, match="already past"):
        ledger.set_deadline_absolute(100.0)


def test_f5_set_deadline_absolute_lifetime_bound() -> None:
    t = {"v": 0.0}
    ledger = model.FixtureLedger(clock=lambda: t["v"])
    with pytest.raises(model.BudgetExceeded, match="lifetime"):
        ledger.set_deadline_absolute(ledger.budgets.lifetime_seconds + 1.0)


def test_f5_count_law_literal_counters() -> None:
    rec = build_positive()
    model.validate_format_snapshot_record(rec)
    # the closed trace: seven model POSTs (positions 0..6) and the
    # exporter's two closed charged commands
    assert rec["model_posts"] == 7
    assert rec["controller_ledger"]["requests"] == 9


def test_f5_count_law_mismatch_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["model_posts"] = 6

    expect_refusal(mutate, "format-ledger-count")


def test_f5_count_law_zero_posts_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["model_posts"] = 0

    expect_refusal(mutate, "format-ledger-bound")


def test_f5_count_law_over_bound_posts_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["model_posts"] = 21

    expect_refusal(mutate, "format-ledger-bound")


def test_f5_count_law_position_equal_posts_refused() -> None:
    def mutate(rec: dict[str, Any]) -> None:
        rec["cases"][3]["results"][0]["result_position"] = rec["model_posts"]

    expect_refusal(mutate, "format-coordinate-truth")


# ---------------------------------------------------------------------------
# F4 receiver transaction (REAL Provider over real loopback, FAKE
# subject client; no native, no Docker, no admission, no host scan)
# ---------------------------------------------------------------------------

_FMT_SESSION = 77


def _fmt_tokens(nbytes: int) -> str:
    return str(model._approx_token_count_bytes(nbytes))


def _w_read() -> str:
    return (
        "Wall time: 0.0200 seconds\nProcess exited with code 0\n"
        f"Original token count: {_fmt_tokens(len(SEED['read-0']))}\nOutput:\n{_READ0}"
    )


def _w_stream_initial() -> str:
    return (
        "Wall time: 0.5000 seconds\n"
        f"Process running with session ID {_FMT_SESSION}\n"
        f"Original token count: {_fmt_tokens(len(SEED['stream-piece-0']))}\nOutput:\n{_P0}"
    )


def _w_poll_running() -> str:
    return (
        "Wall time: 2.5000 seconds\n"
        f"Process running with session ID {_FMT_SESSION}\n"
        f"Original token count: {_fmt_tokens(len(SEED['stream-piece-1']))}\nOutput:\n{_P1}"
    )


def _w_poll_final() -> str:
    return (
        "Wall time: 4.5000 seconds\nProcess exited with code 0\n"
        f"Original token count: {_fmt_tokens(len(SEED['stream-piece-2']))}\nOutput:\n{_P2}"
    )


def _w_empty() -> str:
    return "Wall time: 0.0050 seconds\nProcess exited with code 0\nOutput:\n"


def _w_truncated() -> str:
    out = model.format_truncate_text(_T0, model.FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS)
    return (
        "Wall time: 0.0300 seconds\nProcess exited with code 0\n"
        f"Original token count: {_fmt_tokens(len(SEED['trunc-0']))}\nOutput:\n{out}"
    )


def _fmt_make_provider(
    tmp_path: Path,
    tag: str,
    clock: Any = None,
    auth_token: str | None = None,
) -> tuple[Any, threading.Lock, Any, str]:
    if clock is None:
        ledger = model.FixtureLedger()
        ledger.set_deadline(600)
    else:
        ledger = model.FixtureLedger(clock=clock)
    lock = threading.Lock()
    registry = model.IssuedRegistry(ledger.budgets.max_requests)
    provider = ctl.Provider(
        0,
        ledger,
        registry,
        lock,
        scenario="format-capture",
        originals_dir=str(tmp_path / f"originals-{tag}"),
        exporter_uid=model.CONTROLLER_UID,
        auth_token=auth_token,
    )
    thread = threading.Thread(target=provider.serve, daemon=True)
    provider.accept_thread = thread
    thread.start()
    return provider, lock, ledger, str(provider.port)


def _fmt_close(provider: Any) -> None:
    """Owned teardown for THIS test's provider: flag closed,
    close the listener, then JOIN this test's own accept and
    handler threads so no thread the test started outlives its
    finally block (the previous close left the accept thread
    unjoined and a provider started before a raising anchor
    setup could leak)."""
    provider.closed = True
    try:
        provider.listener.close()
    except OSError:
        pass
    accept = provider.accept_thread
    if accept is not None:
        accept.join(timeout=5)
        assert not accept.is_alive(), "accept thread alive after close"
    with provider.lock:
        handlers = [t for t in provider.handlers if t is not None and t.is_alive()]
    for thread in handlers:
        thread.join(timeout=5)
        assert not thread.is_alive(), "handler thread alive after close"


def _fmt_post(
    port: str, body: dict[str, Any] | str, auth: str | None = None
) -> tuple[int | None, bytes]:
    data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    auth_line = f"Authorization: {auth}\r\n" if auth is not None else ""
    s = socket.create_connection(("127.0.0.1", int(port)), timeout=5)
    try:
        s.sendall(
            (
                f"POST /v1/responses HTTP/1.1\r\nHost: local\r\n"
                f"{auth_line}Content-Length: {len(data)}\r\n\r\n"
            ).encode()
            + data
        )
        chunks: list[bytes] = []
        while True:
            b = s.recv(65536)
            if not b:
                break
            chunks.append(b)
    finally:
        s.close()
    raw = b"".join(chunks)
    if not raw:
        # A closed connection with NO response is the CORRECT
        # closed outcome once the original owner END has
        # expired: the output ledger can no longer account a
        # frame, so the fixed closed failure sends nothing.
        # It is not a protocol failure and must never be turned
        # into a required 400 by the caller.
        return None, raw
    status = int(raw.split(b" ", 2)[1])
    return status, raw


def _fmt_items(raw: bytes) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in raw.split(b"\n"):
        if line.startswith(b"data: "):
            obj = json.loads(line[6:].decode())
            if obj.get("type") == "response.output_item.done":
                items.append(obj["item"])
    return items


def _fmt_user() -> dict[str, Any]:
    return {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": "run the closed format scenario"}],
    }


def _fmt_result_item(call_id: str, wrapper: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": call_id, "output": wrapper}


def _fmt_offer_spy(
    monkeypatch: pytest.MonkeyPatch, cross: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Count every ACTUAL offered-tool verification the real
    receiver performs at the real predicate boundary, with an
    optional spy-driven crossing: when ``cross`` is given as
    {"t": <clock state>, "end": <END anchor>}, the moment a
    LATE second post-commit verification is observed - the
    call count deviates from the closed one-per-POST
    staging/issuance pattern (calls > commits + 2) - the
    original END is crossed (t["v"] := end + 1), so any later
    deadline read in that POST or the next refuses.  A
    correct receiver never crosses: exactly one verification
    per POST, always staged before its commit."""
    state = {"calls": 0, "commits": 0}
    real = model.format_offered_tool_available

    def spy(tools: object, tool_name: str, expected_arguments: dict[str, Any]) -> bool:
        state["calls"] += 1
        if cross is not None and state["calls"] > state["commits"] + 2:
            cross["t"]["v"] = cross["end"] + 1.0
        available = real(tools, tool_name, expected_arguments)
        assert isinstance(available, bool)
        return available

    monkeypatch.setattr(model, "format_offered_tool_available", spy)
    return state


def _fmt_mark_commits(provider: Any, state: dict[str, Any]) -> None:
    """Count every SEMANTIC result commit of this provider
    (the retained verified frame) so the offer spy can
    distinguish the current POST's ONE staged verification
    from any LATE post-commit second verification."""
    original = provider._format_retain_result

    def marked(*args: Any, **kwargs: Any) -> None:
        original(*args, **kwargs)
        state["commits"] += 1

    provider._format_retain_result = marked


def test_f4_missing_poll_offer_adopts_nothing(tmp_path: Path) -> None:
    # the first completed read commits under the VALID FULL
    # offer; the ACTUAL next call after it is the stream case's
    # exec, and only the STREAM transition (initial running
    # result -> next poll) needs the closed poll tool.  That
    # valid stream frame under an offer WITHOUT the poll tool
    # stage-refuses with no adoption; the frozen history stays
    # valid for the later valid POST.
    provider, _lock, _ledger, port = _fmt_make_provider(tmp_path, "f4-nopoll")
    try:
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0 = _fmt_items(raw)[0]
        assert e0["type"] == "function_call" and e0["name"] == "exec_command"
        # the first read completes under the valid full offer
        status, raw = _fmt_post(
            port,
            {
                "input": [e0, _fmt_result_item(e0["call_id"], _w_read())],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        assert e1["name"] == "exec_command"
        assert len(provider._fmt_issued) == 2
        assert provider._fmt_case_index == 1
        # the stream's initial RUNNING frame is valid, but THIS
        # offer lacks the closed poll tool: the staged refusal
        # adopts nothing
        body = {
            "input": [
                e0,
                _fmt_result_item(e0["call_id"], _w_read()),
                e1,
                _fmt_result_item(e1["call_id"], _w_stream_initial()),
            ],
            "tools": list(_PINNED_EXEC),
        }
        status, raw = _fmt_post(port, body)
        assert status == 400, raw[:300]
        assert b"format-tools-unoffered" in raw
        assert len(provider._fmt_retained_results) == 1
        assert provider._fmt_outstanding["call_id"] == e1["call_id"]
        assert provider._fmt_session is None and provider._fmt_cum == 0
        assert provider._fmt_case_index == 1
        assert provider._fmt_cases[1]["status"] == "pending"
        assert provider._fmt_cases[1]["results"] == []
        assert provider._fmt_cases[1]["session_id"] is None
        assert len(provider._fmt_issued) == 2
        assert provider._fmt_polls == 0
        assert provider._fmt_posts == 3  # the refused POST is consumed
        # the same POST under the valid full offer now commits:
        # the outstanding call was kept outstanding, never
        # stranded
        status, raw = _fmt_post(port, {**body, "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        poll = _fmt_items(raw)[0]
        assert poll["name"] == "write_stdin"
        assert len(provider._fmt_issued) == 3
        assert provider._fmt_polls == 1
        assert len(provider._fmt_retained_results) == 2
        assert provider._fmt_session == _FMT_SESSION
        assert provider._fmt_cum == len(SEED["stream-piece-0"])
    finally:
        _fmt_close(provider)


def test_f4_missing_next_exec_offer_adopts_nothing(tmp_path: Path) -> None:
    # the positive prefix stops BEFORE the empty case's result
    # so the ACTUAL empty case (case2) is the one outstanding;
    # its valid empty completion needs the NEXT case's exec in
    # the offer - a poll-only offer stage-refuses with no
    # adoption, and the same valid body under the full offer
    # (clock still before END) commits.
    provider, _lock, _ledger, port = _fmt_make_provider(tmp_path, "f4-noexec")
    try:
        wrappers = [
            _w_read(),
            _w_stream_initial(),
            _w_poll_running(),
            _w_poll_final(),
        ]
        calls: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        calls.append(_fmt_items(raw)[0])
        for wrapper in wrappers:
            status, raw = _fmt_post(
                port,
                {
                    "input": calls + results + [_fmt_result_item(calls[-1]["call_id"], wrapper)],
                    "tools": _PINNED_TOOLS,
                },
            )
            assert status == 200, (wrapper[:40], raw[:300])
            results.append(_fmt_result_item(calls[-1]["call_id"], wrapper))
            calls.append(_fmt_items(raw)[0])
        # the stream case just completed and the EMPTY case's
        # exec is outstanding; the empty completion needs the
        # NEXT (truncated) case's exec in THIS offer
        empty_id = calls[-1]["call_id"]
        status, raw = _fmt_post(
            port,
            {
                "input": calls + results + [_fmt_result_item(empty_id, _w_empty())],
                "tools": list(_PINNED_POLL),
            },
        )
        assert status == 400, raw[:300]
        assert b"format-tools-unoffered" in raw
        # no case advance, no duplicate retention, no issuance
        assert provider._fmt_case_index == 2
        assert provider._fmt_cases[2]["status"] == "pending"
        assert provider._fmt_cases[2]["results"] == []
        assert len(provider._fmt_issued) == 5
        assert provider._fmt_polls == 2
        assert len(provider._fmt_retained_results) == 4
        assert provider._fmt_outstanding["call_id"] == empty_id
        assert provider._fmt_posts == 6
        # a later valid POST completes the advance
        status, raw = _fmt_post(
            port,
            {
                "input": calls + results + [_fmt_result_item(empty_id, _w_empty())],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        assert _fmt_items(raw)[0]["name"] == "exec_command"
        assert len(provider._fmt_issued) == 6
        assert provider._fmt_case_index == 3
        assert len(provider._fmt_retained_results) == 5
    finally:
        _fmt_close(provider)


def test_f4_expired_after_verify_before_commit_adopts_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # running frame -> poll continuation: the anchor is set
    # while the clock is inside the END, and the clock crosses
    # the original END DURING the actual offer-verification
    # return (spy-driven, after connection/admission) - the
    # staged verification ran, so an early connection refusal
    # cannot fake this boundary.  The output ledger is expired
    # at the fence, so the HTTP closes WITHOUT a response: the
    # correct closed outcome is the empty wire plus state
    # equality (no result/session/offset adopted), never a
    # required 400 after budget expiry.  No clock rewind, no
    # END refresh; the independent unexpired positive control
    # runs in a SEPARATELY owned fresh synthetic world, not a
    # revived same attempt.
    t = {"v": 0.0}
    end = 100.0
    calls = {"n": 0}
    real = model.format_offered_tool_available

    def spy(tools: object, tool_name: str, expected_arguments: dict[str, Any]) -> bool:
        calls["n"] += 1
        if calls["n"] == 3:  # this staged poll-continuation verify
            t["v"] = end + 0.5
        available = real(tools, tool_name, expected_arguments)
        assert isinstance(available, bool)
        return available

    monkeypatch.setattr(model, "format_offered_tool_available", spy)
    provider, _lock, ledger, port = _fmt_make_provider(
        tmp_path, "f4-exp-commit", clock=lambda: t["v"]
    )
    try:
        ledger.set_deadline_absolute(end)  # 0.0 < END at set time
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0 = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port,
            {
                "input": [e0, _fmt_result_item(e0["call_id"], _w_read())],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        assert e1["name"] == "exec_command"
        # the stream's initial RUNNING frame is valid; the END
        # crosses the staged verification's return, BEFORE the
        # commit fence
        body = {
            "input": [
                e0,
                _fmt_result_item(e0["call_id"], _w_read()),
                e1,
                _fmt_result_item(e1["call_id"], _w_stream_initial()),
            ],
            "tools": _PINNED_TOOLS,
        }
        status, raw = _fmt_post(port, body)
        # the output ledger is expired: the fixed closed
        # failure sends nothing (the 400 frame itself could
        # not be accounted) - the empty wire is the correct
        # outcome, never a required 400
        assert status is None, raw[:300]
        # the ACTUAL verification ran three times (initial
        # issuance, read transition staging, this staged poll
        # continuation) - not an early connection/admission
        # refusal
        assert calls["n"] == 3
        assert ledger.deadline_expired() is True
        # the verified frame adopted NOTHING: the targeted
        # close reason is the expired fence after the staged
        # verification, proven by the frozen state
        assert len(provider._fmt_retained_results) == 1
        assert provider._fmt_session is None and provider._fmt_cum == 0
        assert provider._fmt_case_index == 1
        assert provider._fmt_cases[1]["status"] == "pending"
        assert provider._fmt_cases[1]["session_id"] is None
        assert len(provider._fmt_issued) == 2
        assert provider._fmt_polls == 0
        assert provider._fmt_outstanding["call_id"] == e1["call_id"]
        assert provider._fmt_posts == 3
    finally:
        _fmt_close(provider)
    # the independent unexpired positive control: a
    # SEPARATELY owned fresh world, the SAME frame and offer,
    # the clock never crossing the END
    t2 = {"v": 50.0}
    provider2, _lock2, ledger2, port2 = _fmt_make_provider(
        tmp_path, "f4-exp-commit-fresh", clock=lambda: t2["v"]
    )
    try:
        ledger2.set_deadline_absolute(end)  # 50.0 < END, never crossed
        status, raw = _fmt_post(port2, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0b = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port2,
            {
                "input": [e0b, _fmt_result_item(e0b["call_id"], _w_read())],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        e1b = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port2,
            {
                "input": [
                    e0b,
                    _fmt_result_item(e0b["call_id"], _w_read()),
                    e1b,
                    _fmt_result_item(e1b["call_id"], _w_stream_initial()),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        poll = _fmt_items(raw)[0]
        assert poll["name"] == "write_stdin"
        assert len(provider2._fmt_issued) == 3
        assert provider2._fmt_polls == 1
        assert len(provider2._fmt_retained_results) == 2
        assert provider2._fmt_session == _FMT_SESSION
        assert provider2._fmt_cum == len(SEED["stream-piece-0"])
        assert calls["n"] == 6  # the fresh world's three verifications
    finally:
        _fmt_close(provider2)


def test_f4_expired_initial_offer_adopts_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # the anchor is set while the clock is inside the END, and
    # the clock crosses the original END DURING the actual
    # initial offer-verification return (spy-driven, after
    # connection/admission): the ACTUAL verification ran, so
    # an early connection refusal cannot fake this boundary.
    # The output ledger is expired at the initial issuance
    # gate, so the HTTP closes WITHOUT a response - the
    # correct closed outcome is the empty wire plus NO
    # issuance/outstanding/case adoption, never a required
    # 400 after budget expiry.  No rewind, no END refresh;
    # the unexpired positive control is a separately owned
    # fresh world.
    t = {"v": 0.0}
    end = 100.0
    calls = {"n": 0}
    real = model.format_offered_tool_available

    def spy(tools: object, tool_name: str, expected_arguments: dict[str, Any]) -> bool:
        calls["n"] += 1
        if calls["n"] == 1:  # the initial issuance's verification
            t["v"] = end + 0.5
        available = real(tools, tool_name, expected_arguments)
        assert isinstance(available, bool)
        return available

    monkeypatch.setattr(model, "format_offered_tool_available", spy)
    provider, _lock, ledger, port = _fmt_make_provider(
        tmp_path, "f4-exp-initial", clock=lambda: t["v"]
    )
    try:
        ledger.set_deadline_absolute(end)  # 0.0 < END at set time
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status is None, raw[:300]  # expired: closed, no response
        # the actual verification ran: not an early connection
        # or admission refusal
        assert calls["n"] == 1
        assert ledger.deadline_expired() is True
        assert provider._fmt_issued == []
        assert provider._fmt_outstanding is None
        assert provider._fmt_cases == []
        assert provider._fmt_state == "awaiting-first-post"
        assert provider._fmt_posts == 1  # the refused POST is consumed
    finally:
        _fmt_close(provider)
    t2 = {"v": 50.0}
    provider2, _lock2, ledger2, port2 = _fmt_make_provider(
        tmp_path, "f4-exp-initial-fresh", clock=lambda: t2["v"]
    )
    try:
        ledger2.set_deadline_absolute(end)  # 50.0 < END, never crossed
        status, raw = _fmt_post(port2, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        assert len(provider2._fmt_issued) == 1
        assert provider2._fmt_state == "awaiting-result"
    finally:
        _fmt_close(provider2)


def test_f4_no_deadline_read_after_commit_late_second_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # the LATE SECOND-CHECK boundary, proven behaviorally:
    # every ACTUAL offered-tool verification is counted at the
    # real predicate boundary, and the monotonic fake clock
    # crosses the original END ONLY if a late post-commit
    # second verification is observed (the spy-driven
    # crossing) - a correct receiver completes the closed
    # exchange 200 with the base never crossed, while any
    # post-commit re-verification crosses the END and breaks
    # the exchange (an expired refusal or suppressed frame
    # after state advance).  No exact interpreter/socket
    # read-count formula; the output-deadline accounting is
    # never dropped to fit one.
    t = {"v": 0.0}
    end = 100.0
    state = _fmt_offer_spy(monkeypatch, cross={"t": t, "end": end})
    provider, _lock, ledger, port = _fmt_make_provider(tmp_path, "f4-late2nd", clock=lambda: t["v"])
    _fmt_mark_commits(provider, state)
    try:
        ledger.set_deadline_absolute(end)  # 0.0 < END at set time
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        first = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port,
            {
                "input": [first, _fmt_result_item(first["call_id"], _w_read())],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    first,
                    _fmt_result_item(first["call_id"], _w_read()),
                    e1,
                    _fmt_result_item(e1["call_id"], _w_stream_initial()),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        # the closed exchange committed end to end
        assert len(provider._fmt_issued) == 3
        assert provider._fmt_polls == 1
        assert len(provider._fmt_retained_results) == 2
        assert provider._fmt_session == _FMT_SESSION
        assert provider._fmt_cum == len(SEED["stream-piece-0"])
        assert provider._fmt_cases[0]["status"] == "completed"
        assert provider._fmt_case_index == 1
        # the predicate-count guard: EXACTLY ONE actual offer
        # verification per POST (the initial issuance, then the
        # staged continuation of each result POST), no second
        # post-commit verification - and the spy-driven
        # crossing never fired (the base never crossed END)
        assert state["calls"] == 3, state
        assert state["commits"] == 2, state
        assert t["v"] == 0.0
    finally:
        _fmt_close(provider)


def test_f4_positive_counters_end_to_end(tmp_path: Path) -> None:
    # the real receiver plus the real exporter: the literal
    # separate counters of the closed trace (the durable port of
    # the private loopback probe's positive, with the ACTUAL
    # counters asserted rather than the inspected-flow derivation)
    provider, lock, ledger, port = _fmt_make_provider(tmp_path, "f4-positive")
    sock_path = str(tmp_path / "f4-positive.sock")
    exporter: Any = None
    exporter_thread = None
    try:
        wrappers = [
            _w_read(),
            _w_stream_initial(),
            _w_poll_running(),
            _w_poll_final(),
            _w_empty(),
            _w_truncated(),
        ]
        calls: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        calls.append(_fmt_items(raw)[0])
        for i, wrapper in enumerate(wrappers):
            status, raw = _fmt_post(
                port,
                {
                    "input": calls + results + [_fmt_result_item(calls[-1]["call_id"], wrapper)],
                    "tools": _PINNED_TOOLS,
                },
            )
            assert status == 200, (i, raw[:300])
            results.append(_fmt_result_item(calls[-1]["call_id"], wrapper))
            items = _fmt_items(raw)
            if i < len(wrappers) - 1:
                calls.append(items[0])
        assert items[0]["type"] == "message"
        assert items[0]["content"][0]["text"] == ctl.FIXED_FINAL_TEXT
        # a further POST after the terminal state is scenario-bounded
        status, raw = _fmt_post(port, {"input": calls + results, "tools": _PINNED_TOOLS})
        assert status == 400 and b"scenario-bounded" in raw, (status, raw[:200])
        # the ACTUAL consumed model-POST counter: seven accepted
        # main POSTs plus the one post-terminal refusal
        assert provider._fmt_posts == 8
        # the real exporter over its protected socket (injected
        # synthetic process scans: hermetic).  The test's OWN
        # exporter thread and server socket are tracked and
        # closed/joined in the finally; every framed receive
        # is deadline-bounded through the export client's own
        # helpers (a closed peer raises, never spins).
        exporter = ctl.Exporter(
            provider, ledger, lock, "main", socket_path=sock_path, trusted_uid=os.getuid()
        )
        exporter_thread = threading.Thread(target=exporter.serve_forever, daemon=True)
        exporter_thread.start()
        time.sleep(0.1)
        provider.quiesce(None, subject_scan=lambda: 0, tools_scan=lambda _peer: 0)
        deadline = time.monotonic() + 5
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect(sock_path)
            s.sendall(b"quiesce\n")
            line = exp._recv_line(s, deadline, 16384)
        finally:
            s.close()
        assert line.startswith(b"quiesce-ok "), line
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect(sock_path)
            s.sendall(b"export\n")
            header = exp._recv_exact(s, deadline, 4)
            (length,) = struct.unpack(">I", header)
            # the declared serialized length is closed BEFORE any
            # receive of the body: the snapshot's own byte law
            assert length <= model.FORMAT_SNAPSHOT_MAX_BYTES, length
            payload = exp._recv_exact(s, deadline, length)
            digest = exp._recv_exact(s, deadline, 64)
        finally:
            s.close()
        assert digest.decode() == hashlib.sha256(payload).hexdigest()
        selected = exp.validate_selected_payload(payload)
        assert selected["record"] == model.SCHEMA_FORMAT_EXPORT
        snap = selected["snapshot"]
        assert [c["case"] for c in snap["cases"]] == [spec["case"] for spec in model.FORMAT_CASES]
        # the literal separate counters: 8 model POSTs, the two
        # closed charged commands, two polls, six issued calls
        assert snap["model_posts"] == 8
        assert snap["controller_ledger"]["requests"] == 10
        assert snap["polls"] == 2
        assert len(snap["issued_calls"]) == 6
        assert snap["final_state"] == "done"
        assert snap["cases"][1]["session_id"] == _FMT_SESSION
        exec_calls = [c for c in snap["issued_calls"] if c["name"] == "exec_command"]
        poll_calls = [c for c in snap["issued_calls"] if c["name"] == "write_stdin"]
        assert all(
            model.format_arguments_exact(c["arguments"], model.format_expected_exec_arguments(spec))
            for c, spec in zip(exec_calls, model.FORMAT_CASES, strict=True)
        )
        assert all(c["arguments"] == {"session_id": _FMT_SESSION, "chars": ""} for c in poll_calls)
        assert all(type(c["arguments"]["session_id"]) is int for c in poll_calls)
    finally:
        # owned teardown: this test's OWN exporter server and
        # thread first, and the provider teardown in the OUTER
        # finally so a failed exporter-join assertion can never
        # skip _fmt_close
        try:
            if exporter_thread is not None:
                try:
                    exporter.server.close()
                except OSError:
                    pass
                exporter_thread.join(timeout=5)
                assert not exporter_thread.is_alive()
        finally:
            _fmt_close(provider)


def _w_stream_frame(data: str, session: int | None, exit_code: int | None, wall: str) -> str:
    """The closed wrapper form for a stream frame with
    arbitrary (test-chosen) output bytes, session and
    completion state: the per-frame token line always
    matches the frame's OWN observed bytes."""
    lines_ = [f"Wall time: {wall} seconds"]
    if exit_code is not None:
        lines_.append(f"Process exited with code {exit_code}")
    if session is not None:
        lines_.append(f"Process running with session ID {session}")
    lines_.append(f"Original token count: {_fmt_tokens(len(data.encode('utf-8')))}")
    return "\n".join(lines_) + "\nOutput:\n" + data


def test_f3_format_causal_seam_equal_pre_issue_positions_refused(
    tmp_path: Path,
) -> None:
    # F3 layer: the format receiver's ACTUAL causal guard at
    # the real _route seam.  A TCP client cannot allocate a
    # position equal to or earlier than its own issuance, so
    # the seam is driven with the controlled positions an
    # overtaken or raced allocation would present: the exact
    # matching result refuses as closed with the state
    # unchanged, and the later real wire POST still commits.
    # The route-level ALLOCATOR law (positions advance per
    # request, semantic state does not) is already proven for
    # the tool-cycle receiver by
    # TestCausalIssuance::test_result_must_come_after_issuance_
    # position in the controller suite - referenced, not
    # re-proven here.  The format POST counter counts the
    # seam-driven refusals too; the ledger request accounting
    # only real wire requests charge (the two separate
    # counters are measured distinct).
    provider, _lock, ledger, port = _fmt_make_provider(tmp_path, "f3-causal")
    try:
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0 = _fmt_items(raw)[0]
        assert provider._fmt_issued[0]["position"] == 0
        assert provider._fmt_outstanding["issue_position"] == 0
        body0 = json.dumps(
            {"input": [e0, _fmt_result_item(e0["call_id"], _w_read())], "tools": _PINNED_TOOLS}
        ).encode()
        # the exact matching result at the EQUAL issue
        # position: closed causal refusal, nothing adopted
        status, _ctype, resp = provider._route("POST", ctl.ROUTE_RESPONSES, body0, 0)
        assert status == "400 Bad Request"
        assert json.loads(resp)["error"]["code"] == "causal-order"
        assert provider._fmt_retained_results == []
        assert provider._fmt_outstanding["call_id"] == e0["call_id"]
        assert provider._fmt_cases[0]["status"] == "pending"
        # the wire POST commits the read and issues e1 at the
        # next ALLOCATED position
        status, raw = _fmt_post(
            port,
            {"input": [e0, _fmt_result_item(e0["call_id"], _w_read())], "tools": _PINNED_TOOLS},
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        assert provider._fmt_issued[1]["position"] == 1
        body1 = json.dumps(
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], _w_read()),
                    e1,
                    _fmt_result_item(e1["call_id"], _w_stream_initial()),
                ],
                "tools": _PINNED_TOOLS,
            }
        ).encode()
        # the equal position of e1's OWN issuance and an
        # EARLIER position: closed causal refusals
        for pos in (1, 0):
            status, _ctype, resp = provider._route("POST", ctl.ROUTE_RESPONSES, body1, pos)
            assert status == "400 Bad Request"
            assert json.loads(resp)["error"]["code"] == "causal-order"
        # malformed positions refuse as closed, not guessed
        for bad in (True, -1):
            status, _ctype, resp = provider._route("POST", ctl.ROUTE_RESPONSES, body1, bad)
            assert status == "400 Bad Request"
            assert json.loads(resp)["error"]["code"] == "causal-position"
        assert len(provider._fmt_retained_results) == 1
        assert provider._fmt_outstanding["call_id"] == e1["call_id"]
        assert provider._fmt_cases[1]["status"] == "pending"
        assert provider._fmt_session is None and provider._fmt_cum == 0
        # the later REAL wire POST at the next allocated
        # position commits: the seam refusals consumed no
        # semantic state
        status, raw = _fmt_post(port, json.loads(body1))
        assert status == 200, raw[:300]
        assert provider._fmt_issued[2]["position"] == 2
        # the two separate actual counters: the route counts
        # every model POST (wire + seam-driven), the ledger
        # request accounting only the real wire requests
        assert provider._fmt_posts == 1 + 1 + 5 + 1
        assert ledger.requests == 3
    finally:
        _fmt_close(provider)


def test_f4_format_stream_bad_frame_refusal_states(tmp_path: Path) -> None:
    # F4 layer: the tentative stream-frame refusal states at
    # the real receiver, after a valid prefix reaches the
    # stream case: (a) a bad initial seed adopts no
    # session/offset; (b) an empty initial frame plus a final
    # with the complete output is only ONE nonempty piece -
    # the multi-chunk qualification refuses with no advance;
    # (c) a partial final (complete frame, incomplete offset)
    # refuses with no advance.  After every refusal the
    # frozen history is unchanged and still commits; no
    # clock rewind, no fresh admission.
    full = (
        SEED["stream-piece-0"].decode()
        + SEED["stream-piece-1"].decode()
        + SEED["stream-piece-2"].decode()
    )
    bad_initial = SEED["stream-piece-0"].decode()[:-1] + "Z"
    provider, _lock, _ledger, port = _fmt_make_provider(tmp_path, "f4-badframe")
    try:
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0 = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port,
            {"input": [e0, _fmt_result_item(e0["call_id"], _w_read())], "tools": _PINNED_TOOLS},
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        base = [
            e0,
            _fmt_result_item(e0["call_id"], _w_read()),
            e1,
        ]
        # (a) the initial RUNNING frame carries a MUTATED
        # first slice: the seed law refuses; the token line
        # matches the frame's own bytes, so the refusal is
        # the seed check, not the metadata
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(
                        e1["call_id"], _w_stream_frame(bad_initial, _FMT_SESSION, None, "0.5000")
                    )
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-seed-mismatch" in raw
        assert provider._fmt_session is None and provider._fmt_cum == 0
        assert provider._fmt_cases[1]["status"] == "pending"
        assert provider._fmt_cases[1]["results"] == []
        assert len(provider._fmt_retained_results) == 1
        assert len(provider._fmt_issued) == 2
        assert provider._fmt_polls == 0
        assert provider._fmt_outstanding["call_id"] == e1["call_id"]
        # (b) a VALID initial frame with EMPTY output
        # commits, then the complete output arrives in ONE
        # final frame: exactly ONE nonempty piece - the
        # multi-chunk qualification refuses with no advance
        empty_initial = _w_stream_frame("", _FMT_SESSION, None, "0.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": base + [_fmt_result_item(e1["call_id"], empty_initial)],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        poll1 = _fmt_items(raw)[0]
        assert poll1["name"] == "write_stdin"
        assert provider._fmt_session == _FMT_SESSION and provider._fmt_cum == 0
        assert len(provider._fmt_retained_results) == 2
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(e1["call_id"], empty_initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], _w_stream_frame(full, None, 0, "4.5000")),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-multichunk-deviation" in raw
        # no offset advance, no result adoption, no case
        # finalization: the running process is still
        # outstanding at the same cumulative offset
        assert provider._fmt_cum == 0
        assert len(provider._fmt_retained_results) == 2
        assert provider._fmt_polls == 1
        assert provider._fmt_cases[1]["status"] == "pending"
        assert len(provider._fmt_issued) == 3
        assert provider._fmt_outstanding["call_id"] == poll1["call_id"]
        # (c) a valid running poll commits the first slice,
        # then a PARTIAL final (complete frame, incomplete
        # offset) refuses with no advance
        p0 = SEED["stream-piece-0"].decode()
        p1 = SEED["stream-piece-1"].decode()
        p2 = SEED["stream-piece-2"].decode()
        # the empty initial left the verifier at offset 0, so the
        # running frame must carry the FIRST slice, not a later one
        running = _w_stream_frame(p0, _FMT_SESSION, None, "2.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(e1["call_id"], empty_initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], running),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        poll2 = _fmt_items(raw)[0]
        assert provider._fmt_cum == len(SEED["stream-piece-0"])
        assert len(provider._fmt_retained_results) == 3
        partial = _w_stream_frame(p1, None, 0, "4.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(e1["call_id"], empty_initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], running),
                    poll2,
                    _fmt_result_item(poll2["call_id"], partial),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-seed-mismatch" in raw
        assert provider._fmt_cum == len(SEED["stream-piece-0"])
        assert len(provider._fmt_retained_results) == 3
        assert provider._fmt_cases[1]["status"] == "pending"
        assert len(provider._fmt_issued) == 4
        # the frozen history still commits: the complete
        # remaining slice finishes the case
        final = _w_stream_frame(p1 + p2, None, 0, "4.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(e1["call_id"], empty_initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], running),
                    poll2,
                    _fmt_result_item(poll2["call_id"], final),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        assert _fmt_items(raw)[0]["name"] == "exec_command"
        assert len(provider._fmt_issued) == 5
        assert provider._fmt_case_index == 2
        assert provider._fmt_cases[1]["status"] == "completed"
        assert provider._fmt_cases[1]["nonempty_pieces"] == 2
        assert len(provider._fmt_retained_results) == 4
    finally:
        _fmt_close(provider)


def test_f5_format_route_counts_early_refusals_and_post_bound(tmp_path: Path) -> None:
    # F5 layer, four honestly named boundaries at the real
    # receiver: (1) WIRE - a wrong-authorization POST and a
    # malformed-JSON POST consume the model-POST counter AND
    # the ledger request accounting BEFORE any semantic step
    # (no state adopted); (2) WIRE - every terminal-state
    # POST is scenario-bounded but still COUNTED (POSTs
    # 10..16); (3) PHYSICAL - the STRONGER existing per-
    # connection thread cap (16, cumulative on the ledger)
    # refuses the 17th wire connection at the admission gate
    # with NO response and closes the provider, so the
    # format 20/21 post gate is unreachable over the wire
    # (measured by a private ad-hoc control: the 17th full
    # POST reset with connections=17/threads=16); (4)
    # SEMANTIC SEAM - the actual _route seam (in-process,
    # controlled position, real terminal body; no connection
    # and no ledger request charge, so the distinct counters
    # stay separately measurable) drives route POSTs 17..20
    # to scenario-bounded and POST 21 to format-post-bound.
    # The existing owner/controller caps stay unchanged.  The
    # exporter's two closed charged commands are not issued
    # in this test and cannot be conflated.  The 16-issued /
    # 12-poll mechanism bounds are proven by the pure F5
    # format-ledger-bound controls (referenced, not re-proven
    # here).
    token = "ab" * 16
    provider, _lock, ledger, port = _fmt_make_provider(tmp_path, "f5-route", auth_token=token)
    assert provider.auth_expected is not None
    auth = "Bearer " + provider.auth_expected
    try:
        # wrong authorization: fixed closed 401, counted
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 401, raw[:300]
        assert b"invalid-authorization" in raw
        assert token.encode() not in raw
        assert provider._fmt_posts == 1
        assert ledger.requests == 1
        assert provider._fmt_state == "awaiting-first-post"
        # malformed JSON with valid auth: fixed closed 400,
        # counted, no semantic progress
        status, raw = _fmt_post(port, "not json", auth=auth)
        assert status == 400, raw[:300]
        assert b"malformed-request" in raw
        assert provider._fmt_posts == 2
        assert ledger.requests == 2
        assert provider._fmt_state == "awaiting-first-post"
        # the valid initial POST commits
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS}, auth=auth)
        assert status == 200, raw[:300]
        calls = [_fmt_items(raw)[0]]
        results: list[dict[str, Any]] = []
        wrappers = [
            _w_read(),
            _w_stream_initial(),
            _w_poll_running(),
            _w_poll_final(),
            _w_empty(),
            _w_truncated(),
        ]
        for i, wrapper in enumerate(wrappers):
            status, raw = _fmt_post(
                port,
                {
                    "input": calls + results + [_fmt_result_item(calls[-1]["call_id"], wrapper)],
                    "tools": _PINNED_TOOLS,
                },
                auth=auth,
            )
            assert status == 200, (i, raw[:300])
            results.append(_fmt_result_item(calls[-1]["call_id"], wrapper))
            items = _fmt_items(raw)
            if i < len(wrappers) - 1:
                calls.append(items[0])
        # the ACTUAL wire arithmetic so far: 1 auth refusal +
        # 1 malformed + 1 initial + 6 results = 9 counted POSTs
        assert provider._fmt_state == "done"
        assert provider._fmt_posts == 9
        assert ledger.requests == 9
        # every further WIRE POST after the terminal state is
        # scenario-bounded but still COUNTED: POSTs 10..16 on
        # connections 10..16 (the stronger physical cap below
        # admits exactly 16 connections, so the wire layer
        # ends here - measured, not inferred)
        for expected in range(10, 17):
            status, raw = _fmt_post(
                port, {"input": calls + results, "tools": _PINNED_TOOLS}, auth=auth
            )
            assert status == 400, (expected, raw[:300])
            assert b"scenario-bounded" in raw, (expected, raw[:200])
            assert provider._fmt_posts == expected
            assert ledger.requests == expected
        # the STRONGER existing physical bound: the per-
        # connection thread cap (16, cumulative on the
        # ledger) refuses the 17th wire connection at the
        # admission gate BEFORE any route or request
        # accounting: the closed connection carries NO
        # response (a bare connection deterministically reads
        # EOF), the provider closes, and the route counters
        # are left untouched
        s = socket.create_connection(("127.0.0.1", int(port)), timeout=5)
        try:
            assert s.recv(65536) == b""
        finally:
            s.close()
        # the refusal path closes the connection BEFORE it sets
        # the closed flag, so the client's EOF can wake first:
        # join this OWN accept thread (it ends on the refusal)
        # with a finite timeout and assert it ended BEFORE
        # asserting the flag (never via _fmt_close, which would
        # manufacture it)
        accept = provider.accept_thread
        assert accept is not None
        accept.join(timeout=5)
        assert not accept.is_alive()
        assert provider.closed is True
        assert ledger.threads == 16
        assert ledger.connections == 17
        assert provider._fmt_posts == 16
        assert ledger.requests == 16
        # the format 20/21 post gate is therefore UNREACHABLE
        # over the wire (the physical cap fires first), so it
        # is driven at the ACTUAL _route semantic seam: an
        # in-process route call with a controlled position
        # and the real terminal body - no connection and no
        # ledger request charge, so the two distinct counters
        # stay separately measurable (route POSTs 17..20
        # refuse scenario-bounded, POST 21 format-post-bound)
        for seam_position in range(16, 21):
            status, _ctype, resp = provider._route(
                "POST",
                ctl.ROUTE_RESPONSES,
                json.dumps({"input": calls + results, "tools": _PINNED_TOOLS}).encode(),
                seam_position,
                auth,
            )
            assert status == "400 Bad Request"
            if seam_position < 20:
                assert json.loads(resp)["error"]["code"] == "scenario-bounded"
            else:
                assert json.loads(resp)["error"]["code"] == "format-post-bound"
            assert provider._fmt_posts == seam_position + 1
        assert ledger.requests == 16
        # no semantic progress after the terminal state; the
        # format's own finite bound refused the 21st POST
        # while the existing owner/controller caps are
        # unchanged (the ledger request bound never fired)
        assert provider._fmt_state == "done"
        assert provider._fmt_posts == 21
        assert len(provider._fmt_issued) == 6
        assert len(provider._fmt_retained_results) == 6
        assert ledger.budgets.max_requests == 512
        assert ledger.budgets.max_threads == 16
    finally:
        _fmt_close(provider)


def test_f4_format_history_identity_adversarial_negatives(tmp_path: Path) -> None:
    # F4 layer: the durable history/identity adversarial
    # negatives at the REAL receiver (the pure model
    # snapshot controls prove the record law; this drives
    # the actual fenced step): a foreign unissued result, a
    # duplicated outstanding result, a MUTATED retained
    # historical result, a TYPED-argument mutation on an
    # echoed historical call and a mismatched poll session
    # all refuse closed with the retained history, the
    # first-accepted positions and the single retention
    # unchanged; the otherwise identical valid bodies still
    # commit (the frozen history is never corrupted by a
    # refusal).
    provider, _lock, _ledger, port = _fmt_make_provider(tmp_path, "f4-history")
    try:
        status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
        assert status == 200, raw[:300]
        e0 = _fmt_items(raw)[0]
        status, raw = _fmt_post(
            port,
            {"input": [e0, _fmt_result_item(e0["call_id"], _w_read())], "tools": _PINNED_TOOLS},
        )
        assert status == 200, raw[:300]
        e1 = _fmt_items(raw)[0]
        base = [
            e0,
            _fmt_result_item(e0["call_id"], _w_read()),
            e1,
        ]
        initial = _w_stream_initial()
        # (1) a FOREIGN unissued result id: refused
        status, raw = _fmt_post(
            port,
            {
                "input": base + [_fmt_result_item("slaif-fmt-9-9", initial)],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-history" in raw
        # (2) the outstanding result DUPLICATED in one
        # request: refused
        status, raw = _fmt_post(
            port,
            {
                "input": base
                + [
                    _fmt_result_item(e1["call_id"], initial),
                    _fmt_result_item(e1["call_id"], initial),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-history" in raw
        # (3) a MUTATED retained historical result (the read
        # wrapper byte-changed): the frozen byte-identity
        # law refuses
        mutated_read = _w_read()[:-1] + "X"
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], mutated_read),
                    e1,
                    _fmt_result_item(e1["call_id"], initial),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-history" in raw
        # (4) a TYPED-argument mutation on an echoed
        # historical call (a string standing in for the
        # required integer): refused, never coerced
        bad_args = dict(provider._fmt_issued[1]["arguments"])
        assert bad_args["yield_time_ms"] == 500
        bad_args["yield_time_ms"] = "500"
        e1_bad = dict(e1)
        e1_bad["arguments"] = json.dumps(bad_args, sort_keys=True, separators=(",", ":"))
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], _w_read()),
                    e1_bad,
                    _fmt_result_item(e1["call_id"], initial),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-history" in raw
        # the valid initial frame commits (frozen history
        # still valid)
        status, raw = _fmt_post(
            port,
            {"input": base + [_fmt_result_item(e1["call_id"], initial)], "tools": _PINNED_TOOLS},
        )
        assert status == 200, raw[:300]
        poll1 = _fmt_items(raw)[0]
        # (5) a running poll with a MISMATCHED session
        # (the process was adopted at 77): the chain law
        # refuses with no adoption
        p1 = SEED["stream-piece-1"].decode()
        wrong_session = _w_stream_frame(p1, 78, None, "2.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], _w_read()),
                    e1,
                    _fmt_result_item(e1["call_id"], initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], wrong_session),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 400, raw[:300]
        assert b"format-chain-deviation" in raw
        assert provider._fmt_session == _FMT_SESSION
        assert provider._fmt_cum == len(SEED["stream-piece-0"])
        assert provider._fmt_polls == 1
        assert provider._fmt_outstanding["call_id"] == poll1["call_id"]
        # the matching session commits, then the final frame
        # completes the case
        running = _w_stream_frame(p1, _FMT_SESSION, None, "2.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], _w_read()),
                    e1,
                    _fmt_result_item(e1["call_id"], initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], running),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        poll2 = _fmt_items(raw)[0]
        final = _w_stream_frame(SEED["stream-piece-2"].decode(), None, 0, "4.5000")
        status, raw = _fmt_post(
            port,
            {
                "input": [
                    e0,
                    _fmt_result_item(e0["call_id"], _w_read()),
                    e1,
                    _fmt_result_item(e1["call_id"], initial),
                    poll1,
                    _fmt_result_item(poll1["call_id"], running),
                    poll2,
                    _fmt_result_item(poll2["call_id"], final),
                ],
                "tools": _PINNED_TOOLS,
            },
        )
        assert status == 200, raw[:300]
        # the first-accepted positions are UNCHANGED across
        # every refusal: e0/e1 at 0/1, then poll1/poll2/e2 at the
        # positions of the wire POSTs that issued them - real-wire
        # refusals consume allocator positions (the request
        # position is allocated before routing), so the recorded
        # positions are 6/8/9, never a compacted trace
        assert [entry["position"] for entry in provider._fmt_issued] == [0, 1, 6, 8, 9]
        # the retained history is single-retained and byte-exact,
        # including the final result's own pair
        assert provider._fmt_retained_results == [
            (e0["call_id"], _w_read()),
            (e1["call_id"], initial),
            (poll1["call_id"], running),
            (poll2["call_id"], final),
        ]
        assert provider._fmt_cases[1]["status"] == "completed"
        assert len(provider._fmt_issued) == 5
    finally:
        _fmt_close(provider)


# -- safe PARTIAL snapshot codec (the distinct closed non-done form) ------------
# The partial form is a DISTINCT closed record: the issued-registry prefix,
# the issued-case prefix (every entry before the last complete, at most ONE
# pending case and it the last) carrying only retained verified frames, the
# immutable seed identity, the ACTUAL issued poll counter, the ACTUAL non-done
# final state and the closed not-qualified fact.  Unknown/unverified selection
# is not in the record at all; no completion/exit/verified placeholder exists.
_POS_PARTIAL = {"e0": 0, "e1": 1, "poll1": 2, "poll2": 3, "poll3": 4, "e2": 5, "e3": 6}
_RES_PARTIAL = {"e0": 1, "e1": 2, "poll1": 3, "poll2": 4, "poll3": 5, "e2": 6, "e3": 7}
_IDS_PARTIAL = {
    **_IDS,
    "poll3": "aj-poll-stream-0007",
}


def _partial_case(
    spec: dict[str, Any], call_id: str, position: int, results: list[dict[str, Any]], polls: int
) -> dict[str, Any]:
    arguments = model.format_expected_exec_arguments(spec)
    return {
        "case": spec["case"],
        "kind": spec["kind"],
        "seed_files": list(spec["seed_files"]),
        "command": spec["command"],
        "call_id": call_id,
        "call_position": position,
        "arguments_sha256": model.sha256_bytes(model.canonical_bytes(arguments)),
        "status": "pending",
        "results": results,
        "polls": polls,
    }


def _partial_record(
    cases: list[dict[str, Any]],
    issued: list[dict[str, Any]],
    model_posts: int,
    output_bytes: int = 0,
    polls: int | None = None,
) -> dict[str, Any]:
    if polls is None:
        # the ACTUAL issued poll count (the global law is bound to the
        # issued registry; the per-case pending retained counts are
        # explicitly separate)
        polls = len([c for c in issued if c["name"] == model.FORMAT_POLL_TOOL])
    return {
        "record": model.SCHEMA_FORMAT_SNAPSHOT_PARTIAL,
        "synthetic": True,
        "issued_calls": issued,
        "cases": cases,
        "seed": [[n, model.sha256_bytes(d), len(d)] for n, d in model.FORMAT_SEED_FILES],
        "seed_total_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_sha256": model.sha256_bytes(b"".join(d for _n, d in model.FORMAT_SEED_FILES)),
        "exporter_uid": model.CONTROLLER_UID,
        "exported_before_teardown": True,
        "model_posts": model_posts,
        "controller_ledger": {"requests": model_posts + 2, "output_bytes": output_bytes},
        "polls": polls,
        "final_state": "awaiting-first-post" if not cases else "awaiting-result",
        "qualification": "not-qualified",
    }


def _read_frame() -> dict[str, Any]:
    return _frame(
        _IDS_PARTIAL["e0"],
        _POS_PARTIAL["e0"],
        _RES_PARTIAL["e0"],
        _wrapper(
            "d4e5f6",
            "0.0200",
            exit_code=0,
            tokens=model._approx_token_count_bytes(len(SEED["read-0"])),
            output=_READ0,
        ),
    )


def _stream_running_frame(
    key: str, chunk: str, wall: str, piece: str, session: int = 7
) -> dict[str, Any]:
    return _frame(
        _IDS_PARTIAL[key],
        _POS_PARTIAL[key],
        _RES_PARTIAL[key],
        _wrapper(
            chunk,
            wall,
            session=session,
            tokens=model._approx_token_count_bytes(len(piece.encode("utf-8"))),
            output=piece,
        ),
    )


def _complete_read_case() -> dict[str, Any]:
    specs = model.FORMAT_CASES
    return _case_record(
        specs[0], _IDS_PARTIAL["e0"], _POS_PARTIAL["e0"], [_read_frame()], None, 0, None
    )


def _complete_stream_case() -> dict[str, Any]:
    specs = model.FORMAT_CASES
    results = [
        _stream_running_frame("e1", "a1b2c3", "0.5000", _P0),
        _stream_running_frame("poll1", "b2c3d4", "2.5000", _P1),
        _frame(
            _IDS_PARTIAL["poll2"],
            _POS_PARTIAL["poll2"],
            _RES_PARTIAL["poll2"],
            # the completion poll may omit the session ID (pinned)
            _wrapper(
                "c3d4e5",
                "4.5000",
                exit_code=0,
                tokens=model._approx_token_count_bytes(len(_P2.encode("utf-8"))),
                output=_P2,
            ),
        ),
    ]
    return _case_record(specs[1], _IDS_PARTIAL["e1"], _POS_PARTIAL["e1"], results, 7, 2, None)


def _issued_read() -> dict[str, Any]:
    return _issued(
        model.FORMAT_EXEC_TOOL,
        _IDS_PARTIAL["e0"],
        _POS_PARTIAL["e0"],
        model.format_expected_exec_arguments(model.FORMAT_CASES[0]),
    )


def _issued_stream_exec() -> dict[str, Any]:
    return _issued(
        model.FORMAT_EXEC_TOOL,
        _IDS_PARTIAL["e1"],
        _POS_PARTIAL["e1"],
        model.format_expected_exec_arguments(model.FORMAT_CASES[1]),
    )


def _issued_poll(key: str) -> dict[str, Any]:
    return _issued(
        model.FORMAT_POLL_TOOL,
        _IDS_PARTIAL[key],
        _POS_PARTIAL[key],
        {"session_id": 7, "chars": ""},
    )


def _issued_empty_exec() -> dict[str, Any]:
    return _issued(
        model.FORMAT_EXEC_TOOL,
        _IDS_PARTIAL["e2"],
        _POS_PARTIAL["e2"],
        model.format_expected_exec_arguments(model.FORMAT_CASES[2]),
    )


def _partial_expect_refusal(rec: dict[str, Any], reason: str) -> None:
    with pytest.raises(model.FixtureError) as excinfo:
        model.validate_format_snapshot_record_partial(rec)
    assert reason in str(excinfo.value)


def test_partial_sourceless_zero() -> None:
    # the empty form: no POSTs at all, no issued calls, no cases
    rec = _partial_record([], [], 0)
    model.validate_format_snapshot_record_partial(rec)
    assert rec["controller_ledger"] == {"requests": 2, "output_bytes": 0}


def test_partial_first_exec_pending() -> None:
    # one issued exec, result not yet retained: the exec is the final
    # registry entry, the case is pending with zero results
    rec = _partial_record(
        [_partial_case(model.FORMAT_CASES[0], _IDS_PARTIAL["e0"], 0, [], 0)],
        [_issued_read()],
        1,
    )
    model.validate_format_snapshot_record_partial(rec)


def test_partial_stream_exec_pending_zero_frames() -> None:
    # the complete read prefix plus the just-issued stream exec: zero
    # retained stream frames, no measured session, no poll target
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(model.FORMAT_CASES[1], _IDS_PARTIAL["e1"], 1, [], 0),
        ],
        [_issued_read(), _issued_stream_exec()],
        2,
        len(SEED["read-0"]),
    )
    model.validate_format_snapshot_record_partial(rec)


def test_partial_running_initial_plus_outstanding_poll() -> None:
    # the transactional FSM: the accepted running initial committed the
    # FIRST poll in the same transaction — ONE outstanding poll, the
    # final registry entry; the per-case RETAINED poll count is zero
    # while the ACTUAL issued counter is one
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
        (len(SEED["read-0"]) + len(SEED["stream-piece-0"])),
    )
    model.validate_format_snapshot_record_partial(rec)
    assert rec["polls"] == 1
    assert rec["cases"][1]["polls"] == 0


def test_partial_running_all_bytes_no_exit() -> None:
    # the WHOLE source observed under actual running wrappers: byte
    # equality does NOT prove completion; the case stays pending with
    # three retained running results and exactly THREE issued polls
    # (the last one outstanding)
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [
                    _stream_running_frame("e1", "a1b2c3", "0.5000", _P0),
                    _stream_running_frame("poll1", "b2c3d4", "2.5000", _P1),
                    _stream_running_frame("poll2", "c3d4e5", "4.5000", _P2),
                ],
                2,
            ),
        ],
        [
            _issued_read(),
            _issued_stream_exec(),
            _issued_poll("poll1"),
            _issued_poll("poll2"),
            _issued_poll("poll3"),
        ],
        5,
        (
            len(SEED["read-0"])
            + len(SEED["stream-piece-0"])
            + len(SEED["stream-piece-1"])
            + len(SEED["stream-piece-2"])
        ),
    )
    model.validate_format_snapshot_record_partial(rec)
    assert rec["polls"] == 3
    assert rec["cases"][1]["polls"] == 2


def test_partial_completed_stream_next_pending() -> None:
    # completed stream prefix plus the pending non-stream last case:
    # the measured stream session is PRESERVED (a pending non-stream
    # case never overwrites it) and the issued polls stay bound to it
    rec = _partial_record(
        [
            _complete_read_case(),
            _complete_stream_case(),
            _partial_case(model.FORMAT_CASES[2], _IDS_PARTIAL["e2"], 5, [], 0),
        ],
        [
            _issued_read(),
            _issued_stream_exec(),
            _issued_poll("poll1"),
            _issued_poll("poll2"),
            _issued_empty_exec(),
        ],
        6,
        (
            len(SEED["read-0"])
            + len(SEED["stream-piece-0"])
            + len(SEED["stream-piece-1"])
            + len(SEED["stream-piece-2"])
        ),
    )
    model.validate_format_snapshot_record_partial(rec)


def build_full_bytes_positive() -> dict[str, Any]:
    """The COMPLETE-form control of the whole-bytes-running pending
    state: the same running frames (already carrying the whole
    source) plus the EMPTY completion poll — the complete chain law
    accepts the full output with the completion frame as the last
    delta."""
    specs = model.FORMAT_CASES
    effective = model.FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS
    trunc_bytes = model.format_truncate_text(_T0, effective).encode()
    results_stream = [
        _stream_running_frame("e1", "a1b2c3", "0.5000", _P0),
        _stream_running_frame("poll1", "b2c3d4", "2.5000", _P1),
        _stream_running_frame("poll2", "c3d4e5", "4.5000", _P2),
        _frame(
            _IDS_PARTIAL["poll3"],
            _POS_PARTIAL["poll3"],
            _RES_PARTIAL["poll3"],
            _wrapper("d4e5f6", "6.5000", exit_code=0, output=""),
        ),
    ]
    results_empty = [
        _frame(
            _IDS_PARTIAL["e2"],
            _POS_PARTIAL["e2"],
            _RES_PARTIAL["e2"],
            _wrapper("e5f6a7", "0.0050", exit_code=0, output=""),
        )
    ]
    results_trunc = [
        _frame(
            _IDS_PARTIAL["e3"],
            _POS_PARTIAL["e3"],
            _RES_PARTIAL["e3"],
            _wrapper(
                "f6a7b8",
                "0.0300",
                exit_code=0,
                tokens=model._approx_token_count_bytes(len(SEED["trunc-0"])),
                output=trunc_bytes.decode(),
            ),
        )
    ]
    return {
        "record": model.SCHEMA_FORMAT_SNAPSHOT,
        "synthetic": True,
        "issued_calls": [
            _issued_read(),
            _issued_stream_exec(),
            _issued_poll("poll1"),
            _issued_poll("poll2"),
            _issued_poll("poll3"),
            _issued_empty_exec(),
            _issued(
                model.FORMAT_EXEC_TOOL,
                _IDS_PARTIAL["e3"],
                _POS_PARTIAL["e3"],
                model.format_expected_exec_arguments(specs[3]),
            ),
        ],
        "cases": [
            _case_record(
                specs[0], _IDS_PARTIAL["e0"], _POS_PARTIAL["e0"], [_read_frame()], None, 0, None
            ),
            _case_record(
                specs[1], _IDS_PARTIAL["e1"], _POS_PARTIAL["e1"], results_stream, 7, 3, None
            ),
            _case_record(
                specs[2], _IDS_PARTIAL["e2"], _POS_PARTIAL["e2"], results_empty, None, 0, None
            ),
            _case_record(
                specs[3], _IDS_PARTIAL["e3"], _POS_PARTIAL["e3"], results_trunc, None, 0, effective
            ),
        ],
        "seed": [[n, model.sha256_bytes(d), len(d)] for n, d in model.FORMAT_SEED_FILES],
        "seed_total_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_bytes": sum(len(d) for _n, d in model.FORMAT_SEED_FILES),
        "originals_sha256": model.sha256_bytes(b"".join(d for _n, d in model.FORMAT_SEED_FILES)),
        "exporter_uid": model.CONTROLLER_UID,
        "exported_before_teardown": True,
        "model_posts": 8,
        "controller_ledger": {
            "requests": 10,
            "output_bytes": (
                len(SEED["read-0"])
                + len(SEED["stream-piece-0"])
                + len(SEED["stream-piece-1"])
                + len(SEED["stream-piece-2"])
                + len(trunc_bytes)
            ),
        },
        "polls": 3,
        "final_state": "done",
    }


def test_partial_full_output_running_then_empty_final_complete() -> None:
    # the COMPLETE law accepts the whole-bytes-running history with an
    # empty completion frame (the pending control's completion twin)
    rec = build_full_bytes_positive()
    model.validate_format_snapshot_record(rec)
    assert rec["cases"][1]["polls"] == 3


def test_partial_rejects_complete_form_tag() -> None:
    # the distinct tag-pair law: the complete snapshot is refused by
    # the partial validator and the partial form by the complete one
    with pytest.raises(model.FixtureError):
        model.validate_format_snapshot_record_partial(build_positive())
    rec = _partial_record([], [], 0)
    with pytest.raises(model.FixtureError):
        model.validate_format_snapshot_record(rec)


def test_partial_unknown_tool_name_refused() -> None:
    # P7: an unknown tool name is refused BEFORE classification or
    # case indexing, never treated as a poll
    rec = _partial_record(
        [_partial_case(model.FORMAT_CASES[0], _IDS_PARTIAL["e0"], 0, [], 0)],
        [
            _issued_read(),
            _issued(
                model.FORMAT_POLL_TOOL.replace("write", "some"),
                "aj-foreign-0000",
                1,
                {"session_id": 7, "chars": ""},
            ),
        ],
        2,
    )
    _partial_expect_refusal(rec, "format-issued-name")


def test_partial_duplicate_call_id_refused() -> None:
    rec = _partial_record(
        [_partial_case(model.FORMAT_CASES[0], _IDS_PARTIAL["e0"], 0, [], 0)],
        [_issued_read(), _issued_read()],
        2,
    )
    # the second entry repeats the position, so the registry's
    # duplicate-ID law and the position law both close; the duplicate
    # call_id is refused at the registry identity
    _partial_expect_refusal(rec, "format-issued")


def test_partial_malformed_poll_args_refused() -> None:
    # typed-strict identity: a float standing in for the required
    # integer session is refused, never coerced
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [
            _issued_read(),
            _issued_stream_exec(),
            _issued(
                model.FORMAT_POLL_TOOL,
                _IDS_PARTIAL["poll1"],
                _POS_PARTIAL["poll1"],
                {"session_id": 7.0, "chars": ""},
            ),
        ],
        3,
    )
    _partial_expect_refusal(rec, "format-issued-arguments")


def test_partial_result_pre_issuance_refused() -> None:
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0, session=7)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
    )
    rec["cases"][1]["results"][0]["result_position"] = 1  # == own issuance
    _partial_expect_refusal(rec, "format-result-causality")


def test_partial_global_polls_counter_mismatch_refused() -> None:
    # the ACTUAL issued counter is one; a relabeled global of two is
    # a counter refusal, never decremented to fit
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
        polls=2,
    )
    _partial_expect_refusal(rec, "format-polls")


def test_partial_orphaned_retained_result_refused() -> None:
    # FSM-exact: a retained running result requires the outstanding
    # poll committed in the SAME transaction; none issued is a
    # closed refusal
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec()],
        2,
    )
    _partial_expect_refusal(rec, "format-issued-polls")


def test_partial_extra_issued_poll_refused() -> None:
    # one retained result has EXACTLY one issued poll; a second
    # issued poll (with no retained result that could follow) is a
    # closed refusal
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1"), _issued_poll("poll2")],
        4,
    )
    _partial_expect_refusal(rec, "format-issued-polls")


def test_partial_poll_without_exec_result_refused() -> None:
    # the poll target comes only from the validated result of this
    # run's actually issued exec: zero retained stream frames has
    # zero legal polls
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(model.FORMAT_CASES[1], _IDS_PARTIAL["e1"], 1, [], 0),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
    )
    _partial_expect_refusal(rec, "format-issued-polls")


def test_partial_outstanding_poll_not_final_refused() -> None:
    # an exec issued AFTER the outstanding poll could only be
    # committed with the stream's verified result: the closed
    # partial form cannot carry that exec without the NEXT case,
    # so the record is structurally refused at the closed
    # exec/case count law (the poll placement checks stay
    # defense-in-depth behind that law)
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [_stream_running_frame("e1", "a1b2c3", "0.5000", _P0)],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1"), _issued_empty_exec()],
        6,
    )
    _partial_expect_refusal(rec, "format-issued-exec")


def test_partial_non_prefix_bytes_refused() -> None:
    # an observed running byte form that is not a prefix of the
    # immutable expected content is an honest source-byte mismatch
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [
                    _frame(
                        _IDS_PARTIAL["e1"],
                        1,
                        2,
                        _wrapper("a1b2c3", "0.5000", session=7, output="X" * 10),
                    )
                ],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1")],
        3,
    )
    _partial_expect_refusal(rec, "format-case-source-mismatch")


def test_partial_retained_completion_frame_refused() -> None:
    # a retained completion would have finalized the case: a pending
    # case carrying an exit frame is a closed refusal
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [
                    _frame(
                        _IDS_PARTIAL["e1"],
                        1,
                        2,
                        _wrapper("a1b2c3", "0.5000", exit_code=0, output=_P0),
                    )
                ],
                0,
            ),
        ],
        [_issued_read(), _issued_stream_exec()],
        2,
    )
    _partial_expect_refusal(rec, "format-case-chain")


def test_partial_mixed_sessions_refused() -> None:
    # all retained stream frames bind to ONE re-derived positive
    # session; a mixed session is a closed refusal
    rec = _partial_record(
        [
            _complete_read_case(),
            _partial_case(
                model.FORMAT_CASES[1],
                _IDS_PARTIAL["e1"],
                1,
                [
                    _stream_running_frame("e1", "a1b2c3", "0.5000", _P0, session=7),
                    _stream_running_frame("poll1", "b2c3d4", "2.5000", _P1, session=8),
                ],
                1,
            ),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1"), _issued_poll("poll2")],
        4,
    )
    # the poll arguments stay bound to the re-derived session 7
    _partial_expect_refusal(rec, "format-case-chain")


def test_partial_pending_not_last_refused() -> None:
    # at most ONE pending case, and it the LAST: a pending case
    # followed by a complete case is not a closed form
    rec = _partial_record(
        [
            _partial_case(model.FORMAT_CASES[0], _IDS_PARTIAL["e0"], 0, [], 0),
            _complete_stream_case(),
        ],
        [_issued_read(), _issued_stream_exec(), _issued_poll("poll1"), _issued_poll("poll2")],
        4,
    )
    _partial_expect_refusal(rec, "format-cases-fields")


def test_partial_done_state_refused() -> None:
    rec = _partial_record(
        [_partial_case(model.FORMAT_CASES[0], _IDS_PARTIAL["e0"], 0, [], 0)],
        [_issued_read()],
        1,
    )
    rec["final_state"] = "done"
    _partial_expect_refusal(rec, "format-final-state")


def test_partial_qualification_literal_refused() -> None:
    # the closed qualification fact is the honest not-qualified
    # literal: any other value mints nothing and is refused
    rec = _partial_record([], [], 0)
    rec["qualification"] = "qualified"
    _partial_expect_refusal(rec, "closed record field enum invalid: qualification")
    rec = _partial_record([], [], 0)
    del rec["qualification"]
    with pytest.raises(model.FixtureError):
        model.validate_format_snapshot_record_partial(rec)


# ---------------------------------------------------------------------------
# T6 producer/export seam: the REAL Provider over real loopback plus the
# REAL Unix-socket exporter for every closed PARTIAL state (owned
# listener/socket/thread cleanup, deadline-bounded receives, hermetic
# injected process scans; no native, no Docker, no admission, no host
# scan).  The pure model tests above prove the partial snapshot law;
# these prove the PRODUCER (format_snapshot_record_partial /
# format_capture_record) and the export-client partial dispatch over
# the actual transport, reusing the closed trace/checkpoint controls.
# ---------------------------------------------------------------------------


def _fmt_partial_export(
    tmp_path: Path,
    tag: str,
    wrappers: list[str] | None,
    malformed: bool = False,
) -> tuple[Any, dict[str, Any], int]:
    """Drive the REAL Provider through the closed scenario prefix
    (``wrappers is None`` sends NO POST at all; an optional FIRST
    malformed POST is a consumed refusal issuing nothing; otherwise
    the initial POST plus the ``wrappers`` accumulated client-side
    results), then run the REAL exporter over its protected Unix
    socket with deadline-bounded receives.  Returns (provider, the
    validated SELECTED payload, the CLIENT-MEASURED wire bytes): the
    wire total is every PRE-EXPORT POST response frame the provider
    emitted (headers plus payload, refusals included) — the ledger's
    own output_bytes counter is that same pre-export accounting (the
    quiesce ack frame is never charged to output_bytes, and the export
    frame itself is charged only AFTER the snapshot is taken, so the
    snapshot's output_bytes is exactly the pre-export POST response
    wire total measured here); the per-case retained
    output CONTENT bytes are a separate case-level fact, never this
    counter.  On success the caller must _fmt_close the provider in
    its own finally; on EVERY failure (drive, export, the common
    asserts, or the exporter teardown) this helper tears down its
    OWN exporter server/thread and the provider, so nothing the test
    started leaks."""
    provider, lock, ledger, port = _fmt_make_provider(tmp_path, f"partial-{tag}")
    sock_path = str(tmp_path / f"partial-{tag}.sock")
    exporter: Any = None
    exporter_thread: threading.Thread | None = None
    selected: dict[str, Any] | None = None
    wire_bytes = 0
    body_error: BaseException | None = None

    def _teardown_exporter() -> None:
        # close then join as separate bounded best-effort steps: a
        # fault in either (a close other than OSError, or joining a
        # never-started thread) is captured, the OTHER step still
        # runs, and the original fault is preserved by the caller
        if exporter is None or exporter_thread is None:
            return
        close_fault: BaseException | None = None
        try:
            try:
                exporter.server.close()
            except OSError:
                pass
        except BaseException:
            close_fault = sys.exc_info()[1]
        try:
            exporter_thread.join(timeout=5)
        except BaseException:
            if close_fault is None:
                close_fault = sys.exc_info()[1]
        if exporter_thread.is_alive():
            raise AssertionError("exporter thread alive after close")
        if close_fault is not None:
            raise close_fault

    try:
        calls: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        if malformed:
            status, raw = _fmt_post(port, "{not-json")
            wire_bytes += len(raw)
            assert status == 400, (status, raw[:200])
        elif wrappers is not None:
            status, raw = _fmt_post(port, {"input": [_fmt_user()], "tools": _PINNED_TOOLS})
            wire_bytes += len(raw)
            assert status == 200, raw[:300]
            calls.append(_fmt_items(raw)[0])
        for i, wrapper in enumerate(wrappers or []):
            status, raw = _fmt_post(
                port,
                {
                    "input": calls + results + [_fmt_result_item(calls[-1]["call_id"], wrapper)],
                    "tools": _PINNED_TOOLS,
                },
            )
            wire_bytes += len(raw)
            assert status == 200, (i, raw[:300])
            results.append(_fmt_result_item(calls[-1]["call_id"], wrapper))
            calls.append(_fmt_items(raw)[0])
        exporter = ctl.Exporter(
            provider, ledger, lock, "main", socket_path=sock_path, trusted_uid=os.getuid()
        )
        exporter_thread = threading.Thread(target=exporter.serve_forever, daemon=True)
        exporter_thread.start()
        time.sleep(0.1)
        provider.quiesce(None, subject_scan=lambda: 0, tools_scan=lambda _peer: 0)
        deadline = time.monotonic() + 5
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect(sock_path)
            s.sendall(b"quiesce\n")
            line = exp._recv_line(s, deadline, 16384)
        finally:
            s.close()
        assert line.startswith(b"quiesce-ok "), line
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect(sock_path)
            s.sendall(b"export\n")
            header = exp._recv_exact(s, deadline, 4)
            (length,) = struct.unpack(">I", header)
            # the declared serialized length is closed BEFORE any
            # receive of the body: the snapshot's own byte law
            assert length <= model.FORMAT_SNAPSHOT_MAX_BYTES, length
            payload = exp._recv_exact(s, deadline, length)
            digest = exp._recv_exact(s, deadline, 64)
        finally:
            s.close()
        assert digest.decode() == hashlib.sha256(payload).hexdigest()
        selected = exp.validate_selected_payload(payload)
        assert selected["record"] == model.SCHEMA_FORMAT_EXPORT_PARTIAL
        snap = selected["snapshot"]
        assert snap["record"] == model.SCHEMA_FORMAT_SNAPSHOT_PARTIAL
        assert snap["synthetic"] is True
        assert snap["qualification"] == model.FORMAT_QUALIFICATION_NOT_QUALIFIED
        assert snap["exporter_uid"] == model.CONTROLLER_UID
        assert snap["exported_before_teardown"] is True
        _teardown_exporter()
        assert selected is not None
        return provider, selected, wire_bytes
    except BaseException:
        body_error = sys.exc_info()[1]
        raise
    finally:
        if body_error is not None:
            # EVERY failure path (drive, export, the common asserts,
            # or the exporter teardown itself — including a close or
            # join fault, or a never-started thread) tears down its
            # OWN exporter server/thread and the provider before the
            # original fault propagates: the original failure is
            # preserved and nothing the test started leaks; on
            # success the caller's finally owns _fmt_close
            if exporter is not None:
                try:
                    exporter.server.close()
                except BaseException:
                    pass
            if exporter_thread is not None:
                try:
                    exporter_thread.join(timeout=5)
                except BaseException:
                    pass
            _fmt_close(provider)
            raise body_error


def test_partial_export_sourceless_zero(tmp_path: Path) -> None:
    # the EMPTY partial form over the real transport: no POSTs at
    # all, nothing issued, the honest awaiting-first-post state, no
    # wire bytes emitted, and only the exporter's two closed
    # charged commands on the ledger
    provider, selected, wire = _fmt_partial_export(tmp_path, "sourceless-zero", None)
    try:
        assert provider._fmt_posts == 0
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-first-post"
        assert snap["cases"] == []
        assert snap["issued_calls"] == []
        assert snap["model_posts"] == 0
        assert snap["polls"] == 0
        assert wire == 0
        assert snap["controller_ledger"] == {"requests": 2, "output_bytes": 0}
    finally:
        _fmt_close(provider)


def test_partial_export_consumed_refusal_no_issue(tmp_path: Path) -> None:
    # a consumed REFUSED POST (malformed JSON) advances the truthful
    # model-POST count and the ledger but issues NOTHING: the
    # scenario stays awaiting-first-post with an empty registry, and
    # the refused POST's closed error frame is accounted wire bytes
    provider, selected, wire = _fmt_partial_export(tmp_path, "consumed-refusal", [], malformed=True)
    try:
        assert provider._fmt_posts == 1
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-first-post"
        assert snap["cases"] == []
        assert snap["issued_calls"] == []
        assert snap["model_posts"] == 1
        assert snap["polls"] == 0
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 3, "output_bytes": wire}
    finally:
        _fmt_close(provider)


def test_partial_export_first_exec_pending(tmp_path: Path) -> None:
    # one accepted initial POST: the first closed case's exec is
    # issued and outstanding, the case record is PENDING with zero
    # retained frames, nothing else exists
    provider, selected, wire = _fmt_partial_export(tmp_path, "first-exec", [])
    try:
        assert provider._fmt_posts == 1
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-result"
        assert snap["model_posts"] == 1
        assert snap["polls"] == 0
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 3, "output_bytes": wire}
        issued = snap["issued_calls"]
        assert len(issued) == 1
        assert issued[0]["name"] == model.FORMAT_EXEC_TOOL
        assert issued[0]["position"] == 0
        assert model.format_arguments_exact(
            issued[0]["arguments"], model.format_expected_exec_arguments(model.FORMAT_CASES[0])
        )
        case = snap["cases"][0]
        assert case["case"] == model.FORMAT_CASES[0]["case"]
        assert case["status"] == "pending"
        assert case["results"] == []
        assert case["polls"] == 0
        assert case["call_id"] == issued[0]["call_id"]
        assert case["call_position"] == 0
        assert case["arguments_sha256"] == issued[0]["arguments_sha256"]
    finally:
        _fmt_close(provider)


def test_partial_export_stream_zero_frames(tmp_path: Path) -> None:
    # the complete read prefix plus the just-issued stream exec:
    # zero retained stream frames, no poll target, zero issued polls
    provider, selected, wire = _fmt_partial_export(tmp_path, "stream-zero", [_w_read()])
    try:
        assert provider._fmt_posts == 2
        assert provider._fmt_polls == 0
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-result"
        assert snap["model_posts"] == 2
        assert snap["polls"] == 0
        # the wire ledger accounts the emitted response FRAMES; the
        # per-case retained output CONTENT bytes are the case fact
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 4, "output_bytes": wire}
        assert snap["cases"][0]["output_bytes"] == len(SEED["read-0"])
        assert len(snap["issued_calls"]) == 2
        assert snap["cases"][0]["status"] == "completed"
        assert snap["cases"][0]["verified"] is True
        assert snap["cases"][1]["case"] == model.FORMAT_CASES[1]["case"]
        assert snap["cases"][1]["status"] == "pending"
        assert snap["cases"][1]["results"] == []
        assert snap["cases"][1]["polls"] == 0
    finally:
        _fmt_close(provider)


def test_partial_export_running_initial_outstanding_poll(tmp_path: Path) -> None:
    # the transactional FSM over the real wire: the accepted running
    # initial committed the FIRST poll in the same transaction — ONE
    # issued (outstanding) poll while the per-case RETAINED poll
    # count is zero; the two ledgers stay separate in the export
    provider, selected, wire = _fmt_partial_export(
        tmp_path, "running-initial", [_w_read(), _w_stream_initial()]
    )
    try:
        assert provider._fmt_posts == 3
        assert provider._fmt_polls == 1
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-result"
        assert snap["model_posts"] == 3
        assert snap["polls"] == 1
        assert snap["cases"][1]["polls"] == 0
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 5, "output_bytes": wire}
        issued = snap["issued_calls"]
        assert len(issued) == 3
        assert issued[2]["name"] == model.FORMAT_POLL_TOOL
        assert model.format_arguments_exact(
            issued[2]["arguments"], model.format_expected_poll_arguments(_FMT_SESSION)
        )
        assert type(issued[2]["arguments"]["session_id"]) is int
        assert snap["cases"][1]["status"] == "pending"
        assert len(snap["cases"][1]["results"]) == 1
    finally:
        _fmt_close(provider)


def test_partial_export_full_bytes_running(tmp_path: Path) -> None:
    # the WHOLE source observed under actual running wrappers over
    # the real wire: byte equality does NOT prove completion — the
    # case stays PENDING with three retained running results while
    # the ACTUAL issued poll counter is three (the last one
    # outstanding)
    provider, selected, wire = _fmt_partial_export(
        tmp_path,
        "full-bytes-running",
        [
            _w_read(),
            _w_stream_initial(),
            _w_poll_running(),
            _w_stream_frame(_P2, _FMT_SESSION, None, "4.5000"),
        ],
    )
    try:
        assert provider._fmt_posts == 5
        assert provider._fmt_polls == 3
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-result"
        assert snap["model_posts"] == 5
        assert snap["polls"] == 3
        assert snap["cases"][1]["polls"] == 2
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 7, "output_bytes": wire}
        assert len(snap["issued_calls"]) == 5
        # the whole source is retained yet the case is NOT complete
        assert snap["cases"][1]["status"] == "pending"
        assert len(snap["cases"][1]["results"]) == 3
    finally:
        _fmt_close(provider)


def test_partial_export_completed_stream_next_pending(tmp_path: Path) -> None:
    # the completed stream prefix (the WHOLE source under running
    # wrappers plus the EMPTY completion frame) plus the pending
    # next case: the measured stream session is preserved on the
    # complete case record and the empty case is pending with zero
    # retained frames
    provider, selected, wire = _fmt_partial_export(
        tmp_path,
        "completed-next",
        [
            _w_read(),
            _w_stream_initial(),
            _w_poll_running(),
            _w_stream_frame(_P2, _FMT_SESSION, None, "4.5000"),
            _w_stream_frame("", _FMT_SESSION, 0, "6.5000"),
        ],
    )
    try:
        assert provider._fmt_posts == 6
        assert provider._fmt_polls == 3
        snap = selected["snapshot"]
        assert snap["final_state"] == "awaiting-result"
        assert snap["model_posts"] == 6
        assert snap["polls"] == 3
        assert wire > 0
        assert snap["controller_ledger"] == {"requests": 8, "output_bytes": wire}
        assert len(snap["issued_calls"]) == 6
        assert snap["issued_calls"][5]["name"] == model.FORMAT_EXEC_TOOL
        stream = snap["cases"][1]
        assert stream["status"] == "completed"
        assert stream["exit"] == 0
        assert stream["verified"] is True
        assert stream["session_id"] == _FMT_SESSION
        assert stream["polls"] == 3
        assert len(stream["results"]) == 4
        pending = snap["cases"][2]
        assert pending["case"] == model.FORMAT_CASES[2]["case"]
        assert pending["status"] == "pending"
        assert pending["results"] == []
        assert pending["polls"] == 0
        assert pending["call_id"] == snap["issued_calls"][5]["call_id"]
    finally:
        _fmt_close(provider)


def test_partial_export_tag_pair_dispatch(tmp_path: Path) -> None:
    # the closed export tag pair law at the real consumer seam: the
    # COMPLETE export tag with a PARTIAL snapshot (and the partial
    # tag with a complete snapshot) are both refusals — neither form
    # is relabeled into the other
    provider, selected, _wire = _fmt_partial_export(tmp_path, "tag-pair", [])
    try:
        bad = dict(selected)
        bad["record"] = model.SCHEMA_FORMAT_EXPORT
        payload = json.dumps(bad, sort_keys=True, separators=(",", ":")).encode()
        # The exporter holds its own model dependency; catch the exception
        # class of the exact raising module.
        with pytest.raises(exp.model.FixtureError):
            exp.validate_selected_payload(payload)
        bad2 = dict(selected)
        bad2["snapshot"] = build_positive()
        payload2 = json.dumps(bad2, sort_keys=True, separators=(",", ":")).encode()
        with pytest.raises(exp.model.FixtureError):
            exp.validate_format_payload_partial(payload2)
    finally:
        _fmt_close(provider)


def test_partial_export_exporter_teardown_fault_tears_down_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # injected exporter CLOSE fault: the real close happens first
    # (so the blocked accept reaps through the OSError path), then
    # the fault propagates; the helper must still tear down its OWN
    # provider on EVERY teardown failure and preserve the original
    # injected fault
    seen: dict[str, Any] = {}
    real_init = ctl.Exporter.__init__

    class _faulty_server:
        def __init__(self, inner: socket.socket) -> None:
            self._inner = inner

        def close(self) -> None:
            self._inner.close()
            raise RuntimeError("injected-exporter-close-fault")

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    def capture_init(self: Any, *args: Any, **kwargs: Any) -> None:
        real_init(self, *args, **kwargs)
        seen["provider"] = self.provider
        self.server = _faulty_server(self.server)

    monkeypatch.setattr(ctl.Exporter, "__init__", capture_init)
    with pytest.raises(RuntimeError, match="injected-exporter-close-fault"):
        _fmt_partial_export(tmp_path, "teardown-fault", None)
    provider = seen["provider"]
    assert provider.closed is True
    assert provider.accept_thread is not None
    assert not provider.accept_thread.is_alive()
    assert provider.listener.fileno() == -1
