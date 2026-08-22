from pathlib import Path

import pytest

from model_preflight.api import check
from tests.mutations.cases import MUTATIONS, Mutation


def write_manifest(tmp_path: Path, mutation: Mutation) -> Path:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "adapter.py").write_text(mutation.source, encoding="utf-8")
    manifest = tmp_path / "preflight.yaml"
    manifest.write_text(
        """
schema_version: 1
candidate: {id: mutation, root: ./candidate, adapter: adapter:CandidateAdapter}
task:
  name: classification
  target_dtype: int64
  output_class_dimension: -1
  num_classes: 2
scenarios:
  train_batch_sizes: [2]
  test_last_batch: false
  run_validation: true
  input_shapes: {normal: [4]}
  precision: [fp32]
target: {profile: nvidia/a10_24gb}
execution:
  abstract_timeout_seconds: 15
  cpu_timeout_seconds: 15
  maximum_cpu_memory_mb: 4096
policy: {mode: balanced}
""",
        encoding="utf-8",
    )
    return manifest


@pytest.mark.parametrize("mutation", MUTATIONS, ids=lambda item: item.name)
def test_mutation_has_expected_confirmed_diagnostic(
    tmp_path: Path, mutation: Mutation
) -> None:
    report = check(write_manifest(tmp_path, mutation), only={mutation.stage})
    assert report.overall_status.value == "FAIL", report.to_dict()
    assert mutation.code in {item.code for item in report.diagnostics}, report.to_dict()
