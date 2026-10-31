# City Prompt repository handoff

Current-state summary for whoever takes over this repository. It complements
the dated review runbooks in `docs/` (start with
[docs/COMPANY_HANDOFF_2026-10-29.md](docs/COMPANY_HANDOFF_2026-10-29.md) and
[docs/FINAL_CANDIDATE_SECURITY_2026-10-30.md](docs/FINAL_CANDIDATE_SECURITY_2026-10-30.md)),
which describe exact review commits, asset packets and evidence. This file
describes how the repository is organised and what remains open.

## Branches and releases

- `deployment-version` is the canonical working, integration and release
  branch and GitHub's default branch. Every merged change lands here through a
  pull request, and the live site is built from it.
- `main` is kept only as a synchronized mirror. Do not base work on it.
- Short-lived branches are `codex/<topic>` or `claude/<topic>`; retired
  branches are preserved as `archive/<date>/<branch>` tags before deletion.
- There are no release tags yet; tag the commit that is live before any
  transfer so there is a fixed reference and a rollback point.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request to the branches
above. Its jobs are the required gates:

| Job | What it proves |
|---|---|
| `repository-hygiene` | no oversized ordinary Git blobs, valid LFS pointers, named source-JSON budgets |
| `backend` | ruff, black, mypy (core/models/schemas), Alembic upgrade, pytest, catalogue promotion drift |
| `frontend` | npm audit, ESLint, knip, type-check, Vitest, production build, asset and catalogue checks, bundle budget |
| `browser` | Playwright student workflow and globe startup check |
| `docker` | backend and frontend images build |

`backend-tests.yml` is a faster backend-only gate for backend-only changes.
`release-assets.yml` is a manual workflow that proves a fully hydrated asset
set for a release candidate.

## Live deployment

The production site, cityprompt.ca, is hosted on Render and deploys from
`deployment-version`. The repository holds the service shape, not the live
configuration:

- `render.staging.yaml` is the Blueprint for the current full-catalogue
  deployment: an API web service, image, maintenance and general Celery
  workers, a beat scheduler, a PostgreSQL database, a key-value queue and a
  static web service built by `scripts/build_hosted_frontend.py --fetch-lfs`.
- The root `render.yaml` is the legacy Blueprint and must not be synced.
- Branch bindings, environment variables, provider keys and auto-deploy
  settings live only in the Render dashboard. `.env.example` lists every
  variable the backend reads; `backend/app/core/config.py` validates them and
  refuses unsafe production values.
- Database migrations run through `python -m scripts.prepare_database`
  (`backend/scripts/start.sh`); the Alembic head is `033`, reached through a
  two-parent merge migration that folds in a legacy document-processing line.
  See [docs/RENDER_DATABASE_BRIDGE_2026-10-14.md](docs/RENDER_DATABASE_BRIDGE_2026-10-14.md).

## Assets and Git LFS

Large models and images are Git LFS objects. `.lfsconfig` excludes everything
from automatic download, so a fresh clone contains pointer files. Hydrate only
what a task needs:

- `scripts/materialize_frontend_assets.py --fetch-lfs` prepares the exact
  archive-backed runtime files CI needs.
- `scripts/hosted_assets.py` and `scripts/build_hosted_frontend.py` prepare
  and verify the production asset packet and build.
- `frontend/src/data/runtimeAssetManifest.json` is the generated registry of
  required runtime files; `npm run check:runtime-assets` proves it is current.

## Local development

[README.md](README.md) covers the Docker and non-Docker stacks;
[docs/LOCAL_SETUP_GUIDE.md](docs/LOCAL_SETUP_GUIDE.md) is the beginner path.
`cityprompt-compose.yml` is an optional port-shifted stack and
`docker-compose.staging.yml` is a local staging overlay; neither is used by
the hosted deployment.

## Known issues and open items

- About 750 MB of images under `frontend/public/archetypes` and
  `frontend/public/park-skins` are committed as ordinary Git blobs although
  `.gitattributes` marks them for LFS. Every clone pays for this. Fixing it is
  a history rewrite (`git lfs migrate import`) that should be planned as a
  separate migration with a remote freeze, not done casually.
- [SECURITY.md](SECURITY.md) records that cloud-storage credentials once
  appeared in a setup document. They are absent from the current tree but the
  account owner must confirm they were rotated.
- Branch protection exists only on `main`; `deployment-version` has none. Add
  the five CI jobs above as required checks on `deployment-version`.
- [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) still has unchecked release
  gates: the hydrated compiler test run, a fresh-clone Docker start and the
  fresh-clone student workflow.
- Behind Render's proxy every request shares one client address unless
  `TRUSTED_PROXY_CIDRS` and `FORWARDED_ALLOW_IPS` are set, so the per-address
  auth rate limits in `backend/app/core/rate_limit.py` act globally.
- `backend/requirements.txt` pins `transformers`, which nothing imports.
- Several provider model identifiers are aliases or older releases
  (`gemini-3-pro-image-preview`, the deprecated `gemini-3.1-flash-image-preview`
  fallback, `claude-sonnet-5`, `claude-haiku-4-5-20251001`); verify each is
  still served before relying on the feature that uses it.
- A few data and evidence JSON files still contain mis-encoded punctuation
  (for example `frontend/src/data/localTeachingBuildings.json` and
  `seed/model-library/rlasm-architectural-clay/library.json`). They were left
  untouched because exact-byte checks may cover them; source files and
  user-facing strings were corrected.

## Owner actions before the transfer

1. Confirm the copyright holder named in [LICENSE](LICENSE) and the terms.
2. Confirm credential rotation (see above) and remove any unused provider keys
   from the Render dashboard.
3. Tag the live commit as a release.
4. Record in the Render dashboard which branch each service deploys from, and
   hand over the dashboard access itself; nothing in this repository can
   reproduce it.
5. Decide whether `main` stays as a mirror or is deleted so that a single
   branch remains.
