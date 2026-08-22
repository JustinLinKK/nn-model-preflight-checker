"""Minimal mutation fixtures and their ground-truth diagnostic codes."""

from __future__ import annotations

from typing import NamedTuple


class Mutation(NamedTuple):
    name: str
    stage: str
    code: str
    source: str


def adapter(
    *,
    model: str = "nn.Linear(4, 2)",
    batch: str = (
        "return (torch.randn(size, 4, device=device), "
        "torch.randint(0, 2, (size,), device=device))"
    ),
    loss: str = "return F.cross_entropy(model(inputs), target)",
    optimizer: str = "return torch.optim.SGD(model.parameters(), lr=0.1)",
    validation: str = "return model(inputs)",
    extra: str = "",
    required: str = "",
) -> str:
    return f"""
import torch
from torch import nn
from torch.nn import functional as F

{extra}

class CandidateAdapter:
    def build_model(self, context):
        return {model}

    def build_optimizer(self, model, context):
        {optimizer}

    def build_train_batch(self, scenario, device):
        size = scenario["batch_size"]
        {batch}

    def build_validation_batch(self, scenario, device):
        return self.build_train_batch(scenario, device)

    def training_step(self, model, batch, context):
        inputs, target = batch
        {loss}

    def validation_step(self, model, batch, context):
        inputs, target = batch
        {validation}

    {required}
"""


MUTATIONS = [
    Mutation(
        "incorrect_linear_in_features",
        "abstract_forward",
        "SHP002",
        adapter(model="nn.Linear(5, 2)"),
    ),
    Mutation(
        "incorrect_convolution_channels",
        "abstract_forward",
        "DAT001",
        adapter(
            model="nn.Conv2d(1, 2, 3)",
            batch=(
                "return (torch.randn(size, 3, 8, 8, device=device), "
                "torch.zeros(size, dtype=torch.long, device=device))"
            ),
            loss="return model(inputs).mean()",
        ),
    ),
    Mutation(
        "invalid_residual_addition",
        "abstract_forward",
        "SHP003",
        adapter(
            model="Residual()",
            loss="return model(inputs).sum()",
            extra="""
class Residual(nn.Module):
    def __init__(self):
        super().__init__()
        self.projection = nn.Linear(4, 3)
    def forward(self, value):
        return value + self.projection(value)
""",
        ),
    ),
    Mutation(
        "invalid_reshape",
        "abstract_forward",
        "SHP004",
        adapter(
            model="BadReshape()",
            loss="return model(inputs).sum()",
            extra="""
class BadReshape(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(()))
    def forward(self, value):
        return value.reshape(value.shape[0], 5) * self.weight
""",
        ),
    ),
    Mutation(
        "detached_loss",
        "cpu_training",
        "AUT001",
        adapter(loss="return F.cross_entropy(model(inputs), target).detach()"),
    ),
    Mutation(
        "vector_loss",
        "cpu_training",
        "LOS001",
        adapter(loss="return F.cross_entropy(model(inputs), target, reduction='none')"),
    ),
    Mutation(
        "non_finite_loss",
        "cpu_training",
        "NUM001",
        adapter(
            loss=(
                "return model(inputs).sum() * "
                "torch.tensor(float('nan'), device=inputs.device)"
            )
        ),
    ),
    Mutation(
        "wrong_target_dtype",
        "data_contract",
        "DAT002",
        adapter(
            batch=(
                "return (torch.randn(size, 4, device=device), "
                "torch.zeros(size, dtype=torch.float32, device=device))"
            )
        ),
    ),
    Mutation(
        "output_class_mismatch",
        "cpu_training",
        "OUT001",
        adapter(model="nn.Linear(4, 3)"),
    ),
    Mutation(
        "empty_optimizer",
        "construction",
        "OPT001",
        adapter(optimizer="return torch.optim.SGD([], lr=0.1)"),
    ),
    Mutation(
        "validation_only_failure",
        "validation",
        "VAL001",
        adapter(validation="raise RuntimeError('validation path failed')"),
    ),
    Mutation(
        "missing_required_gradient",
        "cpu_training",
        "AUT003",
        adapter(
            model="TwoHeads()",
            loss="return F.cross_entropy(model.first(inputs), target)",
            extra="""
class TwoHeads(nn.Module):
    def __init__(self):
        super().__init__()
        self.first = nn.Linear(4, 2)
        self.second = nn.Linear(4, 2)
    def forward(self, value):
        return self.first(value)
""",
            required=(
                "def required_gradient_names(self, model):\n"
                "        return {'first.weight', 'second.weight'}"
            ),
        ),
    ),
]
