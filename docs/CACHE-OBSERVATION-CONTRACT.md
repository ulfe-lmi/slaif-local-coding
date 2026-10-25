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
[the stage ledger](CACHE-REWORK-LEDGER.md). D06-D08 (chained reads,
literal loops, per-read vs global exit evidence) are earned in rounds
017-d and 017-f of this same PR (section 4a and section 4b); D09-D10
(multi-chunk process completion, the remaining truncation matrix and
the duplicate/substitution/branch matrix) are NOT implemented here;
they are planned for later same-PR suffixes (planned 017-g). Round
017-b corrected the 017-a
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
single grammar actually earned keep `READ_GRAMMAR`. Round 017-f earns
the bounded pure literal-loop slice (the D07 loop criterion) in the
new pure inert module `literal_loops.py` with the versioned grammar
`literal-loop/v1`: the human 6.2 loop forms are recognized as finite
parsed data with deterministic requested members, the all-success
guarded pure-cat variants earn one ordered whole-source bundle under
a proven exit-zero, untruncated, present wrapper (one concatenated
region with an exact digest, no fabricated internal boundaries or
member hashes), and unguarded or echo-labeled forms stay non-removable
with typed iteration/outer-attribution limitations; the loop variable,
list, template, guard, echo, adjacent-quote, workdir and whole-loop
bound laws are explicit (section 4b), with the whole-loop expanded-
operand budget never multiplied per iteration, and every observation
the loop parser evaluates carries the actual loop grammar identity
`LOOP_GRAMMAR`. Round 017-m repairs the per-request pairing and
causality identity on this same inert surface: the schema-evidenced
call-ID inventory is eligibility-independent (a collision with an
eligible call ID cannot disappear through filtering of unknown or
ineligible calls; an unknown call never acquires; missing, empty or
malformed call IDs stay observable and are never invented), and a
result attaches to its matching call only when its exact numeric
structural position (the `input` item index; the Chat `messages` index
of the assistant message carrying the call) follows the call's — a
pre-call result is a typed non-removable `PRE_CALL_RESULT` chain with
no bundle/member digest, no source span and no proven-executed claim.
The public D10 composition matrix (ordinary valid reads amid
unrelated calls, same-ID conflicts across supported/unsupported
families, identical/conflicting duplicate calls, missing/empty/
malformed IDs, orphan/mismatched/pre-call outputs, duplicate same-
call results, non-monotonic IDs and >=10 structural positions) and
the pure D09 unsupported/partial negative matrix (command
substitution, unexecuted branches, partial readers, known
truncated/missing/running/unknown wrappers contrasted with the exact
proven empty successful output) are earned as public observation
tests (`tests/test_bundle_d10_matrix.py`).  Round 017-n repairs the
observer identity-inventory boundaries on the same inert surface:
the Responses `custom_tool_call` identity joins the call inventory
alongside `function_call` (identity bookkeeping only — no custom-tool
read parsing/execution/acquisition, opaque input never reinterpreted,
no generic unknown-family wildcard), `max_commands`/`max_outputs`
bound the **complete** relevant inventory (unsupported names, opaque
custom records, missing/empty/malformed IDs, invalid result IDs)
before any identity map or diagnostic is retained (fixed
non-acquiring `OVER_BOUND`, selected-domain scoping under explicit
endpoint selection), and absent/null/empty or non-string result IDs
are fixed typed non-echoing unpaired limitations
(`MISSING_RESULT_ID` / `MALFORMED_RESULT_ID`), never invented,
hashed, attached or acquired.  D09 multi-chunk/
process association remains deferred and is never marked delivered
by these negatives.

## 1. Modules and versions

| Constant | Value | Covers |
|---|---|---|
| `OBSERVER_VERSION` | `cache-bundle-observation/1` | this pure observation stage |
| `ENVELOPE_FORMAT` | `codex-project-instructions/v1` | root delimiter contract |
| `READ_GRAMMAR` | `literal-shell-read/v1` | command grammar |
| `TOOL_WRAPPER_FORMAT` | `codex-exec-wrapper/v1` | exec wrapper text form |
| `READ_PLAN_GRAMMAR` | `literal-read-plan/v1` | finite read-plan grammar (D06-D08) |
| `LOOP_GRAMMAR` | `literal-loop/v1` | finite literal-loop grammar (D07) |

Modules: `observation_models.py` (typed results, spans, digests, bounds),
`client_paths.py` (literal client-workspace path normalization),
`root_envelopes.py` (D01/D02 envelope observation), `shell_tokens.py`
(bounded literal token lexing: raw spans, cooked values, quoting,
operators), `read_grammar.py` (D03/D04 literal command grammar plus the shared cat
operand law), `compound_reads.py` (D06/D07/D08 finite read-plan grammar
and outer attribution), `literal_loops.py` (D07 finite
literal-loop grammar and attribution), `tool_results.py` (D05 pairing
and wrapper),
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
  separately, and individual member hashes are never fabricated: a
  file's digest is proven only when exactly one member occurrence
  covers the entire attributable region (a whole pure region read
  once — including the exact empty digest for a zero-byte read);
  distinct slot width alone cannot prove a per-file digest, so a
  repeated member (`A,A`) has width one but unknown individual
  versions/boundaries and no per-file digest. Requested versus proven
  execution stay distinct, and the plan never invents per-command exit
  metadata:
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

### 4b. Finite literal-loop grammar (D07)

The earned loop surface is a **finite typed loop** (versioned
`literal-loop/v1`), not a general shell interpreter:

```text
loop        := 'for' var 'in' list '; do' body '; done'
var         := one of the earned ordinary names (`f`, `d`)
list        := clean-literal+                (bounded)
body        := statement (';' statement)*
statement   := cat_stmt | echo_stmt
cat_stmt    := 'cat' operand+ ('|| exit 1')?
echo_stmt   := 'echo' quoted_literal | quoted_echo_template
```

- **Domain and identity fallback.** The loop parser's domain is a
  command whose first token is the exact unquoted `for` keyword. A
  command outside the domain is evaluated by the finite-plan parser
  (section 4a), whose reasons and identity apply unchanged; an
  observation the loop parser evaluates carries `LOOP_GRAMMAR`.
- **Variable law (D07).** The loop variable must be exactly one of the
  earned ordinary names of the human handoff 6.2 forms (`f`, `d`).
  Shell-special, dynamic, readonly or any other name (`RANDOM`,
  `SECONDS`, `LINENO`, `_`, `g`, ...) is never a literal local binding
  (`LOOP_VARIABLE_UNSUPPORTED`), and no runtime or environment oracle
  is consulted. A `$name` reference inside a body template that is not
  the loop variable — including a longer name that merely starts with
  it (`$f_extra`) or an unknown name — is typed the same way. Other
  ordinary names may be earned only if explicitly bounded by a later
  round.
- **List law.** List values are clean literals only: an unquoted
  literal, or a fully-quoted literal whose inner text carries no
  metacharacter, quote or whitespace of any kind (the agreed
  no-spaces file convention). A substitution (`$FILES`), a glob
  (`*.md`), an empty list (`in;`), an implicit positional list
  (`for f;`), or a word that mixes quoting is typed
  (`COMMAND_SUBSTITUTION`, `GLOB_UNPROVEN`, `COMMAND_EMPTY`,
  `LOOP_FORM_UNSUPPORTED`, `QUOTED_OPERAND` respectively), never
  guessed. Option-like list values (`-n`, `-`, `--`) never fabricate
  whole-file membership: their substituted expansion is still held to
  the exact cat option/stdin/terminator law per iteration.
- **Template law.** A `cat` operand template is a double-quoted path
  whose segments are clean literal labels with exactly one segment
  equal to `$<loopvar>` (the pure-variable form `"$f"` is the
  one-segment case); a leading `/` is allowed (an absolute client
  template decided by the shared path law). Partial-segment references
  (`pre"$f"`, `"$f.md"`), repeated references, `${...}` defaults,
  substitutions, single-quoted `'$f'`, adjacent-quote mixed words
  (`"$f"".md"`, `pre"$f"`) and any other non-literal segment text are
  typed (`LOOP_TEMPLATE_UNSUPPORTED` / `LOOP_VARIABLE_UNSUPPORTED` /
  `QUOTED_OPERAND`), never guessed. The echoed form may carry at most
  one whole loop-variable reference inside double-quoted text with no
  other metacharacter (whitespace allowed — echo text, not a path).
- **Guard law.** The earned per-iteration guard is exactly `|| exit 1`
  after each `cat` statement (the guard operator is the exact unquoted
  `||` token). A missing guard, an `exit 0` guard, another exit
  literal, a guard after the loop, or a `break`/`continue`/`true`
  variant is not equivalent (`LOOP_GUARD_UNSUPPORTED` /
  `LOOP_FORM_UNSUPPORTED`). A single `|` is a pipe operator, never a
  guard.
- **Adjacent-quote law (word boundaries corrected in 017-g).** A
  shell word that mixes quoting (`A".md"`, `A'.md'`, `"$f"".md"`,
  `pre"$f"`, `"A".md`) is typed (`QUOTED_OPERAND` /
  `ECHO_TARGET_UNSUPPORTED` at its use site), consistent with the
  shared quote law: no member or template is fabricated from the
  fragments. The unquoted `;` is its own syntactic element, emitted
  as a standalone token: a standalone `;` stays syntax (a `;`
  separator after a quoted value stays a separator — `for f in
  "A.md";` still earns), while a semiterminated literal suffix of a
  mixed word can never become an extra member — a quoted prefix plus
  a literal suffix touching the separator (`for f in "A".md;`) is one
  unearned word, typed `QUOTED_OPERAND`, never two members (`A` and
  `.md`); the attached and spaced separator forms observe identically.

- **Echo law (outer attribution).** Loop body echo output is ordinary
  actual output, never source bytes: a loop whose body carries an
  `echo` statement interleaves printed text between the read output,
  so the source region is not attributable as a pure bundle
  (`OUTER_BOUNDARY_UNPROVEN`) — a labeled-loop positive is earned
  later, if at all, with exact multiple-span/collision/order proof,
  never assumed here, and matching file bytes are not an echo-output
  oracle. An unearned echo target (unquoted, mixed, dash-leading
  cooked literal, broken quote, extra words) is
  `ECHO_TARGET_UNSUPPORTED`.
