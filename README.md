# NerveOps — Evidence-Driven Incident Investigation & Controlled Remediation

> **Status:** Design frozen, implementation not started. This repo currently contains planning artifacts only — no runnable application yet.
>
> **Tagline:** AI investigates. NerveOps authorizes, executes safely, and proves what happened.

NerveOps is an **evidence-driven production incident investigation and controlled remediation platform** for engineering teams.

It sits above the systems teams already own — telemetry, logs, deployments, Git, runbooks, databases, external providers — and turns scattered signals into a defensible explanation plus a safe next action.

The core loop:

```text
incident detected
  → collect evidence
  → form competing hypotheses
  → test / reject hypotheses
  → produce evidence-backed findings
  → identify likely causal explanation
  → propose bounded remediation
  → policy + human approval
  → execute exact approved action
  → verify whether the incident actually recovered
  → resolve or reopen
```

Central principle:

> **AI may reason, propose, and investigate; NerveOps owns authority, state transitions, approvals, execution safety, reconciliation, and truth history.**

---

## Why NerveOps exists

Production incidents are rarely hard because there is zero information. They are hard because relevant information is scattered across:

```text
alerts, metrics, logs, traces
recent deployments, Git commits / PRs
runbooks, historical incidents
database diagnostics, provider status
```

Engineers manually correlate all of this under pressure. That causes slow diagnosis, confirmation bias, risky remediation, and poor learning from previous incidents.

NerveOps exists to reduce the time and cognitive load required to go from scattered evidence to:

```text
What happened?
What evidence supports that?
What alternatives were considered?
What remains uncertain?
What should we do next — and is that action allowed?
Did the fix actually work?
```

---

## What NerveOps is / is not

**NerveOps is:**

An evidence-driven investigator that connects existing engineering systems, accelerates diagnosis, proposes bounded remediation, requires explicit authority for production changes, and verifies recovery.

**NerveOps is not:**

- a metrics/log storage platform or Datadog/Prometheus replacement
- an on-call scheduler
- a generic chatbot, agent builder, or workflow builder
- a code-generation agent
- a Kubernetes manager or full incident-collaboration suite
- a generic anomaly detector
- an unrestricted production shell or autonomous production operator

Initial non-goals include fully autonomous production mutations, arbitrary shell/SQL, destructive DB operations, credential/IAM mutation, multi-agent swarms, enterprise SSO, billing, and mobile apps.

---

## Canonical example

One reproducible reference scenario anchors the whole design — a fictional ecommerce stack (`checkout-api`, `payments-api`, PostgreSQL, payment-provider-stub, Git, deployments, telemetry, runbooks).

Seeded fault:

```text
14:31  payments-api v17 deployed
       DB connection pool 40 → 8
14:34  DB pool saturation increases
14:35  connection wait rises, latency rises
14:36  PoolTimeout errors rise
14:37  payment failures rise, checkout conversion drops

Meanwhile: CPU normal, memory normal, external provider healthy
```

Initial hypotheses:

```text
H1 external provider outage
H2 CPU / resource saturation
H3 database connectivity / pool problem
H4 deployment regression
```

Expected outcome: H1/H2 rejected, H3 strongly supported, H4 strongly supported as causal explanation.

NerveOps proposes:

```text
rollback payments-api v17 → v16 (production)
```

Human approval is required. After execution NerveOps verifies `5xx ↓, pool waiters ↓, latency ↓, payment success ↑`. Only then can truth advance toward confirmed root cause.

This single scenario exercises incident creation, evidence collection, truth reasoning, exact action proposal, policy enforcement, approval, real side effect, crash-safe handling, verification, truth revision, and auditability.

---

## Core design ideas

### 1. Observation ≠ inference

NerveOps never presents an inference as an observation, or a supported hypothesis as a confirmed fact.

```text
Observation
  → Evidence (SUPPORTS / CONTRADICTS / CONTEXT, relative to a claim)
  → Hypothesis (competing alternatives maintained)
  → Supported Hypothesis
  → Finding (inspectable, evidence-backed)
  → Likely Root Cause (temporal fit + mechanism + symptom coverage + weakened alternatives)
  → Confirmed Root Cause (remediation+recovery, reproduction, authoritative confirmation, or controlled intervention)
```

No `root cause confidence: 94%`. NerveOps uses semantic states (`supported`, `strongly supported`, `likely`, `confirmed`) and always shows supporting/contradictory evidence, unknowns, provenance, and what would change the conclusion. Unknown is not negative evidence. Contradictions stay visible. Truth is revisable — history is never rewritten.

### 2. Durable state wins

