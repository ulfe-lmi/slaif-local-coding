"""Bounded, disposable, content-addressed derived-index cache.

The cache stores validated indexes only.  It never stores source bytes,
compiler prompts, model prose beyond the validated index, credentials, images,
or request bodies.  A cache miss or damaged entry is always safe: callers must
retain the original governance-bearing request.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from prometheus_client import CollectorRegistry, Counter, Gauge
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .compiler_models import CompiledIndex, ConstitutionalClass

CACHE_SCHEMA_VERSION = "derived-cache-v2"
_KEY_FILENAME_LENGTH = 64


class CacheIdentity(BaseModel):
    """Opaque, pre-hashed identity fields; raw external credentials are forbidden."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    principal: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    session: str | None = Field(default=None, min_length=1, max_length=256)
    repository: str | None = Field(default=None, min_length=1, max_length=256)


@dataclass(frozen=True)
class CachePolicy:
    root: Path
    fallback_root: Path | None
    max_total_bytes: int
    max_entry_bytes: int
    max_pinned_bytes: int
    max_entries: int
    ttl_seconds: float
    max_scan_entries: int

    @property
    def valid(self) -> bool:
        return (
            self.max_entry_bytes > 0
            and self.max_entry_bytes <= self.max_total_bytes
            and self.max_pinned_bytes > 0
            and self.max_pinned_bytes <= self.max_total_bytes
            and self.max_entries > 0
            and self.ttl_seconds > 0
            and self.max_scan_entries > 0
        )


@dataclass(frozen=True)
class CacheReadResult:
    index: CompiledIndex | None
    outcome: Literal["hit", "miss", "disabled", "corrupt", "expired", "permission", "unavailable"]
    detail: str = ""


@dataclass(frozen=True)
class CacheWriteResult:
    outcome: Literal["written", "too-large", "unavailable", "io-failed", "disabled"]
    detail: str = ""
    bytes_written: int = 0


@dataclass(frozen=True)
class _EntryMetadata:
    path: Path
    key: str
    size: int
    created_at: float
    pinned: bool


