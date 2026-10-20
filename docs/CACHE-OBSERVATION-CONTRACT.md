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
same-PR suffixes (planned 017-d/e). Round 017-b corrected the 017-a
observation proof defects (findings A-E) without adding read families.
Round 017-c corrected the remaining literal-grammar and actual-endpoint
proof (bounded literal lexer with raw spans/cooked values, quoted
option/terminator/stdin semantics, non-ASCII separator law, exact operand
limit, per-call workdir Unicode validation, repr privacy, the documented
raw-argument cap, and mixed/envelope endpoint selection) without adding
read families. Round 017-d (this slice) first corrected the root-domain
prerequisite (root observation is scoped to the actual selected
Responses domain; a Responses string input plus Chat messages is a mixed
shape, never unambiguous Chat; the contradictory independence clause is
removed) and then earned the finite read-plan surface D06/D07/D08:
all-cat / literal-cd `&&` plans as one ordered whole bundle, absolute
literal `cd` transitions under the evidenced workspace with per-call
workdir precedence, bounded literal `echo` outer boundaries with exact
prefix/suffix proof, per-read versus global exit evidence, and the whole-
plan bound law — all in the new pure inert module
`compound_reads.py` with the versioned grammar
`literal-read-plan/v1`. Round 017-e is the bounded correction of
that slice: the echo outer-boundary law now types option-like
dash-leading quoted literals (`-n`, `-e`, `-E`, combinations and
repetitions, either quote kind) as `ECHO_TARGET_UNSUPPORTED` —
quoting does not disable `echo`'s option parser, and the actual
`echo '-n'` writes nothing — so such commands keep their typed
unsupported observation with no removable span and no bundle digest
instead of inventing a false boundary; and every observation
produced through the finite-plan parser now carries the actual plan
grammar identity `READ_PLAN_GRAMMAR` across all outcomes (the
grammar-identity fallback law, section 4a), while observations the
single grammar actually earned keep `READ_GRAMMAR`.

## 1. Modules and versions

| Constant | Value | Covers |
|---|---|---|
| `OBSERVER_VERSION` | `cache-bundle-observation/1` | this pure observation stage |
| `ENVELOPE_FORMAT` | `codex-project-instructions/v1` | root delimiter contract |
| `READ_GRAMMAR` | `literal-shell-read/v1` | command grammar |
| `TOOL_WRAPPER_FORMAT` | `codex-exec-wrapper/v1` | exec wrapper text form |
| `READ_PLAN_GRAMMAR` | `literal-read-plan/v1` | finite read-plan grammar (D06-D08) |

Modules: `observation_models.py` (typed results, spans, digests, bounds),
`client_paths.py` (literal client-workspace path normalization),
`root_envelopes.py` (D01/D02 envelope observation), `shell_tokens.py`
(bounded literal token lexing: raw spans, cooked values, quoting,
operators), `read_grammar.py` (D03/D04 literal command grammar plus the shared cat
operand law), `compound_reads.py` (D06/D07/D08 finite read-plan grammar
and outer attribution), `tool_results.py` (D05 pairing and wrapper),
`observe.py` (pure composition entry point `observe_request`).

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
authority. **Root-domain law:** only the actual selected **Responses**
domain can establish a root from its user `input_text` container. An
explicit Chat selection never borrows root authority from an ignored
Responses `input`; mixed, unknown and invalid-endpoint selections return
no valid-root occurrence eligible for later graph/cache admission, even
when a root-shaped object sits in an unused field — such an occurrence is
demoted to non-authoritative typed evidence (status `unsupported`, no
digest, `UNSUPPORTED_ENDPOINT` reason) and the root result is typed
`UNSUPPORTED` with `UNSUPPORTED_ENDPOINT` in its conflicts. A Chat-only
envelope has no recognized root container at all (`UNSUPPORTED_ENDPOINT`,
zero scanned items). A valid Responses string-form input carries no item
container: no root occurrence exists (`NO_ROOT`, zero scanned items). The
legacy detector keeps its own behavior on the legacy path.

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
- **No-spaces convention (all whitespace).** A path label carrying any
  whitespace character of any kind — including non-ASCII (e.g. NBSP) — is
  not a representable literal member under the agreed no-spaces file
  convention and is typed `AMBIGUOUS_PATH`: it never normalizes and is
  never silently split into two fabricated files.  Valid non-ASCII paths
  (e.g. `Aé.md`) are preserved exactly.
