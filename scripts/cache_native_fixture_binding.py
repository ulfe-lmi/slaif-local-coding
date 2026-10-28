#!/usr/bin/env python3
"""Typed immutable OAP order/run binding (order 017-t, section 2).

The smallest binding a later, separately-authorized fixture
preparation needs to bind ONE explicit opted-in run, BEFORE any
mutation, to:

- the exact active order ID (bounded OAP ID grammar);
- its UNIQUE committed immutable order file (exactly one
  ``<ID>-*.md`` entry in the bound source tree, disk bytes equal
  to the committed bytes);
- the literal committed source head (current HEAD equals it,
  clean worktree);
- the repository identity (``owner/repo`` parsed from the origin
  URL; the URL itself is never retained or echoed);
- the run identity (a module-minted 32-hex run id — never a
  caller value).

Resolution is STRICTLY READ-ONLY: no file, directory or git
state is created or changed, and resolution mints no authority
and no attempt.  Publication/review remains the separate
strategic pre-execution gate: this module makes NO
GitHub/network call, and source parsing never invents
permission from prose.  Actual permission still comes from the
active human/strategic order.

Per-order one-attempt namespaces: every order id gets its own
stable ``.oap-local/<order-id>/`` admission namespace, kept out
of git status by the checkout's LOCAL-only ``.git/info/exclude``
(no tracked file, no worktree content).  Within one order a
changed source head, directory or phase NEVER resets the
namespace: the record is keyed by the order, not by the head or
any caller-selected path.  The 017-s order keeps its historical
record schema and exhausted state exactly as written by
``cache_native_fixture_local.py`` (this module reads it with
that order's canonical schema and never rewrites it).

No new watchdog, budget or PID controller: this module is the
binding/record surface only.  One owner, one absolute END and
one cumulative ledger remain owned by the later fixture
preparation itself.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import select
import stat
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_ci as ci  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402

FixtureError = ci.FixtureError

BINDING_RECORD_SCHEMA = "slaif-oap-order-binding-v1"
ADMISSION_SCHEMA = "slaif-oap-order-admission-v1"
# The 017-s order keeps the exact historical schema its own
# module wrote; other orders use the shared schema.
_S_ORDER_ID = "017-s"
_S_ADMISSION_SCHEMA = "slaif-017s-admission-v1"

_ORDER_ID_RE = re.compile(r"^[0-9]{3}-[a-z]{1,2}$")
_HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
_RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_ORIGIN_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")
# The FIXED canonical future entries: each has exactly ONE
# unique committed order path it may resolve at (the canonical
# names owned by the runtime-profile module — the accepted
# 017-ab sealed entry, the inert 017-ad native entry and the
# inert 017-af native-PTY qualification entry, which is named
# but grants no authority: its real order, namespace, admission
# and owner are a later separately authorized round).  A
# pattern-matching FOREIGN name for one of these ids is a
# closed refusal before any admission or owner adoption; every
# other (generic) order keeps the exact historical pattern law.
_CANONICAL_ORDER_PATHS: dict[str, str] = {
    rprofile.AB_ORDER_ID: rprofile.AB_ORDER_PATH,
    rprofile.AD_ORDER_ID: rprofile.AD_ORDER_PATH,
    rprofile.AF_ORDER_ID: rprofile.AF_ORDER_PATH,
}
_IDENT_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$")
_ORDER_NAME_RE_TPL = r"{oid}-[a-z0-9][a-z0-9._-]*\.md"

_GIT_OUTPUT_MAX = 1 << 20
_GIT_TIMEOUT_SECONDS = 60.0
_ADMISSION_READ_CAP = 8192
_ACTIVE_READ_CAP = 4096
_ORDER_READ_CAP = 1 << 20
_ADMISSION_STATUSES = ("running", "pass", "fail", "aborted")
_ADMISSION_DIR = ".oap-local"
_ADMISSION_EXCLUDE_LINE = ".oap-local/"
_MAX_ATTEMPTS = 8

# -- closed failure-reason vocabulary ------------------------------------------
BIND_REASONS = frozenset(
    {
        "bind-order-id-invalid",
        "bind-head-invalid",
        "bind-git-argv",
        "bind-git-timeout",
        "bind-git-output-overbound",
        "bind-git-failed",
        "bind-head-mismatch",
        "bind-head-drift",
        "bind-worktree-dirty",
        "bind-active-missing",
        "bind-active-object",
        "bind-active-mismatch",
        "bind-active-drift",
        "bind-active-committed-mismatch",
        "bind-order-ambiguous",
        "bind-order-path-mismatch",
        "bind-order-missing",
        "bind-order-object",
        "bind-order-bytes",
        "bind-origin-untrusted",
        "bind-repo-identity-mismatch",
        "bind-admission-env",
        "bind-admission-untrusted",
        "bind-admission-malformed",
        "bind-attempt-exhausted",
    }
)


@dataclass(frozen=True)
class OrderRunBinding:
    """The immutable binding of one explicit opted-in run to its
    exact active order, unique committed order file, literal
    source head, repository identity and module-minted run
    identity.  A frozen value: it is passed to the later
    preparation, never mutated, and never re-minted by a changed
    head, directory or phase."""

    order_id: str
    order_path: str
    order_sha256: str
    active_bytes: bytes
    source_head: str
    repo_identity: str
    run_id: str

    def to_record(self) -> dict[str, str]:
        """The closed JSON representation later records embed
        (the active bytes are hashed, never copied raw)."""
        return {
            "record": BINDING_RECORD_SCHEMA,
            "order_id": self.order_id,
            "order_path": self.order_path,
            "order_sha256": self.order_sha256,
            "active_sha256": hashlib.sha256(self.active_bytes).hexdigest(),
            "source_head": self.source_head,
            "repo_identity": self.repo_identity,
            "run_id": self.run_id,
        }


def _validate_order_id(order_id: object) -> str:
    if not isinstance(order_id, str) or _ORDER_ID_RE.fullmatch(order_id) is None:
        raise FixtureError("bind-order-id-invalid")
    return order_id


def parse_repo_identity(origin_url: str) -> str:
    """Closed origin grammar: exactly the plain HTTPS GitHub
    ``owner/repo`` form (optional ``.git``).  Any other host,
    scheme or form — including private endpoints — is refused,
    and only the normalized ``owner/repo`` is ever returned (the
    URL itself is neither retained nor echoed)."""
    if not isinstance(origin_url, str):
        raise FixtureError("bind-origin-untrusted")
    match = _ORIGIN_RE.fullmatch(origin_url.strip())
    if match is None:
        raise FixtureError("bind-origin-untrusted")
    owner, repo = match.group(1).lower(), match.group(2).lower()
    if _IDENT_RE.fullmatch(owner) is None or _IDENT_RE.fullmatch(repo) is None:
        raise FixtureError("bind-origin-untrusted")
    return f"{owner}/{repo}"


# -- bounded read-only git opt-in ------------------------------------------------
# These queries run BEFORE any later fixture deadline/ledger
# exists, so they carry their OWN finite bounds (exact read-only
# grammar, a capped and time-bounded output read, a bounded
# wait).  No shell; the child is reaped and its stream closed on
# EVERY exit; any failure is a fixed closed token.


def _git_query(git: Callable[[list[str], Path], bytes], repo: Path, args: tuple[str, ...]) -> bytes:
    """Closed argv grammar: only the exact read-only forms this
    module needs, with the bound head (40-hex, validated by the
    caller) embedded in the tree/show refs."""
    if args in (("rev-parse", "HEAD"), ("status", "--porcelain"), ("remote", "get-url", "origin")):
        return git(list(args), repo)
    if (
        len(args) == 3
        and args[0] == "ls-tree"
        and args[1] == "--name-only"
        and re.fullmatch(r"[0-9a-f]{40}:oap/orders", args[2]) is not None
    ):
        return git(list(args), repo)
    if (
        len(args) == 2
        and args[0] == "show"
        and re.fullmatch(r"[0-9a-f]{40}:oap/orders/[a-z0-9][a-z0-9._-]*\.md", args[1]) is not None
    ):
        return git(list(args), repo)
    if (
        len(args) == 2
        and args[0] == "show"
        and re.fullmatch(r"[0-9a-f]{40}:oap/active", args[1]) is not None
    ):
        return git(list(args), repo)
    raise FixtureError("bind-git-argv")


def _git_default(args: list[str], repo: Path, _binary: bool = False) -> bytes:
    """Bounded read-only git query: exact argv, a capped AND
    time-bounded output read (a longer or a HUNG response is
    killed — never hashed truncated, never waited on forever)
    and a bounded wait.  The child is reaped and its stream
    closed on every exit (success, timeout, cap or read error)
    — no zombie, no held pipe — and any failure is a fixed
    closed token."""
    proc = subprocess.Popen(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    stream = proc.stdout
    data = b""
    try:
        if stream is not None:
            budget_end = time.monotonic() + _GIT_TIMEOUT_SECONDS
            while True:
                remaining = budget_end - time.monotonic()
                if remaining <= 0:
                    raise FixtureError("bind-git-timeout")
                ready, _, _ = select.select([stream], [], [], min(remaining, 5.0))
                if not ready:
                    continue
                chunk = os.read(stream.fileno(), min(65536, _GIT_OUTPUT_MAX + 1 - len(data)))
                if not chunk:
                    break
                data += chunk
                if len(data) > _GIT_OUTPUT_MAX:
                    raise FixtureError("bind-git-output-overbound")
        try:
            proc.wait(timeout=max(1.0, budget_end - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise FixtureError("bind-git-timeout") from None
    except FixtureError:
        raise
    except (OSError, subprocess.TimeoutExpired):
        raise FixtureError("bind-git-failed") from None
    finally:
        try:
            proc.kill()
        except OSError:
            pass
        try:
            proc.wait(timeout=5.0)
        except (OSError, subprocess.TimeoutExpired):
            pass
        if stream is not None:
            try:
                stream.close()
            except OSError:
                pass
    if proc.returncode != 0:
        raise FixtureError("bind-git-failed")
    return data


def _read_owned_regular(path: Path, cap: int, reason: str) -> bytes:
    """Bounded read of an exact owned regular file: lstat-checked
    (regular, NOT a link, this uid, size within the cap), opened
    NO-FOLLOW, and the descriptor re-verified (same device/inode,
    still regular, still within the cap) BEFORE reading — a
    replaced, special or foreign object cannot bypass the git
    output/time bounds or pin a blocking special-file read.  A
    longer file is rejected, never truncated into an accepted
    object."""
    try:
        st = os.lstat(path)
    except OSError:
        raise FixtureError(
            "bind-active-missing" if reason == "bind-active-object" else "bind-order-missing"
        ) from None
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_size > cap:
        raise FixtureError(reason)
    try:
        # NON-BLOCKING no-follow open: a replacement by a FIFO or
        # other special object between the lstat and the open must
        # not be able to pin this read; the descriptor is validated
        # (fstat identity + regular) before any read.
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    except OSError:
        raise FixtureError(reason) from None
    data = b""
    try:
        ost = os.fstat(fd)
        if (
            not stat.S_ISREG(ost.st_mode)
            or ost.st_dev != st.st_dev
            or ost.st_ino != st.st_ino
            or ost.st_size > cap
        ):
            raise FixtureError(reason)
        while len(data) <= cap:
            chunk = os.read(fd, min(65536, cap + 1 - len(data)))
            if not chunk:
                break
            data += chunk
    except OSError:
        raise FixtureError(reason) from None
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
    if len(data) > cap:
        raise FixtureError(reason)
    return data


def _committed_active(
    git: Callable[[list[str], Path], bytes], repo: Path, head: str
) -> bytes | None:
    """The bounded COMMITTED oap/active bytes at the bound head
    (explicit content query — a clean-status observation alone is
    not content binding; an assume-unchanged index would hide a
    disk/commit divergence).  A missing committed file is the
    honest None, not a transport failure; overbound/timeout
    tokens stay distinct and propagate."""
    try:
        return _git_query(git, repo, ("show", f"{head}:oap/active"))
    except FixtureError as exc:
        if str(exc) == "bind-git-failed":
            return None
        raise


def resolve_order_binding(
    repo: object,
    order_id: object,
    bind_head: object,
    git_runner: Callable[[list[str], Path], bytes] | None = None,
) -> OrderRunBinding:
    """Resolve the immutable binding for one explicit opted-in
    run, read-only.  Every mismatch is a fixed closed refusal;
    nothing is written and no attempt is minted.  ``repo`` is the
    checkout root; ``order_id`` the active OAP id; ``bind_head``
    the literal 40-hex source head the run is bound to.

    The active order is bound as CONTENT, both ways: the disk
    ``oap/active`` must be exactly ``<id>\\n`` AND the committed
    ``oap/active`` at the bound head must be byte-identical —
    clean status alone is not content binding (an
    assume-unchanged index would hide a disk/commit divergence).

    The run identity (32-hex) is minted here by the module from
    a fresh uuid4 — a caller can neither supply it nor mint
    authority by any order string, readiness boolean, arbitrary
    filename or new directory."""
    repo_path = Path(str(repo))
    git = git_runner if git_runner is not None else _git_default
    oid = _validate_order_id(order_id)
    if not isinstance(bind_head, str) or _HEAD_RE.fullmatch(bind_head) is None:
        raise FixtureError("bind-head-invalid")
    head = _git_query(git, repo_path, ("rev-parse", "HEAD")).decode("ascii", "replace").strip()
    if head != bind_head:
        raise FixtureError("bind-head-mismatch")
    status = _git_query(git, repo_path, ("status", "--porcelain")).decode("ascii", "replace")
    if status.strip() != "":
        raise FixtureError("bind-worktree-dirty")
    active = _read_owned_regular(
        repo_path / "oap" / "active", _ACTIVE_READ_CAP, "bind-active-object"
    )
    if active != oid.encode("ascii") + b"\n":
        raise FixtureError("bind-active-mismatch")
    committed = _committed_active(git, repo_path, bind_head)
    if committed != active:
        raise FixtureError("bind-active-committed-mismatch")
    try:
        listing = _git_query(
            git, repo_path, ("ls-tree", "--name-only", f"{bind_head}:oap/orders")
        ).decode("ascii", "replace")
    except FixtureError as exc:
        # A missing oap/orders tree at the bound head is zero
        # matches (ambiguous), not a git transport failure: the
        # overbound/timeout tokens stay distinct and propagate.
        if str(exc) != "bind-git-failed":
            raise
        listing = ""
    pattern = re.compile(_ORDER_NAME_RE_TPL.format(oid=re.escape(oid)))
    matches = [name for name in listing.splitlines() if pattern.fullmatch(name)]
    if len(matches) != 1:
        raise FixtureError("bind-order-ambiguous")
    order_path = "oap/orders/" + matches[0]
    # the fixed canonical future entries resolve ONLY at their
    # own unique committed order path: a foreign pattern-
    # matching name can never mint a canonical binding (a
    # closed refusal BEFORE any admission or owner adoption)
    canonical = _CANONICAL_ORDER_PATHS.get(oid)
    if canonical is not None and order_path != canonical:
        raise FixtureError("bind-order-path-mismatch")
    order_disk = _read_owned_regular(repo_path / order_path, _ORDER_READ_CAP, "bind-order-object")
    order_head = _git_query(git, repo_path, ("show", f"{bind_head}:{order_path}"))
    if hashlib.sha256(order_disk).hexdigest() != hashlib.sha256(order_head).hexdigest():
        raise FixtureError("bind-order-bytes")
    origin = _git_query(git, repo_path, ("remote", "get-url", "origin")).decode("ascii", "replace")
    return OrderRunBinding(
        order_id=oid,
        order_path=order_path,
        order_sha256=hashlib.sha256(order_disk).hexdigest(),
        active_bytes=active,
        source_head=bind_head,
        repo_identity=parse_repo_identity(origin),
        run_id=uuid.uuid4().hex,
    )


def _revalidate_repo_context(
    git: Callable[[list[str], Path], bytes],
    repo_path: Path,
    oid: str,
    binding: OrderRunBinding,
) -> None:
    """Re-verify the ACTUAL repository context against the frozen
    binding at a mutation boundary (admission): HEAD, clean
    worktree, disk AND committed active content, repository
    identity, and the unique committed order file.  A binding is
    only ever admitted in the repository/source/active/order
    context it was resolved from — a stale head, a foreign repo
    or a drifted active/order byte is a closed refusal BEFORE any
    directory or claim mutation.  (The frozen dataclass is data,
    not attestation; the checked context must not be lost between
    resolve and admission.)"""
    head = _git_query(git, repo_path, ("rev-parse", "HEAD")).decode("ascii", "replace").strip()
    if head != binding.source_head:
        raise FixtureError("bind-head-drift")
    status = _git_query(git, repo_path, ("status", "--porcelain")).decode("ascii", "replace")
    if status.strip() != "":
        raise FixtureError("bind-worktree-dirty")
    active = _read_owned_regular(
        repo_path / "oap" / "active", _ACTIVE_READ_CAP, "bind-active-object"
    )
    if active != binding.active_bytes:
        raise FixtureError("bind-active-drift")
    committed = _committed_active(git, repo_path, binding.source_head)
    if committed != binding.active_bytes:
        raise FixtureError("bind-active-committed-mismatch")
    origin = _git_query(git, repo_path, ("remote", "get-url", "origin")).decode("ascii", "replace")
    if parse_repo_identity(origin) != binding.repo_identity:
        raise FixtureError("bind-repo-identity-mismatch")
    listing = _git_query(
        git, repo_path, ("ls-tree", "--name-only", f"{binding.source_head}:oap/orders")
    ).decode("ascii", "replace")
    pattern = re.compile(_ORDER_NAME_RE_TPL.format(oid=re.escape(oid)))
    matches = [name for name in listing.splitlines() if pattern.fullmatch(name)]
    if len(matches) != 1 or "oap/orders/" + matches[0] != binding.order_path:
        raise FixtureError("bind-order-ambiguous")
    order_disk = _read_owned_regular(
        repo_path / binding.order_path, _ORDER_READ_CAP, "bind-order-object"
    )
    if hashlib.sha256(order_disk).hexdigest() != binding.order_sha256:
        raise FixtureError("bind-order-bytes")


# -- per-order stable one-attempt admission namespaces ---------------------------
# The order's ONE authorized attempt is recorded in a stable
# protected file derived from the REPOSITORY and the ORDER
# (never from a caller-selected output/work directory, never
# keyed by the source head): a head change inside the same
# activated order does not reset it.  Admission is an ATOMIC
# EXCLUSIVE CLAIM (an O_EXCL claim file, not a
# read-empty-then-replace race): two concurrent preparers can
# never both admit.


def admission_dir_path(repo: object, order_id: object) -> Path:
    oid = _validate_order_id(order_id)
    return Path(str(repo)) / _ADMISSION_DIR / oid


def admission_path(repo: object, order_id: object) -> Path:
    return admission_dir_path(repo, order_id) / "admission.json"


def claim_path(repo: object, order_id: object) -> Path:
    return admission_dir_path(repo, order_id) / "admission.claim"


def _canonical_schema(order_id: str) -> str:
    return _S_ADMISSION_SCHEMA if order_id == _S_ORDER_ID else ADMISSION_SCHEMA


def _admission_ancestor_ok(path: Path, order_id: str) -> None:
    """Protect the exact owned components this invocation
    creates (and only those): each must be a 0700 regular
    directory owned by this uid; a missing component is created
    fresh 0700.  A pre-existing foreign or group/other-writable
    component is refused — it is never adopted and never
    chmod'd."""
    base = path.parent.parent.parent  # the repository root
    cursor = base
    for component in (_ADMISSION_DIR, order_id):
        cursor = cursor / component
        if cursor.is_symlink():
            raise FixtureError("bind-admission-env")
        if cursor.exists():
            st = os.lstat(cursor)
            if (
                not stat.S_ISDIR(st.st_mode)
                or stat.S_IMODE(st.st_mode) != stat.S_IRWXU
                or st.st_uid != os.getuid()
            ):
                raise FixtureError("bind-admission-env")
        else:
            try:
                os.mkdir(cursor, 0o700)
            except OSError:
                raise FixtureError("bind-admission-env") from None
            st = os.lstat(cursor)
            if (
                not stat.S_ISDIR(st.st_mode)
                or stat.S_IMODE(st.st_mode) != stat.S_IRWXU
                or st.st_uid != os.getuid()
            ):
                raise FixtureError("bind-admission-env")


