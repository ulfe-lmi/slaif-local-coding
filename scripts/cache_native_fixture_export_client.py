"""Host-executed 21001 export client for the fixture (objective 017-r).

Executed by the host via ``docker exec --user 21001:21001`` against
the exact registered CID while the container still exists.  It talks
to the controller's protected exporter socket (peer-verified on the
server side via SO_PEERCRED), drives the ordered quiesce -> export
states, and emits the closed selected payload on its OWN stdout:

  line 1: quiesce-ok <closed quiesce record JSON>
  line 2: export-sha256 <64 hex>
  then:   the raw selected payload bytes (bounded, closed-validated)

The payload is a CLOSED object: exact top-level field set, the
model-validated quiesce and snapshot records, a diagnostic that is
either the closed unobserved marker (with a null observed position)
or a model-validated metadata diagnostic (with a nonnegative
position), and the seeded original count of base64 originals whose
DECODED BYTES bind to the snapshot (combined byte count and sha256).
Unknown fields, bad encodings, count/digest/bind mismatches, frame
truncation or trailing frame bytes are fixed failures: the raw
payload is NEVER emitted or reflected on failure.  This client
validates independently of the controller, and the host runner
re-validates the same closed records itself.  All blocking IO uses
the SAME shared absolute monotonic deadline (the host passes the
anchor to every scenario; it is never reset): the socket timeout is
bounded by the REMAINING time and set before each blocking read, and
an expired or invalid anchor is a typed terminal failure, never a
numeric fallback.  This client never writes to host paths (no bind
mounts).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import os
import socket
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_model as model  # noqa: E402

CTL_EXPORTER_SOCKET = "/run/slaif-ctl/socket/exporter.sock"
READ_TIMEOUT = 5.0
MAX_PAYLOAD = 16 * 1024 * 1024 + 128
_QUIESCE_LINE_CAP = 8192
_MAX_ORIGINAL_BYTES = 1024 * 1024
_FALLBACK_DEADLINE_SECONDS = 300.0
_EXPECTED_TOP_LEVEL = frozenset(
    {"quiesce", "snapshot", "diagnostic", "observed_at_position", "originals", "originals_count"}
)


class ExportFailure(Exception):
    """Typed terminal failure carrying the closed reason."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def out(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def fail(reason: str) -> int:
    # fixed closed reason only: no raw payload, header or error text
    out(f"export-fail {reason}")
    return 2


def _deadline() -> float:
    """The SAME shared absolute monotonic anchor the host passes to
    every scenario.  The hosted runner always provides it; the
    finite fallback exists only for local pure tests and never
    resets a real scenario budget."""
    raw = os.environ.get("SLAIF_FIXTURE_DEADLINE_ABS", "")
    if not raw:
        return time.monotonic() + _FALLBACK_DEADLINE_SECONDS
    try:
        absolute = float(raw)
    except ValueError:
        raise ExportFailure("deadline-invalid") from None
    if not math.isfinite(absolute) or absolute <= time.monotonic():
        raise ExportFailure("deadline-expired")
    return absolute


def _remaining(deadline: float) -> float:
    left = deadline - time.monotonic()
    if left <= 0:
        raise ExportFailure("deadline-expired")
    return left


def _bound(sock: socket.socket, deadline: float) -> None:
    """Set the socket timeout to the REMAINING total budget (capped
    by the per-op bound) BEFORE a blocking IO call."""
    sock.settimeout(min(READ_TIMEOUT, _remaining(deadline)))


def _connect(deadline: float) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        _bound(sock, deadline)
        sock.connect(CTL_EXPORTER_SOCKET)
    except BaseException:
        sock.close()
        raise
    return sock


def _recv_line(sock: socket.socket, deadline: float, max_bytes: int) -> bytes:
    data = b""
    while b"\n" not in data:
        _bound(sock, deadline)
        chunk = sock.recv(1)
        if not chunk:
            raise OSError("eof")
        data += chunk
        if len(data) > max_bytes:
            raise ValueError("overbound")
    return data


def _recv_exact(sock: socket.socket, deadline: float, n: int) -> bytes:
    data = b""
    while len(data) < n:
        _bound(sock, deadline)
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise OSError("truncated")
        data += chunk
    return data


