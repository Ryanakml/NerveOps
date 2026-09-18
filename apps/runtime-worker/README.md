# Runtime worker shell — `apps/runtime-worker`

M0-01 executable shell for the disposable runtime-worker process
(blueprint §§54–55, 58, 65–66, 105–106).

- Owns (future, M2): durable-work claiming, fenced step commits, recovery scanning.
- Contains in M0-01: process boundary + heartbeat + `--check`/`--once` only.
  No scheduling, no leases/fences, no DB writes, no LangGraph/RAG/tool calls.

## Commands

```text
pip install -r apps/runtime-worker/requirements.txt
make -C apps/runtime-worker build
make -C apps/runtime-worker start        # runs until SIGTERM/SIGINT, exits 0
python3 -m worker.main --check           # operability check (no infra needed)
python3 -m worker.main --once            # single heartbeat (test hook)
make -C apps/runtime-worker test
```

Env names: `RUNTIME_WORKER_POLL_INTERVAL_SECONDS`, `LOG_LEVEL`, `NERVEOPS_ENV`,
`NERVEOPS_SHELL_VERSION`. See root `.env.example` and `docs/config-contract.md`.

Process is disposable by design (§55): kill/restart loses no authority because no
authority exists yet. Durable scheduling belongs to M2; Compose wiring to #3.
