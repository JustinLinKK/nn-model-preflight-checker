from pathlib import Path

from model_preflight.checks.hardware import load_profile, run_hardware_checks
from model_preflight.manifest import load_manifest


def test_v100_rejects_bfloat16(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "adapter.py").write_text("class CandidateAdapter: pass\n", encoding="utf-8")
    path = tmp_path / "preflight.yaml"
    path.write_text(
        """
schema_version: 1
candidate: {id: bf16, root: ./candidate, adapter: adapter:CandidateAdapter}
task: {name: test}
scenarios:
  train_batch_sizes: [1]
  precision: [bf16]
target: {profile: nvidia/v100_32gb}
""",
        encoding="utf-8",
    )
    manifest = load_manifest(path)
    result = run_hardware_checks(manifest, load_profile(manifest))
    assert result.status.value == "FAIL"
    assert result.diagnostics[0].code == "GPU001"


def test_a100_80gb_profile_reports_its_real_memory_capacity(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "adapter.py").write_text("class CandidateAdapter: pass\n", encoding="utf-8")
    path = tmp_path / "preflight.yaml"
    path.write_text(
        """
schema_version: 1
candidate: {id: a100-80, root: ./candidate, adapter: adapter:CandidateAdapter}
task: {name: test}
scenarios:
  train_batch_sizes: [1]
  precision: [tf32]
target: {profile: nvidia/a100_80gb}
""",
        encoding="utf-8",
    )

    profile = load_profile(load_manifest(path))

    assert profile["name"] == "A100-80GB"
    assert profile["vram_bytes"] == 85899345920
