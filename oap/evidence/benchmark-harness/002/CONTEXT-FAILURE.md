# Corrected GPU2/GPU3 context qualification failure

## Scope

All four context conditions used the corrected model catalog, mandatory `xhigh`,
262,144 context, 222,000 automatic-compaction threshold, fresh homes, stable
session IDs and disabled time/token stop causes. Each measurement was valid and
its backend drained. None reached the fixed final fact query.

## Attempts

| Attempt | Condition | Lane | Completed invocations | Typed compactions | Terminal state |
|---|---|---:|---:|---:|---|
| `qgpu23-mixed-w02-l2-context-direct` | DIRECT | 2 | 2, failed on 3 | 0 | `SUBJECT_ERROR` |
| `qgpu23-mixed-w04-l3-context-vision` | VISION | 3 | 2, failed on 3 | 0 | `SUBJECT_ERROR` |
| `qgpu23-mixed-w05-l2-context-cache` | CACHE | 2 | 2, failed on 3 | 0 | `SUBJECT_ERROR` |
| `qgpu23-mixed-w06-l3-context-both` | BOTH | 3 | 3, failed on 4 | 1 structural | `SUBJECT_ERROR` |

Every attempt retained exactly one thread identity across resume calls. The
failure was not caused by controller wall time or observed-token limits.

## Error and counter evidence

DIRECT exposed an HTTP 400 `BadRequestError` whose message was:

```text
Unterminated string starting at: line 1 column 9 (char 8)
```

The adapter arms exposed a sanitized `upstream_error`, so the exact upstream
body is unavailable. VISION and CACHE adapter counters each recorded six HTTP
400 Responses requests over the attempt; BOTH recorded one. Successful backend
requests were still counted and included both `stop` and, for the first three
arms, one `length` finish. There was no metric reset or backend queue residue.

The evidence is consistent with malformed generated/parser JSON during the
tool-call loop, but the preserved data does not prove which parser layer emitted
the malformed string. It should not be relabeled as a context-window overflow.

## Compaction and accounting

Context BOTH produced one native structural `compacted` record before its third
pressure turn and then progressed one invocation farther than the other arms.
The other arms emitted no typed compaction before failure. Client usage is
session-cumulative; Context BOTH's final trustworthy completed-turn values
closely track whole-run backend totals. Failed final invocations have no
`turn.completed` usage and remain missing rather than zero.

## Disposition

The context fixed-sequence qualification gate is failed. None of these attempts
is eligible for an invisible retry. A substantive task/driver/parser correction
requires a new protocol/kit identity, while all existing attempts and evidence
remain under `.6`.
