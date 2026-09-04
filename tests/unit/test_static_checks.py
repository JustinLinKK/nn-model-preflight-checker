from pathlib import Path

from model_preflight.checks.source import run_static_checks
from model_preflight.manifest import load_manifest


def _manifest(tmp_path: Path, source: str):
    root = tmp_path / "candidate"
    root.mkdir()
    (root / "adapter.py").write_text(source, encoding="utf-8")
    path = tmp_path / "preflight.yaml"
    path.write_text(
        """
schema_version: 1
candidate: {id: static, root: ./candidate, adapter: adapter:CandidateAdapter}
task: {name: test}
scenarios: {train_batch_sizes: [8]}
target: {profile: nvidia/a10_24gb}
""",
        encoding="utf-8",
    )
    return load_manifest(path)


def test_static_cuda_and_batch_findings(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        """
class CandidateAdapter:
    def build_model(self, context):
        value = tensor.cuda()
        return value.reshape(8, -1)
""",
    )
    result = run_static_checks(manifest)
    assert {item.code for item in result.diagnostics} == {"DEV002", "BAT001"}


def test_static_rejects_nonexistent_torch_backends_cuda_is_available(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        """
import torch

def configure_tf32():
    if torch.backends.cuda.is_available():
        return True
    return False

class CandidateAdapter:
    pass
""",
    )
    result = run_static_checks(manifest)
    assert result.status.value == "FAIL"
    assert any(item.code == "SRC_TORCH_API001" for item in result.diagnostics)


def test_static_rejects_cuda_transfer_inside_multiprocess_dataloader_collate(
    tmp_path: Path,
) -> None:
    manifest = _manifest(
        tmp_path,
        """
import torch
from torch.utils.data import DataLoader

NUM_WORKERS = 4

def collate(samples, device):
    return torch.stack(samples).to(device)

def make_loader(dataset, device):
    return DataLoader(
        dataset,
        num_workers=NUM_WORKERS,
        collate_fn=lambda samples: collate(samples, device),
    )

class CandidateAdapter:
    pass
""",
    )
    result = run_static_checks(manifest)
    assert result.status.value == "FAIL"
    assert any(item.code == "SRC_DATALOADER_CUDA001" for item in result.diagnostics)


def test_syntax_error_is_confirmed(tmp_path: Path) -> None:
    result = run_static_checks(_manifest(tmp_path, "class CandidateAdapter(:\n"))
    assert result.status.value == "FAIL"
    assert result.diagnostics[0].code == "SRC001"