class CacheUnavailableError(RuntimeError):
    """Raised internally when no permitted cache root can be prepared."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def cache_key(
    identity: CacheIdentity,
    *,
    source_logical_path: str,
    source_sha256: str,
    model: str,
    index_schema_version: str,
    compiler_version: str,
    prompt_policy_version: str,
    reasoning_effort: str,
    max_source_bytes: int,
    max_prompt_bytes: int,
    max_output_tokens: int,
    max_output_bytes: int,
    max_candidates: int,
    max_json_depth: int,
) -> str:
    """Build a collision-resistant logical key with every isolation dimension."""
    if not identity.session or not identity.repository:
        raise ValueError("persistent cache requires reliable session and repository identity")
    material = {
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "compiler_version": compiler_version,
        "index_schema_version": index_schema_version,
        "max_candidates": max_candidates,
        "max_json_depth": max_json_depth,
        "max_output_bytes": max_output_bytes,
        "max_output_tokens": max_output_tokens,
        "max_prompt_bytes": max_prompt_bytes,
        "max_source_bytes": max_source_bytes,
        "model": model,
        "principal": identity.principal,
        "prompt_policy_version": prompt_policy_version,
        "reasoning_effort": reasoning_effort,
        "repository": identity.repository,
        "route": identity.route,
        "session": identity.session,
        "source_logical_path": source_logical_path,
        "source_sha256": source_sha256,
    }
    return hashlib.sha256(_canonical_bytes(material)).hexdigest()


def _entry_time(envelope: dict[str, object]) -> float:
    value = envelope.get("created_at")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("invalid cache timestamp")
    return float(value)


def _trusted_path(path: Path, *, directory: bool) -> bool:
    """Check type, owner, and mode without following a final symlink."""
    try:
        info = path.lstat()
    except OSError:
        return False
    expected_type = stat.S_IFDIR if directory else stat.S_IFREG
    expected_mode = 0o700 if directory else 0o600
    return (
        stat.S_IFMT(info.st_mode) == expected_type
        and info.st_uid == os.geteuid()
        and info.st_mode & 0o777 == expected_mode
    )


def _safe_prepare(path: Path) -> None:
    """Create or adopt only a real, current-user, private directory."""
    try:
        if (path.exists() or path.is_symlink()) and not _trusted_path(path, directory=True):
            raise CacheUnavailableError("cache root already exists and is not trusted")
        path.mkdir(mode=0o700, parents=False, exist_ok=True)
        os.chmod(path, 0o700)
    except CacheUnavailableError:
        raise
    except OSError as exc:
        raise CacheUnavailableError("cache root could not be prepared") from exc
    if not _trusted_path(path, directory=True):
        raise CacheUnavailableError("cache root is not a current-user private directory")


class DerivedIndexCache:
    """Process-local LRU/TTL view over a private content-addressed directory."""

    def __init__(
        self,
        policy: CachePolicy,
        registry: CollectorRegistry | None = None,
    ) -> None:
        if not policy.valid:
            raise ValueError("invalid cache policy")
        self.policy = policy
        self.registry = registry or CollectorRegistry()
        self._lock = threading.RLock()
        self._entries: OrderedDict[str, _EntryMetadata] = OrderedDict()
        self._bytes = 0
        self._pinned_bytes = 0
        self._available = False
        self._degraded = False
        self._detail = ""
        self._root: Path | None = None
        self.hits = Counter(
            "slaif_constitution_cache_hits_total",
            "Valid derived-index cache hits",
            registry=self.registry,
        )
        self.misses = Counter(
            "slaif_constitution_cache_misses_total",
            "Derived-index cache misses by fixed reason",
            ["reason"],
            registry=self.registry,
        )
        self.writes = Counter(
            "slaif_constitution_cache_writes_total",
            "Derived-index cache write outcomes",
            ["outcome"],
            registry=self.registry,
        )
        self.evictions = Counter(
            "slaif_constitution_cache_evictions_total",
            "Derived-index cache evictions",
            ["pinned"],
            registry=self.registry,
        )
        self.corruption = Counter(
            "slaif_constitution_cache_corruption_total",
            "Corrupt or integrity-failing derived cache entries",
            registry=self.registry,
        )
        self.permission_failures = Counter(
            "slaif_constitution_cache_permission_failures_total",
            "Derived cache permission failures",
            registry=self.registry,
        )
        self.occupancy = Gauge(
            "slaif_constitution_cache_bytes",
            "Derived cache occupancy",
            ["pinned"],
            registry=self.registry,
        )
        self._prepare_roots()
        self._refresh_occupancy()

    @property
    def available(self) -> bool:
        return self._available

    @property
    def degraded(self) -> bool:
        return self._degraded

    @property
    def detail(self) -> str:
        return self._detail

    def _prepare_roots(self) -> None:
        try:
            _safe_prepare(self.policy.root)
            root = self.policy.root
            self._degraded = False
            self._detail = ""
        except (OSError, CacheUnavailableError):
            if self.policy.fallback_root is None:
                self._set_unavailable("primary cache unavailable")
                return
            try:
                _safe_prepare(self.policy.fallback_root)
                root = self.policy.fallback_root
                self._degraded = True
                self._detail = "primary cache unavailable; configured fallback active"
            except (OSError, CacheUnavailableError):
                self._set_unavailable("primary and fallback cache unavailable")
                return
        self._root = root
        self._available = True
        try:
            failure_reason = self._load_existing()
        except OSError:
            failure_reason = "cache inventory is unavailable"
        if failure_reason is not None:
            self._set_unavailable(failure_reason)

    def _set_unavailable(self, detail: str) -> None:
        self._available = False
        self._degraded = False
        self._detail = detail
        self._root = None
        self._entries.clear()
        self._bytes = 0
        self._pinned_bytes = 0

    def _path_for(self, key: str) -> Path:
        assert self._root is not None
        return self._root / key[:2] / f"{key}.json"

    def _load_existing(self) -> str | None:
        """Reconcile a bounded number of restart artifacts; return a fatal reason."""
        assert self._root is not None
        root = self._root
        pending = [root]
        scanned = 0
        discovered: list[tuple[float, Path, int]] = []
        while pending:
            scanned += 1
            if scanned > self.policy.max_scan_entries:
                return "cache startup scan limit exceeded"
            current = pending.pop()
            info = current.lstat()
            if current != root and current.is_symlink():
                current.unlink(missing_ok=True)
                self.corruption.inc()
                continue
            if current != root and current.parent == root and not stat.S_ISDIR(info.st_mode):
                return "cache contains an unrecognized object"
            if stat.S_IFMT(info.st_mode) == stat.S_IFDIR:
                if not _trusted_path(current, directory=True):
                    return "cache contains an untrusted directory"
                pending.extend(current.iterdir())
                continue
            if not stat.S_IFMT(info.st_mode) == stat.S_IFREG:
                return "cache contains an unrecognized object"
            if not _trusted_path(current, directory=False):
                if current.suffix == ".json" or current.name.startswith(".tmp-"):
                    current.unlink(missing_ok=True)
                    self.permission_failures.inc()
                continue
            if current.name.startswith(".tmp-"):
                current.unlink(missing_ok=True)
                self.corruption.inc()
                continue
            if current.suffix != ".json":
                continue
            size = info.st_size
            key = current.stem
            if (
                len(key) != _KEY_FILENAME_LENGTH
                or current.parent.name != key[:2]
                or any(character not in "0123456789abcdef" for character in key)
            ):
                current.unlink(missing_ok=True)
                self.corruption.inc()
                continue
            if self._inspect(current, key, size) is not None:
                discovered.append((info.st_mtime_ns, current, size))
            else:
                current.unlink(missing_ok=True)
        discovered.sort(reverse=True)
        for _, path, _size in discovered[: self.policy.max_entries]:
            key = path.stem
            metadata = self._inspect(path, key, path.stat().st_size)
            assert metadata is not None
            self._insert_metadata(metadata)
        for _, path, _size in discovered[self.policy.max_entries :]:
            path.unlink(missing_ok=True)
        self._enforce_limits()
        return None

    def _inspect(self, path: Path, key: str, size: int) -> _EntryMetadata | None:
        if size > self.policy.max_entry_bytes or not _trusted_path(path, directory=False):
            return None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(envelope, dict) or envelope.get("key") != key:
                return None
            payload = envelope.get("payload")
            index = CompiledIndex.model_validate(payload)
            created = _entry_time(envelope)
            if time.time() - created > self.policy.ttl_seconds:
                return None
            return _EntryMetadata(
                path=path,
                key=key,
                size=size,
                created_at=created,
                pinned=index.effective_class()
                in {ConstitutionalClass.P0_ROOT, ConstitutionalClass.P1_DELEGATED_OR_SECURITY},
            )
        except (OSError, ValueError, TypeError, ValidationError, json.JSONDecodeError):
            return None

    def _insert_metadata(self, metadata: _EntryMetadata) -> None:
        self._entries[metadata.key] = metadata
        self._bytes += metadata.size
        if metadata.pinned:
            self._pinned_bytes += metadata.size

    def _remove(self, key: str, *, expired: bool = False) -> None:
        metadata = self._entries.pop(key, None)
        if metadata is None:
            return
        self._bytes -= metadata.size
        if metadata.pinned:
            self._pinned_bytes -= metadata.size
        if expired:
            self.misses.labels("expired").inc()
            try:
                metadata.path.unlink()
            except OSError:
                self.corruption.inc()
        else:
            self.evictions.labels("true" if metadata.pinned else "false").inc()
            try:
                metadata.path.unlink()
            except OSError:
                self.corruption.inc()

    def _enforce_limits(self) -> None:
        # Evict unpinned entries first, then honor the isolated P0/P1 budget.
        while self._bytes > self.policy.max_total_bytes:
            unpinned = next((key for key, item in self._entries.items() if not item.pinned), None)
            if unpinned is None:
                pinned = next(iter(self._entries), None)
                if pinned is None:
                    break
                self._remove(pinned)
            else:
                self._remove(unpinned)
        while self._pinned_bytes > self.policy.max_pinned_bytes:
            pinned = next((key for key, item in self._entries.items() if item.pinned), None)
            if pinned is None:
                break
            self._remove(pinned)
        while len(self._entries) > self.policy.max_entries:
            self._remove(next(iter(self._entries)))
        self._refresh_occupancy()

    def _refresh_occupancy(self) -> None:
        self.occupancy.labels("true").set(self._pinned_bytes)
        self.occupancy.labels("false").set(self._bytes - self._pinned_bytes)

    def get(self, key: str) -> CacheReadResult:
        if not self._available or self._root is None:
            self.misses.labels("unavailable").inc()
            return CacheReadResult(None, "unavailable", self._detail)
        if len(key) != _KEY_FILENAME_LENGTH or any(
            character not in "0123456789abcdef" for character in key
        ):
            self.misses.labels("miss").inc()
            return CacheReadResult(None, "miss")
        with self._lock:
            if not _trusted_path(self._root, directory=True):
                self._set_unavailable("cache root became untrusted")
                self.misses.labels("unavailable").inc()
                return CacheReadResult(None, "unavailable", self._detail)
            metadata = self._entries.get(key)
            if metadata is None:
                self.misses.labels("miss").inc()
                return CacheReadResult(None, "miss")
            if not _trusted_path(metadata.path.parent, directory=True):
                self._set_unavailable("cache shard became untrusted")
                self.misses.labels("unavailable").inc()
                return CacheReadResult(None, "unavailable", self._detail)
            if not _trusted_path(metadata.path, directory=False):
                self.permission_failures.inc()
                self._remove(key)
                self._refresh_occupancy()
                return CacheReadResult(None, "permission", "entry is not a trusted private file")
            try:
                if time.time() - metadata.created_at > self.policy.ttl_seconds:
                    self._remove(key, expired=True)
                    self._refresh_occupancy()
                    return CacheReadResult(None, "expired")
                raw = metadata.path.read_bytes()
                envelope = json.loads(raw.decode("utf-8"))
                payload = envelope.get("payload")
                payload_bytes = _canonical_bytes(payload)
                expected_hash = envelope.get("payload_sha256")
                actual_hash = hashlib.sha256(payload_bytes).hexdigest()
                if (
                    envelope.get("cache_schema_version") != CACHE_SCHEMA_VERSION
                    or expected_hash != actual_hash
                ):
                    self.corruption.inc()
                    self._remove(key)
                    self._refresh_occupancy()
                    return CacheReadResult(None, "corrupt", "payload integrity check failed")
                index = CompiledIndex.model_validate(payload)
                if index.source_sha256 != payload.get("source_sha256"):
                    self.corruption.inc()
                    self._remove(key)
                    self._refresh_occupancy()
                    return CacheReadResult(None, "corrupt", "index identity mismatch")
            except (
                OSError,
                UnicodeError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
                ValidationError,
            ):
                self.corruption.inc()
                self._remove(key)
                self._refresh_occupancy()
                return CacheReadResult(None, "corrupt", "entry could not be validated")
            self._entries.move_to_end(key)
            self.hits.inc()
            return CacheReadResult(index, "hit")

    def put(self, key: str, index: CompiledIndex) -> CacheWriteResult:
        if not self._available or self._root is None:
            self.writes.labels("unavailable").inc()
            return CacheWriteResult("unavailable", self._detail)
        payload = index.model_dump(mode="json")
        payload_bytes = _canonical_bytes(payload)
        if len(payload_bytes) > self.policy.max_entry_bytes:
            self.writes.labels("too-large").inc()
            return CacheWriteResult("too-large", "validated index exceeds cache entry budget")
        envelope = {
            "cache_schema_version": CACHE_SCHEMA_VERSION,
            "created_at": time.time(),
            "key": key,
            "payload": payload,
            "payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        }
        content = _canonical_bytes(envelope)
        is_pinned = index.effective_class() in {
            ConstitutionalClass.P0_ROOT,
            ConstitutionalClass.P1_DELEGATED_OR_SECURITY,
        }
        with self._lock:
            existing = self._entries.get(key)
            existing_size = existing.size if existing is not None else 0
            existing_pinned_size = existing.size if existing is not None and existing.pinned else 0

            def fits_after_evictions() -> bool:
                while self._bytes - existing_size + len(content) > self.policy.max_total_bytes:
                    candidate = next(
                        (
                            entry_key
                            for entry_key, item in self._entries.items()
                            if entry_key != key and not item.pinned
                        ),
                        None,
                    )
                    if candidate is None:
                        candidate = next(
                            (
                                entry_key
                                for entry_key, item in self._entries.items()
                                if entry_key != key
                            ),
                            None,
                        )
                    if candidate is None:
                        return False
                    self._remove(candidate)
                if is_pinned:
                    while (
                        self._pinned_bytes - existing_pinned_size + len(content)
                        > self.policy.max_pinned_bytes
                    ):
                        candidate = next(
                            (
                                entry_key
                                for entry_key, item in self._entries.items()
                                if entry_key != key and item.pinned
                            ),
                            None,
                        )
                        if candidate is None:
                            return False
                        self._remove(candidate)
                while (
                    len(self._entries) - (1 if existing is not None else 0) + 1
                    > self.policy.max_entries
                ):
                    candidate = next(
                        (entry_key for entry_key in self._entries if entry_key != key), None
                    )
                    if candidate is None:
                        return False
                    self._remove(candidate)
                return True

            if len(content) > self.policy.max_entry_bytes or not fits_after_evictions():
                self.writes.labels("too-large").inc()
                self._refresh_occupancy()
                return CacheWriteResult("too-large", "entry does not fit configured budgets")
        destination = self._path_for(key)
        temporary: int | None = None
        temporary_path: Path | None = None
        try:
            try:
                destination.parent.mkdir(mode=0o700, parents=False, exist_ok=False)
                os.chmod(destination.parent, 0o700)
            except FileExistsError:
                if not _trusted_path(destination.parent, directory=True):
                    raise OSError("cache shard is not a current-user private directory") from None
            if not _trusted_path(destination.parent, directory=True):
                raise OSError("cache shard is not a current-user private directory")
            file_descriptor, temporary_file = tempfile.mkstemp(
                prefix=".tmp-", suffix=".json", dir=destination.parent
            )
            temporary = file_descriptor
            temporary_path = Path(temporary_file)
            os.fchmod(file_descriptor, 0o600)
            with os.fdopen(file_descriptor, "wb") as stream:
                temporary = None
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            assert temporary_path is not None
            if not _trusted_path(temporary_path, directory=False):
                raise OSError("temporary cache file is untrusted")
            os.replace(temporary_path, destination)
            if not _trusted_path(destination, directory=False):
                raise OSError("cache entry is not trusted after atomic replace")
            try:
                directory_fd = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            except OSError:
                # The rename itself is durable enough for a disposable cache.
                pass
        except OSError:
            if temporary is not None:
                os.close(temporary)
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass
            self.writes.labels("io-failed").inc()
            return CacheWriteResult("io-failed", "atomic cache write failed")
        metadata = _EntryMetadata(
            path=destination,
            key=key,
            size=len(content),
            created_at=_entry_time(envelope),
            pinned=is_pinned,
        )
        with self._lock:
            self._remove(key)
            self._insert_metadata(metadata)
            self._enforce_limits()
        self.writes.labels("written").inc()
        return CacheWriteResult("written", bytes_written=len(content))

    def purge(self) -> int:
        """Remove only this cache's derived JSON entries; source truth is untouched."""
        removed = 0
        with self._lock:
            assert self._root is not None
            for path in tuple(self._root.rglob("*")):
                try:
                    info = path.lstat()
                except OSError:
                    self.corruption.inc()
                    continue
                if stat.S_IFMT(info.st_mode) != stat.S_IFREG:
                    continue
                if path.suffix != ".json" and not path.name.startswith(".tmp-"):
                    continue
                try:
                    path.unlink()
                    removed += 1
                except OSError:
                    self.corruption.inc()
            for directory in tuple(self._root.rglob("*")):
                try:
                    info = directory.lstat()
                except OSError:
                    self.corruption.inc()
                    continue
                if stat.S_IFMT(info.st_mode) != stat.S_IFDIR:
                    continue
                try:
                    directory.rmdir()
                except OSError:
                    # Non-empty means an unrelated file was present; leave it.
                    pass
            self._entries.clear()
            self._bytes = 0
            self._pinned_bytes = 0
            self._refresh_occupancy()
        return removed