- **Control flow and fragments.** The loop is flat: a nested
  `for`/`while`/`until`/`if`/`case`/`select`, `break`/`continue`, or
  any other control-flow keyword is typed (`LOOP_FORM_UNSUPPORTED`);
  a non-`cat`/`echo` body executable is typed (`FRAGMENT_COMMAND` for
  the earned fragment family, `COMMAND_UNSUPPORTED` otherwise);
  comments, heredocs, redirections, writes, pipes, branches and
  substitutions keep their shared typed reasons. A loop with no `cat` statement at all is
  typed, never a silent empty read.
- **Completion and attribution (D07).** An unguarded `cat` does not
  prove that every earlier iteration succeeded from the final exit
  status: an earned loop with an unguarded `cat` is a recognized read
  whose per-iteration execution is not proven (`LOOP_ITERATION_UNPROVEN`),
  and requested paths are not proven-executed paths. Only an
  all-success guarded pure-cat loop (every `cat` guarded, no body
  echo, no member-level limitation) plus a wrapper-proven exit-zero,
  untruncated, present output is a complete ordered whole-source
  bundle: one concatenated region with an exact digest over the
  attributable content span, no fabricated internal boundaries or
  member hashes: a file's digest is proven only when exactly one
  member occurrence covers the entire attributable region (a whole
  pure region read once — including the exact empty digest for a
  zero-byte region); distinct slot width alone cannot prove a
  per-file digest, so a duplicate (`A,A`) has width one but unknown
  individual versions/boundaries and no per-file digest. Duplicate
  operand order is preserved; distinct represented members determine
  the slot width. Unknown, nonzero, partial, truncated or missing
  output never yields a whole complete bundle, and no earlier
  iteration is inferred to have succeeded; malformed-Unicode content
  is rejected before any hashing. Requested, proven and complete stay
  separate facts for every outcome.
- **Whole-loop bounds.** Total command characters
  (`max_command_chars`), iteration count (`max_operands`), body
  statement count (`max_operands`) and — the key bound — the total
  expanded `cat` operands across **all** iterations (one shared
  `max_operands` budget, never re-applied per iteration) are
  explicit (`OVER_BOUND`); the loop is flat and parsing is linear
  over the command string. Path law: the evidenced workspace plus
  the explicit per-call workdir resolves every expanded operand
  lexically in the client domain (the shared `normalize_read_path`
  law); a path-limited expansion stays a member with its typed
  limitation, and sibling/workspace-escape/ambiguous-cwd/
  control-character/Unicode rejections are preserved.
- **Grammar identity (017-f).** Every `ReadObservation` produced
  through the loop parser carries the actual shared loop grammar
  identity `LOOP_GRAMMAR` (`literal-loop/v1`) consistently across
  complete, unsupported, nonzero, missing/truncated/running,
  malformed-content and iteration/outer-boundary-unproven outcomes.
  The grammar label identifies the parser that evaluated the command;
  it never changes outcome, completeness, removability or digests,
  and an unsupported loop attempt is never a successful read. The
  simple (`READ_GRAMMAR`) and finite-plan (`READ_PLAN_GRAMMAR`)
  identities remain exact for their prior families, and the wrapper
  format (`TOOL_WRAPPER_FORMAT`) is a separate identity from the read
  grammar. No raw command, list value or echoed literal appears in a
  loop parse representation (spans, counts, digests and typed reasons
  only).

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
  (every occurrence recorded, never first-match). Missing results are
  `MISSING_CALL_RESULT`. Results without a supported call are
  `MISMATCHED_CALL_ID`. Multiple results for one call are
  `MULTI_CHUNK_DEFERRED` (multi-chunk completion proof is D09, later
  same-PR suffix).
- **Identity conflicts precede eligibility.** The relevant schema-
  evidenced call identities are inventoried **before** read eligibility
  is applied: every call record in a schema call position (Responses
  `input` `function_call` **and** `custom_tool_call` items; Chat
  assistant `tool_calls` `function` entry) participates in duplicate
  bookkeeping regardless of whether its tool name earns read support —
  so an unknown/ineligible call's ID colliding with an eligible call
  ID is a typed `DUPLICATE_CALL_ID` conflict, never filtered away, and
  never first-match.  The Responses `custom_tool_call` wire family is
  identity bookkeeping only: it earns **no** custom-tool read parsing,
  execution or acquisition (whatever its name — a custom call named
  like a supported tool still never acquires), its opaque `input` is
  never captured as arguments and never reinterpreted as a shell or
  source oracle, and no generic unknown-family wildcard recognition is
  invented (the exact family/name/ID association is preserved, and the
  supported namespace-declaration law is unchanged for acquirable
  families).  An unknown or ineligible tool call never acquires a
  source, and an unrelated unknown or opaque custom call with a unique
  ID is neither recorded nor allowed to poison a separate valid chain.
  Arbitrary nested text objects carrying `id`/`name` are not call
  records.  A call ID that is absent, JSON null, or an empty string is
  typed `MISSING_CALL_ID`; a present non-string ID is typed
  `MALFORMED_CALL_ID`.  Both stay observable, never pair, never
  acquire content, and no ID is ever invented.  The exact ID/name/
  arguments association, the namespace-declaration evidence, and the
  typed duplicate/missing/mismatch/unsupported states are preserved;
  diagnostics and reprs stay bounded and non-echoing, and private
  values never become metric labels.
- **Complete-inventory bounds.** `max_commands` is enforced against
  **all** relevant schema-position call records — including
  unsupported names, opaque `custom_tool_call` records, and
  missing/empty/malformed IDs — and `max_outputs` against **all**
  relevant result records, including invalid-ID results, **while
  streaming the inventory**: the bound is decided by a no-retention
  preflight **before** any record tuple, location string, identity
  map or typed diagnostic is retained or built, and the bounded
  collection pass runs only once the complete inventory is proven
  within its limits (retaining at most the declared counts): the
  over-bound input yields the fixed non-acquiring `OVER_BOUND` record
  (single, bounded, no private content), never a silently truncated
  inventory from which an earlier chain acquires while a later
  collision is missed, and never argument/wrapper parsing or
  identity maps for an already over-bound request.  The inspected
  containers are additionally bounded by the existing `max_items`
  item bound — a **per-container** law (round 017-p): each inspected
  outer `input`/`messages` list AND each inspected assistant
  `tool_calls` list is individually length-tested against
  `max_items` **before** it is iterated, parsed or retained,
  counting every raw entry regardless of schema, type or ID (the
  nested length test is O(1) per list; the list contents are never
  touched by the bound decision).  `max_items` is never a total
  across lists: an at-limit nested list still passes and observes
  normally (the useful unknown+valid within-limit control holds;
  there is no blanket reject-all).  Non-assistant `tool_calls`
  fields are uninspected.  For **explicit** endpoint selection only
  the selected domain is inspected and contributes to
  the counts (the other container is neither scanned nor counted);
  mixed input (and the legacy no-selection shape) is bounded across
  the inspected domains and remains non-acquiring under the existing
  law.
- **Private-ID representation.** Exact internal call/result IDs and
  association fields stay usable for pairing and bookkeeping, while
  the operational `str`/`repr` of report, read and unpaired objects
  never echo private ID values: a non-empty `call_id` renders as the
  fixed `<private-id>` placeholder, the observable no-ID state (empty
  string) stays exact, and no ID is invented, hashed or re-serialized
  into a representation.  Fixed enums, counts, locations, spans and
  digests remain observable in operational representations; no
  private value becomes a metric label.
- **Result-ID observability.** In the relevant Responses
  `function_call_output` and Chat `role=tool` schema positions, a
  result ID that is absent, JSON null, or an empty string is typed
  `MISSING_RESULT_ID`; a present non-string result ID (list, dict,
  number, boolean) is typed `MALFORMED_RESULT_ID`.  These are fixed,
  non-echoing, unpaired limitations: no ID is invented, no unhashable
  value is hashed, the malformed output is never attached to any call
  (no pair, no digest, no span, no acquisition), and the offending
  value is never stored or echoed.  Separate well-formed chains remain
  useful within the total inventory limits; the existing
  duplicate/missing/mismatched-result and structural pre-call typing
  and the namespace/domain separation are preserved.  Opaque result
  families (e.g. `custom_tool_call_output`) do not participate in the
  pairing bookkeeping in this slice — no new native format claim.
- **Structural causality.** A result attaches to its matching call only
  when its exact **numeric structural position** follows the call's —
  the Responses `input` item index, or the Chat `messages` index of the
  assistant message carrying the call.  Causality is never established
  from lexical call IDs, JSONPath string sorting, or JSONPath
  evaluation (presentation order of the report is separate from, and
  never used for, causality).  A result structurally before its
  matching call cannot be attached to a future call: its chain stays
  typed `PRE_CALL_RESULT` and non-removable, with no bundle/member
  digest, no source span and no proven-executed claim, while the
  wrapper facts and the exact ID/name/arguments association remain
  recorded.  Missing initial calls remain unsupported.  This is pure
  per-request evidence — no hidden cross-request history, process or
  session state, and no new freshness or root-transition policy.
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
`namespace_tool_unproven`, `duplicate_call_id`, `missing_call_id`,
`malformed_call_id`, `missing_result_id`, `malformed_result_id`,
`missing_call_result`, `mismatched_call_id`,
`pre_call_result`, `nonzero_exit`, `unknown_completion`,
`truncated_output`, `process_running`, `write_stdin_chunk`,
`multi_chunk_deferred`, `missing_output_body`, `malformed_wrapper`,
`output_over_bound`), plan (`cd_target_unsupported`,
`echo_target_unsupported`, `outer_boundary_unproven`), loop
(`loop_form_unsupported`, `loop_variable_unsupported`,
`loop_template_unsupported`, `loop_guard_unsupported`,
`loop_iteration_unproven`).

## 8. Boundedness

