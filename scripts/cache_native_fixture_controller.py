"""21001 Python controller (container PID1) for the serial right-pane
native fixture (017-r).

Stdlib only.  The controller owns the fixture's private controller
root (/run/slaif-ctl, 0700, UID 21001): the loopback fake provider
speaking the REAL Responses-API wire shape (SSE event envelopes with
closed event/item types, a fixed final text and no tools in the
terminal response), the exact-issued call registry, the seeded
synthetic originals, the sentinel file, and the protected exporter
socket.  Nothing here is reachable by the 21002 subject (the
stand-in's denial proofs cover each protected target), and nothing
is exported before verified teardown of everything except the
container itself.

Issuance law: the controller issues calls at ITS OWN causal request
position (the first admitted /v1/responses request of a run),
selecting ONLY known function tools from the admitted request's
schema-evidenced tools region.  Caller-authored flags, replayed
phases or arbitrary inbound progress can never issue, reset or
advance the scenario; the second admitted request validates
function_call_output references against the immutable registry; the
third is refused as scenario-bounded.

Metadata diagnostic: starts UNOBSERVED and is derived only from the
bounded actual admitted request (real endpoint, closed tool-region
metadata, explicit unknown/unsupported states preserved); an
unobserved controller exports the closed unobserved marker, never a
canned tool mode.

Scenario law: the scenario is SELECTED BY THE TRUSTED HOST before the
container/provider starts (constructor/config enum, never an HTTP
payload flag).  "diagnostic" (the default safe fallback for the later
first visible run) observes the actual tools region of one valid
request and answers the fixed assistant final text with NO tool call;
"tool-cycle" (the disposable-CI Python stand-in proof) issues the
known tools at the first causal position, then validates complete
exact-issued results, then answers the fixed terminal text.  A small
controller-owned state machine (awaiting-issue -> awaiting-results ->
done) is fenced under one lock with the locally allocated immutable
causal request position; malformed, refused, preloaded, replayed or
out-of-order requests consume their request/attempt budgets but never
advance, reset or select the semantic scenario state.

Resource law: admission is gated and accounted BEFORE any handler
thread is spawned or retained (global serialized ledger accounting
under one lock, finite thread/connection caps, dead-thread pruning,
bounded refused-connection drain); accepted sockets have finite read
timeouts, per-read absolute-deadline checks, an exact supported
HTTP grammar (method/path/version/headers/single Content-Length,
complete body proof) and fixed non-echoing failure outcomes.
The header byte budget applies to ACTUAL header bytes only (a valid
large body arriving coalesced with its small header is accepted),
and the response output budget accounts the exact complete intended
wire bytes under the global lock BEFORE any sendall: a physical
output cap is never checked after emission.

Exporter: SO_PEERCRED (the exact 12-byte three-int struct ucred
ABI) peer/ownership verification; explicit ordered states
running -> quiesced -> exported (one immutable snapshot, premature
or repeated export refused); bounded command framing; cumulative
experiment deadline (never reset between phases).

Fault-injection modes (declared failure paths): export-fail (the
export frame corrupts after a bounded prefix), quiesce-fail (no
closed quiesce record is produced), crash (self-termination after
measured readiness).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import stat as stat_mod
import struct
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_model as model  # noqa: E402

CTL_DIR = "/run/slaif-ctl"
CTL_SOCKET_DIR = f"{CTL_DIR}/socket"
CTL_EXPORTER_SOCKET = f"{CTL_SOCKET_DIR}/exporter.sock"
CTL_ISSUED_REGISTRY = f"{CTL_DIR}/issued-registry.json"
CTL_ORIGINALS_DIR = f"{CTL_DIR}/originals"
CTL_SENTINEL = f"{CTL_DIR}/sentinel"
PROVIDER_HOST = "127.0.0.1"

SUBJECT_UID = 21002
CONTROLLER_UID = 21001

REQUEST_CAP_BYTES = 1024 * 1024
HEADER_CAP_BYTES = 8192
RESPONSE_CAP_BYTES = 1024 * 1024
COMMAND_CAP_BYTES = 64
MAX_EXPORT_BYTES = 16 * 1024 * 1024
HEALTH_BODY = b'{"slaif-fixture":"provider-health"}'
ORIGINALS_COUNT = 3
FIXED_FINAL_TEXT = "slaif fixed final text"
ROUTE_HEALTH = "/healthz"
ROUTE_RESPONSES = "/v1/responses"
READ_CHUNK_BYTES = 65536
READ_TIMEOUT_SECONDS = 2.0

# Closed fixed synthetic arguments per known tool (the controller's
# own declared scenario content; digests are what the registry binds).
_TOOL_ARGUMENTS: dict[str, dict] = {
    "exec_command": {"cmd": "slaif-synthetic-cmd"},
    "write_stdin": {"session_id": 0, "chars": "slaif-synthetic"},
}
_SSE_CREATED = "response.created"
_SSE_ITEM_ADDED = "response.output_item.added"
_SSE_ITEM_DONE = "response.output_item.done"
_SSE_COMPLETED = "response.completed"


def expected_call_id(name: str, position: int, index: int) -> str:
    """The closed deterministic issued call id for a known tool at
    the controller's request position and tools-region index.
    SINGLE SOURCE OF TRUTH: the controller's issuance and the
    host runner's binding revalidation both derive the id from this
    one function (an independently re-derived copy could drift)."""
    return "slaif-syn-" + model.sha256_bytes(f"{name}|{position}|{index}".encode())[:24]


def expected_arguments_sha256(name: str) -> str:
    """The closed argument digest the registry binds for a known
    tool (the controller's declared fixed synthetic arguments,
    canonicalized); the host revalidation compares the exported
    snapshot binding against this same derivation."""
    return model.sha256_bytes(model.canonical_bytes(_TOOL_ARGUMENTS[name]))


class ControllerError(RuntimeError):
    """Fixed-reason controller failure (never echoes raw content)."""


def log_closed(record: dict) -> None:
    """Bounded closed stdout record (the no-log-driver container
    discards it; kept for in-image bounded debugging only)."""
    try:
        line = json.dumps(record, sort_keys=True, separators=(",", ":"))
        if len(line.encode()) <= 8192:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
    except (OSError, TypeError, ValueError):
        pass


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        raise ControllerError("env-invalid") from None


def prepare_root() -> None:
    for path in (CTL_DIR, CTL_SOCKET_DIR, CTL_ORIGINALS_DIR):
        if os.path.lexists(path):
            if os.path.islink(path) or not os.path.isdir(path):
                raise ControllerError("root-path-untrusted")
        else:
            os.makedirs(path)
        os.chmod(path, 0o700)
    sentinel = b"slaif-synthetic-controller-sentinel-017r\n"
    with open(CTL_SENTINEL, "wb") as handle:
        handle.write(sentinel)
    os.chmod(CTL_SENTINEL, 0o600)


def originals_identity(originals_dir: str) -> tuple[int, str, list[bytes]]:
    """Combined (bytes, sha256, contents) of the fixed seeded
    originals in the given controller-owned directory."""
    digest = hashlib.sha256()
    total = 0
    originals = []
    for index in range(ORIGINALS_COUNT):
        data = open(f"{originals_dir}/{index}", "rb").read()
        digest.update(data)
        total += len(data)
        originals.append(data)
    return total, digest.hexdigest(), originals


def verify_controller_owned() -> None:
    """The controller proves, from its OWN 21001 identity, that every
    protected target exists and is controller-owned (the
    present_21001 half of the subject's denial proofs).  All required
    paths are seeded BEFORE this check runs."""
    for _name, path, want_dir in (
        ("controller_socket_dir", CTL_SOCKET_DIR, True),
        ("issued_registry", CTL_ISSUED_REGISTRY, False),
        ("controller_originals", CTL_ORIGINALS_DIR, True),
        ("controller_sentinel", CTL_SENTINEL, False),
        ("controller_proc", "/proc/1", True),
        ("exporter_socket", CTL_EXPORTER_SOCKET, False),
    ):
        try:
            st = os.lstat(path)
            is_dir = os.path.isdir(path)
            ok = (is_dir == want_dir) and st.st_uid == os.getuid() and not os.path.islink(path)
        except OSError:
            ok = False
        if not ok:
            raise ControllerError("controller-ownership-unverified")


# -- bounded exact HTTP request grammar ----------------------------------------
def _parse_request(
    conn: socket.socket, ledger_lock: threading.Lock, ledger: model.FixtureLedger
) -> tuple[str, str, bytes]:
    """Exact supported HTTP grammar: one request line, closed method
    and version, single nonconflicting Content-Length, no
    Transfer-Encoding, complete body proof, per-read deadline and
    byte budgets.  The header budget applies to ACTUAL header bytes
    only: a valid large body arriving coalesced with its small header
    is accepted, an overbound header is refused.  The path itself is
    passed through to the closed routing table (an unknown route is a
    fixed 400 there, never a silent close).  Fixed non-echoing
    failure outcomes."""

    def _deadline_ok() -> None:
        with ledger_lock:
            ledger.require_within_deadline()

    data = bytearray()
    while True:
        _deadline_ok()
        chunk = conn.recv(READ_CHUNK_BYTES)
        if not chunk:
            raise ControllerError("request-truncated")
        data.extend(chunk)
        end = data.find(b"\r\n\r\n")
        if end != -1:
            if end > HEADER_CAP_BYTES:
                raise ControllerError("request-overbound")
            break
        if len(data) > HEADER_CAP_BYTES:
            # No header terminator inside the header budget: the
            # header itself is overbound, whatever the body length.
            raise ControllerError("request-overbound")
    try:
        header, _, rest = bytes(data).partition(b"\r\n\r\n")
        lines = header.decode("ascii").split("\r\n")
    except UnicodeDecodeError:
        raise ControllerError("request-grammar") from None
    if len(lines) < 2:
        raise ControllerError("request-grammar")
    request_line = lines[0].split(" ")
    if len(request_line) != 3:
        raise ControllerError("request-line")
    method, path, version = request_line
    if method not in ("GET", "POST"):
        raise ControllerError("method")
    if not path or not path.startswith("/"):
        raise ControllerError("route")
    if version != "HTTP/1.1":
        raise ControllerError("version")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            raise ControllerError("header")
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "transfer-encoding":
            raise ControllerError("header")
        if key in headers and headers[key] != value:
            raise ControllerError("header")
        headers[key] = value
    length_raw = headers.get("content-length")
    if method == "GET":
        if length_raw is not None and length_raw != "0":
            raise ControllerError("length")
        return method, path, b""
    if length_raw is None or not length_raw.isdigit():
        raise ControllerError("length")
    length = int(length_raw)
    if length > REQUEST_CAP_BYTES:
        raise ControllerError("request-overbound")
    body = rest
    while len(body) < length:
        _deadline_ok()
        chunk = conn.recv(READ_CHUNK_BYTES)
        if not chunk:
            raise ControllerError("request-truncated")
        body += chunk
    if len(body) != length:
        raise ControllerError("request-overbound")
    return method, path, body


def _final_message() -> dict:
    """The fixed terminal item: the public 0.164.0 ResponseItem::
    Message shape (REQUIRED role, closed content with required
    output_text text), fixed text, never tools."""
    return {
        "type": "message",
        "id": "msg_slaif_final",
        "role": "assistant",
        "content": [{"type": "output_text", "text": FIXED_FINAL_TEXT}],
    }


def _has_preloaded_outputs(payload: dict) -> bool:
    """A request that already carries function_call_output items is
    presenting inbound results; at the issue/diagnostic state those
    are refused as preloaded, never consumed as progress."""
    input_items = payload.get("input")
    if not isinstance(input_items, list):
        return False
    return any(
        isinstance(item, dict) and item.get("type") == "function_call_output"
        for item in input_items
    )


# -- provider (real Responses-API wire) ------------------------------------------
class Provider:
    """Bounded loopback fake provider on the real /v1/responses route.

    The host-selected scenario (diagnostic default safe fallback vs
    CI tool-cycle) is a construction-time closed enum: a request body
    can never select, switch or advance it.  The controller-owned
    state machine (awaiting-issue -> awaiting-results -> done) is
    fenced under one lock together with the locally allocated
    immutable causal request position; issuance selects ONLY known
    function tools from the admitted request's schema-evidenced tools
    region; results must cover the exact-issued registry completely;
    anything after the terminal state is scenario-bounded.  Unknown
    offered modes stay the fixed unsupported state inside the observed
    diagnostic — never synthetic aliases.
    """

    def __init__(
        self,
        port: int,
        ledger: model.FixtureLedger,
        registry: model.IssuedRegistry,
        ledger_lock: threading.Lock,
        scenario: str = "diagnostic",
        originals_dir: str = CTL_ORIGINALS_DIR,
        exporter_uid: int | None = None,
    ):
        if scenario not in ("diagnostic", "tool-cycle"):
            raise ControllerError("scenario-invalid")
        self.scenario = scenario
        self.originals_dir = originals_dir
        # The synthetic snapshot record states the exporter uid the
        # closed record law requires.  Production records the actual
        # controller process uid (os.getuid(); the main() guard makes
        # it CONTROLLER_UID) and fails closed if it is not, so a
        # misuided controller can never publish a truthful-looking
        # record.  Pure local tests inject the production identity
        # explicitly (the record is synthetic: True).
        self.exporter_uid = os.getuid() if exporter_uid is None else exporter_uid
        self.port = port
        self.ledger = ledger
        self.ledger_lock = ledger_lock
        self.registry = registry
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((PROVIDER_HOST, port))
        self.listener.listen(16)
        self.port = self.listener.getsockname()[1]
        self.lock = threading.Lock()
        self.active: list[socket.socket] = []
        self.handlers: list[threading.Thread] = []
        self.accept_thread: threading.Thread | None = None
        self.closed = False
        # Controller-owned semantic scenario state (fenced).
        self.scenario_state = "awaiting-issue"
        self.scenario_lock = threading.Lock()
        # Unobserved until a real admitted request is measured.
        self.diagnostic: dict | None = None
        self.observed_at_position: int | None = None
        self._seeded_originals_sha: str | None = None
        self._verified_originals: list[bytes] | None = None

    # -- seeded originals (fixed BEFORE any service start) -----------------
    def seed_originals(self) -> str:
        """Seed the fixed synthetic originals in the controller-owned
        directory BEFORE any service start; the export oracle must
        never be written after.  Binds the combined identity digest
        the snapshot later verifies against."""
        if os.path.lexists(self.originals_dir):
            if os.path.islink(self.originals_dir) or not os.path.isdir(self.originals_dir):
                raise ControllerError("originals-path-untrusted")
        else:
            os.makedirs(self.originals_dir)
        os.chmod(self.originals_dir, 0o700)
        for index in range(ORIGINALS_COUNT):
            path = f"{self.originals_dir}/{index}"
            with open(path, "wb") as handle:
                handle.write(f"slaif-synthetic-original-{index}-017r\n".encode() * (512 // 32))
            os.chmod(path, 0o600)
        _total, digest, _originals = originals_identity(self.originals_dir)
        self._seeded_originals_sha = digest
        return digest

    # -- ledger accounting (globally serialized) -------------------------
    def _account(self, name: str) -> None:
        with self.ledger_lock:
            getattr(self.ledger, f"record_{name}")()

    # -- admission (gated BEFORE spawn/retention) -------------------------
    def serve(self) -> None:
        while not self.closed:
            try:
                self.listener.settimeout(READ_TIMEOUT_SECONDS)
                conn, _ = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                break
            if self.closed:
                try:
                    conn.close()
                except OSError:
                    pass
                break
            # Gate admission: prune dead handlers, enforce the finite
            # thread/connection caps, serialize the accounting.
            with self.lock:
                self.handlers = [t for t in self.handlers if t.is_alive()]
                try:
                    self._account("connection")
                    self._account("thread")
                    self.active.append(conn)
                    self.handlers.append(None)  # placeholder, replaced below
                except model.BudgetExceeded:
                    # Refuse bounded: no thread spawned, no retention.
                    try:
                        conn.close()
                    except OSError:
                        pass
                    self.closed = True
                    break
            thread = threading.Thread(target=self._handle, args=(conn,), daemon=True)
            with self.lock:
                if self.handlers and self.handlers[-1] is None:
                    self.handlers[-1] = thread
            thread.start()

    def _read_with_deadline(self, conn: socket.socket) -> bytes:
        conn.settimeout(READ_TIMEOUT_SECONDS)
        return _parse_request(conn, self.ledger_lock, self.ledger)

    def _handle(self, conn: socket.socket) -> None:
        try:
            with self.ledger_lock:
                self.ledger.require_within_deadline()
            method, path, body = self._read_with_deadline(conn)
            position: int | None = None
            if method == "POST" and path == ROUTE_RESPONSES:
                # Allocate the immutable causal request position
                # LOCALLY under the global lock before any semantic
                # step; later reads of the shared counter are never
                # used as causal identity.
                with self.ledger_lock:
                    position = self.ledger.record_request() - 1
            status, content_type, payload = self._route(method, path, body, position)
            if len(payload) > RESPONSE_CAP_BYTES:
                raise ControllerError("response-overbound")
            header = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(payload)}\r\n"
                f"Connection: close\r\n\r\n"
            )
            frame = header.encode() + payload
            # Account the EXACT complete intended wire bytes under the
            # global lock BEFORE any emission: an overbound response
            # is never partially sent, and a physical output cap is
            # never checked after send.
            with self.ledger_lock:
                self.ledger.record_output(len(frame))
            conn.sendall(frame)
        except (ControllerError, model.FixtureError, OSError, ValueError):
            pass  # fixed closed failure: nothing is reflected back
        finally:
            with self.lock:
                if conn in self.active:
                    self.active.remove(conn)
            try:
                conn.close()
            except OSError:
                pass

    # -- routing (real wire shape) ------------------------------------------
    def _route(
        self, method: str, path: str, body: bytes, position: int | None
    ) -> tuple[str, str, bytes]:
        if method == "GET" and path == ROUTE_HEALTH:
            return "200 OK", "application/json", HEALTH_BODY
        if method != "POST" or path != ROUTE_RESPONSES or position is None:
            return self._error("route")
        try:
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._error("malformed-request")
        if not isinstance(payload, dict):
            return self._error("malformed-request")
        # One fenced semantic decision: the observation, the scenario
        # state and its transition are serialized so concurrent
        # requests can never double-issue, reorder or skip the
        # scenario.  The position is the locally allocated immutable
        # causal identity of THIS request.
        with self.scenario_lock:
            if self.diagnostic is None:
                try:
                    self.diagnostic = model.bounds_diagnostic(payload)
                    self.observed_at_position = position
                except model.FixtureError:
                    return self._error("tools-overbound")
            if self.scenario == "diagnostic":
                return self._diagnostic_step(payload, position)
            if self.scenario_state == "awaiting-issue":
                return self._issue_step(payload, position)
            if self.scenario_state == "awaiting-results":
                return self._validate_step(payload, position)
            return self._error("scenario-bounded")

    def _diagnostic_step(self, payload: dict, position: int) -> tuple[str, str, bytes]:
        """Default safe fallback for the later first visible run:
        the actual tools region was just observed, and the answer is
        the fixed assistant final text with NO tool call, whatever
        tools were offered (known or unknown).  One exchange; the
        scenario is bounded after it."""
        if self.scenario_state != "awaiting-issue":
            return self._error("scenario-bounded")
        if _has_preloaded_outputs(payload):
            return self._error("preloaded-result")
        self.scenario_state = "done"
        return (
            "200 OK",
            "text/event-stream",
            self._sse(
                response_id=f"resp_slaif_diag_{position}",
                items=[_final_message()],
            ),
        )

    def _issue_step(self, payload: dict, position: int) -> tuple[str, str, bytes]:
        """Controller-owned issuance at the locally allocated causal
        request position.  Preloaded inbound results are refused,
        never treated as progress or selection; only known function
        tools from the admitted request's tools region are issued,
        with the exact closed synthetic arguments the registry
        digests."""
        if _has_preloaded_outputs(payload):
            return self._error("preloaded-result")
        tools = payload.get("tools")
        if not isinstance(tools, list):
            return self._error("no-issuable-tools")
        items: list[dict] = []
        for index, entry in enumerate(tools):
            if not isinstance(entry, dict) or entry.get("type") != "function":
                continue
            name = entry.get("name")
            if not isinstance(name, str) or name not in model.KNOWN_TOOL_NAMES:
                continue  # unknown offered mode: fixed unsupported state
            arguments = _TOOL_ARGUMENTS[name]
            arguments_sha = expected_arguments_sha256(name)
            call_id = expected_call_id(name, position, index)
            try:
                self.registry.issue("function", name, call_id, arguments_sha, position)
            except model.FixtureError:
                return self._error("issue-rejected")
            items.append(
                {
                    "type": "function_call",
                    "id": f"msg_slaif_fc_{position}_{index}",
                    "call_id": call_id,
                    "name": name,
                    "arguments": json.dumps(arguments, sort_keys=True, separators=(",", ":")),
                }
            )
        if not items:
            return self._error("no-issuable-tools")
        self.scenario_state = "awaiting-results"
        return (
            "200 OK",
            "text/event-stream",
            self._sse(
                response_id=f"resp_slaif_syn_{position}",
                items=items,
            ),
        )

    def _validate_step(self, payload: dict, position: int | None) -> tuple[str, str, bytes]:
        """Complete-result validation against the exact-issued
        registry: every issued call must be referenced EXACTLY ONCE
        (no duplicates, no missing, no foreign ids); the immutable
        registry binding (family/name/argument digest/causal
        position) is what the snapshot exports, because the wire
        reference carries the call id only.  The result request's own
        immutable local position must be STRICTLY AFTER the issuance
        position (an overtaken or same-position handler can never
        pass matching ids as order).  Any incomplete, conflicting or
        out-of-order set is refused without advancing the state."""
        if not isinstance(position, int) or isinstance(position, bool) or position < 0:
            return self._error("causal-position")
        issued_positions = [entry["request_position"] for entry in self.registry.entries()]
        if issued_positions and position <= max(issued_positions):
            return self._error("causal-order")
        input_items = payload.get("input")
        if not isinstance(input_items, list):
            return self._error("missing-calls")
        refs = [
            item
            for item in input_items
            if isinstance(item, dict) and item.get("type") == "function_call_output"
        ]
        if not refs:
            return self._error("missing-calls")
        for ref in refs:
            if not isinstance(ref.get("output"), str):
                return self._error("malformed-result")
        call_ids = [ref.get("call_id") for ref in refs]
        if any(not isinstance(c, str) or not c for c in call_ids):
            return self._error("slaif_fixture_partial")
        if len(set(call_ids)) != len(call_ids):
            return self._error("slaif_fixture_partial")
        expected = {entry["call_id"] for entry in self.registry.entries()}
        offered = set(call_ids)
        if offered - expected:
            return self._error("slaif_fixture_unissued")
        if offered != expected:
            return self._error("slaif_fixture_partial")
        for call_id in call_ids:
            state, _ = self.registry.lookup(call_id)
            if state != "exact_issued":
                return self._error("slaif_fixture_unissued")
        self.scenario_state = "done"
        return (
            "200 OK",
            "text/event-stream",
            self._sse(
                response_id="resp_slaif_final",
                items=[_final_message()],
            ),
        )

    def _sse(self, response_id: str, items: list[dict]) -> bytes:
        """Exact 0.164.0 wire subset (public source, tag
        6aaac694803004a63c6f393d153c96d22521a6b9): response.created,
        then for each output item response.output_item.added
        followed by response.output_item.done — the DISTINCT native
        event paths carrying the same completed item — then
        response.completed.  Item shapes carry the exact required
        fields (message role required; output_text text required,
        annotations optional and omitted; function_call
        name/call_id/arguments required)."""

        def event(event_type: str, data: dict) -> str:
            payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
            return f"event: {event_type}\ndata: {payload}\n\n"

        created = {
            "type": _SSE_CREATED,
            "response": {
                "id": response_id,
                "object": "response",
                "status": "in_progress",
                "output": [],
            },
        }
        blocks = [event(_SSE_CREATED, created)]
        for index, item in enumerate(items):
            blocks.append(
                event(
                    _SSE_ITEM_ADDED,
                    {
                        "type": _SSE_ITEM_ADDED,
                        "output_index": index,
                        "item": item,
                    },
                )
            )
            blocks.append(
                event(
                    _SSE_ITEM_DONE,
                    {
                        "type": _SSE_ITEM_DONE,
                        "output_index": index,
                        "item": item,
                    },
                )
            )
        completed = {
            "type": _SSE_COMPLETED,
            "response": {"id": response_id, "status": "completed", "output": items},
        }
        blocks.append(event(_SSE_COMPLETED, completed))
        return "".join(blocks).encode("utf-8")

    def _error(self, code: str) -> tuple[str, str, bytes]:
        messages = {
            "malformed-request": "request body is not a valid object",
            "route": "route is not supported",
            "no-issuable-tools": "no issuable function tools offered",
            "missing-calls": "no function call outputs referenced",
            "preloaded-result": "inbound call results are refused at this scenario state",
            "malformed-result": "call result shape is not supported",
            "scenario-bounded": "declared scenario is bounded",
            "causal-position": "causal request position is not closed",
            "causal-order": "result request is not after issuance",
            "slaif_fixture_unissued": "call identity not runtime issued",
            "slaif_fixture_mismatched": "call identity mismatched",
            "slaif_fixture_partial": "call result set is incomplete",
            "issue-rejected": "issuance was refused",
            "tools-overbound": "offered tools exceed the finite bound",
            "request-truncated": "request is incomplete",
            "request-overbound": "request exceeds the finite bound",
            "request-grammar": "request grammar is not supported",
            "request-line": "request line is not supported",
            "method": "method is not supported",
            "version": "protocol version is not supported",
            "header": "header set is not supported",
            "length": "content length is not supported",
            "response-overbound": "response exceeds the finite bound",
        }
        message = messages.get(code, "request is not supported")
        body = json.dumps(
            {"error": {"message": message, "type": "invalid_request_error", "code": code}}
        ).encode()
        return "400 Bad Request", "application/json", body

    # -- quiesce (ordered, measured, final) ---------------------------------
    def quiesce(self, peer_pid: int | None, subject_scan=None, tools_scan=None) -> dict:
        """Close admission, wake and join every handler, then MEASURE
        the final closure state.  A daemon or scan failure is a
        failure, never a silent zero."""
        with self.lock:
            self.closed = True
        try:
            self.listener.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        accept = self.accept_thread
        if accept is not None and accept is not threading.current_thread():
            accept.join(timeout=READ_TIMEOUT_SECONDS)
            if accept.is_alive():
                raise ControllerError("quiesce-accept-alive")
        limit = self.ledger.deadline_monotonic()
        deadline_left = (
            (limit - time.monotonic()) if limit is not None else READ_TIMEOUT_SECONDS * 2
        )
        with self.lock:
            for conn in list(self.active):
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            handlers = list(self.handlers)
        join_timeout = max(0.05, min(2.0, deadline_left / max(1, len(handlers))))
        for thread in handlers:
            thread.join(timeout=join_timeout)
        with self.lock:
            alive = [t for t in self.handlers if t.is_alive()]
            active_count = len(self.active)
        subjects = subject_scan() if subject_scan is not None else count_uid_processes(SUBJECT_UID)
        tools = tools_scan(peer_pid) if tools_scan is not None else count_controller_tools(peer_pid)
        if subjects < 0 or tools < 0:
            raise ControllerError("quiesce-scan-degraded")
        record = {
            "record": model.SCHEMA_QUIESCE,
            "provider_sockets_closed": active_count == 0,
            "handlers_stopped": len(alive) == 0,
            "owned_subject_stopped": subjects == 0,
            "owned_tools_stopped": tools == 0,
            "active_connections": active_count,
            "residual_writers": len(alive),
        }
        model.validate_quiesce_record(record)
        return record

    def snapshot_record(self) -> dict:
        seeded = self._seeded_originals_sha
        originals_bytes, sha, originals = originals_identity(self.originals_dir)
        if seeded is None or sha != seeded:
            raise ControllerError("originals-mutated")
        # the VERIFIED bytes are what the export frame carries: no
        # second read of the oracle after the identity check
        self._verified_originals = originals
        calls = []
        for entry in self.registry.entries():
            calls.append(
                {
                    "family": entry["family"],
                    "name": entry["name"],
                    "call_id": entry["call_id"],
                    "position": entry["request_position"],
                    "arguments_sha256": entry["arguments_sha256"],
                }
            )
        # The controller's OWN ledger totals at export time (trusted
        # observation the host reconciles against the client-side
        # measurements): requests = every POST /v1/responses plus
        # every exporter command (quiesce/export, admitted or
        # refused); output_bytes = wire response bytes accounted
        # before emission.  Read under the global lock: the export
        # command's own record_request already counted.
        with self.ledger_lock:
            controller_ledger = {
                "requests": self.ledger.requests,
                "output_bytes": self.ledger.output_bytes,
            }
        record = {
            "record": model.SCHEMA_SNAPSHOT,
            "synthetic": True,
            "issued_calls": calls,
            "originals_bytes": originals_bytes,
            "originals_sha256": sha,
            "exporter_uid": self.exporter_uid,
            "exported_before_teardown": True,
            "controller_ledger": controller_ledger,
        }
        model.validate_snapshot_record(record)
        return record


# -- bounded process scans (fail closed on degraded evidence) --------------------
def count_uid_processes(uid: int) -> int:
    count = 0
    try:
        entries = [e for e in os.listdir("/proc") if e.isdigit()]
    except OSError:
        return -1  # degraded: never a silent zero
    for entry in entries[:20000]:
        try:
            with open(f"/proc/{entry}/status", encoding="ascii") as handle:
                uid_line = next((line for line in handle if line.startswith("Uid:")), None)
        except FileNotFoundError:
            continue  # expected churn
        except (OSError, StopIteration):
            return -1  # degraded scan
        if uid_line is not None and int(uid_line.split()[1]) == uid:
            count += 1
    return count


def count_controller_tools(peer_pid: int | None) -> int:
    """Leftover tool/subject processes: pids whose parent is this
    controller, excluding the controller itself and the trusted
    exporter peer (the live 21001 helper on the protected channel)."""
    allowed = {os.getpid()}
    if peer_pid is not None and peer_pid > 0:
        allowed.add(peer_pid)
    count = 0
    try:
        entries = [e for e in os.listdir("/proc") if e.isdigit()]
    except OSError:
        return -1
    for entry in entries[:20000]:
        pid = int(entry)
        if pid in allowed:
            continue
        try:
            with open(f"/proc/{entry}/status", encoding="ascii") as handle:
                status = {
                    line.split(":", 1)[0]: line.split(":", 1)[1].strip()
                    for line in handle
                    if ":" in line
                }
        except FileNotFoundError:
            continue
        except (OSError, StopIteration):
            return -1
        if status.get("PPid") == str(os.getpid()):
            count += 1
    return count


# -- exporter (peer-verified, ordered states) -------------------------------------
def peer_trusted(cred_bytes: bytes, expected_uid: int) -> bool:
    """Exact 12-byte struct ucred (pid, uid, gid — three native
    signed ints).  Malformed credentials fail closed.  The expected
    uid is the exporter's trusted-uid seam: production default
    CONTROLLER_UID; pure local tests inject the local uid."""
    if len(cred_bytes) != 12:
        return False
    try:
        pid, uid, gid = struct.unpack("iii", cred_bytes)
    except struct.error:
        return False
    return pid > 0 and uid == expected_uid and gid == expected_uid


class Exporter:
    """Protected export channel: 0700 dir, 0600 socket, SO_PEERCRED
    peer verification (expected uid injectable for pure local tests;
    production default CONTROLLER_UID), ordered running -> quiesced
    -> exported states, one immutable snapshot, bounded framing,
    cumulative deadline."""

    def __init__(
        self,
        provider: Provider,
        ledger: model.FixtureLedger,
        ledger_lock: threading.Lock,
        mode: str,
        socket_path: str = CTL_EXPORTER_SOCKET,
        trusted_uid: int = CONTROLLER_UID,
    ):
        self.provider = provider
        self.ledger = ledger
        self.ledger_lock = ledger_lock
        self.mode = mode
        self.trusted_uid = trusted_uid
        if os.path.lexists(socket_path):
            # A leftover bound socket is expected between test runs;
            # anything that is not a plain unix socket file is
            # untrusted.
            if os.path.islink(socket_path) or not stat_mod.S_ISSOCK(os.lstat(socket_path).st_mode):
                raise ControllerError("exporter-path-untrusted")
            os.unlink(socket_path)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(socket_path)
        os.chmod(socket_path, 0o600)
        self.server.listen(1)
        self.state = "running"
        self._quiesce_record: dict | None = None
        self._payload: bytes | None = None

    def _peer_pid(self, conn: socket.socket) -> int | None:
        try:
            cred = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        except OSError:
            return None
        if not peer_trusted(cred, self.trusted_uid):
            return None
        return struct.unpack("iii", cred)[0]

    def _build_payload(self) -> bytes:
        if self.provider._seeded_originals_sha is None:
            raise ControllerError("originals-unseeded")
        snapshot = self.provider.snapshot_record()
        diagnostic = self.provider.diagnostic
        if diagnostic is None:
            diagnostic_marker: dict = {"state": "unobserved"}
        else:
            diagnostic_marker = diagnostic
        originals = self.provider._verified_originals
        if originals is None:
            raise ControllerError("originals-unverified")
        selected = {
            "quiesce": self._quiesce_record,
            "snapshot": snapshot,
            "diagnostic": diagnostic_marker,
            "observed_at_position": self.provider.observed_at_position,
            "originals": [base64.b64encode(o).decode("ascii") for o in originals],
            "originals_count": ORIGINALS_COUNT,
        }
        payload = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
        if len(payload) > MAX_EXPORT_BYTES:
            raise ControllerError("export-overbound")
        return payload

    def serve_forever(self) -> None:
        while True:
            try:
                self.server.settimeout(READ_TIMEOUT_SECONDS)
                conn, _ = self.server.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            peer_pid = self._peer_pid(conn)
            if peer_pid is None:
                try:
                    conn.close()
                except OSError:
                    pass
                continue
            try:
                command = self._read_command(conn)
                if command is None:
                    conn.close()
                    continue
                with self.ledger_lock:
                    self.ledger.record_request()
                    self.ledger.require_within_deadline()
                if command == "quiesce":
                    if self.state != "running":
                        conn.sendall(b"error quiesce-not-running\n")
                        conn.close()
                        continue
                    if self.mode == "quiesce-fail":
                        # Declared failure path: the provider refuses
                        # to close; no closed quiesce record is ever
                        # produced and the state never advances.
                        conn.sendall(b"error quiesce-fail\n")
                        conn.close()
                        continue
                    record = self.provider.quiesce(peer_pid)
                    self._quiesce_record = record
                    self.state = "quiesced"
                    conn.sendall(
                        b"quiesce-ok " + json.dumps(record, sort_keys=True).encode() + b"\n"
                    )
                    conn.close()
                elif command == "export":
                    if self.state == "exported":
                        conn.sendall(b"error export-repeated\n")
                        conn.close()
                        continue
                    if self.state != "quiesced" or self._quiesce_record is None:
                        conn.sendall(b"error export-before-quiesce\n")
                        conn.close()
                        continue
                    payload = self._build_payload()
                    digest = hashlib.sha256(payload).hexdigest()
                    frame = struct.pack(">I", len(payload)) + payload + digest.encode()
                    if len(frame) > MAX_EXPORT_BYTES + 128:
                        raise ControllerError("export-overbound")
                    # Account the exact complete frame BEFORE send,
                    # on both the success and declared-failure paths.
                    with self.ledger_lock:
                        self.ledger.record_output(len(frame))
                    self._payload = frame
                    self.state = "exported"
                    if self.mode == "export-fail":
                        # Declared failure path: bounded prefix, then a
                        # corruption byte; the host's digest/schema
                        # validation must fail closed.
                        cut = max(1, len(frame) // 2)
                        conn.sendall(frame[:cut] + b"\xff")
                    else:
                        conn.sendall(frame)
                    conn.close()
                else:
                    conn.close()
            except (ControllerError, OSError, ValueError):
                try:
                    conn.close()
                except OSError:
                    pass

    def _read_command(self, conn: socket.socket) -> str | None:
        conn.settimeout(READ_TIMEOUT_SECONDS)
        data = b""
        while b"\n" not in data:
            chunk = conn.recv(1)
            if not chunk:
                return None
            data += chunk
            if len(data) > COMMAND_CAP_BYTES:
                return None
        command = data.strip().decode("ascii", "replace")
        if command not in ("quiesce", "export"):
            return None
        return command


def main() -> int:
    if os.getuid() != CONTROLLER_UID:
        log_closed(
            {"record": "slaif-fixture-controller-v1", "status": "fail", "reason": "uid-not-21001"}
        )
        return 2
    mode = os.environ.get("SLAIF_FIXTURE_MODE", "main")
    if mode not in ("main", "export-fail", "quiesce-fail", "crash"):
        log_closed(
            {"record": "slaif-fixture-controller-v1", "status": "fail", "reason": "mode-invalid"}
        )
        return 2
    scenario = os.environ.get("SLAIF_FIXTURE_SCENARIO", "diagnostic")
    if scenario not in ("diagnostic", "tool-cycle"):
        log_closed(
            {
                "record": "slaif-fixture-controller-v1",
                "status": "fail",
                "reason": "scenario-invalid",
            }
        )
        return 2
    try:
        prepare_root()
        port = env_int("SLAIF_FIXTURE_PORT", 18443)
        deadline = env_int("SLAIF_FIXTURE_DEADLINE", 1800)
        ledger = model.FixtureLedger()
        ledger.set_deadline(min(deadline, ledger.budgets.lifetime_seconds))
        ledger_lock = threading.Lock()
        registry = model.IssuedRegistry(ledger.budgets.max_requests)
        provider = Provider(port, ledger, registry, ledger_lock, scenario=scenario)
        exporter = Exporter(provider, ledger, ledger_lock, mode)
        # Seed the fixed originals BEFORE ownership verification.
        provider.seed_originals()
        # Seed the registry file BEFORE ownership verification.
        with open(CTL_ISSUED_REGISTRY, "w", encoding="ascii") as handle:
            json.dump({"synthetic": True, "count": registry.count()}, handle, sort_keys=True)
        os.chmod(CTL_ISSUED_REGISTRY, 0o600)
        verify_controller_owned()
    except (ControllerError, model.FixtureError, OSError) as exc:
        reason = getattr(exc, "args", ("controller-failure",))[0]
        log_closed(
            {
                "record": "slaif-fixture-controller-v1",
                "status": "fail",
                "reason": reason if isinstance(reason, str) else "controller-failure",
            }
        )
        return 1
    accept_thread = threading.Thread(target=provider.serve, daemon=True)
    provider.accept_thread = accept_thread
    exporter_thread = threading.Thread(target=exporter.serve_forever, daemon=True)
    for thread in (accept_thread, exporter_thread):
        thread.start()
    log_closed(
        {
            "record": "slaif-fixture-controller-v1",
            "status": "ready",
            "provider_port": provider.port,
            "pid1": os.getpid() == 1,
        }
    )
    if mode == "crash":
        # Declared failure path: readiness measured, then termination.
        time.sleep(2.0)
        os._exit(137)
    try:
        while True:
            with ledger_lock:
                ledger.require_within_deadline()
            if not accept_thread.is_alive() and mode != "main":
                break
            time.sleep(0.25)
    except model.BudgetExceeded:
        log_closed(
            {
                "record": "slaif-fixture-controller-v1",
                "status": "fail",
                "reason": "self-deadline-expired",
            }
        )
        return 124
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
