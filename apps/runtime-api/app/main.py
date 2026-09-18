"""M0-01 Investigation Runtime API shell (FastAPI).

Blueprint §§54-55, 58, 105-106: role boundary and process entrypoint only.
Owns (future): incidents, runs, steps, leases/fencing, evidence/truth revisions,
Action Intents, approvals, executions, reconciliation, verification, audit.
Contains NO M1/M2 behavior in M0-01: no tables, no scheduling, no auth, no tools.

Health/readiness are limited to shell operability; they expose no domain data
and perform no authority-changing operation.
"""

from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config import SHELL_SERVICE, SHELL_VERSION

_BOOT_TIME = time.time()

app = FastAPI(title="NerveOps Runtime API (M0-01 shell)", version=SHELL_VERSION)


def shell_status() -> dict:
    return {
        "status": "ok",
        "service": SHELL_SERVICE,
        "version": SHELL_VERSION,
        "uptimeSeconds": int(time.time() - _BOOT_TIME),
    }


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse(status_code=200, content=shell_status())


@app.get("/ready")
def ready() -> JSONResponse:
    # M0-01 readiness = shell can serve. #3 owns infra-gated readiness
    # (PostgreSQL/Redis reachable); #2 owns migration-gated readiness.
    return JSONResponse(status_code=200, content={**shell_status(), "ready": True})
