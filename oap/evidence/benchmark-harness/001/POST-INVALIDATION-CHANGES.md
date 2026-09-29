# Post-invalidation repair inputs and changes

## Status boundary

Human authority cancelled and invalidated the harness before the changes in
this file were made. No preserved benchmark or qualification attempt used these
changes. They are supplied for code review and successor-harness development,
not as evidence that the defect is fixed in practice.

## Codex model metadata supplied after cancellation

The human supplied [`qwen-neumann-models.json`](qwen-neumann-models.json) and
required it to be committed verbatim. The candidate harness copies the same
bytes into every fresh worker as:

```text
~/.codex/qwen-neumann-models.json
```

Its SHA-256 is
`c6ad4d996815941a07849ac931f239857614bae255ecab6a566c0e109539f08f`.

Every generated worker `~/.codex/config.toml` points `model_catalog_json` at
that file. The catalog establishes:

- model slug `qwen3.8-27b`;
- context and maximum context window of 262,144 tokens;
- automatic compaction threshold of 222,000 tokens;
- default reasoning level `xhigh`, with `low`, `medium`, and `xhigh` declared;
- text and image input modalities;
- unified-exec shell and freeform apply-patch metadata.

The candidate validator rejects a site whose served model, context window,
compaction threshold, or required reasoning level disagrees with the catalog.

## Codex worker configuration supplied after cancellation

The human also supplied a Codex TOML used in another environment. The safe
adaptation is preserved as
[`subject-config.reference.toml`](subject-config.reference.toml). The candidate
harness renders the same material into every fresh worker home with these
benchmark-specific adaptations:

- the provider identifier is `qwen-LSI-A100`;
- the URL is rendered as the measured LAN URL for DIRECT or the isolated
  loopback adapter URL for VISION/CACHE/BOTH;
- the credential is read from `BENCH_API_KEY`, not stored in TOML;
- apps, MCP apps, and plugins are disabled;
- subject reasoning is mandatorily `xhigh`.

The adapter compiler's own `reasoning_effort` remains a distinct frozen
product-treatment setting. It is not the Codex subject reasoning setting.

## Difference from the invalid-attempt configuration

The invalid attempts used scalar Codex settings with a 196,608-token automatic
compaction value and subject reasoning `low`, but did not install a custom model
catalog into each fresh subject home. The candidate source archive changes that
configuration to the supplied catalog, 222,000-token threshold, and mandatory
subject `xhigh`.

## Future two-GPU requirement

After cancellation, the human also directed that future testing use GPUs 2 and
3 in parallel. This is not represented as an implemented or qualified feature
in archive 001. At archive time GPU3 was the only dedicated benchmark lane;
GPU2 belonged to a protected service. A successor protocol may add GPU2 only
after the host operator provides a separately authorized endpoint, immutable
model/runtime identity, credential scope, recorder attribution, and confirmation
that GPU2 is no longer part of the protected service. It requires a new
protocol/site/freeze identity and must never be implemented by sending benchmark
traffic to the protected port 8000 service.

## Public-disclosure consequence

Archive 001 includes the historical tasks, evaluators, visual rubric, and
context answer key because the human required the whole harness to be handed to
the repository owner. Their publication is appropriate for diagnosis of this
invalid harness, but permanently disqualifies them from reuse as hidden material
in a successor benchmark.
