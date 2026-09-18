# Control Plane shell — `@nerveops/control-plane`

M0-01 executable shell for the NestJS Control Plane (blueprint §§54–55, 57, 105–106).

- Owns (future): workspace/tenant, users/memberships/roles, catalog, integrations,
  credential references, policy definitions/versions, public REST boundary.
- Does not own: run state, leases/fences, evidence/truth revisions, action execution,
  reconciliation, verification. Never writes runtime tables (§59).

## Commands

```text
npm run build --workspace @nerveops/control-plane   # tsc -> dist/
npm run start --workspace @nerveops/control-plane   # node dist/main.js (:3001)
npm run start:dev --workspace @nerveops/control-plane
npm run lint --workspace @nerveops/control-plane
npm run type-check --workspace @nerveops/control-plane
npm run test --workspace @nerveops/control-plane    # vitest shell-operability tests
```

Env names follow the shared contract: `CONTROL_PLANE_PORT`, `WEB_BASE_URL`,
`RUNTIME_API_BASE_URL`. See root `.env.example` and `docs/config-contract.md`.

## Probes (shell operability only, no domain data)

```text
GET /health  -> { status, service, version, uptimeSeconds }
GET /ready   -> { status, service, version, uptimeSeconds, ready: true }
```

Full auth/RBAC, policy, and cross-plane commands belong to M1; Compose wiring to #3.