def validate_payload(payload: bytes) -> dict:
    """Closed-object proof of the selected payload BEFORE any
    publication: exact top-level field set, model-validated nested
    records, closed diagnostic/position consistency, exactly the
    shared seeded original count of decodable base64 originals whose
    DECODED bytes bind to the snapshot record (combined byte count
    and sha256 — a matching frame digest proves framing integrity
    only, never original binding).  Raises ValueError on any
    violation."""
    try:
        selected = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise ValueError("payload-not-closed") from None
    if not isinstance(selected, dict) or set(selected) != _EXPECTED_TOP_LEVEL:
        raise ValueError("payload-fields")
    model.validate_quiesce_record(selected["quiesce"])
    snapshot = selected["snapshot"]
    model.validate_snapshot_record(snapshot)
    diagnostic = selected["diagnostic"]
    position = selected["observed_at_position"]
    if diagnostic == {"state": "unobserved"}:
        if position is not None:
            raise ValueError("payload-state")
    else:
        model.validate_metadata_diagnostic(diagnostic)
        if not isinstance(position, int) or isinstance(position, bool) or position < 0:
            raise ValueError("payload-position")
    originals = selected["originals"]
    count = selected["originals_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count != model.ORIGINALS_COUNT:
        raise ValueError("payload-originals")
    if not isinstance(originals, list) or len(originals) != count:
        raise ValueError("payload-originals")
    decoded: list[bytes] = []
    for original in originals:
        if not isinstance(original, str):
            raise ValueError("payload-originals")
        try:
            raw = original.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("payload-originals") from None
        try:
            data = base64.b64decode(raw, validate=True)
        except (binascii.Error, ValueError):
            raise ValueError("payload-originals") from None
        if not data or len(data) > _MAX_ORIGINAL_BYTES:
            raise ValueError("payload-originals")
        decoded.append(data)
    combined = b"".join(decoded)
    if len(combined) != snapshot["originals_bytes"]:
        raise ValueError("payload-original-binding")
    if hashlib.sha256(combined).hexdigest() != snapshot["originals_sha256"]:
        raise ValueError("payload-original-binding")
    return selected


def validate_format_payload(payload: bytes) -> dict:
    """Closed-object proof of the DISTINCT selected
    format-capture payload BEFORE any publication: the exact
    three-field top level (record tag, quiesce, snapshot), the
    model-validated quiesce record, and the nested format
    snapshot RE-VALIDATED by the closed format-snapshot law
    (strict pinned wrapper re-parse, immutable seed identity,
    closed chains, the typed issued-identity law).  The TOTAL
    serialized payload (tag + quiesce + snapshot) is bounded at
    the 256 KiB selected-capture bound; the owner's outer
    identity metadata (binding/identity/CID) is added by the
    owner and bounded by the SAME total at the consumer and
    producer seams — this payload bound is the transport's
    share of that total, never a replacement for it.  Raises
    ValueError on any violation.  The original selected
    payload's exact historical field set and law are unchanged
    (``validate_payload`` is never widened)."""
    try:
        selected = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise ValueError("format-payload-not-closed") from None
    if not isinstance(selected, dict) or set(selected) != {
        "record",
        "quiesce",
        "snapshot",
    }:
        raise ValueError("format-payload-fields")
    if selected["record"] != model.SCHEMA_FORMAT_EXPORT:
        raise ValueError("format-payload-tag")
    model.validate_quiesce_record(selected["quiesce"])
    model.validate_format_snapshot_record(selected["snapshot"])
    if len(payload) > model.FORMAT_SNAPSHOT_MAX_BYTES:
        raise ValueError("format-payload-overbound")
    return selected


def validate_format_payload_partial(payload: bytes) -> dict:
    """Closed-object proof of the DISTINCT safe PARTIAL selected
    format-capture payload BEFORE any publication: the exact
    three-field top level (record tag, quiesce, snapshot), the
    model-validated quiesce record, and the nested PARTIAL
    snapshot RE-VALIDATED by the closed partial-snapshot law
    (strict pinned wrapper re-parse of every retained frame,
    immutable seed identity, the typed issued-identity prefix
    law, honest pending facts, the closed not-qualified fact).
    The TOTAL serialized payload (tag + quiesce + snapshot) is
    bounded at the 256 KiB selected-capture bound; the owner's
    outer identity metadata (binding/identity/CID) is added by
    the owner and bounded by the SAME total at the consumer and
    producer seams — this payload bound is the transport's
    share of that total, never a replacement for it.  Raises
    ValueError on any violation.  The COMPLETE format payload's
    exact law is unchanged (``validate_format_payload``), and
    the original six-field payload's exact historical field set
    and law are never widened (``validate_payload``)."""
    try:
        selected = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise ValueError("format-payload-not-closed") from None
    if not isinstance(selected, dict) or set(selected) != {
        "record",
        "quiesce",
        "snapshot",
    }:
        raise ValueError("format-payload-fields")
    if selected["record"] != model.SCHEMA_FORMAT_EXPORT_PARTIAL:
        raise ValueError("format-payload-tag")
    model.validate_quiesce_record(selected["quiesce"])
    model.validate_format_snapshot_record_partial(selected["snapshot"])
    if len(payload) > model.FORMAT_SNAPSHOT_MAX_BYTES:
        raise ValueError("format-payload-overbound")
    return selected


def validate_selected_payload(payload: bytes) -> dict:
    """The closed dispatcher over the DISTINCT selected payload
    forms: the payload's closed record tag selects its
    validator (the COMPLETE format-capture tag and the safe
    PARTIAL format-capture tag are the canonical 017-aj entry's
    scenario forms; the original six-field payload — which
    carries NO record tag — keeps its exact historical law
    unchanged).  A malformed object is a refusal of every
    form."""
    try:
        selected = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise ValueError("payload-not-closed") from None
    if isinstance(selected, dict):
        tag = selected.get("record")
        if tag == model.SCHEMA_FORMAT_EXPORT:
            return validate_format_payload(payload)
        if tag == model.SCHEMA_FORMAT_EXPORT_PARTIAL:
            return validate_format_payload_partial(payload)
    return validate_payload(payload)


def _run(deadline: float) -> None:
    # -- quiesce ---------------------------------------------------------
    sock = _connect(deadline)
    try:
        _bound(sock, deadline)
        sock.sendall(b"quiesce\n")
        line = _recv_line(sock, deadline, _QUIESCE_LINE_CAP)
    finally:
        sock.close()
    text = line.decode("ascii", "replace").strip()
    if not text.startswith("quiesce-ok "):
        raise ExportFailure("quiesce-state")
    record = json.loads(text[len("quiesce-ok ") :])
    model.validate_quiesce_record(record)
    out("quiesce-ok " + json.dumps(record, sort_keys=True, separators=(",", ":")))

    # -- export -------------------------------------------------------------
    sock = _connect(deadline)
    try:
        _bound(sock, deadline)
        sock.sendall(b"export\n")
        header = _recv_exact(sock, deadline, 4)
        (length,) = struct.unpack(">I", header)
        if length > MAX_PAYLOAD:
            raise ExportFailure("export-overbound")
        payload = _recv_exact(sock, deadline, length)
        digest = _recv_exact(sock, deadline, 64)
        if digest.decode("ascii", "replace").lower() != hashlib.sha256(payload).hexdigest():
            raise ExportFailure("export-digest")
        # frame completion: the server closes the channel after the
        # exact frame; trailing bytes are a frame violation
        _bound(sock, deadline)
        if sock.recv(1):
            raise ValueError("frame-extra")
        # closed-object proof BEFORE any raw payload emission
        # (the payload's closed record tag selects its DISTINCT
        # validator; see validate_selected_payload)
        validate_selected_payload(payload)
    finally:
        sock.close()
    out("export-sha256 " + hashlib.sha256(payload).hexdigest())
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()


def main() -> int:
    try:
        if os.getuid() != 21001:
            return fail("uid-not-21001")
        _run(_deadline())
        return 0
    except ExportFailure as exc:
        return fail(exc.reason)
    except (OSError, ValueError, UnicodeDecodeError, struct.error, model.FixtureError):
        return fail("export-invalid")


if __name__ == "__main__":
    raise SystemExit(main())
