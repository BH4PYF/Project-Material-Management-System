"""
Development environment overrides.

This module is intentionally lightweight: it only applies additive
development tweaks so existing defaults in `settings.py` remain valid.
"""


def apply(target):
    # Development-only knobs can be centralized here over time.
    # Keep behavior unchanged for now.
    return target
