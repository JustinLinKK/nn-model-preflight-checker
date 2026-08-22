from pathlib import Path

from model_preflight.cli import main

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_valid_candidate_passes_runtime_and_writes_report(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    exit_code = main(
        [
            "check",
            str(FIXTURES / "valid.yaml"),
            "--only",
            "construction",
            "--only",
            "data_contract",
            "--only",
            "cpu_training",
            "--only",
            "validation",
            "--report",
            str(report),
        ]
    )
    assert exit_code == 0
    assert '"overall_status": "PASS"' in report.read_text(encoding="utf-8")


def test_detached_loss_is_confirmed_failure(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    exit_code = main(
        [
            "check",
            str(FIXTURES / "broken.yaml"),
            "--only",
            "cpu_training",
            "--report",
            str(report),
        ]
    )
    assert exit_code == 10
    assert '"code": "AUT001"' in report.read_text(encoding="utf-8")


def test_invalid_manifest_never_imports_candidate(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    marker = tmp_path / "imported"
    (candidate / "adapter.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "preflight.yaml"
    manifest.write_text(
        """
schema_version: 2
candidate: {id: bad, root: ./candidate, adapter: adapter:CandidateAdapter}
task: {name: test}
scenarios: {train_batch_sizes: [1]}
target: {profile: nvidia/a10_24gb}
""",
        encoding="utf-8",
    )
    assert main(["check", str(manifest)]) == 30
    assert not marker.exists()

