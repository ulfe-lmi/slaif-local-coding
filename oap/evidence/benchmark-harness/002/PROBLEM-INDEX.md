# Engineering problem index

This is a triage guide, not a root-cause declaration. Start with the evidence
named for each item and preserve all existing attempt identities when testing a
repair.

## P0 — long-context sequence fails in every condition

All four context attempts terminated before the fixed final query. DIRECT
surfaced HTTP 400 with `Unterminated string starting at: line 1 column 9
(char 8)`. VISION and CACHE failed on their third invocation; BOTH produced one
native compaction, completed a third invocation, and failed on the fourth.

Inspect:

- `CONTEXT-FAILURE.md`;
- context task/driver code in `harness.tar.gz`;
- Responses tool-call parsing, serialization, and resume behavior;
- the difference between direct upstream errors and adapter error sanitization.

Do not assume the cause was the 262,144-token context window. The corrected
catalog declared a 222,000-token auto-compaction threshold, and BOTH did compact
before later failing. The public evidence cannot attribute the malformed string
to Codex, vLLM, model output, or an adapter parser with certainty.

## P0 — very low independent functional success

Only one of fourteen workload attempts passed its frozen independent functional
judge. `SUBMITTED` means the subject claimed completion; it does not mean the
implementation was correct. Review `JUDGE-CHECKS.csv` rather than treating the
terminal status as the score.

## P1 — repeated web rule defects

Four web attempts passed 6/8 checks but failed `flood_and_win` and
`independent_randomized_rule_sequences`. The only 8/8 attempt consumed much
more prompt/time than the others. Determine whether failures share a generated
implementation pattern, a task ambiguity, or a model/client behavior. The
public archive excludes raw source workspaces; use the separately preserved
private handoff for content-level comparison.

## P1 — accumulated-image failure in Web DIRECT

Web DIRECT ended with a backend error stating that at most 16 images may be
provided in one prompt. The attempt had 17 native `imageView` items and still
scored 6/8. DIRECT intentionally performs no image-history adaptation, while
VISION/BOTH retain only the newest image and CACHE passes image history through.
Review whether the frozen workload/client interaction is suitable for a DIRECT
control against this backend limit; do not covertly add a workaround to only
one condition after observing the result.

Web CACHE on lane 2 also ended in a sanitized upstream error after 17 native
image views, but the public evidence does not prove that it had the same
upstream cause.

## P1 — repeated terminal interaction defects

No terminal implementation passed. Two attempts reached 4/5 and failed only
`flood_win_and_restart`; three passed only `quit_from_initial_state`. Review PTY
timing/state assumptions, UI semantics, and generated implementations without
weakening the frozen oracle after observing results.

## P1 — adapter arms hide the actionable upstream context error

DIRECT preserved the upstream HTTP 400 message; VISION/CACHE/BOTH exposed only
the product's sanitized `upstream_error`. Sanitization is an important public
security behavior, but authorized private diagnostics need a content-safe way
to attribute which layer rejected malformed tool-call data. Do not add raw-body
logging to production or publish private prompts/tool output.

## P1 — qualification cannot make a formal interference claim

Two different workloads were exercised concurrently, endpoint exclusivity was
observed, and protected activity on the other GPUs was present. No predeclared
criterion says what shared CPU/RAM/PCIe/network interference is acceptable.
Post-hoc acceptance would be methodologically invalid. Define the criterion
before a successor formal campaign.

## P2 — energy is provisional

Recorder counter transitions correlate with VM observations only at roughly
one-to-two-second scrape scale, not the required independent sub-100 ms clock
standard. Keep energy values provisional and do not use them for exact attempt
boundary attribution until the clocks are qualified.

## P2 — one host/VM counter boundary mismatch

Thirteen attempts had exact host-versus-VM prompt-token deltas. Web DIRECT
missed 125,998 prompt tokens at the host sampling boundary. VM before/after
counters remain authoritative for the published attempt total.

## P2 — visual quality remains unscored

Web functional checks were run, but blinded visual ratings were not completed.
No missing visual score may be treated as zero or pass.

## Repair discipline

- Do not mutate archive 002 or relabel its attempts.
- Add regression tests for each harness correction.
- Create a new kit/protocol identity for substantive changes.
- Keep the supplied model catalog byte-identical and subject reasoning `xhigh`
  unless human authority explicitly changes the experimental configuration.
- Rerun known-correct and defective judge controls before model-backed work.
- Preserve every attempt and use a new ID for any permitted retry.
