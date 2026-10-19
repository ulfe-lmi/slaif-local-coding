# Bundle observation contract (objective 017, D01-D05 slice)

**Status:** Implemented as an inert, typed, pure module set. **Not active in
the adapter.** The modules under
`src/slaif_local_coding/constitution/bundles/` are not wired into the legacy
request execution path, the graph/cache/compiler, or any runtime stage; they
exist behind the planned v1 package boundary for the subsequent stages (018+).
The legacy detector and its behavior are unchanged.

This document is the versioned contract for the first observation slice of
the dependency-bundle cache rework (D01-D05 in
[the stage ledger](CACHE-REWORK-LEDGER.md)). The accepted design authority is
[the human handoff](CACHE-REWORK.md); the resolved engineering choices are in
[the implementation plan](CACHE-IMPLEMENTATION-PLAN.md); delivery state is in
[the stage ledger](CACHE-REWORK-LEDGER.md). D06-D10 (chained reads, literal
loops, per-read vs global exit evidence, multi-chunk pairing and remaining
truncation matrix) are NOT implemented here; they are planned for later
same-PR suffixes (planned 017-c/d). Round 017-b corrected the 017-a
observation proof defects (findings A-E) without adding read families.

## 1. Modules and versions

| Constant | Value | Covers |
|---|---|---|
| `OBSERVER_VERSION` | `cache-bundle-observation/1` | this pure observation stage |
| `ENVELOPE_FORMAT` | `codex-project-instructions/v1` | root delimiter contract |
| `READ_GRAMMAR` | `literal-shell-read/v1` | command grammar |
| `TOOL_WRAPPER_FORMAT` | `codex-exec-wrapper/v1` | exec wrapper text form |

Modules: `observation_models.py` (typed results, spans, digests, bounds),
`client_paths.py` (literal client-workspace path normalization),
`root_envelopes.py` (D01/D02 envelope observation), `read_grammar.py`
(D03/D04 literal command grammar), `tool_results.py` (D05 pairing and
wrapper), `observe.py` (pure composition entry point
`observe_request`).

Coordinate law: every span is a half-open pair of **character offsets into the
exact decoded JSON string** that carried the source (`CharSpan`).
`CharSpan.to_byte_span(text)` converts to exact UTF-8 byte offsets over that
same string; the two domains are never mixed. Digests are
`sha256(text.encode("utf-8"))` over the exact observed bytes; they assert
nothing about the original filesystem encoding. Malformed (lone surrogate)
strings are rejected with `MALFORMED_UNICODE` before any hashing — never a
crash. A digest field is explicitly absent (`None`) only under that typed
malformed/unsupported contract; a placeholder digest is never treated as
valid, and an unhashable observation stays non-removable and ineligible for
later graph/cache admission.

## 2. Root envelope contract (D01/D02)

Recognized endpoint: Responses `input` array, `role="user"`,
`content[].type="input_text"`, and only an item whose text **starts at
character 0** with the header. Exact grammar (each `T` is `LF` or `CRLF`):

```text
# AGENTS.md instructions for <label> T T <INSTRUCTIONS> T
<source content> T </INSTRUCTIONS>
[ T? <environment_context> T <environment body> T </environment_context> ]
```

- `<label>` is the exact directory scope: non-empty, no control characters,
  bounded in **UTF-8 bytes** (`max_label_bytes`; 9 bytes for `/éééé`, so an
  8-byte limit rejects it although the label is only 5 characters); it is
  recorded verbatim (no normalization, no host mapping). A label may be a
  POSIX absolute path or a logical label; only an explicit validated
  client-workspace context (section 3) performs path normalization.
- `<source content>` is the exact inner bytes: everything after the opening
  tag line's terminator and up to (excluding) the closing tag's own
  line-start newline (LF or CRLF). Internal Unicode and CRLF bytes are
  preserved as source; a blank line before the closing tag keeps its newline
  in the source bytes. The closing tag must stand on its own line; an earlier
  literal `</INSTRUCTIONS>` not on its own line, or a nested `<INSTRUCTIONS>`
  inside the content, is ambiguous and rejected (never retried) — the same
  law as the legacy detector.
