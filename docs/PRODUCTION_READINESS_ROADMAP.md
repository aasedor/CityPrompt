# SiteForge Production Readiness Roadmap

**Status label:** advanced prototype / private-beta candidate.

**Goal:** move SiteForge from "works well with supervision" to "safe enough for real users, real project data, and controlled public beta." This roadmap is meant to survive context resets. If a future session starts cold, begin here before touching production-hardening work.

## Current Read

SiteForge already has substantial product infrastructure:

- React/TypeScript/Vite frontend with Mapbox, Three.js, Zustand, TanStack Query, and Sentry dependency.
- FastAPI backend with SQLAlchemy, PostgreSQL/PostGIS, Redis, Celery, object storage, auth, migrations, and API routers.
- Render pipelines for aerial and street-level AI outputs.
- Deployment artifacts for Docker Compose, Render, Kubernetes, and Terraform.
- Test coverage exists across backend, frontend, and e2e folders.

It is not yet fully production-grade because the remaining work is mostly operational hardening: security defaults, expensive render-job controls, observability, repeatable QA, deployment discipline, backups, scale testing, and polished recovery states.

## Operating Principles

1. **Private beta before public SaaS.** Treat the near-term target as a controlled beta with known users and monitored usage.
2. **Guard expensive actions first.** AI render calls need quotas, cancellation, retries, audit logs, and spend caps before scale.
3. **Protect production by default.** In `APP_ENV=production`, unsafe defaults should fail startup rather than quietly run.
4. **Golden path must be tested.** Login, create project, draw zone, assign archetype, render, save, reload, and share/export should be covered end to end.
5. **Observe before scaling.** Add request IDs, render traces, provider/model/timing/cost logs, and alerts before increasing traffic.
6. **One blessed deployment path.** Keep local/staging/prod workflows clear and documented; avoid multiple half-maintained production stories.
7. **Small, verifiable changes.** Each hardening task should include a local check, test, or operational verification.

## Wave 1: Safety First

These are the highest-priority blockers before an unsupervised beta.

### 1. Production Config Lockdown

**Target outcome:** the app refuses unsafe production configuration.

- [x] Fail backend startup in production if `JWT_SECRET_KEY` is missing or still equals `change-this-in-production`.
- [x] Require explicit production `ALLOWED_ORIGINS`; do not allow broad localhost regex in production.
- [x] Disable or protect `/docs`, `/redoc`, and `/metrics` in production.
- [ ] Audit `.env`, `.env.example`, Render env vars, and frontend `VITE_*` vars.
- [ ] Rotate any secret that may have been exposed locally or committed historically.

Suggested files to inspect:

- `backend/app/core/config.py`
- `backend/app/main.py`
- `.env.example`
- `render.yaml`
- `docker-compose.staging.yml`

### 2. Render Cost Controls

**Current baseline:** SiteForge already has a render-token system. Users have `render_credits`, non-admin renders are checked before generation, successful renders deduct per-model token costs, credits reset weekly, admins can adjust user tokens, render audit logs store `tokens_spent`, and API usage logs aggregate provider token/credit usage.

**Target outcome:** strengthen the existing system so no user, race condition, provider failure, or bug can accidentally create runaway AI spend.

- [ ] Audit existing render-token flows and document exact coverage/gaps.
- [ ] Add per-user render limits by day/month if weekly reset is not enough for beta.
- [ ] Add global daily spend cap.
- [ ] Add per-job estimated and final provider cost fields where internal tokens are not enough.
- [ ] Block or require confirmation for bulk render operations above a configured threshold.
- [ ] Expose admin view of queued/running/succeeded/failed/cancelled jobs and estimated spend.
- [ ] Record provider, model, image count, prompt length, input image count, timing, status, and cost.
- [ ] Make token deduction/reservation safe under concurrent requests.
- [ ] Decide how failed/timeout/provider-charged attempts should affect credits and usage logs.

Suggested files to inspect:

- `backend/app/api/v1/render.py`
- `backend/app/api/v1/admin.py`
- `backend/app/models/models.py`
- `frontend/src/components/viewer/useAIRender.ts`
- `frontend/src/components/viewer/useStreetViewRender.ts`
- `frontend/src/store/useGenerationStore.ts`

