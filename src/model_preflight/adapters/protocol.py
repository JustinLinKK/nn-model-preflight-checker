"""Framework-neutral candidate adapter protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CandidateAdapter(Protocol):
    def build_model(self, context: Any) -> Any: ...

    def build_optimizer(self, model: Any, context: Any) -> Any: ...

    def build_train_batch(self, scenario: Any, device: str) -> Any: ...

    def build_validation_batch(self, scenario: Any, device: str) -> Any: ...

    def training_step(self, model: Any, batch: Any, context: Any) -> Any:
        """Return a scalar loss tensor."""
        ...

    def validation_step(self, model: Any, batch: Any, context: Any) -> Any: ...

