# OAP ORDER 014-f — Recover valid A7, prove the complete pre-freeze gate, and qualify private RC7

## Objective and GitHub state

Continue numeric Objective 014 in the existing PR. **AMEND_EXISTING_PR** only.

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: `#19`, open, base `main`, head `oap/014-real-codex-compatibility-rc3`
- Remote PR head at publication: `6f82b46557b1e99e49fcc9172f702bfc8c11593c`
- Remote `main`: `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`
- Active predecessor: `014-e`; it has no report and is abandoned before push/publication.
- Valid local artifact-input source to retain: A7 `0f999e77b487b757841e288897bc9c74e411a28b`.
- Invalid local-only freeze commits to discard: `11cec47d1951e3ae67344facbd07e8e4d48e35d8` and its message-only replacement `25d66a6d8d54acf624f9bb178b21d3f4b20b90bb`.
- Neither invalid freeze is remote. Neither RC7 tag exists. No RC7 release workflow or registry mutation has occurred.

This round corrects execution ordering only. All applicable requirements and non-goals from 014-a through 014-e remain cumulative.

## Strategic finding and required recovery

014-e correctly rebuilt the intended RC7 source from remote truth and committed A7. Focused gates, Ruff, format, mypy, documentation checks, and clean reproducible builds were observed. Clean A7 builds on CPython 3.12.3 and 3.12.14 were byte-identical:

- wheel SHA-256 `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`;
- sdist SHA-256 `65527c6f657023d556c3d6cb5b9bf849a8fe4dac8c53d77a8de26d9e76be4579`;
- 127 source-input entries.

The worker then committed S7 before running the complete pytest suite against the generated pre-freeze manifest. That violated 014-e. It also first wrote the wrong A7 SHA in the commit message and locally replaced that commit. Strategy stopped the worker before push or publication.

Recover without rewriting A7:

1. preserve the byte-exact A7 tree and commit `0f999e77b487b757841e288897bc9c74e411a28b`;
2. discard the local-only invalid S7 history, restoring HEAD to A7 before committing this round's OAP transcript/activation;
3. preserve this immutable 014-f order and set `oap/active` to `014-f` in the activation/transcript commit;
4. do not commit the stray pre-existing untracked files `Local`, `clean`, or `unchanged`;
5. independently recheck the remote branch, PR, tags, workflow history, and private package state before mutation.

Do not reuse `25d66a6` as the image source. Do not call the abandoned attempt a valid freeze.

## Exact pre-freeze sequence

The generated pre-freeze manifest can and must be tested before it is committed. Use this sequence exactly:

1. From the retained A7 bytes, rebuild in clean archived trees under both available Python 3.12 patch environments. Require byte-identical wheel and sdist and the hashes above. A mismatch blocks the round.
2. Generate `packaging/release_provenance_manifest.json` in the working tree with:
   - objective `014-f`;
   - candidate `0.1.0-rc7`;
   - `generated_from.git_commit` exactly A7;
   - `pre_freeze` / unpublished state;
   - no OCI digest;
   - the complete A7 source-input map;
   - the freshly reproduced artifact hashes.
3. Leave those exact generated manifest bytes **uncommitted** and run the entire local gate against that working tree:
   - `uv lock --check` and frozen sync as required;
   - Ruff check;
   - Ruff format check;
   - mypy;
   - documentation consistency;
   - the complete `pytest -q` suite, with no unexpected skip and no failure;
   - artifact-policy inspect and fresh-wheel install smoke;
   - the PRE-mode record-present rehearsal and all tamper cases;
   - the focused record/handoff, provenance, source-binding, release-publisher, Docker-record, and real-Codex harness suites.
4. If any gate fails, do not freeze, push, publish, or repair around the failure. Publish a truthful blocked report for 014-f.
5. If every gate passes, commit the already-tested manifest bytes once as the sole valid S7 freeze. The commit message must name literal A7 `0f999e77b487b757841e288897bc9c74e411a28b`. Prove the working-tree manifest hash immediately before commit equals the committed blob hash after commit. Prove A7..S7 changes only permitted derived/OAP material and both refs have the same 127-entry source-input map.
6. After S7, run the complete local gate and PRE rehearsal again from clean S7. No tracked script, test, documentation, schema, workflow, configuration, packaging-policy, or other source correction is permitted after S7. Any such need blocks RC7; do not re-freeze.

