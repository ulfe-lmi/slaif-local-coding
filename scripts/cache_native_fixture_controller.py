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
import errno
import hashlib
import hmac
import json
import math
import os
import re
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

# -- owner-UID quiesce accounting (017-aa) ----------------------------------
# The quiesce subject is resolved from the SAME fixed in-image
# identity facts the stand-in's closed resolution uses (the image
# layout is the closed contract): the image-owned identity-mode
# constant file (parsed, never executed) selects the mode, and the
# baked closed profile DATA record (decoded with the production
# codec, never imported) carries the frozen subject UID.  The
# original image never bakes the marker: an ABSENT marker (or the
# explicit original value) keeps the historical fixed-21002 quiesce
# subject law byte-for-byte, ignoring any file at the DATA path
# (a file's presence never selects the mode).  The explicit owner
# marker REQUIRES the bounded immutable DATA: missing / unknown /
# mismatched / unsafe marker or DATA fails the quiesce closed (a
# fixed refusal, a degraded scan) — never a silent zero and NEVER
# a fallback to the original subject.
IDENTITY_PROFILE_FILE = "/opt/slaif-fixture/identity_profile.py"
IDENTITY_PROFILE_FILE_MAX_BYTES = 128
PROFILE_DATA_PATH = "/opt/slaif-fixture/fixture-identity.json"
_QUIESCE_MODE_RE = re.compile(rb'SLAIF_FIXTURE_IDENTITY_PROFILE = "([a-z0-9-]+)"\n')
_QUIESCE_OWNER_PROFILE = "slaif-fixture-identity-owner-uid-v1"
_QUIESCE_ORIGINAL_PROFILE = "slaif-fixture-identity-original-v1"

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
ROUTE_STATE = "/state"
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


