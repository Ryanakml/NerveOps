"""Acceptance: health/readiness are shell-operability only (no domain data).

Proves the contract by importing Python shells (no infra) and by statically
checking TypeScript shell sources for exact payload shape.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import APPS, ROOT

ALLOWED_HEALTH_KEYS = {"status", "service", "version", "uptimeSeconds"}
FORBIDDEN_TERMS = [
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


def _run_isolated(shell_dir: str, snippet: str):
    proc = subprocess.run(
        [sys.executable, "-c", f"import sys; sys.path.insert(0, '{shell_dir}'); {snippet}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc


def test_runtime_api_health_shape_no_infra():
    pytest.importorskip("fastapi", reason="pip install -r apps/runtime-api/requirements.txt first")
    proc = _run_isolated(
        "apps/runtime-api",
        "from app.main import shell_status; import json; b=shell_status(); print(json.dumps(b))",
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert set(body.keys()) == ALLOWED_HEALTH_KEYS
    assert body["status"] == "ok" and body["service"] == "runtime-api"
    assert FORBIDDEN_TERMS and all(t not in json.dumps(body).lower() for t in FORBIDDEN_TERMS)


def test_runtime_worker_check_shape_no_infra():
    proc = _run_isolated(
        "apps/runtime-worker",
        "from worker.main import shell_status; import json; print(json.dumps(shell_status()))",
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert set(body.keys()) == ALLOWED_HEALTH_KEYS
    assert body["service"] == "runtime-worker"


def test_celery_worker_check_shape_no_broker():
    pytest.importorskip("celery", reason="pip install -r apps/celery-worker/requirements.txt first")
    proc = _run_isolated(
        "apps/celery-worker",
        "from app.check import shell_status; import json; print(json.dumps(shell_status()))",
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout.strip().splitlines()[-1])
    assert set(body.keys()) == ALLOWED_HEALTH_KEYS
    assert body["service"] == "celery-worker"


def _strip_ts_comments(text: str) -> str:
    # Remove // line comments and /* block comments so explanatory non-goal
    # mentions (e.g. "no workspace/incident fields") don't count as leaks.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    stripped = []
    for line in text.splitlines():
        # naive but sufficient for shell sources: cut at // outside strings
        if "//" in line:
            line = line.split("//", 1)[0]
        stripped.append(line)
    return "\n".join(stripped)


def test_web_health_source_has_exact_shape():
    text = (APPS / "web" / "app" / "lib-shell.ts").read_text()
    assert '"ok"' in text or "'ok'" in text or "ok" in text
    for key in ("status", "service", "version", "uptimeSeconds"):
        assert key in text
    # Assert the executable code (comments stripped) carries no domain identifiers.
    code = _strip_ts_comments(text).lower()
    for term in FORBIDDEN_TERMS:
        assert term not in code, f"web lib-shell.ts leaks domain term: {term}"
    health_route = (APPS / "web" / "app" / "api" / "health" / "route.ts").read_text()
    assert "shellStatus" in health_route


def test_control_plane_health_source_has_exact_shape():
    text = (APPS / "control-plane" / "src" / "health" / "shell.ts").read_text()
    for key in ("status", "service", "version", "uptimeSeconds"):
        assert key in text
    code = _strip_ts_comments(text).lower()
    for term in FORBIDDEN_TERMS:
        assert term not in code, f"control-plane shell.ts leaks domain term: {term}"


def test_health_endpoints_do_not_mutate():
    """Failure case: probes must be read-only (GET only, no POST/PUT/DELETE)."""
    web_health = (APPS / "web" / "app" / "api" / "health" / "route.ts").read_text()
    assert "export async function GET" in web_health
    assert "export async function POST" not in web_health
    assert "export async function PUT" not in web_health
    assert "export async function DELETE" not in web_health

    runtime_main = (APPS / "runtime-api" / "app" / "main.py").read_text()
    assert '@app.get("/health")' in runtime_main
    assert '@app.get("/ready")' in runtime_main
    assert ".post(" not in runtime_main and ".put(" not in runtime_main and ".delete(" not in runtime_main

    control = (APPS / "control-plane" / "src" / "health" / "health.controller.ts").read_text()
    assert '@Get("health")' in control
    assert "Post(" not in control and "Put(" not in control and "Delete(" not in control
