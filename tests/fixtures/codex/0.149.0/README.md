# Sanitized Codex 0.149.0 fixtures

`project_instructions_responses.json` is the canonical minimized current-Codex
fixture. Three fresh disposable Codex CLI 0.149.0 runs on 2026-08-21 each completed
the fake Responses endpoint, placed exactly one project block in a top-level
user/`input_text` item, omitted a project block from top-level `instructions`, and
normalized to byte-identical fixture bytes. The logical repository label and
environment tail are synthetic privacy mappings; only exact inner instruction
bytes are hashed and enumerated.

This corrects, without rewriting immutable reports, the historical `001-a`
captured-developer claim. The old developer project fixture is removed. The
input-file and paired-tool JSON fixtures remain synthetic supplemental tested
shapes, not captured or future-version compatibility claims.

The detector requires one exact block at a top-level Responses user/`input_text`
position: `# AGENTS.md instructions for <label>`, a blank line, `<INSTRUCTIONS>`,
exact UTF-8 inner bytes, and `</INSTRUCTIONS>`. Only a terminal newline or the
captured structural `<environment_context>` tail may follow; tail bytes are not
source bytes. A parseable top-level `instructions` block is optional corroboration
and must match the safe logical label and exact inner content. Plain mentions,
wrong roles/types/parents, malformed/duplicate blocks, unsupported tails, and
unsafe labels do not establish a root. A manually constructed exact supported
user envelope intentionally has the same effective-governance meaning and is
therefore evidence; this is a client-supplied trust boundary.

To refresh safely from the repository root:

```bash
python3 tests/helpers/capture_codex_project_envelope.py \
  --codex-bin codex --output /tmp/project_instructions_responses.json
```

The helper creates a temporary `CODEX_HOME`, Git repository, model catalog, and
loopback fake Responses endpoint. It uses only synthetic `AGENTS.md` bytes, model,
credential, response, and prompt. The raw request remains in memory. Before writing,
the minimizer allowlists exactly one supported user occurrence, zero or one matching
instructions occurrence, and the captured suffix grammar. Output contains only the
synthetic model, canonical user item, privacy-mapped label/content, synthetic tail,
with no provenance-only fields. Safe synthetic provenance is stored separately in
`project_instructions_provenance.json`; its fixed schema contains only marker count,
logical label, content byte length/hash, and a synthetic-only flag, and it is never
passed to `observe_request` or an upstream. Optional corroboration is printed only as a sanitized
run fact, so it cannot alter fixture bytes. Raw bodies, internal instructions,
host paths, IDs, tools, user prompts, environment content, auth, headers, and
responses are never written or printed.

This remains observation-only and request-only. It provides no compiler, ranking,
cache, acquisition, injection, rehydration, semantic-governance, compaction, or
future Codex-version guarantee.
