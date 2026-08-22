"""PyTorch adapter loading and runtime validation (worker use only)."""

from __future__ import annotations

import importlib
import inspect
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any


def load_adapter(root: Path, entry_point: str) -> Any:
    module_name, attribute_path = entry_point.split(":", 1)
    sys.path.insert(0, str(root))
    try:
        module = importlib.import_module(module_name)
    finally:
        with suppress(ValueError):
            sys.path.remove(str(root))
    value: Any = module
    for part in attribute_path.split("."):
        value = getattr(value, part)
    if inspect.isclass(value):
        value = value()
    required = [
        "build_model",
        "build_optimizer",
        "build_train_batch",
        "training_step",
    ]
    missing = [name for name in required if not callable(getattr(value, name, None))]
    if missing:
        raise TypeError(f"adapter is missing required callable(s): {', '.join(missing)}")
    return value
