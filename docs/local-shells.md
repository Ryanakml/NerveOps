# Local shell commands (M0-01)

Fresh-checkout order: install once, then build/start each shell independently.
No database, Redis, model, or paid credential is required for any command below.
Full Compose topology belongs to #3; deterministic harness belongs to #4.

## 0. Install

```text
# Node shells (from repository root)
npm install

# Python shells (each shell is independently installable)
pip install -r apps/runtime-api/requirements.txt
pip install -r apps/runtime-worker/requirements.txt
pip install -r apps/celery-worker/requirements.txt

# Contract tests
pip install pytest httpx fastapi uvicorn celery redis
# (or: pip install -r apps/runtime-api/requirements.txt -r apps/celery-worker/requirements.txt)
```

## 1. Web Product (`apps/web`, Next.js, :3100)

```text
npm run dev --workspace @nerveops/web      # dev server
npm run build --workspace @nerveops/web    # production build
npm run start --workspace @nerveops/web    # serve build on http://localhost:3100
curl -s http://localhost:3100/api/health | jq .
curl -s http://localhost:3100/api/ready | jq .
```

## 2. Control Plane (`apps/control-plane`, NestJS, :3001)

```text
npm run build --workspace @nerveops/control-plane
npm run start --workspace @nerveops/control-plane   # node dist/main.js (:3001)
npm run start:dev --workspace @nerveops/control-plane
curl -s http://localhost:3001/health | jq .
curl -s http://localhost:3001/ready | jq .
```

Env: `CONTROL_PLANE_PORT` (default 3001), `WEB_BASE_URL` (CORS origin).

## 3. Runtime API (`apps/runtime-api`, FastAPI, :8000)

```text
make -C apps/runtime-api build
make -C apps/runtime-api start        # uvicorn on $RUNTIME_API_PORT (default 8000)
# or directly:
RUNTIME_API_PORT=8000 uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir apps/runtime-api
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/ready | jq .
```

## 4. Runtime worker (`apps/runtime-worker`, Python process)

```text
make -C apps/runtime-worker build
make -C apps/runtime-worker start     # runs until SIGTERM/SIGINT, exits 0
python3 -m worker.main --check        # operability check, no infra (run from apps/runtime-worker)
python3 -m worker.main --once         # single heartbeat (test hook)
```

Stop with `Ctrl-C` or `kill <pid>`; the shell logs `stopped cleanly` and exits 0.

## 5. Celery worker (`apps/celery-worker`, background only)

```text
make -C apps/celery-worker build
python3 -m app.check --check          # operability check, no broker (run from apps/celery-worker)
make -C apps/celery-worker start      # real worker; requires Redis (wired fully in #3)
```

`debug_ping` (`nerveops.shell.debug_ping`) proves task registration only; it is not
a product job. Celery/Redis are never authoritative (§§65–68).

## 6. All shells at once (process-level verification)

```text
npm run integration-test              # boots shells, polls probes, stops cleanly
# equivalent:
bash scripts/integration-shell-check.sh
```

Node shells are skipped with a clear message when `node_modules` is absent;
Python shells always run. Logs go to `/tmp/nw-*.log`.
