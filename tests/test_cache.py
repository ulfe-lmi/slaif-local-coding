"""Isolation, disposal, integrity, and budget tests for the derived cache."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.constitution.cache import (
    CacheIdentity,
    CachePolicy,
    DerivedIndexCache,
    cache_key,
)
from tests.test_compiler import SECRET_MARKER, SOURCE, dependency, identity, index


def policy(root: Path, **changes: Any) -> CachePolicy:
    values: dict[str, Any] = {
        "root": root,
        "fallback_root": None,
        "max_total_bytes": 1_000_000,
        "max_entry_bytes": 1_000_000,
        "max_pinned_bytes": 1_000_000,
        "max_entries": 16,
        "ttl_seconds": 60,
        "max_scan_entries": 64,
    }
    values.update(changes)
    return CachePolicy(**values)


def key_for(
    cache_index: Any, source: bytes = SOURCE, cache_identity: CacheIdentity | None = None
) -> str:
    return cache_key(
        cache_identity or identity(),
        source_logical_path=cache_index.source_logical_path,
        source_sha256=hashlib.sha256(source).hexdigest(),
        model=cache_index.model,
        index_schema_version=cache_index.schema_version,
        compiler_version=cache_index.compiler_version,
        prompt_policy_version=cache_index.prompt_policy_version,
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_bytes=256_000,
        max_candidates=128,
        max_json_depth=24,
    )


def bounds(**changes: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "reasoning_effort": "low",
        "max_source_bytes": 262_144,
        "max_prompt_bytes": 384_000,
        "max_output_tokens": 3000,
        "max_output_bytes": 256_000,
        "max_candidates": 128,
        "max_json_depth": 24,
    }
    values.update(changes)
    return values


def write_cache(root: Path, **policy_changes: Any) -> DerivedIndexCache:
    clock = policy_changes.pop("clock", None)
    cache = DerivedIndexCache(policy(root, **policy_changes), clock=clock)
    result = cache.put(key_for(index()), index())
    assert result.outcome == "written"
    return cache


class ControlledClock:
    """Explicit wall-clock test boundary with controlled advancement."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_atomic_private_write_payload_integrity_and_hit(tmp_path: Path) -> None:
    cache = write_cache(tmp_path / "private")
    path = next((tmp_path / "private").rglob("*.json"))
    assert os.stat(path).st_mode & 0o777 == 0o600
    for parent in path.parents:
        if parent == tmp_path:
            break
        assert parent.stat().st_mode & 0o777 == 0o700
    read = cache.get(key_for(index()))
    assert read.index is not None and read.outcome == "hit"
    envelope = json.loads(path.read_text())
    assert "prompt" not in envelope and SECRET_MARKER not in path.read_text()


def test_invalid_cache_key_cannot_escape_shard_layout(tmp_path: Path) -> None:
    cache = DerivedIndexCache(policy(tmp_path / "key-boundary"))
    result = cache.put("../outside", index())
    assert result.outcome == "invalid"
    assert not (tmp_path / "outside").exists()


def test_all_identity_source_and_policy_dimensions_isolate_entries(tmp_path: Path) -> None:
    base = key_for(index())
    changes: list[tuple[str, Any]] = [
        ("principal", "other"),
        ("route", "other"),
        ("session", "other"),
        ("repository", "other"),
    ]
    isolated_keys = [base]
    for field, value in changes:
        isolated_keys.append(key_for(index(), cache_identity=identity(**{field: value})))
    isolated_keys.extend(
        [
            cache_key(
                identity(),
                source_logical_path="OTHER.md",
                source_sha256="1" * 64,
                model="m",
                index_schema_version="i",
                compiler_version="c",
                prompt_policy_version="p",
                **bounds(max_output_tokens=1),
            ),
            cache_key(
                identity(),
                source_logical_path="AGENTS.md",
                source_sha256="2" * 64,
                model="other",
                index_schema_version="constitution-index-v1",
                compiler_version="compiler-v2",
                prompt_policy_version="constitutional-rank-v2",
                **bounds(),
            ),
            cache_key(
                identity(),
                source_logical_path="AGENTS.md",
                source_sha256=hashlib.sha256(SOURCE).hexdigest(),
                model="test-model",
                index_schema_version="other",
                compiler_version="compiler-v2",
                prompt_policy_version="constitutional-rank-v2",
                **bounds(),
            ),
            cache_key(
                identity(),
                source_logical_path="AGENTS.md",
                source_sha256=hashlib.sha256(SOURCE).hexdigest(),
                model="test-model",
                index_schema_version="constitution-index-v1",
                compiler_version="other",
                prompt_policy_version="constitutional-rank-v2",
                **bounds(),
            ),
            cache_key(
                identity(),
                source_logical_path="AGENTS.md",
                source_sha256=hashlib.sha256(SOURCE).hexdigest(),
                model="test-model",
                index_schema_version="constitution-index-v1",
                compiler_version="compiler-v2",
                prompt_policy_version="other",
                **bounds(),
            ),
            cache_key(
                identity(),
                source_logical_path="AGENTS.md",
                source_sha256=hashlib.sha256(SOURCE).hexdigest(),
                model="test-model",
                index_schema_version="constitution-index-v1",
                compiler_version="compiler-v2",
                prompt_policy_version="constitutional-rank-v2",
                **bounds(max_output_tokens=2999),
            ),
        ]
    )
    assert len(set(isolated_keys)) == len(isolated_keys)
    with pytest.raises(ValueError, match="session"):
        cache_key(
            CacheIdentity(principal="p", route="r"),
            source_logical_path="AGENTS.md",
            source_sha256=hashlib.sha256(SOURCE).hexdigest(),
            model="test-model",
            index_schema_version="i",
            compiler_version="c",
            prompt_policy_version="p",
            **bounds(max_output_tokens=1),
        )


