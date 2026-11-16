"""Protected per-session recovery storage (objective 020).

This is the explicitly opted-in protected per-session store
(SECURITY.md narrow exception; CACHE-REWORK.md section 12):
ONE protected namespace per coding session, directory mode
0700 / file mode 0600 / current owner / no symlink or path
escape, exclusive writer ownership, expected-generation
CAS, atomic generation publication (temp + fsync + rename +
directory fsync) and integrity digests.  Generation
serializes PUBLICATION, never source freshness.  A fault
preserves the previous committed generation or reports the
actual committed outcome explicitly; the store never
silently falls back from an invalid current generation and
never mixes new metadata with old bytes.  There is no
TTL, no LRU, no automatic deletion and no hidden hot
lookup: retention is operator-owned.

The session lookup ADDRESS is the authenticated stable
principal / session / repository / route plus the
configured model / policy context (``model_identity`` /
``config_fingerprint``) -- the session directory name is
the SHA-256 of that address's canonical JSON, an opaque
name that is NOT authentication and requires NO root,
source or surviving virtual reference to locate ONE
record.  The COMPLETE trusted namespace (workspace / mode /
bounds / versions / derived keys) is validated from the
LOADED record and must bind the address before any RAM
publication.

The configured root is OPERATOR-PREPARED: the store
requires the existing protected root (a real non-symlink
0700 directory of the current owner, validated on the same
descriptor) and refuses a missing root with the fixed
error -- it never creates the root or any ancestor, and
preparing the configured location is operator state.  A
newly created session directory is durably published in the
root before use; a pre-existing session directory is never
repaired (an unsafe pre-existing mode / owner is a fixed
refusal).

Every open / read / rename is descriptor-relative to the
owned session (or store-root) directory descriptor, and
every file is validated (regular file, current owner,
mode 0600) on the SAME opened descriptor that reads it
(no stat-then-reopen race), through a NON-BLOCKING open
so an untrusted FIFO / device can never block before the
type validation refuses it.  Exclusive writer ownership is
the OS-held ``flock`` on the session's ``writer.lock``
descriptor: held for the whole session lifetime, released
atomically by ``close`` or by the kernel on process death
(no live / stale pid guessing, no reclaim race).  A
publication fault reports the ACTUAL observed generation
(``RecoveryPublishResult.actual_generation``: 0 when no
pointer is committed, None when a pointer exists but is
unreadable, never an assumption) so a caller can never
assume the old state.  All refusals are fixed private
limitations or typed errors with no content, path or
identity echo.  The stage is INERT: no adapter wiring, no
v1 runtime activation, no normal-path read of recovery
content.
"""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import stat as stat_module
import threading
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .recovery_codec import (
    RecoveryCodecIntegrityError,
    RecoveryCodecMalformedError,
    RecoveryCodecSizeError,
    RecoveryCredentialQuarantineError,
    decode_recovery_record,
    encode_recovery_record,
)
from .recovery_models import (
    RECOVERY_RECORD_HARD_MAX_BYTES,
    RECOVERY_RECORD_INITIAL_MAX_BYTES,
    RecoveryError,
    RecoveryRecord,
    RecoverySessionAddress,
    recovery_address_key,
)

#: The ``current.json`` pointer file is a small closed
#: metadata document, never a content carrier.
POINTER_MAX_BYTES = 8192

#: The checkpoint write / read chunk (bounded transient
#: buffer, distinct from committed occupancy).
_IO_CHUNK = 65536


class RecoveryStoreLimitation(StrEnum):
    """The closed store limitation vocabulary (fixed
    private messages; no content echo)."""

    OK = "ok"
    MISSING = "missing"
    FOREIGN_OWNER = "foreign_owner"
    UNSAFE_MODE = "unsafe_mode"
    SYMLINK_PATH = "symlink_path"
    PATH_ESCAPE = "path_escape"
    WRITER_CONFLICT = "writer_conflict"
    CHECKPOINT_MISSING = "checkpoint_missing"
    CHECKPOINT_TORN = "checkpoint_torn"
    DIGEST_MISMATCH = "digest_mismatch"
    OVERSIZED = "oversized"
    MALFORMED = "malformed"
    CREDENTIAL_QUARANTINE = "credential_quarantine"
    NAMESPACE_MISMATCH = "namespace_mismatch"
    GENERATION_MISMATCH = "generation_mismatch"
    IO_FAILURE = "io_failure"
    SESSION_CLOSED = "session_closed"
    WRITE_IN_FLIGHT = "write_in_flight"
    RESOURCE_EXHAUSTED = "resource_exhausted"


