# Celery worker shell — `apps/celery-worker`

M0-01 executable shell for the background Celery worker
(blueprint §§54–55, 65–68, 105–106).

- Role: background processing only (future ingestion/embeddings/reports/cleanup).
- Rule: Celery task state is NOT product state. Redis is broker/disposable cache only,
  never authoritative for runs, leases, approvals, or truth.
- Contains in M0-01: Celery app boundary + `debug_ping` wiring task + `--check` only.
  No real jobs, no scheduling, no DB writes.

## Commands

```text
pip install -r apps/celery-worker/requirements.txt
make -C apps/celery-worker build
make -C apps/celery-worker start        # requires Redis (wired fully in #3)
python3 -m app.check --check            # operability check, no broker needed
make -C apps/celery-worker test
```

Env names: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `LOG_LEVEL`,
`NERVEOPS_SHELL_VERSION`. See root `.env.example` and `docs/config-contract.md`.

Real topology, queues, and background jobs belong to #3/M4+; harness to #4.