- Optional environment tail forms, all excluded from the source bytes and
  preserved as spans: (a) adjacent — `</INSTRUCTIONS><environment_context>…`
  with no separator; (b) newline-separated — one `T` between the closing tag
  and the block; (c) separate item — a user `input_text` item whose entire
  text is a well-formed `<environment_context> T … T </environment_context>`
  block. The item must end exactly at the closing tag; a trailing newline
  after the block is an unsupported shape (typed, never trimmed).
- The environment body must start and end with a newline inside the block
  (observed Codex shape).

Authority law: assistant/developer/system/tool text, quoted marker prose at
any later offset, and top-level `instructions` text never create root
authority. The Chat endpoint is `UNSUPPORTED_ENDPOINT` for root observation in
this slice (the legacy detector keeps its own behavior on the legacy path).

Aggregation law: repeated byte- and scope-identical roots are idempotent —
every occurrence span is preserved for later edits. Same-scope differing
content yields `VERSION_CANDIDATES` (each candidate: scope, digest,
occurrence locations) for 018 temporal/replay resolution; a candidate is not
a conflict and no newest-content choice is made. Differing scope labels are
`COMPETING_ROOT_SCOPES` (explicit conflict). A malformed occurrence never
creates authority, is recorded with its typed reason, and does not destroy a
separately proven valid root (a deliberate, documented difference from the
legacy all-or-nothing rule).

## 3. Client path grammar (D03/D04)

Paths live in a separate client-workspace domain. Normalization is strictly
lexical; it never subprocesses, expands environment variables or globs,
resolves symlinks, or stats/reads the client or adapter filesystem. A path
that does not exist on the client still normalizes.

- **Workspace context.** `PathContext.workspace` must be an evidenced literal
  absolute POSIX path (component-collapsed, no `..`, no backslash/UNC/drive,
  no control characters, bounded). A logical scope (e.g. `repo`) is not a
  POSIX workspace: absolute operands are `UNKNOWN_WORKSPACE`, relative
  operands `UNPROVEN_CWD`. There is no adapter-host cwd and no inference from
  prose or headers.
- **Absolute operands.** Accepted only when the component sequence extends
  the workspace's component sequence (component comparison, never
  string-prefix comparison: `/work-other/A.md` is outside `/work`).
- **Relative operands.** Resolve against the explicit supported workdir
  (itself validated inside the workspace), else the evidenced workspace (the
  evidenced default client cwd). The workdir may be the batch context workdir
  or the **per-call** workdir carried by a supported call-arguments object
  (section 4); a per-call workdir takes precedence over the batch default for
  that call and, when it does not validate inside the evidenced workspace,
  the affected reads are typed (e.g. `OUTSIDE_WORKSPACE`) — never silently
  re-resolved against the batch context or an adapter-host cwd.
- **Lexical `.`/`..` policy.** Segments resolve lexically; any resolution
  step whose prefix leaves the workspace is `TRAVERSAL` (e.g.
  `/work/../A.md` with workspace `/work`). A `..` at the workspace boundary
  is traversal. Staying-inside resolution is kept, e.g.
  `/work/docs/../A.md` → `A.md`.
- **Literal operands.** Operands are literal path tokens. URL fragment
  syntax is literal: `A.md#frag` is a different file from `A.md` and is
  never stripped or mapped onto `A.md`. `?` is shell glob syntax, so
  `A.md?x=1` is non-literal and typed (`NON_LITERAL_OPERAND`), never mapped
  onto `A.md`. A fully-quoted operand (`"A.md"`) is the same literal path
  under the agreed no-spaces file convention and is recorded with
  `quoted=True`; partial or nested quotes are `QUOTED_OPERAND`.