def test_ttl_expiry_corruption_and_permission_failures_are_misses(tmp_path: Path) -> None:
    root = tmp_path / "ttl"
    clock = ControlledClock()
    cache = write_cache(root, ttl_seconds=10.0, clock=clock)
    key = key_for(index())
    assert cache.get(key).outcome == "hit"
    clock.advance(9.999)
    assert cache.get(key).outcome == "hit"
    clock.advance(0.002)
    assert cache.get(key).outcome == "expired"
    assert not list(root.rglob("*.json"))

    cache = write_cache(tmp_path / "corrupt")
    path = next((tmp_path / "corrupt").rglob("*.json"))
    path.write_text("{truncated")
    assert cache.get(key_for(index())).outcome == "corrupt"

    cache = write_cache(tmp_path / "permissions")
    path = next((tmp_path / "permissions").rglob("*.json"))
    path.chmod(0o644)
    read = cache.get(key_for(index()))
    assert read.outcome == "permission"


def test_payload_tampering_is_integrity_failure_not_valid_data(tmp_path: Path) -> None:
    cache = write_cache(tmp_path / "tamper")
    path = next((tmp_path / "tamper").rglob("*.json"))
    envelope = json.loads(path.read_text())
    payload = envelope["payload"]
    payload["summary"] += " tampered"
    path.write_text(json.dumps(envelope))
    assert cache.get(key_for(index())).outcome == "corrupt"


def test_per_entry_total_lru_and_pinned_budgets(tmp_path: Path) -> None:
    small = index()
    cache = DerivedIndexCache(policy(tmp_path / "entry", max_entry_bytes=10))
    assert cache.put(key_for(small), small).outcome == "too-large"

    root = tmp_path / "lru"
    first_cache = DerivedIndexCache(policy(root))
    first_source = SOURCE + b"\nFirst unpinned synthetic source.\n"
    first_index = index(
        first_source,
        source_sha256=hashlib.sha256(first_source).hexdigest(),
        source_byte_length=len(first_source),
        dependencies=(dependency(classification="P4"),),
    )
    first_result = first_cache.put(key_for(first_index, first_source), first_index)
    assert first_result.outcome == "written"
    total = first_result.bytes_written
    evicting = DerivedIndexCache(
        policy(
            root,
            max_total_bytes=total + 128,
            max_entry_bytes=total + 128,
            max_pinned_bytes=total + 128,
            max_entries=1,
        )
    )
    background_source = SOURCE + b"\nSecond unpinned synthetic source.\n"
    background = index(
        background_source,
        source_sha256=hashlib.sha256(background_source).hexdigest(),
        source_byte_length=len(background_source),
        dependencies=(dependency(classification="P4"),),
    )
    # The new entry forces eviction of the older unpinned item.
    second_result = evicting.put(key_for(background, background_source), background)
    assert second_result.outcome == "written"
    assert evicting.get(key_for(first_index, first_source)).outcome == "miss"
    assert evicting.get(key_for(background, background_source)).outcome == "hit"

    oversized_summary = "x" * 1_900
    oversized = index(summary=oversized_summary)
    bounded = DerivedIndexCache(
        policy(
            tmp_path / "total",
            max_total_bytes=2_500,
            max_entry_bytes=2_500,
            max_pinned_bytes=2_500,
        )
    )
    assert bounded.put(key_for(oversized), oversized).outcome == "too-large"

    pinned_root = tmp_path / "pinned"
    pinned_cache = DerivedIndexCache(
        policy(
            pinned_root,
            max_total_bytes=first_result.bytes_written + 128,
            max_entry_bytes=first_result.bytes_written + 128,
            max_pinned_bytes=first_result.bytes_written + 128,
        )
    )
    assert pinned_cache.put(key_for(small), small).outcome == "written"
    assert pinned_cache.get(key_for(small)).outcome == "hit"
    replacement = index(summary="Another bounded synthetic summary.")
    replacement_key = cache_key(
        identity(session="replacement"),
        source_logical_path=replacement.source_logical_path,
        source_sha256=replacement.source_sha256,
        model=replacement.model,
        index_schema_version=replacement.schema_version,
        compiler_version=replacement.compiler_version,
        prompt_policy_version=replacement.prompt_policy_version,
        **bounds(),
    )
    assert pinned_cache.put(replacement_key, replacement).outcome == "written"
    assert pinned_cache.get(key_for(small)).outcome == "miss"
    assert pinned_cache.get(replacement_key).outcome == "hit"