No worker, HTTP request, browser, LangGraph checkpoint, Celery task, Redis key, or observability trace owns an investigation. **PostgreSQL-backed runtime state is the authority.** Processes are disposable actors with temporary leases + fencing generations. Stale writers are rejected transactionally. Restart resumes from committed state, never from memory.

Three lifecycles stay separate:

- **User lifecycle (UX):** `OPEN → INVESTIGATING → AWAITING_APPROVAL → REMEDIATING → VERIFYING → RESOLVED`
- **Execution lifecycle (correctness):** runs, steps, leases, action attempts, reconciliation, verification work
- **Truth lifecycle (epistemics):** hypothesis → finding → likely → confirmed / rejected / revised

### 3. Approval binds to an exact intent

An **Action Intent** is immutable: tool capability + version, target identity, environment, normalized payload + digest, truth/evidence revisions, policy version, preconditions, validity window.

Approval means *“this actor approved this exact intent at this time”* — not similar future actions. Before dispatch the runtime revalidates intent freshness, payload digest, target, tool version, current policy, integration/credential scope, and duplicate execution. Sensitive execution also requires a short-lived Control Plane execution grant. If policy is unavailable: fail closed.

### 4. Ambiguous side effects are first-class

NerveOps does not claim generic exactly-once external mutations. Tools are classified:

```text
PURE_COMPUTE / EXTERNAL_READ / IDEMPOTENT_MUTATION / RECONCILABLE_MUTATION / OPAQUE_MUTATION
```

Crash during dispatch → `OUTCOME_UNKNOWN` → read-only reconciliation (`CONFIRMED_SUCCEEDED / CONFIRMED_NOT_APPLIED / CONFIRMED_FAILED / STILL_IN_PROGRESS / INCONCLUSIVE`). No blind retry. If outcome cannot be determined → `AMBIGUOUS`, run blocks for manual resolution. Action success ≠ incident resolution — read-only verification must independently prove recovery, and may revise truth.

---

## Architecture (frozen blueprint v1.0-design)

```text
Engineer / Browser
  → Next.js Web Product (incident workspace, evidence/hypothesis views, approvals, verification, timeline)
  → NestJS Control Plane (workspace/identity, RBAC, catalog, integrations, credentials, policy — public API boundary)
  → Python Investigation Runtime / FastAPI (incidents, runs, steps, leases/fences, evidence/truth, intents, approvals, executions, reconciliation, verification, runtime audit)
    → AI Reasoning (LangGraph + thin LangChain, via NerveOps ModelGateway)
    → Knowledge / RAG (LlamaIndex + PostgreSQL FTS + pgvector + reranker)
    → Tool Gateway (native + MCP adapters, EXTERNAL_READ first)
    → Model Gateway (Ollama locally, vLLM production profile)
```

Supporting systems:

- **PostgreSQL** — durable authority. Separate ownership schemas: `control` (Prisma), `runtime` / `knowledge` / `eval` (SQLAlchemy/Alembic). No dual mutable ownership, no cross-owner FKs initially.
- **Redis** — Celery broker + disposable cache only. Never authoritative for runs, leases, approvals, or truth.
- **Celery** — background jobs only (ingestion, embeddings, reports, evals, cleanup). Not the investigation scheduler.
- **MinIO / S3** — blob bytes only. PostgreSQL owns object identity, workspace, version, digest, and lifecycle.
- **Langfuse** — AI behavior traces. **OpenTelemetry** — system traces. Neither is the audit log. Collector failure must not block correctness.

Key boundaries:

- Browser talks to NestJS only. NestJS authenticates + RBAC, then sends authenticated workspace-bound commands to the runtime. NestJS never writes runtime tables.
- LangGraph owns AI reasoning flow, never approval validity, execution identity, leases, or truth authority. Losing a checkpoint may cause recomputation, never forgotten dispatch.
- MCP is an external integration adapter, never the internal service bus or authorization layer.

---

## Repository status & roadmap

**Current state:**

- Product contract, truth model, execution semantics, architecture, and low-level contracts are frozen in `NerveOps Blueprint.md` (v1.0-design).
- GitHub milestones + 32 issues (M0–M7) are published. See Issues tab.
- No application code has landed yet. `main` has no executable app.

Evidence discipline throughout implementation:

```text
IMPLEMENTED ≠ TESTED ≠ CI-PASSING ≠ DEPLOYED ≠ STAGING-VERIFIED ≠ ACCEPTANCE-PROVEN
```

**Milestones:**

