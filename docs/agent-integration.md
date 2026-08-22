# Agent and scheduler integration

Keep framework-specific translation outside this repository:

1. Materialize the generated candidate and a tiny task fixture.
2. Supply an explicit adapter and v1 manifest.
3. Invoke the CLI in the CPU container and persist the JSON report with node metadata.
4. Send confirmed diagnostics to the review agent and rerun after repair.
5. Limit repair attempts.
6. Admit `PASS`, reject `FAIL`, and handle `INCONCLUSIVE` according to policy with
   `GPU_CHECK_REQUIRED`.
7. Treat `INTERNAL_ERROR` as checker infrastructure failure, never model blame.
8. Run a target-GPU canary inside the eventual full allocation before expensive setup, then
   continue training in that allocation.

Pin a released commit as a submodule only after replaying the organization's historical corpus
and measuring catch rate, false hard rejection, inconclusive rate, latency, and peak CPU memory.

