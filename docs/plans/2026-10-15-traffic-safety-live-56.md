# Traffic safety: 56-asset live integration

Authorized scope: all five supplied kits, with grouped variants and immutable
source hashes. Preview acceptance precedes production. No new paid resources,
schema migrations, provider changes, or LFS policy changes. Existing scenes and
unrelated work are preserved.

## Baseline and rollback

Verified 2026-10-15 in the Render dashboard and public identity endpoints:
- Site: https://www.cityprompt.ca
- Render workspace: Walid's workspace, tea-d6ehg8kr85hc73d775lg.
- Frontend srv-d6ehqtjh46gs73e28n50: 6ae24c9fd0c44352befc417b76f4187bf7d3b40c,
  deployment dep-db8emtvf3r2c73fi6170. version.json agrees, source_dirty=true.
- API https://threed-platform-api.onrender.com: health reports
  c56414430c33389736810b1c785410d89f5dceee; ready endpoint passes.
  Service srv-d6ehtvk1hm7c73f5ho9g; deployment dep-db8f3inf3r2c73fj9clg.
- Source aasedor/CityPrompt, deployment-version. Frontend auto-deploy OFF.
  API auto-deploy also OFF. API Dockerfile ./backend/Dockerfile.render,
  context ., root blank; Docker/pre-deploy command overrides blank.
- Frontend build: npm ci --prefix frontend && python3 scripts/build_hosted_frontend.py --fetch-lfs
  root blank, publish frontend/dist. Existing Blueprint must NOT be synchronized.
- Rollback: retain the above frontend deployment; Render deployment history exposes
  Rollback for successful prior deployments. After promotion restore this retained
  frontend through that normal control if needed. Record API deployment before any
  backend promotion, preserve all database/media data, never downgrade schema or
  delete objects. Reverify health, identity and existing scene after rollback.
  Compatibility caveat: the retained API rejects new safety IDs and the old
  frontend cannot resolve them. Do not roll back blindly after real users save
  safety items. Retain a compatibility release or gate new writes before rollout;
  never erase new scene items to make an older release load.

## Work sequence

1. Audit five preserved ZIPs outside Git, read contracts/QA/provenance, verify all
   56 GLBs against exact manifests and record inventory. No regeneration.
2. Reuse Add Details catalogue/loader and instancing; add grouped variant controls,
   fixed metre transforms and datum handling. Pilot curb and crosswalk first.
3. Implement placement validation against authored flat roads/sidewalk hosts.
   Curb bulbs require complete attachment match and host curb replacement. Reject
   unsupported/uncertain host shapes and ramp conflicts rather than overlap them.
4. Extend existing project-detail persistence and shared undo/redo without losing
   old IDs, variants or transforms. Explicit host dependencies must survive reload.
5. Complete all variants, hashes, source-driven thumbnails and selective hosted
   asset closure. Reuse existing LFS-covered runtime directories.
6. Narrow frontend/backend tests, type check, lint, build, regression checks, actual
   browser preview. Test all 56 GLB loads and transforms, each operation and variant,
   capture, mixed scenes, depth and terrain restrictions; record measured costs.
7. Fresh whole-branch review; fix critical findings. Commit only this initiative.
8. Publish verified commit via current Render process, API before frontend when
   registry compatibility requires it. Verify live identities, 56 responses/hashes,
   selectors, disposable scene placement/save/reload and existing-feature smoke.

## Evidence ledger

- Ruling: release the 44 supplied assets that pass placement checks plus ten
  reviewed Calgary concepts; keep twelve curb bulbs disabled in both menus and
  the placement validator. The user's acceptance requires failing assets to stay
  outside enabled placement. This defers complete sidewalk/curb integration.
- Preview evidence is in ../traffic-safety/RELEASE_VALIDATION.md. Production
  dashboard baseline was rechecked this session and still matches the IDs above.

- Isolated linked worktree reused: add-details-recovery/CityPrompt, initially clean.
  New initiative branch codex/traffic-safety-live-56 from c56414430.
- OneDrive checkout is dirty and untouched.
- Source archive directory: D:/CityPrompt-traffic-safety-2026-10-15/source.
- Current findings: shared detail placement adds 0.084m; new kits require exact
  road datum. Existing detail persistence validates model IDs server-side.
- Partial implementation and evidence are recorded in docs/traffic-safety/README.md
  and asset-inventory.json. Full application and live acceptance remain NOT TESTED.
- Physical student-laptop/mobile access not established; do not describe desktop
  timings or viewport emulation as physical-device measurements.