def test_primary_unavailable_uses_explicitly_degraded_fallback(tmp_path: Path) -> None:
    primary = tmp_path / "missing-parent" / "root"
    fallback = tmp_path / "fallback"
    cache = DerivedIndexCache(policy(primary, fallback_root=fallback))
    assert cache.available and cache.degraded
    key = key_for(index())
    assert cache.put(key, index()).outcome == "written"
    assert cache.get(key).outcome == "hit"
    assert any(fallback.rglob("*.json"))


def test_symlinked_primary_is_rejected_and_protected_fallback_is_used(tmp_path: Path) -> None:
    hostile_target = tmp_path / "hostile-target"
    hostile_target.mkdir(mode=0o700)
    primary = tmp_path / "primary"
    primary.symlink_to(hostile_target, target_is_directory=True)
    fallback = tmp_path / "protected-fallback"
    cache = DerivedIndexCache(policy(primary, fallback_root=fallback))
    assert cache.available and cache.degraded
    assert cache.put(key_for(index()), index()).outcome == "written"
    assert not any(hostile_target.iterdir())
    assert any(fallback.rglob("*.json"))


def test_foreign_owned_primary_is_rejected_without_adopting_untrusted_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    foreign_uid = os.geteuid() + 1
    primary = tmp_path / "primary"
    primary.mkdir(mode=0o700)
    untrusted_fallback = tmp_path / "untrusted-fallback"
    untrusted_fallback.mkdir(mode=0o755)
    monkeypatch.setattr("slaif_local_coding.constitution.cache.os.geteuid", lambda: foreign_uid)
    cache = DerivedIndexCache(policy(primary, fallback_root=untrusted_fallback))
    assert not cache.available
    assert cache.detail == "primary and fallback cache unavailable"


def test_untrusted_shard_and_entry_types_modes_and_owners_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    foreign_uid = os.geteuid() + 1
    type_root = tmp_path / "type"
    type_root.mkdir(mode=0o700)
    (type_root / "ab").write_text("not a shard")
    assert not DerivedIndexCache(policy(type_root)).available

    mode_root = tmp_path / "mode"
    mode_root.mkdir(mode=0o700)
    shard = mode_root / "ab"
    shard.mkdir(mode=0o700)
    shard.chmod(0o755)
    assert not DerivedIndexCache(policy(mode_root)).available

    owner_root = tmp_path / "owner"
    owner_root.mkdir(mode=0o700)
    (owner_root / "ab").mkdir(mode=0o700)
    with monkeypatch.context() as context:
        context.setattr("slaif_local_coding.constitution.cache.os.geteuid", lambda: foreign_uid)
        assert not DerivedIndexCache(policy(owner_root)).available

    entry_root = tmp_path / "entry"
    first = write_cache(entry_root)
    path = next(entry_root.rglob("*.json"))
    path.chmod(0o644)
    restarted = DerivedIndexCache(policy(entry_root))
    assert restarted.available
    assert not path.exists()
    assert restarted.get(key_for(index())).outcome == "miss"
    assert first.get(key_for(index())).outcome == "permission"


def test_untrusted_fallback_is_never_adopted(tmp_path: Path) -> None:
    primary = tmp_path / "missing-parent" / "primary"
    fallback = tmp_path / "fallback"
    fallback.mkdir(mode=0o755)
    cache = DerivedIndexCache(policy(primary, fallback_root=fallback))
    assert not cache.available
    assert cache.detail == "primary and fallback cache unavailable"