_LIMITATION_MESSAGES: dict[RecoveryStoreLimitation, str] = {
    RecoveryStoreLimitation.OK: "ok",
    RecoveryStoreLimitation.MISSING: "the recovery session has no committed generation",
    RecoveryStoreLimitation.FOREIGN_OWNER: "the recovery session is owned by another principal",
    RecoveryStoreLimitation.UNSAFE_MODE: "the recovery session permissions are unsafe",
    RecoveryStoreLimitation.SYMLINK_PATH: "the recovery session path is unsafe",
    RecoveryStoreLimitation.PATH_ESCAPE: "the recovery session path is unsafe",
    RecoveryStoreLimitation.WRITER_CONFLICT: "another live writer owns the recovery session",
    RecoveryStoreLimitation.CHECKPOINT_MISSING: "the committed recovery checkpoint is absent",
    RecoveryStoreLimitation.CHECKPOINT_TORN: "the recovery checkpoint is torn",
    RecoveryStoreLimitation.DIGEST_MISMATCH: "the recovery checkpoint failed integrity",
    RecoveryStoreLimitation.OVERSIZED: "the recovery checkpoint exceeds its bound",
    RecoveryStoreLimitation.MALFORMED: "the recovery checkpoint is malformed",
    RecoveryStoreLimitation.CREDENTIAL_QUARANTINE: (
        "a detectable forbidden credential is present in the recovery record"
    ),
    RecoveryStoreLimitation.NAMESPACE_MISMATCH: ("the recovery record does not bind its session"),
    RecoveryStoreLimitation.GENERATION_MISMATCH: (
        "the expected checkpoint generation does not match"
    ),
    RecoveryStoreLimitation.IO_FAILURE: "the recovery session store operation failed",
    RecoveryStoreLimitation.SESSION_CLOSED: (
        "the recovery session is closed and can no longer publish"
    ),
    RecoveryStoreLimitation.WRITE_IN_FLIGHT: (
        "an owned recovery write is in flight; drain it before closing"
    ),
    RecoveryStoreLimitation.RESOURCE_EXHAUSTED: (
        "the process occupancy ceiling cannot cover a recovery transient reservation"
    ),
}


class RecoveryStoreError(RecoveryError):
    """A store refusal raised at a caller boundary (fixed
    private message, no echo; the closed limitation is
    carried so typed callers can dispatch on it without
    message parsing)."""

    def __init__(self, limitation: RecoveryStoreLimitation) -> None:
        super().__init__(_message(limitation))
        self.limitation = limitation


def _message(limitation: RecoveryStoreLimitation) -> str:
    return _LIMITATION_MESSAGES[limitation]


@dataclass(frozen=True, slots=True)
class RecoveryPointer:
    """The committed generation pointer (closed metadata:
    the generation serializes publication, never source
    freshness)."""

    generation: int
    file_name: str
    file_digest: str
    record_bytes: int


@dataclass(frozen=True, slots=True)
class RecoveryLoadResult:
    """The bounded result of ONE session load."""

    limitation: RecoveryStoreLimitation
    record: RecoveryRecord | None
    pointer: RecoveryPointer | None


@dataclass(frozen=True, slots=True)
class RecoveryPublishResult:
    """The bounded result of ONE expected-generation
    publication attempt.  ``generation`` / ``pointer`` are
    set only on OK; ``actual_generation`` is the
    generation ACTUALLY observed in the store after the
    attempt (0 when no pointer is committed, None when a
    pointer exists but is unreadable / corrupt) -- a
    refused or faulted attempt never lets a caller assume
    the previous state."""

    limitation: RecoveryStoreLimitation
    generation: int | None
    pointer: RecoveryPointer | None
    actual_generation: int | None


def session_directory_name(address: RecoverySessionAddress) -> str:
    """The opaque per-session directory name: the SHA-256
    of the canonical JSON of the authenticated stable
    address (an opaque filename is not authentication):
    the SAME stable 64-hex derivation as the
    trusted-address ``lineage_key`` identity, so the
    store directory and the resume boundary's initial-
    load reservation key are ONE identity."""
    return recovery_address_key(address)


