"""
Production environment overrides.

Use this module for explicit production-only hardening that should not
depend on `.env` defaults.
"""


def apply(target):
    # Keep behavior unchanged by default.
    # Future production-only toggles can be added here.
    return target
