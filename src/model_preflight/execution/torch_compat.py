"""Compatibility wrappers for version-sensitive PyTorch internals."""

from __future__ import annotations

from typing import Any


def create_fake_tensor_mode() -> Any | None:
    try:
        from torch._subclasses.fake_tensor import FakeTensorMode
    except (ImportError, AttributeError):
        return None
    return FakeTensorMode(allow_non_fake_inputs=True)
