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


def test_syntax_error_is_confirmed(tmp_path: Path) -> None:
    result = run_static_checks(_manifest(tmp_path, "class CandidateAdapter(:\n"))
    assert result.status.value == "FAIL"
    assert result.diagnostics[0].code == "SRC001"