- **Non-literal operands.** Any shell metacharacter (`$`, backtick, `\`,
  `*`, `?`, `[`, `]`, `{`, `}`, `~`, `^`, `|`, `&`, `;`, `<`, `>`, `(`, `)`,
  `!`) makes the operand non-literal (`NON_LITERAL_OPERAND` /
  `UNSUPPORTED_PATH_FORM` / `QUOTED_OPERAND` as appropriate); nothing is
  expanded or executed.
- **Bounds.** Operand bytes are bounded (`max_path_bytes`); over-bound
  operands are `PATH_TOO_LONG`.

## 4. Read command grammar (D03/D04)

The earned literal surface in this slice is exactly:

```text
cat <operand>
cat -- <operand>
cat <operand> <operand> ...        (bounded operand count)
```

- Tokenization is literal whitespace splitting; no quote-aware parsing
  beyond the fully-quoted operand rule, no shell parsing (no new external
  shell parser dependency), no execution, no environment/glob expansion.
- **Option terminator.** The first `--` after the executable is processed
  once as the option terminator. A later `--` token is a **literal operand**
  and stays in the actual complete member list (e.g. `cat -- A.md -- B.md`
  has members `A.md`, `--`, `B.md`): it is never silently dropped and its
  output is never attributed to fewer members than were actually requested.
- **Per-call workdir.** The supported argument object may carry a `workdir`
  string (a literal absolute client path); it is validated against the
  evidenced workspace at normalization time. A non-string, empty, or
  control-bearing `workdir` makes the argument shape typed unsupported.
- **Malformed Unicode.** A command string containing lone surrogates is
  rejected with `MALFORMED_UNICODE` before any UTF-8 hashing; its
  `command_digest` is explicitly absent (never a placeholder) and no
  operand is normalized or proven.
- **Argument decoding bounds.** A raw JSON-string argument longer than the
  worst case of the command bound plus JSON wrapper/escaping overhead
  (`2 * max_command_chars + 128`) is typed unsupported without being parsed;
  decode errors (including nesting-depth `RecursionError`) return the same
  typed result. No broad exception swallowing.
- The executable must be exactly `cat`. Flags (`-n`, …), other executables
  (`head`, `tail`, `sed`, …), path-prefixed cats (`/bin/cat`), and unknown
  syntax are typed (`COMMAND_UNSUPPORTED` / `FRAGMENT_COMMAND`).
- A token containing substitution (`$`, backtick) is `COMMAND_SUBSTITUTION`;
  `\` is `SHELL_ESCAPE`; `*?[]` are `GLOB_UNPROVEN`; `<`/`>` are
  `REDIRECTION`; `|` is `PIPE`; `&`/`;` are `MULTIPLE_COMMANDS`; a
  `#`-starting token is `COMMENT_PRESENT` and terminates the line. A loop or
  branch is a compound command, not a read.
- A command string containing newlines is `MULTIPLE_COMMANDS`. Commands are
  bounded (`max_command_chars`); operand counts are bounded
  (`max_operands`).
- Supported argument shapes (documented envelope forms): a JSON string or
  object with a `cmd`/`command` string; an argv list that is exactly one
  string or exactly `[bash|sh|zsh, -c|-lc, <string>]`. Other shapes are
  typed unsupported.

## 5. Tool call/result pairing and wrapper (D05)

- **Eligibility.** Only `exec_command` and `shell_command` are supported
  bare names; a declared unrelated bare function with a `cmd`-shaped
  parameter is **not** an exec tool. A namespace-qualified name (containing
  `/`) is eligible only when **both** hold: its **leaf** (the part after the
  last `/`) is a known executable supported name, and the request's own
  `tools` array declares the exact name with the compatible `cmd` string
  schema. Suffix or substring resemblance alone is never evidence.
  `write_stdin` is recognized and typed `WRITE_STDIN_CHUNK` (deferred in
  this slice).
- **Pairing.** Calls and results pair by exact call ID **and within the same
  endpoint envelope**: a Responses `function_call` pairs only with a
  Responses `function_call_output`, and a Chat assistant `tool_calls` entry
  pairs only with a Chat `role=tool` message. An ID match across endpoints
  is never evidence — the call is typed `MISSING_CALL_RESULT` and the
  foreign result typed `MISMATCHED_CALL_ID` (ambiguous mixed shapes are
  typed, never globally guessed). Duplicate call IDs are `DUPLICATE_CALL_ID`
  (both occurrences recorded, never first-match). Missing results are
  `MISSING_CALL_RESULT`. Results without a supported call are
  `MISMATCHED_CALL_ID`. Multiple results for one call are
  `MULTI_CHUNK_DEFERRED` (multi-chunk completion proof is D09, later
  same-PR suffix).
- **Wrapper grammar.** Recognized header lines before the `Output:` marker
  line: the human-handoff 6.2 real format `Chunk ID: <token>` plus the
  explicitly earned compatible variant `Chunk Id: <token>`, `Wall time:
  <…>`, `Process exited with code <0-255>`, and `Truncated: true|false`, and
  `Process is still running` (typed `PROCESS_RUNNING`, deferred). The exit
  value uses a bounded canonical ASCII decimal grammar (0..255, at most
  three digits, no leading zeros): Unicode digit-likes (`²`) and over-long
  fields are typed, never `int()`-converted (no crash, no unbounded work).
  Each status field (exit code, truncation) appears **at most once**: any
  repetition — contradictory or identical — is `MALFORMED_WRAPPER` with no
  trusted status (never last-field-wins). The declared
  `max_wrapper_header_lines` bound is enforced before the frame is
  accepted: an over-bound header block is typed `OVER_BOUND`, never
  complete. The `Output:` line must be newline-terminated; everything after
  it is the exact source region (its character span is `content_span`). A
  header line that is not recognized is `MALFORMED_WRAPPER` when headers
  were already seen, otherwise `UNKNOWN_COMPLETION` (plain unstructured
  output). A missing `Output:` marker is `UNKNOWN_COMPLETION`.
- **Content hashing bounds.** When the wrapper proves a complete read,
  content containing lone surrogates is rejected with `MALFORMED_UNICODE`
  before any UTF-8 hashing: the observation is typed, non-removable, and
  carries no bundle/member digest (explicitly absent, never a placeholder).
  Read-level reasons propagate the wrapper's typed reasons (falling back to
  `UNKNOWN_COMPLETION` only when the wrapper carries none).
