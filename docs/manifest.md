# Manifest v1

The authoritative contract is `model_preflight/manifest/schema_v1.json`. YAML is accepted as the
wire format. Unknown fields are rejected to catch misspellings.

`candidate.root` and `task.fixture_root` resolve against the manifest's directory. `adapter` is a
required `module:attribute` entry point. `task.input_rank`, when set, excludes the batch
dimension. `task.target_dtype` enables an explicit target check rather than relying on loss
heuristics. Set `task.output_class_dimension` (often `-1` for classification/transformers or
`1` for segmentation) to enforce `num_classes` on the captured model output.

`train_batch_sizes` should contain every scheduler proposal. Abstract execution forms the cross
product of batch sizes, normal and boundary input shapes, and requested precisions. Real CPU
training uses the first normal proposal plus `last_batch_size` when `test_last_batch` is true.
The last-batch scenario is omitted when `task.drop_last` is true.

Abstract execution remains meta-only by default. `allow_real_cpu_abstract_fallback` permits a
resource-bounded real CPU forward when an operation has no meta implementation.

Built-in profile names omit `.yaml`, for example `nvidia/v100_32gb`. A relative `.yaml` path
selects a custom profile relative to the manifest.

`memory_failure_fraction` is optional. Crossing it remains an inconclusive estimate—not a
confirmed defect—but recommends blocking in balanced/strict modes.
