"""Permanent 021 tokenizer matrix (contract
``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``, tokenizer half).

The pinned public CPU tokenizer for the declared Qwen3.8-27B
reference capability: the closed pinned-asset table (exact sizes
and SHA-256 at the pinned HF revision), load-and-validate-once
(no reload on repeated counting / hot hits), the real-tokenizer
counting surface over the pinned render policy (the framing
verified against the pinned added-token IDs), the identity
invalidation law (any asset or template byte change changes the
tokenization identity and the tampered load is a typed refusal),
and the hermetic loader (no network, no weights, no torch).

INERT component: no request-pipeline wiring, no v1 runtime.
"""

from __future__ import annotations

import hashlib
import json
import socket
from pathlib import Path

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    _IM_END,
    _IM_START,
    BUNDLE_TOKENIZER_CONTRACT_VERSION,
    BUNDLE_TOKENIZER_POLICY_VERSION,
    BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
    PINNED_CHAT_TEMPLATE_JINJA,
    PINNED_TOKENIZER_ASSETS,
    PINNED_TOKENIZER_JSON,
    PINNED_TOKENIZER_REVISION,
    PINNED_TOKENIZER_UPSTREAM,
    PINNED_TOKENIZERS_VERSION,
    BundleTokenizer,
    BundleTokenizerBinding,
    BundleTokenizerError,
    BundleTokenizerReason,
    _reset_load_registry_for_tests,
    bundle_tokenizer_load_counts,
    bundled_assets_dir,
    derive_tokenization_identity,
    get_bundle_tokenizer,
    make_bundle_tokenizer_binding,
    verify_pinned_assets,
)

#: The pinned added-token IDs of the Qwen chat-family framing
#: (added_tokens_decoder of the pinned tokenizer_config.json).
ADDED_TOKEN_IM_START = 248045
ADDED_TOKEN_IM_END = 248046


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tampered_dir(tmp_path: Path, name: str, *, resize: bool = False) -> Path:
    """A copy of the pinned assets with ONE byte changed in ``name``."""
    src = bundled_assets_dir()
    dst = tmp_path / "tampered"
    dst.mkdir(parents=True)
    for asset_name, _size, _digest in PINNED_TOKENIZER_ASSETS:
        raw = (src / asset_name).read_bytes()
        if asset_name == name:
            if resize:
                raw = raw[:-1]
            else:
                raw = raw[:-1] + (b"\x00" if raw[-1:] != b"\x00" else b"\x01")
        (dst / asset_name).write_bytes(raw)
    return dst


@pytest.fixture()
def tokenizer() -> BundleTokenizer:
    return get_bundle_tokenizer()


