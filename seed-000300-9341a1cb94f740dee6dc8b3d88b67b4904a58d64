# Next-Session Workplan (written 2026-07-07)

Three approved plans to execute, in recommended order. Branch: `feat/urban-intelligence-dna`
(local, unpushed; HEAD ≈ b05a274). Backend tests run IN DOCKER:
`docker exec devplatform-backend python -m pytest tests/ -q` (242 green at time of writing);
restart `devplatform-backend` + `devplatform-celery` after backend changes; frontend gates:
`npx tsc --noEmit` (delta-clean only — ~39 chronic pre-existing errors) + `npx vitest run`
(64 green) + `npm run build`.

## Order

1. **Render boundary accuracy — P0 slice first** (hours, fixes live bugs affecting every render
   today: label-leak into composites, GPT resize ghosting, 16-ref cap, style-contract split,
   streets clause). → `docs/RENDER_BOUNDARY_ACCURACY_PLAN_2026_07_07.md`
2. **Generate Community / unsaved-zone errors** (half day; option A root-cause + option B guards).
   → `docs/GENERATE_COMMUNITY_TEMP_ZONE_PLAN_2026_07_07.md`
3. **Custom master-plan scenario** (~1.5 days incl. tests).
   → `docs/CUSTOM_SCENARIO_PLAN_2026_07_07.md`
4. Render accuracy **P1** (verification gate + re-roll; OSM carve; two-pass artistic toggle),
   then the ≤8-call pilot per its protocol (artistic pilots on **Gemini** — ledger #34).

## Session bootstrap notes

- Test account for e2e: `claude.test.customstyle@example.com` / `testpass1234`; planner test data
  lives in project "Custom Style E2E" (Beltline site, scenarios + drawn plans + saved renders).
  The user's own trials: "Water Centre" and the small riverfront site.
- Headless-preview recipe (hidden preview tab, WebGL): memory
  `feedback_hidden_preview_webgl_rendering` — rAF/ResizeObserver shims via a TEMP index.html
  flag block (never commit it), captures POSTed to a local :5199 server.
- Do-not-retry ledger: `docs/CITY_PROMPT_DO_NOT_RETRY_LEDGER_2026_06_17.md` — no stacked
  negatives (≤8 constraint budget: adding a clause must displace one), no red-mask/zone-crop/
  auto-frame retries, artistic → Gemini, refs ≤16 on GPT with the plan diagram in slot 1.
- Never `git add -A` (env backups / chat logs / .bak catalogs in tree); stage explicit paths;
  after every commit run `git diff HEAD --stat` on the committed paths (OneDrive once produced a
  stale-copy commit).
- Ship steps when the user asks: fetch all remotes → backup-push to `origin2` → push `beeman`
  (real prod main = beeman/main; branch fast-forwards) → one PR; deploy runbook is in the plan
  file `C:\Users\andre\.claude\plans\city-prompt-urban-velvety-sparrow.md` (env keys on BOTH
  Render services, `alembic current` → 024, corpus seed via Render shell, worker smoke).
