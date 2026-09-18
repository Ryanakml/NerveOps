"""M0-01 celery-worker operability entrypoint.

- `python -m app.check --check` imports the Celery app and reports shell-only JSON
  WITHOUT requiring a live Redis broker (shell operability only).
- Real `celery worker` startup (requiring Redis) belongs to #3 topology; this shell
  only proves the process/task boundary is correctly wired.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

_BOOT_TIME = time.time()


def shell_status() -> dict:
    from .celery_app import SHELL_SERVICE, SHELL_VERSION

    return {
        "status": "ok",
        "service": SHELL_SERVICE,
        "version": SHELL_VERSION,
        "uptimeSeconds": int(time.time() - _BOOT_TIME),
    }


def check() -> dict:
    # Import proves wiring; do NOT connect to broker here.
    from . import celery_app  # noqa: F401

    status = shell_status()
    # Prove the shell task is registered without dispatching it.
    assert "nerveops.shell.debug_ping" in celery_app.celery.tasks
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NerveOps celery-worker shell (M0-01)")
    parser.add_argument("--check", action="store_true", help="operability check only")
    parser.add_argument("--once", action="store_true", help="alias for --check (test hook)")
    args = parser.parse_args(argv)
    if args.check or args.once or True:
        print(json.dumps(check()), flush=True)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
