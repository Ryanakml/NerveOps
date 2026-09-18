#!/usr/bin/env python3
"""M0-01 Python shell import/shape check (stable interface; #4 owns full harness).

Each shell is validated in an isolated subprocess so the per-shell top-level
package names (`app`, `worker`) never collide. No DB/Redis/model required.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "runtime-api": (
        "apps/runtime-api",
        "from app.main import shell_status; b=shell_status(); "
        "assert b['service']=='runtime-api' and b['status']=='ok', b; "
        "assert set(b.keys())=={'status','service','version','uptimeSeconds'}, b; "
        "print('runtime-api: import + shell_status OK')",
    ),
    "runtime-worker": (
        "apps/runtime-worker",
        "from worker.main import shell_status; b=shell_status(); "
        "assert b['service']=='runtime-worker' and b['status']=='ok', b; "
        "assert set(b.keys())=={'status','service','version','uptimeSeconds'}, b; "
        "print('runtime-worker: import + shell_status OK')",
    ),
    "celery-worker": (
        "apps/celery-worker",
        "from app.check import shell_status; b=shell_status(); "
        "assert b['service']=='celery-worker' and b['status']=='ok', b; "
        "assert set(b.keys())=={'status','service','version','uptimeSeconds'}, b; "
        "print('celery-worker: import + shell_status OK')",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=list(CHECKS.keys()))
    args = parser.parse_args()
    targets = [args.only] if args.only else list(CHECKS.keys())
    for target in targets:
        shell_dir, snippet = CHECKS[target]
        proc = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0, '{shell_dir}'); {snippet}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            print(f"{target}: CHECK FAILED", file=sys.stderr)
            return proc.returncode
    print("python shells: operability shape OK (no infra required)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
