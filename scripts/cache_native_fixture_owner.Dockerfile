# Disposable serial right-pane owner-UID fixture image variant
# (objective 017-aa).
#
# The EXPLICIT owner-profile variant of the 017-r fixture image: the
# SAME digest-pinned Python 3.12 base (B1 law: no floating tags), the
# SAME dedicated nonprivileged controller (UID/GID 21001), the SAME
# pinned public Codex 0.164.0 static artifact with its public LICENSE
# and NOTICE identities, and the SAME confinement.  The only deltas
# are: the subject identity (created from the EXACT frozen validated
# build ARGs — there is NO subject default); the EXPLICIT image-owned
# identity-mode CONSTANT file (a generated closed single-constant
# Python source, root-owned 0444, an immutable image fact — the
# ONLY selector of the owner-UID stand-in identity law; the original
# image never bakes it, so its fixed-21002 law stays byte-for-byte
# even if an arbitrary file sits at the DATA path); and the baked
# closed profile DATA file, the bounded subject-identity record
# required by the owner mode.
# Missing DATA, an unknown profile, a grammar failure, a controller
# collision or an ARG/data mismatch exits the build step nonzero:
# the build FAILS CLOSED and never falls back to the original
# profile.  Every fixture Python source and the DATA file is
# root-owned 0444 on the read-only rootfs, chowned/chmodded inside
# the image, so controller and subject read them immutably regardless
# of the protected host build-context mode (a 077/0600 host context
# is never relied upon for in-image readability).  The original
# fixture Dockerfile and its default fixed-21002 image stay
# byte-for-byte unchanged; no path, test or job of this variant
# executes the native binary.
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ARG SLAIF_CTL_UID=21001
ARG SLAIF_CTL_GID=21001
# No subject defaults: the variant build must pass the exact frozen
# validated IDs explicitly (the owner-scoped closed build form).  An
# empty or malformed value fails the closed validation step below.
ARG SLAIF_SUBJ_UID
ARG SLAIF_SUBJ_GID
# The profile-name ARG (NO default): the variant build must explicitly
# pass the frozen owner-uid profile name; the closed validation step
# asserts it equals the production constant, so every build ARG of the
# owner-scoped closed form is consumed and verified.
ARG SLAIF_FIXTURE_PROFILE

# The inert fixture identity contract module (closed bounded codec +
# strict production validation; inert: no filesystem/env/network/
# process access in the module itself) and the baked closed profile
# DATA record (the Z canonical record bytes written by the owner from
# its frozen description; a data file, never host authority).
COPY cache_native_fixture_identity.py /opt/slaif-fixture/cache_native_fixture_identity.py
COPY fixture-identity.json /opt/slaif-fixture/fixture-identity.json
COPY cache_native_fixture_model.py /opt/slaif-fixture/cache_native_fixture_model.py
COPY cache_native_fixture_controller.py /opt/slaif-fixture/cache_native_fixture_controller.py
COPY cache_native_fixture_standin.py /opt/slaif-fixture/cache_native_fixture_standin.py
COPY cache_native_fixture_export_client.py /opt/slaif-fixture/cache_native_fixture_export_client.py

# Closed build-time profile validation with the PRODUCTION codec and
# validator (the file read happens in this one-time build step, never
# in the inert module or at runtime).  The DATA record must decode as
# the closed canonical record of the owner-UID profile with the fixed
# controller identity and a subject distinct from the controller, and
# its subject IDs must EQUAL the explicit build ARGs — any missing /
# unknown / mismatched / unsafe DATA fails the build closed.  The
# validated IDs are then the exact user/group creation values, and
# every fixture source and the DATA file is made root-owned 0444
# (immutable, readable by controller and subject on the read-only
# rootfs, independent of the host build-context mode).  The same
# step GENERATES the explicit image-owned identity-mode constant
# file (a closed single-constant Python source, root-owned 0444,
# parsed never executed by the stand-in): an immutable image fact,
# not runtime-overridable — it is the ONLY selector of the
# owner-UID stand-in identity law.  The Python
# payload is ONE physical line: Dockerfile-level continuations strip
# newlines, so raw newlines are invalid inside the single-quoted
# -c string (the only continuations are backslashes AFTER the
# closing quote).
RUN python3 -c 'import sys; sys.path.insert(0, "/opt/slaif-fixture"); import cache_native_fixture_identity as ident; desc = ident.decode_description(open("/opt/slaif-fixture/fixture-identity.json", "rb").read()); assert desc.profile == ident.PROFILE_OWNER_UID, "profile-mismatch"; assert (desc.controller_uid, desc.controller_gid) == (ident.CONTROLLER_UID, ident.CONTROLLER_GID), "controller-mismatch"; assert desc.subject_uid == int(sys.argv[1]), "subject-uid-mismatch"; assert desc.subject_gid == int(sys.argv[2]), "subject-gid-mismatch"; assert sys.argv[3] == ident.PROFILE_OWNER_UID, "profile-arg-mismatch"' "${SLAIF_SUBJ_UID}" "${SLAIF_SUBJ_GID}" "${SLAIF_FIXTURE_PROFILE}" \
    && printf 'SLAIF_FIXTURE_IDENTITY_PROFILE = "slaif-fixture-identity-owner-uid-v1"\n' > /opt/slaif-fixture/identity_profile.py \
    && chown root:root /opt/slaif-fixture \
    && chown root:root /opt/slaif-fixture/*.py /opt/slaif-fixture/fixture-identity.json \
    && chmod 0444 /opt/slaif-fixture/*.py /opt/slaif-fixture/fixture-identity.json \
    && groupadd --gid "${SLAIF_CTL_GID}" --system slaifctl \
    && useradd --uid "${SLAIF_CTL_UID}" --gid "${SLAIF_CTL_GID}" --system \
        --home-dir /nonexistent --shell /usr/sbin/nologin slaifctl \
    && groupadd --gid "${SLAIF_SUBJ_GID}" --system slaifsubj \
    && useradd --uid "${SLAIF_SUBJ_UID}" --gid "${SLAIF_SUBJ_GID}" --system \
        --home-dir /nonexistent --shell /usr/sbin/nologin slaifsubj

# The pinned public artifact (fetched, size+digest verified, and
# bounded-extracted by the runner) is installed as the native PATH
# entry under its public artifact name; the public license and NOTICE
# identities stay separate immutable files.  Immutable: root-owned
# 0555 / 0444 on a read-only rootfs (readable+executable, never
# writable, by anyone).  No path of this variant executes the binary.
COPY codex-x86_64-unknown-linux-musl /usr/local/bin/codex
COPY codex-0.164.0-license.txt /opt/slaif-native/codex-0.164.0-license.txt
COPY codex-0.164.0-notice.txt /opt/slaif-native/codex-0.164.0-notice.txt
RUN chmod 0555 /usr/local/bin/codex \
    && chown root:root /usr/local/bin/codex \
    && chmod 0444 /opt/slaif-native/codex-0.164.0-license.txt \
    && chmod 0444 /opt/slaif-native/codex-0.164.0-notice.txt \
    && chown root:root /opt/slaif-native

USER slaifctl
# Backstop for the flushed-record law: non-TTY stdout is
# block-buffered, so closed records must reach the pipe before any
# finite hold (the stand-in also flushes explicitly).
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/usr/local/bin/python3", "/opt/slaif-fixture/cache_native_fixture_controller.py"]
