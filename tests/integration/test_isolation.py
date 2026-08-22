from pathlib import Path

from model_preflight.api import check


def _manifest(
    tmp_path: Path,
    source: str,
    timeout: float = 4.0,
    *,
    allow_real_cpu_abstract_fallback: bool = False,
) -> Path:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "adapter.py").write_text(source, encoding="utf-8")
    manifest = tmp_path / "preflight.yaml"
    manifest.write_text(
        f"""
schema_version: 1
candidate: {{id: isolation, root: ./candidate, adapter: adapter:CandidateAdapter}}
task: {{name: test}}
scenarios: {{train_batch_sizes: [1], test_last_batch: false, run_validation: false}}
target: {{profile: nvidia/a10_24gb}}
execution:
  cpu_timeout_seconds: {timeout}
  allow_real_cpu_abstract_fallback: {str(allow_real_cpu_abstract_fallback).lower()}
  maximum_cpu_memory_mb: 4096
""",
        encoding="utf-8",
    )
    return manifest


def test_timeout_is_inconclusive(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        """
import time
time.sleep(30)
class CandidateAdapter:
    pass
""",
        timeout=1.0,
    )
    report = check(manifest, only={"construction"})
    assert report.overall_status.value == "INCONCLUSIVE"
    assert report.diagnostics[0].code == "CHK002"


def test_worker_crash_is_internal_error(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        """
import os
os._exit(17)
""",
    )
    report = check(manifest, only={"construction"})
    assert report.overall_status.value == "INTERNAL_ERROR"
    assert report.diagnostics[0].code == "CHK003"


def test_configured_real_cpu_abstract_fallback(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        """
import torch
from torch import nn

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.Linear(4, 1)
    def forward(self, value):
        if value.is_meta or type(value).__name__ == "FakeTensor":
            raise NotImplementedError("no abstract kernel")
        return self.layer(value)

class CandidateAdapter:
    def build_model(self, context):
        return Model()
    def build_optimizer(self, model, context):
        return torch.optim.SGD(model.parameters(), lr=0.1)
    def build_train_batch(self, scenario, device):
        return torch.randn(scenario["batch_size"], 4, device=device), None
    def training_step(self, model, batch, context):
        return model(batch[0]).mean()
""",
        allow_real_cpu_abstract_fallback=True,
    )
    report = check(manifest, only={"abstract_forward"})
    assert report.overall_status.value == "PASS", report.to_dict()
    scenario = report.stages[0].evidence["scenarios"][0]
    assert scenario["backend"] == "real_cpu_fallback"