def test_pinned_load_positive(tokenizer: BundleTokenizer) -> None:
    b = tokenizer.binding
    assert b.upstream == PINNED_TOKENIZER_UPSTREAM
    assert b.revision == PINNED_TOKENIZER_REVISION
    assert b.tokenizers_version == PINNED_TOKENIZERS_VERSION
    assert b.contract_version == BUNDLE_TOKENIZER_CONTRACT_VERSION
    assert b.policy_version == BUNDLE_TOKENIZER_POLICY_VERSION
    assert b.render_policy_version == BUNDLE_TOKENIZER_RENDER_POLICY_VERSION
    assert [(a.name, a.size_bytes, a.sha256) for a in b.assets] == [
        tuple(item) for item in PINNED_TOKENIZER_ASSETS
    ]
    # The actual vocabulary of the pinned tokenizer:
    assert b.vocab_size == 248077
    # The normalizer digest is the canonical digest of the ACTUAL
    # pinned normalizer section:
    raw = (bundled_assets_dir() / PINNED_TOKENIZER_JSON[0]).read_bytes()
    cfg = json.loads(raw.decode("utf-8"))
    normalizer = cfg["normalizer"]
    assert b.normalizer_digest == _sha256_hex(
        json.dumps(normalizer, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    # The template digest is the pinned template asset digest:
    assert b.template_sha256 == PINNED_CHAT_TEMPLATE_JINJA[2]
    # The identity rederives from the actual fields:
    assert b.rederive_identity() == b.identity


def test_count_real_tokens(tokenizer: BundleTokenizer) -> None:
    # Deterministic real-tokenizer counts (known synthetic texts):
    assert tokenizer.count_tokens("Hello, world!") == 4
    assert tokenizer.count_tokens("") == 0
    mixed = "The quick brown fox. \u4f60\u597d\u4e16\u754c."
    assert tokenizer.count_tokens(mixed) == tokenizer.count_tokens(mixed)
    assert tokenizer.count_tokens(mixed) > 0
    with pytest.raises(BundleTokenizerError) as exc:
        tokenizer.count_tokens(12)  # type: ignore[arg-type]
    assert exc.value.reason is BundleTokenizerReason.BAD_INPUT


def test_pinned_render_policy_framing(tokenizer: BundleTokenizer) -> None:
    # The framing encodes to the EXACT pinned added-token IDs:
    assert tokenizer._engine.encode(_IM_START, add_special_tokens=False).ids == [
        ADDED_TOKEN_IM_START
    ]
    assert tokenizer._engine.encode(_IM_END, add_special_tokens=False).ids == [ADDED_TOKEN_IM_END]
    rendered = tokenizer.render_message("user", "hi")
    assert rendered == f"{_IM_START}user\nhi{_IM_END}\n"
    ids = tokenizer._engine.encode(rendered, add_special_tokens=False).ids
    assert ids[0] == ADDED_TOKEN_IM_START
    assert ids[-2] == ADDED_TOKEN_IM_END
    # No padding: the rendered text is exactly the framing + content:
    assert tokenizer.count_tokens(rendered) == tokenizer.count_tokens(
        f"{_IM_START}user\nhi{_IM_END}\n"
    )
    with pytest.raises(BundleTokenizerError) as exc:
        tokenizer.render_message("tool", "x")
    assert exc.value.reason is BundleTokenizerReason.BAD_INPUT


def test_pinned_render_policy_tool_envelope(tokenizer: BundleTokenizer) -> None:
    params = {"type": "object", "properties": {"a": {"type": "string"}}}
    rendered = tokenizer.render_tool_envelope("lookup", "Look up a.", params)
    expected = json.dumps(
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up a.",
                "parameters": params,
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    assert rendered == expected
    # Stable and counted with the real tokenizer:
    assert rendered == tokenizer.render_tool_envelope("lookup", "Look up a.", params)
    assert tokenizer.count_tokens(rendered) > 0
    with pytest.raises(BundleTokenizerError) as exc:
        tokenizer.render_tool_envelope("", "d", {})
    assert exc.value.reason is BundleTokenizerReason.BAD_INPUT
    with pytest.raises(BundleTokenizerError) as exc:
        tokenizer.render_tool_envelope("n", "d", {"x": object()})
    assert exc.value.reason is BundleTokenizerReason.BAD_INPUT


def test_pinned_render_policy_compiled_block(tokenizer: BundleTokenizer) -> None:
    block = tokenizer.render_compiled_block(
        entry_label="root-entry",
        body="MUST keep the bounds.",
        references=("AGENTS.md",),
    )
    # Metadata, separators and references are ALL part of the final
    # rendered text (counted, not padded away):
    assert (
        block == "<slaif-compiled-block render=bundle-render-policy/v1 entry=root-entry>\n"
        "MUST keep the bounds.\n<references>\nAGENTS.md\n</references>\n"
        "</slaif-compiled-block>"
    )
    body_only = tokenizer.count_tokens("MUST keep the bounds.")
    assert tokenizer.count_tokens(block) > body_only
    with pytest.raises(BundleTokenizerError) as exc:
        tokenizer.render_compiled_block(entry_label="", body="x")
    assert exc.value.reason is BundleTokenizerReason.BAD_INPUT


def test_load_validate_once_no_reload(tokenizer: BundleTokenizer) -> None:
    key = str(bundled_assets_dir())
    assert bundle_tokenizer_load_counts() == {key: 1}
    assert get_bundle_tokenizer() is tokenizer
    assert get_bundle_tokenizer(bundled_assets_dir()) is tokenizer
    # Repeated counting never reloads assets:
    for _ in range(50):
        assert tokenizer.count_tokens("repeat") > 0
    assert bundle_tokenizer_load_counts() == {key: 1}


def test_asset_missing_refused(tmp_path: Path) -> None:
    dst = tmp_path / "assets"
    dst.mkdir()
    src = bundled_assets_dir()
    for asset_name, _size, _digest in PINNED_TOKENIZER_ASSETS:
        (dst / asset_name).write_bytes((src / asset_name).read_bytes())
    (dst / "LICENSE").unlink()
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(dst)
    assert exc.value.reason is BundleTokenizerReason.ASSET_MISSING


def test_asset_directory_invalid_refused(tmp_path: Path) -> None:
    file_path = tmp_path / "afile"
    file_path.write_bytes(b"x")
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(file_path)
    assert exc.value.reason is BundleTokenizerReason.ASSET_DIRECTORY_INVALID
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(tmp_path / "missing")
    assert exc.value.reason is BundleTokenizerReason.ASSET_DIRECTORY_INVALID
    link = tmp_path / "link"
    link.symlink_to(bundled_assets_dir())
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(link)
    assert exc.value.reason is BundleTokenizerReason.ASSET_DIRECTORY_INVALID


@pytest.mark.parametrize("name", [asset[0] for asset in PINNED_TOKENIZER_ASSETS])
def test_tampered_asset_digest_refused(tmp_path: Path, name: str) -> None:
    dst = _tampered_dir(tmp_path, name)
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(dst)
    assert exc.value.reason is BundleTokenizerReason.ASSET_DIGEST_MISMATCH
    # A resized asset is refused at the size fence (before digest):
    dst2 = _tampered_dir(tmp_path / "sz", name, resize=True)
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(dst2)
    assert exc.value.reason is BundleTokenizerReason.ASSET_SIZE_MISMATCH


def test_symlinked_asset_file_refused(tmp_path: Path) -> None:
    dst = tmp_path / "assets"
    dst.mkdir()
    src = bundled_assets_dir()
    for asset_name, _size, _digest in PINNED_TOKENIZER_ASSETS:
        (dst / asset_name).symlink_to(src / asset_name)
    with pytest.raises(BundleTokenizerError) as exc:
        get_bundle_tokenizer(dst)
    assert exc.value.reason is BundleTokenizerReason.ASSET_MISSING


def test_byte_change_invalidates_identity(tokenizer: BundleTokenizer) -> None:
    b = tokenizer.binding
    # A single-byte asset change (different pinned digest) yields a
    # different tokenization identity -- and therefore a different
    # derived compiled-entry identity in the budget / compiler:
    assets = [(a.name, a.size_bytes, a.sha256) for a in b.assets]
    tampered = [(a[0], a[1], "f" * 64) if a[0] == PINNED_TOKENIZER_JSON[0] else a for a in assets]
    tampered_template = [
        (a[0], a[1], "e" * 64) if a[0] == PINNED_CHAT_TEMPLATE_JINJA[0] else a for a in assets
    ]

    def _identity(
        assets_key: tuple[tuple[str, int, str], ...],
        template_sha256: str,
        *,
        normalizer_digest: str | None = None,
        vocab_size: int | None = None,
        tokenizers_version: str | None = None,
    ) -> str:
        return derive_tokenization_identity(
            contract_version=b.contract_version,
            policy_version=b.policy_version,
            render_policy_version=b.render_policy_version,
            upstream=b.upstream,
            revision=b.revision,
            vocab_size=b.vocab_size if vocab_size is None else vocab_size,
            normalizer_digest=(
                b.normalizer_digest if normalizer_digest is None else normalizer_digest
            ),
            template_sha256=template_sha256,
            tokenizers_version=(
                b.tokenizers_version if tokenizers_version is None else tokenizers_version
            ),
            assets=assets_key,
        )

    actual = _identity(tuple(assets), b.template_sha256)
    assert actual == b.identity
    changed_asset = _identity(tuple(tampered), b.template_sha256)
    changed_template = _identity(tuple(tampered_template), "d" * 64)
    assert changed_asset != b.identity
    assert changed_template != b.identity
    assert changed_asset != changed_template
    # A changed normalizer / vocabulary / loader version too:
    assert _identity(tuple(assets), b.template_sha256, normalizer_digest="c" * 64) != b.identity
    assert _identity(tuple(assets), b.template_sha256, vocab_size=b.vocab_size + 1) != b.identity
    assert _identity(tuple(assets), b.template_sha256, tokenizers_version="0.22.9") != b.identity


def test_binding_factory_identity_mismatch_refused() -> None:
    fields = dict(
        contract_version=BUNDLE_TOKENIZER_CONTRACT_VERSION,
        policy_version=BUNDLE_TOKENIZER_POLICY_VERSION,
        render_policy_version=BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
        upstream=PINNED_TOKENIZER_UPSTREAM,
        revision=PINNED_TOKENIZER_REVISION,
        assets=tuple(
            type("A", (), {"name": n, "size_bytes": s, "sha256": d})()
            for n, s, d in PINNED_TOKENIZER_ASSETS
        ),
        vocab_size=248077,
        normalizer_digest="a" * 64,
        template_sha256="b" * 64,
        tokenizers_version=PINNED_TOKENIZERS_VERSION,
        identity="0" * 64,
    )
    with pytest.raises(BundleTokenizerError) as exc:
        make_bundle_tokenizer_binding(**fields)
    assert exc.value.reason is BundleTokenizerReason.IDENTITY_MISMATCH


def test_hermmetic_load_no_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The loader never touches the network (no hosted tokenizer)."""
    dst = tmp_path / "assets"
    dst.mkdir()
    src = bundled_assets_dir()
    for asset_name, _size, _digest in PINNED_TOKENIZER_ASSETS:
        (dst / asset_name).write_bytes((src / asset_name).read_bytes())

    def _refused(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network use during pinned tokenizer load")

    monkeypatch.setattr(socket, "socket", _refused)
    _reset_load_registry_for_tests()
    try:
        loaded = get_bundle_tokenizer(dst)
        assert loaded.count_tokens("offline") > 0
        assert loaded.binding.identity
    finally:
        _reset_load_registry_for_tests()


def test_verify_pinned_assets_packaged(tokenizer: BundleTokenizer) -> None:
    verified, snapshots = verify_pinned_assets(bundled_assets_dir())
    assert [(a.name, a.size_bytes, a.sha256) for a in verified] == [
        tuple(item) for item in PINNED_TOKENIZER_ASSETS
    ]
    assert verified == tuple(tokenizer.binding.assets)
    # The verified snapshots are the exact pinned bytes (same bytes
    # the loader consumes for the engine / config / template):
    src = bundled_assets_dir()
    for name, size_bytes, _sha256 in PINNED_TOKENIZER_ASSETS:
        assert snapshots[name] == (src / name).read_bytes()
        assert len(snapshots[name]) == size_bytes
    # The binding model is closed and frozen:
    binding: BundleTokenizerBinding = tokenizer.binding
    with pytest.raises(ValidationError):
        binding.vocab_size = 1