def format_clamped_deadline_anchor(relative_seconds: int) -> float:
    """The format scenario's ledger deadline ANCHOR: the SAME
    original owner absolute END transported by the existing
    trusted config channel (``SLAIF_FIXTURE_DEADLINE_ABS``, set
    by the owner's prepare-target as the repr of its monotonic
    END anchor), intersected with the controller's own relative
    bound at ONE clock reading — never a fresh
    controller-relative window at controller startup, and never
    a relative remainder re-anchored at a LATER clock reading
    (that would extend the original owner END by the elapsed
    setup time).  The returned absolute monotonic anchor is
    stored as the ledger deadline itself.  A missing, malformed
    or already-past anchor is a closed refusal.  Every other
    scenario keeps its historical relative meaning unchanged
    (this helper is used only for the format scenario)."""
    raw = os.environ.get("SLAIF_FIXTURE_DEADLINE_ABS")
    if raw is None:
        raise ControllerError("format-deadline-unbound")
    try:
        anchor = float(raw)
    except ValueError:
        raise ControllerError("format-deadline-unbound") from None
    if not math.isfinite(anchor) or anchor <= 0:
        raise ControllerError("format-deadline-unbound")
    now = time.monotonic()
    if anchor - now <= 0:
        raise ControllerError("format-deadline-expired")
    return min(anchor, now + float(relative_seconds))


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
) -> tuple[str, str, bytes, str | None]:
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
        return method, path, b"", headers.get("authorization")
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
    return method, path, body, headers.get("authorization")


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
        auth_token: str | None = None,
    ):
        if scenario not in ("diagnostic", "tool-cycle", "format-capture"):
            raise ControllerError("scenario-invalid")
        self.scenario = scenario
        self.originals_dir = originals_dir
        # Closed local (017-s) synthetic auth binding: when a 32-hex
        # token is bound, EVERY POST on /v1/responses must carry
        # exactly ``Bearer <synthetic_credential(token)>`` where the
        # credential uses the same closed derivation as the subject's
        # synthetic credential file.  Hosted CI never binds a token:
        # with ``auth_expected`` None the path is unchanged and the
        # Authorization header (if any) is discarded, never logged,
        # never exported, never reflected.  A present-but-malformed
        # token fails closed at construction.
        if auth_token is None:
            self.auth_expected: str | None = None
        else:
            if not isinstance(auth_token, str) or not re.fullmatch(r"[0-9a-f]{32}", auth_token):
                raise ControllerError("auth-token-invalid")
            self.auth_expected = (
                "slaif-synthetic-" + hashlib.sha256(auth_token.encode("ascii")).hexdigest()[:32]
            )
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
        # Closed serial format-capture scenario state (017-ai):
        # awaiting-first-post -> awaiting-result (one outstanding
        # issued call at a time) -> done.  Every transition is
        # fenced under the scenario lock with the locally
        # allocated immutable causal position; the retained
        # issued entries keep the EXACT closed argument shapes
        # (typed), the per-case results keep the EXACT received
        # wrapper text, and nothing is re-issued or re-
        # retained.  A format request body can never select,
        # switch or advance this state.
        self._fmt_state = "awaiting-first-post"
        self._fmt_case_index = 0
        self._fmt_outstanding: dict | None = None
        self._fmt_session: int | None = None
        self._fmt_polls = 0
        # the finite model-POST counter: EVERY POST that reaches
        # the semantic step counts, accepted or refused
        self._fmt_posts = 0
        self._fmt_cum = 0
        self._fmt_cases: list[dict] = []
        self._fmt_issued: list[dict] = []
        self._fmt_retained_results: list[tuple[str, str]] = []

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

    # -- format seeds (published BEFORE any service start) ------------
    def seed_format_seeds(self) -> None:
        """Publish the IMMUTABLE pre-launch seed set into the
        subject-readable mirror seam (``model.FORMAT_SEED_DIR``)
        BEFORE any service start: the copies are byte-identical
        to the code-defined originals, and the published set is
        sealed read-only (mode-0555 directory, mode-0444 files).
        The seam is created as a restrictive OWNED writable
        directory, fully written and bounded-verified, and only
        THEN sealed — the controller is a nonroot UID under
        cap-drop-ALL, so it can never write into a 0555 root:
        the seal comes last, never first.  The seam law is
        REJECT-ALL-PREEXISTING: the seam is published once per
        fresh scenario container and no legitimate caller ever
        reseeds an existing root, so ANY pre-existing root at
        this call — even a correctly sealed one — is untrusted
        and is never adopted, completed, rewritten or read; a
        partial or foreign seam is refused exactly the same
        way.  The fresh root is opened O_NOFOLLOW directly
        after mkdir and fstat'd from its own descriptor
        (directory, owned by this controller, mode 0700)
        before any file is created, so a swapped name is
        refused, never followed.  Every published file is then
        bounded-re-verified through the SAME held directory fd
        (O_NOFOLLOW | O_NONBLOCK opens; a planted FIFO or
        symlink is refused by the fstat regularity law without
        blocking) and only THEN sealed.  The snapshot's seed
        identity comes from the code-defined pre-launch bytes,
        never from these child-readable copies."""
        root = model.FORMAT_SEED_DIR
        me = os.getuid()
        my_gid = os.getgid()
        if os.path.lexists(root):
            # reject-all-preexisting: never adopted, completed,
            # rewritten or read
            raise ControllerError("format-seed-untrusted")
        try:
            os.mkdir(root, 0o700)
        except FileExistsError:
            # a raced creator is refused, never adopted
            raise ControllerError("format-seed-untrusted") from None
        try:
            root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError:
            raise ControllerError("format-seed-untrusted") from None
        try:
            ost = os.fstat(root_fd)
            if (
                not stat_mod.S_ISDIR(ost.st_mode)
                or ost.st_uid != me
                or ost.st_gid != my_gid
                or stat_mod.S_IMODE(ost.st_mode) != 0o700
            ):
                raise ControllerError("format-seed-untrusted")
            for name, data in model.FORMAT_SEED_FILES:
                try:
                    fd = os.open(
                        name,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=root_fd,
                    )
                except FileExistsError:
                    # a root we just created cannot contain
                    # pre-existing entries: any hit is untrusted
                    raise ControllerError("format-seed-untrusted") from None
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
            # bounded complete verification THROUGH THE SAME
            # HELD directory fd (no re-resolution, no symlink
            # follow), then the read-only seal through the fd
            # (files first, root last — the subject sees only
            # the sealed set)
            self._format_verify_sealed_set(root_fd, want_file_mode=0o600)
            for name, _data in model.FORMAT_SEED_FILES:
                fd = os.open(
                    name,
                    os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                    dir_fd=root_fd,
                )
                try:
                    os.fchmod(fd, model.FORMAT_SEED_FILE_MODE)
                finally:
                    os.close(fd)
            os.fchmod(root_fd, model.FORMAT_SEED_DIR_MODE)
        finally:
            os.close(root_fd)

    def _format_verify_sealed_set(self, root_fd: int, want_file_mode: int = 0o444) -> None:
        """Bounded re-verification of the complete published set
        THROUGH THE HELD root directory fd: every seed file is
        opened O_NOFOLLOW | O_NONBLOCK relative to that fd
        — the OPENED OBJECT is the check target (a swapped or
        planted symlink is refused, never followed, and a
        planted FIFO is refused by the fstat regularity law
        without blocking) — and fstat'd from its own
        descriptor: a regular file owned by this controller,
        at the exact expected mode, and byte-identical to the
        immutable code-defined original (bounded full read
        capped at the expected length plus one; a missing,
        overlong, linked or non-regular entry is a closed
        refusal, never an adopted or completed seam).  The
        complete-set law (no extra entries are ever adopted)
        lives in the reject-all-preexisting public entry,
        which never reuses a pre-existing root.  The resolved
        root is never re-opened by path."""
        me = os.getuid()
        my_gid = os.getgid()
        for name, data in model.FORMAT_SEED_FILES:
            try:
                fd = os.open(
                    name,
                    os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                    dir_fd=root_fd,
                )
            except OSError:
                raise ControllerError("format-seed-untrusted") from None
            try:
                st = os.fstat(fd)
                if (
                    not stat_mod.S_ISREG(st.st_mode)
                    or st.st_uid != me
                    or st.st_gid != my_gid
                    or stat_mod.S_IMODE(st.st_mode) != want_file_mode
                ):
                    raise ControllerError("format-seed-untrusted")
                if st.st_size != len(data):
                    raise ControllerError("format-seed-copy-mismatch")
                if self._format_read_bounded(fd, len(data) + 1) != data:
                    raise ControllerError("format-seed-copy-mismatch")
            finally:
                os.close(fd)

    @staticmethod
    def _format_read_bounded(fd: int, limit: int) -> bytes:
        """Read up to ``limit`` bytes from an already-opened
        descriptor; the result is shorter only at EOF (a single
        os.read is never relied on for a full regular-file
        read)."""
        parts: list[bytes] = []
        total = 0
        while total < limit:
            piece = os.read(fd, limit - total)
            if not piece:
                break
            total += len(piece)
            parts.append(piece)
        return b"".join(parts)

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
            method, path, body, auth = self._read_with_deadline(conn)
            position: int | None = None
            if method == "POST" and path == ROUTE_RESPONSES:
                # Allocate the immutable causal request position
                # LOCALLY under the global lock before any semantic
                # step; later reads of the shared counter are never
                # used as causal identity.
                with self.ledger_lock:
                    position = self.ledger.record_request() - 1
            status, content_type, payload = self._route(method, path, body, position, auth)
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

    def _state_body(self) -> bytes:
        """Closed NON-CONSUMING status record (local 017-s observe):
        the declared scenario, the controller's OWN cumulative
        request count and the one-shot diagnostic state.  This
        command is NOT a model POST: it allocates no causal
        position, consumes nothing, advances no scenario or
        exporter state, and charges no provider request budget."""
        with self.ledger_lock:
            requests = self.ledger.requests
        record = {
            "record": "slaif-fixture-state-v1",
            "scenario": self.scenario,
            "wire_requests": requests,
            "diagnostic": "unobserved" if self.diagnostic is None else "observed",
        }
        return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii")

    # -- routing (real wire shape) ------------------------------------------
    def _route(
        self,
        method: str,
        path: str,
        body: bytes,
        position: int | None,
        auth: str | None = None,
    ) -> tuple[str, str, bytes]:
        if method == "GET" and path == ROUTE_HEALTH:
            return "200 OK", "application/json", HEALTH_BODY
        if method == "GET" and path == ROUTE_STATE:
            return "200 OK", "application/json", self._state_body()
        if method != "POST" or path != ROUTE_RESPONSES or position is None:
            return self._error("route")
        # The finite model-POST bound is fenced at the route:
        # EVERY model POST to the fixture route counts —
        # accepted or refused (an auth/JSON refusal below is a
        # consumed POST, never free) — BEFORE any auth, JSON or
        # semantic gate, and distinct from the cumulative
        # controller/export request ledger.
        if self.scenario == "format-capture":
            with self.scenario_lock:
                self._fmt_posts += 1
                post_bound = self._fmt_posts > model.FORMAT_MAX_POSTS
            if post_bound:
                return self._error("format-post-bound")
        # Closed local synthetic auth binding (017-s): checked BEFORE
        # any semantic step, so a refused authorization can never
        # observe or advance the scenario.  The comparison is a
        # constant-time compare of the exact expected header value;
        # the raw header is never logged, exported or reflected.
        if self.auth_expected is not None:
            if not isinstance(auth, str):
                return self._auth_refused()
            expected = "Bearer " + self.auth_expected
            if not hmac.compare_digest(auth.encode("ascii", "replace"), expected.encode("ascii")):
                return self._auth_refused()
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
            if self.scenario == "format-capture":
                return self._format_step(payload, position)
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

    # -- closed serial format-capture scenario (017-ai) -----------------
    def _format_step(self, payload: dict, position: int) -> tuple[str, str, bytes]:
        """The closed serial ONE-outstanding format-capture step
        (host-selected; a request body can never select, switch
        or advance it):

        - the FIRST admitted POST carries NO tool history at
          all (preloaded results or echoed calls are refused);
          the controller issues the first case's exec call.
        - every later POST carries the COMPLETE accumulated
          history: every retained issued call (echoed with the
          TYPED-exact closed arguments) plus every retained
          result (byte-identical wrapper), plus the ONE
          outstanding result.  The outstanding result is
          verified against the closed per-case law of the
          immutable pre-launch seed; a deviation is a closed
          refusal, never a partial pass.
        - after each accepted result the controller issues the
          next closed call at THIS POST's position (the next
          case's exec in the closed case order, or the next
          bounded empty-stdin poll of the ONE running
          process): the same POST that validated the prior
          result issues the next call at that very position
          (equality of the result and issue positions is
          legal).
        - once all four cases complete, the scenario is done
          and the fixed final message answers; anything after
          the terminal state is scenario-bounded.

        Every LATER post is a small bounded proposal/transition:
        the verified frame, the proposed continuation and the
        applicable NEXT actual offered tool shape plus the
        original owner END at this return are all verified
        BEFORE any semantic commit (result retention, stream
        session/offset, case finalization, registry advance).
        A refusal at any staged point adopts no state: the
        retained history stays frozen and the outstanding call
        stays outstanding, never stranded.  No potentially
        refusing check runs AFTER the semantic commit: the
        continuation's offered shape and the original END are
        both verified at this POST's pre-commit return, and the
        post-commit issuance performs no fallible re-check, so
        an expiry crossing the commit point can neither strand
        the adopted result nor mint a call after a refusal.
        The consumed model-POST count is fenced at the route
        (every POST to the fixture route counts, accepted or
        refused), distinct from the cumulative controller/export
        request ledger.
        """
        if not isinstance(position, int) or isinstance(position, bool) or position < 0:
            return self._error("causal-position")
        if self._fmt_state == "done":
            return self._error("scenario-bounded")
        if self._fmt_state == "awaiting-first-post":
            if _has_preloaded_outputs(payload):
                return self._error("preloaded-result")
            input_items = payload.get("input")
            if isinstance(input_items, list) and any(
                isinstance(item, dict) and item.get("type") == "function_call"
                for item in input_items
            ):
                return self._error("format-history")
            return self._format_issue_exec(0, position, payload.get("tools"))
        if self._fmt_outstanding is None:
            return self._error("format-chain-deviation")
        # the outstanding result must arrive on a request
        # STRICTLY AFTER its own issuance, gated BEFORE any
        # result state mutation (the legitimate
        # result_position == NEXT issue_position of the same
        # POST is checked at issuance, never here)
        if position <= self._fmt_outstanding["issue_position"]:
            return self._error("causal-order")
        history = self._format_verify_history(payload)
        if history is None:
            return self._error("format-history")
        wrapper_text, outstanding = history
        (
            error,
            continuation,
            stream_proposal,
            trunc_tokens,
        ) = self._format_verify_case_result(wrapper_text, outstanding)
        if error is not None:
            return self._error(error)
        # STAGE the continuation BEFORE any semantic commit: the
        # applicable NEXT actual offered tool shape is verified
        # ONCE here (the closed in-memory capability decision
        # against THIS POST's tools region), the next call's
        # finite budgets are checked, and the SMALL prepared
        # transition (the closed tool name, the closed call id,
        # the TYPED closed arguments, the causal position and
        # the phase) is built — all while the shared state is
        # still unchanged.  A staged refusal adopts no
        # result/session/offset, advances no case and issues no
        # call: the outstanding call stays outstanding for a
        # later valid POST, never stranded.
        next_case_index = (
            self._fmt_case_index + 1
            if continuation == "next-case" and self._fmt_case_index < len(model.FORMAT_CASES) - 1
            else None
        )
        stage_error, prepared = self._format_stage_next(
            continuation,
            stream_proposal,
            next_case_index,
            payload.get("tools"),
            position,
        )
        if stage_error is not None:
            return self._error(stage_error)
        # the final END commit fence: the original owner END at
        # THIS return.  An expired anchor cannot adopt the
        # verified frame or issue the prepared call (state
        # equality on that refusal).  Every potentially
        # refusing check — frame verification, the applicable
        # offered shape, the finite budgets and this fence —
        # has now completed ONCE, before any semantic adoption.
        try:
            with self.ledger_lock:
                self.ledger.require_within_deadline()
        except model.BudgetExceeded:
            return self._error("scenario-deadline-expired")
        # COMMIT the prepared transition: retain the result
        # EXACTLY ONCE (the frozen fingerprint is never
        # re-advanced or re-retained), apply the stream
        # session/offset and the recovered truncation budget,
        # then bind the prepared call — no offered-schema work
        # and no further deadline read run after the adoption.
        self._format_retain_result(wrapper_text, position, outstanding)
        if stream_proposal is not None:
            session, cum = stream_proposal
            self._fmt_session = session
            self._fmt_cum = cum
            self._fmt_cases[self._fmt_case_index]["session_id"] = session
        if trunc_tokens is not None:
            self._fmt_cases[self._fmt_case_index]["truncated_effective_tokens"] = trunc_tokens
        if continuation == "poll":
            self._format_commit_issue(prepared)
            return self._format_issue_response(
                prepared["call_id"],
                prepared["name"],
                prepared["arguments"],
                prepared["position"],
            )
        # the case is complete
        self._format_finalize_case()
        if next_case_index is not None:
            self._fmt_case_index = next_case_index
            self._format_commit_issue(prepared)
            return self._format_issue_response(
                prepared["call_id"],
                prepared["name"],
                prepared["arguments"],
                prepared["position"],
            )
        self._fmt_state = "done"
        return (
            "200 OK",
            "text/event-stream",
            self._sse(
                response_id="resp_slaif_final",
                items=[_final_message()],
            ),
        )

    def _format_register_issue(
        self, name: str, call_id: str, arguments: dict, position: int
    ) -> dict | None:
        """Issue ONE closed call at the POST position: the
        registry binding (family/name/call id/typed argument
        digest/causal position) plus the controller's OWN
        retained entry with the EXACT argument shape (the
        registry's closed export omits the arguments; the
        snapshot law requires them).  A budget or identity
        refusal is a fixed closed failure."""
        digest = model.sha256_bytes(model.canonical_bytes(arguments))
        try:
            self.registry.issue("function", name, call_id, digest, position)
        except model.FixtureError:
            return None
        self._fmt_issued.append(
            {
                "family": "function",
                "name": name,
                "call_id": call_id,
                "position": position,
                "arguments_sha256": digest,
                "arguments": arguments,
            }
        )
        return {"call_id": call_id, "issue_position": position}

    def _format_new_case_record(
        self, spec: dict, call_id: str, position: int, arguments: dict
    ) -> dict:
        # HONEST internal facts at issuance: the case is PENDING
        # with NO result retained — completion/exit/verified are
        # committed by _format_finalize_case ONLY after the full
        # verified chain (a partial state never presents
        # placeholders as observed facts, and is never exported:
        # format_snapshot_record refuses a non-done scenario)
        return {
            "case": spec["case"],
            "kind": spec["kind"],
            "seed_files": list(spec["seed_files"]),
            "command": spec["command"],
            "call_id": call_id,
            "call_position": position,
            "arguments_sha256": model.sha256_bytes(model.canonical_bytes(arguments)),
            "status": "pending",
            "exit": None,
            "session_id": None,
            "results": [],
            "output_bytes": 0,
            "output_sha256": model.sha256_bytes(b""),
            "nonempty_pieces": 0,
            "polls": 0,
            "truncated": False,
            "truncated_effective_tokens": None,
            "crlf": False,
            "non_ascii": False,
            "verified": False,
        }

    def _format_issue_response(
        self, call_id: str, name: str, arguments: dict, position: int
    ) -> tuple[str, str, bytes]:
        item = {
            "type": "function_call",
            "id": f"msg_slaif_fmt_{position}",
            "call_id": call_id,
            "name": name,
            "arguments": json.dumps(arguments, sort_keys=True, separators=(",", ":")),
        }
        return (
            "200 OK",
            "text/event-stream",
            self._sse(response_id=f"resp_slaif_fmt_{position}", items=[item]),
        )

    def _format_issue_exec(
        self, case_index: int, position: int, tools: object
    ) -> tuple[str, str, bytes]:
        spec = model.FORMAT_CASES[case_index]
        if len(self._fmt_issued) >= model.FORMAT_MAX_ISSUED:
            return self._error("format-issue-bound")
        expected = model.format_expected_exec_arguments(spec)
        # the closed tool must be OFFERED in this POST's tools
        # region in the exact closed shape BEFORE any issuance
        # or state adoption (bounded in-memory capability
        # decision; the raw schema is never retained)
        if not model.format_offered_tool_available(tools, model.FORMAT_EXEC_TOOL, expected):
            return self._error("format-tools-unoffered")
        # the SAME original owner END at THIS return: an expired
        # anchor cannot issue the call — checked AFTER the
        # bounded offer verification and BEFORE any
        # registry/state commit: this refusal adopts no call,
        # no outstanding and no case record, and never extends
        # the END or uses the cleanup grace.  (The continuation
        # issuances never take this path: their offer
        # verification and the END fence complete ONCE, before
        # the semantic commit, in _format_stage_next and the
        # step's final END commit fence.)
        try:
            with self.ledger_lock:
                self.ledger.require_within_deadline()
        except model.BudgetExceeded:
            return self._error("scenario-deadline-expired")
        call_id = f"slaif-fmt-{case_index}-{position}"
        registered = self._format_register_issue(
            model.FORMAT_EXEC_TOOL, call_id, expected, position
        )
        if registered is None:
            return self._error("issue-rejected")
        self._fmt_outstanding = {**registered, "phase": "exec"}
        self._fmt_state = "awaiting-result"
        self._fmt_cases.append(self._format_new_case_record(spec, call_id, position, expected))
        return self._format_issue_response(call_id, model.FORMAT_EXEC_TOOL, expected, position)

    def _format_verify_history(self, payload: dict) -> tuple[str, dict] | None:
        """The closed accumulated-history law (the receiver
        NEVER coerces): the POST's input must carry EXACTLY the
        retained issued calls — each echoed once, under its own
        family/name, with the TYPED-exact closed arguments
        (a same-ID changed argument, a bool/float standing in
        for a required integer, a duplicated or foreign ID, or
        a malformed argument object is a refusal) and the
        digest binding to the canonical bytes of the TYPED
        EXPECTED shape — plus EXACTLY the retained results
        (byte-identical wrappers; the frozen fingerprints are
        never re-advanced or re-retained) and the ONE
        outstanding result.  The item ORDER within the request
        carries no execution meaning (set-level law).  Returns
        (the outstanding wrapper text, the outstanding
        descriptor) or None (a fixed refusal)."""
        input_items = payload.get("input")
        if not isinstance(input_items, list):
            return None
        call_items = [
            item
            for item in input_items
            if isinstance(item, dict) and item.get("type") == "function_call"
        ]
        result_items = [
            item
            for item in input_items
            if isinstance(item, dict) and item.get("type") == "function_call_output"
        ]
        expected_calls = self._fmt_issued
        if len(call_items) != len(expected_calls):
            return None
        for call in expected_calls:
            matches = [item for item in call_items if item.get("call_id") == call["call_id"]]
            if len(matches) != 1:
                return None
            item = matches[0]
            if item.get("name") != call["name"]:
                return None
            raw_args = item.get("arguments")
            if not isinstance(raw_args, str):
                return None
            try:
                decoded = json.loads(
                    raw_args, object_pairs_hook=model._format_reject_duplicate_keys
                )
            except ValueError:
                return None
            if not model.format_arguments_exact(decoded, call["arguments"]):
                return None
            if model.sha256_bytes(model.canonical_bytes(decoded)) != call["arguments_sha256"]:
                return None
        expected_result_ids = [cid for cid, _w in self._fmt_retained_results]
        expected_result_ids = expected_result_ids + [self._fmt_outstanding["call_id"]]
        if len(result_items) != len(expected_result_ids):
            return None
        result_map: dict[str, list[str]] = {}
        for item in result_items:
            cid = item.get("call_id")
            output = item.get("output")
            if not isinstance(cid, str) or not isinstance(output, str):
                return None
            result_map.setdefault(cid, []).append(output)
        if len(result_map) != len(expected_result_ids):
            return None
        for cid in expected_result_ids:
            if len(result_map.get(cid, [])) != 1:
                return None
        for cid, wrapper in self._fmt_retained_results:
            if result_map[cid][0] != wrapper:
                return None
        return result_map[self._fmt_outstanding["call_id"]][0], self._fmt_outstanding

    def _format_verify_case_result(
        self, wrapper_text: str, outstanding: dict
    ) -> tuple[str | None, str | None, tuple[int | None, int] | None, int | None]:
        """The closed per-case law at arrival: the strict
        pinned wrapper parse and per-result transport law
        (grammar, bounds, omission marker), the per-frame
        token-count metadata against the frame's OWN observed
        bytes (the truncated case: against the frame's
        original pre-truncation seed bytes), and the
        kind-specific output law against the immutable
        pre-launch seed (raw-byte law, declared chain,
        unique bounded truncation match, the multi-chunk
        qualification at stream completion).  TENTATIVE: it
        adopts no state.  Returns
        (error_code, continuation, stream_proposal,
        truncation_tokens): on success the error is None, the
        continuation is 'poll' (the ONE running process awaits
        its next bounded empty-stdin poll) or 'next-case' (the
        case is complete), stream_proposal is the (session,
        cumulative-offset) pair for the stream case or None,
        and truncation_tokens is the uniquely recovered
        effective budget of the truncated case or None."""
        case_index = self._fmt_case_index
        spec = model.FORMAT_CASES[case_index]
        case = self._fmt_cases[case_index]
        try:
            facts, data = model.format_frame_output_facts(wrapper_text)
        except model.FixtureError:
            return ("format-frame-deviation", None, None, None)
        count = facts["original_token_count"]
        if count is not None:
            if spec["kind"] == "truncated":
                expected_count = model._approx_token_count_bytes(
                    len(model._format_expected_bytes(spec))
                )
            else:
                expected_count = model._approx_token_count_bytes(len(data))
            if count != expected_count:
                return ("format-frame-deviation", None, None, None)
        if spec["kind"] == "stream":
            return self._format_verify_stream_frame(spec, case, facts, data, outstanding)
        # single-final case: the ONE frame must be completed
        if facts["exit_code"] != 0:
            return ("format-chain-deviation", None, None, None)
        if spec["kind"] == "read":
            if data != model._format_expected_bytes(spec):
                return ("format-seed-mismatch", None, None, None)
        elif spec["kind"] == "empty":
            if data != b"":
                return ("format-seed-mismatch", None, None, None)
        else:
            # the deliberate bounded truncation: the observed
            # output is the PINNED formatter applied to the
            # immutable seed under exactly ONE effective token
            # budget within the offered budget (recovered by
            # unique match, never assumed); the recovered
            # budget is PROPOSED here and committed only by the
            # caller after the continuation is staged
            seed_text = model._format_expected_bytes(spec).decode("utf-8")
            matches = [
                tokens
                for tokens in range(1, model.FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS + 1)
                if model.format_truncate_text(seed_text, tokens).encode("utf-8") == data
            ]
            if len(matches) != 1:
                return ("format-truncation-mismatch", None, None, None)
            return (None, "next-case", None, matches[0])
        return (None, "next-case", None, None)

    def _format_verify_stream_frame(
        self, spec: dict, case: dict, facts: dict, data: bytes, outstanding: dict
    ) -> tuple[str | None, str | None, tuple[int | None, int] | None, None]:
        """The stream case's declared chain
        (initial-running-poll-final): the initial frame MUST be
        a running result carrying the observed positive
        session identity; a poll's running frame carries the
        SAME session, the completion frame (exit 0) may omit
        it (pinned) but a present one must match.  Each
        frame's output is the next unverified SLICE of the
        immutable expected full bytes (the transport's
        delivery grouping is observed, never declared — the
        cumulative offset is the only structure), and at
        completion the cumulative output is complete with at
        least TWO nonempty observed pieces (the multi-chunk
        qualification).  TENTATIVE: every check runs against
        local session/offset values ONLY; the shared state is
        never written here (the caller commits the returned
        (session, cumulative-offset) proposal after the
        continuation is staged and the original END verified
        at return), so a refused frame adopts no poll identity
        and advances no source offset (a later valid handling
        sees uncorrupted state)."""
        session = facts["session_id"]
        running = facts["exit_code"] is None
        if outstanding["phase"] == "exec":
            if not running:
                return ("format-chain-deviation", None, None, None)
            if not isinstance(session, int) or isinstance(session, bool) or session <= 0:
                return ("format-chain-deviation", None, None, None)
            tentative_session: int | None = session
            tentative_cum = 0
        else:
            if running:
                if session != self._fmt_session:
                    return ("format-chain-deviation", None, None, None)
            elif facts["exit_code"] != 0:
                return ("format-chain-deviation", None, None, None)
            elif session is not None and session != self._fmt_session:
                return ("format-chain-deviation", None, None, None)
            tentative_session = self._fmt_session
            tentative_cum = self._fmt_cum
        total = len(model._format_expected_bytes(spec))
        if tentative_cum + len(data) > total:
            return ("format-seed-mismatch", None, None, None)
        expected_slice = model._format_expected_bytes(spec)[
            tentative_cum : tentative_cum + len(data)
        ]
        if data != expected_slice:
            return ("format-seed-mismatch", None, None, None)
        tentative_cum += len(data)
        if running:
            return (None, "poll", (tentative_session, tentative_cum), None)
        if tentative_cum != total:
            return ("format-seed-mismatch", None, None, None)
        nonempty = sum(
            1
            for entry in case["results"]
            if model.parse_native_tool_wrapper(entry["wrapper"])["output"] != ""
        )
        if data:
            nonempty += 1
        if nonempty < 2:
            return ("format-multichunk-deviation", None, None, None)
        return (None, "next-case", (tentative_session, tentative_cum), None)

    def _format_stage_next(
        self,
        continuation: str,
        stream_proposal: tuple[int | None, int] | None,
        next_case_index: int | None,
        tools: object,
        position: int,
    ) -> tuple[str | None, dict | None]:
        """Bounded local staging of the PROPOSED continuation,
        completed ONCE and entirely BEFORE the final END commit
        fence: the applicable NEXT actual offered tool shape is
        verified here (the closed in-memory capability decision
        against THIS POST's tools region), the next call's
        finite budgets are checked, and the SMALL prepared
        transition (closed tool name, closed call id, TYPED
        closed arguments, causal position, phase) is built.
        Adopts no state itself.  Returns (error_code,
        prepared_descriptor): a staged refusal returns its
        closed error with no descriptor, and the terminal
        continuation (all cases complete) returns no
        descriptor.  The commit applies the prepared
        descriptor with no further schema work or deadline
        read."""
        if continuation == "poll":
            if self._fmt_polls >= model.FORMAT_MAX_POLLS:
                return "format-poll-bound", None
            if len(self._fmt_issued) >= model.FORMAT_MAX_ISSUED:
                return "format-issue-bound", None
            session = stream_proposal[0] if stream_proposal is not None else self._fmt_session
            if not isinstance(session, int) or isinstance(session, bool) or session <= 0:
                return "format-chain-deviation", None
            expected = model.format_expected_poll_arguments(session)
            if not model.format_offered_tool_available(tools, model.FORMAT_POLL_TOOL, expected):
                return "format-tools-unoffered", None
            return None, {
                "name": model.FORMAT_POLL_TOOL,
                "call_id": f"slaif-fmt-{self._fmt_case_index}-{position}",
                "arguments": expected,
                "position": position,
                "phase": "poll",
            }
        # continuation == "next-case": the next closed case's
        # exec (when one remains) must be issuable at this
        # POST's position
        if next_case_index is None:
            return None, None
        if len(self._fmt_issued) >= model.FORMAT_MAX_ISSUED:
            return "format-issue-bound", None
        expected = model.format_expected_exec_arguments(model.FORMAT_CASES[next_case_index])
        if not model.format_offered_tool_available(tools, model.FORMAT_EXEC_TOOL, expected):
            return "format-tools-unoffered", None
        return None, {
            "name": model.FORMAT_EXEC_TOOL,
            "call_id": f"slaif-fmt-{next_case_index}-{position}",
            "arguments": expected,
            "position": position,
            "phase": "exec",
            "case_index": next_case_index,
        }

    def _format_commit_issue(self, prepared: dict) -> None:
        """The COMMIT-side binding of the staged prepared
        transition: the registry entry plus the controller's
        OWN retained entry (and, for the exec phase, the next
        case record), applied AFTER the final END commit fence.
        NO offered-schema verification and NO deadline read run
        here — every potentially refusing check completed once
        before the fence, and only the prepared typed closed
        arguments are bound.  The registry's own identity and
        budget laws are data-integrity invariants already
        established by the staged bounds (the finite issue
        bound, the strictly monotonic position, the unique
        closed call id) and cannot newly refuse."""
        digest = model.sha256_bytes(model.canonical_bytes(prepared["arguments"]))
        try:
            self.registry.issue(
                "function",
                prepared["name"],
                prepared["call_id"],
                digest,
                prepared["position"],
            )
        except model.FixtureError:
            raise ControllerError("issue-rejected") from None
        self._fmt_issued.append(
            {
                "family": "function",
                "name": prepared["name"],
                "call_id": prepared["call_id"],
                "position": prepared["position"],
                "arguments_sha256": digest,
                "arguments": prepared["arguments"],
            }
        )
        if prepared["phase"] == "exec":
            self._fmt_cases.append(
                self._format_new_case_record(
                    model.FORMAT_CASES[prepared["case_index"]],
                    prepared["call_id"],
                    prepared["position"],
                    prepared["arguments"],
                )
            )
        else:
            self._fmt_polls += 1
        self._fmt_outstanding = {
            "call_id": prepared["call_id"],
            "issue_position": prepared["position"],
            "phase": prepared["phase"],
        }

    def _format_retain_result(self, wrapper_text: str, position: int, outstanding: dict) -> None:
        case = self._fmt_cases[self._fmt_case_index]
        case["results"].append(
            {
                "call_id": outstanding["call_id"],
                "issued_position": outstanding["issue_position"],
                "result_position": position,
                "wrapper": wrapper_text,
            }
        )
        self._fmt_retained_results.append((outstanding["call_id"], wrapper_text))

    def _format_finalize_case(self) -> None:
        """Fill the COMPLETE case record from the retained
        verified frames (the closed transport byte law held
        slice by slice, so the retained concatenation IS the
        verified full output): the dual numeric coordinates,
        the poll count, the output identity and the closed
        byte facts."""
        case = self._fmt_cases[self._fmt_case_index]
        pieces = [
            model.parse_native_tool_wrapper(entry["wrapper"])["output"].encode()
            for entry in case["results"]
        ]
        output = b"".join(pieces)
        case["output_bytes"] = len(output)
        case["output_sha256"] = model.sha256_bytes(output)
        case["nonempty_pieces"] = sum(1 for piece in pieces if piece)
        case["polls"] = len(case["results"]) - 1 if case["kind"] == "stream" else 0
        case["truncated"] = case["kind"] == "truncated"
        case["crlf"] = b"\r\n" in output
        case["non_ascii"] = any(b >= 0x80 for b in output)
        # the verified full chain committed: completion is a
        # measured fact now, never an issuance placeholder
        case["status"] = "completed"
        case["exit"] = 0
        case["verified"] = True

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
            "scenario-deadline-expired": "the scenario deadline is expired at this request",
            "causal-position": "causal request position is not closed",
            "causal-order": "result request is not after issuance",
            "slaif_fixture_unissued": "call identity not runtime issued",
            "slaif_fixture_mismatched": "call identity mismatched",
            "slaif_fixture_partial": "call result set is incomplete",
            "issue-rejected": "issuance was refused",
            "tools-overbound": "offered tools exceed the finite bound",
            "format-history": "accumulated tool history is not the retained set",
            "format-frame-deviation": "tool result frame is not the pinned closed form",
            "format-chain-deviation": "tool result chain is not the declared form",
            "format-multichunk-deviation": "stream case did not deliver multiple nonempty pieces",
            "format-seed-mismatch": "observed output differs from the immutable seed",
            "format-truncation-mismatch": "truncated output has no unique effective budget",
            "format-poll-bound": "empty-stdin poll bound exceeded",
            "format-not-ready": "format scenario is not complete",
            "format-seed-untrusted": "format seed seam is untrusted",
            "format-seed-copy-mismatch": "format seed copy is not the immutable original",
            "format-tools-unoffered": "the closed format tool is not offered in the closed shape",
            "format-post-bound": "the finite model-POST bound is exceeded",
            "format-issue-bound": "the finite issued-call bound is exceeded",
            "format-deadline-unbound": "the owner absolute END is not bound",
            "format-deadline-expired": "the owner absolute END is already past",
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

    def _auth_refused(self) -> tuple[str, str, bytes]:
        """Fixed closed 401 for the local synthetic auth binding:
        no header value, reason detail or echo of any kind."""
        body = (
            b'{"error":{"code":"invalid-authorization",'
            b'"message":"authorization is not valid",'
            b'"type":"authentication_error"}}'
        )
        return "401 Unauthorized", "application/json", body

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
        # The quiesce subject is resolved from the image-owned
        # identity facts BEFORE any scan: the owner-profile image
        # accounts its frozen independent subject UID, the original
        # image keeps the fixed 21002 (the closed law above).  A
        # corrupted owner image fails the quiesce closed with a
        # fixed refusal — it never silently counts the wrong
        # subject and never mints a false closure.
        subject_uid = quiesce_subject_uid()
        subjects = subject_scan() if subject_scan is not None else count_uid_processes(subject_uid)
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

    def format_snapshot_record(self) -> dict:
        """The DISTINCT closed format-capture snapshot record
        (the canonical 017-aj entry's scenario): the four
        COMPLETE case records (retained verified wrappers with
        their dual numeric coordinates), the complete ordered
        issued registry WITH the exact closed argument shapes
        (typed), the immutable pre-launch seed identity, and
        the controller's own ledger totals — RE-VALIDATED by
        the closed format-snapshot law before export: a
        non-complete or deviant scenario is a closed refusal,
        never a partial record (an honest unqualified state,
        never a minted pass)."""
        if self._fmt_state != "done" or len(self._fmt_cases) != len(model.FORMAT_CASES):
            raise ControllerError("format-not-ready")
        with self.ledger_lock:
            controller_ledger = {
                "requests": self.ledger.requests,
                "output_bytes": self.ledger.output_bytes,
            }
        seed_total = sum(len(data) for _name, data in model.FORMAT_SEED_FILES)
        record = {
            "record": model.SCHEMA_FORMAT_SNAPSHOT,
            "synthetic": True,
            "issued_calls": [dict(entry) for entry in self._fmt_issued],
            "cases": [dict(case) for case in self._fmt_cases],
            "seed": [
                [name, model.sha256_bytes(data), len(data)]
                for name, data in model.FORMAT_SEED_FILES
            ],
            "seed_total_bytes": seed_total,
            "originals_bytes": seed_total,
            "originals_sha256": model.sha256_bytes(
                b"".join(data for _name, data in model.FORMAT_SEED_FILES)
            ),
            "exporter_uid": self.exporter_uid,
            "exported_before_teardown": True,
            "model_posts": self._fmt_posts,
            "controller_ledger": controller_ledger,
            "polls": self._fmt_polls,
            "final_state": "done",
        }
        model.validate_format_snapshot_record(record)
        return record

    def format_snapshot_record_partial(self) -> dict:
        """The DISTINCT safe PARTIAL format-capture snapshot
        record (the canonical 017-aj entry's scenario, non-
        complete state): the ordered issued-registry prefix
        (typed closed argument shapes), the issued-case prefix —
        every entry before the last a COMPLETE verified case
        record, at most ONE pending case (the last) carrying
        only its retained verified frames — the immutable pre-
        launch seed identity, the controller's own ledger totals,
        the ACTUAL non-resettable ISSUED poll counter (the
        per-case pending retained poll counts are explicitly
        separate), and the ACTUAL non-done final state,
        RE-VALIDATED by the closed partial-snapshot law before
        export: every
        retained wrapper is re-verified against the immutable
        seed, no completion/exit/verified placeholder exists in
        the form, and a deviant or unknown state is a closed
        refusal — never a capture-ready fact and never a minted
        pass (the complete form keeps its exact historical
        law)."""
        if self._fmt_state == "done":
            raise ControllerError("format-not-partial")
        with self.ledger_lock:
            controller_ledger = {
                "requests": self.ledger.requests,
                "output_bytes": self.ledger.output_bytes,
            }
        cases: list[dict] = []
        for case in self._fmt_cases:
            if case["verified"]:
                cases.append(dict(case))
            else:
                results = [dict(entry) for entry in case["results"]]
                # the per-case RETAINED poll count: explicitly
                # separate from the global issued counter
                case_polls = len(results) - 1 if case["kind"] == "stream" and results else 0
                cases.append(
                    {
                        "case": case["case"],
                        "kind": case["kind"],
                        "seed_files": list(case["seed_files"]),
                        "command": case["command"],
                        "call_id": case["call_id"],
                        "call_position": case["call_position"],
                        "arguments_sha256": case["arguments_sha256"],
                        "status": "pending",
                        "results": results,
                        "polls": case_polls,
                    }
                )
        seed_total = sum(len(data) for _name, data in model.FORMAT_SEED_FILES)
        record = {
            "record": model.SCHEMA_FORMAT_SNAPSHOT_PARTIAL,
            "synthetic": True,
            "issued_calls": [dict(entry) for entry in self._fmt_issued],
            "cases": cases,
            "seed": [
                [name, model.sha256_bytes(data), len(data)]
                for name, data in model.FORMAT_SEED_FILES
            ],
            "seed_total_bytes": seed_total,
            "originals_bytes": seed_total,
            "originals_sha256": model.sha256_bytes(
                b"".join(data for _name, data in model.FORMAT_SEED_FILES)
            ),
            "exporter_uid": self.exporter_uid,
            "exported_before_teardown": True,
            "model_posts": self._fmt_posts,
            "controller_ledger": controller_ledger,
            # the ACTUAL non-resettable ISSUED poll counter (the
            # transactional FSM commits the next poll with every
            # accepted running result): never decremented or
            # relabeled for codec acceptance
            "polls": self._fmt_polls,
            "final_state": self._fmt_state,
            "qualification": model.FORMAT_QUALIFICATION_NOT_QUALIFIED,
        }
        model.validate_format_snapshot_record_partial(record)
        return record

    def format_capture_record(self) -> dict:
        """The DISTINCT closed format-capture record for the
        current state: the COMPLETE snapshot if and only if the
        scenario is done, otherwise the DISTINCT safe PARTIAL
        form.  The closed pair law: the complete export tag
        pairs with the complete snapshot, the partial export tag
        with the partial snapshot — the owner's outer identity
        metadata is bounded by the SAME 256 KiB total at the
        consumer and producer seams.  A deviant state is a
        closed refusal from the re-validation, never a minted
        pass and never silently relabeled."""
        if self._fmt_state == "done":
            return self.format_snapshot_record()
        return self.format_snapshot_record_partial()


