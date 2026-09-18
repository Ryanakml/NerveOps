# Web Product shell — `@nerveops/web`

M0-01 executable shell for the Next.js Web Product (blueprint §§54–56, 103, 105–106).

- Owns (future): incident workspace UX, evidence/hypothesis views, approval interaction.
- Never owns: authorization, approval validity, incident truth, action state, execution authority.

## Commands

```text
npm run dev --workspace @nerveops/web      # Next.js dev on http://localhost:3100
npm run build --workspace @nerveops/web    # production build
npm run start --workspace @nerveops/web    # serve production build on :3100
npm run lint --workspace @nerveops/web
npm run type-check --workspace @nerveops/web
npm run test --workspace @nerveops/web     # vitest shell-operability tests
```

## Probes (shell operability only, no domain data)

```text
GET /api/health  -> { status, service, version, uptimeSeconds }
GET /api/ready   -> { status, service, version, uptimeSeconds, ready: true }
```

No workspace/incident/evidence/approval fields appear here by contract.
Full Compose wiring and infra readiness belong to #3; deterministic harness belongs to #4.
