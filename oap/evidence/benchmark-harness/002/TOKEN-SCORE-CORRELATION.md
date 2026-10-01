# Partial functional score versus token/resource use — GPU2/GPU3 qualification

This is exploratory qualification evidence, not a treatment-effect estimate. Backend and client tokens overlap and are never added.

| Task | Condition | Lane | Score | Backend prompt | Backend generated | Gross tokens | Wall min | Mean GPU W | Provisional kJ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Web | BOTH | 2 | 75% | 5,241,987 | 96,771 | 5,338,758 | 22.1 | 283.4 | 375.6 |
| Web | CACHE | 2 | 75% | 6,465,565 | 124,754 | 6,590,319 | 29.2 | 282.0 | 495.4 |
| Web | CACHE | 3 | 100% | 18,492,251 | 180,295 | 18,672,546 | 63.0 | 231.5 | 888.8 |
| Web | DIRECT | 3 | 75% | 5,070,385 | 98,495 | 5,168,880 | 23.0 | 281.0 | 388.4 |
| Web | VISION | 2 | 75% | 4,114,120 | 98,760 | 4,212,880 | 23.4 | 282.2 | 397.3 |
| Terminal | BOTH | 3 | 20% | 3,507,370 | 86,508 | 3,593,878 | 20.5 | 276.5 | 341.8 |
| Terminal | CACHE | 2 | 20% | 12,843,675 | 160,876 | 13,004,551 | 55.4 | 231.3 | 780.2 |
| Terminal | DIRECT | 2 | 80% | 3,704,642 | 92,080 | 3,796,722 | 23.2 | 261.2 | 365.0 |
| Terminal | DIRECT | 3 | 20% | 8,469,519 | 129,460 | 8,598,979 | 41.1 | 243.3 | 606.4 |
| Terminal | VISION | 3 | 80% | 6,504,110 | 128,006 | 6,632,116 | 32.9 | 271.3 | 537.9 |
| Context | BOTH | 3 | 0% | 1,814,364 | 231,160 | 2,045,524 | 41.9 | 326.3 | 816.2 |
| Context | CACHE | 2 | 0% | 747,854 | 123,052 | 870,906 | 21.6 | 319.5 | 412.4 |
| Context | DIRECT | 2 | 0% | 891,646 | 121,069 | 1,012,715 | 21.4 | 319.1 | 408.7 |
| Context | VISION | 3 | 0% | 755,410 | 121,434 | 876,844 | 21.4 | 318.3 | 407.6 |

## Within-task exploratory associations

| Task | n | Mean score | Pearson(score, gross tokens) | Spearman | Pearson(score, wall time) |
|---|---:|---:|---:|---:|---:|
| Web | 5 | 80.0% | 0.990 | 0.707 | 0.987 |
| Terminal | 5 | 44.0% | -0.448 | -0.289 | -0.424 |
| Context | 4 | 0.0% | NULL | NULL | NULL |

## Interpretation

- Web shows a near-perfect positive Pearson association only because the single 100% attempt also consumed far more tokens/time than the four tied 75% attempts. With n=5, this is an outlier pattern, not evidence that spending more tokens causes success.
- Terminal shows a weak-to-moderate negative association: the two 80% attempts generally used fewer resources than several 20% attempts. Again, n=5 is too small for inference.
- Context has no score variance (all 0%), so score/resource correlation is undefined.
- Partial scores are useful secondary outcomes within task. They must not be pooled as equal raw checks across tasks or replace binary functional success post hoc.
- Energy is labeled provisional: recorder/VM clock alignment is bounded only at scrape-cadence scale, not the sub-100ms criterion required for official energy attribution.

## Recorder quality

- Samples in window: 13,622
- Median achieved interval: 0.493 s; p95 2.544 s; max 2.953 s.
- Median scrape duration: 0.800 s; p95 1.811 s; max 2.193 s.
- No scrape failures, queue waits, counter resets, GPU UUID gaps, or extra measured-GPU PIDs were observed.
- One Web DIRECT attempt missed 125,998 prompt tokens at the host sample boundary; VM counter deltas remain authoritative for attempt totals.
