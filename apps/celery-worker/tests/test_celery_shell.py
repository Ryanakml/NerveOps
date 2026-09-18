"""M0-01 celery-worker shell-operability tests (no domain behavior)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = [
    "workspace",
    "incident",
    "hypothesis",
    "evidence",
    "approval",
    "intent",
    "execution",
    "lease",
    "policy",
]


def test_celery_app_wiring_without_broker():
    from app.celery_app import SHELL_SERVICE, celery, debug_ping

    assert SHELL_SERVICE == "celery-worker"
    assert "nerveops.shell.debug_ping" in celery.tasks
    # Calling the task function directly must not require a broker.
    body = debug_ping.run() if hasattr(debug_ping, "run") else debug_ping()
    assert body["status"] == "ok"
    assert body["service"] == "celery-worker"


def test_check_cli_exits_zero_without_broker():
    proc = subprocess.run(
        [sys.executable, "-m", "app.check", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert body["status"] == "ok"
    assert body["service"] == "celery-worker"
    assert isinstance(body["version"], str)


def test_no_domain_fields_leak():
    from app.check import shell_status

    raw = json.dumps(shell_status()).lower()
    for term in FORBIDDEN:
        assert term not in raw
