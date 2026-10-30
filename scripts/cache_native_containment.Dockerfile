# Disposable containment-capability fixture image (objective 017-p).
#
# Reuses the repository's digest-pinned Python 3.12 base (the Dockerfile
# B1 law: no floating tags).  Contains ONLY the stdlib-only probe and a
# dedicated nonroot user: no repository source, no client binary, no
# model, no credentials.  Build/pull may use the public network; the
# runtime performs NO network access at all (run with --network none)
# and downloads nothing.
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ARG SLAIF_PROBE_UID=21001
ARG SLAIF_PROBE_GID=21001
RUN groupadd --gid "${SLAIF_PROBE_GID}" --system slaifprobe \
    && useradd --uid "${SLAIF_PROBE_UID}" --gid "${SLAIF_PROBE_GID}" --system \
        --home-dir /nonexistent --shell /usr/sbin/nologin slaifprobe

COPY cache_native_containment_probe.py /opt/slaif-containment-probe.py
USER slaifprobe
# Backstop for the probe's flushed-record law: non-TTY stdout is
# block-buffered, so the exact record must reach the pipe before the
# finite hang hold (the probe also flushes explicitly).
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/usr/local/bin/python3", "/opt/slaif-containment-probe.py"]
