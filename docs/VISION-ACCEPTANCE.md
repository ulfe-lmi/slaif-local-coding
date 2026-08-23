# Vision acceptance handoff

This is a repository-only, human-gated acceptance path. The current protected
host state is text-only: `qwen-serving.service` is active on
`127.0.0.1:18020` and `qwen-serving-vision.service` is loaded but inactive.
No port-18021 image proxy is assumed.

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
status, event counts/bytes, fixed marker booleans, image labels, lengths,
SHA-256 values, metric deltas, and cleanup facts.

The fake-upstream tests construct the production `create_app` path with the
acceptance-only `VisionOutboundRecorder` as its HTTPX transport. The recorder
sees the exact request object after image policy, constitutional processing,
and serialization, then forwards that same object to fake upstream. It proves
one full image on turn 1 and two input images reduced to exactly the newest
crop on turn 2. It also proves non-image content, tool items, and governance
markers are preserved, with exact image metric deltas of seen/removed `1/0`
then `2/1`. Compiler `/v1/chat/completions` requests share the transport but
are not counted as main image turns. Only fixed labels, counts, types, lengths,
hashes, and booleans are retained; no production debug header or raw-body
diagnostic is added.

## Human-gated command

After the vision unit is active and independently verified, run from the coding
repository with the protected key already present in the environment:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

The test constructs the repository-owned candidate through `create_app` with
the same acceptance-only recorder and a real HTTPX upstream transport, serves
it on loopback 18031 using a temporary configuration, runs the two Codex turns
through that candidate, and stops/removes the candidate and all temporary
fixture/cache/session state. It requires both responses, exact final-message
sentinel binding, a direct matching persisted/resumed session identity, the
governance and image markers on both turns, the exact model catalog facts,
image metric deltas, and two ordered recorder facts for full then crop. Port
18031 must be absent afterward. It does not switch or mutate protected
services.

The live test is intentionally skipped unless `SLAIF_VISION_ACCEPTANCE=1` is
set. A skipped run is not acceptance evidence. If the human fixture is not
active, retain the text-only limitation and do not run this command.

## Rollback and safety

The human-controlled rollback is `qwen-serving-vision.service` stopped and
`qwen-serving.service` started, followed by read-only health/model/listener
checks. The protected unit files, launchers, environment/credential files,
Codex profiles, model files, firewall/VPN/network bindings, and port 18020 are
outside this repository-owned test and must remain unchanged.
