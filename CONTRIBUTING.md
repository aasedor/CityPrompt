# Contributing to City Prompt

City Prompt uses `main` as its canonical working and integration branch. Keep
changes small, verified, and easy to review; do not leave completed work on
long-lived pilot branches.

Before substantial work, read [AGENTS.md](AGENTS.md) and
[CLAUDE.md](CLAUDE.md). Building-family work also requires
[docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md](docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md).

## Setup

~~~bash
git lfs install
git clone https://github.com/aasedor/CityPrompt.git
cd CityPrompt
cp .env.example .env
docker compose up -d --build
~~~

See [docs/LOCAL_SETUP_GUIDE.md](docs/LOCAL_SETUP_GUIDE.md) for complete setup
and troubleshooting.

## Working on main

1. Start from a clean tree: `git status --short --branch`.
2. Fetch and fast-forward from `cityprompt/main`.
3. Work on one named initiative at a time.
4. Use a temporary branch or worktree only when concurrent or risky work needs
   isolation, and integrate it promptly.
5. Preserve unrelated local changes; never reset or clean another person's
   work.
6. Commit one coherent, verified unit at a time.
7. Do not push unverified changes or force-push shared history.

## Required checks

Frontend production changes:

~~~bash
cd frontend
npm ci
npm run lint
npm run type-check
npm run test -- --run
npm run build
~~~

Backend changes:

~~~bash
cd backend
python -m pytest
~~~

Asset and catalogue changes:

~~~bash
cd frontend
npm run check:archetype-assets
npm run check:sticker-pilot-assets
~~~

Compiler changes:

~~~bash
python -m pytest tools/archetype_compiler/tests/ -v
~~~

Before every commit:

~~~bash
git diff --check
git diff --stat
git status --short
~~~

Use `git diff --cached` variants when the change is staged.

## Code conventions

### Frontend

- React 18, TypeScript, Vite, Zustand, TanStack Query, Three.js, and Mapbox.
- ESLint 9 is the source lint gate.
- Keep components accessible and avoid adding unguarded debug logging.
- Add focused Vitest coverage for changed behavior.

### Backend

- Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic, and Celery.
- Format with Black, lint with Ruff, and type-check touched code when practical.
- Add focused pytest coverage for services and endpoints.

## Assets and generated output

- Runtime archetype roots are `buildings`, `openspaces`, and `streets` under
  `frontend/public/archetypes`.
- Use Git LFS for intentional large binary runtime assets.
- Keep renders, screenshots, compiler builds, and visual-QA batches outside
  the source tree or in the ignored `artifacts/` directory.
- Never stage a generated directory wholesale.
- Generate a finite batch: dry run, one-archetype pilot, visual review, then a
  bounded rollout.

## Catalogue edits

Do not parse and rewrite `frontend/src/data/buildingArchetypes.json` with
`json.dump()`. Its path spellings are contract data. Follow the text-level
editing rule in [CLAUDE.md](CLAUDE.md), preserve incomplete entries explicitly,
and run the asset checks.

## Pull requests

When review is needed, include:

- the user-visible outcome;
- the exact verification commands and results;
- screenshots for visual changes;
- source changes separated from ignored/generated output; and
- any known limitation or follow-up.
