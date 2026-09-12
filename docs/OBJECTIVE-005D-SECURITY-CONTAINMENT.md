# Objective-005-d security-containment record

## Classification

`SECURITY-CONTAINMENT`: an Objective-005-c diagnostic used a prohibited broad
pattern search that traversed host Codex session-cache JSONL. Cached session
prose consequently crossed into the coding agent's local tool-output/provider
context. No session content is reproduced here.

## Bounded impact facts

- The affected coding rollout was identified by rollout metadata; the real
  session filename, UUID, host identity, and cached prose are intentionally not
  retained.
- Pattern-only evidence found zero GitHub-token matches, zero private-key
  blocks, two unique OpenAI-style `sk-*` shapes across eight occurrences, and
  one unique long Bearer shape across four occurrences. These shapes are not
  safely attributable from content-free evidence.
- Temporary/synthetic database, secret, and token-shaped matches were also
  observed. No evidence proves that the protected Qwen credential or a
  persistent GitHub/OpenAI credential value was printed; this is not a formal
  secret-forensics guarantee.

## Containment

- Strategic containment changed the affected rollout mode from `0644` to
  `0600` without deleting or rewriting it.
- The disposable gateway database, generated rehearsal credentials, service,
  container, and PostgreSQL image were removed or made unusable as applicable.
- Repository-owned diagnostics now require paths beneath a driver-owned
  disposable root and an explicit subprocess allowlist. They do not construct
  host Codex-cache searches. Capture bodies are reduced to bounded tool-type
  and policy facts in memory, then discarded.

## Residual uncertainty and action

The bounded evidence cannot attribute the credential-shaped matches or prove
absence from the affected host cache. Human security review and rotation or
revocation of any credential potentially present in that cached session are
recommended according to the credential owner's policy. This repository does
not rotate credentials, delete sessions, change Codex profiles, or change
global permissions further.

Repository and GitHub artifacts for this incident contain no raw exposed
content, credential values, credential hashes, raw command output, session
prose, or sensitive session identifiers. This record is evidence of
containment, not a formal forensic clearance or production-security claim.