`ObservationBounds` (defaults: 1024 items, 1,000,000 item chars, 512 label
**UTF-8 bytes**, 100,000 environment chars, 128 commands, 4,096 command
chars, 32 operands, 256 path bytes, 128 outputs, 1,000,000 output chars, 8
wrapper header lines, 128 tools) bounds every scan; the complete
call/result inventory is bounded by `max_items` per inspected
container — outer `input`/`messages` lists and, since round 017-p,
each nested assistant `tool_calls` list individually, by an O(1)
length test before any iteration, parsing or retention — before any
record is retained, and `max_commands` /
`max_outputs` are enforced on the **complete** relevant inventory
(all schema-position call records and all result records, including
invalid IDs) before any identity map or diagnostic is built (section
5, complete-inventory bounds).  The derived argument-decode bound is
`12 * max_argument_chars + 128` (the documented
conservative JSON-encoding worst case).  Parsing is linear; adversarial
input (multi-megabyte items, huge item counts, unterminated envelopes,
over-long numeric fields, deep JSON nesting) terminates deterministically
with typed limitations (`OVER_BOUND`, `MALFORMED_WRAPPER`, typed argument
shapes) — no regex blowup, no timing-dependent behavior, no uncaught
exceptions at the public entry points.  Plan parsing is linear over the
whole command string (one lexing pass plus one statement pass); the
whole-plan bounds above cap statements, operands and characters before
any attribution work. Loop parsing is likewise linear over the command
string (one quote-aware scan plus one statement pass); the whole-loop
bounds above cap characters, iterations, statements and — before any
expansion — the total expanded operands across all iterations under one
shared `max_operands` budget (never multiplied per iteration).

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
bounded correction (echo option semantics plus plan-grammar identity).
Round 017-f earned the bounded pure literal-loop slice on this same
inert surface (section 4b, module `literal_loops.py`, grammar
`literal-loop/v1`): the human 6.2 loop forms are recognized as finite
parsed data with deterministic requested members, the all-success
guarded pure-cat variants earn complete ordered whole-source bundles
under wrapper-proven exit-zero/untruncated/present completion, and
unguarded or echo-labeled forms stay typed and non-removable. Still
deferred there: the labeled-loop positive (exact multiple-span/
collision/order proof), other ordinary loop variable names, and
wildcard iteration evidence — explicitly typed, never executed.
Strategy now plans 017-g process/chunk association, subject to
review.  Graph identity, admission, RAM state, recovery,
tokenization, and replacement belong to objectives 018-024.
Round 017-g published the bounded loop word/separator correction on
this same inert surface (the unquoted `;` as a standalone token;
the occurrence law for member digests). Round 017-h attempted the
process/chunk association evidence path but was **interrupted and
published as PARTIAL, non-delivery**: the original worker persisted
full provider requests and raw child stdout/stderr, exceeded the
prescribed ingress and attempt bounds, and triggered a client-startup
plugin sync side effect; it produced **no repository utility, test,
fixture or documentation change** and earned no format or process
acquisition. D09/D10 remain `NOT RUN`. Round 017-i (this round)
superseded the collector draft with a corrective **offline
process-capture utility** for independent strategic review (section
12): bounded, opt-in, fail-closed, stdlib-only, not wired into the
adapter runtime; it acquires no format evidence. (Historical
note: the 017-i record's "actual-client path unreachable by
construction" wording is a REJECTED claim, superseded by 017-j:
the path is input-gated, not structurally unreachable; see section
12.3.) The actual capture and the process/chunk collector remain
`NOT RUN`, planned for later exact orders after independent
review.
Round 017-j amended that same inert utility (still not wired into
the adapter runtime) from independent review: frozen review scripts
at the 017-i head exposed 11 check failures across the selection,
resource, and process surfaces (the file-boundary control had
already passed 3/3 and stays passing). 017-j repaired those bounded
defects: selection is bound to the controller's issued call records
(exact issued ID, tool family/name, declared step/command and
expected argument values, controller-issued process ID) with
advancement requiring completed outputs that carry issued metadata;
unissued/orphaned/conflicting/mismatched items are rejected with
typed reasons and their raw values are stored nowhere; proven
selected synthetic result text is retained losslessly after strict
ownership, shape, and byte verification against the owned seeded
workspace (selection schema v2, still `fixture_authority: none`);
the selected cap is enforced on the exact serialized UTF-8 record
bytes (serialize once, publish the same bytes); every fixture
request counts against the per-run budget before route/auth/body
outcome branches; preflight binary output is bounded while
receiving; pre-existing directories are never chmoded (group- or
world-writable pre-existing directories are rejected in place);
readiness/authorization metadata schemas are closed; and the
absolute run deadline spans owned descendants (the group is
terminated and reaped before pipe-drain waits; unrelated processes
survive). The 017-i record's "unreachable by construction" wording
is superseded: the actual-client path is input-gated (caller-
supplied `ready`/authorization records can launch the bound
stand-in), and this version's generated readiness verdict is
`not_ready`; the gate is stated accurately in section 12.3. This
round still performs no actual client, provider session, or model
call; the actual capture and the process/chunk collector remain
`NOT RUN`. Round 017-k amended that same inert utility (still not
wired into the adapter runtime) from a second independent review:
two additional frozen scripts at the 017-j implementation head
exposed 5 failures among 10 checks with valid controls
(`check-capture-issued-registry.py` 1/2;
`check-capture-finalization-v3.py` 4/8; the twelve original frozen
scripts and their hashes remain unchanged and passing). 017-k
repaired those four bounded defect areas: (1) RUNTIME frame
selection is bound to the controller's ACTUAL issued records
created before each provider request (a preloaded/anticipated/
forged call is never selected before the controller issues it; the
pure-facade candidate parsing is a distinct fixture mode, and a
constructor or manually populated state is not runtime provenance
evidence); (2) finalization quiesces the owned provider BEFORE
final validation/publication (freeze, stop accepting, close the
listening socket, bounded handler join) and validates/serializes
the explicit frozen frame snapshot, so no late or in-flight append
can reach a persisted record; (3) EVERY request method and
error-dispatch path consumes the per-run budget with fixed
sanitized errors (the 017-j do_GET/do_POST-only centralization
missed the BaseHTTPRequestHandler error-dispatch fallback), and
accepted handler concurrency is bounded with honestly reported
teardown; (4) readiness metadata round-trips the validated
live-facts flag count faithfully for zero and every nonzero known
flag (the 017-j `tuple("") * count` placeholder was always empty),
and malformed Unicode (e.g. a lone surrogate) is rejected with the
fixed typed `malformed_unicode` reason before any
encoding/hashing/retention, with the raw value stored nowhere and
no lossy replacement. This round still performs no actual client,
provider session, or model call; the actual capture and the
process/chunk collector remain `NOT RUN`.
Round 017-l repaired the two remaining offline capture
boundaries on that same inert utility (still not wired into the
adapter runtime) from a third independent review: a new
source-driven probe at the 017-k implementation head exposed 2
failures among 5 checks with 3 valid positive controls
(`check-capture-owned-io-and-seed-v2.py`; the fourteen prior frozen
scripts and their hashes remain unchanged and passing). 017-l
repaired those two bounded defects: (1) quiesce now closes every
ADMISSION-OWNED request socket (a bounded registry capped at the
concurrent-handler cap) as soon as no new admission can join it, so
an in-flight bounded body read that a per-read timeout cannot stop
(a progressing drip) is unblocked by an effective socket shutdown,
the peer observes closure, and the remaining handler work is joined
under the bounded grace; thread-start failure is counted and its
socket closed; repeated stop is safe; and an incomplete teardown (a
handler that outlives the bounded grace) is reported honestly and
can never yield a completed outcome (fixed `cleanup_failed`, no raw
error details); (2) selected result text is verified against the
IMMUTABLE ORIGINAL seed bytes (the default synthetic workspace files
plus every explicitly supplied extra synthetic workspace file)
recorded BEFORE the child launches -- never against a
child-writable file reread at finalization: a child that rewrites
its own seed after receiving a legitimately issued read can no
longer redefine the purported original, the received text is
compared against that pre-launch original, and tampered or
unverified text is stripped with the fixed `content_unverified`
reason (or a typed non-echoing failure plus safe cleanup), reaching
no persisted record, console, repr, or diagnostic. This round still
performs no actual client, provider session, or model call; the
actual capture and the process/chunk collector remain `NOT RUN`.
Round 017-m repaired the per-request pure read-observation identity
and causality pairing on the same inert surface (no capture
utility/child modification, no actual capture, no process
collector): (1) identity conflicts now precede read eligibility —
the schema-evidenced call-ID inventory is eligibility-independent, so
an unknown/ineligible call colliding with an eligible call ID is a
typed `DUPLICATE_CALL_ID` conflict instead of disappearing through
filtering, unknown calls never acquire, unrelated unique unknown
calls are neither recorded nor allowed to poison separate valid
chains, and absent/null/empty (`MISSING_CALL_ID`) or non-string
(`MALFORMED_CALL_ID`) call IDs stay observable without inventing an
ID; (2) results now attach only when their exact numeric structural
position follows the matching call's (the `input` item index; the
Chat `messages` index of the assistant message carrying the call) —
never from lexical call IDs or JSONPath string sorting — and a pre-
call result keeps its chain typed `PRE_CALL_RESULT`, non-removable,
with no bundle/member digest, no source span and no proven-executed
claim. The public D10 composition matrix (Responses and Chat:
ordinary valid reads amid unrelated calls, same-ID conflicts across
supported/unsupported names and families, identical/conflicting
duplicate calls, missing/empty/malformed IDs, orphan/mismatched/
pre-call outputs, duplicate same-call results remaining unsupported
absent later earned process-chain evidence, non-monotonic IDs and
>=10 structural positions, with independent valid chains still
earning exact source span/digest/members/width alongside the
rejected ambiguous chain) and the pure D09 unsupported/partial
negative matrix (command substitution `$()` and backticks,
false/conditional/unexecuted branches, partial `head`/`sed` readers,
known truncated/missing/running/unknown wrappers — all typed
unsupported/partial, never complete whole-file acquisitions —
contrasted with the exact proven empty successful output) are earned
by the new public suite `tests/test_bundle_d10_matrix.py`, with
unchanged inputs, non-echoing reprs, preserved bounds and exact
Unicode/CRLF source slices.  All previously earned literal read/
plan/loop positives, exact spans, aggregate work bounds and the
occurrence/member-hash/slot-width laws are preserved.  D09 multi-
chunk/process association remains deferred (these negatives are not
multi-chunk evidence); the D10 delivery claim requires independent
strategic acceptance.
Round 017-n completed the per-request identity-inventory repairs
required by 017-m on the same inert surface (no capture
utility/child modification, no actual capture, no process
collector): (1) the Responses `custom_tool_call` wire family now
joins the schema-evidenced call inventory alongside
`function_call` — identity bookkeeping only, earning no custom-tool
read parsing, execution or acquisition (a custom call named like a
supported tool still never acquires), its opaque `input` never
captured as arguments or reinterpreted as a shell/source oracle,
with no generic unknown-family wildcard recognition — so an exact
colliding ID makes the ambiguous eligible chain typed
`DUPLICATE_CALL_ID` non-removable with no acquired digest, span or
proven members (every relevant occurrence observable, never
first-match), while a unique unrelated opaque custom call neither
records nor poisons a separate valid read; (2) `max_commands` and
`max_outputs` are now enforced against the **complete** relevant
inventory — every schema-position call record (supported,
unsupported, opaque custom, missing/empty/malformed ID) and every
result record (including invalid IDs) — before any identity map or
typed diagnostic is retained, yielding the fixed non-acquiring
`OVER_BOUND` record (no truncated acquisition missing a later
collision), with the scan itself bounded by the existing `max_items`
item bound, the bound scoped to the selected domain under explicit
endpoint selection, and mixed input bounded across its inspected
domains; (3) absent/null/empty result IDs are typed
`MISSING_RESULT_ID` and present non-string result IDs typed
`MALFORMED_RESULT_ID` — fixed, non-echoing, unpaired limitations
that never invent an ID, hash an unhashable value, attach the
output to a call, or acquire, while separate well-formed chains
remain useful within the total limits and the existing
duplicate/missing/mismatched/pre-call typing is preserved.  The
public regression proof (both collision orderings, repeated
identical/conflicting records, supported/unsupported/custom
positive controls, missing/null/empty/list/dict/number result IDs,
all-inventory at-limit and one-over bounds on Responses and Chat
including many `tool_calls` in one assistant message, and a late
collision beyond any retained prefix) is earned in
`tests/test_bundle_d10_matrix.py::TestWireFamilyInventoryAndBounds`;
all previously earned D10 causality tests, selected/mixed/ignored
domain behavior and literal read/plan/loop positives are preserved
with unchanged inputs and non-echoing reprs.  No shell/filesystem/
network oracle and no new dependency.  D09 multi-chunk/process
association remains `NOT RUN`; no v1 runtime claim.
Round 017-o completed the two remaining per-request boundary
repairs on the same inert surface (no capture utility/child
modification, no actual capture, no process collector): (1) the
complete relevant call/result inventory bounds are now enforced
**before retention** — a no-retention streaming preflight decides
`max_commands`/`max_outputs` over the complete inventory (every
schema-position call record, every result record including invalid
IDs) and stops at the first exceeded limit, so an over-bound request
is a fixed non-acquiring `OVER_BOUND` before any record tuple,
location string, identity map, typed diagnostic, argument/wrapper
parsing or identity mapping is retained or built; the bounded
collection pass retains at most the declared counts, and the 2 MiB
allocation regression ceiling at inventory budget one (excluding
inputs, imports and full-payload fingerprinting — a generous
regression ceiling, not a new runtime setting or total-RSS
guarantee) is proven by the frozen allocation probe and the public
`TestInventoryAllocationAndIdRepresentation` suite in
`tests/test_bundle_d10_matrix.py` on large prebuilt Responses calls,
nested Chat calls, Responses results and Chat results at limit one,
with
at-limit useful reads keeping their exact digest/span/member/width
proof and one-over/late-collision/invalid-ID/ignored-domain/mixed
shapes keeping their typed behavior; (2) exact internal call/result
IDs stay usable while operational `str`/`repr` of report/read/
unpaired objects never echo private ID values (fixed `<private-id>`
placeholder for non-empty values; the observable no-ID state, fixed
enums, counts, locations and digests remain visible; synthetic
canaries only — no actual secret or private body test data).  This
supersedes the 017-n status wording "before any identity map or
typed diagnostic is retained": the pre-017-o code had already
retained the record lists and location strings before the bound
check — from 017-o the bound is decided before any retention.  D09
multi-chunk/process association remains `NOT RUN`; no v1 runtime
claim.
Round 017-p extends the same inert surface in two bounded parts (no
capture utility/child modification, no actual capture, no process
collector).  (1) Per-nested-container scan guard: `observe_reads`
now length-tests each inspected assistant `tool_calls` list against
the existing `max_items` item bound BEFORE it is iterated, parsed
or retained — counting every raw entry regardless of schema, type
or ID — so an over-limit nested list is the fixed non-acquiring
`OVER_BOUND`, and `max_items` is explicitly a **per-container**
bound (never a total across lists): an at-limit nested list passes
and observes normally, and non-assistant `tool_calls` fields are
uninspected.  The 017-o structural no-retention preflight remains
the retention proof; the 2 MiB allocation regression ceiling at
inventory budget one remains supplementary (a generous regression
ceiling — not a scan-count oracle, not a new runtime setting, and
no total-RSS guarantee).  The public regression proof
(at-limit useful read, one-over with and without a valid call,
selected-domain scoping, mixed over-bound, malformed nested types,
non-assistant uninspected, per-container-not-total) is earned in
`tests/test_bundle_d10_matrix.py::TestNestedScanBounds`.  (2)
Disposable-CI containment capability (a D10 prerequisite; the
first remote job run at the previously published head `ec08a1b`
failed `runtime-invalid` and this round corrects the runtime-shape
handling — the capability qualification is `PENDING` strategic
review, with the exact execution outcomes/SHAs in the immutable
round report
`oap/reports/017-p-observation-native-fixture-prerequisites.md`):
`scripts/cache_native_containment_probe.py` (an
in-container stdlib probe emitting a closed JSON pass record —
dedicated nonroot uid/gid with no supplementary groups, all-zero
capability fields, no-new-privs, seccomp filter mode, private
pid/mnt/ipc/uts/net against the shared user namespace, parent proc
and sentinel absence, private-loopback-only interfaces with echo,
parent listener unreachable, read-only rootfs denial, explicit rw
bounded tmpfs roots, exact memory/swap/pids/writable-storage
limits, keyring syscall denial (x86_64 `add_key`=248,
`request_key`=249 four-argument, `keyctl`=250 unknown command —
expecting EPERM), and a child deadline kill) and
`scripts/cache_native_containment_ci.py` (a host-side runner that
refuses every non-disposable-CI context): the digest-pinned
byte-identical-base fixture image, create-before-start ownership
(bare 64-hex CID registered before any start), the exact
confinement surface (`--network none`, read-only rootfs, dedicated
nonroot uid, cap-drop ALL, no-new-privileges, explicit
`seccomp=builtin`, bounded memory with no swap, pids 64, 1 CPU,
explicit tmpfs roots), closed inspection extraction (the actual
`ReadonlyRootfs` field plus the exact default runtime identity),
the ordered parent-death proof (a live owned descendant bound to a
per-run token is positively observed exactly once BEFORE the
registered container is killed, its disappearance and the
container's verified absence are required AFTER, and the unrelated
parent-owned sentinel must survive; a vanished-entry /proc scan is
never conflated with absence and any other read error fails the
scan), bounded capture (the pipe is owned by the reader thread
alone, a leader exit with a held pipe converges by the exact owned
group kill after a bounded grace, a failed capture is the fixed
closed state `output-read-failed` — never an empty-success output
or an uncaught thread exception), verified image removal (the
result-checked `rmi` plus an authoritative absence query; cleanup
failures stay visible even when a primary check also failed), and a
fresh owned 0700 scratch root validated as-given (no symlink or
`..` alias laundering of a pre-existing target).  Forty-two public
orchestration tests, now Sixty-one
(`tests/test_cache_native_containment_ci.py` —
fake docker emulation plus tiny real owned children only; no docker
daemon, namespace or syscall probe) and the new
`cache-native-containment` CI job (disposable `ubuntu-latest`
runner, stdlib only, no secrets forwarded to the fixture — the job
maps no secrets and the runner accepts no credentials —
`persist-credentials: false`)
carry the local and remote halves.  This capability proof is NOT
genuine native-client qualification: no genuine client, model, GPU
or gateway activity; D09 remains `NOT RUN`; no v1 runtime claim.