| Milestone | Outcome | Gate |
|---|---|---|
| M0 — Executable Foundation (#1–#4) | Repo shells, Compose topology, schema ownership, deterministic test/fake/CI harness | — |
| M1 — Tenant and Cross-Plane Authority (#5–#7) | Workspace/RBAC, catalog/credentials, authenticated idempotent commands | — |
| M2 — Durable Investigation Kernel (#8–#11) | Incidents/runs/steps, PG scheduling + leases/fences, restart/audit | **Gate A** (#11) |
| M3 — First Inspectable Product Path (#12–#13) | Alert/manual entry, durable workspace + timeline + SSE replay | — |
| M4 — Read-Only Investigation Intelligence (#14–#20) | Observations/evidence, ingestion, hybrid retrieval, Tool Gateway, truth engine, FakeLLM investigator | **Gate B** (#20) |
| M5 — Controlled Remediation Preparation (#21–#24) | Policy versions/grants, immutable intents, approval + durable wait, fenced preparation | **Gate C** (#24) |
| M6 — Trustworthy Side-Effect, Recovery, Verification (#25–#29) | Reconciliation, real rollback adapter, ambiguity resolution, verification | **Gate D** (#29) |
| M7 — Canonical Seeded Incident Acceptance (#30–#32) | Seeded payment incident E2E, browser acceptance, hosted demo + release proof | — |

Gate meanings:

- **A:** tenant substitution rejected, duplicate-safe commands, stale-worker rejection, restart recovery proven through real DB/process boundaries.
- **B:** tenant-safe retrieval/tools, stale reasoning cannot overwrite truth, every finding reconstructs sources/contradictions/unknowns.
- **C:** authorized mutation safely prepared up to dispatch boundary (exact binding, current policy/grant/precondition checks, fail-closed).
- **D:** first trustworthy production-like mutation path with crash/reconciliation/ambiguity/verification proofs.

M5 uses deterministic fake mutation providers by default. Only Gate D earns the word “trustworthy” for the real adapter path.

---

## Documentation map

Local working docs (not yet published as site docs):

```text
design phase/
  1. NerveOps Raw Idea.md
  2. NerveOps Architectural Review.md
  3. NerveOps Product Truth Model.md
  4. System Behavior Execution Semantics.md
  5. NerveOps Architecture Design.md
  6. NerveOps Low Level Contracts Review.md

issues design/
  1. NerveOps Blueprint.md              ← canonical frozen contract (v1.0-design)
  2. NerveOps Implementation Dependency Plan.md
  3. NerveOps Complete Implementation Issue Plan.md
  4. NerveOps M1-M7 GitHub Publication Manifest.md
```

GitHub Issues #1–#32 are the executable plan. Each issue body contains its outcome, blueprint references, hard blockers (H), acceptance prerequisites (A), scope/acceptance contract, non-goals, validation/evidence, and delivery artifacts.

---

## Tech stack (current mechanism, not résumé-driven)

| Layer | Choice | Role |
|---|---|---|
| Web | Next.js, React, TypeScript, Tailwind, shadcn/ui | Incident workspace product surface |
| Control Plane | NestJS, TypeScript, Prisma | Identity, RBAC, catalog, policy, public API |
| Runtime | Python, FastAPI, SQLAlchemy/Alembic | Investigation execution authority |
| DB / vectors | PostgreSQL, pgvector, PostgreSQL FTS | Durable state + hybrid retrieval |
| Ingestion | LlamaIndex (bounded helpers) | Parse/chunk/metadata/index prep |
| Reasoning | LangGraph + thin LangChain | Bounded AI investigation graph |
| Tools | Native adapters + MCP client | Versioned Tool Gateway |
| Inference | Ollama (local), vLLM (production profile) | Zero-paid-token dev path |
| Background | Celery, Redis | Ingestion/evals/reports only |
| Storage | MinIO locally, S3-compatible in prod | Blob bytes |
| Observability | Langfuse (AI), OpenTelemetry (system) | Traces, non-blocking |
| Testing | pytest, Vitest, Playwright | Unit → integration → browser E2E |
| Infra | Docker + Compose, GitHub Actions | Reproducible local env + CI |

If a technology stops serving a frozen requirement, it gets removed — portfolio value never overrides correctness.

---

## Getting started

> Not runnable yet. M0 (#1–#4) will establish `git clone && docker compose up`, owned migrations, health checks, and baseline CI. Until then, start with the blueprint and issues.

1. Read `issues design/1. NerveOps Blueprint.md`.
2. Read the dependency plan + complete issue plan for execution order.
3. Pick issues in dependency order (M0 first, then M1/M2 toward Gate A). Do not claim downstream acceptance before its gate.
4. Every state-adding issue must use its schema owner, carry workspace/version identity, provide migration + compatibility test, extend audit/traces, and add deterministic tests to the #4 harness.

If a change would alter a product requirement, invariant, authority boundary, execution semantic, tenant boundary, approval contract, or side-effect safety rule: stop and raise `BLUEPRINT AMENDMENT REQUIRED`.
