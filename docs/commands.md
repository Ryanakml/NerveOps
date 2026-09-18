# Repository command conventions (M0-01 owns wiring; #4 owns harness proof)

This issue establishes the STABLE INTERFACES below. Every shell implements the
same five verbs with runtime-appropriate mechanisms. #4 implements and proves the
deterministic harness (fakes, fixtures, CI) behind these names without renaming them.

## The five verbs

| Verb | Meaning | JS mechanism | Python mechanism |
|---|---|---|---|
| `lint` | static style/syntax check | `eslint` | `python -m py_compile` (ruff/mypy arrive in #4/later) |
| `type-check` | type/shape validation | `tsc --noEmit` | `scripts/check-python-shells.py` (import + operability shape, no infra) |
| `test` | fast shell/unit tests | `vitest run` | `pytest` |
| `integration-test` | process-level boot/probe/stop | `scripts/check-shell-http.sh` per shell | CLI `--check` + uvicorn boot via `scripts/integration-shell-check.sh` |
| `build` | producible artifact | `next build` / `tsc` | `pip install -r requirements.txt` + `compileall` |

## Repository-level entrypoints (run from root)

```text
npm run lint               # eslint apps/web apps/control-plane
npm run type-check         # tsc (both TS shells) + check-python-shells.py
npm run test               # vitest (both TS shells, if present) + pytest tests/m0_01_shell_contract
npm run integration-test   # bash scripts/integration-shell-check.sh
npm run build              # next build + tsc + python compileall
```

## Per-shell entrypoints

```text
# TypeScript shells (npm workspaces)
npm run <verb> --workspace @nerveops/web
npm run <verb> --workspace @nerveops/control-plane

# Python shells (make targets mirror the same verbs)
make -C apps/runtime-api <verb>        # verbs: build start lint type-check test integration-test
make -C apps/runtime-worker <verb>
make -C apps/celery-worker <verb>
```

## Ownership rules

1. #1 owns these NAMES and the wiring above. Later issues MUST extend the existing
   harnesses behind them, not introduce parallel `test2`/`ci-test` entrypoints.
2. #2 owns migration/reset commands (`db:migrate`, `db:reset` arrive in #2, not here).
3. #3 owns `docker compose up` and infra readiness gates (not here).
4. #4 owns FakeLLM/fake-provider seams, ephemeral fixtures, Playwright scaffolding,
   and `.github/workflows` (not here). Model-quality/DeepEval suites are explicitly
   excluded from M0 PR checks per #4.
5. `integration-test` in M0-01 proves shells start/stop and probes respond; it does
   NOT prove tenant isolation, crash safety, or runtime correctness (Gates A–D).
