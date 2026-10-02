# Corrected GPU2/GPU3 qualification — partial functional checks

These are independent-judge functional components. They do not include blinded
web visual ratings, which remain unscored. Context uses facts correct with both
value and source; all context attempts terminated before the final query.

| Task | Condition | Lane | Subject status | Passed | Fraction | Passed checks |
|---|---|---:|---|---:|---:|---|
| Web | DIRECT | 3 | `SUBJECT_ERROR` | 6/8 | 75% | reveal/neighbors; flags; loss; restart; difficulty sizes; no browser errors |
| Web | VISION | 2 | `SUBMITTED` | 6/8 | 75% | reveal/neighbors; flags; loss; restart; difficulty sizes; no browser errors |
| Web | CACHE | 2 | `SUBJECT_ERROR` | 6/8 | 75% | reveal/neighbors; flags; loss; restart; difficulty sizes; no browser errors |
| Web | CACHE | 3 | `SUBMITTED` | 8/8 | 100% | all eight, including flood/win and randomized rule sequences |
| Web | BOTH | 2 | `SUBMITTED` | 6/8 | 75% | reveal/neighbors; flags; loss; restart; difficulty sizes; no browser errors |
| Terminal | DIRECT | 3 | `SUBMITTED` | 1/5 | 20% | quit from initial state |
| Terminal | DIRECT | 2 | `SUBMITTED` | 4/5 | 80% | movement/reveal; flags; loss/restart; quit |
| Terminal | VISION | 3 | `SUBMITTED` | 4/5 | 80% | movement/reveal; flags; loss/restart; quit |
| Terminal | CACHE | 2 | `SUBMITTED` | 1/5 | 20% | quit from initial state |
| Terminal | BOTH | 3 | `SUBMITTED` | 1/5 | 20% | quit from initial state |
| Context | DIRECT | 2 | `SUBJECT_ERROR` | 0/16 | 0% | none |
| Context | VISION | 3 | `SUBJECT_ERROR` | 0/16 | 0% | none |
| Context | CACHE | 2 | `SUBJECT_ERROR` | 0/16 | 0% | none |
| Context | BOTH | 3 | `SUBJECT_ERROR` | 0/16 | 0% | none |

## Scoring interpretation

`passed / total` is useful as a descriptive secondary score within each task.
It reveals that four web failures were 75% implementations and two terminal
failures were 80% near-misses. It must not silently replace the frozen primary
functional-success endpoint after observing these results.

Checks are not exchangeable units: randomized web sequences cover much more
behavior than “no browser errors,” and terminal checks bundle multiple actions.
Therefore, summing raw checks across tasks or treating every check as equal would
create an unjustified global score. A future formal protocol may predeclare a
task-normalized partial score (`passed/total`) and equal-weight task macro-average,
while retaining binary functional success as primary and visual quality as a
separate web outcome.

With only one attempt in most cells and unequal duplicate cells, these
qualification scores cannot estimate condition effects.
