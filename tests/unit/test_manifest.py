from pathlib import Path

import pytest

from model_preflight.core.exceptions import ManifestError
from model_preflight.manifest import load_manifest

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_manifest_paths_are_normalized() -> None:
    manifest = load_manifest(FIXTURES / "valid.yaml")
    assert manifest.candidate.root.is_absolute()
    assert manifest.candidate.root.name == "valid_candidate"
    assert manifest.scenarios.train_batch_sizes == (2, 4, 8, 16, 32)
    assert manifest.policy.mode.value == "balanced"


def test_unknown_schema_version_is_manifest_error(tmp_path: Path) -> None:
    path = tmp_path / "preflight.yaml"
    path.write_text("schema_version: 99\n", encoding="utf-8")
    with pytest.raises(ManifestError, match="schema_version"):
        load_manifest(path)


def test_missing_candidate_is_rejected_before_execution(tmp_path: Path) -> None:
    path = tmp_path / "preflight.yaml"
    path.write_text(
        """
schema_version: 1
candidate:
  id: missing
  root: ./does-not-exist
  adapter: adapter:CandidateAdapter
task:
  name: test
scenarios:
  train_batch_sizes: [1]
target:
  profile: nvidia/a10_24gb
""",
        encoding="utf-8",
    )
    with pytest.raises(ManifestError, match="does not exist"):
        load_manifest(path)


def test_unknown_fields_are_rejected(tmp_path: Path) -> None:
    root = tmp_path / "candidate"
    root.mkdir()
    path = tmp_path / "preflight.yaml"
    path.write_text(
        f"""
schema_version: 1
candidate:
  id: invalid
  root: {root}
  adapter: adapter:CandidateAdapter
  surprise: true
task:
  name: test
scenarios:
  train_batch_sizes: [1]
target:
  profile: nvidia/a10_24gb
""",
        encoding="utf-8",
    )
    with pytest.raises(ManifestError, match="surprise"):
        load_manifest(path)