- **Malformed Unicode.** A workspace or workdir label containing lone
  surrogates is rejected **before** any UTF-8 byte check (typed, never a
  `UnicodeEncodeError`).  A per-call `workdir` that is malformed Unicode
  makes the whole call typed `MALFORMED_UNICODE` (relative and absolute
  operand variants alike): a fixed non-removable limitation with no
  placeholder digest and no raw exception echo.
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

- Tokenization is a bounded literal lexing (the pure `shell_tokens`
  module) that separates each token's raw span (character offsets into the
  exact command string), cooked value (the quoted inner text for a fully-
  quoted literal, otherwise the exact raw text), quote classification and
  shell-operator classification.  Only **ASCII whitespace** separates
  tokens: arbitrary Unicode `isspace` characters (e.g. NBSP) are **not**
  POSIX shell separators — they stay inside the token and are typed by the
  path layer (no-spaces convention), never split into two files.  No shell
  parsing (no new external shell parser dependency), no execution, no
  environment/glob/substitution expansion; operators and substitutions
  stay classified data.
- **Option parser (quoting does not disable it).** Recognition is by
  **cooked value**: the first token whose cooked value is exactly `--`
  (quoted or not) is processed once as the option terminator — `cat '--'
  A.md` proves only `A.md` and never invents a `--` file.  A later `--`
  token (quoted or not) is a **literal operand** and stays in the actual
  complete member list (e.g. `cat -- A.md '--' B.md` has members `A.md`,
  `--`, `B.md`): it is never silently dropped and its output is never
  attributed to fewer members than were actually requested.  A token whose
  cooked value starts with `-` before the terminator (`-n`, `--number`,
  quoted or not) is a cat option, never a file member
  (`COMMAND_UNSUPPORTED`); after the terminator, option-looking names are
  literal file labels.  The stdin special operand `-` (cooked value,
  quoted or not, before or after the terminator) is never a file member:
  the read is typed `STDIN_OPERAND` and never complete (cat would read
  stdin as well).  A literal path that merely ends in `-` (`./-`,
  `/work/-`) is a path operand, distinguished from the special operand.
- **Per-call workdir.** The supported argument object may carry a `workdir`
  string (a literal absolute client path); it is validated against the
  evidenced workspace at normalization time. A non-string, empty, or
  control-bearing `workdir` makes the argument shape typed unsupported.  A
  workdir containing lone surrogates is typed `MALFORMED_UNICODE` before
  any UTF-8 byte check and makes the whole call non-removable (relative
  and absolute operand variants alike) — a fixed typed limitation, no
  placeholder digest, no raw exception echo.
- **Malformed Unicode.** A command string containing lone surrogates is
  rejected with `MALFORMED_UNICODE` before any UTF-8 hashing; its
  `command_digest` is explicitly absent (never a placeholder) and no
  operand is normalized or proven.
- **Argument decoding bounds.** A raw JSON-string argument longer than the
  documented conservative cap `12 * max_argument_chars + 128` — the finite
  worst case of the supported JSON encoding (at most 6 characters per
  Unicode character per string field, two fields, plus bounded wrapper
  overhead) — is typed unsupported without being parsed; decode errors
  (including nesting-depth `RecursionError`) return the same typed result
  and are never re-raised with raw argument text.  No broad exception
  swallowing.  (The earlier `2 * max_command_chars + 128` was not a Unicode
  JSON-escaping bound and is superseded.)
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
  (`max_operands`) **exactly**: up to `max_operands` operands form a
  complete observation, and the first operand beyond the limit is typed
  `COMMAND_OVER_BOUND`.
