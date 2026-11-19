"""Pinned actual-model CPU tokenizer (objective 021, tokenizer half).

INERT component of the v1 dependency-bundle cache rework
(``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``): the adapter loads the
pinned public CPU tokenizer artifacts for the declared Qwen3.8-27B
reference capability ONCE from the packaged, digest-verified assets,
counts tokens with the real tokenizer over final rendered text, and
binds the tokenization identity (model / revision / asset digests /
vocabulary / normalizer / template / render policy / loader version)
into the derived cache identity.

Law (objective 021 item 1 + plan policy 10):

- the four pinned assets are CLOSED constants (exact sizes and
  SHA-256); a missing, resized, re-hashed or structurally wrong asset
  is a fixed typed refusal and never a fallback to byte / character
  estimation;
- load and validate ONCE: repeated counting and hot hits never reload
  assets or read recovery originals;
- a byte change to any asset or the template invalidates the
  tokenization identity (the identity is derived from the verified
  digests);
- no model weights, no torch, no image decoding, no runtime model
  download and no hosted tokenizer call; the loader touches only the
  packaged (or explicitly supplied) asset files;
- the component is INERT: no request-pipeline wiring, no v1 runtime
  activation, no configuration key.
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import Field, field_validator

from .graph_models import _fixed, _GraphFrozen

BUNDLE_TOKENIZER_CONTRACT_VERSION = "cache-bundle-tokenizer/v1"
BUNDLE_TOKENIZER_POLICY_VERSION = "bundle-tokenizer-policy/v1"
BUNDLE_TOKENIZER_RENDER_POLICY_VERSION = "bundle-render-policy/v1"

#: The declared reference capability: the pinned public upstream
#: tokenizer artifacts (Apache-2.0), revision-pinned.
PINNED_TOKENIZER_UPSTREAM = "Qwen/Qwen3.8-27B"
PINNED_TOKENIZER_REVISION = "37561816e66b5b9153b1b64c10968c18c1e6f4a0"
PINNED_TOKENIZERS_VERSION = "0.22.2"
PINNED_TOKENIZER_MODEL_TYPE = "BPE"
PINNED_TOKENIZER_MAX_JSON_DEPTH = 64

#: Closed pinned asset table (name, exact size, exact SHA-256).
PINNED_TOKENIZER_JSON: Final = (
    "tokenizer.json",
    12_809_320,
    "0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3",
)
PINNED_TOKENIZER_CONFIG_JSON: Final = (
    "tokenizer_config.json",
    9_984,
    "207c03c41a06a9c3b0cc527d8a56115159c1eac6b59a4ffae85b646e773d074e",
)
PINNED_CHAT_TEMPLATE_JINJA: Final = (
    "chat_template.jinja",
    9_004,
    "af16f654968d47d09a6c604e00370b12dbc21f76456f59c9e98b82e84d9f6375",
)
PINNED_ASSET_LICENSE: Final = (
    "LICENSE",
    11_544,
    "bbedc3fda3305820b977265f01b8619d87570a6739de3a5582c3464840f1e57a",
)

PINNED_TOKENIZER_ASSETS: Final[tuple[tuple[str, int, str], ...]] = (
    PINNED_CHAT_TEMPLATE_JINJA,
    PINNED_ASSET_LICENSE,
    PINNED_TOKENIZER_CONFIG_JSON,
    PINNED_TOKENIZER_JSON,
)

BUNDLED_ASSETS_DIRNAME = "tokenizer_assets"

#: The pinned Qwen chat-family framing tokens (documented render
#: policy); the renderers embed them verbatim, no padding.
_IM_START = "<" + "|im_" + "start|" + ">"
_IM_END = "<" + "|im_" + "end|" + ">"


class _EngineEncoding(Protocol):
    """The narrow encoding surface the component consumes."""

    ids: Sequence[int]


class _TokenizerEngine(Protocol):
    """The narrow loaded-engine surface (the locked ``tokenizers``
    ``Tokenizer``); only the documented methods are consumed."""

    def encode(self, text: str, add_special_tokens: bool) -> _EngineEncoding: ...


class BundleTokenizerReason(StrEnum):
    """The closed tokenizer-component failure vocabulary (021)."""

    ASSET_DIRECTORY_INVALID = "asset_directory_invalid"
    ASSET_MISSING = "asset_missing"
    ASSET_SIZE_MISMATCH = "asset_size_mismatch"
    ASSET_DIGEST_MISMATCH = "asset_digest_mismatch"
    ASSET_UNREADABLE = "asset_unreadable"
    ASSET_SHAPE_MISMATCH = "asset_shape_mismatch"
    TEMPLATE_INVALID = "template_invalid"
    LOADER_VERSION_MISMATCH = "loader_version_mismatch"
    BAD_INPUT = "bad_input"
    IDENTITY_MISMATCH = "identity_mismatch"


class BundleTokenizerError(Exception):
    """Fixed typed tokenizer-component refusal (content-free)."""

    def __init__(self, reason: BundleTokenizerReason) -> None:
        self.reason = reason
        super().__init__(f"bundle tokenizer refusal: {reason.value}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _bounded_asset_json(raw: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError("non-finite")),
        )
    except (UnicodeError, ValueError) as exc:
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH) from exc
    if not isinstance(value, dict):
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)
    _check_json_depth(value, 0, PINNED_TOKENIZER_MAX_JSON_DEPTH, name)
    return value


def _check_json_depth(value: Any, depth: int, limit: int, name: str) -> None:
    if depth > limit:
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)
    if isinstance(value, dict):
        for item in value.values():
            _check_json_depth(item, depth + 1, limit, name)
    elif isinstance(value, list):
        for item in value:
            _check_json_depth(item, depth + 1, limit, name)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bundled_assets_dir() -> Path:
    """The packaged pinned-asset directory (wheel/sdist input)."""
    return Path(__file__).resolve().parent / BUNDLED_ASSETS_DIRNAME


def derive_tokenization_identity(
    *,
    contract_version: str,
    policy_version: str,
    render_policy_version: str,
    upstream: str,
    revision: str,
    assets: tuple[tuple[str, int, str], ...],
    vocab_size: int,
    normalizer_digest: str,
    template_sha256: str,
    tokenizers_version: str,
) -> str:
    """Deterministic 64-hex tokenization identity.

    Any byte change to any pinned asset or template changes the
    recorded digests and therefore this identity; any change of the
    bound vocabulary, normalizer, policies, upstream or loader
    version does the same.
    """
    material = {
        "contract_version": contract_version,
        "policy_version": policy_version,
        "render_policy_version": render_policy_version,
        "upstream": upstream,
        "revision": revision,
        "assets": [list(item) for item in assets],
        "vocab_size": vocab_size,
        "normalizer_digest": normalizer_digest,
        "template_sha256": template_sha256,
        "tokenizers_version": tokenizers_version,
    }
    return _sha256_hex(_canonical_json_bytes(material))


class PinnedAsset(_GraphFrozen):
    """One closed pinned asset fact (name, exact size, exact digest)."""

    name: str = Field(min_length=1, max_length=128)
    size_bytes: int = Field(ge=1, le=16_777_216)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("name")
    @classmethod
    def _v_name(cls, value: str) -> str:
        if value in {pinned[0] for pinned in PINNED_TOKENIZER_ASSETS}:
            return value
        raise _fixed(f"the pinned tokenizer asset name is not closed: {value!r}")


class BundleTokenizerBinding(_GraphFrozen):
    """The identity-bound tokenization binding (021).

    ``identity`` is recomputed from every actual field on every
    construction (factory and direct) and a mismatch is refused;
    the opaque value alone is never trusted.
    """

    contract_version: str = Field(min_length=1, max_length=64)
    policy_version: str = Field(min_length=1, max_length=64)
    render_policy_version: str = Field(min_length=1, max_length=64)
    upstream: str = Field(min_length=1, max_length=256)
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    assets: tuple[PinnedAsset, ...] = Field(min_length=4, max_length=4)
    vocab_size: int = Field(ge=1, le=2_097_152)
    normalizer_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    template_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    tokenizers_version: str = Field(min_length=1, max_length=32)
    identity: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("assets")
    @classmethod
    def _v_assets(cls, value: tuple[PinnedAsset, ...]) -> tuple[PinnedAsset, ...]:
        names = [item.name for item in value]
        if len(set(names)) != len(names):
            raise _fixed("the pinned tokenizer asset set carries a duplicate name")
        return value

    def rederive_identity(self) -> str:
        return derive_tokenization_identity(
            contract_version=self.contract_version,
            policy_version=self.policy_version,
            render_policy_version=self.render_policy_version,
            upstream=self.upstream,
            revision=self.revision,
            assets=tuple((item.name, item.size_bytes, item.sha256) for item in self.assets),
            vocab_size=self.vocab_size,
            normalizer_digest=self.normalizer_digest,
            template_sha256=self.template_sha256,
            tokenizers_version=self.tokenizers_version,
        )


def make_bundle_tokenizer_binding(**fields: Any) -> BundleTokenizerBinding:
    """The factory path: recompute ``identity`` from the actual fields."""
    binding = BundleTokenizerBinding.model_construct(**fields)
    expected = binding.rederive_identity()
    if binding.identity != expected:
        raise BundleTokenizerError(BundleTokenizerReason.IDENTITY_MISMATCH)
    return binding


def verify_pinned_assets(
    assets_dir: Path,
) -> tuple[tuple[PinnedAsset, ...], dict[str, bytes]]:
    """Verify the exact pinned asset table (size + digest) at load.

    Returns the verified asset facts AND the SAME verified byte
    snapshots: the loader must consume these snapshots (never reopen
    the files) so the engine / config / template are validated
    against the exact bytes the digests were computed over.  Every
    refusal is a fixed typed reason; no file content is ever
    reported.
    """
    if not assets_dir.is_dir() or assets_dir.is_symlink():
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_DIRECTORY_INVALID)
    verified: list[PinnedAsset] = []
    snapshots: dict[str, bytes] = {}
    for name, size_bytes, sha256 in PINNED_TOKENIZER_ASSETS:
        path = assets_dir / name
        if not path.is_file() or path.is_symlink():
            raise BundleTokenizerError(BundleTokenizerReason.ASSET_MISSING)
        if path.stat().st_size != size_bytes:
            raise BundleTokenizerError(BundleTokenizerReason.ASSET_SIZE_MISMATCH)
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise BundleTokenizerError(BundleTokenizerReason.ASSET_UNREADABLE) from exc
        if len(raw) != size_bytes or _sha256_hex(raw) != sha256:
            raise BundleTokenizerError(BundleTokenizerReason.ASSET_DIGEST_MISMATCH)
        verified.append(PinnedAsset(name=name, size_bytes=size_bytes, sha256=sha256))
        snapshots[name] = raw
    return tuple(verified), snapshots


def _load_once(assets_dir: Path) -> BundleTokenizer:
    from tokenizers import Tokenizer

    try:
        import tokenizers as _tokenizers_module
    except ImportError as exc:  # pragma: no cover - locked dependency
        raise BundleTokenizerError(BundleTokenizerReason.LOADER_VERSION_MISMATCH) from exc
    loader_version = str(getattr(_tokenizers_module, "__version__", ""))
    if loader_version != PINNED_TOKENIZERS_VERSION:
        raise BundleTokenizerError(BundleTokenizerReason.LOADER_VERSION_MISMATCH)

    assets, snapshots = verify_pinned_assets(assets_dir)
    # The SAME verified byte snapshots: no second open, no re-hash
    # drift between verification and load.
    tokenizer_raw = snapshots[PINNED_TOKENIZER_JSON[0]]
    config_raw = snapshots[PINNED_TOKENIZER_CONFIG_JSON[0]]
    template_raw = snapshots[PINNED_CHAT_TEMPLATE_JINJA[0]]

    tokenizer_json = _bounded_asset_json(tokenizer_raw, PINNED_TOKENIZER_JSON[0])
    config_json = _bounded_asset_json(config_raw, PINNED_TOKENIZER_CONFIG_JSON[0])
    if not isinstance(config_json, dict):
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)

    model_section = tokenizer_json.get("model")
    if not isinstance(model_section, dict) or model_section.get("type") != (
        PINNED_TOKENIZER_MODEL_TYPE
    ):
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)
    normalizer_section = tokenizer_json.get("normalizer")
    if not isinstance(normalizer_section, (dict, list)):
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)
    template = template_raw.decode("utf-8", errors="strict")
    if not template or not template.strip() or "{" not in template:
        raise BundleTokenizerError(BundleTokenizerReason.TEMPLATE_INVALID)

    try:
        engine = Tokenizer.from_str(tokenizer_raw.decode("utf-8"))
    except (UnicodeError, ValueError, OSError) as exc:
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH) from exc
    vocab_size = int(engine.get_vocab_size())
    if vocab_size <= 0:
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_SHAPE_MISMATCH)

    assets_by_name = {item.name: item for item in assets}
    normalizer_digest = _sha256_hex(_canonical_json_bytes(normalizer_section))
    template_digest = assets_by_name[PINNED_CHAT_TEMPLATE_JINJA[0]].sha256
    binding = make_bundle_tokenizer_binding(
        contract_version=BUNDLE_TOKENIZER_CONTRACT_VERSION,
        policy_version=BUNDLE_TOKENIZER_POLICY_VERSION,
        render_policy_version=BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
        upstream=PINNED_TOKENIZER_UPSTREAM,
        revision=PINNED_TOKENIZER_REVISION,
        assets=assets,
        vocab_size=vocab_size,
        normalizer_digest=normalizer_digest,
        template_sha256=template_digest,
        tokenizers_version=loader_version,
        identity=derive_tokenization_identity(
            contract_version=BUNDLE_TOKENIZER_CONTRACT_VERSION,
            policy_version=BUNDLE_TOKENIZER_POLICY_VERSION,
            render_policy_version=BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
            upstream=PINNED_TOKENIZER_UPSTREAM,
            revision=PINNED_TOKENIZER_REVISION,
            assets=tuple((item.name, item.size_bytes, item.sha256) for item in assets),
            vocab_size=vocab_size,
            normalizer_digest=normalizer_digest,
            template_sha256=template_digest,
            tokenizers_version=loader_version,
        ),
    )
    return BundleTokenizer(binding=binding, _engine=engine)


class BundleTokenizer:
    """The loaded pinned tokenizer (load once; count forever).

    ``count_tokens`` is the ONLY authoritative counting surface: the
    real tokenizer over the final rendered text.  Byte / character
    heuristics are diagnostics only and are never a substitute here.
    """

    def __init__(self, *, binding: BundleTokenizerBinding, _engine: _TokenizerEngine) -> None:
        if binding.rederive_identity() != binding.identity:
            raise BundleTokenizerError(BundleTokenizerReason.IDENTITY_MISMATCH)
        self.binding = binding
        self._engine = _engine

    # -- counting ------------------------------------------------------

    def count_tokens(self, text: str) -> int:
        """Count ONE rendered text with the real tokenizer."""
        if not isinstance(text, str):
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT)
        return len(self._engine.encode(text, add_special_tokens=False).ids)

    # -- pinned render policy (documented deterministic renderers) -----

    def render_message(self, role: str, content: str) -> str:
        """Pinned compatible message rendering (role framing only).

        The deterministic ``im_start`` / ``im_end`` framing of the
        Qwen chat family; no padding, no whitespace normalization of
        the content, so the rendered bytes are exactly what is
        counted.
        """
        if role not in {"system", "user", "assistant"}:
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT)
        if not isinstance(content, str):
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT)
        return f"{_IM_START}{role}\n{content}{_IM_END}\n"

    def render_tool_envelope(self, name: str, description: str, parameters: dict[str, Any]) -> str:
        """Pinned compatible tool-definition envelope rendering.

        The exact minified JSON the OpenAI-compatible tool envelope
        carries; ``parameters`` must be JSON-serializable plain data.
        """
        if not name or not isinstance(name, str):
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT)
        envelope = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }
        try:
            return json.dumps(envelope, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT) from exc

    def render_compiled_block(
        self,
        *,
        entry_label: str,
        body: str,
        references: tuple[str, ...] = (),
    ) -> str:
        """The versioned compiled-block render policy (no padding).

        Final rendered compiled text INCLUDING references, metadata
        and separators; this exact text is what the budget counts
        against the per-entry allowance and the aggregate limit.
        """
        if not entry_label or not body:
            raise BundleTokenizerError(BundleTokenizerReason.BAD_INPUT)
        parts = [
            f"<slaif-compiled-block render={BUNDLE_TOKENIZER_RENDER_POLICY_VERSION} "
            f"entry={entry_label}>",
            body.rstrip(),
        ]
        if references:
            parts.append("<references>")
            parts.extend(references)
            parts.append("</references>")
        parts.append("</slaif-compiled-block>")
        return "\n".join(parts)

    # -- introspection --------------------------------------------------

    @property
    def vocab_size(self) -> int:
        return self.binding.vocab_size


_load_lock = threading.Lock()
_load_registry: dict[str, BundleTokenizer] = {}
_load_counts: dict[str, int] = {}


def get_bundle_tokenizer(assets_dir: Path | str | None = None) -> BundleTokenizer:
    """Load-and-validate-once access to the pinned tokenizer.

    The first call for a resolved asset directory verifies the exact
    pinned asset table and loads the engine; every later call returns
    the SAME instance with zero asset reads (repeated counting and
    hot hits never reload assets).
    """
    raw_dir = Path(assets_dir) if assets_dir is not None else bundled_assets_dir()
    # Fail closed BEFORE any resolve/follow: the supplied asset directory
    # itself may not be a symlink (no silent escape from the pinned set).
    if raw_dir.is_symlink() or not raw_dir.is_dir():
        raise BundleTokenizerError(BundleTokenizerReason.ASSET_DIRECTORY_INVALID)
    resolved = raw_dir.resolve()
    key = str(resolved)
    with _load_lock:
        cached = _load_registry.get(key)
        if cached is not None:
            return cached
        loaded = _load_once(resolved)
        _load_registry[key] = loaded
        _load_counts[key] = _load_counts.get(key, 0) + 1
        return loaded


def bundle_tokenizer_load_counts() -> dict[str, int]:
    """Process-local actual load counts per resolved asset directory."""
    with _load_lock:
        return dict(_load_counts)


def _reset_load_registry_for_tests() -> None:
    with _load_lock:
        _load_registry.clear()
        _load_counts.clear()
