# Investigation Runtime API shell — `apps/runtime-api`

M0-01 executable shell for the Python/FastAPI Investigation Runtime API
(blueprint §§54–55, 58, 105–106).

- Owns (future): incidents, runs, steps, scheduling, leases/fencing, evidence/truth
  revisions, Action Intents, approvals, executions, reconciliation, verification, audit.
- Contains in M0-01: role boundary + `/health` + `/ready` only. No tables, no auth,
  no scheduling, no LangGraph/RAG/tools.

## Commands

```text
pip install -r apps/runtime-api/requirements.txt
make -C apps/runtime-api build
make -C apps/runtime-api start        # uvicorn on $RUNTIME_API_PORT (default 8000)
make -C apps/runtime-api lint
make -C apps/runtime-api type-check
make -C apps/runtime-api test         # pytest shell-operability tests
```

Env names: `RUNTIME_API_PORT`, `LOG_LEVEL`, `NERVEOPS_ENV`, `NERVEOPS_SHELL_VERSION`.
See root `.env.example` and `docs/config-contract.md`.

## Probes (shell operability only, no domain data)

```text
GET /health  -> { status, service, version, uptimeSeconds }
GET /ready   -> { status, service, version, uptimeSeconds, ready: true }
```

PostgreSQL/Redis-gated readiness belongs to #2/#3; deterministic harness to #4.
