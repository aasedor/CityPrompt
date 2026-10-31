# Project preview pressure implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this bounded repair with regression tests and an independent review.

**Goal:** Keep project creation and navigation responsive when an account has many projects.

**Architecture:** Bound complete saved-render list operations, including their asset-ticket preparation, to three concurrent operations. Consume React Query cancellation, pause previews during New Project, and use the existing small-image URL helper for lazy thumbnails while retaining originals in the viewer and downloads.

**Tech Stack:** React, TanStack Query, Axios, Vitest.

**Spec:** Live acceptance reproduced a project-create 502 while the Projects page issued more than 100 concurrent render/ticket operations. Render application logs recorded database pool exhaustion. The existing Projects page uses an unbounded Promise.all. No new features, database limits, CORS changes, or authentication changes are part of this repair.

## Constraints and review focus

- Preserve existing projects, credentials, services, render originals, and release gates.
- One failed preview must not prevent other projects' previews.
- Navigation, query cancellation, and opening New Project must stop queued requests.
- Closing New Project must allow previews to resume; creation must remain usable while previews are pending.
- Small previews must preserve scoped URL credentials; expanded images and downloads must retain original URLs.

## Tasks

- [x] Add failing tests for 100 projects, cancellation, creation priority, recovery, and thumbnail/original separation.
- [x] Reuse the existing bounded worker helper; pass AbortSignal through rendersApi.list and shared ticket preparation; cancel preview work while creating.
- [x] Run focused tests, type checking, lint, production budgets, and independent review. Root focused run: 38 cases across six files; independent cancellation review: 23 cases. A broader eight-service run passed 33 cases. Production code build meets the unchanged budgets (8442.3/8448 KiB total JS). Ordinary local UI create/cancel/reopen/create succeeded with zero console errors.
- [ ] Open a checked PR to deployment-version; merge only when CI passes and deploy the frontend.
- [ ] Recheck actual live project creation and the new two-point bridge catalogue placements; save and deliver evidence.
