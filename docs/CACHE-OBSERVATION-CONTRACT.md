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
attempts vs admitted/refused outcomes vs readiness polling); a
readiness FAILURE records no readiness-poll count at all — that
is an UNMEASURED quantity and is never to be read as a claim of
zero actual readiness polls (any count that is reported is
measured, strictly typed and bounded by the probe's own closed
window); and when a nonzero bounded readiness exec produces no
closed probe failure record, the closed readiness diagnosis
(017-y) may issue the ONE conditional bounded read-only
lifecycle query of the SAME already-registered CID (exactly one
allowlisted `docker inspect` selecting the single finite fact
`.State.Status` — never the full State object, logs or any
listing), which is charged to this same ledger and clamped by
this same deadline before and after the work: only the closed
line `exited` refines the original `controller-not-ready`
category (`controller-not-ready:container-exited`), and any
other status, any other output shape and every query failure
(including a bounded timeout and a transport failure) stay
honestly UNKNOWN — a query failure is NOT absence and the
original fixed-unknown cause is preserved through
abort/cleanup/publication); each
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
evidence publication) is the `cache-native-fixture` job; the
bounded 017-r fixture preparation is accepted (strategic decision
at head `2ce9dcd`, with the recorded wording limitations), the
serial foreground handoff itself remains a later separately
authorized order, and D09 (genuine native capture/collector)
remains `NOT RUN` in R.  No product parser, source or legacy
runtime behavior changed; the fixture is not imported into the
adapter path.

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
   in its own `/proc/PID/stat` — the stopped STATE is the stop
   proof (W's pgrp remains `G` while stopped; a stopped
   foreground job does NOT remain the TTY's foreground group).
   Once every intended member is `T`, interactive Bash reclaims
   the terminal for its own process group before presenting its
   prompt (glibc job control: the shell regains terminal control
   for its own group via `tcsetpgrp`; GNU Bash Job Control
   Basics), so the foreground verification is: B is at its prompt
   again with state `R`/`S`, and the TTY foreground (field 8,
   tpgid, of `/proc/B/stat`) equals B's OWN verified pgrp (field
   5 of `/proc/B/stat`).  Do NOT require the impossible `F == G`
   after Bash has reclaimed foreground, and do NOT read W's
   field 8 as stop proof (after reclamation it reflects B's
   group, not the stopped job's).  The separately grouped owned
   sessions are still idle/terminated; and the unrelated
   parent-owned sentinel (and any other-repository process) is
   verified still running.

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
  127.0.0.1, `wire_api = "responses"`, history persistence off)
  plus the required optional controls of the exact pinned 0.164.0
  config schema (verified at
  `6aaac694803004a63c6f393d153c96d22521a6b9`, no native
  download/execution): `check_for_update_on_startup = false`,
  `analytics.enabled = false`, all three OTEL exporters
  (`exporter`/`trace_exporter`/`metrics_exporter`) set to
  `"none"`, and the plugin synchronization/remote-plugin/
  recommended-plugins/plugin-hooks feature booleans set to
  `false` — `features.plugins` defaults to TRUE at that commit,
  so it is set explicitly; the actual offered native tool modes
  are preserved (no `unified_exec`/code-mode swap).
  `history.persistence = "none"` is not proof that every rollout/
  log file vanishes: unavoidable native transient state remains
  private bounded tmpfs, destroyed with the exact fixture;
- the SEPARATE `early-beta.config.toml` (0600) — official 0.164.0
  profile semantics verified at the exact pinned loader:
  `--profile early-beta` loads `CODEX_HOME/early-beta.config.toml`
  as a second user layer ON TOP of the base `config.toml` (the
  profile needs only overrides), never a `[profiles.NAME]`
  table; a base config containing a legacy `profile = "..."`
  selector or `[profiles.NAME]` table is rejected by that
  loader;
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
bounded 017-r fixture preparation is accepted (strategic
decision at head `2ce9dcd`, with the recorded wording
limitations), the serial foreground handoff itself remains a
later separately authorized order, and D09 (genuine native
capture/collector) remains `NOT RUN` until a later order
executes this runbook and records actual measurements.

### 11d. Round 017-s: local fixture preparation and one Python-only
rehearsal (no D-syntax change)

Round 017-s lands the repo-owned stdlib-only local
preparer/supervisor `scripts/cache_native_fixture_local.py`,
reusing R's validated image/model/controller/exporter/stand-in,
the guarded executor, measured confinement, single run deadline
and ledger, artifact acquisition and ownership helpers — no
copy of the CI runner and no general framework.  The distinct
explicit local entry (`rehearsal`) carries the order-bound opt-in
(literal `017-s` + literal bound head, verified read-only against
the bound repository) and fresh protected work/evidence roots.

One long-lived non-Codex Python fixture owner (the supervisor)
owns every Docker operation through the closed guarded executor,
the exact resource registry (CID registered BEFORE start, image
identity, build intent, env file), the single 1800 s END anchor
plus one bounded 600 s cleanup grace, the non-resettable ledger
and the final evidence.  A thin CLI caller drives the protected
bounded lifecycle prepare / observe / rehearse / finish / abort
over a 0600 socket in a protected 0700 control root OUTSIDE the
disposable work root (state/abort files 0600): a caller death,
second phase or new directory cannot stop, reset or re-admit the
run; the owner converges its own exact-owned cleanup on its own
remaining budgets (SIGTERM and KeyboardInterrupt converge through
the same path), and container termination is by docker on the
exact registered CID only (no host PID signalling).  Prepare
measures the same reviewed confinement as R (21001 controller
PID1, 21002 subject, network none, read-only rootfs, cap-drop
ALL, no-new-privileges/builtin seccomp, private pid/mnt/ipc/uts/
net, 1 GiB/CPU 1/PIDs 96/swap 0, three configured 64 MiB
writable-data mounts plus the daemon's /dev/shm bounded to
64 MiB — four mounts, 256 MiB effective total — log-driver
none),
verifies the env-file handoff (0600 under 0700, exact two
synthetic keys, removed on every path) and the PTY attach with
zero wire, and observes the closed controller state
non-consuming; the pure attach plan (exactly `codex --yolo
--profile early-beta`, `executed: false`) is inert and is never
executed in S.  Rehearsal consumes the one-shot diagnostic with
the existing Python stand-in under 21002; finish is
variant-aware (python-rehearsal / unobserved / external) with
the retained summary bound to the decoded payload, and
`native_started` / `worker_stopped` / `codex_invoked` stay
false throughout.

Section 2 (verified local endpoint binding): the narrow
supported local endpoint is the documented default unix socket
(`/var/run/docker.sock`), verified read-only by lstat (it must
exist as a socket file; never connected), corroborated by the
daemon-declared name equal to this host's hostname through the
pinned bound executor.  EVERY run Docker child inherits a
FROZEN once-per-owner environment in which DOCKER_HOST is
pinned to that verified socket and the overriding context
selection is removed, so a stored currentContext or later
HOME/DOCKER_CONFIG/DOCKER_CONTEXT drift cannot redirect a later
action; an explicit remote selection (non-blank DOCKER_HOST or a
non-default DOCKER_CONTEXT) refuses BEFORE any mutation, and no
endpoint value (URL, credential, context name) is ever echoed.

The ONE bounded local rehearsal (only at the committed/pushed
reviewed head, fresh owned roots) ran EXACTLY ONCE, bound to
implementation head `2a9c44e2ee327b965828bafdfcaf444abc3a581c`
(source inputs `54ef177`), and PASSED through the full
prepare -> Python rehearsal -> finish lifecycle: the exact CID
was registered BEFORE start and the same CID bound across all
phases (alive through preparation, the diagnostic consume and
quiesce/freeze/export, with its final absence verified only
during terminal teardown, after the export); the Python
stand-in consume admitted the one valid diagnostic request
(the missing and wrong variants refused), returned the fixed
final text with no tools and no issued calls, and finish
quiesced closed-pass with the retained 2991-byte export bound
to the decoded payload.
Teardown left no prepared container, supervisor, listener, key
file or owned image (container and image removals
`absent-verified`, zero descendants, sentinel survived, owner
converged without its backstop), and the non-resettable ledger
recorded 5 API requests (3 admitted, 2 refused), 34 docker
admissions, 0 refusals and 23763 bytes drained/retained.  The
measured evidence (restricted-permission JSON) is preserved
with the round; the immutable round report records the
measured facts, the preserved pre-rehearsal CI failures and
all disclosed deviations.  CI remains Python-only with the ten
existing required checks (no new job; the pinned public Codex
binary is fetched and hashed statically in the R
`cache-native-fixture` job and is NEVER EXECUTED there —
including help/version — preserving the static acquisition and
the RIGHT-only startup law).  No native launch, no worker
suspension, no protected service or profile change: the
handoff-preparation qualification stays `PENDING` strategic
review of the actual outcomes, and D09 (genuine native
capture/collector) remains `NOT RUN`.

### 11e. Round 017-t: evidence finalization and inert native-handoff
preparation (no D-syntax change)

Round 017-t finalizes the S evidence record and lands the
REUSABLE, INERT preparation boundary for the later separately
activated RIGHT-pane native handoff.  It performs NO native
launch (including help/version), NO worker stop, NO local
Docker operation and NO new rehearsal; the S admission remains
consumed and the S/R/Q/P reports remain immutable.

Order/run binding (`scripts/cache_native_fixture_binding.py`):
the smallest typed immutable binding a later fixture
preparation needs — one explicit opted-in run bound, before
any mutation, to the exact active order ID (bounded OAP
grammar), its UNIQUE committed immutable order file (exactly
one `<ID>-*.md` in the bound source tree; disk bytes equal
the committed bytes), the literal committed source head (HEAD
equals it, clean worktree), the repository identity
(`owner/repo` parsed from the plain-HTTPS GitHub origin form;
the URL is never retained or echoed, private endpoints
refused) and a module-minted 32-hex run identity (never a
caller value).  Resolution is strictly read-only, makes no
GitHub/network call and mints no authority: publication/
review stays the separate strategic pre-execution gate, and
source parsing never invents permission from prose.  Each
order id gets its own stable one-attempt
`.oap-local/<order-id>/` namespace (atomic O_EXCL claim; a
changed head, directory or phase within the order NEVER
resets it); the historical 017-s record keeps its exact
schema and exhausted state.

Native-handoff preparation contract
(`scripts/cache_native_fixture_native_prep.py`, closed schema
`slaif-native-handoff-prep-v1`): small READ-ONLY collection /
validation seams for the LATER native path.  Fixture-owner
facts and external-native facts stay SEPARATE: the owner's
retained evidence (its own closed 017-s record: exact CID,
verified teardown, sentinel survival, export sha, and its
`codex_invoked` / `worker_stopped` / `native_*` flags — the
closed safety facts of the WHOLE historical S rehearsal run:
a full-rehearsal-scope statement that that run never invoked
Codex, never stopped the worker and never started a native
subject; NOT an owner-processes-only claim, and the new
native schema is separate, never an owner-only
reinterpretation of those flags) is parsed into typed
`OwnerFinalFacts` under the historical S schema; the native
subject is a distinct measured `SubjectIdentity`; the overall verdict is composed AFTER the
owner's own export/teardown finished (teardown-before-
restore ordering; nothing keeps the container alive until
restoration, nothing deadlocks finish on the stopped
worker).  No record can therefore claim "Codex was never
invoked" while a foreground native subject actually ran.

The closed identity laws the later native pass must satisfy
(finalized from this code, not prose):

- subject identity is adopted from the EXACT registered CID
  only (`source: cid-registered`); a host UID/name-only
  process or a caller-supplied bare PID is never proof;
  UID/GID exactly 21002 with the closed group law (empty, or
  the own primary 21002 — strict integers only); argv
  EXACTLY `codex --yolo --profile early-beta` (value AND
  recomputed digest); the pinned binary sha256 bound to the
  expectation; the birth bound (`/proc` start_time at or
  after the ticks measured at run admission — an unobserved
  bound is incomplete, never ready) and the expected-PTY
  provenance (the identity records whether the expected
  PTY was actually bound — a strict NONZERO int — and
  matched; an unobserved expected PTY or a measured tty0
  subject is `pty_matched` false and can never qualify
  native-ready, while legitimate no-TTY process parsing
  stays a separate capability);
- worker/Bash group facts are collected READ-ONLY: worker W,
  parent Bash B, pgrp G, session/TTY relation, complete
  bounded G membership (capped enumeration, tri-stated row by
  row — only an independently VERIFIED-gone listed entry may
  be ignored; an unreadable still-existing or unprovable
  entry cannot be classified as a non-member and is a closed
  `prep-group-incomplete` refusal, never a silently skipped
  row), separately grouped owned tool sessions distinguished,
  the actual Bash job J NEVER guessed, and the tty
  foreground pgrp a read-only observation (None = unobserved,
  never assumed); this round never signals W/G/B or changes
  foreground;
- the worker stop and same-job restoration are measured
  INDEPENDENTLY of the owner as two distinct phases: the
  RECORDED stop is the stable stopped phase — the worker W
  observed in state T, its parent Bash B running, G differing
  from B's group, every other observed G member stopped
  (each listed row tri-stated through the bounded absence
  seam — only an independently VERIFIED-gone entry may be
  ignored; an unreadable still-existing or unprovable entry
  cannot establish nonmembership or a complete G and is a
  closed refusal, never a silently skipped row), and the tty
  foreground observed back on B's group (Bash reclaimed the
  TTY; G does not hold the foreground while stopped) — a
  separately recorded event, never re-derived from a later
  snapshot; RESTORATION is measured AGAINST
  that receipt and holds only for the RUNNING phase: the
  same worker (pid, birth, group G, session, TTY) running
  again with the observed foreground back on G — a worker
  still stopped, a missing recorded stop, an unobserved or
  contradicting foreground, or a vanished process is
  honestly unknown, never restored;
