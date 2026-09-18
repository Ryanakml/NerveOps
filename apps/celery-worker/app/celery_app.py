"""M0-01 celery-worker shell: Celery app boundary only (background-only).

Blueprint §§54-55, 65-68, 105-106:
- Celery is background processing only (ingestion/embeddings/reports/cleanup in later
  milestones). Celery task state is NEVER product state.
- Redis is broker/transport + disposable cache only; never authoritative for runs,
  leases, approvals, or truth.
- M0-01 contains NO real jobs, NO scheduling, NO DB writes. One `debug_ping`
  task exists only to prove the worker process boundary is wired.
"""

from __future__ import annotations

import os

from celery import Celery

SHELL_SERVICE = "celery-worker"
SHELL_VERSION = os.getenv("NERVEOPS_SHELL_VERSION", "0.1.0-m0-01")
BROKER_URL_ENV = "CELERY_BROKER_URL"
DEFAULT_BROKER_URL = "redis://localhost:6379/0"

celery = Celery(
    "nerveops_celery_shell",
    broker=os.getenv(BROKER_URL_ENV, DEFAULT_BROKER_URL),
    backend=os.getenv("CELERY_RESULT_BACKEND", "cache+memory://"),
)

# Shell-only task: proves task registration/wiring without domain semantics.
# Later milestones own real ingestion/eval/report tasks (never investigation authority).
celery.conf.update(
    task_default_queue="nerveops-shell",
    task_acks_late=False,
)


@celery.task(name="nerveops.shell.debug_ping")
def debug_ping() -> dict:
    return {"status": "ok", "service": SHELL_SERVICE, "version": SHELL_VERSION}
