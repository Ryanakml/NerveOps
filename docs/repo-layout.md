# Repository layout (M0-01)

Source of truth: blueprint §§54–58, 62–64, 103, 105–106, 124.
Issue: [#1 — M0-01](https://github.com/Ryanakml/NerveOps/issues/1).
Follow-ups own their areas: [#2](https://github.com/Ryanakml/NerveOps/issues/2)
migrations/ownership, [#3](https://github.com/Ryanakml/NerveOps/issues/3) Compose
topology, [#4](https://github.com/Ryanakml/NerveOps/issues/4) test harness/CI.

## Top level

```text
apps/
  web/               # Next.js Web Product shell (@nerveops/web, :3100)
  control-plane/     # NestJS Control Plane shell (@nerveops/control-plane, :3001)
  runtime-api/       # FastAPI Investigation Runtime API shell (:8000)
  runtime-worker/    # Python runtime-worker process shell (CLI heartbeat)
  celery-worker/     # Python Celery background-worker shell (broker NOT required for --check)
docs/
  repo-layout.md     # this file
  local-shells.md    # per-shell build/start/probe commands
  config-contract.md # shared configuration NAME contract (no secrets)
  commands.md        # repository command conventions + wiring
scripts/
  check-shell-http.sh        # poll an HTTP health endpoint
  check-python-shells.py     # import + operability-shape check (no infra)
  integration-shell-check.sh # M0-01 process-level start/stop verification
tests/
  m0_01_shell_contract/      # structural acceptance tests for this issue
.env.example         # configuration NAMES only (copy to .env locally)
package.json         # npm workspaces (web, control-plane) + root command wiring
eslint.config.mjs    # root lint wiring (stable interface)
```

## Process boundaries (why five shells)

| Shell | Runtime | Default port | Owns in M0-01 | Future owner |
|---|---|---|---|---|
| `apps/web` | Next.js/React/TS | 3100 | composable page + `/api/health`, `/api/ready` | workspace UX (M3) |
| `apps/control-plane` | NestJS/TS | 3001 | `/health`, `/ready` | identity/RBAC/policy/public API (M1) |
| `apps/runtime-api` | FastAPI/Python | 8000 | `/health`, `/ready` | incidents/runs/truth/execution (M2+) |
| `apps/runtime-worker` | Python process | — (CLI) | `--check`/`--once`/heartbeat loop | durable scheduling/leases (M2) |
| `apps/celery-worker` | Celery/Python | — (CLI) | `--check`, `debug_ping` wiring | background jobs only (M4+) |

Boundaries enforce blueprint §55 (PostgreSQL runtime state wins over process
memory/Redis/MCP/traces) and INV-15 / §§62–64 (one mutable owner per domain
object) before any domain code exists. NestJS never writes runtime tables (§59).

## What is deliberately absent (non-goals)

No Prisma schema with domain tables, no SQLAlchemy models, no Alembic migrations
(#2 owns them). No `docker-compose.yml` (#3 owns it). No `.github/workflows`
(#4 owns it). No workspace/user/RBAC, catalog, policy, incident/run/step,
evidence/truth, intents/approvals/executions, Tool Gateway, RAG, LangGraph,
model inference, or product UI beyond the composable shell.