### 11a. Round 017-r: serial right-pane native fixture preparation
(inertia and limits; no D-syntax change)

Round 017-r lands the reviewed fixture prerequisite for the later
human-authorized serial foreground handoff.  It is a **small inert
preparation**: repo-owned stdlib-only fixture modules
(`scripts/cache_native_fixture_model.py` — the typed
phase/budget/closed-schema model; `cache_native_fixture_controller.py`
— the in-container 21001 PID1 fake provider/issued-registry
controller; `cache_native_fixture_standin.py` — the 21002
Python stand-in subject; `cache_native_fixture_export_client.py` —
the protected 21001 exporter client), a distinct fixture image
(`scripts/cache_native_fixture.Dockerfile`) and the host runner
`scripts/cache_native_fixture_ci.py` that drives ten fresh-container
scenarios on disposable GitHub-hosted CI only (the new
`cache-native-fixture` job, Python-only; no job or test line
invokes the native binary — asserted statically).  The phase model
is explicit and derived from measurement: prepared -> measured ->
synthetic scenarios -> quiesced -> frozen selected snapshot ->
teardown-verified -> publication.

Confinement (measured, never inferred from argv): dedicated
nonprivileged controller/exporter UID/GID 21001 (controller is
PID1) and native-subject UID/GID 21002; `--network none` private
loopback, read-only rootfs, cap-drop ALL, the actual SecurityOpt
no-new-privileges/builtin-seccomp strings, private
pid/mount/ipc/uts/net, no caller-configured host bind
mounts/devices (the daemon's standard tmpfs facts — e.g. the
bounded /dev/shm — stay distinct from caller mounts); finite
documented limits sized for an eventual native Rust client
(memory 1 GiB, swap 0, CPUs 1, PIDs 96, the reconciled
writable-data surface: distinct tmpfs budgets totaling 192 MiB
plus the daemon's /dev/shm explicitly bounded to 64 MiB — 256 MiB
effective total, verified from the actual HostConfig ShmSize);
`--log-driver none` verified by actual inspection.  The 21002 exec
subject measures its OWN uid/gid/groups, all capability sets,
NoNewPrivs, seccomp, namespace comparison against the disposable
parent, loopback-only reachability, the reviewed harmless
keyring-denial ABI, the effective memory/swap/pids bounds and the
reconciled writable-data inventory from its ACTUAL mount table
(bounded table input; kernel virtual/device filesystems a distinct
class; an unlisted writable data mount or a missing documented
root fails closed); controller-private paths/sockets are
denial-proven from 21002.  Scenarios: controller
measurement, 21002 exec measurement, PTY attachment through the
owned host-side seam (the later native attach point), synthetic
success/fail/hang tool cycles against the fixed loopback provider,
bounded output cap, failed export, failed quiesce and controller
crash — with an unrelated parent-owned sentinel that must survive.