def _ensure_git_exclude(repo: Path) -> None:
    git_dir = repo / ".git"
    try:
        gst = os.lstat(git_dir)
    except OSError:
        raise FixtureError("bind-admission-env") from None
    if not stat.S_ISDIR(gst.st_mode) or gst.st_uid != os.getuid():
        raise FixtureError("bind-admission-env")
    info_dir = git_dir / "info"
    try:
        ist = os.lstat(info_dir)
    except OSError:
        raise FixtureError("bind-admission-env") from None
    if not stat.S_ISDIR(ist.st_mode) or ist.st_uid != os.getuid():
        raise FixtureError("bind-admission-env")
    exclude = info_dir / "exclude"
    try:
        if exclude.is_symlink() or (exclude.exists() and not exclude.is_file()):
            raise FixtureError("bind-admission-env")
        data = _read_bounded(exclude, _ADMISSION_READ_CAP) if exclude.exists() else b""
    except FixtureError:
        raise
    except OSError:
        raise FixtureError("bind-admission-env") from None
    lines = data.decode("utf-8", "replace").splitlines()
    if any(line.strip() == _ADMISSION_EXCLUDE_LINE for line in lines):
        return
    try:
        fd = os.open(exclude, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as handle:
            if data and not data.endswith(b"\n"):
                handle.write("\n" + _ADMISSION_EXCLUDE_LINE)
            else:
                handle.write(_ADMISSION_EXCLUDE_LINE)
    except OSError:
        raise FixtureError("bind-admission-env") from None


def _read_bounded(path: Path, cap: int) -> bytes:
    """Bounded descriptor read of an exact owned regular file:
    lstat-checked (regular, not a link, size within the cap)
    and opened NO-FOLLOW, then read in chunks capped at
    ``cap + 1`` — a longer file is REJECTED, never silently
    truncated into a shorter accepted object."""
    try:
        st = os.lstat(path)
    except OSError:
        raise FixtureError("bind-admission-malformed") from None
    if not stat.S_ISREG(st.st_mode) or st.st_size > cap:
        raise FixtureError("bind-admission-malformed")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    except OSError:
        raise FixtureError("bind-admission-malformed") from None
    data = b""
    try:
        while len(data) <= cap:
            chunk = os.read(fd, min(65536, cap + 1 - len(data)))
            if not chunk:
                break
            data += chunk
    except OSError:
        raise FixtureError("bind-admission-malformed") from None
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
    if len(data) > cap:
        raise FixtureError("bind-admission-malformed")
    return data


def _claim_owned_file(path: Path, expected_content: bytes) -> bool:
    """Verify a pre-existing claim file is OUR exact 0600 owned
    regular file with the expected content; True when it is."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        return False
    try:
        return path.read_bytes() == expected_content
    except OSError:
        return False


def _validate_record(record: object, order_id: str) -> dict:
    if (
        not isinstance(record, dict)
        or set(record) != {"record", "order", "attempts"}
        or record["record"] != _canonical_schema(order_id)
        or record["order"] != order_id
        or not isinstance(record["attempts"], list)
        or len(record["attempts"]) > _MAX_ATTEMPTS
        or any(
            not isinstance(entry, dict)
            or set(entry) != {"head", "run_id", "status"}
            or not isinstance(entry["head"], str)
            or _HEAD_RE.fullmatch(entry["head"]) is None
            or not isinstance(entry["run_id"], str)
            or _RUN_ID_RE.fullmatch(entry["run_id"]) is None
            or entry["status"] not in _ADMISSION_STATUSES
            for entry in record["attempts"]
        )
    ):
        raise FixtureError("bind-admission-malformed")
    return record


def read_admission_record(repo: object, order_id: object) -> dict:
    """Read the order's stable admission record (its canonical
    schema: the historical 017-s schema for 017-s, the shared
    schema for every other order).  A missing record is the
    empty not-yet-admitted state; anything untrusted or
    malformed is a closed refusal."""
    oid = _validate_order_id(order_id)
    path = admission_path(Path(str(repo)), oid)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return {"record": _canonical_schema(oid), "order": oid, "attempts": []}
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("bind-admission-untrusted")
    parent = path.parent
    pst = os.lstat(parent)
    if (
        not stat.S_ISDIR(pst.st_mode)
        or stat.S_IMODE(pst.st_mode) != stat.S_IRWXU
        or pst.st_uid != os.getuid()
    ):
        raise FixtureError("bind-admission-untrusted")
    try:
        raw = _read_bounded(path, _ADMISSION_READ_CAP)
        record = json.loads(raw.decode("ascii"))
    except (ValueError, UnicodeDecodeError, OSError):
        raise FixtureError("bind-admission-malformed") from None
    return _validate_record(record, oid)


def _write_admission(path: Path, record: dict) -> None:
    _admission_ancestor_ok(path, str(record["order"]))
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise FixtureError("bind-admission-malformed") from None
    st = path.lstat()
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("bind-admission-untrusted")


def _release_claim(repo: Path, order_id: str, run_id: str) -> None:
    """Release the exclusive claim ONLY when it is still our
    exact owned 0600 file carrying our run id (never a foreign
    object)."""
    claim = claim_path(repo, order_id)
    if _claim_owned_file(claim, run_id.encode("ascii")):
        try:
            os.unlink(claim)
        except OSError:
            pass


def admit_order_attempt(
    repo: object,
    order_id: object,
    binding: OrderRunBinding,
    git_runner: Callable[[list[str], Path], bytes] | None = None,
) -> None:
    """ATOMICALLY ADMIT the one authorized attempt for this
    order (the experiment boundary): an O_EXCL claim is won
    before the admission record is read, so two concurrent
    preparers can never both admit.  A claim left by a run that
    already reached a TERMINAL record is stale (crash between
    the terminal record and the release) and is re-claimed
    exactly once; any other pre-existing claim or any
    previously admitted attempt — pass, fail, aborted or still
    running — exhausts the order's one attempt.  BEFORE any
    directory or claim mutation the ACTUAL repository context is
    re-validated against the binding (HEAD, worktree, disk and
    committed active, repository identity, unique order file and
    its bytes): a binding resolved elsewhere, or in a now-stale
    head, is refused.  A changed head, directory or phase never
    resets the namespace: the record is keyed by the order, and
    one-attempt exhaustion survives later heads."""
    oid = _validate_order_id(order_id)
    if not isinstance(binding, OrderRunBinding) or binding.order_id != oid:
        raise FixtureError("bind-order-id-invalid")
    repo_path = Path(str(repo))
    git = git_runner if git_runner is not None else _git_default
    _revalidate_repo_context(git, repo_path, oid, binding)
    path = admission_path(repo_path, oid)
    _admission_ancestor_ok(path, oid)
    claim = claim_path(repo_path, oid)
    run_id = binding.run_id
    for attempt in (1, 2):
        try:
            fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if attempt == 2:
                raise FixtureError("bind-attempt-exhausted") from None
            try:
                claimed_run_id = _read_bounded(claim, 64).decode("ascii").strip()
            except (OSError, ValueError, UnicodeDecodeError):
                raise FixtureError("bind-attempt-exhausted") from None
            if _RUN_ID_RE.fullmatch(claimed_run_id) is None:
                raise FixtureError("bind-attempt-exhausted") from None
            record = read_admission_record(repo_path, oid)
            terminal = any(
                entry["run_id"] == claimed_run_id and entry["status"] in ("pass", "fail", "aborted")
                for entry in record["attempts"]
            )
            if not terminal or not _claim_owned_file(claim, claimed_run_id.encode("ascii")):
                raise FixtureError("bind-attempt-exhausted") from None
            try:
                os.unlink(claim)
            except OSError:
                raise FixtureError("bind-attempt-exhausted") from None
            continue
        with os.fdopen(fd, "wb") as handle:
            handle.write(run_id.encode("ascii"))
        break
    else:
        raise FixtureError("bind-attempt-exhausted")
    try:
        record = read_admission_record(repo_path, oid)
        if record["attempts"]:
            raise FixtureError("bind-attempt-exhausted")
        _ensure_git_exclude(repo_path)
        _write_admission(
            path,
            {
                "record": _canonical_schema(oid),
                "order": oid,
                "attempts": [{"head": binding.source_head, "run_id": run_id, "status": "running"}],
            },
        )
    except BaseException:
        # The claim was won but the attempt was not admitted:
        # release it so a later invocation can claim cleanly.
        _release_claim(repo_path, oid, run_id)
        raise


def record_order_attempt(repo: object, order_id: object, run_id: str, status: str) -> str:
    """Finalize the admitted attempt's terminal outcome (honest
    preservation: a failed or aborted attempt stays recorded),
    then release the exclusive claim (terminal record first,
    release second — a crash between them leaves a reclaimable
    stale claim, never a double-admission).

    Terminal and historical records are IMMUTABLE: only the
    FIRST running-to-terminal finalization of an admitted run is
    written.  A later or mismatched finalization — including any
    rewrite of an already-terminal outcome in the historical
    017-s ledger — is a closed no-op refusal: it never rewrites
    prior evidence and never hides a failure.  Returns the
    closed token ``"finalized" | "terminal-preserved" |
    "not-running" | "record-unreadable"``.  The journal is
    evidence, not a gate on cleanup: a journal failure after the
    run converged never masks the primary outcome (an unreadable
    record is reported by token, not raised)."""
    oid = _validate_order_id(order_id)
    if not isinstance(run_id, str) or _RUN_ID_RE.fullmatch(run_id) is None:
        raise FixtureError("bind-admission-malformed")
    if status not in ("pass", "fail", "aborted"):
        raise FixtureError("bind-admission-malformed")
    repo_path = Path(str(repo))
    try:
        path = admission_path(repo_path, oid)
        record = read_admission_record(repo_path, oid)
    except FixtureError:
        _release_claim(repo_path, oid, run_id)
        return "record-unreadable"
    result = "not-running"
    changed = False
    for entry in record["attempts"]:
        if entry["run_id"] == run_id:
            if entry["status"] == "running":
                entry["status"] = status
                changed = True
                result = "finalized"
            else:
                # already terminal (or a historical record):
                # immutable — no rewrite, no hidden failure
                result = "terminal-preserved"
            break
    if changed:
        _write_admission(path, record)
    _release_claim(repo_path, oid, run_id)
    return result


def admission_exhausted(repo: object, order_id: object) -> bool:
    """True when this order's ONE attempt is already admitted
    (any status) or a live/foreign claim blocks admission;
    malformed or untrusted records are refused, not read as
    not-exhausted."""
    oid = _validate_order_id(order_id)
    repo_path = Path(str(repo))
    record = read_admission_record(repo_path, oid)
    if record["attempts"]:
        return True
    return claim_path(repo_path, oid).exists()


__all__ = [
    "ADMISSION_SCHEMA",
    "BINDING_RECORD_SCHEMA",
    "BIND_REASONS",
    "FixtureError",
    "OrderRunBinding",
    "admission_dir_path",
    "admission_exhausted",
    "admission_path",
    "admit_order_attempt",
    "claim_path",
    "parse_repo_identity",
    "read_admission_record",
    "record_order_attempt",
    "resolve_order_binding",
]
