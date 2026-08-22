"""POSIX resource-limit setup for worker subprocesses."""

from __future__ import annotations

import math
import os
import resource


def apply_resource_limits(
    *,
    timeout_seconds: float,
    memory_mb: int,
    maximum_processes: int,
    maximum_output_bytes: int,
) -> None:
    cpu_seconds = max(1, math.ceil(timeout_seconds))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
    memory_bytes = memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (maximum_output_bytes, maximum_output_bytes))
    if hasattr(resource, "RLIMIT_NPROC") and os.getuid() != 0:
        resource.setrlimit(resource.RLIMIT_NPROC, (maximum_processes, maximum_processes))

