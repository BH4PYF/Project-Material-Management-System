"""
Test environment overrides.

The base settings already include test acceleration logic via `TESTING`.
This module exists to keep environment structure consistent and to host
future explicit test-only overrides.
"""


def apply(target):
    return target
