# Architecture

The controller loads and normalizes the manifest, hashes inputs, runs AST and target-profile
checks, dispatches isolated workers, applies policy, and serializes the report. It never imports
candidate modules.

Each construction, data, abstract, training, or validation request starts
`model_preflight.execution.worker_main` in a new process. Requests and responses use protocol
version 1 and JSON-compatible values. Candidate stdout/stderr are redirected before import.
Timeouts and resource-limit terminations become `INCONCLUSIVE`; malformed worker responses and
unexpected worker crashes become `INTERNAL_ERROR`.

The PyTorch abstract path first attempts `torch.export` when a conventional input can be
identified. Regardless of export success, meta execution checks the adapter's training path and
collects leaf-module output sizes. Unsupported abstract semantics are inconclusive. Known,
unambiguous dimension errors are confirmed failures.

The framework-facing boundaries are the candidate adapter protocol and the worker stage
handlers. A future backend can implement the same adapter/abstract-result contracts without
changing report policy.

The analytical memory estimate separates exact parameter/gradient storage from estimated
optimizer state, saved activations, and a safety margin. It always records uncertainty and never
asserts that CUDA OOM is impossible.

