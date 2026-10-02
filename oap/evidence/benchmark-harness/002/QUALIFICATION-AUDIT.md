# Corrected GPU2/GPU3 qualification audit

## Verdict

Qualification is **false**. The corrected two-lane campaign completed its
model-backed workloads, judges, isolation checks, usage accounting, and recorder
extraction, but three mandatory gates remain false:

1. the fixed context-pressure sequence did not complete;
2. shared-host interference has no predeclared accepted criterion;
3. recorder/VM clock alignment was not independently verified to the required
   sub-100 ms standard.

No freeze or formal stage approval was created. Qualification success would not
itself have authorized a pilot.

## Execution accounting

- Backend capability attempts: 2 (one partial output-bound probe and one
  explicitly linked diagnostic).
- Workload attempts: 14.
- Terminal states: 8 `SUBMITTED`, 6 `SUBJECT_ERROR`.
- Measurement validity: 14/14 valid; both endpoints drained after attempts.
- Independent functional successes: 1/14.
- Hidden retries: 0.
- Formal pilot/main/extension attempts: 0.
- Native model-directed image evidence: 67 typed `imageView` items across five
  web attempts.
- Native structural compaction: one event, in Context `BOTH` only.

Two early `.5` attempts recorded a protocol flag because Codex added exactly
`[projects."/work"] trust_level="trusted"` to its own configuration. The `.6`
runner classified that single self-registration as benign while continuing to
reject changes to model, provider, endpoint, reasoning, catalog, or feature
settings. Original result bytes and flags were preserved.

All-attempt backend use was 78,622,898 prompt tokens and 1,792,720 generated
tokens (80,415,618 gross) across 792 completed backend requests. The only
functionally successful attempt used 18,492,251 prompt and 180,295 generated
tokens. Backend totals and overlapping client usage are reported separately and
never summed.

## Qualification checks

| Check | State | Evidence summary |
|---|---|---|
| two measured GPU lanes | PASS | distinct GPU2/GPU3 endpoints and process attribution |
| one model replica per measured GPU | PASS | exactly one stable measured process per GPU in every sample |
| same model/runtime | PASS | matching served model and runtime configuration |
| host-LAN reachability | PASS | permitted preflight and route validation |
| Responses/tool loop | PASS | real Codex local-command continuation observed |
| vision image delivery | PASS | typed native `imageView` evidence |
| multi-image capability classified | PASS | bounded one/two-image probes |
| governance observation/injection | PASS | adapter counters in `ADAPTER-MECHANISMS.csv` |
| backend metric attribution | PASS | per-lane counters reconciled to attempts |
| client usage semantics | PASS | observed as session-cumulative |
| driver calibration | PASS | exec/resume identity remained stable |
| compaction signal calibration | PASS | native typed event distinguished from adapter history reduction |
| context-pressure sequence completed | **FAIL** | 0/4 reached final query |
| judge positive/negative controls | PASS | all correct and defective controls classified as expected |
| paired concurrency observed | PASS | six mixed-workload dual-lane waves |
| shared-host interference accepted | **FAIL** | no predeclared acceptance criterion |
| GPU2 endpoint exclusive | PASS | no extra measured-GPU PID and no queue overlap |
| GPU3 endpoint exclusive | PASS | no extra measured-GPU PID and no queue overlap |
| background GPU activity recorded | PASS | protected-GPU process presence recorded; utilization unavailable |
| recorder cadence/coverage | PASS | 13,622 samples; no scrape failures |
| recorder/VM clock alignment | **FAIL** | correlation only at scrape-cadence scale |
| backend prefix-cache policy recorded | PASS | exposed counters preserved and reconciled |
| subject isolation | PASS | fresh workspace/home/adapter/cache and no controller mounts |
| VM capacity | PASS | two-worker run observed without infrastructure failure |

## Judge controls

Known-correct and deliberately defective fixtures were run for web, terminal,
and context judges. All six controls produced the expected success/failure
classification. This validates the judge control path; it does not turn failed
subject implementations into passes.

## Workload outcomes

All four context conditions ended with `SUBJECT_ERROR` before the final query.
DIRECT exposed an HTTP 400 unterminated-string message. Adapter arms exposed a
sanitized upstream error, limiting layer attribution. The evidence supports a
malformed generated/parser JSON failure somewhere in the tool-call path, but
does not prove which parser emitted it and does not establish a context-window
overflow.

Web and terminal subjects frequently submitted implementations, but the
independent judges rejected every one except GPU3 Web `CACHE`. These are task
outcomes rather than proven infrastructure errors, so no invisible retry was
performed.

## Disposition

The failures and missing observations are retained as preliminary diagnostic
evidence. A substantive task, driver, parser, scoring, or protocol change needs
a new kit/protocol identity. A future formal schedule also needs a freeze and a
separate human approval binding exact waves, two-lane concurrency, expiry, and
retry policy.