def test_restart_removes_expired_corrupt_and_invalid_artifacts(tmp_path: Path) -> None:
    valid_root = tmp_path / "valid"
    write_cache(valid_root)
    restarted = DerivedIndexCache(policy(valid_root))
    assert restarted.available and restarted.get(key_for(index())).outcome == "hit"

    expired_root = tmp_path / "expired"
    expired_clock = ControlledClock()
    write_cache(expired_root, ttl_seconds=0.01, clock=expired_clock)
    expired_clock.advance(0.02)
    restarted = DerivedIndexCache(policy(expired_root, ttl_seconds=0.01), clock=expired_clock)
    assert restarted.available
    assert not list(expired_root.rglob("*.json"))

    corrupt_root = tmp_path / "corrupt"
    write_cache(corrupt_root)
    next(corrupt_root.rglob("*.json")).write_text("{truncated")
    restarted = DerivedIndexCache(policy(corrupt_root))
    assert restarted.available
    assert not list(corrupt_root.rglob("*.json"))

    invalid_root = tmp_path / "invalid"
    write_cache(invalid_root)
    shard = invalid_root / key_for(index())[:2]
    (shard / "not-a-key.json").write_text("{}")
    (shard / ".tmp-orphan.json").write_text("{}")
    restarted = DerivedIndexCache(policy(invalid_root))
    assert restarted.available
    assert restarted.get(key_for(index())).outcome == "hit"
    assert [path.name for path in shard.iterdir()] == [key_for(index()) + ".json"]


def test_scan_overload_marks_entire_cache_unavailable(tmp_path: Path) -> None:
    root = tmp_path / "overload"
    root.mkdir(mode=0o700)
    shard = root / "ab"
    shard.mkdir(mode=0o700)
    for index_number in range(2):
        path = shard / f"{index_number:064x}.json"
        path.write_text("{}")
    cache = DerivedIndexCache(policy(root, max_scan_entries=2))
    assert not cache.available
    assert cache.detail == "cache startup scan limit exceeded"
    assert cache.get(key_for(index())).outcome == "unavailable"


def test_every_output_affecting_bound_changes_persistent_identity() -> None:
    base = key_for(index())
    changed_bounds = [
        ("reasoning_effort", "high"),
        ("max_source_bytes", 262_143),
        ("max_prompt_bytes", 383_999),
        ("max_output_tokens", 2999),
        ("max_output_bytes", 255_999),
        ("max_candidates", 127),
        ("max_json_depth", 23),
    ]
    changed_keys = [
        cache_key(
            identity(),
            source_logical_path=index().source_logical_path,
            source_sha256=index().source_sha256,
            model=index().model,
            index_schema_version=index().schema_version,
            compiler_version=index().compiler_version,
            prompt_policy_version=index().prompt_policy_version,
            **bounds(**{field: value}),
        )
        for field, value in changed_bounds
    ]
    assert len({base, *changed_keys}) == len(changed_keys) + 1


def test_no_raw_source_or_prompt_persistence_and_purge_supports_reconstruction(
    tmp_path: Path,
) -> None:
    marker = b"UNIQUE-SYNTHETIC-SOURCE-MARKER"
    governed = b"MUST obey synthetic rule\n" + marker
    from slaif_local_coding.constitution.compiler_models import CompiledIndex

    governed_index = CompiledIndex(
        **{
            **index().model_dump(mode="json"),
            "source_sha256": hashlib.sha256(governed).hexdigest(),
            "source_byte_length": len(governed),
        }
    )
    cache = DerivedIndexCache(policy(tmp_path / "privacy"))
    key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=governed_index.source_sha256,
        model=governed_index.model,
        index_schema_version=governed_index.schema_version,
        compiler_version=governed_index.compiler_version,
        prompt_policy_version=governed_index.prompt_policy_version,
        **bounds(),
    )
    assert cache.put(key, governed_index).outcome == "written"
    rogue_temp = tmp_path / "privacy" / "ab" / ".tmp-orphan.json"
    rogue_temp.parent.mkdir()
    rogue_temp.write_bytes(b"orphan")
    persisted = b"".join(
        path.read_bytes() for path in (tmp_path / "privacy").rglob("*") if path.is_file()
    )
    assert marker not in persisted and b"UNIQUE-PROMPT" not in persisted
    assert cache.purge() == 2
    assert cache.get(key).outcome == "miss"
    assert not list((tmp_path / "privacy").rglob("*"))
