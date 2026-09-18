"""M0-01 shared shell configuration (names only, no secrets).

Blueprint §§54-55, 57-58, 103-106, 124. Values come from the environment;
see root `.env.example` and `docs/config-contract.md`.
"""

from __future__ import annotations

import os


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


RUNTIME_API_PORT: int = _int("RUNTIME_API_PORT", 8000)
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
NERVEOPS_ENV: str = os.getenv("NERVEOPS_ENV", "development")
SHELL_VERSION: str = os.getenv("NERVEOPS_SHELL_VERSION", "0.1.0-m0-01")
SHELL_SERVICE: str = "runtime-api"
