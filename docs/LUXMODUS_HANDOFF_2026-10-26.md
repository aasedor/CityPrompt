# City Prompt — current application handoff, 26 October 2026

Target repository: `beemanbesh/2D-Maps2`.
New branch: `codex/luxmodus-current-20261026`.
Application source snapshot: `18d2cb62d105ffd7ed87f6feec28c1c0bc125124`
from the current local City Prompt checkout, following the published
`aasedor/CityPrompt` development line.

This branch copies the current application while preserving the target
repository's existing `main` and other branches. It is an application handoff,
not a deployment or a completed integration with LuxModus-specific changes.
Its snapshot parent is the target repository's existing main commit; the
application tree comes from the source snapshot above. This avoids importing
unrelated development history into the handoff branch.

## Transfer status: source review only; asset sync blocked

The application source and Git LFS pointer files are present on this branch.
The attempted model/image payload transfer was rejected by GitHub:
`This repository exceeded its LFS budget. The account responsible for the budget should increase it to restore access.`
The attempted upload reported 0 bytes transferred. **Do not treat this branch as
a complete, deployment-ready copy until its LFS assets have been synchronized
and verified.** No budget settings or purchases were changed.

The account owner must restore LFS availability before the remaining asset
transfer can finish. The original assets and the exact source snapshot are
preserved locally; after that restriction is resolved, resume a normal LFS
upload to this repository and verify the required asset downloads. Avoid
merging this branch into a deployed branch before the preview checks below.

## What is included

- Current frontend, backend, migrations, catalogue definitions and tracked asset
  references. Large model/image payload synchronization is blocked as noted above.
- The architecture/style/era/planning teaching interface, optional public data
  layers, court-only sports assets and the latest placement/recovery fixes.
- Seven independently reviewed architectural-clay teaching buildings as
  **development-only trials**. Their exact GLBs, front/oblique/top references and
  independent reviews are declared at their public paths. Their model/image
  payloads require the blocked LFS synchronization. They remain
  excluded from production discovery; this copy grants no new catalogue approval.
- The existing database compatibility bridge for the older `2D-Maps2` schema.
  See `docs/RENDER_DATABASE_BRIDGE_2026-10-14.md`.

Only the handoff note, the portable teaching-trial asset files and their Git LFS
attributes were added to the application snapshot. Application code is unchanged.
The original seven-building trial and its limits are documented in
`docs/LOCAL_TEACHING_BUILDINGS_TRIAL_2026-10-26.md`.

## Assets and private data

Git LFS stores large models and images. Retrieve actual LFS objects before
building or reviewing; pointer text is not a model/image. The current hosted
asset builder verifies selected files and can fetch required LFS objects.

This branch does not contain development dotenv files, provider keys, database
backups, user accounts, balances, saved projects or private media buckets. A Git
transfer does not create the Model Library's database rows or upload its private
storage objects. Existing exact seeding and readback verification remain required.

The seven local teaching trials use direct GLBs and need no new database model
rows. Their original local-only metadata and publication guards are preserved.

## Before a LuxModus preview

1. Record LuxModus's actual deployed commit, configuration and custom changes.
   Compare those with this branch before choosing integration changes.
2. Preserve their existing domain, login/OAuth, allowed origins, storage and
   provider settings in their deployment environment. Keep server credentials
   out of browser build configuration.
3. The current backend Dockerfile is `backend/Dockerfile.render` and its **build
   context is the repository root**. This differs from the older backend-only
   context. Current frontend asset-aware build tooling is
   `scripts/build_hosted_frontend.py`; see `render.staging.yaml` and
   `docs/RENDER_RELEASE_2026-10-07.md` for the prepared deployment structure.
   The older root `render.yaml` is historical configuration.
4. If a build environment strips Git remotes, configure `origin` for this
   repository before requesting LFS downloads. The existing automatic Render
   origin restoration is pinned to `aasedor/CityPrompt`; private-repository
   asset access must use the host's authorized Git credentials.
5. Rehearse the database upgrade on an isolated restored copy. Preserve accounts,
   projects and media, then seed/verify eligible exact Model Library assets.
6. Test login, reopening old projects, building identity, placement/editing and
   render/export workflows on a separate preview before changing live hosting.

## Verification carried forward

The source snapshot passed 183 focused frontend tests, seven installer tests
and TypeScript checking. The ordinary local trial placed all seven new models,
fully reloaded the project and observed no browser warnings/errors. The original
35 local trial files were verified by SHA-256 against actual localhost responses.

These are local/source checks. LuxModus hosting, its database and its custom
integration have not been exercised by copying this branch. Natural terrain,
entrance routes, touch, mixed-scene and export acceptance for the seven new trials
retain their recorded untested status. No paid generations or hosting changes
are part of this handoff.
