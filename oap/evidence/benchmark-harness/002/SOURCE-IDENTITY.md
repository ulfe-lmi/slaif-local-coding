# Source and runtime identity

## Public source snapshot

- Current audit identity:
  `slaif-benchmark-kit-gpu23-context-gate-pre-freeze-20260930.8`.
- Status: pre-freeze; qualification false.
- `harness.tar.gz` SHA-256:
  `d1a880535dfc37c3d039e9cd9b23773a16ad838c45a68c1caca705e27b684332`.
- Extracted regular files: 110.
- Model-catalog SHA-256:
  `c6ad4d996815941a07849ac931f239857614bae255ecab6a566c0e109539f08f`.
- Subject reasoning: mandatory `xhigh`.
- Declared physical context: 262,144 tokens.
- Declared automatic compaction threshold: 222,000 tokens.
- Maximum measured concurrency: two subjects, one per lane.

## Executed attempt chronology

The two first Web CACHE attempts retain identity
`slaif-benchmark-kit-gpu23-catalog-xhigh-pre-freeze-20260929.5`. The following
twelve mixed qualification attempts retain identity
`slaif-benchmark-kit-gpu23-mixed-qualification-pre-freeze-20260929.6`.
Post-run audit identities `.7` and `.8` preserve and analyze those attempts;
they do not claim the attempts were rerun or rewritten.

## Client and immutable images

- Subject client: Codex CLI 0.149.0.
- Subject worker image ID:
  `sha256:094da60913f5af301c004a676bd9053e009068ea4d722c94be9b81f07a61e16e`.
- Product candidate: `slaif-local-coding` 0.1.0-rc7.
- Product source commit:
  `ae6271318627703785f42de57d893c9be3b980c9`.
- Product image digest:
  `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`.
- Merged RC7 record commit:
  `d0bf3a47eec6b52b0127f8cac5e483c8c0f5b13c`.

The measured backend consisted of two independent replicas of the same
`qwen3.8-27b` checkpoint/configuration on physical A100-class devices. Physical
UUIDs and private addresses are excluded from the public archive.
