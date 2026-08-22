"""Stack-trace normalization helpers."""

import re


def compact_stacktrace(value: str, maximum_characters: int = 8000) -> str:
    value = re.sub(r"\x1b\[[0-9;]*m", "", value)
    value = value.strip()
    if len(value) <= maximum_characters:
        return value
    return value[-maximum_characters:]

