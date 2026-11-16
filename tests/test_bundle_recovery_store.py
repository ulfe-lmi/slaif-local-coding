"""Protected per-session recovery store (020) -- first increment.

Real temporary-filesystem evidence over the protected store:
the OPERATOR-PREPARED 0700 root, descriptor-relative session
creation (0700 even under the umask-022 test context),
expected-generation CAS with the actual observed generation
on every refusal, the OS-held exclusive writer lock (in-
process and cross-process, with kernel release on holder
death) and the pointer / checkpoint permission law.  The
genuine 018-p/018-t chain fixtures are reused from the
accepted codec increment (legal NON-DEFAULT 1048576
GraphBounds stage, disclosed there).  The fault /
security matrix covers the closed store limitations
(symlink / unsafe-mode / FIFO / torn / corrupt / missing
/ oversized / foreign-address / credential / escape
negatives) at their actual temp-filesystem scope.
"""

from __future__ import annotations

import hashlib
import json
import os
import select
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.recovery_codec import (
    encode_recovery_record,
)
from slaif_local_coding.constitution.bundles.recovery_models import (
    RecoveryRecord,
    RecoverySessionAddress,
)
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryStore,
    RecoveryStoreError,
    RecoveryStoreLimitation,
    session_directory_name,
)
from tests.test_bundle_recovery_codec import (
    _canonical_bytes,
    _credential_record_direct,
    _genuine_record,
    _rebind_digest,
)
from tests.test_causal_history import ENDPOINTS, MODES

_IO_FAILURE = "the recovery session store operation failed"
_WRITER_CONFLICT = "another live writer owns the recovery session"
_PATH_ESCAPE = "the recovery session path is unsafe"

#: The subprocess lock holder: takes the OS-held exclusive
#: writer lock on the pre-existing session directory and
#: holds it until signalled (no product code, stdlib only).
_HOLDER_SCRIPT = """
import fcntl
import os
import sys


session_dir = sys.argv[1]
root_fd = os.open(session_dir, os.O_RDONLY | os.O_DIRECTORY)
try:
    lock_fd = os.open(
        "writer.lock", os.O_RDWR | os.O_CREAT, 0o600, dir_fd=root_fd
    )
except OSError:
    print("holder-error")
    sys.exit(1)
fcntl.flock(lock_fd, fcntl.LOCK_EX)
print("locked")
sys.stdout.flush()
import time

while True:
    time.sleep(3600)
"""


def _prepared_root(tmp_path: Path) -> Path:
    """The operator-prepared protected store root (the
    store requires the existing 0700 / current-owner
    directory and never creates it)."""
    root = tmp_path / "recovery-root"
    root.mkdir(mode=0o700)
    root.chmod(0o700)
    st = os.stat(root)
    assert stat.S_ISDIR(st.st_mode)
    assert stat.S_IMODE(st.st_mode) == 0o700
    assert st.st_uid == os.getuid()
    return root


def _address_and_records(
    mode: AdmissionMode, endpoint: str
) -> tuple[RecoverySessionAddress, RecoveryRecord, RecoveryRecord]:
    ns_a, _, _, _, record_a = _genuine_record(mode, endpoint)
    # A genuinely NEW second-generation checkpoint for the
    # SAME session address (a fresh genuine chain with a
    # distinct root body; the store serializes PUBLICATION,
    # never source freshness).
    ns_b, _, _, _, record_b = _genuine_record(mode, endpoint, root_body="ROOT-V2 " * 512)
    assert ns_a.principal == ns_b.principal
    assert record_a.payload_digest != record_b.payload_digest
    return RecoverySessionAddress.from_namespace(ns_a), record_a, record_b


