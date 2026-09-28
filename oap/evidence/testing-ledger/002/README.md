# Testing ledger 002 — real Codex RC3 qualification (PASS)

## Purpose

This append-only ledger entry records the bounded standalone real-Codex
qualification of `slaif-local-coding` 0.1.0-rc3 performed by the opt-in,
fail-closed, privacy-bounded repository gate
(`scripts/real_codex_rc_qualification.py`). It is documentation and
sanitized evidence, not an accepted fix, release acceptance, benchmark
result, or authorization to modify a deployed service.

## Qualified identities

- Product source (image build commit `S`):
  `307a929ffb30f4ea41c8be4e8a5ea25802e25142`
- Product OCI digest `D`:
  `sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436`
  (tags `0.1.0-rc3` and `sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142`)
- Product wheel `W` (byte-identical across builds; re-verified equal to the
  committed manifest at publication):
  `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
- Subject client: Codex CLI 0.149.0
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
- Responses model name: `qwen3.8-27b`
- Topology: disposable Codex home/repository → `127.0.0.1:18031` Local
  Coding → existing tested endpoint; **no SLAIF API Gateway** (gateway
  ingress disabled, no signed Gateway headers)
- Gate schema: `slaif-real-codex-rc-qualification-v1`
- Run date: 2026-09-28 UTC

## Result

Overall verdict: **PASS** (all three required product arms pass; protected
state unchanged; disposable state removed).

- **VISION**: verdict `PASS` — attempts 1, exit 0, sentinel present (3 bytes), adapter 200/500/422 = 2/0/0, upstream failures 0, compiler cache entries 0, duration 4s, failure class `none`.
- **CACHE**: verdict `PASS` — attempts 1, exit 0, sentinel present (3 bytes), adapter 200/500/422 = 2/0/0, upstream failures 0, compiler cache entries 1, duration 35s, failure class `none`.
- **BOTH**: verdict `PASS` — attempts 1, exit 0, sentinel present (3 bytes), adapter 200/500/422 = 2/0/0, upstream failures 0, compiler cache entries 1, duration 40s, failure class `none`.
- **DIRECT**: verdict `PASS` — attempts 1, exit 0, sentinel present (3 bytes), adapter 200/500/422 = 0/0/0, upstream failures 0, compiler cache entries 0, duration 5s, failure class `none`.

The CACHE and BOTH arms demonstrate the full constitutional path end to end
(deterministic AGENTS.md observation from a genuine Codex project envelope →
compiler over the direct authenticated upstream channel → one derived-cache
entry each) while the VISION arm demonstrates the one-image `retain_newest`
route policy with the compatibility repair in place. DIRECT is a contextual
backend control and never substitutes for a product arm.

## Protected state

13 protected files checked, 0 changed; units `qwen-serving-vision.service`
(active) and `qwen-serving.service` (inactive) unchanged; port 18020 held
exactly one listener and 18031 was free before and after. No protected
model, vLLM, network, or service state was altered.

## Environment note

The protected host forbids the unprivileged user-namespace network setup that
bubblewrap requires, so the genuine client runs with its client-side sandbox
set to `danger-full-access`. The gate's own boundary is the control: fresh
disposable workspace and Codex home, loopback-only adapter, fixed synthetic
prompt, no credentials in argv, bounded attempts and timeouts, sanitized
facts only.

## Evidence

[real-codex-rc3-qualification.json](real-codex-rc3-qualification.json) is the
gate's closed-schema sanitized facts record. It contains only fixed
categories, counts, statuses, version/hash, timings, and boolean verdicts —
no prompt, source, tool argument or output, request/response body, image,
credential, private URL, or session ID.
