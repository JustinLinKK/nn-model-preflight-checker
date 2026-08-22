import torch
from torch import nn
from torch.nn import functional as F


class CandidateAdapter:
    def build_model(self, context):
        return nn.Linear(4, 2)

    def build_optimizer(self, model, context):
        return torch.optim.SGD(model.parameters(), lr=0.1)

    def build_train_batch(self, scenario, device):
        size = scenario["batch_size"]
        return torch.randn(size, 4, device=device), torch.randint(0, 2, (size,), device=device)

    def build_validation_batch(self, scenario, device):
        return self.build_train_batch(scenario, device)

    def training_step(self, model, batch, context):
        inputs, target = batch
        return F.cross_entropy(model(inputs), target)

    def validation_step(self, model, batch, context):
        inputs, _ = batch
        return model(inputs)