- Supported argument shapes (documented envelope forms): a JSON string or
  object with a `cmd`/`command` string; an argv list that is exactly one
  string or exactly `[bash|sh|zsh, -c|-lc, <string>]`. Other shapes are
  typed unsupported.

### 4a. Finite read-plan grammar (D06/D07/D08)

The earned plan surface is a **finite typed plan** (versioned
`literal-read-plan/v1`), not a general shell interpreter:

```text
plan        := statement ('&&' statement)*
statement   := cat_stmt | cd_stmt | echo_stmt
cat_stmt    := 'cat' operand ...        (the exact earned cat option law)
cd_stmt     := 'cd' absolute_literal_dir
echo_stmt   := 'echo' 'quoted_literal'    (cooked value not dash-leading)
```

- **Separators.** Statements join only on the exact unquoted `&&`
  operator token. Operators are earned only outside quotes: a quoted
  `&&` is a literal token (typed `QUOTED_OPERAND`), never a separator.
  Adjacent-operator variants (`&&&`), semicolons, a single `&`, pipes,
  redirections, substitutions, comments, heredocs, branches and other
  metacharacters keep the plan typed unsupported. The control-character
  guard is not relaxed: POSIX blanks are not interchangeable with
  CR/VT/FF. Unknown branch/control flow stays typed, and later-command
  words are never reinterpreted as requested `cat` filenames (the first
  typed operator inside a `cat` statement terminates member collection).
- **`cat` statements.** The exact single-command option/terminator/stdin
  law (section 4), with one shared whole-plan operand budget.
- **`cd` statements (D07).** Exactly one absolute literal directory that
  validates inside the evidenced workspace (component comparison;
  `..`-carrying, relative, bare, multi-target and over-bound targets are
  `CD_TARGET_UNSUPPORTED`; outside the workspace is `OUTSIDE_WORKSPACE`;
  no evidenced workspace is `UNKNOWN_WORKSPACE`). `cd` transitions
  affect following reads only; the explicit supported per-call workdir
  takes precedence over the batch default before the first transition.
  Absolute literal directory transitions suffice in this slice; other
  forms are explicitly typed, never guessed. No host cwd/stat/resolve,
  no environment or glob expansion.
- **`echo` statements (outer regions, D06).** Exactly one clean
  fully-quoted literal whose cooked value is **not dash-leading**
  (`ECHO_TARGET_UNSUPPORTED` otherwise). Quoting does **not** disable
  `echo`'s own option parser: an option-like cooked operand (`-n`,
  `-e`, `-E`, combinations and repetitions, in either quote kind) is
  implementation-sensitive — the actual `echo '-n'` writes nothing —
  so it never earns a literal+newline boundary; the command keeps its
  typed unsupported observation with no removable span and no bundle
  digest. Command-local grammar semantics precede boundary matching:
  matching file bytes cannot establish that an echo printed them. The
  exclusion is narrow and conservative: non-dash-leading literals
  (including a dash inside the literal and the empty literal) stay
  earned. An earned echo before all reads is a deterministic output
  **prefix**, one after all reads a **suffix** (echo's newline
  terminator included), proven at its exact position in the wrapper
  output. Only the pure file-source span between proven boundaries is
  attributable; a label inside a file stays source. Printed delimiters
  are not a universal boundary oracle: a collision (content shorter
  than prefix plus suffix), a mismatched boundary, or an `echo`
  between reads (unknown internal boundary) is
  `OUTER_BOUNDARY_UNPROVEN` — typed where proof is insufficient.
