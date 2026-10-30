# Disposable serial right-pane native fixture image (objective 017-r).
#
# Reuses the repository's digest-pinned Python 3.12 base (Dockerfile
# B1 law: no floating tags).  Contains ONLY the stdlib-only fixture
# modules, the dedicated nonprivileged controller/exporter user
# (UID/GID 21001), the native-subject user (UID/GID 21002), and the
# pinned public Codex 0.164.0 static artifact copied in by the
# runner's reviewed build context.  The native binary is prepared as
# an IMMUTABLE EXECUTABLE PATH ENTRY (root:root 0555, read-only
# rootfs) so the later human-authorized foreground handoff
# (docker exec --user 21002:21002 ... codex --yolo --profile
# early-beta) is concretely possible from this exact image.  The R
# CI invokes ONLY Python: the executable bit is not authorization,
# and no R path, test or job ever executes the binary (the runner
# statically asserts this).  Build/pull may use the public network;
# the runtime performs NO network access beyond the container's
# private loopback (run with --network none) and downloads nothing.
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ARG SLAIF_CTL_UID=21001
ARG SLAIF_CTL_GID=21001
ARG SLAIF_SUBJ_UID=21002
ARG SLAIF_SUBJ_GID=21002
RUN groupadd --gid "${SLAIF_CTL_GID}" --system slaifctl \
    && useradd --uid "${SLAIF_CTL_UID}" --gid "${SLAIF_CTL_GID}" --system \
        --home-dir /nonexistent --shell /usr/sbin/nologin slaifctl \
    && groupadd --gid "${SLAIF_SUBJ_GID}" --system slaifsubj \
    && useradd --uid "${SLAIF_SUBJ_UID}" --gid "${SLAIF_SUBJ_GID}" --system \
        --home-dir /nonexistent --shell /usr/sbin/nologin slaifsubj

# Reviewable fixture sources (byte-identity verified by the runner
# against the repository before build).
COPY cache_native_fixture_model.py /opt/slaif-fixture/cache_native_fixture_model.py
COPY cache_native_fixture_controller.py /opt/slaif-fixture/cache_native_fixture_controller.py
COPY cache_native_fixture_standin.py /opt/slaif-fixture/cache_native_fixture_standin.py
COPY cache_native_fixture_export_client.py /opt/slaif-fixture/cache_native_fixture_export_client.py
# The pinned public artifact (fetched, size+digest verified, and
# bounded-extracted by the runner) is installed as the native PATH
# entry under its public artifact name; the public license and
# NOTICE identities stay separate immutable files (the NOTICE
# credits the included Ratatui-derived code under MIT — the pinned
# upstream publishes it and it is retained, never dropped).
# Immutable: root-owned 0555 / 0444 on a read-only rootfs
# (readable+executable, never writable, by anyone).
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
