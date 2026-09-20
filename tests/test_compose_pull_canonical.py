"""Order 013-a, workstream C (R10); order 013-i, B7: static gate for the
pull-based canonical compose file (stdlib only; no Docker required).

compose.yaml is the pull-based canonical operator file: it carries NO build
key and its `image` field is the EXPLICIT-selection form
`${SLAIF_LOCAL_CODING_IMAGE:?<message>}` — no silent default. The
historical private 0.1.0 tag is legacy output that was never published to
users and is NOT the RC benchmark target, so no default may render it. An
env-provided value renders verbatim (including a digest-pinned form); an
unset variable must fail compose interpolation (required variable), never
fall back to a default.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSE = REPO_ROOT / "compose.yaml"

# The exact required-variable form: the `:?` operator makes the variable
# mandatory (compose fails closed when it is absent/empty) and carries an
# operator-facing message (no default value group).
IMAGE_FIELD = (
    "${SLAIF_LOCAL_CODING_IMAGE:?set SLAIF_LOCAL_CODING_IMAGE to the explicit "
    "image reference (candidate tag or digest, digest preferred) - see INSTALL.md}"
)


def _image_field_value() -> str:
    text = COMPOSE.read_text(encoding="utf-8")
    # The whole remainder of the `image:` line is the value: the documented
    # form ${SLAIF_LOCAL_CODING_IMAGE:?<message>} may contain spaces.
    m = re.search(r"^\s*image:\s*(.+?)\s*$", text, re.MULTILINE)
    assert m, "compose.yaml must declare an image field"
    return m.group(1)


def _interpolate_image(value: str, env: dict[str, str]) -> str | None:
    """Deterministic render of the documented variable form
    `${SLAIF_LOCAL_CODING_IMAGE:?<message>}`: an env value renders verbatim;
    an unset/empty variable yields None (compose would fail with the
    required-variable error — there is no default to fall back to)."""
    m = re.fullmatch(r"\$\{SLAIF_LOCAL_CODING_IMAGE:\?(?P<message>[^}]*)\}", value)
    assert m, f"unexpected image field form: {value}"
    return env.get("SLAIF_LOCAL_CODING_IMAGE") or None


def test_canonical_compose_has_no_build_key() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert not re.search(r"^[ \t]+build:", text, re.MULTILINE), (
        "compose.yaml must not carry a build key (pull-based canonical)"
    )


def test_image_field_is_explicit_selection_with_no_silent_default() -> None:
    value = _image_field_value()
    assert value == IMAGE_FIELD
    # The `:?` operator means REQUIRED: there must be no `:-` default group
    # that could silently select a legacy tag.
    assert ":-" not in value
    assert re.fullmatch(r"\$\{SLAIF_LOCAL_CODING_IMAGE:\?.+\}", value)


def test_unset_variable_fails_closed_with_no_default() -> None:
    value = _image_field_value()
    rendered = _interpolate_image(value, {})
    assert rendered is None, (
        "an unset SLAIF_LOCAL_CODING_IMAGE must fail compose interpolation "
        "(required variable); no default group may exist"
    )
    # The message names the variable and the install doc.
    assert "SLAIF_LOCAL_CODING_IMAGE" in value
    assert "INSTALL.md" in value


def test_image_override_renders_verbatim_including_digest_pin() -> None:
    value = _image_field_value()
    plain = "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1"
    assert _interpolate_image(value, {"SLAIF_LOCAL_CODING_IMAGE": plain}) == plain
    digest_pin = "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:" + "0" * 64
    assert _interpolate_image(value, {"SLAIF_LOCAL_CODING_IMAGE": digest_pin}) == digest_pin