- **Non-read statements.** Any other executable (`ls`, `head`, …) is
  typed (`COMMAND_UNSUPPORTED` / `FRAGMENT_COMMAND`) and, in a
  multi-statement plan, makes the combined output structurally
  unattributable (`OUTER_BOUNDARY_UNPROVEN`): listing rows and
  diagnostics are never swallowed into a file bundle, no saved snapshot
  is a runtime oracle, and whole-request acquisition never claims
  support merely because `cat` appears. A plan with no `cat` statement
  at all is typed, never a silent empty read.
- **Whole-plan bounds.** Total plan characters (`max_command_chars`),
  total `cat` operands across all statements (one shared
  `max_operands` budget), statement count (`max_operands`), output
  (wrapper `max_output_chars`) and nesting (the plan is flat; any
  nesting metacharacter is typed). A per-segment bound is never
  multiplied over segments.
- **Completion and attribution (D08).** A complete plan plus a
  wrapper-proven exit-zero, untruncated, present output proves each
  requested read succeeded: the attributable content region is **one
  ordered whole bundle** even without inner separators — repeated
  operands preserve observed order, distinct member width is recorded
  separately, and individual member hashes are never fabricated (a
  single distinct member proves its digest, including the exact empty
  digest for a zero-byte middle). Requested versus proven execution
  stay distinct, and the plan never invents per-command exit metadata:
  a global nonzero in an `&&` chain identifies no per-read failure and
  proves no earlier source complete (`NONZERO_EXIT` / `PARTIAL`, no
  proven members, no digest); a truncated chain is `TRUNCATED` /
  `PARTIAL`; a semicolon or mixed chain never proves an earlier `cat`.
  The original wrapper/global status is always preserved as recorded
  facts.
- **Grammar identity (017-e).** Every `ReadObservation` produced
  through the finite-plan parser carries the actual plan grammar
  identity `READ_PLAN_GRAMMAR` (`literal-read-plan/v1`) consistently
  across complete, unsupported, nonzero, missing/truncated/running,
  malformed-content and outer-boundary-unproven outcomes. The
  fallback selection is explicit: the single-command grammar
  (`READ_GRAMMAR`, `literal-shell-read/v1`) is primary; a command it
  does not complete is evaluated by the finite-plan parser and its
  observations carry the plan grammar, while an observation the single
  grammar actually earned keeps `READ_GRAMMAR`. The grammar label
  identifies the parser that evaluated the command; it never changes
  outcome, completeness, removability or digests, and an unsupported
  attempted read is never a successful plan. The wrapper format
  (`TOOL_WRAPPER_FORMAT`) is a separate identity from the read
  grammar.

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
- **Endpoint selection.** One API request is one endpoint, never a batch
  of two.  The selected domain is an explicit validated endpoint context
  (`observe_request(..., endpoint="responses"|"chat")`) or an inferred
  **unambiguous** supported envelope (exactly one of `input` / `messages`
  present as a list).  A mixed shape (both present, no explicit context)
  is typed `ENDPOINT_UNSUPPORTED` and non-removable: pairing bookkeeping
  (duplicate/missing/mismatched IDs, including cross-endpoint ID matches)
  is preserved, but no read is acquired from either container — never by
  precedence, never as two real calls.  The report's `endpoint` is
  `responses`, `chat`, `mixed` or `unknown`.  An explicit endpoint scopes
  observation to its own root/call/result container (the other container
  is never acquired); an explicit endpoint whose container is absent, or
  an invalid value, is typed `ENDPOINT_UNSUPPORTED` with `endpoint`
  `unknown`.  The global endpoint and per-read endpoints always agree
  about the selected domain (under a mixed selection the per-read value is
  the container provenance of a typed, non-acquiring record).  Root
  envelope observation is scoped by this same actual endpoint selection
  (section 2 root-domain law): only the selected Responses domain scans
  roots; the other container is never acquired and can never mint a
  valid root.
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
`comment_present`, `quoted_operand`, `tilde_unproven`, `stdin_operand`),
tool (`unsupported_tool`,
`namespace_tool_unproven`, `duplicate_call_id`, `missing_call_result`,
`mismatched_call_id`, `nonzero_exit`, `unknown_completion`,
`truncated_output`, `process_running`, `write_stdin_chunk`,
`multi_chunk_deferred`, `missing_output_body`, `malformed_wrapper`,
`output_over_bound`), plan (`cd_target_unsupported`,
`echo_target_unsupported`, `outer_boundary_unproven`).