@pytest.mark.parametrize("mode,endpoint", list(zip(MODES, ENDPOINTS, strict=True)))
def test_publish_load_second_generation_and_cas(
    tmp_path: Path, mode: AdmissionMode, endpoint: str
) -> None:
    address, record_a, record_b = _address_and_records(mode, endpoint)
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        assert session.address is address or session.address == address
        session_dir = store.root / session_directory_name(address)
        st = os.stat(session_dir)
        assert stat.S_ISDIR(st.st_mode)
        assert stat.S_IMODE(st.st_mode) == 0o700  # exact, despite umask 022
        assert st.st_uid == os.getuid()

        first = session.publish(record_a, expected_generation=0)
        assert first.limitation is RecoveryStoreLimitation.OK
        assert first.generation == 1
        assert first.actual_generation == 1
        assert first.pointer is not None
        assert first.pointer.file_name == "checkpoint-1.json"
        assert first.pointer.record_bytes > 0
        assert len(first.pointer.file_digest) == 64
        for name in ("checkpoint-1.json", "current.json", "writer.lock"):
            fst = os.stat(session_dir / name)
            assert stat.S_ISREG(fst.st_mode)
            assert stat.S_IMODE(fst.st_mode) == 0o600
            assert fst.st_uid == os.getuid()

        loaded = session.load()
        assert loaded.limitation is RecoveryStoreLimitation.OK
        assert loaded.record == record_a
        assert loaded.pointer is not None
        assert loaded.pointer.generation == 1
        assert session.current_generation() == 1

        second = session.publish(record_b, expected_generation=1)
        assert second.limitation is RecoveryStoreLimitation.OK
        assert second.generation == 2
        assert second.actual_generation == 2
        assert second.pointer is not None
        assert second.pointer.file_name == "checkpoint-2.json"

        loaded2 = session.load()
        assert loaded2.limitation is RecoveryStoreLimitation.OK
        assert loaded2.record == record_b
        assert loaded2.pointer is not None
        assert loaded2.pointer.generation == 2
        assert session.current_generation() == 2

        # A STALE CAS (expected 1 under current 2) refuses with
        # the ACTUAL observed generation and preserves state.
        stale = session.publish(record_a, expected_generation=1)
        assert stale.limitation is RecoveryStoreLimitation.GENERATION_MISMATCH
        assert stale.generation is None
        assert stale.actual_generation == 2
        assert session.load().record == record_b
        assert session.current_generation() == 2

        # Expected-0 against an existing generation refuses too.
        zero = session.publish(record_a, expected_generation=0)
        assert zero.limitation is RecoveryStoreLimitation.GENERATION_MISMATCH
        assert zero.actual_generation == 2
    finally:
        session.close()


def test_missing_and_relative_root_refused(tmp_path: Path) -> None:
    with pytest.raises(RecoveryStoreError) as exc:
        RecoveryStore(tmp_path / "absent" / "root")
    assert exc.value.args[0] == _IO_FAILURE
    with pytest.raises(RecoveryStoreError) as exc:
        RecoveryStore(Path("relative/root"))
    assert exc.value.args[0] == _PATH_ESCAPE


@pytest.mark.parametrize("mode,endpoint", list(zip(MODES, ENDPOINTS, strict=True)))
def test_competing_writer_in_process(tmp_path: Path, mode: AdmissionMode, endpoint: str) -> None:
    address, record_a, _ = _address_and_records(mode, endpoint)
    store = RecoveryStore(_prepared_root(tmp_path))
    first = store.open_session(address)
    try:
        with pytest.raises(RecoveryStoreError) as exc:
            store.open_session(address)
        assert exc.value.args[0] == _WRITER_CONFLICT
        # The first writer is unaffected and can still publish.
        published = first.publish(record_a, expected_generation=0)
        assert published.limitation is RecoveryStoreLimitation.OK
    finally:
        first.close()


def _read_bounded_line(fd: int, timeout: float) -> str:
    """A select-gated UNBUFFERED line read on the raw
    descriptor (``os.read`` returns exactly what the pipe
    holds; a Python-level buffer can never starve the
    select loop, and a holder that fails to start cannot
    block the test)."""
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        ready, _, _ = select.select([fd], [], [], min(remaining, 0.5))
        if not ready:
            continue
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        chunks.append(chunk)
        if b"\n" in chunk:
            break
    return b"".join(chunks).decode("utf-8", "replace").strip()