Public pinned artifact (static preparation only, never executed in
R): the legitimate Codex 0.164.0 Linux x86_64 musl release archive
(tag `rust-v0.164.0`, OpenAI commit
`6aaac694803004a63c6f393d153c96d22521a6b9`, archive SHA256
`90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4`,
114,979,035 bytes) is fetched with bounded reads, its complete
size+digest verified BEFORE extraction, and then only the single
expected regular executable member is extracted (no symlink,
hardlink, path-escape, extra/duplicate or empty member; decompressed
size bounded to a reviewed finite ceiling).  The pinned public
LICENSE (10,926 bytes) and NOTICE (242 bytes — the Ratatui-derived
MIT credit the pinned upstream publishes) are fetched with the same
bounded reads and their full byte identity (size, closed markers,
exact sha256) verified before they enter the build context; both are
installed immutably (root-owned 0444) alongside the 0555 binary PATH
entry.  Signature verification was not performed: `NOT RUN`.

Accounting is one non-resettable host ledger shared with the single
run deadline: distinct measured quantities stay distinct (host
command admissions/refusals; drained vs retained bytes — a
timed-out capture is charged its measured drained total before the
scenario consumes the timeout, so a hang emitting discarded output
cannot skip the output budget; provider requests that received a
response — a refused call is still a request — vs client wire
attempts vs admitted/refused outcomes vs readiness polling); each
scenario's closed worst-case wire bound is checked against the
REMAINING budgets by a sequential PRE-WORK bound check before its
work may start (the check compares the current counters plus the
scenario's closed worst case with the remaining caps; it stores no
held amount — measured scenario charges accumulate instead), so an
over-budget scenario never begins; each scenario's measured facts
are then charged at scenario end with all validation before any
counter mutation (no reset, refund or re-budgeting), and a failed
or unknown phase aborts the run closed — its unmeasured wire work
is never silently re-budgeted.  The
post-teardown /proc scan uses a closed listing bound: a complete
listing at the bound counts, an over-bound listing is rejected
before any presence/absence claim (never silently truncated into a
false absence), and a vanished entry is expected churn.  Cleanup is
exact-owned and honest: the verified-absent-before-build fresh tag
is never adopted; a missed build-ID discovery recovers the exact id
from the owned tag under the single bounded cleanup grace (an
unresolvable ownership is a recorded unverified failure, never a
silent skip); the fresh owned scratch root is destroyed last and the
destruction is verified (a failed destruction is exposed on the
preserved primary failure); the retained evidence is published
atomically no-overwrite (same-directory 0600 temp, full digest
before the atomic link commit — a concurrent destination is
preserved, never overwritten; a destination inside the scratch root
or a link/foreign-owned path is refused).

The Python-only disposable-CI capability is the first bounded slice
of the later native evidence: actual hosted execution of the
fixture (image build, ten scenarios, exact teardown, selected
evidence publication) is the `cache-native-fixture` job; its
qualification of the serial handoff preparation remains `PENDING`
strategic review of the actual job outcome, and D09 (genuine
native capture/collector) remains `NOT RUN` in R.  No product
parser, source or legacy runtime behavior changed; the fixture is
not imported into the adapter path.

### 11b. Required-syntax matrix (handoff 6.2 literals and D01-D10, as of 017-r)

R changes no D-syntax surface (no parser or observation change this
round); the states below are the carried P/Q states, mapped to the
ACTUAL test assertions (the exact node IDs are the runnable proof;
where a class is named, the full node list is in
`docs/CACHE-REWORK-LEDGER.md`).  Statuses: `EARNED` = acquisition
under the named typed slice; `RECOGNIZED-ONLY` = parsed/typed with
the stated limitation, no acquisition; `UNSUPPORTED` = typed
unsupported, non-acquiring; `NOT RUN` = no measurement earned.

Handoff 6.2 literals:

| Handoff 6.2 literal | Status | Actual evidence (exact node) |
| --- | --- | --- |
| `cat A.md` | EARNED | tests/test_bundle_read_grammar.py::TestSupportedForms::test_single_relative_operand; tests/test_bundle_tool_results.py::TestWholeBundles::test_single_complete_read |
| `cat /work/A.md` | EARNED | tests/test_bundle_read_grammar.py::TestSupportedForms::test_absolute_workspace_operands; tests/test_bundle_client_paths.py::TestAbsolutePaths::test_simple_absolute_under_workspace |
| `cd /work && cat A.md B.md` | EARNED | tests/test_bundle_compound_reads.py::TestLiteralCdTransitions (class); tests/test_bundle_read_grammar.py::TestSupportedForms::test_two_operands_in_order |
| `cat A.md && cat B.md` | EARNED | tests/test_bundle_compound_reads.py::TestChainedReadPlans (all-cat `&&` plans: one ordered bundle, order/duplicate preservation) |
| `ls -la /work && cat /work/A.md` | UNSUPPORTED (ls read) / RECOGNIZED-ONLY (requested member) | the `ls` family is a typed NON-ACQUIRING read: tests/test_bundle_compound_reads.py::TestPlanNegatives::test_ls_family_is_not_a_read_and_mixes_output asserts `COMMAND_UNSUPPORTED` + `OUTER_BOUNDARY_UNPROVEN` (requested A exists as finite parsed data; nothing is proven), and ::TestMixedOutputNegatives::test_ls_family_exit_zero_is_not_support asserts `UNSUPPORTED`, no digest, no proven members and non-removable even with global exit 0; the earned D06 slice is the all-cat chained plans and outer-label regions, which do not earn the ls form |
| `for f in A.md B.md; do echo "=== $f ==="; cat "$f"; done` | RECOGNIZED-ONLY (labeled unguarded loop) | membership is finite parsed data (variable/list/echo/cat kinds, members A.md B.md) with the exact typed limitations `LOOP_ITERATION_UNPROVEN` + `OUTER_BOUNDARY_UNPROVEN` and no bundle digest: tests/test_bundle_literal_loops.py::TestHumanForms::test_unguarded_echo_form_membership_is_recognized; recognized membership is not proven execution and is not removable at composition: ::TestHumanForms::test_unguarded_echo_form_is_not_removable_at_composition; the EARNED loop slice is the guarded echoless form (::TestHumanForms::test_guarded_echoless_forms_are_earned, ::test_guarded_loop_is_one_complete_ordered_bundle, ::test_guarded_template_loop_proves_ordered_policy_files) |
| `for d in alpha beta; do cat "policies/$d/AGENTS.md"; done` | RECOGNIZED-ONLY (unguarded template loop) | membership is finite parsed data with `LOOP_ITERATION_UNPROVEN` (recognized requested membership, not proven execution): tests/test_bundle_literal_loops.py::TestHumanForms::test_unguarded_template_form_membership_is_recognized; non-removable at composition: ::TestHumanForms::test_unguarded_template_form_is_not_removable_at_composition; the EARNED slice requires the exact per-iteration `\|\| exit 1` guard (contract section 4b) |

D01-D10 criterion-by-criterion (actual module/test, exact earned
slice versus remaining gap):

