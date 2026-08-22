# Diagnostics

Diagnostics have stable codes, severity, stage, classification, message, scenario, evidence,
exception details, compact stack trace, and reproduction command when available.

Core codes:

| Area | Codes |
|---|---|
| Source/import | `SRC001` syntax, `SRC002` import/entry resolution |
| Device/batch | `DEV001` hard-coded CUDA, `DEV002` direct `.cuda()`, `BAT001` literal batch |
| Data/shape | `DAT001` input contract, `DAT002` target dtype, `SHP001` rank, `SHP002` matmul, `SHP003` residual/broadcast, `SHP004` reshape |
| Construction/output/loss | `CON001`, `OUT001`, `LOS001`, `VAL001`, `FIX001` |
| Autograd/optimizer | `AUT001` detached loss, `AUT002` backward, `AUT003` missing gradient, `OPT001` empty/invalid optimizer, `OPT002` foreign parameters |
| Numeric | `NUM001` non-finite loss/output, `NUM002` non-finite gradient |
| Hardware/resource | `GPU001` precision, `GPU002` architecture, `GPU003` GPU canary required, `MEM001` analytical memory risk |
| Isolation/checker | `NET001` blocked network dependency, `CHK001` unsupported/resource limit, `CHK002` timeout, `CHK003` checker failure |

`confirmed_candidate_failure`, `inconclusive`, `checker_error`, `risk`, and `informational`
classifications are intentionally separate. Timeout alone never becomes a candidate defect, and
an export/meta failure alone never hard-rejects a candidate.

