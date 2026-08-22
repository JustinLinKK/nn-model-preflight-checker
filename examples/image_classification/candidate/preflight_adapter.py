"""Small end-to-end example candidate."""

import torch
from torch import nn
from torch.nn import functional as F


class CandidateAdapter:
    def build_model(self, context):
        shape = context["scenario"].get("input_shape") or [4]
        features = 1
        for value in shape:
            features *= value
        classes = context["manifest"]["task"].get("num_classes", 2)
        return nn.Sequential(
            nn.Flatten(),
            nn.Linear(features, 16),
            nn.ReLU(),
            nn.Linear(16, classes),
        )

    def build_optimizer(self, model, context):
        return torch.optim.Adam(model.parameters(), lr=1e-3)

    def build_train_batch(self, scenario, device):
        shape = scenario.get("input_shape") or [4]
        batch_size = scenario["batch_size"]
        inputs = torch.randn(batch_size, *shape, device=device)
        labels = torch.randint(0, 2, (batch_size,), device=device)
        return inputs, labels

    def build_validation_batch(self, scenario, device):
        return self.build_train_batch(scenario, device)

    def training_step(self, model, batch, context):
        inputs, labels = batch
        return F.cross_entropy(model(inputs), labels)

    def validation_step(self, model, batch, context):
        inputs, _ = batch
        return model(inputs)