- the verdict composes only typed measured records (or an
  explicit None): a caller-authored ready/status/flag JSON
  is a closed refusal; unknown/unobserved/incomplete facts
  can never be ready/pass, with the closed 15-reason
  vocabulary (no-owner-final / owner-teardown-unverified /
  owner-subject-context-mismatch / owner-subject-binary-
  mismatch / owner-native-unready / owner-scope-not-native /
  no-native-identity / subject-start-unbound /
  subject-pty-unmatched / subject-cid-unscoped /
  subject-binary-unmeasured / subject-absence-unverified /
  no-restoration / worker-stop-unmeasured /
  same-job-restore-unmeasured).
  A historical S-scope owner record decodes and validates
  under its own closed schema, but it can NEVER qualify a
  native-ready composition (the closed
  `owner-scope-not-native` refusal), and its flags are
  never relabeled as native facts.  An honest
  started-but-not-ready native-owner record (a truthful
  `native_ready` false) parses but never becomes ready
  (`owner-native-unready`), and the owner's registered
  artifact binary must equal the retained measured
  subject's executable identity (`owner-subject-binary-
  mismatch`) — same CID/run strings cannot substitute for
  exact executable agreement;
- the public prepare / observe / finalize workflow invokes
  the collectors itself before recording measured state — a
  constructor or manually prepopulated record is not
  workflow evidence; there is no CLI entry, so the runtime
  CLI cannot accept a fabricated collector result (injection
  is in-process, trusted fake tests only); malformed,
  mismatched, vanished, reused/incomparable or unreadable
  identities yield closed non-echoing refusals; no raw
  cmdline, environment, API/schema/body/TUI/history is
  retained or exported (the exact pinned argv only, where
  the contract requires it).  `finalize` binds the owner
  record's run id to the workflow's registered run, and a
  native-owner record must additionally equal the
  immutable workflow binding's order, literal source head
  and run, with the retained pre-teardown subject receipt
  bound to that same run — order/head/run mismatches are
  closed refusals (prep-owner-order-mismatch /
  prep-owner-head-mismatch / prep-owner-run-mismatch /
  prep-subject-run-mismatch); a historical S-scope record
  is not order/head-checked there and never becomes ready;

Native-owner evidence producer (closed schema
`slaif-native-owner-evidence-v1`): the explicit
measurement-to-record boundary for a LATER native-owner
run.  It invokes the owned finish/export/teardown
measurement seam (the closed read-only method set over the
completed owner's measured state — a None is unmeasured
and a closed refusal, never a default), validates the
FULL measured export payload with the ACTUAL shared export
validator (the same closed quiesce/snapshot/diagnostic/
originals law the R/S finish path applies to its host
revalidation — a recomputed digest alone proves framing
integrity, never payload validity), recomputes the export
digest from the measured payload bytes ITSELF (a supplied
digest is never trusted), and only then emits the closed
record from the closed teardown facts (present-before /
absent-after on the exact CID and image, zero
descendants, sentinel survival, native started — a run
that never started native is out of this producer's
scope).  The consumer validates the EXACT closed record
grammar — the exact top-level key set and the exact
nested object key sets; unknown, missing, or non-mapping
fields are closed non-echoing refusals before the record
is used, and no unknown field or value is echoed or
retained.  The measured image id admits only the bare
64-hex digest or the actual measured `sha256:<digest>`
form; the typed fact is the normalized bare digest.  A
measurement that exposes the closed six-key measured
context (order, source head, run, CID, image, binary)
must bind it EXACTLY to the expected immutable order/run
binding — an incomplete (None), extra-key, or
contradicting context is a closed non-echoing refusal,
never a silent skip to caller strings.  The produced
record must round-trip the closed consumer validation
before it is returned (producer/consumer agreement is
enforced, never assumed).  The real owned measurement
adapter (`OwnedOwnerMeasurement`) reads the completed
fixture owner's closed attribute seam (no platform
operation is re-invoked) and derives the run's native
started/ready facts ONLY from the public workflow's
measured pre-teardown subject receipt: a run with no
measured subject (the historical S scope) has no measured
native start, and a caller flag never mints one.  A
subject whose expected PTY was never bound (unobserved
expectation or measured tty0) — or whose measured binary
contradicts the owner's own registered artifact — is
honestly started-but-NOT-ready.  The historical S record
is never relabeled or derived into this scope.

Public local proof: `tests/test_cache_native_fixture_binding.
py` (45 tests) and `tests/test_cache_native_fixture_native_
prep.py` (124 tests) — valid active-order/source binding
(strictly read-only), foreign/malformed/duplicate/dirty/
mismatched binding refusals, stable attempts across
head/directory/phase changes, the preserved exhausted 017-s
record (historical schema, never rewritten) with shared-
schema/malformed/untrusted refusals, the closed git grammar
and bounded reads; registration collects before recording,
valid positive baselines plus wrong executable/argv/UID/
GID/groups/CID/run/start/TTY/foreground/restoration and
unknown/vanished negatives, no readiness from fabricated
flags, the native-owner producer (full shared-payload
validation, measured-context binding with forged/incomplete
negatives, the closed image-id forms, unmeasured/
contradicted teardown refusals), the owned adapter whose
native facts derive only from the public receipt (no-
receipt refusal, started-but-not-ready honesty, incomplete
measured-context refusals), the verdict's S-scope
`owner-scope-not-native` refusal, the finalize binding law
(order/head/run/source-head and subject-receipt run
mismatches refused) with the full public lifecycle
positives — including the REAL owner finish/export/
teardown code driven with fake platform operations over
ONE coupled fake process world (the workflow measures the
native subject while the same CID is alive, records the
stop, the exact CID removal updates the same world to
absent, and the same worker is restored before finalize) —
and cross-context refusal contrasts, the complete-group
tri-state law (complete observed group, running-member
refusal, verified-gone churn tolerated, unreadable
still-existing or capability-less inventory refused at
prepare/observe/stop without minting a baseline, stop or
restoration, and the membership cap unaffected by verified
churn), bounded enumeration/capture/diagnostics, and no
signals or Codex subprocess calls (static AST law).  The
real /proc mechanics are proven with tiny EXACT-OWNED
Python children only (each exact-owned child is killed
by the test's own cleanup if still alive; the absent-pid
closed negative uses the same real table); no test signals
the real worker/Bash group or any unrelated process.

Round 017-u repairs the complete-inventory law
demonstrated by the review-11 public group-readability
probe (3/4 at the T source): the T implementation skipped
every None stat as a raced-away non-member in BOTH the
initial group inventory and the complete-stop predicate, so
a stat-unreadable PID whose entry positively still existed
silently minted a complete stop receipt.  The repaired law
tri-states each listed row through the bounded read-only
absence seam (its historical `pid_present` contract: True =
verified absent, False = exists, None = unknown; missing
capability or unreadable presence evidence stays unknown,
never verified gone): only an independently verified-gone
entry may be ignored (bounded churn law); an unreadable
still-existing or unprovable entry is a closed non-echoing
refusal (`prep-group-incomplete` in the inventory,
`prep-stop-unobserved` in the stop predicate); a failed
initial prepare/observe mints no baseline or admission and a
refused stop can never later claim a recorded stop or
restoration.  The unchanged four-case probe passes 4/4 at
the repaired source; the original 13 preparation probes,
frozen 21 and installed 27 retain their earned scope.

The later execution contract is finalized from this code:
the serial foreground handoff still requires its own
separately activated order (human/strategic authorization,
RIGHT-pane manual foreground boundary), the exact pinned
attach argv (inert attach plan unchanged), the verified
local endpoint binding, that order's own one-attempt
admission namespace, and the measured verdict above.  D09
(genuine native formats/collector) remains `NOT RUN`; no v1
runtime claim.

### 11f. Round 017-v: public native-owner lifecycle
composition (fake integration only; no D-syntax change)

Round 017-v materializes the small EXPLICIT operator
composition that binds the accepted immutable order/run
binding to the REAL fixture owner and the public staged
native workflow as ONE coherent run
(`scripts/cache_native_fixture_native_owner.py`,
`NativeOwnerRun`).  It exercises that composition with
injected FAKE external operations only (fake
git/platform/process seams and owned synthetic
repositories): NO actual local Docker operation, NO
native launch (including help/version), NO worker stop,
NO TTY/job manipulation, NO real fixture admission in
the real checkout, NO host signal.  The real backend
code is imported and its real methods driven; the
platform operations are faked.  No CLI entry accepts a
fabricated collector result, and no v1 runtime claim is
made.

Constructor and admission (the composition's entry
law): `NativeOwnerRun` accepts ONLY a verified
immutable `OrderRunBinding` (any other binding type is
the closed `native-owner-binding-invalid`), and admits
EXACTLY ONCE in that order's stable one-attempt
namespace BEFORE any external mutation — the admission
itself re-validates the ACTUAL repository, committed
active/order content, literal head and repository
identity against the frozen binding, so a stale,
foreign or exhausted binding is a closed refusal before
the owner exists.  The REAL `LocalFixtureOwner`
constructor then selects the authority of the
binding's OWN order: the historical S default (no
binding) keeps the order-bound opt-in and the fresh
mint + stable 017-s admission UNCHANGED; a 017-s
binding keeps the historical S opt-in unchanged; a
NEW-order binding requires a LIVE bound admission in
that order's namespace before adoption (a bare caller
run id can never skip or bypass the order's one-attempt
law) and re-validates the real repository context
READ-ONLY through the ACTUAL resolver (committed and
disk active, unique committed order file and its bytes,
repository identity, head, clean worktree — nothing
written, no authority minted, the resolver's fresh run
id discarded, no active/S constant changes, no
runtime-global monkeypatch, no second owner).  The
owner adopts the binding's minted run identity — the
ONE shared identity with the public native workflow —
with no second mint and no second admission.  A
constructor failure AFTER winning the admission closes
THAT SAME run honestly (a terminal fail record in the
bound namespace, never an orphan running claim) and
propagates the primary closed refusal unchanged.

One shared run context: ONE owner, ONE RAM run
context, ONE absolute END anchor (the owner's OWN
published END anchor), ONE cumulative ledger and ONE
bounded cleanup grace are shared across construction,
prepare, held observation, finish/abort, evidence
publication and attempt finalization — no second
watchdog/owner/controller, no reset, no new budget, no
hidden retry, no host signal.  The bounded public
lifecycle is `start` (the owner's protected serve
loop; the published run id MUST equal the binding's;
an expired budget refuses BEFORE the launch) ->
`prepare` (the owner's REAL prepare path, then the
workflow's measured W/B birth/group/session/TTY
baseline — no predicted native PID) -> `observe`* (the
non-consuming held observation: the owner's closed
controller state plus the workflow's re-collected
read-only facts; idempotent) -> `record_stop` (the
SEPARATELY MEASURED worker-stop event, read-only) ->
`register_subject` (the PUBLIC staged registration of
the actual later native subject — see below) ->
`finish`/`abort` (the owner's REAL finish/export/
teardown or honest abort; the composition never
signals or kills the owner; the bounded join reaps the
serve loop within the REMAINDER of the ONE absolute
budget).

Staged subject registration (the prep module's public
entry, `register_subject`): the actual later native
subject is registered only AFTER prepare AND after the
separately measured stop (a pre-stop registration
cannot mint a receipt); the FROZEN first-prepare W/B
baseline must still be the same worker job (a
substituted worker/bash after the stop is a closed
refusal, never a silently adopted baseline); the
CURRENT bounded stable-stop predicate is re-measured
BEFORE any identity commit (the retained stop receipt
is the immutable HISTORICAL record, never replaced or
re-measured into; the re-measurement is predicate-only
and its receipt is discarded — a resumed worker, a
newly running group member, a changed foreground or a
newly unreadable positively-existing listed entry
under the tri-state law is a closed refusal outside
its stable stopped phase); the registered run identity
is immutable (a foreign expectation run is refused);
the expected PTY, binary, CID and run arrive from the
operator's OWNED attach registration and are
independently correlated with the measured subject by
the collector (copying the candidate's own unchecked
fields is not proof; a channel bound to another CID
refuses before any read); a refused registration
commits nothing (no baseline replacement, no receipt,
no stop); a conflicting second registration is a
closed refusal and the retained receipt stays the
first measured identity.

Distinct native-scope owner terminal record (local
module): a new-order bound run's converged owner
terminal state is published as the DISTINCT closed
record `slaif-native-owner-run-evidence-v1` / scope
`native-owner-run` — the SAME measured owner state,
cleanup and publication facts as the S record, but
WITHOUT the historical S whole-run false assertions
(`native_started` / `worker_stopped` / `codex_invoked`
/ `native_ready` — a native run that observed a native
subject must never assert them) and without the S-only
CI-image comparison (the measured native-owner record
carries the image identity).  The closed validator
(`validate_native_owner_run_evidence`, fixed token
`native-owner-run-evidence-invalid`) enforces the
exact key set per status, the OAP order id (any
order, not fixed to 017-s), the 32-hex run id and the
40-hex bound head, and validates the shared measured
substructures with the reviewed S validator over an
internal S-shaped envelope carrying the IDENTICAL
sub-values (a validation vehicle only — the retained
record itself never carries the S whole-run false
assertions).  The historical S rehearsal record keeps
its exact schema, scope and S meaning and is never
relabeled, derived or doubled.

Native-run terminal record (closed schema
`slaif-native-owner-run-v1`, scope
`native-owner-run`): the composition's own terminal
record for the run — the immutable binding record (in
the binding module's own closed grammar: OAP order
id, 40-hex source head, 32-hex run id, sha256
digests), the owner's closed terminal outcome
(pass/fail/aborted), the ALREADY-KNOWN journal state
(see below), the measured subject/stop booleans, the
measured native-owner record (produced through the
EXISTING producer/consumer ONLY where its measured
prerequisites hold — a pass-converged owner, the
retained pre-teardown subject receipt, the recorded
stop, and the owner's own registered CID/image/
binary context; an unmeasured component is a closed
honest refusal, never a caller-chosen string; the
producer is never fed fabricated starts) or its
closed refusal, and the closed verdict (ready boolean
+ reasons from the closed verdict vocabulary).  The
consumer (`parse_native_run_record`) validates the
exact top-level key set, the closed outcome/attempt
vocabularies as CLOSED STRINGS first (a non-string or
unhashable value is a typed refusal, never an untyped
error), the closed booleans, the binding grammar, and
— when present — a native_record that passes the
ACTUAL native-owner consumer validation AND is bound
to the OUTER binding (its measured order/head/run
identity must equal the outer binding's — a foreign
nested identity is a contradiction); a refusal
forbids a measured native record and any readiness; a
ready verdict requires EVERY measured prerequisite
(the owner's converged pass, the measured subject, the
recorded stop, the measured native record with its own
ready fact, no refusal).  Unknown, missing or
non-mapping fields are closed non-echoing refusals.
Retention is the reviewed protected 0600 atomic
no-overwrite seam (destination and every ancestor
validated as given; the commit is an atomic
no-overwrite LINK; the bytes are digest-verified
before the commit and the retained object
re-verified; a pre-existing destination or same-name
temporary file is crashed/foreign state — refused,
never unlinked or adopted; the composition's evidence
root must be outside the owner's disposable work
root).

Honest publication ordering (the owner's cleanup/
export outcome stays DISTINCT from the full handoff
qualification): the owner's convergence measures and
retains the DISTINCT owner-phase outcome read from the
SAME completed owner state (the same-order attempt
journal is the durable record, NOT a prerequisite for
deriving the outcome — no circular journal
dependency).  A terminal owner or publication error
(fail/aborted — including a publication failure after
a computed pass, which is never an admitted pass) is
finalized HONESTLY at convergence in the bound
order's namespace; a converged pass KEEPS the bound
attempt RUNNING.  `publish_native` then (1) reads the
owner's terminal outcome from the completed owner
state, (2) builds the record from that state and the
measured verdict, with the `attempt` field carrying
the ALREADY-KNOWN journal state — the pending
`running` state on the pass path (the terminal pass
finalization follows the successful protected
publication) and `terminal-preserved` for an
already-final terminal outcome — never a predicted
finalize token, (3) retains the protected native
record FIRST (a failed native publication closes the
still-pending bound attempt as a fail and the refusal
propagates — a failed publication never leaves an
admitted pass), and (4) ONLY THEN finalizes the
same-order journal (terminal pass on success;
terminal fail/aborted as an honest idempotent no-op).
The REAL returned finalize token is retained in
RAM/result (`finalize_attempt`, idempotent; it
refuses before a successful publication) and the
immutable retained evidence is never rewritten to
insert it.  The owner's historical S-scope record
keeps its S meaning; the verdict is composed AFTER
the owner's teardown and the independently measured
same-worker restoration (the operator restores the
same job before publication), with the subject's
post-teardown ABSENCE verified on the read-only
table.

Public local proof: `tests/test_cache_native_fixture_
native_owner.py` (12 tests) — the full public happy
path (start -> prepare -> observe -> the separately
measured stop -> the actual later subject launched
bound to the owner's OWN registered target CID ->
`register_subject` -> observe -> `finish` driving the
REAL owner finish/export/teardown with fake platform
operations over ONE coupled fake process world, the
exact CID removal updating the same world to absent
-> the same-worker restoration -> `publish_native`;
the retained native-scope owner evidence carries NO
historical S whole-run false assertions, the journal
admission runs running->pass, the retained record's
attempt field carries the pending `running` state,
the finalize token is `finalized`, the measured
native facts are bound to the order/head/run, the
verdict is ready, and the retained file is 0600) and
the closed negatives: a non-binding constructor
refusal (no work directory created), an exhausted
admission (a second verified binding is refused
before any external mutation, the retained record
unchanged, no executor action), a stale bound head
(refused before any work, evidence or executor
action), a pre-stop registration refusal, a
pre-prepare registration refusal, a double-
registration and resumed-worker refusal, a foreign
expectation run refusal, a preparation-only honest
not-ready publication (the attempt stays `running`,
the verdict is not ready, closed reasons), an
owner-failure honest fail (the native-scope fail
record, the journal `fail`, and the refused
not-prepared publication — no journal rewrite) and an
abort honest `aborted` (the attempt recorded
`terminal-preserved`, the owner evidence
`reason=cancelled`), plus the closed native-scope
validator (accepts the native fail record; refuses
the S schema, the S whole-run false-flag presence, a
bad OAP order grammar, a bad head, an unknown key, a
broken ledger law and an unknown reason).  The real
backend code stays unexecuted against any real
backend: the platform operations are faked; no
actual Docker operation, no native launch (including
help/version), no worker stop, no TTY/job
manipulation, no real fixture admission in the real
checkout, no host signal, and no CLI entry.  The
later serial native handoff remains a separately
authorized order; D09 remains `NOT RUN`; no v1
runtime claim.

### 11g. Round 017-w: owner-bound registration and
terminal publication coherence (fake integration only)

Round 017-w is the same-PR coherence repair of the
public native-owner composition demonstrated
independently after 017-v's publication; the 11f
success-path law stays in force and this section
records the tightened failure semantics.  As in 017-v
the composition is exercised with injected FAKE
external operations only (fake git/platform/process
seams and owned synthetic repositories): NO actual
local Docker operation, NO native launch (including
help/version), NO worker stop, NO TTY/job
manipulation, NO real fixture admission in the real
checkout, NO host signal; no v1 runtime claim.

(1) Owner-bound staged registration: BEFORE any
staged receipt commit, the operator's expectation is
bound to THIS SAME prepared owner's measured
registration — the owner's own registered CID and
artifact binary must already be measured, and the
expectation must equal them exactly (closed tokens
`native-owner-registration-unmeasured`,
`native-owner-subject-cid-mismatch`,
`native-owner-subject-binary-mismatch`).  A caller's
matching foreign expectation + foreign channel, or a
matching foreign expected + measured binary, cannot
redefine this owner's subject — the collector proves
agreement with the expectation, never with the
owner's registration.  A refused registration
commits nothing (no baseline, receipt or stop
change), and a later genuinely matching
registration within the same still-valid measured
phase remains possible; the workflow's own staged
gates (prepared, recorded stop, CURRENT stable-stop
predicate, frozen W/B baseline, immutable run,
collect-before-commit) are preserved unchanged.

(2) Frozen-context revalidation at actual owner
construction: the REAL owner constructor's
new-order authority branch now compares the ACTUAL
repository context READ-ONLY with the ORIGINAL
immutable binding through the complete
frozen-context revalidation seam (literal head,
clean worktree, disk AND committed active,
repository identity, the unique committed order
file and its bytes) — not a fresh resolution whose
result is discarded.  A repository-identity drift
AFTER the won admission but BEFORE owner adoption is
a closed refusal before any owner adoption, and the
already-won attempt is closed honestly as a terminal
`fail` with no external action (the composition's
existing post-admission closure); a contradictory
`bind_head` argument to a bound construction is a
closed refusal before adoption.  The S default and
the historical S opt-in are unchanged.

(3) The ONE-SHOT terminal publication transition:
once native publication for the COMPLETED owner
begins (at the read of its terminal outcome), the
attempt is marked publication-attempted and every
failure is terminal for this qualified attempt — no
fresh-path retry, no relabel, no journal reset.
The ACTUAL bound journal state for this run is read,
never assumed from the outcome: the pass path
requires the bound attempt still RUNNING (an early,
already-terminal or unreadable journal cannot admit
pass); a terminal owner outcome requires that SAME
terminal outcome already recorded (carried as
`terminal-preserved`) or a still-running attempt
finalized honestly NOW with the real verified
token.  A PRE-RETENTION failure (verdict
measurement, record validation, serialization, a
destination or writer refusal) closes the
still-pending attempt truthfully — an unpublished
pass is closed as a `fail`, the primary closed
refusal propagates unchanged, and an unexpected
serialization error surfaces as the module's own
`internal` token.  The protected native record is
retained FIRST; ONLY THEN the same-order journal is
finalized, and the terminal pass admits ONLY the
real returned `finalized` token: a POST-RETENTION
unverified (record-unreadable) or raced (contradictory
terminal) finalization is a CLOSED failure that
preserves the immutable retained bytes AND the
actual journal facts as-is (the journal is never
overwritten, re-closed or relabeled by this path)
and never returns a normal qualified success.  The
real finalize token stays in RAM/result
(`finalize_attempt`), never rewritten into the
immutable evidence.

Public local proof: the composition suite grows to
19 tests (the 017-v twelve retain their assertions,
except the pre-prepare registration expectation,
which now observes the owner-bound
`native-owner-registration-unmeasured` token — a
stronger refusal with the same commit-nothing
semantics).  The seven new tests: the foreign-
owner-context registration refusals (foreign CID,
foreign binary) with the later genuinely matching
registration recovered in the same still-valid
phase; the origin drift before actual owner
construction (refused with `bind-repo-identity-
mismatch`, the already-won attempt closed terminal
`fail`, no external action, no work directory); the
failed publication (untrusted destination) with the
journal closed `fail` and the FRESH-PATH retry
refused without a new record; the unverified
post-retention finalization (record-unreadable)
preserving the retained bytes and the still-
`running` journal fact; the raced post-retention
finalization preserving the raced `fail` journal
fact; and the completed-run measurement and
serialization failures (closed truthfully, the
primary token / `internal` propagating, the attempt
closed `fail`, the retry refused).  The later
serial native handoff remains a separately
authorized order; D09 remains `NOT RUN`; no v1
runtime claim.

### 11h. Round 017-x: one bounded Python-only actual
fixture capability measurement

Round 017-x executes the ONE bounded outcome the earlier native-
preparation rounds left to a separately authorized order: with a REAL
finite Python-only fixture, determine whether the existing unprivileged
host CID channel can measure the CURRENT executable of an actual UID/GID
21002 process WHILE IT IS ALIVE. The driver is repo-owned stdlib-only
(`scripts/cache_native_fixture_exec_capability.py`; closed result record
`slaif-017x-exec-capability-driver-v1`) and drives the REAL fixture
owner's protected interface prepare -> hold -> finish over the SAME run,
ledger, attempt and END (no direct-call simulation). The measurement is
bounded and fail-closed, and its conclusion is HONEST: a measured
unknown or a refusal is a USEFUL diagnostic result — never a native-
ready, worker-stop or whole-017 success claim; D09 remains NOT RUN; no
v1 runtime claim.

(1) One sealed admission, owned by the child: the driver SEALED-launches
the one bound owner (exact closed argv; the owner IS the supervisor — no
second watchdog, no caller launch argv). The SEALED CHILD owns
resolve+admit ONCE before any external work: the module-minted run
identity is admitted in the child's process, and the driver only
verifies the child's closed protected outputs (the published owner state
and the stable admission record) — it never re-resolves, re-mints,
adopts or replaces any run id, and a post-admission constructor failure
closes the SAME won attempt honestly. An exhausted running journal is
refused, never adopted or reconstructed.

(2) Startup authority (fresh protected bootstrap): the control root is
created fresh by this launch's owner at serve start. A pre-existing root
is a prior/foreign owner's terminal/control surface and is never adopted
— no child is launched, no command is issued, no journal is mutated. The
published owner state is bound to the ACTUAL still-live sealed child of
THIS launch: the state's PID must equal the still-live child PID, and a
prior state — even with a matching run id and head — is refused before
any command.

(3) One closed detached hold, one start: the capability start is the
owner's ONE closed detached stand-in hold exec — subject UID/GID 21002
on the held prepared exact CID, the exact immutable stand-in path and
mode, the issued 32-hex run-id marker on argv, bounded by the stand-in's
own finite hold. This is the ONE subject start in the order, INCLUDING
failed starts (a failed start consumes the one start and is a closed
outcome, not a second opportunity); it is a fixture stand-in, never a
Codex instance, and no native or PTY readiness is inferred from it.

(4) Bounded exact-CID discovery: the AUTHORITATIVE member list comes
from the owner's OWN guarded `top` command (every query charges the SAME
ledger/deadline; at most the fixture pids limit of 96 rows; overflow,
ambiguity or degradation are closed refusals). The host /proc is NEVER
enumerated for membership: the host view is consulted per attested PID
only, and every attested member is verified IN-SCOPE through the
registered-CID channel before it may be a row. Churn counts as absent
only when the channel INDEPENDENTLY verifies the PID gone; an existing-
but-unreadable or raced member is a closed refusal, never a silent skip;
a host PID outside the attested list is never a candidate. The subject
is then the issued-marker kernel-cmdline correlation against the exact
closed hold form, FRESH against the pre-launch inventory (a previous
attachment is never adopted; ambiguous, duplicate or identity-mismatched
candidates are refused).

(5) Scoped current-executable read: the channel's read is at most 16 MiB
and at most 10 s, further clamped at MEASUREMENT time against the SAME
remaining owner END (cleanup grace is convergence, never fresh
measurement) intersected with the issued hold's own finite lifetime, and
birth-bound. PID/birth/CID/UID/GID frame checks run BEFORE AND AFTER;
the observed identity capability and the executable capability are
DISTINCT closed fields — one readable field does not prove the other. An
unreadable or absent executable is a closed `unknown`, never an
artifact-hash fallback and never a readiness claim. The order prose
`HostCidScopedTable` names the existing `RealCidScopedTable` channel;
the implementation, channel and seam are unchanged (a naming
clarification only).

(6) Honest termination and exact-owned removal: the subject exits 0 on
its own finite hold, and the driver polls the channel's tri-state
verified-absence primitive on a bounded window (no signal, no kill, no
watchdog; the owner's exact-CID cleanup is the removal path on every
outcome). `verified-gone` proves ABSENCE only — never an exit code or a
termination cause; `still-present` and `unknown` stay distinct, and a
presence is never relabeled as a termination.

(7) Owner-converged failure, one END+grace budget: any capability-phase
failure before the finish converges through the owner's OWN bounded
abort terminal command over the protected interface (never a host
signal; the terminal command is issued first, the owner settles and its
output is reaped within the same budget, and the actual issuance is
tracked, never derived). The owner's retained terminal evidence is then
validated with the reviewed closed validator BOUND to this exact attempt
(order, head, run and prepared CID — a valid foreign record is not this
run's evidence). The driver's whole command/wait/measurement budget is
the owner's published END anchor plus the owner's one allowed cleanup
grace — the approved ONE END+grace anchor: an expired budget refuses
before any blocking wait, and the already-exited distinction never
authorizes a pass over missing or unverified evidence.

(8) W-order publication of the closed result: on a verified owner PASS
the driver retains the validated protected owner evidence FIRST, then
retains its own protected capability record (the reviewed protected-
path/atomic-no-overwrite retention; `--record-out` is REQUIRED by the
CLI preflight — so the ONE qualification attempt is never
admitted without its retention destination — and a
destination at or under the disposable work root is a
closed READ-ONLY refusal before any launch (the
retained record must outlive the scratch root), and
only then performs the verified
same-attempt terminal finalization (the real `finalized` token is
required; an unverified token never returns a qualified success). A
refusal closes the returned record as `fail` with NO journal pass and NO
fresh-path retry. A driver `pass` is a closed truthful conclusion: an
unknown or a refusal is a useful diagnostic, never readiness.

Public local proof: `tests/test_cache_native_fixture_exec_capability.py`
(34 tests) covers three DISTINCT layers, not conflated: (1) the REAL CLI
admission tests (the closed `main()` grammar — the one subcommand, the
bound order, `--record-out` REQUIRED by the preflight; invalid forms
refused before any launch) plus the child-owned resolve+admit law (the
sealed child admits ONCE; a post-admission constructor failure closes
the same won attempt; an exhausted running journal is refused, never
adopted or reconstructed); (2) the scripted driver bootstrap tests (the
real driver launches an ACTUAL exact-owned Python child — the fake owner
side bootstraps the fresh protected control root and publishes the
closed state with the child's own pid, so the driver's startup
verification and owner wait observe a live owner exactly as the real
composition does: the pre-existing-control-root refusal before any
launch, the foreign-prior-owner state refusal (no command, no journal
mutation), the scripted full positive measuring the subject WHILE ALIVE,
and the full-driver refusals — the failed sealed startup with the
child's closed reason adopted, the failed hold, the capture cap, the
read error (the live reader state read after drain, the primary
preserved), the expired budget before any blocking wait, the
ambiguous/duplicate/identity-mismatch candidates, and the
foreign/S-scope evidence never adopted); and (3) the in-process real
public-owner tests (the REAL `LocalFixtureOwner` public interface and
the driver terminal are driven in-process with fake platform operations:
the coupled positive measures the scoped read BEFORE the owner finish,
the abort convergence, the retention and finalize orderings — the bound
verified evidence first, refusals closed `fail` without journal pass,
the post-retention unverified/raced finalization preserved — plus the
cleanup-failure and unrelated-survival refusals and the record-out-
inside-work read-only preflight refusal). Across these layers the shared
closed law is proven: the guarded `top` inventory grammar (default and
real header forms, exactly one verified PID column, the 96-row bound,
duplicate/malformed/overbound refusals), the issued-marker correlation
controls (FRESH vs pre-launch; ambiguous, duplicate and identity-
mismatch refused), the scoped-read law (a readable coherent identity
with an absent executable is `unknown`, never an artifact-hash fallback;
a reused PID/birth mismatch refused before any exe read; a frame race
and a vanished subject refused), and the tri-state discovery absent-
versus-foreign-scope contrast. These compositions are USEFUL FAKE PROOF
of the named mechanisms — the actual Docker operations and the fixture
image are faked in every test; they are not one full sealed-real-owner
end-to-end test. Pure/fake platform seams plus tiny exact-owned Python
children (each exact-owned child is cleaned up by the test's own bounded
cleanup if still alive; no signal to any real worker, Bash group or
unrelated process; no container of any kind). The actual outcome of the
ONE authorized attempt RAN EXACTLY ONCE at literal implementation
head `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (run
`9fd5cf1d95924a47b8bf53e8624242a5`): a terminal FAIL at prepare-target with `controller-not-ready`, `capability` null — no complete preparation, hold, subject identity or executable result (neither a readable nor an unreadable executable was established); the admission is terminal fail and is never reset, retried or relabeled; the
measured outcome is recorded in the immutable round report. Round
017-y adds the closed readiness diagnosis and the second explicit
sealed entry (order 017-y, record `slaif-017y-exec-capability-driver-v1`
paired ONLY with order 017-y; the historical S/X entries unchanged):
on a nonzero bounded readiness exec, ONLY the fixed probe's own exact
finite closed failure record refines the original `controller-not-ready`
category (`controller-not-ready:<cause>`; the fixed measured causes
`uid-not-21001`, `pid1-uid`, `health-unreachable`; a missing,
malformed, multiple/duplicate, foreign, over-bound or contradictory
output is the fixed unknown; a raw exception or Docker failure is
never a measured cause; no raw output is ever persisted); the
readiness failure path records NO readiness-poll count (an unmeasured
quantity, never a claim of zero actual readiness polls — see the
ledger quantity law above); and the ONE conditional bounded lifecycle
query (only when the readiness exec produced no closed record: exactly
one allowlisted read-only `docker inspect` of the single finite fact
`.State.Status` on the SAME registered CID, charged to the SAME owner
ledger/END — only the closed line `exited` refines to
`controller-not-ready:container-exited`, and any other status, any
other output shape and EVERY query failure (including a bounded
timeout and a transport failure) stay honestly unknown — a query
failure is NOT absence); a retained capability record is valid ONLY
under its canonical sealed entry (caller-created descriptors and
cross-entry pairs are closed refusals), and the terminal
retention/qualification propagates the entry through both the pass
and fail paths, the matching record retained FIRST and only then the
pass finalization. Ten focused tests were added across the three
fixture suites (ci 224, local 50, exec_capability 38).
The actual outcome of the ONE separately bound 017-y attempt
RAN EXACTLY ONCE at literal implementation head
`35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (run
`fbe526a3290d465298bc8da61ef2a304`): a closed driver PASS with
the complete preparation, confinement and Python-PTY phases;
the subject uniquely identified and measured from the exact-CID
inventory (UID/GID/groups 21002, birth-bound), then observed
`verified-gone` after the bounded hold (absence only — never an
exit code or termination cause), while the current executable
remained the closed UNKNOWN (no digest; not native readiness and
no proven kernel/errno cause); the admission is terminal pass
and is never reset, retried or relabeled; the measured outcome
is recorded in the immutable round report; no native launch, no
worker stop, no host signal; D09 remains NOT RUN; no v1 runtime
claim.

### 11i. Round 017-z: inert versioned fixture identity contract

(software-only; no runtime switch, no new admission, no
Docker/native work)

017-z makes the fixture identity contract explicit BEFORE any
alternative runtime integration: a later owner-UID profile might
permit the existing unprivileged host read without another
measurement process; that is unproven and needs actual same-UID
containment/current-exe qualification under a later exact order.

- Two explicitly named immutable identity descriptions (names
  distinct from adapter cache profiles):
  `slaif-fixture-identity-original-v1` — controller 21001/21001,
  subject 21002/21002, expected groups (21002,). It REMAINS the
  current fixture identity; every old record/schema/constant
  meaning is unchanged and the old 21002 record law — including
  its empty-group allowance — is never reinterpreted by the new
  record. And the INERT `slaif-fixture-identity-owner-uid-v1`
  candidate — subject UID/GID equal to the captured eligible
  host owner's real/effective/saved values, each triple's three
  values equal, nonroot, strict finite integers, distinct from
  the controller identity; Linux IDs bound 1..4294967294
  inclusive (0, -1 and 4294967295 never admitted); expected
  subject groups exactly (primary GID,), never copied from host
  supplementary groups. Construction enforces the complete
  field laws: no description with a mutable alias, an
  oversized group vector (refused before any copy) or an
  invalid field can exist; no caller-selected UID/argv, root
  fallback, environment override or silent default; equivalent
  numeric IDs under different profile versions remain different
  configurations.
- Closed strict record `slaif-fixture-identity-record-v1` with
  a bounded mapping codec (at most 4096 bytes, exactly one
  mapping, no duplicate keys; malformed/duplicate/over-bound/
  missing/extra/contradictory input refused with fixed
  non-echoing reasons) and a deterministic canonical
  configuration fingerprint that binds complete profile
  semantics and changes on any real identity/configuration
  change. The fingerprint is a configuration digest — never a
  process hash, trusted identity receipt, admission, cache key
  or readiness certificate.
- Bounded READ-ONLY host-owner-ID collector: direct stdlib
  getresuid/getresgid plus the simple uid/euid/gid/egid getters
  (cross-checked, never used to infer a missing value), ONE
  collection, explicit unsupported/unavailable outcome when the
  complete real/effective/saved IDs are not obtainable; no
  filesystem/proc traversal, environment/config/profile read,
  network/GitHub/Docker/subprocess, signal, UID/GID/group/
  privilege/prctl/kernel mutation or credential handling. Raw
  collection / data validation / derivation stay separate
  behind a narrow fake OS-read seam; tests never bypass the
  production validator or constructor.
- INERT law: typed objects, decoded JSON/data, a profile name,
  a fingerprint or caller flags NEVER establish measured
  authority. A valid closed data record may decode into an
  immutable description — a pure data transformation, not
  measurement authority; serialization validity does not prove
  the IDs came from an OS observation. The contract selects no
  live profile, records no fixture admission and yields no
  ready/native verdict.
- Required LATER integration boundary (described, NOT
  implemented): a later sealed child selects a canonical
  profile, collects/freezes the actual owner IDs, binds them to
  its ORIGINAL verified order/head/run and live admission
  BEFORE external work, and revalidates the same context at
  actual use. No path is opened through the existing local
  CLI/defaults/validators by this increment.
- A later profile must preserve: private PID/mount/IPC/UTS/
  network namespaces; no host mounts or devices;
  rootfs-readonly; cap-drop-ALL / no-new-privileges / seccomp;
  exact bounded storage/memory/swap/pids/CPU; controller-
  private paths; and EMPIRICAL keyring denial under the
  matching host UID. Matching UID is NOT proof of safe
  containment. The later native artifact (308139304 bytes)
  also needs a later justified native-size byte/time
  measurement bound, not blind reuse of the X/Y Python
  16 MiB/10 s bound. No implementation or experiment of those
  later mechanisms in this increment.
- Packaging: the helper is repository-only under the existing
  policy (pyproject top-level `scripts` exclusion and the
  artifact policy's forbidden `scripts/` prefix in BOTH
  artifacts); it enters neither wheel nor sdist; its bytes are
  bound by the committed source A identity and the clean
  git-archive check, separate from the artifact input map. The
  new test file refreshes the development provenance input map
  normally (197 to 198 inputs); the wheel stays byte-identical;
  no published RC record is rewritten.
- Verification: 19 focused tests (48 collected cases) plus the
  relevant original fixture suites unchanged; the complete
  frozen development gate at the literal committed head; D09
  remains NOT RUN; no v1 runtime delivery.

### 11j. Round 017-aa: owner-UID fixture integration
(software-only; the integrated path is INACTIVE and unqualified)

017-aa threads the inert 017-z owner-UID identity contract
through the REAL existing fixture owner, its prepared
image/exec/measurement/control/evidence path and the Python
capability driver. No real local Docker/fixture/owner startup,
admission, native/extra Codex, worker stop, signal, TTY handoff
or model/Gateway call occurs in this round; the standard
existing CI jobs remain under their ORIGINAL default scope.

- ONE canonical future sealed entry, fixed now but INACTIVE:
  `017-ab` (exact unique future order path
  `oap/orders/017-ab-owner-uid-python-capability-qualification.md`,
  driver record `slaif-017ab-owner-uid-exec-capability-v1`,
  selecting ONLY `slaif-fixture-identity-owner-uid-v1`). It is
  not an activated AB order: AA never creates its real order,
  never changes `oap/active` to it, never admits it and never
  launches its owner. Actual repository-context validation
  refuses the entry under AA-active state BEFORE any external
  fixture work or admission, proven over hermetic synthetic
  repositories and active/orders/admissions — never the real
  checkout.
- The SEALED child retains sole resolve+admit ownership. AFTER
  its ORIGINAL verified order/run wins admission, the REAL
  owner collects the host owner IDs through the ONE raw read
  seam (production: direct bounded OS reads; tests: the
  faithful narrow fake seam) and derives its description with
  the Z production collector/derivation: each
  real/effective/saved UID and GID triple equal, nonroot,
  strict finite Linux IDs 1..4294967294, distinct from
  controller 21001. A post-admission collection/constructor
  failure closes the SAME already-won attempt honestly before
  any external fixture work; an exhausted or foreign journal is
  never reconstructed or adopted, no run is re-minted and no
  binding is resolved and discarded. No process may be
  started merely to collect host IDs, and a caller-supplied
  description, fingerprint or ready flag is NEVER accepted —
  only this own collection/derivation feeds the context.
- ONE immutable owner context: the canonical profile
  description's fingerprint, the frozen INDEPENDENT subject
  identity (UID and GID are separate — the useful fake positive
  is 1001/1002), the closed runtime profile view and the
  ORIGINAL verified order/head/run/admission binding. It is
  revalidated at actual use through a bounded current-ID
  coherence read that may COMPARE but never rebase or silently
  re-freeze after drift; a drifted or unreadable context is a
  closed refusal.
- Image/subject execution: the explicit owner-profile
  Dockerfile variant uses ONLY the frozen validated IDs, the
  same pinned base and the immutable native
  artifact/LICENSE/NOTICE, with the same confinement; the
  original Dockerfile defaults remain fixed-21002. The
  small root-owned immutable fixed-path profile DATA file
  baked into the image is not host authority: missing,
  unknown, mismatched or unsafe profile data under the new
  path fails closed and never falls back to original, and new
  semantics are never selected merely because an env var or an
  arbitrary file is present. Public copied fixture modules and
  the profile DATA are explicitly readable by
  controller/subject and immutable inside the image, even
  when the protected host build context is 077/0600. The
  owner-scoped guarded executor admits only the canonical
  profile's exact UID:GID and fixed Python commands/flags/CID;
  the original guard defaults are unchanged.
- Expected effective groups remain exactly the primary GID: an
  empty supplementary array or own primary GID alone adds no
  privilege; foreign/duplicate/root/boolean/float/string
  groups are refused, and no supplementary membership is
  invented from the primary GID.
- DISTINCT versioned records: identity-bearing owner state
  `slaif-017ab-owner-state-v1` (the old 12-key v1 state form
  is byte-for-byte unchanged and rejects identity-bearing
  records); owner-run evidence
  `slaif-017ab-owner-run-evidence-v1` (scope
  `slaif-017ab-owner-uid-scope`; the SAME measured owner
  state/cleanup/publication facts plus the frozen identity
  substructure — re-derived through the production codec and
  re-hashed, so retained identity is closed data integrity,
  never a measured-authority claim — and the
  exact-CID-membership teardown marker); the AB driver
  record; and the subject measurement/synthetic-profile
  records take the DISTINCT new tags
  `slaif-fixture-exec-measurement-v2` and
  `slaif-fixture-profile-v2` (each tag refuses its v1
  counterpart and vice versa): the SAME closed facts and
  error law measured under the frozen owner-profile subject
  through the shared profile-independent structural core,
  which is reused ONLY with its unchanged closed meaning
  (only the expected subject identity differs), while the
  strict original identity-v1 wrappers keep the fixed-21002
  subject law and refuse the v2 tag and every other
  subject.  The ORIGINAL identity-bearing v1
  tags/consumers stay strictly fixed-21002: a new profile
  record with the same numeric 21002 tuple stays isolated,
  and measured 1001-class facts are validated as-is, NEVER
  normalized to 21002; the generic profile-independent
  standin/control transport v1 is retained ONLY where its
  existing closed meaning is unchanged (no wire-tag
  renaming).
- CRITICAL cleanup law: the owner-UID descendant and cleanup
  proof is EXACT registered-CID plus owned PID/birth lifetime
  membership with tri-stated post-removal verification. The
  original global controller/subject UID teardown scans are
  NEVER substituted with the host owner's UID (that would
  include the worker/owner/unrelated host processes): no
  UID-only membership or zero-global-UID claim. Unknown or
  unreadable still-existing entries stay unverified, never
  silently ignored.
- A post-admission startup refusal (control-root creation or
  the bounded socket bind) routes through the SAME single
  owner convergence as every terminal path: the already-won
  attempt closes terminal honestly (no retry, no remint), the
  owned partial control root is disposed through the same
  exact-ownership law, a pre-existing foreign control root is
  never adopted or deleted, and the thin CLI keeps the same
  closed startup record and exit code.
- Budget/END isolation: one absolute END, one cumulative
  ledger, one cleanup grace across the whole owner lifecycle;
  the capability read keeps the X/Y law (16 MiB/10 s clamped
  at measurement to the SAME remaining owner END intersected
  with the issued hold's finite lifetime; unknown executable
  remains unknown with no digest — never an artifact-hash
  fallback).
- Original preservation: the S/X/Y entries, sealed pairs,
  defaults, record meanings, consumed namespaces and actual
  records are unchanged; the original fixed-21002 path
  remains the current qualified fixture default.
- Verification scope: fake platform operations in three
  distinct honest layers — the coupled public-owner terminal
  layer runs over ONE coherent coupled process/resource
  world, while the scripted driver bootstrap and the
  in-process sealed-CLI own-collection are their own distinct
  layers — useful fake proof, NOT one sealed-real-owner
  end-to-end qualification; the `017-ab` entry is INACTIVE,
  so no actual AB fixture operation may ever run in this
  round. The new helper
  `scripts/cache_native_fixture_runtime_profile.py` and the
  owner Dockerfile are repository-only under the existing
  artifact policy (excluded from BOTH the wheel and the sdist
  source-input maps; their bytes are bound separately by the
  committed Git/source-A identity and the clean-archive
  helper-byte check); the development provenance input map
  gains the new TEST input
  `tests/test_cache_native_fixture_owner_uid.py` only (its
  measured count is reported at the gate). D09 remains NOT
  RUN; no native-ready, actual containment/current-exe or v1
  runtime claim.

### 11k. Round 017-ab: owner-UID Python capability
qualification (ONE bounded actual PYTHON-only run)

Round 017-ab activates the canonical sealed entry fixed by
017-aa (`017-ab`, driver record
`slaif-017ab-owner-uid-exec-capability-v1`, selecting ONLY
`slaif-fixture-identity-owner-uid-v1`) and executes the ONE
bounded actual PYTHON-only fixture capability
qualification on the same PR25 with no source change: at
the literal attempt head
`cdb6a101ecbd6d687f8ad413b9505c7198000758` (run
`87ee9c006d7f4de98d11af2dfbe5bd5c`) the existing public
driver ran EXACTLY ONCE, Python-only, over the real local
Docker endpoint, with all 17 helper bytes, the runtime
source, the 199-input map and both artifacts verified
identical to qualified AA, the focused owner/capability
suites 92/92 under frozen Python 3.12/umask 022, and all
10 CI checks green at that head.

- Admission and identity: the sealed child won the ONE
  admission; the real owner collected and froze its OWN
  eligible host identity through the 017-z production
  collector (subject UID 1001, GID 1001, expected groups
  exactly the primary GID `[1001]` — measured
  real/effective/saved values, never a caller flag;
  fingerprint
  `7e5a6432d91bc873c3c3208e384efd48fac7f1bff3e8fe6b93240343cc5387b0`,
  profile DATA sha256
  `9e0db129cf5c9ce073ae5db03f670d383de0613021cbaa7d3def47699e0a3e2b`).
- Preparation and confinement: the owner-profile image
  (`sha256:dbb93559d3efcbd1575e15cafb43eebc219f6c4129b55f419d7a262dee4abc59`,
  pinned base plus the owner-variant Dockerfile with the
  frozen validated IDs, the root-owned immutable 0444
  profile DATA and the 0555 native PATH entry) was built
  once; the pinned native artifact (308139304 B, sha256
  `b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306`)
  was fetched, hashed and baked, and was NEVER executed
  (not even a version query). The preparation,
  confinement and Python-PTY phases completed with the
  measured confinement unchanged (controller 21001:21001;
  subject 1001:1001; 1 GiB memory/no swap; 1 CPU; pids
  96; four writable mounts including /dev/shm 64 MiB;
  empirical keyring syscall denial — EPERM, errno 1 —
  under the matching host UID; a matching UID is never
  containment proof, and the measured denial is the
  empirical fact).
- The ONE capability-hold subject start: uniquely
  identified from the exact-CID inventory (pid 2781142,
  birth 174880545, UID/GID 1001/1001, groups `[1001]`,
  closed argv; pre/post inventory 1/2 rows, ≤96; process
  identity measured). The current executable was MEASURED
  through the existing unprivileged scoped CID channel:
  sha256
  `4dbf3143240288fb2170257ffaa7bd030cdda5d2703d1f5f30b627042267e2e3`
  — the first measured executable for this entry class
  (distinct from the X null and the Y unknown).
- Termination and cleanup: the subject was then observed
  `verified-gone` after the bounded hold — ABSENCE only,
  never an exit code, signal, errno, kernel cause or
  natural-exit provenance. The exact-CID cleanup
  converged (descendants 1 before / 0 after; the exact-
  CID-membership proof, never a host UID scan; container
  removal and owned-image removal verified absent; the
  unrelated same-UID worker and host sentinel survived).
  Bounded ledger charges: 36 docker admissions, 2
  admitted requests, 1 healthz attempt, 24710 drained
  bytes.
- Publication ordering: the verified owner evidence
  (`slaif-017ab-owner-run-evidence-v1`, scope
  `slaif-017ab-owner-uid-scope`, status pass, sha256
  `fa51cfafe56f7694ee4ed983fbffc7f42310f2a525e7f3a1b1d1f7eae521fc8f`)
  was retained FIRST, the driver record
  (`slaif-017ab-owner-uid-exec-capability-v1`) SECOND, and
  the SAME still-live admitted-attempt pass finalization
  LAST (ONE terminal-pass journal entry; finalize
  `finalized`; owner exit 0; driver exit 0;
  `terminal_command` none; reason null).
- Scope: a bounded Python-only diagnostic capability
  qualification on the owner-UID profile — NOT
  native-ready, NOT whole-017 acceptance, NOT v1 runtime
  delivery. Full-017 native/current-binary/right-pane
  format/PTY, D09, the required-syntax audit and ALL
  018-024 remain mandatory. The admission is terminal
  pass and is never reset, retried or relabeled; the
  measured outcome is recorded in the immutable round
  report. D09 remains NOT RUN; no v1 runtime claim.

### 11l. Round 017-ac: owner-UID native handoff
integration (software-only)

Round 017-ac integrates the existing owner-UID fixture
composition with the native handoff path on the same
PR25 (amend; software-only — no actual local
Docker/fixture/owner startup or admission, no native
launch (including help/version), no worker stop, no real
host signal, no model/Gateway call, no new runner,
supervisor, watchdog, transport, privilege channel or
framework; no adapter/runtime/parser/cache/compiler/
image/Gateway/model/dependency/lock/workflow behavior
change).

- The ONE canonical future sealed entry `017-ad` is
  fixed now but INERT, input-gated and UNQUALIFIED: its
  entry constant names the unique order path
  `oap/orders/017-ad-owner-uid-native-handoff-qualification.md`
  required for the LATER strategic activation — not an
  already-committed or activated AD order, no run
  authority, and the real AD order file is ABSENT from
  this checkout (the prior unauthorized stray file was
  removed; the incident is disclosed in the round
  report); actual repository-context validation
  refuses the entry under AC-active BEFORE any
  external work or admission, proven only in hermetic
  synthetic repositories (never in the real checkout);
  no arbitrary order/profile switch; the original
  S/X/Y/AB entries, sealed pairs, defaults and
  consumed namespaces are unchanged.
- Identity: the SAME real owner's OWN bounded OS
  identity collection — frozen in the owner's immutable
  context AFTER its ORIGINAL won admission, BEFORE
  external work (real/effective/saved UID and GID
  triples each equal, nonroot, 1..4294967294, distinct
  from the controller 21001; expected effective groups
  exactly the primary GID, never host supplementary
  groups) — is carried through the EXISTING public
  NativeOwnerRun / preparation / measurement / evidence
  composition, and the SAME frozen context is revalidated
  by comparison at EVERY identity-bound use —
  construction, prepare, hold start, finish AND the
  public staged registration — never rebased or
  re-frozen; a caller description/fingerprint/ready
  flag, serialized receipt, matching numbers, foreign
  owner or fresh resolution never proves origin; an AD
  owner without a frozen context is a closed refusal,
  never a silent original-profile fallback.
- The FROZEN owner context is revalidated at the public
  staged registration (the bounded current-ID coherence
  read through the SAME seam, compared to the frozen
  fingerprint): a host identity that drifted after the
  measured stop is refused at registration BEFORE any
  channel construction or receipt commit — nothing is
  committed (no baseline, receipt or stop change), the
  frozen context is never rebased, and the same won
  attempt converges honestly (the original profile keeps
  its context None and is a no-op, unchanged).
- DISTINCT versioned identity-bearing tags wherever the
  original or AB-only tags cannot honestly represent AD
  (the original fixed-21002 and the AB consumers stay
  strict, including equal-numeric cross-profile
  separation; shared profile-independent cores keep
  their unchanged closed meaning): the AD state form
  `slaif-017ad-owner-state-v1`, the AD preparation
  snapshot `slaif-017ad-native-handoff-prep-v1`, the AD
  owner-run evidence
  `slaif-017ad-native-owner-run-evidence-v1`, the AD
  native-owner evidence
  `slaif-017ad-native-owner-evidence-v1` (the frozen
  owner-identity substructure cross-bound to the outer
  record) and the AD native-run terminal record
  `slaif-017ad-native-owner-run-v1`; data
  validation/integrity stays distinct from measured
  authority.
- The canonical AD entry resolves ONLY at the unique
  order path named by the entry constant: a
  directly-constructed AD binding at a foreign path is
  refused BEFORE the admission or the owner adoption
  (the generic original orders keep their exact
  historical law).
- Subject registration binds THIS prepared owner's
  ACTUAL registered CID and artifact, the actual fresh
  PID/birth/UID/GID/groups, the exact argv
  `codex --yolo --profile early-beta` and a nonzero
  actually matched expected PTY: foreign
  expected/channel/artifact, stale stop, ambiguous/
  reused subject, unbound tty0 or unknown still-existing
  inventory member refuses without committing a receipt;
  a refused registration commits nothing and a later
  genuinely matching registration within the same
  still-valid phase remains possible.
- The retained-record consumers stay coherent with the
  ORIGINAL frozen workflow context: the bound workflow's
  finalize composes a ready verdict ONLY for the
  DISTINCT identity-bearing AD tag carrying the SAME
  frozen owner-identity substructure as the workflow's
  frozen subject law (a valid FOREIGN frozen identity
  can never become ready, never adopted); the EXACT
  tag-pair law keeps the original tag for the historical
  entries ONLY — an original-tag record of the AD order
  is a closed refusal at the record grammar (the AD tag
  stays the 017-ad form), while the historical orders of
  the original tag parse unchanged.
- Native executable measurement: ACTUAL current bytes
  through the EXISTING unprivileged registered-CID
  channel, coherent before/after lifetime/identity/CID/
  current-exe frames, bounded streaming (not full-file
  buffering) at exactly 320 MiB (335544320 bytes) and
  10 s per measurement, further clamped AT USE to the
  SAME remaining owner END (the cleanup grace is
  convergence, never fresh measurement); overbound/
  slow/unreadable/raced remains a closed refusal/unknown
  with no expected-artifact fallback, automatic ceiling
  increase or refreshed deadline; the original Python
  16 MiB / 10 s bound and the historical entries are
  unchanged; no ptrace/prctl/proc/kernel/privileged
  helper.
- One owner / RAM context / absolute 1800 s END /
  cumulative ledger / single 600 s cleanup grace;
  existing resource/confinement limits unchanged; no
  global owner-UID membership/cleanup scan (exact
  registered-CID plus owned PID/birth lifetimes with
  tri-state absence; a failed query never absence; the
  unrelated same-UID worker/sentinel survives).
- Native owner evidence FIRST, protected native
  terminal record SECOND, SAME pending pass
  finalization LAST: actual journal read, one-shot
  publication, fail-if-exists, no fresh-path retry, no
  second publication or journal reset.
- The NEW `tests/test_cache_native_fixture_native_handoff.py`
  suite (22 tests) names its layers.  The COUPLED
  public-lifecycle layer (13 tests) drives the REAL
  constructor/admission/prepare/stop/register/observe/
  finish/restore/publish over ONE coherent coupled
  fake process world (bash 40, worker 50 with an
  unrelated SAME-UID frame, native subject 60 held
  out): the useful 1001:1002 positive with the distinct
  identity-bearing record tags at every retained layer
  and the same frozen identity carried through all of
  them; alive-at-finish quiesce refusal (fail evidence
  keeps the FROZEN identity); unreadable/leftover
  lifetime-frame refusals; the default-channel factory
  bound to THIS owner's registered CID + the SAME
  absolute owner END; expired-anchor patience before
  the factory; foreign registration commits nothing
  then a valid registration works; post-admission
  drift refused at the identity use (terminal fail,
  frozen identity in the fail evidence); post-PREPARE
  registration drift refused with NO commit and no
  rebase (same attempt aborted); the finalize
  foreign-identity and original-tag refusals with the
  unmutated ready control; prepare-only honest
  not-ready; second publication one-shot; pre-existing
  destination refusal.  The named pure-data layer (4
  tests) covers the frozen subject-identity
  construction law, the original-vs-frozen disjoint
  laws, the AD channel closed fields (335544320 /
  10.0 / the exe END) and the retained-record consumer
  grammar (a foreign-path record refused).  The named
  admission/constructor layer (5 tests) covers the
  three pre-admission AC-active/canonical-path/
  foreign-path refusals over owned synthetic
  repositories and the two post-admission
  uncollected/mismatched-identity constructor
  failures closing the SAME won attempt terminal
  fail.  EVERY started test
  owner is reaped in a per-test finally before
  monkeypatch teardown (the bounded exact-owner abort
  is issued only while still held; an already-
  converged owner is simply joined, so a positive
  test finishes normally and stays a pass; no
  framework, no host cleanup); a global subject-UID
  scan is trapped and never called (the controller-UID
  scan keeps its closed historical semantics). Fake
  platform only: useful software integration, NEVER
  sealed-real-owner/native/host readiness. The original
  S/X/Y/AB suites retain their recorded checkpoints (ci
  224, local 50, native_prep 124, native_owner 19,
  standin 102, identity 48, exec_capability 52,
  owner_uid 40, binding 45, controller 33 — 759 fixture
  cases green under frozen Python 3.12 / umask 022).
  D09 remains NOT RUN; no native-ready or v1 runtime
  claim. The later serial native handoff remains the
  separately authorized `017-ad` order.

### 11m. Round 017-ae: independent native-attach PTY expectation producer (software-only)

Round 017-ad closed as PARTIAL, and its prescribed
actual single-attempt native handoff qualification was
NOT RUN — never PASS, never waived. During the required
private preparation (no local test/fixture operation,
no source/helper/test/lock/workflow change) the
pre-admission engineering gap was found: no existing
seam produces the native expected PTY independently.
The candidate host /dev/pts delta was REJECTED (kernel
devpts mounts have independent allocation domains;
equal device numbers do not prove one mount/allocation)
and the checkpoint 0001–0003 findings were accepted
WITH QUALIFICATION (immutable references: the AD round
report SHA-256
fb075eaf87cbb45241337f3a0ececcb41dae9f6141081cfb9f82fb47957d9717
and `reviews/017-ad-decision.md`). Round 017-ae repairs
that missing prerequisite SOFTWARE ONLY through the
EXISTING fixture owner, guarded exact-CID exec channel
and NativeOwnerRun composition (no native/client
launch, no actual local fixture operation, no new
runner, supervisor, watchdog, transport, privilege
mechanism or framework; no adapter/cache/parser/
compiler/image/Gateway/model behavior change; all
original S/X/Y/AB/AD schemas, sealed entries, defaults
and consumed namespaces unchanged).

- ONE new future canonical sealed entry `017-af`
  (owner-UID profile; unique order path constant
  `oap/orders/017-af-owner-uid-native-pty-qualification.md`)
  is fixed now but INERT: the constant names the LATER
  strategic activation — not an already-committed or
  activated AF order or run authority; the real AF
  order/namespace/admission/owner is ABSENT (verified
  before activation), and under AE-active the entry is
  refused BEFORE admission or any external work
  (proven only in hermetic synthetic repositories,
  never in the real checkout). AF is selected ONLY by
  its own entry — never a generic wildcard or caller
  flag; the original AD stays strictly AD.
- DISTINCT identity-bearing AF wire tags (closed list,
  one literal each): `slaif-017af-owner-state-v1`
  (owner state), `slaif-017af-native-handoff-prep-v1`
  (preparation snapshot for the AF subject),
  `slaif-017af-native-owner-evidence-v1` (native-owner
  evidence — producer of the nested native facts,
  frozen identity substructure cross-bound),
  `slaif-017af-native-attach-binding-v1` (attach
  binding record: record/baseline/observation/
  allocation/expected_tty_nr/encoding/binding/cid/
  namespace/phase/identity),
  `slaif-017af-native-owner-run-v1` (native run
  terminal record),
  `slaif-017af-native-owner-run-evidence-v1`
  (backend owner-run terminal evidence) and the scope constant
  `slaif-017af-owner-uid-scope`. The original fixed-
  21002, AB and AD consumers stay strict (including
  equal-numeric cross-profile separation); the
  original `slaif-native-handoff-prep-v1` and the AD
  `slaif-017ad-*` tags keep their closed meanings —
  the old-tag prep consumer refuses the owner-UID
  identity form, and a relabeled AF record of the
  original tag can never parse as an original record.
- Attach-binding phase (ONE, non-resettable, in the
  SAME owner RAM context / absolute 1800 s END /
  cumulative ledger / 600 s convergence grace): AFTER
  the original prepare and the separately measured
  stable worker stop, ONE measured baseline is
  collected through the owner (an EMPTY baseline is a
  valid measured state, not missing output; bound to
  the original owner/run/head/admission/profile/
  exact-CID/namespace/phase; caller JSON/data/ready
  flag/descriptor never mints measured origin). After
  the attach, ONE second bounded same-namespace
  observation may derive an expectation ONLY from a
  unique fresh OWNED allocation, with observed
  baseline/device/inode/owner/namespace coherence and
  the legal devpts node GID governed by the MEASURED
  devpts policy (never assumed equal to the process
  GID). Multiple candidates, removal/reuse/
  contradictory baseline, missing/changed namespace,
  unreadable/oversized/malformed rows, failed exec or
  churn uncertainty stay a TYPED refusal (closed
  reason vocabulary) — no second baseline, no
  cosmetic re-snapshot, no fresh window; a CONSUMED
  failed phase retains the failure and never
  re-samples (registration may retry corrected
  parameters against the SAME already-measured
  receipt, never resample allocations). The measured
  probe UID must equal the FROZEN subject UID at the
  owner measurement boundary.
- Expectation encoding: the PRIMARY-SOURCE-VERIFIED
  Linux proc tty_nr encoding, distinct from the
  kernel-internal MKDEV layout: reference unsigned
  encoding `(minor & 0xff) | (major << 8) | ((minor &
  ~0xff) << 12)` as in the primary kernel kdev_t.h,
  emitted through signed tty_nr by proc array.c
  (136:0 → 34816 where MKDEV is 142606336; root-
  verified 136:256 → 1083392, 1024:0 → 262144).
  Finite/signed limits are enforced (0 < tty_nr ≤
  2^31-1); unrepresentable or non-positive values
  refuse; the strict-positive expected-PTY law holds;
  no general conversion is inferred from one sample.
- Producer probe: a minimal FIXED read-only
  `python3 -I -S -c` program admitted ONLY by the AF
  guard (the original default and every AB/AD matcher
  stay byte-for-byte in meaning and refuse the exact
  new probe plus every mutated argv; the -it /
  controller-user / env / env-file forms are never
  inherited). The probe inventories ONLY the
  registered fixture's OWN devpts namespace: at most
  96 slave-device rows (the reserved ptmx node is not
  a slave; unknown names and numeric non-character
  entries refuse, never silently continue), 65536
  output bytes (the drained-total law: a retained
  valid prefix with discarded extra output is not a
  complete observation), 5 s per probe, clamped AT
  EVERY USE to min(start+5 s, the SAME original owner
  END) — the cleanup grace is convergence, never fresh
  measurement; an already-expired/equal END refuses
  before the first read, and expiry is re-checked
  between blocking reads and at the final frame. The
  probe carries a bounded MEASURED devpts-policy fact
  (node GID/mode) bound to the same namespace/root;
  every node's filesystem identity is checked against
  the measured devpts root and the namespace/root
  frame is re-checked AFTER collection. Malformed
  records, duplicate keys and deep-under-byte-cap
  nesting are normalized typed refusals, never raw
  exceptions. The isolated interpreter never executes
  user startup/site modules (proven with bounded owned
  NON-Codex children against synthetic startup
  canaries; the devpts probe itself is never executed
  in that proof).
- Public staged registration: AF registers through its
  OWN default exact registered-CID native channel
  (caller channel overrides refuse; the default 320
  MiB / 10 s native current-executable law and the
  original Python 16 MiB / 10 s bound are unchanged)
  with coherent before/after PID/birth/UID/GID/
  groups/argv/PTY/CID/current-exe frames and the SAME
  frozen context COMPARED, never rebased, plus the
  measured per-subject devpts namespace verification:
  bounded `/proc/<attested-pid>/root/dev/pts` and
  selected-slave metadata reads through the existing
  scoped/birth-bound CID table (5 s operation bound
  clamped to the SAME original owner END; permission
  bits normalized while the character-device and
  device-identity checks are retained; the node device
  must equal the measured devpts root device) and the
  final subject frame revalidated AFTER the blocking
  operations and BEFORE any receipt commit, bound to
  the ORIGINAL collected PID/birth (a reused PID
  cannot validate itself). Matching tty NUMBERS alone
  never establish origin (an equal number in a foreign
  devpts namespace fails); a fabricated/caller/
  replayed allocation receipt, stale stop, PID reuse,
  current-exe race, post-admission/pre-registration
  identity drift, or expiry across a blocking read or
  final frame refuses; a refusal commits NO subject
  receipt/baseline/stop change and the SAME won
  attempt converges honestly.
- Publication: owner evidence FIRST, protected native
  terminal record SECOND, SAME pending-pass
  finalization LAST (one-shot, fail-if-exists, no
  fresh-path retry).
- Proof: REAL constructors / public lifecycle /
  production validators over ONE coherent coupled
  fake process world with the useful unequal 1001:1002
  identity (full public-lifecycle positive: measured
  empty baseline → one new device → independent
  correct expectation → CID/native comparison →
  evidence / retention / one-shot finalization; the
  unrelated same-UID worker survives; a global
  subject-UID scan is trapped and never called).
  Honestly named layers: pure-data (inventory/
  allocation/attach-binding codecs, closed bounds,
  malformed-input and deep-nesting normalization,
  replay/foreign refusals), coupled public-lifecycle
  (the real public positive and contrasts: probe-UID
  boundary, foreign namespace, churn/reuse, post-
  admission/pre-registration drift, expiry across
  blocking reads, one-shot publication, pre-existing
  destination), admission/constructor (AF selection
  positive, AE-active refusal over an owned synthetic
  repository, canonical path, guard construction) and
  at-use boundary (the REAL `owner.devpts_inventory`
  over fake executor failures: exec-failed, discarded-
  prefix capture-invalid, over-cap, late-return END
  expiry, identity drift). EVERY started test owner is
  reaped in a per-test finally before monkeypatch
  teardown (the bounded exact-owner abort issued only
  while still held; an already-converged owner is
  simply joined; no framework, no host cleanup). The
  two AE-modified fixture suites collect 205 tests
  (native_handoff 53 / native_prep 152 collected
  tests); the full fixture regression over ALL
  eleven fixture suites is 818 passed (frozen
  Python 3.12.15, umask 022 test child; pre-commit
  development capture — the prescribed locked B
  gate is the final qualification); the original
  S/X/Y/AB/AD suites are unchanged.
- NOT RUN / unqualified: NO actual local Docker/
  fixture/admission/native/client/model/Gateway
  operation, no worker stop, no host /dev/pts
  enumeration in the ordered scope; D09 remains NOT
  RUN; no native-ready, whole-017 or v1 runtime
  claim. Bounded process deviations (one out-of-scope
  host devpts inventory read — observed read-only,
  full original invocation unverified, no categorical
  host-mutation-absence claim; manual /tmp canary-
  experiment objects preserved AS IS; manual Python
  invocations without -B; the first isolation-test
  variant's ambient-environment controls, with no
  credential claim) are disclosed in the round report
  and the private deviation checkpoints. The LATER
  ACTUAL qualification belongs to the separately
  authorized `017-af` order, strategy-chosen.


### 11n. Round 017-af: ONE actual owner-UID native PTY
qualification attempt (FAILED at preparation)

Round 017-af activated the sealed entry and executed
the ONE authorized bounded actual diagnostic
qualification on the same PR25 (no source change;
attempt P
622f9a7bb52980e9358d60d8220812f66f4b4c4e; run
30eab04899784690a3ac289b1686cb08): ONE reviewed
private non-Codex operator driving the EXISTING
production APIs over ONE managed foreground
procedure (outside RIGHT, `tty:true`, pipefail + tee
of the precreated 0600 stage log, literal P, freshly
measured W/B/F/birth), ONE resolve/constructor
admission, ONE owner/RAM context/1800 s END/
cumulative ledger/600 s convergence grace.

- ACTUAL OUTCOME - honest closed FAILURE at
  preparation (never pass, never waived): the owner
  constructed/admitted ONCE and completed the
  artifact/build/build-context/collision/preflight/
  prepare-target/pull/sentinels phases, then the
  actual preparation/observation failed
  `prep-stat-malformed`. The stage stream contains
  ONLY `s0-preflight` and `closed-failure`: NO
  `s0-prepared` permission, NO stop (stop never
  POSSIBLE), NO baseline, NO attach, NO
  discovery/derivation/registration, NO native
  launch, NO diagnostic. One exact-owner abort
  converged; the journal holds ONE entry (order
  017-af, head P, status `aborted`); the owner
  evidence validates via the production
  `validate_af_owner_run_evidence` (status fail /
  reason cancelled / `cleanup_failures` empty); the
  exact owned container and image were independently
  verified ABSENT (HTTP 404 via the verified
  default local Docker socket); the work/control
  roots are absent.
- WORKER: the SAME W 598258 / birth 150182858 stayed
  running/foreground throughout; B 2014146 / birth
  95656910 unchanged. NO signal, fg, monitor setter
  or restoration was required or performed (no stop
  occurred - the restoration law was never
  triggered).
- DIAGNOSIS (current read-only host stat parsing
  only; NOT a replay of the workflow and mints no
  authority): 454 of 640 current rows were refused
  by the pure parser; the first observed PID 2 and
  other kernel rows carry legal pgrp 0 / session 0 /
  tty 0 / tpgid -1 while the parser demands positive
  pgrp/session - a concrete reproducible defect
  class. The ORIGINAL exact failing row was NOT
  captured and MUST NOT be invented. The operator's
  `prep-stat-malformed` and the owner's `cancelled`
  are DISTINCT facts.
- PUBLICATION: the protected AF native terminal
  record publication was attempted ONCE, raised
  (type only - no invented deeper exception
  reason); the record is ABSENT. No publication
  retry, no new destination, no relabel.
- RETAINED ACTUAL BYTES (0600, preserved AS IS):
  owner evidence
  `2cb066c380d0b7532cc790613b522c85c57b048d58a386dec3a99d10434a93b9`
  (1358 B), operator stage log
  `c79ab2bfa783f9bb7dcc03b17ecbb74341006ec315cc7d100d4556d6588a941f`
  (569 B) under the private AF root, and the
  admission record
  `43fae6ff80a0780c28dffbd09fd3247a65e9435cec6acb10b0f0d3f4bfc4ac78`
  (187 B) under `.oap-local/017-af/`.
- LAW: no retry, no re-admission, no namespace
  reset, no in-round source repair under AF; a later
  strategic continuation owns the software repair
  and a SEPARATELY SEALED later attempt (never
  resetting AF). The ordered native qualification
  is FAILED (never pass): actual preparation FAILED,
  worker stop NOT RUN, native NOT RUN - distinct
  measured statuses, never relabeled. No
  model/Gateway request; all protected
  Qwen/model/network/key/profile state unchanged.
  D09 remains NOT RUN; no native-ready, whole-017
  or v1 runtime claim; ALL 018-024 remain
  mandatory.

### 11o. Round 017-ag: zero-group observations and inert next native entry (software-only)

Round 017-ag repairs the concrete process-observation
prerequisite exposed by the AF attempt SOFTWARE ONLY
(no actual local fixture/owner/admission/Docker/
native/stop/signal/model/Gateway operation; AF stays
spent/aborted forever — no retry, reset, re-admission
or source/head/path/phase re-qualification):
- PURE PARSER: the closed /proc stat parser
  represents well-formed ZERO pgrp/session
  observations (e.g. kernel-thread-like rows) as
  observation data instead of refusing them — the
  exact field/length/state/comm/numeric bounds are
  preserved (negative, overflow and truncated forms
  stay refused; the finite upper bounds unchanged);
  no kernel identity is inferred from comm/name/UID
  and no rows are filtered to avoid validation;
  unavailable/raced/unknown metadata stays explicit
  (True = verified gone, False = present, None =
  unknown remain distinct).
- AUTHORITY CONSUMERS: every authority-bearing
  consumer that previously obtained positive
  group/session implicitly from the parser enforces
  strict positive finite identity itself — the
  actual W/B group and session facts (worker group,
  worker session, Bash pgrp AND Bash session),
  scoped subject and post-executable frames, stop
  receipts, restoration/native-ready verdicts, CID-
  scoped birth and member lifetime. A well-formed
  zero observation can NEVER become a signal
  target, a valid prepared handoff, a stop receipt,
  a registered subject or a restored/native-ready
  verdict. `_is_pid` and the shared execution-
  identity validators are NOT relaxed; the complete
  inventory still inspects every listed row and
  only independently verified-gone churn is
  ignorable.
- WORKER ANCESTRY: separately grouped owned tools
  and worker descendants stay correctly bounded and
  independently inventoried; an unrelated zero-
  group row is classified as unrelated from
  validated metadata and never acquires ownership or
  authority; a genuine unstopped member of G still
  refuses a complete stop. No serialized historical
  record meaning changes to accommodate raw rows.
- ONE new future canonical sealed entry `017-ah`
  (owner-UID profile; unique canonical path
  `oap/orders/017-ah-owner-uid-native-pty-requalification.md`)
  — INERT under AG-active: the real AH order file,
  namespace (production admission path
  `.oap-local/<order>`) and owner are ABSENT now
  (hermetically proven in owned synthetic
  repositories; the real checkout untouched);
  refused BEFORE admission under AG-active;
  resolvable only under its own active at its own
  unique canonical committed order path; never a
  caller flag, wildcard entry or path switch. It
  composes the EXISTING owner/guarded exact-CID/
  NativeOwnerRun and independent devpts producer
  APIs with the SAME frozen bounds (frozen own OS
  identity after won admission; compare-at-use
  law; absolute 1800 s END / cumulative ledger /
  600 s convergence grace; 320 MiB/10 s native and
  16 MiB/10 s Python current-exe bounds; 96 slaves
  / 65536 drained B / 5 s devpts and 5 s subject
  metadata at use/return). No new runner,
  supervisor, watchdog, transport, privilege
  channel, framework, CLI or real-client collector;
  no adapter/cache/Gateway/model behavior change.
- DISTINCT identity-bearing AH wire tags (closed
  list, one literal each):
  `slaif-017ah-owner-state-v1` (owner state),
  `slaif-017ah-native-handoff-prep-v1`
  (preparation snapshot),
  `slaif-017ah-native-owner-evidence-v1`
  (native-owner evidence — producer of the
  nested native facts),
  `slaif-017ah-native-attach-binding-v1` (attach
  binding record),
  `slaif-017ah-native-owner-run-v1` (native run
  terminal record),
  `slaif-017ah-native-owner-run-evidence-v1`
  (backend owner-run terminal evidence) and the
  scope constant `slaif-017ah-owner-uid-scope`. The EXACT tag-
  pair law extends: each identity-bearing tag is
  the record of ITS OWN canonical entry only — the
  AF tags remain AF-only and the AH tags AH-only,
  even for equal numeric identities (cross-entry
  tag/binding pairs refuse at the closed consumers,
  including the workflow finalization dispatcher).
  Shared structural cores keep unchanged meaning;
  the original fixed-21002, S, X, Y, AB, AD and AF
  consumers stay strict. The ONE exact NON-PTY
  devpts probe form is admitted by the AF AND AH
  guards, selected from the owner's OWN bound order
  id (the AB/AD/default guards keep the byte-for-
  byte old closed forms).
- PROOF (fake seams only, no host devpts): the
  REAL public composition over one coherent
  coupled fake process world carrying an unrelated
  well-formed kernel zero-group row across
  prepare/observe/stop/register/finish/restore/
  retention (observed, never adopted, never
  mutated); zero-frame authority negatives (zeroed
  Bash frame refused by the stop collector's own
  zero-group law including the Bash session;
  zeroed Worker frame refused by the baseline
  binding; no receipt committed, honest abort);
  cross-entry tag-pair refusals in both
  directions; the full eleven-fixture-suite
  regression green pre-commit (835 cases; the
  prescribed locked B gate is the final
  qualification).
- ONE bounded READ-ONLY real-host check through
  the existing `collect_worker_group(RealProcTable)`
  against freshly measured SAME W/B/foreground:
  executed exactly once at 2026-10-28T20:11:51Z
  against the literal final source (collector
  sha256 e56d2ac28d44038958481c6b08912b6be9af9e9b55adaec01afa184bf52ea58f),
  exit 0 in 0.117 s with no refusal: the SAME
  worker 598258 (birth 150182858) and Bash
  2014146 (birth 95656910) revalidated
  parent/TTY/comm, the TTY foreground pgrp
  measured 598258 (equal to the worker pgrp;
  same_tty true, same_job false as expected for a
  foreground job in its own group), and the
  closed complete inventory recorded group
  598258 with exactly ONE member (the worker),
  ONE other session group (the Bash group
  2014146) and two separately grouped tool
  sessions (the Bash itself retained as unknown;
  the check's own two tool processes as
  worker-descendants) — closed
  group/ancestry/completeness facts only (not a
  raw process corpus; no argv/environment; no
  total PID/parsed-row count claimed), never
  stop/subject/attach/native readiness, never an
  idle-boundary or handoff-ready proof;
  unknown/raced/overbound outcomes stay truthful.
  The earlier host-wide name/argv candidate scan
  is a separate recorded preflight occurrence,
  not this production check.
- AF is CLOSED FAILED actual native qualification
  (its ONE admission spent forever). D09 remains
  NOT RUN; no native-ready, whole-017 or v1
  runtime claim.


### 11p. Round 017-ah: ONE actual owner-UID native PTY requalification
(verified PASS at the qualified diagnostic scope)

Round 017-ah activated the sealed AH entry and executed the ONE authorized
actual attempt on the same PR25 (no source change; attempt P
06806eeeebac76b38f9ab5d6bbcfd2940f8b66a8; run
1bbeeabfb9434ebf965eaa7e1a624a49; CID
0b5d35f07f984d1fe1c3344e6f6f606afb1142bef9c5e740b14f2d2c3e9da1bc; image
sha256:085bb42752808e9eb52192e0486306f9cc5006b6ac44e2c0049071ea63a74997):
ONE reviewed private non-Codex operator driving the EXISTING production
APIs over ONE managed foreground procedure, ONE resolve/constructor
admission, ONE owner/RAM context/1800 s END/cumulative ledger/600 s
convergence grace. The outcome is a verified actual PASS at the qualified
diagnostic scope, delivered as an accurate PARTIAL round (the single
preserved CI hermetic failure is documented below).
- STOP + ATTACH (measured): the SAME worker 598258 (birth
  150182858, tty 34834) was stopped exactly once through the
  reviewed exact-group stop; the monitor mode was measured ON
  via `set -o` with no option name BEFORE any setter (the
  required attach-branch gate; OFF/unknown would apply the
  failure law); the attach window used `set +m`, and the SAME
  Bash foreground-launched ONE native in the exact owned
  prepared CID with the exact frozen argv `codex --yolo
  --profile early-beta`, the synthetic environment carried in
  the explicit attach via the owner-created env-file path
  (the file held the synthetic CODEX_HOME/provider-key
  values; the retained metadata lists only the key names
  CODEX_HOME/SLAIF_SYNTHETIC_API_KEY and the file sha256, no
  real credentials; no key values on argv), never assumed
  inherited.
- SUBJECT + INDEPENDENT EXPECTED PTY (measured): uniquely
  discovered from the exact-CID inventory (pid 3836555, birth
  184083134 above the launch floor 184080662, UID/GID/groups
  1001:1001/[1001] equal to the frozen owner identity, tty
  matched); baseline zero slave rows (empty, valid), then ONE
  fresh owned allocation 136:0 (uid 1001, node gid 5, inode 3,
  mode 400) coherent with the baseline device and namespace
  [1048813, 1] under the MEASURED devpts policy (fstype
  devpts, gid 5, mode 400) - the legal node GID is governed by
  that policy, lawfully distinct from the frozen process GID
  1001; expected_tty_nr 34816 is the proc new-encode of 136:0
  (never MKDEV); the guarded `-I -S` probe (site/startup
  isolation verified) read only the fixture's OWN devpts.
- CURRENT EXE (measured): the current executable through the
  existing unprivileged registered-CID channel equals the
  pinned public 0.164.0 artifact (sha256
  b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306,
  308139304 bytes; archive sha256
  90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4)
  - binary_verified true in the retained subject frame.
- DIAGNOSTIC + COUNT LAW (measured): ONE visible final
  assistant answer ("slaif fixed final text") with no tool
  call, then a normal `/exit` with the SAME Bash prompt; the
  counts are separate ledgers, never conflated - controller
  wire_requests 2 at the finish observation (0 / unobserved at
  the prepare observation); the second POST's cause is
  UNMEASURED (no retained body/status trace; no forensics or
  rerun authorized, and it is never called a second user
  diagnostic); controller snapshot requests 4 (including
  quiesce/export commands); host ledger 2 API requests (2
  admitted, 0 refused, 0 refusals, 38 docker admissions, 25617
  bytes drained and retained); issued_calls empty; the
  retained metadata record
  (slaif-fixture-metadata-diagnostic-v1) proves
  endpoint/schema/known-name presence only (10 function names;
  known exec_command/write_stdin; 8 unknown unsupported;
  traversal depth 3; raw content NOT retained).
- QUIESCE / EXPORT / TEARDOWN (measured): quiesce closed-pass
  (active 0, residual writers 0, handlers/subject/tools
  stopped, provider sockets closed); the 3273-byte export
  (sha256
  3a1b5bd584414957598a6771b44817873d81bad8579d2fc831d1e6183f403861,
  exporter uid 21001) was exported BEFORE teardown and
  revalidated; the exact-CID teardown converged (descendants 1
  to 0; container and image independently 404 absent-verified;
  the unrelated same-UID sentinel survived with its birth; the
  owner-removed env file, work/control leaves absent).
- RESTORATION + TTY QUALIFICATION (measured): the SAME stopped
  worker was restored in the SAME Bash - monitor restored to
  its measured ON state, jobs-l bound the actual numeric J=1
  to the worker group, `fg %1`, foreground re-measured 598258,
  restoration closed "restored", worker_state S,
  worker_stopped false at the terminal frame. The physical
  restoration bool alone does NOT prove a functional TUI:
  after `fg` the TUI remained canonical/echo (a continuation
  Enter became a newline; no model turn started) and root
  restored raw/noecho on the exact verified /dev/pts/18
  (TCSANOW, no inputflush; no signal/restart/profile/service
  change) before the coding input resumed.
- PROCESS QUALIFICATIONS (by immutable reference): the
  original fixed-21002 validator refused the AH evidence
  before any output/file/resource query; root corrected to the
  explicit validate_ah_owner_run_evidence - no record edit, no
  runtime retry. The initial phase-wait creation line was a
  parse failure (the retained wait facts were re-measured from
  /proc and root-verified: PID 3833957, birth 184063503, state
  S, wait_for_partner; the initial line retained as printed).
- PUBLICATION ORDERING (measured): owner evidence FIRST
  (production-validated), protected native terminal record
  SECOND (one-shot, fail-if-exists), same pending-pass journal
  finalization LAST (ONE entry pass); the retained native run
  record's attempt field "running" is the pre-finalization
  snapshot, and the actual journal terminal pass was verified.
- NOT EARNED: actual tool/read/result formats;
  multichunk/process completion (D09 - NOT RUN); the
  required-syntax audit; whole-017 acceptance; v1 runtime; ALL
  018-024. This diagnostic earns measured startup/request
  schema only, never generic native compatibility.
- CI HERMETIC FAILURE + PARTIAL DELIVERY (measured): the P CI
  run (GitHub run 40780306145, test job 123140025243) measured
  9 SUCCESS / 1 FAILURE: the AG-round hermetic test
  test_ag_ah_refused_under_ag_active_before_admission
  (tests/test_cache_native_fixture_native_handoff.py, lines
  3498/3501/3502) ends by asserting the REAL AH
  order/admission ABSENCE in the checkout - a premise AH
  activation itself invalidated (the order file is committed
  at P; the local admission namespace is consumed, so the
  later two assertions are likewise stale). No production
  defect or native-readiness failure is proven. AH strictly
  forbids source/helper/test changes and in-round repair: no
  repair, skip, xfail or conditional weakening this round; the
  prescribed locked B gate is required once at the final
  delivery head (its actual outcome - the single failure
  preserved - is recorded in the immutable round report); a
  later software continuation owns the hermetic repair (the
  absence/nonmutation proof moved wholly
  into owned hermetic synthetic repositories). The round is
  delivered as an accurate PARTIAL.
- AF is CLOSED FAILED actual native qualification (its ONE
  admission spent forever); AD remains PARTIAL (by the
  immutable round reports). D09 remains NOT RUN; no
  native-ready, whole-017 or v1 runtime claim. The retained
  actual bytes (0600 owner evidence / native run record /
  stage log under the private AH root; the consumed
  .oap-local/017-ah/ admission journal; root review records)
  are inventoried in the immutable round report.
- Round 017-ai (software-only) repairs the
  activated-checkout-dependent AG hermetic
  test — the real-checkout AH order/admission
  absence assertions are INVALIDATED by the
  AH activation itself (the order is
  committed and the local admission
  namespace consumed; the sole P CI test
  failure) — by moving the WHOLE absence/
  nonmutation proof into owned hermetic
  synthetic repositories (AG-active refusal
  before admission, own-active canonical-
  path acceptance, foreign-path refusal,
  pre-admission no-journal/no-claim) plus an
  activated-checkout-shaped synthetic
  control that proves the sealed-entry law
  for an activated checkout without reading
  or mutating the real spent namespace (no
  recursive scan or byte read of it; no
  skip/xfail/weakened validation; no
  production change). It lands the ONE
  explicit future canonical sealed entry
  `017-aj` (owner-UID profile; unique path
  `oap/orders/017-aj-native-process-format-
  qualification.md`) — INERT under AI-active
  (the real AJ order file, namespace,
  admission and owner are absent,
  hermetically proven including the
  production admission path
  `.oap-local/<order>`; refused BEFORE
  admission under AI-active; resolvable only
  under its own active at its own unique
  canonical committed order path; never a
  caller flag, wildcard entry or path
  switch). The AJ entry's OWN verified
  frozen binding selects the CLOSED native-
  format scenario BEFORE startup (the exact
  create argv carries the owner's own
  frozen-entry scenario; ambient env/HTTP/
  caller flags can never select or redefine
  it; the selected closed expectation is
  transport DATA to the owned standin over
  the EXISTING reviewed configuration
  transport, and the host revalidates the
  record against its OWN verified entry;
  default/historical consumers stay strict).
  It composes the EXISTING NativeOwnerRun /
  owner-controller / guarded exact-CID
  channel / frozen owner-UID identity /
  independent devpts producer and the
  existing quiesce/export/integrity/
  teardown/publication law under the SAME
  frozen bounds (1800 s END / 600 s
  convergence grace / 320 MiB-10 s native /
  16 MiB-10 s Python exe / 96 slave rows /
  65536 drained B / 5 s devpts and subject
  metadata at use and return); no new
  runner, supervisor, watchdog, transport,
  privilege channel or framework. The closed
  deterministic format workload (code-
  defined before any actual qualification):
  at most 8 bounded synthetic seed files /
  128 KiB total whose identity is retained
  from PRE-LAUNCH originals (bounded owned
  seed root sealed after the bounded
  writes; no pre-existing-file adoption or
  overwrite), exposed to subject reads
  through the smallest existing fixture
  seam; at most 16 issued semantic calls (4
  exec cases plus at most 12 empty-stdin
  write_stdin polls across the ONE running
  process; never concurrent outstanding
  execs); any forced sleep at most 5 s; at
  most 20 model POSTs, 1 MiB per inbound
  body and 256 KiB TOTAL SERIALIZED
  selected record (including the outer
  binding/identity/CID/tag; byte-checked
  BEFORE decode/copy at export, consumer
  and publication). The four serial cases:
  the complete exit-0 literal file read;
  the genuine initial-running exec plus
  causally associated empty-stdin polls
  through actual completion with output in
  MULTIPLE chunks (at least two NONEMPTY
  observed output pieces across verified
  exec/poll results — empty poll frames
  cannot inflate the proof); the successful
  empty output (the native EMPTY output
  requires the delimiter LF); the
  deliberate bounded truncation with actual
  formatter evidence (always non-acquiring).
  The REAL pinned native text wrapper is
  strictly parsed from the pinned primary-
  source grammar (the pinned
  `function_tool_response` text wrapper;
  the actual formatter truncation is
  warning/line-count plus a UTF-8 head/tail
  marker over the effective-token budget —
  never an assumed fixed byte prefix; chunk
  grouping accepted only as ACTUALLY
  observed in the verified results — never
  declared transport boundaries; native
  completion may omit the process ID); the
  exact issued family/name/call-ID/argument
  digest and numeric causal request
  position retained before accepting a
  result (strictly AFTER its own issuance
  — it may equal the next call's issuance;
  same-ID changed-arguments/results,
  unissued/preloaded/duplicate/conflicting
  results and foreign process/session facts
  refuse; issued call IDs unique across the
  complete <=16 registry; previously
  completed historical results in later
  accumulated requests validate as frozen
  historical identity and never advance or
  retain twice). Selected frames only:
  exact known synthetic call/result text
  after strict formatter/source/byte
  verification against the immutable seeds
  (actual IDs/association, complete wrapper
  ordering, chunk/process fields, Unicode/
  CRLF/empty/truncation facts); no
  reconstruction from digests, no raw
  unknown output, no source/private-
  history/full-request/headers/auth/prompt/
  schema blob persistence; unknown text is
  a fixed safe metadata/digest or typed
  refusal. The complete four-case snapshot
  validator keeps its earned law; a
  DISTINCT closed PARTIAL snapshot form
  (zero-POST source-less; completed-prefix-
  plus-one-outstanding) retains only
  verified frames, re-derives pending
  byte/session facts from them and never
  mints a format qualification. Publication
  keeps the ordered separation: the FIRST
  protected owner evidence requires the
  SAME owner's OWN successful protected
  retention (a narrow RAM retention receipt
  set ONLY after the protected owner writer
  returned verified success, independent of
  the cleanup/evidence status — a post-
  commit unverified result never sets it, a
  precomputed digest or merely existing
  matching file is not a receipt; an honest
  failed owner whose FIRST evidence WAS
  retained keeps its representable
  publication; a failed/unverified
  retention refuses BEFORE any AJ native/
  capture destination); the SECOND
  protected selected native capture record
  is built only from this owner's retained
  selected export (validated at the
  producer boundary with the shared
  selected-export validator before
  decode/copy under the existing raw-export
  byte cap); the SAME pending-pass journal
  is finalized LAST (actual journal read,
  one-shot, no overwrite, no fresh-path
  retry). The AJ QUALIFICATION journal gate
  keeps the facts separate: terminal PASS
  additionally requires the ACTUAL cleanup
  pass, the native-ready verdict, the
  strict full four-case format
  qualification and the protected
  retention; a cleanup-pass / native-ready
  owner with an unsupported, partial or
  absent format stays truthfully
  representable and retainable with the
  owner's actual outcome and the native
  verdict preserved unchanged, but the
  journal closes terminal FAIL (never
  pass) and the cached outcome/
  finalize_attempt can never later upgrade
  it; a post-retention unverified or raced
  finalization is a closed failure
  preserving the retained bytes and the
  actual journal facts as-is. The proof
  drives the REAL public composition over
  ONE coherent coupled fake process world
  (the useful unequal 1001:1002 positive
  plus the adversarial contrasts) with
  EVERY started test owner reaped in a per-
  test finally and the global subject-UID
  scan trapped; 1071 collected across all
  twelve fixture suites at the current
  source (pre-commit development capture —
  the prescribed locked B gate at the final
  delivery head is the final qualification).
  NO actual AJ fixture operation, native
  launch (including help/version), worker
  stop, Docker operation, model/Gateway
  call or host signal this round; the
  bounded process deviations are disclosed
  in the round report. D09 remains NOT RUN;
  no native-ready, whole-017 or v1 runtime
  claim; the later ACTUAL format
  qualification belongs to the separately
  activated `017-aj` order, strategy-
  chosen.

- Round 017-aj (the ONE actual attempt) executed
  the ACTUAL native format qualification that
  017-ai landed inertly, on the bounded
  reference fixture, under ONE reviewed
  private non-Codex operator, ONE managed
  foreground procedure and the ONE terminal
  admission (attempt head P; operator terminal
  exit 0; every fact in the immutable round
  records). The SAME coding worker was stopped
  once, by exact-group TSTP with the monitor
  already ON before any setter, and the pinned
  0.164.0 native ran in the exact owned CID
  against an independently measured expected
  PTY (never MKDEV), frozen identity 1001:1001
  groups [1001], synthetic environment attached
  explicitly, current exe MEASURED through the
  registered-CID channel as the pinned
  artifact. From ONE closed input line the four
  serial cases byte-verified against the
  immutable pre-launch seed originals:
  complete 494 B read; genuine
  initial-running exec, 1536 B output (CRLF
  and non-ASCII), ONE poll, TWO non-empty
  pieces; successful 0 B empty output; bounded
  truncation at the effective token budget,
  never acquiring. Measured: 5 issued calls, 1
  poll, 7 model POSTs (planned minimum 6; the
  ONE extra POST's purpose UNMEASURED, no trace
  or forensics); controller export ledger 9
  requests / 7561 output bytes; host 2 API
  requests (2 admitted / 0 refused) plus 38
  Docker admissions; healthz 1; the physical 16
  cumulative TCP-handler cap preserved, exact
  physical TCP admission count NOT retained.
  Quiesce closed-pass (0/0); the 8252 B
  retained FULL four-case capture (exporter uid
  21001) was revalidated BEFORE teardown and
  qualified by the shared strict full consumer,
  the only form that ever qualifies.
  Publication kept the ordered separation: the
  owner's OWN successful retention receipt
  FIRST, the retained AJ record
  (publication-time attempt=running) SECOND,
  the ONE pass journal entry LAST, one-shot
  with no fresh-path retry and no
  cached-finalize upgrade; ALL EIGHT separate
  facts verified; exact-CID and image teardown
  404-verified with the sentinel surviving;
  the host-side synthetic env file (holding
  the attempt's CODEX_HOME and provider-key
  values), explicitly used by the Docker
  attach, was removed during the owned
  cleanup, while the retained metadata
  records key names plus sha only. The SAME Bash job restored
  the worker
  foreground with the saved TTY attributes
  (TCSANOW, no input flush, readback equal),
  and functional input was verified by the
  root with an actual read-only tool probe. The
  ONE admission is terminal (never reset,
  retried or relabeled); no source, helper,
  test, lock or workflow file changed in this
  round; the bounded process deviations are
  disclosed in the immutable round records.
  D09 remains NOT RUN; the measured
  native_ready=true verdict is bounded to
  this reference-fixture attempt and
  recorded in those immutable records; no
  generic native-ready, whole-017 or v1
  runtime claim; 018-024 remain the
  mandatory planned succession.

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
