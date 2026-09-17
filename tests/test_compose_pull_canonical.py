"""Order 013-a, workstream C (R10): static gate for the pull-based canonical
compose file (stdlib only; no Docker required).

compose.yaml is the pull-based canonical operator file: it carries NO build
key, its default pull reference equals the manifest's OCI image reference plus
the 0.1.0 tag, and a SLAIF_LOCAL_CODING_IMAGE override renders into the
`image` field verbatim, including a digest-pinned form.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSE = REPO_ROOT / "compose.yaml"
MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"
IMAGE_REF_DEFAULT = "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0"
IMAGE_FIELD = "${SLAIF_LOCAL_CODING_IMAGE:-ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0}"


def _image_field_value() -> str:
    text = COMPOSE.read_text(encoding="utf-8")
    m = re.search(r"^\s*image:\s*(\S+)\s*$", text, re.MULTILINE)
    assert m, "compose.yaml must declare an image field"
    return m.group(1)


def _interpolate_image(value: str, env: dict[str, str]) -> str:
    """Deterministic render of the single documented variable form
    `${SLAIF_LOCAL_CODING_IMAGE:-<default>}`: the override renders verbatim,
    otherwise the default applies (compose interpolation semantics)."""
    m = re.fullmatch(r"\$\{SLAIF_LOCAL_CODING_IMAGE:-([^}]+)\}", value)
    assert m, f"unexpected image field form: {value}"
    return env.get("SLAIF_LOCAL_CODING_IMAGE") or m.group(1)


def test_canonical_compose_has_no_build_key() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert not re.search(r"^[ \t]+build:", text, re.MULTILINE), (
        "compose.yaml must not carry a build key (pull-based canonical)"
    )


def test_canonical_compose_default_pull_reference_matches_manifest() -> None:
    value = _image_field_value()
    assert value == IMAGE_FIELD
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = str(manifest["oci"]["image_reference"]) + ":0.1.0"
    assert _interpolate_image(value, {}) == expected == IMAGE_REF_DEFAULT


def test_image_override_renders_verbatim_including_digest_pin() -> None:
    value = _image_field_value()
    plain = "ghcr.io/ulfe-lmi/slaif-local-coding:0.2.0"
    assert _interpolate_image(value, {"SLAIF_LOCAL_CODING_IMAGE": plain}) == plain
    digest_pin = "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:" + "0" * 64
    assert _interpolate_image(value, {"SLAIF_LOCAL_CODING_IMAGE": digest_pin}) == digest_pin
