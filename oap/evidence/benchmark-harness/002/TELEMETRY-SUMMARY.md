# Synchronized host telemetry summary

## Coverage

The dual-lane recorder window contained 13,622 valid samples spanning every
published workload attempt. Numeric metrics were scraped from both measured
vLLM endpoints, and GPU process/power/clock/temperature data were sampled for
the measured devices.

- Parse errors: 0.
- Endpoint scrape failures: 0.
- Counter resets: 0.
- Maximum waiting requests per lane: 0.
- Maximum running requests per lane: 1.
- Samples without exactly one expected measured-GPU process: 0.
- Samples with a missing/wrong measured GPU identity: 0.
- Stable process identity: one unchanged process per measured GPU for the full
  window.

The other two protected GPUs each had a compute process present throughout the
window. Their utilization and power time series were not included, so presence
is recorded but the magnitude of shared-host contamination cannot be inferred.

## Achieved cadence

| Metric | Median | p95 | Maximum |
|---|---:|---:|---:|
| interval between samples | 0.493 s | 2.544 s | 2.953 s |
| individual scrape duration | 0.800 s | 1.811 s | 2.193 s |

Configured cadence and achieved cadence are not treated as equivalent.

## Token reconciliation

Thirteen of fourteen attempts had exact host-versus-VM prompt-token deltas.
Web DIRECT differed by 125,998 prompt tokens at a recorder boundary; the VM
before/after snapshot is authoritative for its attempt total. Small generated-
token differences reflect the same scrape-boundary effect. There were no
counter resets or queue residue.

## Clock and energy limitation

Matching 1,358 changing vLLM counter states between independently collected
host and VM samples produced a median apparent host-minus-VM observation offset
of about 0.937 seconds and p95 about 1.943 seconds. This method is bounded by
scrape cadence and is not an independent clock-offset measurement. It does not
satisfy the required sub-100 ms criterion.

Accordingly, the per-attempt mean power and integrated energy values in
`TOKEN-SCORE-CORRELATION.md` are explicitly provisional. They are useful for
diagnosis but not for exact energy attribution or a formal efficiency claim.

## Retention boundary

After verified streaming extraction, the multi-gigabyte raw recorder copies on
the VM were deleted at human instruction to recover disk space. The private
compact derivative, summary, and per-attempt correlation were retained. This
public archive includes only the content-free summary; it excludes timestamps,
PIDs, GPU UUIDs, endpoint addresses, and raw samples.