### 3. Render Job Reliability

**Target outcome:** render jobs are visible, recoverable, cancellable, and not mysterious when they fail.

- [ ] Persist clear job states: `queued`, `running`, `succeeded`, `failed`, `cancelled`, `timed_out`.
- [ ] Add cancellation from the frontend and backend.
- [ ] Add retry rules for transient provider/network failures.
- [ ] Add hard timeouts and useful failure messages.
- [ ] Make retries idempotent where possible.
- [ ] Keep saved render outputs durable and linked to project/user/job records.

## Wave 2: Trust The Product

These tasks make SiteForge defensible for real customer workflows.

### 4. Core End-to-End QA

**Target outcome:** one repeatable golden-path test proves the core product loop.

- [ ] Login or seed auth.
- [ ] Create/open project.
- [ ] Locate map/site.
- [ ] Draw site boundary and at least one zone.
- [ ] Assign an archetype and variant.
- [ ] Trigger an AI render using a mocked provider in CI.
- [ ] Save the render.
- [ ] Reload the project and verify zones/render persist.

Suggested files to inspect:

- `frontend/e2e/*`
- `frontend/playwright.config.ts`
- `backend/tests/*`
- `.github/workflows/ci.yml`

### 5. Observability

**Target outcome:** when something fails, the team can see where and why.

- [ ] Configure Sentry frontend and backend for staging and production.
- [ ] Add request IDs/correlation IDs across frontend, backend, render jobs, and provider calls.
- [ ] Emit structured backend logs for render lifecycle events.
- [ ] Track queue depth, render failure rate, provider latency, and spend threshold.
- [ ] Add alerts for failed-render spikes, queue backlog, API 5xx rate, and spend caps.

### 6. Deployment Discipline

**Target outcome:** staging and production are repeatable and recoverable.

- [ ] Choose and document the blessed deployment path.
- [ ] Document environment variables for local/staging/production.
- [ ] Run migrations automatically or with a documented manual procedure.
- [ ] Configure database backups.
- [ ] Perform and document a restore drill.
- [ ] Add smoke tests after deploy.
- [ ] Document rollback steps.

Suggested files to inspect:

- `docs/DEPLOYMENT.md`
- `render.yaml`
- `docker-compose.staging.yml`
- `k8s/`
- `terraform/`

## Wave 3: Public Beta Polish

These tasks improve user confidence and reduce support load.

### 7. Frontend Production Polish

- [ ] Gate or remove noisy `console.log` calls in render-heavy paths.
- [ ] Add friendly error states for render failures, auth failures, provider timeouts, and save errors.
- [ ] Add clear progress states for long-running render jobs.
- [ ] Improve empty states and first-use flow.
- [ ] Enforce bundle and performance budgets in CI.

### 8. Scale And Stress Checks

- [ ] Test large projects with many zones.
- [ ] Test multiple simultaneous users and render jobs.
- [ ] Test provider slowness and provider failure.
- [ ] Test map/render performance on lower-end machines.
- [ ] Test object storage failure and recovery behavior.

## Recommended First Sprint

Start here if there is no active production-readiness branch yet.

1. Add production config guardrails.
2. Protect production docs/metrics.
3. Add render job cost/status audit fields or document the current model gap.
4. Add one mocked-provider golden-path e2e test.
5. Add basic render telemetry: request ID, provider, model, timing, status, and error reason.

## Definition Of Done For Beta

SiteForge can be called controlled-beta ready when:

- Unsafe production config fails startup.
- Expensive render operations have quotas and admin visibility.
- Core render jobs are persisted, cancellable, retryable, and recoverable.
- The golden path is covered by CI.
- Sentry/logging can connect frontend action to backend request to render job.
- Staging deploys are repeatable.
- Database backup and restore have been tested.
- User-facing failure states explain what happened and how to continue.

## Future Session Start Prompt

Use this when restarting with little or no context:

```text
Read docs/PRODUCTION_READINESS_ROADMAP.md and AGENTS.md first. We are moving SiteForge from advanced prototype/private beta toward production grade. Start with Wave 1 unless I specify another task. Preserve catalog JSON rules, avoid unrelated refactors, and verify each hardening change locally.
```
