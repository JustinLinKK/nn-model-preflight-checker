# Implementation status against the plan

The repository implements the standalone v1 foundation and runnable checker. This file keeps
release-gate claims separate from implemented capabilities.

| Plan phase | Status | Evidence / limitation |
|---|---|---|
| 0: taxonomy and corpus | Partial | Stable taxonomy and 12 labeled mutation cases exist. No historical MLEvolve artifacts were present, so historical replay metrics remain a release gate. |
| 1: foundation and schemas | Implemented | Installable `src` package, manifest/report/profile schemas, CLI/API, deterministic serialization, exit codes, Ruff, mypy, pytest. |
| 2: isolated workers | Implemented | Fresh process per runtime stage, JSON protocol, process groups, time/CPU/address-space/PID/output limits, captured logs, offline environment, non-root CPU container. External container controls remain required for hostile native code. |
| 3: static checks | Implemented | Syntax, entry/relative import resolution, CUDA devices/branches/streams, batch literals, distributed/GPU libraries, and extension compilation findings. |
| 4: adapter and construction | Implemented | Protocol/function adapter, worker-only import, model/parameter/optimizer ownership validation, meta construction. |
| 5: task/data contract | Implemented | Real adapter batch path, recursive batch evidence, explicit input-rank and target-dtype checks, normal/final batch scenarios. Task-specific masks/lengths remain the adapter/loss contract unless an integration adds explicit fields. |
| 6: CPU micro-training | Implemented | Finite scalar loss, output class contract, anomaly-enabled backward, required and finite gradients, optimizer step, optional second step, validation path. |
| 7: abstract execution | Implemented | `torch.export`, meta, wrapped FakeTensor, optional bounded real-CPU fallback, full scenario matrix, operation error normalization, activation evidence. |
| 8: GPU profiles | Implemented | Versioned V100-16/32, A10-24, and A100-40 profiles with dtype rejection and GPU-canary markers. |
| 9: resource estimate | Implemented | Exact parameter/gradient bytes and labeled optimizer/activation/margin estimates with uncertainty. |
| 10: reports/cache | Implemented | JSON/text/JUnit, reproduction commands, content-addressed opt-in cache keyed by candidate, fixture, manifest, checker, PyTorch, profile, and selected stages. |
| 11: evaluation/hardening | Partial | Unit, integration, isolation, and mutation tests plus a historical-corpus evaluator. The broader model zoo, real historical measurements, and GPU queue-hour metrics require external artifacts/infrastructure. |
| 12: release | Partial | README, docs, CI, sdist/wheel, CPU and optional CUDA-build Dockerfiles exist. Tagging is intentionally deferred until historical replay. |

The checker does not include MLEvolve integration code, auto-repair, GPU emulation, or a
target-GPU canary, matching the standalone boundary and v1 non-goals.