| D | Criterion (handoff) | Earned slice (actual proof) | Remaining gap |
| --- | --- | --- | --- |
| D01 | Valid automatic `AGENTS.md` message + environment metadata | exact source extraction, environment excluded, directory scope, CRLF bytes exact: tests/test_bundle_root_envelopes.py::TestCanonicalSanitizedFixture::test_real_format_canonical_fixture_parses_with_exact_bytes, ::test_adjacent_environment_tail, ::test_newline_separated_environment_tail, ::test_separate_item_environment_is_excluded, ::test_crlf_envelope_preserves_crlf_content_bytes; 017-b ::TestLabelByteBound | strategic acceptance PENDING |
| D02 | Fake marker in assistant text/tool description; malformed or duplicate envelope | no false root / typed occurrences: tests/test_bundle_root_envelopes.py::TestNoAuthorityWithoutEnvelope::test_assistant_envelope_never_creates_root, ::test_marker_prose_at_later_offset_is_not_a_root, ::test_tool_output_envelope_is_not_a_root, ::test_unclosed_tail_is_typed, ::test_nested_duplicate_opening_marker_is_typed, ::test_duplicate_closing_tag_in_tail_is_typed, ::test_invalid_labels_and_delimiters_are_typed, ::test_valid_root_coexists_with_observable_malformed_occurrence | strategic acceptance PENDING |
| D03 | Single relative/absolute workspace `cat` | tests/test_bundle_read_grammar.py::TestSupportedForms::test_single_relative_operand, ::test_dash_dash_separator, ::test_absolute_workspace_operands; tests/test_bundle_client_paths.py::TestAbsolutePaths::test_simple_absolute_under_workspace, ::TestMalformedUnicodeAndSpaces; tests/test_bundle_tool_results.py::TestWholeBundles::test_single_complete_read, ::test_empty_file_is_complete_empty_version, ::test_unicode_crlf_bytes_are_exact | strategic acceptance PENDING |
| D04 | `/work-other`, traversal, unknown root, quoted `cat`, heredoc write | conservative typed non-acquisition (sibling prefix outside, traversal typed, unknown root unproven, quoted literal per convention, URL/query never mapped): tests/test_bundle_client_paths.py::TestAbsolutePaths::test_sibling_prefix_is_outside, ::test_lexical_dotdot_escaping_is_traversal, ::test_outside_absolute_path, ::test_absolute_with_unknown_workspace, ::test_relative_without_workspace_is_unproven, ::test_relative_traversal_escape, ::test_fully_quoted_literal_operand_under_no_spaces_convention, ::test_url_fragment_is_literal_never_stripped, ::test_query_syntax_is_never_mapped_to_the_plain_file; tests/test_bundle_read_grammar.py::TestSafeNegatives::test_unsupported_shapes_are_typed_never_complete, ::test_no_expansion_no_evaluation | strategic acceptance PENDING |
| D05 | `cat A.md B.md` without internal separators | tests/test_bundle_read_grammar.py::TestSupportedForms::test_two_operands_in_order, ::test_repeated_operand_preserves_order; tests/test_bundle_tool_results.py::TestWholeBundles::test_two_members_without_separators_is_one_ordered_bundle (one complete two-member bundle; no fabricated individual hashes) | strategic acceptance PENDING |
| D06 | Chained reads with `ls`, labels and unrelated output | all-cat `&&` plans and outer-label/outer-region composition: tests/test_bundle_compound_reads.py::TestChainedReadPlans, ::TestEchoOuterBoundaries, ::TestOuterRegionComposition, ::TestOuterSourceRegions — this slice does NOT earn the `ls` form (see the ls+cat literal row above: `ls` is typed unsupported, non-acquiring) | the ls+cat required-syntax variant remains pending scope audit; strategic acceptance PENDING |
| D07 | Literal loop, supported wildcard evidence, explicit `workdir`/`cd` | guarded echoless loop forms (one complete ordered bundle; ordered policy files; per-call workdir; absolute template): tests/test_bundle_literal_loops.py::TestHumanForms::test_guarded_echoless_forms_are_earned, ::test_guarded_loop_is_one_complete_ordered_bundle, ::test_guarded_template_loop_proves_ordered_policy_files, ::test_per_call_workdir_resolves_expanded_relative_members; literal `cd`: tests/test_bundle_compound_reads.py::TestLiteralCdTransitions — this slice does NOT earn the literal unguarded/labeled human forms (typed `LOOP_ITERATION_UNPROVEN`/`OUTER_BOUNDARY_UNPROVEN`, recognized membership non-removable) or wildcard membership (`GLOB_UNPROVEN`) | the unguarded/labeled loop required-syntax variants remain pending scope audit; strategic acceptance PENDING |
| D08 | Read succeeds/later fails; earlier fails/later succeeds | per-read evidence distinguished from global exit as CONSERVATIVE uncertainty: tests/test_bundle_compound_reads.py::TestPerReadVersusGlobalExit (a nonzero chain proves NO read and no digest — requested members preserved, wrapper status recorded; earlier-failure/later-success, truncated chain, process-running, malformed-Unicode, chat composition, mixed suppression) — these negatives prove conservative uncertainty, NOT per-read completion where no completion evidence exists | strategic acceptance PENDING |
| D09 | Truncation, partial `head`/`sed`, missing output, multi-chunk process | typed partial/truncation UNSUPPORTED/unsupported negatives only: tests/test_bundle_d10_matrix.py::TestUnsupportedAndPartialMatrix (command substitution `$()`/backticks, partial `head`/`sed`, known truncated/missing/running/unknown wrappers — never complete whole-file acquisitions) | `NOT RUN`: genuine multi-chunk process completion and the process/chunk association remain for a later same-PR suffix (a later exact order may authorize one bounded reviewed actual capture, then the process/chunk collector) |
| D10 | Duplicate/mismatched call IDs, command substitution, unexecuted branch; wire-family inventory | eligibility-independent call-ID inventory, structural-position causality, the composition matrix, the unsupported/partial matrix and the wire-family/inventory bounds: tests/test_bundle_d10_matrix.py::TestIdentityConflictPrecedesEligibility, ::TestStructuralCausality, ::TestD10MatrixComposition, ::TestUnsupportedAndPartialMatrix, ::TestWireFamilyInventoryAndBounds, ::TestInventoryAllocationAndIdRepresentation | strategic acceptance PENDING |

`head`/`tail`/`sed`/pipes/glob/Python-reader families remain typed
per actual evidence (partial/truncated typed, glob
`GLOB_UNPROVEN`, substitution typed) — no blanket earnings claim,
and no negative test is upgraded into a positive acquisition claim.

### 11c. Serial foreground handoff runbook (order 017-r section 5 —
preparation only; no execution in R)

This runbook is the explicit order-section-5 deliverable: the
concrete future sequence that preserves the existing coding worker
in the SAME right-pane Bash job/TTY.  It grants NO execution: R
performs no stop, no resume, no local Docker and no native launch;
a later active order must authorize the execution and record the
actual local measurements before any step below is taken.  The
unimplemented local preparer (local build/start of this exact
fixture) and the environment handoff helper are explicit later
execution gates, not claimed runnable or qualified paths.

Fixed invariants (re-verified before every step, never assumed):

- The worker is restored through the verified existing Bash job:
  no `codex resume`, no replacement/restarted Codex startup, no
  CI/background/native instance, no profile change.  The native
  argv stays exactly `codex --yolo --profile early-beta`.
- No Bash job number is assumed, no Ctrl-Z-on-raw-terminal is
  assumed, no stopping signal's effect is assumed (the later order
  selects and verifies the actual stopping signal for this CLI),
  and the coding tool's subprocesses are NOT assumed to share the
  parent's PGID: every identity is read from the live process
  table and controlling-terminal metadata and cross-checked; any
  mismatch aborts the sequence with no signal sent.