def _verify_chain(root: Path) -> Path:
    """Setup-time root chain fence: the resolved path
    stays under the canonical parent (no escape) and every
    directory component is real and not a symlink.  All
    per-session work afterwards is descriptor-relative."""
    resolved = root.resolve(strict=True)
    if resolved.parent != root.parent or resolved.name != root.name:
        raise RecoveryStoreError(RecoveryStoreLimitation.PATH_ESCAPE)
    current = Path(root.anchor)
    for part in resolved.parts:
        if part == ".":
            continue
        current = current / part
        if current == resolved:
            break
        st = os.lstat(current)
        if stat_module.S_ISLNK(st.st_mode):
            raise RecoveryStoreError(RecoveryStoreLimitation.SYMLINK_PATH)
        if not stat_module.S_ISDIR(st.st_mode):
            raise RecoveryStoreError(RecoveryStoreLimitation.PATH_ESCAPE)
    return resolved


def _read_bounded(fd: int, size: int, limit: int) -> bytes:
    """Bounded full read of an fstat-sized file from the
    SAME descriptor that was validated."""
    if size > limit:
        raise RecoveryStoreError(RecoveryStoreLimitation.OVERSIZED)
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = os.read(fd, min(_IO_CHUNK, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    data = b"".join(chunks)
    if len(data) != size:
        raise RecoveryStoreError(RecoveryStoreLimitation.CHECKPOINT_TORN)
    return data


def _checkpoint_file_name(generation: int) -> str:
    return f"checkpoint-{generation}.json"


class RecoverySession:
    """ONE writer-owned open of a protected per-session
    recovery namespace (the owned session directory
    descriptor plus the OS-held exclusive writer lock)."""

    def __init__(
        self,
        store: RecoveryStore,
        address: RecoverySessionAddress,
        dir_fd: int,
    ) -> None:
        self._store = store
        self._address = address
        self._dir_fd = dir_fd
        # The exclusive writer lock: created / opened with
        # O_NOFOLLOW relative to the owned directory, then
        # validated (regular file, current owner, mode
        # 0600) on THAT SAME descriptor before the lock is
        # taken.  An untrusted target is refused, never
        # repaired; a live foreign holder is a fixed
        # conflict; a dead holder's lock is released by the
        # kernel (no pid guessing).
        try:
            lock_fd = os.open(
                "writer.lock",
                os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                0o600,
                dir_fd=dir_fd,
            )
        except OSError:
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        st = os.fstat(lock_fd)
        if not stat_module.S_ISREG(st.st_mode) or st.st_uid != os.getuid():
            os.close(lock_fd)
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.FOREIGN_OWNER)
        if stat_module.S_IMODE(st.st_mode) != 0o600:
            os.close(lock_fd)
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.UNSAFE_MODE)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, PermissionError):
            os.close(lock_fd)
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.WRITER_CONFLICT) from None
        self._lock_fd = lock_fd
        # The owned-write drain state (requirement 4): every
        # durable publication holds the in-flight slot for
        # its WHOLE owned write (write + fsync + rename +
        # directory fsync + readback), and the writer is
        # never released while a slot is held -- the async
        # teardown drains the slot count to zero before
        # closing, and a closed session refuses new writes
        # with the fixed limitation before any IO.  The
        # guard lock keeps the state consistent while an
        # owned write runs on a worker thread.
        self._write_guard = threading.Lock()
        self._in_flight = 0
        self._closing = False

    @property
    def address(self) -> RecoverySessionAddress:
        return self._address

    @property
    def in_flight(self) -> int:
        """The number of owned durable writes currently in
        flight (the teardown drain contract)."""
        with self._write_guard:
            return self._in_flight

    @property
    def max_bytes(self) -> int:
        return self._store.max_bytes

    @property
    def observed_generation(self) -> int | None:
        """The generation ACTUALLY observed in the store
        (0 = no pointer, None = pointer exists but is
        unreadable / corrupt, never an assumption)."""
        return self._observed_generation()

    def _begin_write(self) -> bool:
        """Claim the in-flight slot for ONE owned durable
        write; False when the session is already closed
        (no new write may start after close)."""
        with self._write_guard:
            if self._closing:
                return False
            self._in_flight += 1
            return True

    def _end_write(self) -> None:
        with self._write_guard:
            self._in_flight -= 1

    def _open_verified(self, name: str) -> int:
        """Open ONE descriptor relative to the owned
        directory (O_NOFOLLOW) and validate it (regular
        file, current owner, mode 0600) on THAT SAME
        descriptor before any read."""
        # O_NONBLOCK (no effect on regular files) keeps an
        # untrusted FIFO / device from blocking the open
        # before the same-descriptor type validation can
        # refuse it (bounded-IO law).
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self._dir_fd)
        except FileNotFoundError:
            raise
        except OSError:
            # A non-regular, unopenable or permission-
            # invisible entry (FIFO, device, foreign-mode
            # file) is the fixed ownership refusal -- never
            # a raw error or a blocked open.
            raise RecoveryStoreError(RecoveryStoreLimitation.FOREIGN_OWNER) from None
        st = os.fstat(fd)
        if not stat_module.S_ISREG(st.st_mode) or st.st_uid != os.getuid():
            os.close(fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.FOREIGN_OWNER)
        if stat_module.S_IMODE(st.st_mode) != 0o600:
            os.close(fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.UNSAFE_MODE)
        return fd

    def _open_pointer(self) -> int | None:
        """Open the committed pointer, validated on the
        same descriptor; None when no generation is
        committed yet.  Raises the fixed store error on
        unsafe ownership / mode / oversize."""
        try:
            fd = self._open_verified("current.json")
        except FileNotFoundError:
            return None
        st = os.fstat(fd)
        if st.st_size > POINTER_MAX_BYTES:
            os.close(fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.OVERSIZED)
        return fd

    def _parse_pointer(self, raw: bytes) -> RecoveryPointer | RecoveryStoreLimitation:
        """Closed pointer fence: the exact field set, the
        generation bound and the EXACT generated
        checkpoint basename for that generation (an
        untrusted absolute / ``..`` name can never be
        opened).  A malformed pointer document is the
        closed MALFORMED limitation, never a raised error
        or an opened path."""
        if b"/" in raw or b".." in raw:
            return RecoveryStoreLimitation.MALFORMED
        try:
            payload: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return RecoveryStoreLimitation.MALFORMED
        if not isinstance(payload, dict):
            return RecoveryStoreLimitation.MALFORMED
        if set(payload) != {"generation", "file", "file_digest", "record_bytes"}:
            return RecoveryStoreLimitation.MALFORMED
        generation = payload["generation"]
        file_name = payload["file"]
        file_digest = payload["file_digest"]
        record_bytes = payload["record_bytes"]
        if (
            isinstance(generation, bool)
            or not isinstance(generation, int)
            or generation < 1
            or not isinstance(file_name, str)
            or not isinstance(file_digest, str)
            or len(file_digest) != 64
            or any(c not in "0123456789abcdef" for c in file_digest)
            or isinstance(record_bytes, bool)
            or not isinstance(record_bytes, int)
            or record_bytes < 0
        ):
            return RecoveryStoreLimitation.MALFORMED
        if file_name != _checkpoint_file_name(generation):
            return RecoveryStoreLimitation.MALFORMED
        return RecoveryPointer(generation, file_name, file_digest, record_bytes)

    def _observed_generation(self) -> int | None:
        """The generation ACTUALLY observed in the store
        (bounded best-effort): 0 when no pointer is
        committed, the observed generation when readable,
        None when a pointer exists but is unreadable /
        corrupt (never an assumption)."""
        try:
            fd = self._open_pointer()
        except RecoveryStoreError:
            return None
        if fd is None:
            return 0
        try:
            try:
                raw = _read_bounded(fd, os.fstat(fd).st_size, POINTER_MAX_BYTES)
            except RecoveryStoreError:
                return None
        finally:
            os.close(fd)
        pointer = self._parse_pointer(raw)
        return pointer.generation if isinstance(pointer, RecoveryPointer) else None

    def load(self) -> RecoveryLoadResult:
        """Read the committed generation (bounded, fenced,
        codec-validated, address-bound) without any
        publication."""
        try:
            fd = self._open_pointer()
        except RecoveryStoreError as exc:
            # Every pointer-entry refusal (unsafe ownership /
            # mode, hard oversize fence) is a closed load
            # result, never a raw error: ``load`` is a pure
            # read, and ``current_generation`` remains the
            # raising accessor for an invalid current.
            return RecoveryLoadResult(exc.limitation, None, None)
        if fd is None:
            return RecoveryLoadResult(RecoveryStoreLimitation.MISSING, None, None)
        try:
            try:
                raw = _read_bounded(fd, os.fstat(fd).st_size, POINTER_MAX_BYTES)
            except RecoveryStoreError:
                # A short / torn pointer document is a
                # closed malformed document.
                return RecoveryLoadResult(RecoveryStoreLimitation.MALFORMED, None, None)
        finally:
            os.close(fd)
        pointer = self._parse_pointer(raw)
        if not isinstance(pointer, RecoveryPointer):
            return RecoveryLoadResult(pointer, None, None)
        try:
            data_fd = self._open_verified(pointer.file_name)
        except FileNotFoundError:
            return RecoveryLoadResult(RecoveryStoreLimitation.CHECKPOINT_MISSING, None, None)
        except RecoveryStoreError as exc:
            # A committed checkpoint entry that is not a
            # trusted regular file (FIFO / device / foreign
            # mode) is refused with its closed limitation;
            # the previous generation is never mixed with
            # untrusted bytes.
            return RecoveryLoadResult(exc.limitation, None, None)
        try:
            st = os.fstat(data_fd)
            if st.st_size != pointer.record_bytes:
                return RecoveryLoadResult(RecoveryStoreLimitation.CHECKPOINT_TORN, None, None)
            if st.st_size > self._store.max_bytes:
                return RecoveryLoadResult(RecoveryStoreLimitation.OVERSIZED, None, None)
            data = _read_bounded(data_fd, st.st_size, self._store.max_bytes)
        finally:
            os.close(data_fd)
        digest = hashlib.sha256(data).hexdigest()
        if digest != pointer.file_digest:
            return RecoveryLoadResult(RecoveryStoreLimitation.DIGEST_MISMATCH, None, None)
        try:
            record = decode_recovery_record(data, max_bytes=self._store.max_bytes)
        except RecoveryCodecSizeError:
            return RecoveryLoadResult(RecoveryStoreLimitation.OVERSIZED, None, None)
        except RecoveryCredentialQuarantineError:
            return RecoveryLoadResult(RecoveryStoreLimitation.CREDENTIAL_QUARANTINE, None, None)
        except RecoveryCodecIntegrityError:
            return RecoveryLoadResult(RecoveryStoreLimitation.DIGEST_MISMATCH, None, None)
        except RecoveryCodecMalformedError:
            return RecoveryLoadResult(RecoveryStoreLimitation.MALFORMED, None, None)
        if not self._address.binds(record.namespace):
            return RecoveryLoadResult(RecoveryStoreLimitation.NAMESPACE_MISMATCH, None, None)
        return RecoveryLoadResult(RecoveryStoreLimitation.OK, record, pointer)

    def _refused(self, limitation: RecoveryStoreLimitation) -> RecoveryPublishResult:
        return RecoveryPublishResult(limitation, None, None, self._observed_generation())

    def publish(self, record: RecoveryRecord, expected_generation: int) -> RecoveryPublishResult:
        """Publish ONE new generation under the expected-
        generation CAS: the checkpoint file is written
        O_EXCL with 0600 and fsynced, then the pointer is
        published atomically (temp + fsync + rename +
        directory fsync, every step descriptor-relative to
        the owned session directory).  A refused or
        faulted attempt reports the ACTUAL observed
        generation and never lets a caller assume the
        previous state."""
        if isinstance(expected_generation, bool) or not isinstance(expected_generation, int):
            raise RecoveryStoreError(RecoveryStoreLimitation.GENERATION_MISMATCH)
        if not self._address.binds(record.namespace):
            return self._refused(RecoveryStoreLimitation.NAMESPACE_MISMATCH)
        try:
            encoded = encode_recovery_record(record, max_bytes=self._store.max_bytes)
        except RecoveryCodecSizeError:
            return self._refused(RecoveryStoreLimitation.OVERSIZED)
        except RecoveryCredentialQuarantineError:
            return self._refused(RecoveryStoreLimitation.CREDENTIAL_QUARANTINE)
        return self.publish_encoded(encoded, record, expected_generation)

    def publish_encoded(
        self,
        encoded: bytes,
        record: RecoveryRecord,
        expected_generation: int,
    ) -> RecoveryPublishResult:
        """Publish ALREADY-ENCODED bounded bytes under
        the expected-generation CAS: the same fence
        law as ``publish`` (generation type, address
        join, the store byte ceiling) with the owned
        write marked in flight for the whole
        publication (a closed session refuses with
        the fixed ``session_closed`` limitation
        before any IO).  The encode step and the
        bounded transient reservation for these
        bytes are the caller's: the caller runs the
        codec under the store's declared bound (an
        oversized result refuses with the codec
        size law) and reserves these exact bytes
        against the SAME 019 process ceiling before
        this write starts.  The bytes / record
        association and the codec / credential law
        are re-proven BEFORE any write: the record
        is re-encoded under the SAME store bound and
        the supplied bytes must be byte-identical to
        that canonical encoding (a mismatch, an
        oversized record or a detectable credential
        refuses with the closed limitation before
        any IO; the post-publication read-back fence
        remains the descriptor-level check)."""
        if not isinstance(encoded, bytes) or not encoded:
            return self._refused(RecoveryStoreLimitation.MALFORMED)
        if isinstance(expected_generation, bool) or not isinstance(expected_generation, int):
            raise RecoveryStoreError(RecoveryStoreLimitation.GENERATION_MISMATCH)
        if not self._address.binds(record.namespace):
            return self._refused(RecoveryStoreLimitation.NAMESPACE_MISMATCH)
        if len(encoded) > self._store.max_bytes:
            return self._refused(RecoveryStoreLimitation.OVERSIZED)
        try:
            canonical = encode_recovery_record(record, max_bytes=self._store.max_bytes)
        except RecoveryCodecSizeError:
            return self._refused(RecoveryStoreLimitation.OVERSIZED)
        except RecoveryCredentialQuarantineError:
            return self._refused(RecoveryStoreLimitation.CREDENTIAL_QUARANTINE)
        if encoded != canonical:
            # The supplied bytes are not the record's
            # canonical encoding under the store's
            # bound: torn / mixed content must never
            # be persisted (the read-back fence alone
            # would be too late -- the write runs
            # first).
            return self._refused(RecoveryStoreLimitation.CHECKPOINT_TORN)
        if not self._begin_write():
            return self._refused(RecoveryStoreLimitation.SESSION_CLOSED)
        try:
            return self._publish_encoded_locked(encoded, record, expected_generation)
        finally:
            self._end_write()

    def _publish_encoded_locked(
        self,
        encoded: bytes,
        record: RecoveryRecord,
        expected_generation: int,
    ) -> RecoveryPublishResult:
        """The publication write body (checkpoint
        file, pointer publication, read-back
        fence), called with the in-flight write
        slot already held by ``publish_encoded``:
        no guard bookkeeping here, and every
        refusal and fault outcome is
        byte-for-byte the original single-method
        implementation."""
        current: RecoveryPointer | None = None
        try:
            current_fd = self._open_pointer()
        except RecoveryStoreError as exc:
            return self._refused(exc.limitation)
        try:
            if current_fd is None:
                if expected_generation != 0:
                    return self._refused(RecoveryStoreLimitation.GENERATION_MISMATCH)
            else:
                try:
                    raw = _read_bounded(current_fd, os.fstat(current_fd).st_size, POINTER_MAX_BYTES)
                except RecoveryStoreError:
                    return self._refused(RecoveryStoreLimitation.MALFORMED)
                parsed = self._parse_pointer(raw)
                if not isinstance(parsed, RecoveryPointer):
                    return self._refused(parsed)
                if expected_generation != parsed.generation:
                    return self._refused(RecoveryStoreLimitation.GENERATION_MISMATCH)
                current = parsed
        finally:
            if current_fd is not None:
                os.close(current_fd)
        generation = 1 if current is None else current.generation + 1
        file_name = _checkpoint_file_name(generation)
        digest = hashlib.sha256(encoded).hexdigest()
        # A crashed prior attempt of the SAME generation may
        # have left orphan bytes: reuse them only when they
        # ARE exactly the new bytes (idempotent
        # re-publication), and only after fsyncing them --
        # anything else is a torn checkpoint that must not
        # be mixed with new metadata.
        try:
            orphan_fd = self._open_verified(file_name)
        except FileNotFoundError:
            orphan_fd = None
        except RecoveryStoreError as exc:
            # A same-generation entry that is not a trusted
            # regular file can never be mixed with new
            # metadata: refuse with its closed limitation.
            return self._refused(exc.limitation)
        if orphan_fd is not None:
            try:
                st = os.fstat(orphan_fd)
                if st.st_size != len(encoded):
                    return self._refused(RecoveryStoreLimitation.CHECKPOINT_TORN)
                if _read_bounded(orphan_fd, st.st_size, self._store.max_bytes) != encoded:
                    return self._refused(RecoveryStoreLimitation.CHECKPOINT_TORN)
                os.fsync(orphan_fd)
            except (OSError, RecoveryStoreError):
                return self._refused(RecoveryStoreLimitation.IO_FAILURE)
            finally:
                os.close(orphan_fd)
        else:
            try:
                fd = os.open(
                    file_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=self._dir_fd,
                )
            except OSError:
                return self._refused(RecoveryStoreLimitation.IO_FAILURE)
            try:
                offset = 0
                while offset < len(encoded):
                    offset += os.write(fd, encoded[offset : offset + _IO_CHUNK])
                os.fchmod(fd, 0o600)
                os.fsync(fd)
            except OSError:
                # The pointer is untouched: the previous
                # committed generation is preserved (an
                # orphan partial file may remain,
                # unreferenced by any pointer).
                return self._refused(RecoveryStoreLimitation.IO_FAILURE)
            finally:
                os.close(fd)
        pointer = RecoveryPointer(generation, file_name, digest, len(encoded))
        pointer_bytes = json.dumps(
            {
                "generation": pointer.generation,
                "file": pointer.file_name,
                "file_digest": pointer.file_digest,
                "record_bytes": pointer.record_bytes,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        if len(pointer_bytes) > POINTER_MAX_BYTES:
            return self._refused(RecoveryStoreLimitation.MALFORMED)
        tmp_name = "current.json.tmp"
        try:
            os.unlink(tmp_name, dir_fd=self._dir_fd)
        except FileNotFoundError:
            pass
        except OSError:
            return self._refused(RecoveryStoreLimitation.IO_FAILURE)
        try:
            fd = os.open(
                tmp_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=self._dir_fd,
            )
        except OSError:
            return self._refused(RecoveryStoreLimitation.IO_FAILURE)
        try:
            offset = 0
            while offset < len(pointer_bytes):
                offset += os.write(fd, pointer_bytes[offset : offset + _IO_CHUNK])
            os.fchmod(fd, 0o600)
            os.fsync(fd)
        except OSError:
            return self._refused(RecoveryStoreLimitation.IO_FAILURE)
        finally:
            os.close(fd)
        try:
            os.rename(
                tmp_name,
                "current.json",
                src_dir_fd=self._dir_fd,
                dst_dir_fd=self._dir_fd,
            )
            os.fsync(self._dir_fd)
        except OSError:
            # The rename may be committed while directory
            # durability is unconfirmed: report the ACTUAL
            # observed generation; a caller must assume
            # neither the old nor the new state.
            return self._refused(RecoveryStoreLimitation.IO_FAILURE)
        # Post-publication fence: the committed pointer must
        # read back exactly as published (same-descriptor
        # validation, codec law, address join).
        loaded = self.load()
        actual = (
            loaded.pointer.generation if loaded.pointer is not None else self._observed_generation()
        )
        if (
            loaded.limitation is not RecoveryStoreLimitation.OK
            or loaded.pointer != pointer
            or loaded.record != record
        ):
            return RecoveryPublishResult(
                loaded.limitation
                if loaded.limitation is not RecoveryStoreLimitation.OK
                else RecoveryStoreLimitation.CHECKPOINT_TORN,
                None,
                None,
                actual,
            )
        return RecoveryPublishResult(RecoveryStoreLimitation.OK, generation, pointer, generation)

    def current_generation(self) -> int:
        """The committed generation: 0 ONLY when no
        generation is committed (MISSING).  An invalid /
        unreadable current pointer raises the fixed store
        error -- it is never silently mapped to 0."""
        loaded = self.load()
        if loaded.limitation is RecoveryStoreLimitation.MISSING:
            return 0
        if loaded.limitation is not RecoveryStoreLimitation.OK or loaded.pointer is None:
            raise RecoveryStoreError(loaded.limitation)
        return loaded.pointer.generation

    def committed_record_bytes(self) -> int:
        """The committed checkpoint's declared record
        bytes (the pointer's ``record_bytes`` field),
        read through the SAME descriptor-relative safe-
        open law (bounded by the pointer ceiling): a
        pre-allocation SIZE probe, not a restore -- no
        record bytes are read or parsed.  Returns 0
        when no generation is committed or the pointer
        is unreadable / malformed (the caller's own
        publication fences refuse that state regardless;
        the reservation floor still applies)."""
        try:
            fd = self._open_pointer()
        except RecoveryStoreError:
            return 0
        if fd is None:
            return 0
        try:
            raw = _read_bounded(fd, os.fstat(fd).st_size, POINTER_MAX_BYTES)
        except RecoveryStoreError:
            return 0
        finally:
            os.close(fd)
        parsed = self._parse_pointer(raw)
        if not isinstance(parsed, RecoveryPointer):
            return 0
        return parsed.record_bytes

    def close(self) -> None:
        """Release the writer lock (the kernel releases it
        on process death regardless).  Checkpoints and the
        lock file are operator-owned retention; nothing is
        deleted, and the stable lock inode means no
        unlink-replace race can mint a second owner.  The
        writer is NEVER released while an owned write is
        in flight: closing under a live write raises the
        fixed ``write_in_flight`` limitation (the session
        stays usable; the async teardown drains first)."""
        with self._write_guard:
            if self._in_flight > 0:
                raise RecoveryStoreError(RecoveryStoreLimitation.WRITE_IN_FLIGHT)
            self._closing = True
        try:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(self._lock_fd)
        os.close(self._dir_fd)


class RecoveryStore:
    """The protected per-session recovery store root (the
    owned root directory descriptor is validated on the
    same descriptor and used for all session creation)."""

    def __init__(
        self,
        root: Path | str,
        *,
        max_bytes: int = RECOVERY_RECORD_INITIAL_MAX_BYTES,
    ) -> None:
        if (
            isinstance(max_bytes, bool)
            or not isinstance(max_bytes, int)
            or not 1 <= max_bytes <= RECOVERY_RECORD_HARD_MAX_BYTES
        ):
            raise RecoveryStoreError(RecoveryStoreLimitation.OVERSIZED)
        self.max_bytes = max_bytes
        root_path = Path(root)
        if not root_path.is_absolute():
            raise RecoveryStoreError(RecoveryStoreLimitation.PATH_ESCAPE)
        # The configured root is OPERATOR-PREPARED: the store
        # requires the existing protected root (0700, current
        # owner) and never creates the root or any ancestor --
        # preparing and durably publishing the configured
        # location is operator state, and creating it here
        # would let fchmod repair a raced or pre-existing
        # target without owned-inode validation.
        try:
            resolved_root = _verify_chain(root_path)
        except FileNotFoundError:
            raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        self._root = resolved_root
        try:
            root_fd = os.open(resolved_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError:
            raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        st = os.fstat(root_fd)
        if not stat_module.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
            os.close(root_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.FOREIGN_OWNER)
        if stat_module.S_IMODE(st.st_mode) != 0o700:
            os.close(root_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.UNSAFE_MODE)
        self._root_fd = root_fd

    @property
    def root(self) -> Path:
        return self._root

    def open_session(self, address: RecoverySessionAddress) -> RecoverySession:
        """Open ONE writer-owned session for the
        authenticated stable address (no root / source /
        reference required to locate the session; the
        complete trusted namespace is validated from the
        loaded record).  Session creation and open are
        descriptor-relative to the owned root directory;
        a pre-existing session directory with an unsafe
        mode / owner is refused, never repaired."""
        name = session_directory_name(address)
        try:
            st = os.lstat(self._root / name)
        except FileNotFoundError:
            st = None
        if st is not None and stat_module.S_ISLNK(st.st_mode):
            raise RecoveryStoreError(RecoveryStoreLimitation.SYMLINK_PATH)
        created_dir = False
        try:
            os.mkdir(name, mode=0o700, dir_fd=self._root_fd)
            created_dir = True
        except FileExistsError:
            pass
        except OSError:
            raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        try:
            dir_fd = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=self._root_fd,
            )
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise RecoveryStoreError(RecoveryStoreLimitation.SYMLINK_PATH) from None
            raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        st = os.fstat(dir_fd)
        if not stat_module.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.FOREIGN_OWNER)
        if created_dir:
            # A newly created session directory is masked by
            # the process umask at mkdir time: force the exact
            # protected 0700 on the descriptor we own before
            # any use.  A pre-existing directory is NEVER
            # repaired -- an unsafe pre-existing mode is the
            # fixed UNSAFE_MODE refusal below.
            try:
                os.fchmod(dir_fd, 0o700)
            except OSError:
                os.close(dir_fd)
                raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        if stat_module.S_IMODE(st.st_mode) != 0o700:
            os.close(dir_fd)
            raise RecoveryStoreError(RecoveryStoreLimitation.UNSAFE_MODE)
        if created_dir:
            # Durably publish the NEW session directory entry
            # in the (pre-existing, operator-prepared) root
            # before the session can be used: fsyncing the
            # session directory alone would not durably
            # publish its name in its parent.
            try:
                os.fsync(self._root_fd)
            except OSError:
                os.close(dir_fd)
                raise RecoveryStoreError(RecoveryStoreLimitation.IO_FAILURE) from None
        return RecoverySession(self, address, dir_fd)


__all__ = [
    "POINTER_MAX_BYTES",
    "RecoveryLoadResult",
    "RecoveryPointer",
    "RecoveryPublishResult",
    "RecoverySession",
    "RecoveryStore",
    "RecoveryStoreError",
    "RecoveryStoreLimitation",
    "session_directory_name",
]
