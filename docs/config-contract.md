# Shared configuration-name contract (M0-01)

Source of truth: blueprint §§54–58, 62–64, 103, 105–106, 124.
Names live in root `.env.example`. Copy to `.env` locally; **never commit `.env`**
or any secret value. This issue documents NAMES only; #2/#3 own behavior/wiring.

## Rules

1. Every name below is optional in M0-01: each shell starts on documented defaults
   with no `.env` present (local-first, zero-paid-token per §124).
2. Values containing secrets (`*_TOKEN`, `*_KEY`, `*_SECRET`, `*_URL` with credentials)
   exist as commented placeholders in `.env.example` only.
3. Cross-plane URLs are server-side names only; the browser never holds a service
   token. Internal service-auth format is UNRESOLVED per blueprint §126 — M1 owns it.
4. Adding a new shared name requires updating `.env.example` + this file + the
   owning shell README in the same change.

## Names by shell

### Web (`apps/web`)

| Name | Default | Meaning |
|---|---|---|
| `WEB_PORT` | `3100` | local port for `next dev`/`next start` |
| `CONTROL_PLANE_BASE_URL` | `http://localhost:3001` | server-side Control Plane base URL |
| `NERVEOPS_SHELL_VERSION` | `0.1.0-m0-01` | version reported by probes |

### Control Plane (`apps/control-plane`)

| Name | Default | Meaning |
|---|---|---|
| `CONTROL_PLANE_PORT` | `3001` | NestJS listen port |
| `WEB_BASE_URL` | `http://localhost:3100` | CORS origin for local web |
| `RUNTIME_API_BASE_URL` | `http://localhost:8000` | internal Runtime API base URL |
| `CONTROL_PLANE_TO_RUNTIME_TOKEN` | — (unset) | placeholder name for future M1 service auth; value never committed |

### Runtime API (`apps/runtime-api`)

| Name | Default | Meaning |
|---|---|---|
| `RUNTIME_API_PORT` | `8000` | uvicorn listen port |
| `LOG_LEVEL` | `info` | shell log verbosity |
| `NERVEOPS_ENV` | `development` | environment label in logs |
| `NERVEOPS_SHELL_VERSION` | `0.1.0-m0-01` | version reported by probes |

### Runtime worker (`apps/runtime-worker`)

| Name | Default | Meaning |
|---|---|---|
| `RUNTIME_WORKER_POLL_INTERVAL_SECONDS` | `5` | heartbeat cadence (lease tuning itself is UNRESOLVED, §126) |
| `RUNTIME_WORKER_PORT` | `8001` | reserved name for future #3 wiring; unused in M0-01 |
| `LOG_LEVEL`, `NERVEOPS_ENV`, `NERVEOPS_SHELL_VERSION` | as above | shared shell labels |

### Celery worker (`apps/celery-worker`, background only)

| Name | Default | Meaning |
|---|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | broker URL name (real Redis wired in #3) |
| `CELERY_RESULT_BACKEND` | `cache+memory://` | M0-01 shell default; never authoritative |
| `LOG_LEVEL`, `NERVEOPS_SHELL_VERSION` | as above | shared shell labels |

### Infrastructure names (reserved for #3; local-only defaults, no committed values)

`DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT_URL`, `S3_BUCKET`, `OLLAMA_BASE_URL`,
`OTEL_EXPORTER_OTLP_ENDPOINT`, `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`,
`LANGFUSE_SECRET_KEY`. Core shells MUST NOT require any of these to boot in M0-01.

## Verification

- `tests/m0_01_shell_contract/test_config_contract.py` asserts every `KEY=` name in
  `.env.example` is documented here and that no secret value is committed.
- `grep -rE '(sk-|ghp_|AKIA|BEGIN .*PRIVATE KEY|password\s*=\s*[^$])'` over the repo
  (excluding `non-published-docs/`) must return no committed credential.