# -- bounded process scans (fail closed on degraded evidence) --------------------
def _image_identity_profile_raw() -> bytes | None:
    """The bounded immutable read of the image-owned mode constant.

    Same closed law as the stand-in's resolution: absent file is
    None (the original default — the original image never bakes
    it); ABSENCE is verified ENOENT ONLY (any other lookup failure
    is a fixed closed refusal — a failed lookup must never
    silently choose the original); present file facts are verified
    FIRST (regular file, no link, root-owned, mode 0444 — the
    in-image immutable state), then the content is read with a
    cap+1 bound (an overbound file is refused, never fully read).
    """
    try:
        st = os.lstat(IDENTITY_PROFILE_FILE)
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise ControllerError("quiesce-profile-lookup") from None
        return None
    if (
        not stat_mod.S_ISREG(st.st_mode)
        or st.st_uid != 0
        or st.st_gid != 0
        or stat_mod.S_IMODE(st.st_mode) != 0o444
    ):
        raise ControllerError("quiesce-profile-state")
    if st.st_size > IDENTITY_PROFILE_FILE_MAX_BYTES:
        raise ControllerError("quiesce-profile-size")
    try:
        with open(IDENTITY_PROFILE_FILE, "rb") as handle:
            raw = handle.read(IDENTITY_PROFILE_FILE_MAX_BYTES + 1)
    except OSError:
        raise ControllerError("quiesce-profile-unreadable") from None
    if len(raw) > IDENTITY_PROFILE_FILE_MAX_BYTES:
        raise ControllerError("quiesce-profile-size")
    return raw