- Only the exact verified process group is ever signaled (the
  verified NEGATIVE group ID, never PID 0 or -1, never the parent
  Bash's group, never a name/UID pattern); no cleanup/restart of
  other repositories.

Step 1 — read-only discovery of W/B/G and the foreground boundary
(no signal, and no `jobs` in B: B cannot run its job builtins
while its foreground worker owns the TTY):

1. Discover the RIGHT pane's TTY path from the pane whose command
   is the coding worker (pane identity by command, not by assumed
   pane or job number).
2. Find the worker main PID `W` as the process on that TTY whose
   argv is exactly the allowed startup argv
   (`codex --yolo --profile early-beta`).
3. Read `/proc/W/stat`: field 4 (ppid) must be the pane's
   interactive Bash `B` (verified by its command/image, not by
   name pattern); field 5 (pgrp) is the worker group `G`; field 7
   (ctty) and `/proc/W/fd/0` must be the RIGHT pane TTY.
4. B's own process group (field 5 of `/proc/B/stat`) must DIFFER
   from `G`: a foreground job runs in its own group; if `G`
   equals B's group, the identity is not the expected one —
   abort.
5. Read the foreground process group `F` from read-only process
   metadata: field 8 (tpgid) of `/proc/W/stat` — the TTY's
   foreground group as reported in the worker's own stat — must
   equal `G`; cross-check with the read-only
   `ps -p W -o pid,ppid,pgid,tpgid,sid,tty,stat,comm` record (and
   B's own ppid/sid).  Do NOT issue an external `TIOCGPGRP` ioctl
   on the pane's slave TTY: from a session that does not control
   that slave it fails closed with ENOTTY (Linux `tty_jobctrl.c`,
   `tiocgpgrp`), and the runbook never acquires or steals a
   controlling terminal to make an external ioctl work.  Values
   observed at review time (particular PIDs, tty names, session
   IDs) are observation-time facts, never hardcoded future
   identities.  The requirement `F == G` means the worker's group
   is B's current foreground job.
6. Complete group membership: scan `/proc` read-only and
   enumerate EVERY actual process whose pgrp equals `G` (field 5
   of `/proc/PID/stat`); each member must be verified as an
   intended member of the worker job (the worker itself or one of
   its tool subprocesses) — enumerating W's descendants alone does
   NOT enumerate every member of G.  Separately, enumerate W's
   descendants that sit in their OWN distinct groups (owned
   background tool sessions) and verify each is idle or
   terminated at this boundary: stopping group `G` does not stop
   separately grouped tool processes, so a surviving non-idle
   separately grouped owned session aborts the sequence (the
   unrelated sentinel's survival alone does NOT prove the
   complete target membership).
7. Clean no-mutation boundary: `W` must be at the idle OAP
   control wait (a descendant `oap_fifo.py wait` argv is
   observable) with no in-flight command, commit, push or
   publication.  Record the repository branch/head read-only for
   the post-restore comparison.  If any identity disagrees,
   STOP — no signal is sent.

Step 2 — stop only the verified worker job (later order only):

1. Re-verify W, B, G, `F == G` and the step-6 grouping exactly as
   discovered (any drift aborts).
2. The later order selects and verifies the actual stopping
   signal for this CLI (SIGTSTP is the candidate); do not assume
   a raw-terminal Ctrl-Z and do not assume a catchable signal
   necessarily stops the CLI.
3. Signal ONLY the exact verified group, expressed with the
   verified NEGATIVE group ID and an option terminator:
   `kill -s TSTP -- "-${G}"` — valid only once the checks above
   have established `G > 1` and the exact intended group
   membership (Linux `kill(2)` semantics; never PID 0 or -1,
   never B's group, never a pattern).
4. Verify the stop before proceeding: the state of EVERY
   intended member of group `G` (as enumerated in step 1) is `T`
   in its own `/proc/PID/stat` — W's stopped state alone does not
   prove the rest of the group is stopped; a fresh field-8 read
   of `/proc/W/stat` still reports the foreground tpgid `G` (a
   stopped foreground job remains the TTY's foreground group); B
   is at its prompt again; the separately grouped owned sessions
   are still idle/terminated; and the unrelated parent-owned
   sentinel (and any other-repository process) is verified still
   running.

Step 3 — fixture container and the 21002 environment handoff
(later order only):

The fixture container (this R image; controller/exporter 21001 as
PID1; private loopback provider; the owned bounded tmpfs budgets;
`--log-driver none`) is built and started locally only under the
later order.  A Python-only setup exec as 21002 then creates the
fresh owned files in the subject's owned tmpfs (the
`/run/slaif-subj` budget, 0700, uid/gid 21002), from reviewed
templates, never copied from any host profile, config or key — the
synthetic state the R pty-attach scenario already exercises:

- `codex-home` (0700, uid 21002) as the fresh synthetic
  `CODEX_HOME`;
- the base `config.toml` (0600) pointing the client at the private
  loopback fake provider only (the 21001 controller endpoint on
  127.0.0.1, `wire_api = "responses"`, history persistence off);
- the SEPARATE `early-beta.config.toml` (0600) — official 0.164.0
  profile semantics: `--profile early-beta` overlays
  `CODEX_HOME/early-beta.config.toml`, not a `[profiles.NAME]`
  table;
- the generated fake provider credential (0600 file, a fresh value
  derived from the run token; the base config's `env_key` names
  the environment variable the client reads it from).

This runbook names only paths, owners, modes and the variable
name; it never reproduces config or credential contents, and no
host profile, key or home content is copied or printed.

Environment handoff law: an environment assignment made only
inside a terminated Python stand-in (or any prior exec) is NOT
automatically inherited by a later `docker exec`, and a later
exec does not inherit container PID1's runtime environment
either.  The foreground attach must therefore supply the
selecting environment explicitly on the exec invocation itself —
`-e CODEX_HOME=/run/slaif-subj/codex-home` plus the provider key
variable (its value loaded from the owned 0600 credential file by
the 21002 setup step, never printed) — so the later 21002 native
process provably receives the fresh synthetic `CODEX_HOME`, the
separate early-beta profile and the generated fake credential
from the owned tmpfs, and nothing else: no real key, provider,
home or profile forwarding.

Step 4 — bind the stopped job, then foreground the one native
subject:

1. NOW that B has regained the foreground, run B's REAL `jobs -l`
   and bind the now-stopped job by W/G (the listed job line whose
   PID matches the verified worker group leader; its state must
   be stopped).  Let `J` be the ACTUAL numeric job field of that
   verified line — taken from this listing, never assumed and
   never read from a new shell.
2. From B, run the owned attach in the foreground: `docker exec
   -it --user 21002:21002 <verified CID> codex --yolo --profile
   early-beta` with the explicit `-e` wiring from step 3.  `-it`
   uses the same owned host-side PTY seam the R pty-attach
   scenario demonstrated with its Python stand-in; that scenario
   is prerequisite proof of the seam (a real owned PTY allocated
   to the exec child), NOT the measured identity, TTY or
   capability properties of the later native process — the
   native subject's own measurements happen in the later order
   and are never labeled as already performed by the stand-in.
   `--user 21002:21002` keeps the subject under the dedicated
   confinement identity.  The run is bounded by an explicit wall
   deadline recorded in the later order; on deadline the owned
   exact-CID/owned-image teardown applies.  A native version
   observed during this run may be correlated against the pinned
   public archive digest; no path here invokes the binary for a
   version check, and the CI job still invokes no native binary.

Step 5 — teardown, export, restore:

1. On subject completion (or bounded deadline): quiesce the exact
   owned client/tool processes and the provider's admitted
   sockets/handlers, freeze the CLOSED selected snapshot, retrieve
   it over the protected 21001 exporter channel while the
   container still exists, validate the closed schema/counts/
   digests on the host, then verify exact CID/image/descendant
   teardown and publish only after verified cleanup (the R
   teardown-before-publication law; a failed quiesce cannot be
   called completed).
2. Return foreground to the SAME worker: re-run `jobs -l` in B,
   confirm the bound job is still the stopped worker (PID group
   G, state stopped), and restore it with the actual shell job
   expansion of the re-verified numeric ID — `fg "%${J}"` (the
   verified line `[1]+  Stopped  ...` yields `J=1`, i.e. the
   command `fg "%1"`); a literal `%J` is a different job spec and
   is never used, nor is any assumed number.
3. Restoration checks: `W` is running again on the SAME TTY and
   resumes its OAP control wait (no restart, no replacement); the
   branch/head recorded in step 1 is unchanged (read-only
   comparison).  The stopped worker performed no mutation, and
   the subject container has no host bind mount, so no concurrent
   coding mutation was possible — both facts are verified, not
   assumed.
4. Failure checks (fail closed): if the stop, the attach or the
   subject run cannot be verified, the sequence stops — owned
   exact-CID/owned-image cleanup first, then the verified-job
   restore, then a truthful record of the actual state.  If the
   bound job no longer verifies as the stopped worker, it is not
   restored as if it were the worker; the sequence stops and
   records the actual state.  The worker is never left stopped
   and no replacement worker is started; any residual uncertainty
   is recorded, not papered over.

What this runbook is NOT: it is not the hosted-CI execution
path.  The R runner entry guard refuses any context that is not
both `GITHUB_ACTIONS=true` and `RUNNER_ENVIRONMENT=github-
hosted`; that guard must never be spoofed to run the CI entry
locally — local execution is only this separately authorized
foreground sequence.  It grants no capability verdict: the
handoff-preparation qualification stays `PENDING` strategic
review of the actual R job outcome, and D09 (genuine native
capture/collector) remains `NOT RUN` until a later order executes
this runbook and records actual measurements.

## 12. Offline process-capture utility (rounds 017-i/017-j/017-k/017-l, inert)

Round 017-i lands `scripts/real_client_capture.py` (schema family
`slaif-real-client-capture-*-v1`; the selection record is
`slaif-real-client-capture-selection-v2` after the round 017-j
export correction), a small repo-owned capture utility
for **independent strategic review**. It is stdlib-only, explicit
opt-in, and **inert**: nothing in the adapter runtime imports or
consults it, and it never reads or modifies `oap/active` or
`oap/orders`. Its companion `scripts/real_client_capture_fake_child.py`
is a wholly synthetic child executable used **only** by the offline
test suite (`tests/test_real_client_capture.py`); it is not a client
and earns no genuine-client format authority.

### 12.1 Hard limits (fail closed; config may only lower)

- At most **1 actual attempt** under an external authorized-run
  identity (`max_attempts=1`, `max_requests=20`, `deadline_seconds=120`,
  `max_inbound_bytes=1 MiB` per request, `max_selected_bytes=256 KiB`,
  `max_child_output_bytes=4 MiB` aggregate, one concurrent
  child). `CaptureLimits.resolved` rejects over-hard or invalid values.
  The selected cap is enforced on the **exact UTF-8 bytes of the
  serialized selection record** (metadata and serialization overhead
  included), serialized once and published as those same bytes;
  exceedance is a typed `selected_over_bound` failure with no
  oversized or partial artifact, and the run record reports the
  exact published byte count in that unit.
- A persistent, non-sensitive **attempt ledger** (O_EXCL, 0600) claims a
  run ID before any genuine launch and consumes it exactly once with the
  truthful outcome; it can never be reset by a new wrapper invocation.
- A hard deadline independently terminates the **owned process group**
  (SIGTERM then SIGKILL) across all owned descendants, including after
  the leader has exited; the group is terminated and reaped **before**
  pipe-drain joins can pin the supervisor, with a bounded, reported
  teardown grace; unrelated sessions are never signalled. Group
  membership is verified gone after both normal exit and timeout.
- Finite reads on the owned fake provider: a stalling or truncated
  client (malformed, chunked, oversized, or invalid-length payloads) is
  rejected with a sanitized status; no handler thread can be pinned.
  EVERY request method and error-dispatch path consumes the per-run
  request budget before route, authentication, or body-outcome
  branches — known routes, unsupported routes, unsupported HTTP
  methods, malformed request lines, and unsupported versions (the
  accounting covers the BaseHTTPRequestHandler error-dispatch
  fallback, which 017-j's do_GET/do_POST-only centralization
  missed) — so no request or error path can evade the cap; error
  dispatch sends fixed sanitized bodies that never echo the request
  line or method, and authentication failures remain value-free.
- Bounded handler work: accepted handler concurrency is capped (hard
  cap 4 concurrent handlers); connections beyond the cap are closed
  without a response and counted; every admission-owned request
  socket is tracked in a bounded registry (capped at the
  concurrent-handler cap) and is shut down and closed as soon as no
  new admission can join it, so an in-flight bounded read a per-read
  timeout cannot stop (a progressing drip) is unblocked by an
  effective socket shutdown, the peer observes closure, and no
  handler can pin the bounded join; thread-start failure is counted
  and its socket closed; repeated stop is a safe no-op; in-flight
  handler work is joined under a bounded grace at quiesce time and
  unsuccessful teardown is reported honestly in the run record,
  never hidden, and can never yield a completed outcome (fixed
  `cleanup_failed`, no raw error details). Only sockets admitted by
  the owned server are ever touched; unrelated sockets and processes
  are never seen.
- **Finalization quiesce**: before any final validation or
  publication the owned provider is quiesced — the frame state is
  FROZEN (the append path rechecks the gate under the state lock, so
  no further append can happen), no new admission is accepted, every
  admission-owned request socket is shut down and closed (an
  in-flight progressing read is thereby unblocked and the peer
  observes closure), the accept loop stops, the listening socket
  closes, and the remaining in-flight handlers are joined under the
  bounded grace; an incomplete teardown is honestly reported and can
  never yield a completed outcome (fixed `cleanup_failed`). Validation and serialization then operate on
  the explicit frozen frame snapshot: every exported text is
  byte-verified in that final snapshot, and serialization cannot
  pick up a later unverified append (the 017-j ordering verified
  BEFORE drain/stop, leaving a check/append/write race).
- Child stdout/stderr are drained in bounded memory (byte counts only,
  never content); exceeding the cap terminates the owned group. Child
  output is never redirected to raw files.
- Binary preflight (`--version`/`--help`) output is bounded **while
  receiving** (bounded collection with a finite deadline); overflow
  and timeout are fixed, non-echoing failures; there is no
  buffer-then-truncate path.

### 12.2 Privacy law (enforced in code, not documentation)

- Bounded in-memory request parsing only (JSON with a recursion guard);
  the provider is log-silent; diagnostics are fixed enums, counts and
  digests. No raw request, system prompt, tool schema, header value,
  body, history, unknown stdout/stderr or credential ever reaches disk,
  console, errors, tracebacks or reprs.
- **Issued-binding extraction (runtime vs pure-facade)**: at RUNTIME
  (the owned provider receiver) selection is bound to the
  controller's ACTUAL issued records created BEFORE that provider
  request — the exact issued call ID, the tool family/name matching
  the offered tool schema, the declared step/command and expected
  argument values, and the controller-issued process ID on results.
  A preloaded, anticipated, or forged call is never selected before
  the controller issues it; issuance/completion is never inferred
  from a caller's predicted ID or forged earlier status (the
  controller's own gating already encoded causal progression when it
  issued each record), and valid echoed histories keep their
  occurrence order. The pure-facade candidate parsing (declared-step
  ID inference plus progression from the request's own completed
  outputs, where a later step's call counts as issued only after a
  structurally valid completed output for every earlier step that
  carries issued metadata) is a distinct FIXTURE mode used only by
  the offline pure controls; a constructor or manually populated
  ProviderState is not runtime provenance evidence. Unissued,
  orphaned, conflicting, mismatched, wrong-mode (wrong item family
  under the offered tool schema), undeclared-command, unknown tool
  mode, unknown item type (bounded sample count), over-bound
  metadata, and credential-marker (canary) hits are rejected or
  excluded with typed reasons, item by item; their raw values are
  stored nowhere.
- **Malformed-Unicode law**: a `str` carrying a lone surrogate (e.g.
  from a JSON `\ud800` escape) is malformed Unicode and can never
  be a faithful byte value. It is validated BEFORE any
  encoding, hashing, or retention on the function/custom
  output/argument and relevant metadata paths: the frame is
  rejected with the fixed typed `malformed_unicode` reason, the raw
  value is stored nowhere (not in exceptions, reprs, digests, or
  records), and no lossy replacement ever masquerades as fidelity.
  Valid non-ASCII Unicode (e.g. `\u00e9`) is processed normally and
  is never typed malformed.
- **Narrow synthetic text export (selection schema v2)**: the exact
  received result text of a proven selected synthetic frame is
  retained losslessly **only after** strict ownership, source/shape,
  and byte verification against the IMMUTABLE ORIGINAL seed bytes
  bound BEFORE the child launches — the exact bytes this run seeded
  (the default synthetic workspace files plus every explicitly
  supplied extra synthetic workspace file) for the declared read
  path (or the exact empty payload of a sleep step); the comparison
  never reads a child-writable file at finalization, so a child that
  rewrites its own seed after a legitimately issued read cannot
  redefine the purported original; anything else is stripped to
  metadata plus the exact-byte digest and counted
  `content_unverified` (or a typed non-echoing failure plus safe
  cleanup is raised), reaching no persisted record, console, repr,
  or diagnostic. Retained text is the actual received text —
  controlled synthetic fixture data, never reconstructed from hashes
  or guessed metadata; no full requests,
  user/system/developer messages, tool schemas, headers, histories,
  unknown child stdout/stderr, credentials, or unrelated tool output
  is ever persisted.
- Selected frames carry exact-byte digests of the raw output bytes
  and bounded metadata only (proven selected synthetic frames
  additionally carry the byte-verified result text above); the
  run/selection records carry
  `provenance: "synthetic-offline"` and `fixture_authority: "none"`.
- The child environment is built from scratch (fixed PATH, no parent
  auth/profile/config/keys/SQLite/hooks/login/network inheritance); the
  child CODEX_HOME is a fresh 0700 scratch directory, and the scratch
  root is removed only by exact per-entry, lstat-validated cleanup that
  refuses symlinks, foreign ownership, and escape paths.
- Output directories are protected without mutation: a pre-existing
  directory is accepted only when owned by this run's user and not
  group- or world-writable, is **never chmoded**, and a directory this
  run creates is created 0700; symlinks and foreign ownership are
  rejected in place.

### 12.3 Actual-client path (input-gated; not exercised this round)

`child_kind="actual"` requires, **all before any launch**: explicit
opt-in, a version/hash-bound read-only binary preflight
(`--version` and `--help` probes, bounded output, closed flag
set), a readiness record whose verdict is `ready`, and a matching
external authorization record. The gate is **input-driven, not
structural**: a caller-supplied `ready`/authorization record can
launch the bound stand-in binary through the public API (the
fail-closed tests demonstrate the block-until-records and
consume-once behavior). What this version cannot produce is a
*trusted* ready verdict: `evaluate_startup_readiness` can only ever
produce `not_ready`, because the H-round startup plugin sync shows
that relocating a private home plus `--ephemeral` does not prove
suppression of component/plugin downloads, updates, or telemetry,
and no packaged static evidence for the candidate controls
(`features.remote_plugin`, `features.plugins`,
`features.code_mode.enabled`, `features.unified_exec`) exists. Unknown
control means **not ready**, never a silent fetch. A literal `ready`
value in a hand-supplied record is **not** proof that those unverified
startup controls were verified or applied. The readiness record is
metadata-only (no observed flag text). Round 017-k repaired the
generated record's round-trip fidelity: the loaded facts
reproduce the record's validated flag count exactly for zero and
every nonzero known flag (the live preflight facts own the in-
memory flag set; the validated ``count ==
len(facts.detected_flags)`` binding replaces the 017-j placeholder
tuple, which always exported count 0 after loading), with no
flag-text export, no fabricated placeholder semantics, and no new
ready state — the generated verdict remains `not_ready`, and a
caller's literal `ready` record remains caller input, not
verification. No actual client, provider
session, or model call is made or authorized by this round; a future
exact order may authorize one bounded reviewed actual capture, and the
process/chunk collector follows earned format evidence (D09/D10).

### 12.4 Offline verification

`tests/test_real_client_capture.py` exercises only the offline
surface: injected synthetic child executables (pinned paths, no
installed-client fallback), the in-process owned fake provider over
raw sockets (auth, limits, malformed/chunked/oversized/invalid-length
robustness, finite stalls), allowlist extraction, supervision
(deadline/output-cap kills, unrelated-process survival, environment
isolation), the attempt ledger, the fail-closed actual-client gates,
workspace/cleanup guards, the CLI, and static guards (stdlib-only
imports, OAP decoupling, no raw-content persistence, marker
non-leakage). Round 017-j adds regressions for every repaired boundary:
issued-ID binding and progression (including non-selected marker
variants, input immutability, and malformed Unicode), exact
selected text/digest/byte counts, the serialized-byte cap, budget
centralization, bounded preflight, no-mutation directory rejection,
closed readiness/authorization schemas, the descendant deadline, and
deterministic non-root simulated-UID ownership-guard proofs (the
foreign-ownership cleanup test that requires a real `chown` remains
an explicit environment skip, never a pass). The permission fixtures
are intentional, so the suite runs under a process-local umask of
022. Its synthetic frames are synthetic test data; they are
**not** earned genuine-client fixtures.

Round 017-k adds public receiver/run/lifecycle regressions for
every repaired boundary: RUNTIME issued-registry binding through
embedded-mode fake children (preloaded first/later calls and forged
inbound progression are never selected before the controller
issues; the actually-issued echo is selected and byte-verified; a
constructor or manually populated state is not runtime provenance
evidence), wrong-family items under an otherwise valid offered
schema typed `input_shape_unsupported` with the matching-family
control, finalization quiesce (a REAL late HTTP request at the
public shutdown boundary is processed pre-freeze, byte-verified and
stripped to `content_unverified`, and its marker bytes appear
nowhere under the output directory; the frozen provider rejects
later appends with a fixed typed status and the frozen snapshot is
final; stop is bounded under a stalled in-flight handler with
honest teardown accounting), every unsupported method, malformed
request line, and error-dispatch path consuming a lowered budget
with fixed non-echoing sanitized bodies, bounded handler
concurrency with rejected over-cap connections and a surviving
server, generated readiness records round-tripping the validated
count for zero and every nonzero known flag without flag-text
export, and ACTUAL lone-surrogate values across function/custom
output/argument and run-level paths rejected with the fixed typed
`malformed_unicode` reason (no echo in any exported record) plus
valid non-ASCII Unicode controls. The two added frozen probes'
expectations (`check-capture-issued-registry.py` 2 checks;
`check-capture-finalization-v3.py` 8 checks) are covered by these
suites and are re-asserted by the canonical probes at the
implementation head. Skip accounting stays distinct: the 27 prior
stage skips plus the one foreign-ownership `chown` environment
skip; the simulated-UID and these new lifecycle proofs are passing
tests, never skips.

Round 017-l adds public receiver/run/lifecycle regressions for
every repaired boundary: an authenticated progressing slow-drip
body (1 byte per 0.05 s, defeating the 2 s per-read bound) whose
owned accepted socket is observed closed by the PEER from an
external socket after stop, with honest teardown accounting, a
repeated stop no-op, and an unrelated own-session process
surviving; a closed listener (the port re-bindable) with
idempotent stop; an incomplete teardown (a handler that ignores
the socket closure and outlives a tiny quiesce grace) producing
the fixed `cleanup_failed` outcome and never `completed`, with the
persisted record carrying only the closed enum set and the honest
boolean (no raw error details); the failure/timeout cleanup path
(a non-progressing stalled read rejected at the per-read bound
with complete teardown); actual-issued default-seed and
actual-issued custom-seed positives (an arbitrary declared path
`C.md` plus explicitly supplied seed bytes) retaining useful exact
received text with `content_verified` true; and the
child-mutated original negative — a child that rewrites its own
`A.md` after receiving the legitimately issued read and returns
the new bytes, with the marker bytes absent from every persisted
file, the frame stripped to `content_unverified` — plus an
unseeded-path negative (no original exists, never verified, never
invented). The added frozen probe
`check-capture-owned-io-and-seed-v2.py` (5 checks: three positive
controls plus two negatives) is covered by these suites and is
re-asserted by the canonical probes at the implementation head.
Skip accounting stays distinct: the 27 prior stage skips plus the
one foreign-ownership `chown` environment skip; the new 017-l
lifecycle proofs are passing tests, never skips.
