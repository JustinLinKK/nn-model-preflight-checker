"""Convenience adapter composed from ordinary functions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class FunctionAdapter:
    build_model_fn: Callable[[Any], Any]
    build_optimizer_fn: Callable[[Any, Any], Any]
    build_train_batch_fn: Callable[[Any, str], Any]
    training_step_fn: Callable[[Any, Any, Any], Any]
    build_validation_batch_fn: Callable[[Any, str], Any] | None = None
    validation_step_fn: Callable[[Any, Any, Any], Any] | None = None

    def build_model(self, context: Any) -> Any:
        return self.build_model_fn(context)

    def build_optimizer(self, model: Any, context: Any) -> Any:
        return self.build_optimizer_fn(model, context)

    def build_train_batch(self, scenario: Any, device: str) -> Any:
        return self.build_train_batch_fn(scenario, device)

    def build_validation_batch(self, scenario: Any, device: str) -> Any:
        if self.build_validation_batch_fn is None:
            return self.build_train_batch(scenario, device)
        return self.build_validation_batch_fn(scenario, device)

    def training_step(self, model: Any, batch: Any, context: Any) -> Any:
        return self.training_step_fn(model, batch, context)

    def validation_step(self, model: Any, batch: Any, context: Any) -> Any:
        if self.validation_step_fn is None:
            raise NotImplementedError("validation_step was not configured")
        return self.validation_step_fn(model, batch, context)