- **Completion states.** Exit zero + present body + no `Truncated: true`
  marker = complete (the wrapper asserts process completion; an explicit
  truncation marker overrides). `Truncated: true` is `TRUNCATED_OUTPUT`.
  Nonzero exit is `NONZERO_EXIT` — never a complete file bundle. A missing
  body (empty result string) is `MISSING_OUTPUT_BODY`, distinct from a proven
  empty successful output (exit zero, `Output:` present, zero content bytes),
  which is a complete empty version carrying the exact empty digest
  `e3b0c442…`.
- **Source is source.** Text after `Output:` that merely looks like
  execution metadata (`Process exited with code 1`, `Truncated: true`, …)
  remains source and never redefines wrapper status.

## 6. Bundle attribution (D05)

A successful complete `cat A.md B.md` result is **one ordered, whole
attributable bundle** even without any internal A/B separator:

- `bundle_digest` = SHA-256 of the exact combined content bytes.
- Individual member boundaries are not fabricated: with more than one
  operand, `member_digests` entries are `None` (unknown) — the bundle digest
  is never labeled as any member's hash. Exactly one operand proves the
  member boundary (the whole body is that one file), so the member digest
  equals the content digest (a zero-byte body yields the exact empty digest).
- `proven_executed` preserves the observed operand order (repeats included);
  `distinct_member_count`/`slot_width` count distinct normalized members
  (repeated operands never inflate width).
- The tool wrapper, headers, call and arguments are untouched; only
  `content_span` is exposed as removable, and only when the read is complete
  (`removable=True`).

## 7. Fixed limitation vocabulary