## RC7 publication and qualification

Only after the preceding sequence is green:

1. push the existing PR branch and obtain fresh PR CI and CodeQL at exact S7;
2. require every required check present and successful and zero open CodeQL alerts;
3. verify both aliases are absent before mutation: `0.1.0-rc7` and `sha-<exact-S7>`;
4. publish exactly those two private aliases from exact S7 with the existing release workflow; fail closed if either identity is occupied;
5. independently resolve both aliases to one new digest and keep GHCR private;
6. create a new immutable testing ledger `005`; never modify ledger `001` or earlier ledgers;
7. qualify the actual pulled image by digest through every ordinary Docker/release gate: platform, OCI labels, retained in-image wheel hash, dependency lock inventory, hardened properties, signed Gateway contract CI where ordinarily required, fail-closed readiness, teardown absence, source/provenance binding, and no-build pull deployment;
8. run bounded standalone genuine-Codex compatibility with Gateway absent:
   - Codex CLI `0.149.0` is already established on this host and remains the required client for this round;
   - VISION, CACHE with static single-user constitution identity, and BOTH must each complete a genuine model/tool loop through loopback Local Coding to the unchanged tested vLLM endpoint;
   - DIRECT is contextual control evidence where safe;
   - use no signed-Gateway headers to make standalone qualification pass;
   - preserve the request/schema fixture regression in ordinary CI regardless of live-backend availability.
9. generate the current RC7 record, handoff, and published provenance only from verified facts. Preserve the archived RC5 material and failed RC2 identities. Record the exact RC identifier, S7, digest, aliases, wheel/sdist hashes, build pins, lock hash, configuration/source-input hashes, Codex version, VISION/CACHE/BOTH/DIRECT results, platform, private-auth requirement, Gateway absence, and explicit statements that benchmark execution, final public release, and protected-host cutover did not occur.
10. push the generated evidence/records as permitted post-freeze material, obtain fresh final PR CI/CodeQL, and publish the immutable 014-f report in the final report-only SELF commit.

If the real backend becomes unavailable, report `BENCHMARK_BLOCKED`. Do not infer readiness from synthetic tests. Codex versions later than 0.149.0 are allowed only if 0.149.0 can no longer be established, and the report must prove that unavailability and identify the exact substitute version.

## Product, security, and host boundaries

Do not run or analyze the Minesweeper benchmark. Do not touch its repository. Do not modify, install, upgrade, patch, restart, or reconfigure vLLM, its environment, model/checkpoint/quantization/context/parser/GPU arguments, port 18020, `qwen-serving`, firewall/VPN, API keys, Gateway production state, routing, or active Codex profiles. Candidate Local Coding may bind loopback port 18031 only and must tear down fully.

Do not make GHCR public, create `v0.1.0`, create a final GitHub Release, perform protected-host cutover, or claim public/production/compliance/general-model readiness. Do not log or persist raw prompts, images, tool output, source content, credentials, bearer values, or private registry tokens. Sanitize all evidence.

## Immutable report contract

Create exactly one report matching `oap/reports/014-f-*.md`. Before the report commit, all claimed implementation/evidence state must be remote. The final commit must change only that report, its parent must equal the report's literal implementation SHA, and the report must state literal SELF. Include exact PR/base/head/commit chain; A7/S7; discarded local freeze identities; manifest pre-commit and committed hashes; every command/result/count/skip; CI and CodeQL run/job URLs; publication run; tag/digest inspection; ledger 005 paths and redaction review; pulled-image results; real-Codex mode results; protected-host before/after facts; port-18031 teardown; diff/non-goal audit; and one explicit verdict.

The verdict may be `BENCHMARK_READY` only when every cumulative Objective-014 criterion is satisfied. Otherwise use `BENCHMARK_BLOCKED` with the exact blocker. Never merge.