def _parse_quiesce_profile(raw: bytes) -> str | None:
    """The closed single-constant content law (pure, no FS).

    Exactly one line of the closed grammar (a fixed name, `` = ``,
    the quoted closed value, one trailing newline); the closed
    values are the two canonical profile names: the owner value
    selects the owner-UID mode, the original value the original
    mode (like an absent file).  Any other value, malformed
    grammar or encoding is a closed refusal.  The content is never
    imported or executed.
    """
    match = _QUIESCE_MODE_RE.fullmatch(raw)
    if match is None:
        raise ControllerError("quiesce-profile-grammar")
    value = match.group(1).decode("ascii")
    if value == _QUIESCE_OWNER_PROFILE:
        return "owner"
    if value == _QUIESCE_ORIGINAL_PROFILE:
        return None
    raise ControllerError("quiesce-profile-unknown")


def quiesce_subject_uid() -> int:
    """The closed in-image quiesce subject UID (017-aa).

    Original mode (absent image-owned marker, or the explicit
    original value): the historical fixed 21002 — the original
    quiesce subject law byte-for-byte.  Owner mode: the baked
    closed profile DATA record's frozen subject UID, decoded with
    the production codec after the bounded immutable state checks
    (regular file, no link, root-owned, 0444, cap+1) and the
    closed profile/controller verification.  Any missing / unknown
    / mismatched / unsafe marker or DATA under the owner marker is
    a fixed closed refusal — the quiesce scan then reports a
    degraded scan, never a silent zero, and NEVER falls back to
    the original subject.  The identity module is imported ONLY
    in owner mode (the original image does not carry it).
    """
    raw_mode = _image_identity_profile_raw()
    mode = None if raw_mode is None else _parse_quiesce_profile(raw_mode)
    if mode != "owner":
        return SUBJECT_UID
    try:
        import cache_native_fixture_identity as fixture_identity
    except ImportError:
        raise ControllerError("quiesce-profile-module") from None
    try:
        st = os.lstat(PROFILE_DATA_PATH)
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise ControllerError("quiesce-data-lookup") from None
        raise ControllerError("quiesce-data-missing") from None
    if (
        not stat_mod.S_ISREG(st.st_mode)
        or st.st_uid != 0
        or st.st_gid != 0
        or stat_mod.S_IMODE(st.st_mode) != 0o444
    ):
        raise ControllerError("quiesce-data-state")
    max_bytes = fixture_identity.MAX_RECORD_BYTES
    if st.st_size > max_bytes:
        raise ControllerError("quiesce-data-size")
    try:
        with open(PROFILE_DATA_PATH, "rb") as handle:
            raw = handle.read(max_bytes + 1)
    except OSError:
        raise ControllerError("quiesce-data-unreadable") from None
    if len(raw) > max_bytes:
        raise ControllerError("quiesce-data-size")
    try:
        desc = fixture_identity.decode_description(raw)
    except ValueError:
        raise ControllerError("quiesce-data-invalid") from None
    if desc.profile != fixture_identity.PROFILE_OWNER_UID or (
        desc.controller_uid,
        desc.controller_gid,
    ) != (fixture_identity.CONTROLLER_UID, fixture_identity.CONTROLLER_GID):
        raise ControllerError("quiesce-data-invalid")
    return desc.subject_uid


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
        if self.provider.scenario == "format-capture":
            # The DISTINCT selected format payload: the quiesce
            # record plus the format capture record ONLY — the
            # COMPLETE snapshot if and only if the scenario is
            # done, otherwise the DISTINCT safe PARTIAL form
            # (honest pending facts, never a minted pass) — and
            # the closed export tag paired with it (the
            # original six-field payload's exact historical
            # field set and law are never widened).  The TOTAL
            # serialized payload is bounded at the 256 KiB
            # selected-capture bound; the owner's outer
            # identity metadata (binding/identity/CID) is
            # bounded by the SAME total at the consumer and
            # producer seams.
            snapshot = self.provider.format_capture_record()
            selected = {
                "record": (
                    model.SCHEMA_FORMAT_EXPORT
                    if snapshot["record"] == model.SCHEMA_FORMAT_SNAPSHOT
                    else model.SCHEMA_FORMAT_EXPORT_PARTIAL
                ),
                "quiesce": self._quiesce_record,
                "snapshot": snapshot,
            }
            payload = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
            if len(payload) > model.FORMAT_SNAPSHOT_MAX_BYTES:
                raise ControllerError("export-overbound")
            return payload
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
    if scenario not in ("diagnostic", "tool-cycle", "format-capture"):
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
        if scenario == "format-capture":
            # the SAME original owner absolute END (the existing
            # trusted config transport, already set by the
            # owner's prepare-target): the format scenario's
            # ledger deadline is that absolute anchor clamped at
            # ONE clock reading — never a fresh window, and the
            # anchor itself is stored (no later-clock
            # re-derivation that would extend the owner END);
            # the old relative meaning stays unchanged for
            # every other scenario
            ledger.set_deadline_absolute(format_clamped_deadline_anchor(deadline))
        else:
            ledger.set_deadline(min(deadline, ledger.budgets.lifetime_seconds))
        ledger_lock = threading.Lock()
        registry = model.IssuedRegistry(ledger.budgets.max_requests)
        # Local 017-s synthetic auth binding: the host selects it via
        # the container environment (absent on the hosted CI path).
        # A present-but-malformed token fails closed above.
        auth_token = os.environ.get("SLAIF_FIXTURE_AUTH_TOKEN")
        provider = Provider(
            port,
            ledger,
            registry,
            ledger_lock,
            scenario=scenario,
            auth_token=auth_token,
        )
        exporter = Exporter(provider, ledger, ledger_lock, mode)
        # Seed the fixed originals BEFORE ownership verification.
        provider.seed_originals()
        # The format seed seam (subject-readable mirror of the
        # immutable pre-launch originals) is published BEFORE
        # ownership verification as well: a pre-existing
        # mismatched copy is a closed refusal at construction.
        if scenario == "format-capture":
            provider.seed_format_seeds()
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
