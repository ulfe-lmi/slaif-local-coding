# SLAIF Local Coding — production runtime image (order 011-a, workstream B).
#
# Linux Docker Engine only. Multi-stage: the build stage produces the locked
# wheel; the runtime stage contains NO repository source checkout (no src/,
# no .git, no oap/, no tests/, no references/, no caches, no placeholder
# files) — only the non-editable wheel install, its frozen locked
# dependencies, the built wheel artifact (for the in-image provenance proof),
# and the dedicated non-root runtime user.
#
# Every base image is pinned: the build stage by immutable version tag plus
# digest, the runtime stage by digest (B1: no unpinned floating base tags
# anywhere). Outbound connectivity is required at build time only (base
# image pulls and the locked build-backend resolution); the runtime performs
# no package downloads.

# --- uv provider stage: pinned by digest; the static uv binary only -----
# (the uv image is distroless: no shell; it is only a binary source)
FROM ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 AS uv-provider

# --- Build stage: pinned base + pinned uv builds the locked wheel --------
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS build

COPY --from=uv-provider /uv /usr/local/bin/uv
WORKDIR /build
# Exactly what the wheel build needs (see .dockerignore); the committed
# uv.lock pins every runtime dependency.
COPY pyproject.toml uv.lock LICENSE NOTICE README.md ./
COPY src/ src/
RUN uv build --wheel --out-dir /build/wheel

# --- Runtime stage: pinned by digest, wheel-based, non-root ---------------
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS runtime

ARG SLAIF_UID=10001
ARG SLAIF_GID=10001
RUN groupadd --gid "${SLAIF_GID}" --system slaif \
 && useradd --uid "${SLAIF_UID}" --gid "${SLAIF_GID}" --system --home-dir /opt/slaif --shell /usr/sbin/nologin slaif

# Projected provenance (B6). All ARGs are non-secret build facts; CI records
# them in the report. The wheel SHA-256 is the committed provenance-manifest
# wheel hash bound to this image (B8/C2).
ARG SLAIF_GIT_SHA=unknown
ARG SLAIF_PACKAGE_VERSION=0.1.0
ARG SLAIF_GATEWAY_PEER_SHA=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb
ARG SLAIF_WHEEL_SHA256=
ARG SLAIF_IMAGE_CREATED=unknown
LABEL org.opencontainers.image.source="https://github.com/ulfe-lmi/slaif-local-coding" \
      org.opencontainers.image.revision="${SLAIF_GIT_SHA}" \
      org.opencontainers.image.version="${SLAIF_PACKAGE_VERSION}" \
      org.opencontainers.image.created="${SLAIF_IMAGE_CREATED}" \
      slaif-local-coding.package.version="${SLAIF_PACKAGE_VERSION}" \
      slaif-local-coding.gateway.peer.sha="${SLAIF_GATEWAY_PEER_SHA}" \
      slaif-local-coding.topology.mode="linux-docker-host-network;loopback-default;lan-visible-only-with-full-signed-ingress" \
      slaif-local-coding.qualification="disposable-qualification-only; not released" \
      slaif-local-coding.wheel.sha256="${SLAIF_WHEEL_SHA256}"

# Runtime dependencies resolved from the committed uv.lock (frozen), then the
# built wheel installed NON-EDITABLE from the artifact (no repository source
# remains in this stage). The uv build cache is confined to /build and wiped
# by the same RUN: the runtime stage contains NO caches.
COPY --from=build /usr/local/bin/uv /usr/local/bin/uv
COPY pyproject.toml uv.lock /build/
WORKDIR /build
ENV UV_CACHE_DIR=/build/uv-cache
RUN uv venv /opt/slaif/venv \
 && VIRTUAL_ENV=/opt/slaif/venv uv sync --frozen --no-dev --no-install-project \
 && rm -rf /build

# The built wheel is retained inside the image solely for the mechanical
# in-image provenance proof (B8: its SHA-256 must equal the provenance
# manifest wheel hash); it is not executed from this path.
COPY --from=build /build/wheel/slaif_local_coding-0.1.0-py3-none-any.whl /opt/slaif/artifacts/
RUN uv pip install --python /opt/slaif/venv/bin/python \
        /opt/slaif/artifacts/slaif_local_coding-0.1.0-py3-none-any.whl \
 && chown -R slaif:slaif /opt/slaif \
 && rm -rf /build

# The mounted configuration (read-only, from the host) is the single input.
# /tmp and /dev/shm are bounded tmpfs in the compose definition; the
# root filesystem is read-only there.
USER slaif
WORKDIR /opt/slaif
ENTRYPOINT ["/opt/slaif/venv/bin/slaif-local-coding"]
CMD ["--config=/etc/slaif/adapter.toml"]
