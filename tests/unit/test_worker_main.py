import torch

from model_preflight.execution.worker_main import _find_inputs_and_target


def test_finds_feature_tensor_named_feats_in_mapping_batch() -> None:
    """Feature-extractor adapters commonly expose ``feats`` plus side inputs."""
    batch = {
        "feats": torch.randn(3, 1152),
        "metas": torch.randn(3, 12),
        "targets": torch.randn(3),
    }

    inputs, target = _find_inputs_and_target(batch)

    assert inputs is batch["feats"]
    assert target is batch["targets"]