All results carry `Limitation` enum values only — stable identifiers that
never echo payload text and are safe for operational logs. The full closed
list is `Limitation` in `observation_models.py`: root (`marker_misplaced`,
`malformed_delimiters`, `duplicate_marker`, `unclosed_tail`,
`unsupported_shape`, `over_bound`, `invalid_scope_label`,
`competing_root_scopes`, `malformed_unicode`, `malformed_environment`,
`unsupported_endpoint`), path (`outside_workspace`, `unknown_workspace`,
`unproven_cwd`, `traversal`, `unsupported_path_form`, `ambiguous_path`,
`path_too_long`, `non_literal_operand`, `empty_operand`), command
(`command_unsupported`, `command_empty`, `command_over_bound`,
`command_substitution`, `shell_escape`, `glob_unproven`, `redirection`,
`pipe`, `multiple_commands`, `heredoc`, `fragment_command`,
`comment_present`, `quoted_operand`, `tilde_unproven`), tool (`unsupported_tool`,
`namespace_tool_unproven`, `duplicate_call_id`, `missing_call_result`,
`mismatched_call_id`, `nonzero_exit`, `unknown_completion`,
`truncated_output`, `process_running`, `write_stdin_chunk`,
`multi_chunk_deferred`, `missing_output_body`, `malformed_wrapper`,
`output_over_bound`).

## 8. Boundedness

`ObservationBounds` (defaults: 1024 items, 1,000,000 item chars, 512 label
**UTF-8 bytes**, 100,000 environment chars, 128 commands, 4,096 command
chars, 32 operands, 256 path bytes, 128 outputs, 1,000,000 output chars, 8
wrapper header lines, 128 tools) bounds every scan; the derived argument-
decode bound is `2 * max_command_chars + 128`. Parsing is linear; adversarial
input (multi-megabyte items, huge item counts, unterminated envelopes,
over-long numeric fields, deep JSON nesting) terminates deterministically
with typed limitations (`OVER_BOUND`, `MALFORMED_WRAPPER`, typed argument
shapes) — no regex blowup, no timing-dependent behavior, no uncaught
exceptions at the public entry points.

## 9. Privacy and identity

- No model field derives an authenticated principal, session, or user
  identity from untrusted text; `PathContext` accepts only explicit validated
  client-workspace context supplied by the caller.
- Results carry spans, digests, counts and fixed reasons only. Raw source
  content, prompts, tool output bodies, and argument payloads are not
  retained in result representations (bounded path labels and scope labels
  are metadata).
- No filesystem or network access occurs anywhere in this package; observed
  commands are never executed.

## 10. Fixtures and provenance

The synthetic fixtures under `tests/fixtures/cache_bundles/v1/`
self-identify as synthetic with **per-shape-family** observed-format
authority and the parser versions above:

- **Root envelope shapes** (`root_*` fixtures): the sanitized Codex 0.149.0
  API-boundary capture record
  (`tests/fixtures/codex/0.149.0/README.md`). That capture is **root-only**
  — it contains no read call/result or exec-wrapper content, so it is not
  authority for the read wrapper shape. The canonical sanitized fixture
  (`tests/fixtures/codex/0.149.0/project_instructions_responses.json`) is
  reused directly as a D01 real-format input.
- **Read call/result and wrapper shapes** (`read_*` fixtures): the human
  handoff section 6.2 documented real format (`docs/CACHE-REWORK.md`), with
  synthetic supplemental values (chunk IDs, timings, content). Both the
  real-format `Chunk ID:` header and the explicitly earned compatible
  `Chunk Id:` variant are exercised
  (`read_handoff_wrapper_format_responses.json`).

Root capture and synthetic supplemental read shapes are distinct; no fixture
claims to be a fresh actual-client trace, and no private audit history, task
answer, credential, or customer/source content is included.

## 11. Deferred in this slice (later same-PR suffixes, 017-c/d and later)

Round 017-b is the bounded correction of the 017-a observation proof
(findings A-E: real-format wrapper, membership, per-call cwd, tool/endpoint
evidence, Unicode/bounds, parser bounds, and the normative mirror); it adds
no new read families. Still deferred: chained/mixed reads (`ls` + labels +
unrelated output, D06), literal loops and `cd` transitions with explicit
workdir chains (D07), per-read execution evidence distinct from global exit
status (D08), multi-chunk process completion proof and the remaining
truncation matrix (D09), and the full duplicate/mismatched/substitution/
unexecuted-branch matrix beyond the simple negatives already covered (D10).
Those compound/loop/chunk families move to later same-PR suffixes
(planned 017-c/d). Graph identity, admission, RAM state, recovery,
tokenization, and replacement belong to objectives 018-024.
