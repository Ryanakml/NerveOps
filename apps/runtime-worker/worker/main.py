"""M0-01 runtime-worker shell.

Blueprint §§54-55, 58, 65-66: disposable runtime-worker role boundary only.
Future owner of durable-work claiming (M2). In M0-01 it performs NO scheduling,
NO lease/fencing, NO step commits, NO LangGraph/RAG/tool calls, NO DB writes.

Operability contract:
- `python -m worker.main --check` exits 0 with shell-only JSON (no domain data).
- `python -m worker.main --once` runs one heartbeat iteration (test hook).
- `python -m worker.main` runs until SIGTERM/SIGINT and exits 0 (clean stop).
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time

from .config import POLL_INTERVAL_SECONDS, SHELL_SERVICE, SHELL_VERSION

_BOOT_TIME = time.time()
_SHUTDOWN = False


def shell_status() -> dict:
    return {
        "status": "ok",
        "service": SHELL_SERVICE,
        "version": SHELL_VERSION,
        "uptimeSeconds": int(time.time() - _BOOT_TIME),
    }


def _handle_signal(_signum, _frame) -> None:
    global _SHUTDOWN
    _SHUTDOWN = True


def heartbeat_once() -> dict:
    """One disposable heartbeat iteration. No state commit in M0-01."""
    status = shell_status()
    print(json.dumps({**status, "heartbeat": True}), flush=True)
    return status


def run_forever(poll_interval: int = POLL_INTERVAL_SECONDS) -> int:
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    print(
        json.dumps({**shell_status(), "msg": "runtime-worker shell started"}),
        flush=True,
    )
    while not _SHUTDOWN:
        heartbeat_once()
        # Sleep in small slices so SIGTERM stops promptly.
        for _ in range(max(1, poll_interval * 10)):
            if _SHUTDOWN:
                break
            time.sleep(0.1)
    print(
        json.dumps({**shell_status(), "msg": "runtime-worker shell stopped cleanly"}),
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NerveOps runtime-worker shell (M0-01)")
    parser.add_argument("--check", action="store_true", help="operability check only")
    parser.add_argument("--once", action="store_true", help="single heartbeat then exit")
    args = parser.parse_args(argv)
    if args.check:
        print(json.dumps(shell_status()), flush=True)
        return 0
    if args.once:
        heartbeat_once()
        return 0
    return run_forever()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
