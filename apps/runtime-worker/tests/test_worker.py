"""M0-01 runtime-worker shell-operability tests (no domain behavior)."""

import json
import subprocess
import sys
from pathlib import Path

from worker.main import heartbeat_once, shell_status

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


def test_status_shape_only_operability():
    body = shell_status()
    assert body["status"] == "ok"
    assert body["service"] == "runtime-worker"
    assert isinstance(body["version"], str)
    assert isinstance(body["uptimeSeconds"], int)
    assert sorted(body.keys()) == ["service", "status", "uptimeSeconds", "version"]


def test_no_domain_fields_leak():
    raw = json.dumps(shell_status()).lower()
    for term in FORBIDDEN:
        assert term not in raw


def test_check_exits_zero_with_shell_json():
    proc = subprocess.run(
        [sys.executable, "-m", "worker.main", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert body["status"] == "ok"
    assert body["service"] == "runtime-worker"


def test_once_runs_single_heartbeat():
    proc = subprocess.run(
        [sys.executable, "-m", "worker.main", "--once"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert body.get("heartbeat") is True