## 8. Boundedness

`ObservationBounds` (defaults: 1024 items, 1,000,000 item chars, 512 label
**UTF-8 bytes**, 100,000 environment chars, 128 commands, 4,096 command
chars, 32 operands, 256 path bytes, 128 outputs, 1,000,000 output chars, 8
wrapper header lines, 128 tools) bounds every scan; the derived argument-
decode bound is `12 * max_argument_chars + 128` (the documented
conservative JSON-encoding worst case).  Parsing is linear; adversarial
input (multi-megabyte items, huge item counts, unterminated envelopes,
over-long numeric fields, deep JSON nesting) terminates deterministically
with typed limitations (`OVER_BOUND`, `MALFORMED_WRAPPER`, typed argument
shapes) — no regex blowup, no timing-dependent behavior, no uncaught
exceptions at the public entry points.  Plan parsing is linear over the
whole command string (one lexing pass plus one statement pass); the
whole-plan bounds above cap statements, operands and characters before
any attribution work.

## 9. Privacy and identity

- No model field derives an authenticated principal, session, or user
  identity from untrusted text; `PathContext` accepts only explicit validated
  client-workspace context supplied by the caller.
- Results carry spans, digests, counts and fixed reasons only. Raw source
  content, prompts, tool output bodies, and argument payloads are not
  retained in result representations (bounded path labels and scope labels
  are metadata).
- Operational representations never echo raw text: the
  `UnwrappedCommand` repr carries command/workdir lengths and presence
  only, and token representations carry spans and flags only; no
  exception path re-raises with raw command, workdir, body or source
  text.
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

## 11. Deferred in this slice (later same-PR suffixes, 017-d/e and later)

Round 017-b is the bounded correction of the 017-a observation proof
(findings A-E: real-format wrapper, membership, per-call cwd, tool/endpoint
evidence, Unicode/bounds, parser bounds, and the normative mirror); it adds
no new read families.  Round 017-c is the bounded correction of the
remaining literal-grammar and actual-endpoint proof (bounded literal lexer
with raw spans/cooked values; quoted option/terminator/stdin semantics;
non-ASCII separator law; exact operand limit; per-call workdir Unicode
validation; repr privacy; the documented raw-argument cap; mixed/envelope
endpoint selection); it adds no new read families.  Round 017-d first
corrects the root-domain prerequisite (root observation scoped to the
actual selected Responses domain; string-input plus messages is a mixed
shape; the contradictory root-scanning independence clause removed) and
then earns D06/D07/D08 on the same inert surface: all-cat / literal-cd
`&&` plans as one ordered whole bundle (new module `compound_reads.py`,
grammar `literal-read-plan/v1`), absolute literal `cd` transitions with
per-call workdir precedence, bounded literal `echo` outer boundaries with
exact prefix/suffix proof, per-read versus global exit evidence, and the
whole-plan bound law — still inert, with no graph/cache/compiler/app
integration.  Still deferred: multi-chunk process completion proof and the
remaining truncation matrix (D09), and the full
duplicate/mismatched/substitution/unexecuted-branch matrix beyond the
negatives already covered (D10), on later same-PR suffixes — the
earlier planned 017-e loops/chunks draft is superseded by the 017-e
bounded correction (echo option semantics plus plan-grammar identity),
and strategy now plans 017-f literal loops and 017-g process/chunk
association, subject to review.  Literal loops remain explicitly
unsupported in this slice (typing, not execution). Graph identity,
admission, RAM state, recovery, tokenization, and replacement belong to
objectives 018-024.
