# Vision acceptance handoff

This is a repository-only, human-gated acceptance path. The 004-al acceptance
run completed with the protected `qwen-serving-vision.service` active on
`127.0.0.1:18020`; `qwen-serving.service` was inactive and no port-18021 image
proxy was assumed.

## Exact fixture contract

The mutually exclusive protected fixture is:

- user unit: `qwen-serving-vision.service`;
- endpoint while active: `http://127.0.0.1:18020/v1`;
- served model: `qwen3.8-27b`;
- Responses `input_image`, text Responses, ordinary function tools;
- one image per request, `detail: auto`, and
  `supports_image_detail_original = false`;
- vision tower enabled, no `--language-model-only`,
  `--limit-mm-per-prompt {"image":1}`, context 100000, max sequences 1.

The fixture is mutually exclusive with the active text unit because both use
the one GPU and port 18020. The human owns the deliberate switch and rollback:

1. stop the text unit and start the vision unit;
2. verify the exact unit, model, capability, and protected endpoint read-only;
3. run the gated acceptance command below;
4. stop the vision unit and start the text unit again;
5. verify the text service and port 18020 are restored.

Coding does not perform, enable, reload, or restore either protected unit.

## Runner and evidence

`tests/helpers/vision_e2e_support.py` creates a private disposable Git fixture,
CODEX_HOME, cache, model catalog, and two deterministic synthetic PNGs. The
full scene has distinguishable left/right color blocks; `crop.png` is the
newest right-side crop. The catalog is derived from installed Codex `0.149.0`
schema and is constrained to text+image input, 100000 context, disabled
`supports_image_detail_original`, and no parallel tool calls.

The runner invokes exactly two bounded commands:

```text
codex --dangerously-bypass-approvals-and-sandbox exec --image full.png ...
codex --dangerously-bypass-approvals-and-sandbox exec resume --last --image crop.png ...
```

It does not use `--ephemeral`; the second command resumes the first persisted
session. Prompts do not contain the delegated sentinel. Results retain only
status, event counts/bytes, `binding_effective` and `byte_exact_format` booleans,
the CR/LF framing class, image labels, lengths, SHA-256 values, metric deltas,
and cleanup facts. No prompt-supplied processing marker is used.

The 004-aj disposable no-model capture used the same vision catalog/configuration
and global-yolo image invocation against a temporary loopback error provider. It
retained only the ordered top-level type tuple/counts: `function` × 8, `custom`
× 1, `tool_search` × 1, and `web_search` × 1. The repository-only structural
predicate recognizes exactly those observed standard categories; the fixed
`local_shell` and `unexpected` buckets remain diagnostic negative categories,
and no tool name/schema/argument/body is retained.

The fake-upstream tests construct the production `create_app` path with the
acceptance-only `VisionOutboundRecorder` as its HTTPX transport. The recorder
sees the exact request object after image policy, constitutional processing,
and serialization, then forwards that same object to fake upstream. A single
Codex invocation may run a tool loop and emit multiple main Responses
requests, so the recorder opens an explicit phase around each invocation and
checks every request in order. Every phase-1 request must contain exactly the
full scene; every phase-2 request must contain exactly the newest right crop.
One invalid request therefore rejects the whole grouped acceptance, even when
another request in the same phase is correct. Compiler `/v1/chat/completions`
requests share the transport but are ignored as non-main requests. Image
metrics scale from the directly recorded phase counts: phase 1 is
`seen=n1, removed=0`, and phase 2 is `seen=2*n2, removed=n2`, with each phase
bounded and non-empty. Only fixed labels, counts, types, lengths, hashes, and
booleans are retained; no production debug header or raw-body diagnostic is
added.

## Human-gated command

After the vision unit is active and independently verified, run from the coding
repository with the protected key already present in the environment:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

The test constructs the repository-owned candidate through `create_app` with
the same acceptance-only recorder and a real HTTPX upstream transport, serves
it on loopback 18031 using a temporary configuration, runs the two Codex
invocations through that candidate, and stops/removes the candidate and all
temporary fixture/cache/session state. It requires both responses,
`binding_effective=true` on both turns with CR/LF-only framing and separate
`byte_exact_format=false`, a direct matching persisted/resumed session identity,
governance observation/acquisition/compile/injection on both
invocations, exact outbound image identity and count for every main request,
the exact model catalog facts, a non-empty bounded phase for each invocation,
every outbound request grouped in its phase, the scaled image metric invariant,
and effective binding. Exact outbound image identity/count plus the
successful protected-upstream/Codex lifecycle proves this compatibility
property; no visual-quality benchmark or prompt-supplied marker is used. Port
18031 must be absent afterward. It does not switch or mutate protected
services.

The live test is intentionally skipped unless `SLAIF_VISION_ACCEPTANCE=1` is
set. A skipped run is not acceptance evidence. If the human fixture is not
active, retain the text-only limitation and do not run this command.

## 004-al result

The exact command above was run once and passed: `1 passed, 120 deselected` in
99.16 seconds. The two persistent Codex invocations used the repository-owned
global-yolo runner and the protected vision fixture without changing the
fixture.

The safe outbound result was full/full then crop/crop: every bounded phase-1
main request forwarded exactly one `full_scene` image, and every bounded
phase-2 main request forwarded exactly one newest `right_crop` image. The
phase counts were non-empty and bounded to four requests per invocation; the
image metrics matched the direct recorder invariant `(n1, 0)` for phase 1 and
`(2*n2, n2)` for phase 2. Non-image, governance, and tool content remained
preserved for every recorded request.

The final binding was effective on both turns. The event and output-file
evidence retained the fixed `leading_lf_lf` classification from the known
fixture, so `binding_effective=true` and `byte_exact_format=false` are separate
facts; the accepted provenance is `event_surrounding_crlf`. Effective binding
content is accepted, but byte-exact final formatting is not proven or supported
on this fixture. No spaces, tabs, Unicode whitespace, markup, punctuation,
prose, substring, or wrapper is accepted by the repository-only predicate. Only
the hidden sentinel's leading/trailing CR/LF framing is normalized.

The result is scoped to Qwen3.8-27B on the selected RTX 3090 fixture: vision
context 100000 versus the text configuration's 150000, one image per upstream
request, and no production, cutover, benchmark, or visual-quality claim.

## Rollback and safety

The human-controlled rollback is `qwen-serving-vision.service` stopped and
`qwen-serving.service` started, followed by read-only health/model/listener
checks. The protected unit files, launchers, environment/credential files,
Codex profiles, model files, firewall/VPN/network bindings, and port 18020 are
outside this repository-owned test and must remain unchanged.
