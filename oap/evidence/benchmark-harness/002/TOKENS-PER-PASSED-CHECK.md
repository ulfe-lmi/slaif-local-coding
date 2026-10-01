# Backend tokens per passed functional check

These are descriptive ratios requested during qualification, not a replacement
score or an efficiency endpoint. Checks differ in scope and difficulty, task
totals differ, failed checks also consumed tokens, and context attempts passed
zero checks (their ratio is `NULL`, not infinity or zero). Backend and client
usage overlap and are never added.

## Ordered by generated tokens per passed check

| Task | Condition | Lane | Checks | Generated/check | Prompt/check |
|---|---|---:|---:|---:|---:|
| Web | BOTH | 2 | 6/8 | 16,128.5 | 873,664.5 |
| Web | DIRECT | 3 | 6/8 | 16,415.8 | 845,064.2 |
| Web | VISION | 2 | 6/8 | 16,460.0 | 685,686.7 |
| Web | CACHE | 2 | 6/8 | 20,792.3 | 1,077,594.2 |
| Web | CACHE | 3 | 8/8 | 22,536.9 | 2,311,531.4 |
| Terminal | DIRECT | 2 | 4/5 | 23,020.0 | 926,160.5 |
| Terminal | VISION | 3 | 4/5 | 32,001.5 | 1,626,027.5 |
| Terminal | BOTH | 3 | 1/5 | 86,508.0 | 3,507,370.0 |
| Terminal | DIRECT | 3 | 1/5 | 129,460.0 | 8,469,519.0 |
| Terminal | CACHE | 2 | 1/5 | 160,876.0 | 12,843,675.0 |

## Ordered by prompt tokens per passed check

| Task | Condition | Lane | Checks | Prompt/check | Generated/check |
|---|---|---:|---:|---:|---:|
| Web | VISION | 2 | 6/8 | 685,686.7 | 16,460.0 |
| Web | DIRECT | 3 | 6/8 | 845,064.2 | 16,415.8 |
| Web | BOTH | 2 | 6/8 | 873,664.5 | 16,128.5 |
| Terminal | DIRECT | 2 | 4/5 | 926,160.5 | 23,020.0 |
| Web | CACHE | 2 | 6/8 | 1,077,594.2 | 20,792.3 |
| Terminal | VISION | 3 | 4/5 | 1,626,027.5 | 32,001.5 |
| Web | CACHE | 3 | 8/8 | 2,311,531.4 | 22,536.9 |
| Terminal | BOTH | 3 | 1/5 | 3,507,370.0 | 86,508.0 |
| Terminal | DIRECT | 3 | 1/5 | 8,469,519.0 | 129,460.0 |
| Terminal | CACHE | 2 | 1/5 | 12,843,675.0 | 160,876.0 |

All four context rows are excluded from both orderings because each passed
0/16 checks. See `PRELIMINARY-RESULTS.csv` for their nonzero token use.
