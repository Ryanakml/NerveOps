"""M0-01 runtime-worker shell configuration (names only, no secrets)."""

from __future__ import annotations

import os


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


SHELL_SERVICE = "runtime-worker"
SHELL_VERSION = os.getenv("NERVEOPS_SHELL_VERSION", "0.1.0-m0-01")
POLL_INTERVAL_SECONDS = _int("RUNTIME_WORKER_POLL_INTERVAL_SECONDS", 5)
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
NERVEOPS_ENV = os.getenv("NERVEOPS_ENV", "development")