def _drain_bounded(fd: int, timeout: float) -> str:
    """A bounded diagnostic drain (select-gated, raw
    ``os.read``; after the writer is dead the pipe reaches
    EOF, so the read can never block past the deadline)."""
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        ready, _, _ = select.select([fd], [], [], min(remaining, 0.5))
        if not ready:
            continue
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", "replace")


def _kill_bounded(holder: subprocess.Popen[bytes]) -> None:
    """Guaranteed cleanup of the owned holder child:
    terminate -> wait (kill on timeout) -> close the
    pipes, never an unbounded wait."""
    try:
        holder.terminate()
    except OSError:
        pass
    try:
        holder.wait(timeout=30)
    except subprocess.TimeoutExpired:
        holder.kill()
        holder.wait(timeout=30)
    for stream in (holder.stdout, holder.stderr):
        if stream is not None:
            stream.close()


@pytest.mark.parametrize("mode,endpoint", list(zip(MODES, ENDPOINTS, strict=True)))
def test_cross_process_writer_conflict_and_kernel_release(
    tmp_path: Path, mode: AdmissionMode, endpoint: str
) -> None:
    address, record_a, _ = _address_and_records(mode, endpoint)
    store = RecoveryStore(_prepared_root(tmp_path))
    # Pre-create the session directory through the store, then
    # release: a real external process now owns the only path
    # to the exclusive writer lock.
    session_dir = store.root / session_directory_name(address)
    opened = store.open_session(address)
    opened.close()
    holder = subprocess.Popen(
        [sys.executable, "-c", _HOLDER_SCRIPT, str(session_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert holder.stdout is not None
    assert holder.stderr is not None
    # BOUNDED readiness wait: a holder that fails to start
    # cannot block the test forever, and the owned child is
    # always cleaned up (terminate -> wait -> close).
    line = _read_bounded_line(holder.stdout.fileno(), timeout=60.0)
    if line != "locked":
        diagnostics = _drain_bounded(holder.stderr.fileno(), timeout=5.0)
        _kill_bounded(holder)
        raise AssertionError(
            f"lock holder did not become ready: {line!r}; stderr: {diagnostics[:300]!r}"
        )
    try:
        with pytest.raises(RecoveryStoreError) as exc:
            store.open_session(address)
        assert exc.value.args[0] == _WRITER_CONFLICT
    finally:
        _kill_bounded(holder)
    # Kernel release: after the holder died, the SAME address
    # opens and can publish without any stale-pid guessing.
    resumed = store.open_session(address)
    try:
        published = resumed.publish(record_a, expected_generation=0)
        assert published.limitation is RecoveryStoreLimitation.OK
        assert resumed.current_generation() == 1
    finally:
        resumed.close()


#: An actual process crash during publication (order:
#: fault/crash points before/after write, fsync and atomic
#: publication; compare the ACTUAL previous/current
#: generations, never manufacture a clean recovery
#: verdict): the plain-Python child opens the session,
#: hooks ``os.fsync`` to signal and block on the DIRECTORY
#: fsync (the durability step immediately after the
#: pointer rename), and publishes generation 2. The parent
#: SIGKILLs the child at the signal: a real crash after
#: atomic publication but before the directory durability
#: confirmation, with the writer process dead.
_CRASH_PUBLISH_SCRIPT = """
import json
import os
import stat as _stat
import sys
import time

root = os.path.abspath(sys.argv[1])
signal_path = sys.argv[2]
address_fields = json.loads(sys.argv[3])

from slaif_local_coding.constitution.bundles.recovery_models import (
    RecoverySessionAddress,
)
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryStore,
)

real_fsync = os.fsync


def held_fsync(fd):
    try:
        if _stat.S_ISDIR(os.fstat(fd).st_mode):
            with open(signal_path, "w", encoding="utf-8") as f:
                f.write("entered")
            while True:
                time.sleep(3600)
    except OSError:
        pass
    return real_fsync(fd)


os.fsync = held_fsync

store = RecoveryStore(root)
address = RecoverySessionAddress(**address_fields)
session = store.open_session(address)
loaded = session.load()
if loaded.record is None or loaded.pointer is None:
    print("crash-child-load-failed")
    sys.exit(1)
published = session.publish(loaded.record, expected_generation=loaded.pointer.generation)
print("published:" + published.limitation.value)
"""


@pytest.mark.parametrize("mode,endpoint", list(zip(MODES, ENDPOINTS, strict=True)))
def test_process_crash_during_publication_preserves_actual_committed(
    tmp_path: Path, mode: AdmissionMode, endpoint: str
) -> None:
    """An actual SIGKILL during publication (between the
    pointer rename and the directory fsync): the ACTUAL
    committed outcome is the new generation (the rename
    preceded the crash and the checkpoint file was fully
    written and fsynced before the pointer), the store is
    consistent and fully usable afterwards, and the writer
    lock was released by the kernel on process death. The
    previous generation is never claimed to have been
    rolled back, and no torn state survives."""
    address, record_a, _ = _address_and_records(mode, endpoint)
    store = RecoveryStore(_prepared_root(tmp_path))
    opened = store.open_session(address)
    try:
        first = opened.publish(record_a, expected_generation=0)
        assert first.limitation is RecoveryStoreLimitation.OK
        assert first.generation == 1
    finally:
        opened.close()
    signal_path = tmp_path / "crash-publish-signal"
    child = subprocess.Popen(
        [
            sys.executable,
            "-c",
            _CRASH_PUBLISH_SCRIPT,
            str(store.root),
            str(signal_path),
            json.dumps(address.model_dump()),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    try:
        deadline = time.monotonic() + 120.0
        while not signal_path.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not signal_path.exists():
            diagnostics = (
                _drain_bounded(child.stderr.fileno(), timeout=5.0)
                if child.stderr is not None
                else ""
            )
            _kill_bounded(child)
            raise AssertionError(
                f"crash child never reached the directory fsync; stderr: {diagnostics[:300]!r}"
            )
        try:
            os.kill(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        assert child.wait(timeout=30) == -signal.SIGKILL
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=30)
        for stream in (child.stdout, child.stderr):
            if stream is not None:
                stream.close()
    # The ACTUAL committed outcome: the pointer rename
    # committed before the crash, so generation 2 is the
    # committed consistent state (never a manufactured
    # rollback to 1), and the store is fully usable.
    resumed = store.open_session(address)
    try:
        assert resumed.current_generation() == 2
        loaded = resumed.load()
        assert loaded.limitation is RecoveryStoreLimitation.OK
        assert loaded.pointer is not None
        assert loaded.pointer.generation == 2
        assert loaded.record == record_a
        again = resumed.publish(record_a, expected_generation=2)
        assert again.limitation is RecoveryStoreLimitation.OK
        assert again.generation == 3
    finally:
        resumed.close()


def _write_protected(path: Path, data: bytes) -> None:
    """Write ONE new protected 0600 file (exact mode
    regardless of umask), fsynced."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset : offset + 65536])
        os.fsync(fd)
    finally:
        os.close(fd)


def test_symlinked_session_dir_and_root_refused(tmp_path: Path) -> None:
    address, _, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    session_dir = root / session_directory_name(address)
    real = tmp_path / "real-session"
    real.mkdir(mode=0o700)
    real.chmod(0o700)
    os.symlink(real, session_dir)
    with pytest.raises(RecoveryStoreError) as exc:
        store.open_session(address)
    assert exc.value.limitation is RecoveryStoreLimitation.SYMLINK_PATH
    os.unlink(session_dir)
    real_root = tmp_path / "real-root"
    real_root.mkdir(mode=0o700)
    real_root.chmod(0o700)
    link_root = tmp_path / "link-root"
    os.symlink(real_root, link_root)
    # A symlinked ROOT changes the canonical identity: the
    # fence reports it as a path escape (refused either way).
    with pytest.raises(RecoveryStoreError) as exc:
        RecoveryStore(link_root)
    assert exc.value.limitation is RecoveryStoreLimitation.PATH_ESCAPE
    # An ANCESTOR symlink changes the root's canonical
    # identity too: the closed fence refuses it as a path
    # escape (the per-component S_ISLNK branch of the chain
    # fence is the TOCTOU guard on top of this).
    sub = tmp_path / "sub"
    sub.mkdir(mode=0o700)
    sub.chmod(0o700)
    sub_real = sub / "real-root-2"
    sub_real.mkdir(mode=0o700)
    sub_real.chmod(0o700)
    sub_link = sub / "link-root-2"
    os.symlink(sub_real, sub_link)
    (sub_real / "nested").mkdir(mode=0o700)
    (sub_real / "nested").chmod(0o700)
    with pytest.raises(RecoveryStoreError) as exc:
        RecoveryStore(sub_link / "nested")
    assert exc.value.limitation is RecoveryStoreLimitation.PATH_ESCAPE


def test_preexisting_unsafe_session_dir_refused_not_repaired(tmp_path: Path) -> None:
    address, _, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    root = _prepared_root(tmp_path)
    session_dir = root / session_directory_name(address)
    session_dir.mkdir(mode=0o755)
    session_dir.chmod(0o755)
    store = RecoveryStore(root)
    with pytest.raises(RecoveryStoreError) as exc:
        store.open_session(address)
    assert exc.value.limitation is RecoveryStoreLimitation.UNSAFE_MODE
    # Refuse, never repair: the mode is exactly as found.
    assert stat.S_IMODE(os.stat(session_dir).st_mode) == 0o755


def test_fifo_entries_refused_bounded(tmp_path: Path) -> None:
    """An untrusted FIFO where the committed pointer or
    checkpoint entry should be a regular file is refused
    promptly with the closed ownership limitation -- the
    bounded-IO law (no blocking open, no raw error)."""
    address, record_a, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        session_dir = store.root / session_directory_name(address)
        ok = session.publish(record_a, expected_generation=0)
        assert ok.limitation is RecoveryStoreLimitation.OK
        checkpoint = session_dir / "checkpoint-1.json"
        os.unlink(checkpoint)
        os.mkfifo(checkpoint, mode=0o600)
        started = time.monotonic()
        result = session.load()
        assert time.monotonic() - started < 5.0
        assert result.limitation is RecoveryStoreLimitation.FOREIGN_OWNER
        assert result.record is None
        # A FIFO at the pointer entry is the same refusal,
        # and a publish reports it with the ACTUAL observed
        # state (pointer exists but is unreadable).
        pointer = session_dir / "current.json"
        os.unlink(pointer)
        os.mkfifo(pointer, mode=0o600)
        assert session.load().limitation is RecoveryStoreLimitation.FOREIGN_OWNER
        refused = session.publish(record_a, expected_generation=0)
        assert refused.limitation is RecoveryStoreLimitation.FOREIGN_OWNER
        assert refused.actual_generation is None
    finally:
        session.close()


def test_corrupt_truncated_and_missing_checkpoint(tmp_path: Path) -> None:
    address, record_a, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        ok = session.publish(record_a, expected_generation=0)
        assert ok.limitation is RecoveryStoreLimitation.OK
        session_dir = store.root / session_directory_name(address)
        checkpoint = session_dir / "checkpoint-1.json"
        original = checkpoint.read_bytes()
        corrupted = bytearray(original)
        corrupted[len(corrupted) // 2] ^= 0x01
        checkpoint.write_bytes(bytes(corrupted))
        assert session.load().limitation is RecoveryStoreLimitation.DIGEST_MISMATCH
        checkpoint.write_bytes(original[: len(original) // 2])
        assert session.load().limitation is RecoveryStoreLimitation.CHECKPOINT_TORN
        checkpoint.unlink()
        assert session.load().limitation is RecoveryStoreLimitation.CHECKPOINT_MISSING
        # The committed pointer is intact (the deletion did
        # not move it): a republish must CAS against the
        # committed generation, and it recreates the
        # checkpoint file.
        ok2 = session.publish(record_a, expected_generation=1)
        assert ok2.limitation is RecoveryStoreLimitation.OK
        assert ok2.generation == 2
        assert session.load().limitation is RecoveryStoreLimitation.OK
    finally:
        session.close()


def test_oversized_pointer_and_record(tmp_path: Path) -> None:
    address, record_a, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    small_store = RecoveryStore(store.root, max_bytes=1024)
    small_session = small_store.open_session(address)
    try:
        refused = small_session.publish(record_a, expected_generation=0)
        assert refused.limitation is RecoveryStoreLimitation.OVERSIZED
        assert refused.actual_generation == 0
        assert small_session.load().limitation is RecoveryStoreLimitation.MISSING
    finally:
        small_session.close()
    session = store.open_session(address)
    try:
        pointer = store.root / session_directory_name(address) / "current.json"
        _write_protected(pointer, b"x" * 9000)
        # load is a pure read: the hard pointer-size fence is
        # the closed OVERSIZED result with no record.
        oversize = session.load()
        assert oversize.limitation is RecoveryStoreLimitation.OVERSIZED
        assert oversize.record is None
        assert oversize.pointer is None
        # current_generation stays the raising accessor for
        # an invalid current (never silently 0).
        with pytest.raises(RecoveryStoreError) as exc:
            session.current_generation()
        assert exc.value.limitation is RecoveryStoreLimitation.OVERSIZED
    finally:
        session.close()


def test_foreign_address_and_pointer_escape_refusals(tmp_path: Path) -> None:
    address, record_a, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    foreign = RecoverySessionAddress(
        principal=address.principal,
        session="other-session",
        repository=address.repository,
        route=address.route,
        model_identity=address.model_identity,
        config_fingerprint=address.config_fingerprint,
    )
    session = store.open_session(foreign)
    try:
        refused = session.publish(record_a, expected_generation=0)
        assert refused.limitation is RecoveryStoreLimitation.NAMESPACE_MISMATCH
        assert refused.actual_generation == 0
        assert session.load().limitation is RecoveryStoreLimitation.MISSING
    finally:
        session.close()
    # Hand-crafted pointer documents with absolute / escape
    # file names can never be opened (closed MALFORMED).
    session_dir = store.root / session_directory_name(address)
    opened = store.open_session(address)
    try:
        pointer = session_dir / "current.json"
        for evil in ("/etc/passwd", "../checkpoint-1.json"):
            doc = json.dumps(
                {
                    "generation": 1,
                    "file": evil,
                    "file_digest": "0" * 64,
                    "record_bytes": 1,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
            pointer.unlink(missing_ok=True)
            _write_protected(pointer, doc)
            result = opened.load()
            assert result.limitation is RecoveryStoreLimitation.MALFORMED
    finally:
        opened.close()


def test_orphan_checkpoint_torn_then_exact_reuse(tmp_path: Path) -> None:
    address, record_a, record_b = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        ok1 = session.publish(record_a, expected_generation=0)
        assert ok1.limitation is RecoveryStoreLimitation.OK
        session_dir = store.root / session_directory_name(address)
        encoded_b = encode_recovery_record(record_b, max_bytes=store.max_bytes)
        orphan = session_dir / "checkpoint-2.json"
        # A different-byte same-generation orphan is torn:
        # refused, the previous generation preserved.
        _write_protected(orphan, encoded_b[:-4] + b"XXXX")
        torn = session.publish(record_b, expected_generation=1)
        assert torn.limitation is RecoveryStoreLimitation.CHECKPOINT_TORN
        assert torn.actual_generation == 1
        assert session.load().record == record_a
        # The EXACT-byte orphan is idempotently reused.
        orphan.unlink()
        _write_protected(orphan, encoded_b)
        ok2 = session.publish(record_b, expected_generation=1)
        assert ok2.limitation is RecoveryStoreLimitation.OK
        assert ok2.generation == 2
        assert session.load().record == record_b
    finally:
        session.close()


def test_credential_checkpoint_quarantine_at_load(tmp_path: Path) -> None:
    """A detectable forbidden credential in the retained
    source quarantines the load with the fixed limitation
    (no content echo) -- the checkpoint boundary of the
    SECURITY.md detectable-credential law."""
    record_cred, payload = _credential_record_direct()
    payload["payload_digest"] = _rebind_digest(payload)
    encoded = _canonical_bytes(payload)
    address = RecoverySessionAddress.from_namespace(record_cred.namespace)
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        session_dir = store.root / session_directory_name(address)
        _write_protected(session_dir / "checkpoint-1.json", encoded)
        digest = hashlib.sha256(encoded).hexdigest()
        pointer_doc = json.dumps(
            {
                "generation": 1,
                "file": "checkpoint-1.json",
                "file_digest": digest,
                "record_bytes": len(encoded),
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        _write_protected(session_dir / "current.json", pointer_doc)
        result = session.load()
        assert result.limitation is RecoveryStoreLimitation.CREDENTIAL_QUARANTINE
        assert result.record is None
    finally:
        session.close()


def test_publish_fault_after_rename_reports_actual_committed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A directory-fsync fault AFTER the atomic rename: the
    pointer IS committed while its durability is
    unconfirmed.  The store must report the ACTUAL
    committed outcome (the NEW observed generation under
    the closed IO_FAILURE), never the assumed old state."""
    address, record_a, record_b = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        ok1 = session.publish(record_a, expected_generation=0)
        assert ok1.limitation is RecoveryStoreLimitation.OK
        session_dir = store.root / session_directory_name(address)
        session_ino = os.stat(session_dir).st_ino
        real_fsync = os.fsync

        def flaky_fsync(fd: int) -> None:
            if os.fstat(fd).st_ino == session_ino:
                raise OSError("injected directory fsync failure")
            real_fsync(fd)

        with monkeypatch.context() as scoped:
            scoped.setattr(os, "fsync", flaky_fsync)
            faulted = session.publish(record_b, expected_generation=1)
        assert faulted.limitation is RecoveryStoreLimitation.IO_FAILURE
        assert faulted.generation is None
        assert faulted.pointer is None
        assert faulted.actual_generation == 2
        # The committed pointer reads back exactly (the
        # fault did not un-commit the rename).
        assert session.current_generation() == 2
        assert session.load().record == record_b
        # A later publish under the committed generation
        # proceeds normally (no phantom state).
        ok3 = session.publish(record_a, expected_generation=2)
        assert ok3.limitation is RecoveryStoreLimitation.OK
        assert ok3.generation == 3
    finally:
        session.close()


def test_stale_pointer_tmp_is_consumed_by_publish(tmp_path: Path) -> None:
    """A crashed prior publication may leave the pointer
    temp file behind: the next publication removes it and
    commits cleanly (no old temp bytes can bind a new
    generation)."""
    address, record_a, _ = _address_and_records(MODES[0], ENDPOINTS[0])
    store = RecoveryStore(_prepared_root(tmp_path))
    session = store.open_session(address)
    try:
        session_dir = store.root / session_directory_name(address)
        _write_protected(session_dir / "current.json.tmp", b"garbage-pointer-bytes")
        ok = session.publish(record_a, expected_generation=0)
        assert ok.limitation is RecoveryStoreLimitation.OK
        assert ok.generation == 1
        assert not (session_dir / "current.json.tmp").exists()
        assert session.load().record == record_a
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
