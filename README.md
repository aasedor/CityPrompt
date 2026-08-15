# City Prompt

City Prompt is an interactive urban-design workspace for turning a site,
planning intent, and a catalogue of building and public-realm archetypes into
editable 2D plans, explorable 3D scenes, and presentation renders.

The application combines:

- a React, TypeScript, Mapbox, and Three.js frontend;
- a FastAPI backend with PostgreSQL/PostGIS, Redis, Celery, and S3-compatible
  storage;
- building, street, park, and plaza catalogues;
- modular LEGO assembly and Sticker Method 3D assets; and
- optional AI providers for document interpretation, images, 3D generation,
  and video.

`main` is the canonical working branch. Long-lived pilot branches are not part
of the release workflow.

## Student workflow

Once the local stack is running, a student can:

1. create an account and project;
2. locate or define a site;
3. draw and edit planning zones;
4. assign building, street, park, and plaza archetypes;
5. generate and refine a master plan;
6. inspect the design in 2D and 3D;
7. use available LEGO and Sticker Method families; and
8. create optional AI renders when the relevant provider key is configured.

See [the user guide](docs/USER_GUIDE.md) for the product walkthrough and
[the local setup guide](docs/LOCAL_SETUP_GUIDE.md) for a beginner-friendly
installation.

## Prerequisites

- Git 2.40+ and Git LFS
- Docker Desktop with Docker Compose v2
- Node.js 20+ for frontend development
- Python 3.11 or 3.12 for backend development

## Quick start

~~~bash
git lfs install
git clone https://github.com/aasedor/CityPrompt.git
cd CityPrompt
cp .env.example .env
docker compose up -d --build
~~~

On PowerShell, create the environment file with:

~~~powershell
Copy-Item .env.example .env
~~~

At minimum, set `MAPBOX_ACCESS_TOKEN` in `.env` for map tiles. AI features are
enabled only when their corresponding keys are present. Never commit `.env` or
paste credentials into documentation.

Open:

- application: <http://localhost:5175>
- API health: <http://localhost:8000/health>
- API documentation: <http://localhost:8000/docs>
- MinIO console: <http://localhost:9001>

The first build can take several minutes. Use `docker compose ps` and
`docker compose logs -f` to inspect startup.

### Windows development launcher

For day-to-day Windows development, including linked Git worktrees:

~~~powershell
.\scripts\start-local-city-prompt.ps1
~~~

The launcher preserves the shared local database and storage containers,
starts the API from the current worktree, starts the frontend when necessary,
and waits for health checks. Pass `-KeepBackend` only when intentionally
retaining an already-running API.

## Run services without Docker

Keep PostgreSQL, Redis, and MinIO available, then run:

~~~bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
~~~

In another terminal:

~~~bash
cd frontend
npm ci
npm run dev
~~~

The direct Vite server uses <http://localhost:5174>.

## Verification

Run these gates before integrating application changes:

~~~bash
cd frontend
npm ci
npm run lint
npm run type-check
npm run test -- --run
npx playwright install chromium
npm run test:e2e
npm run build
npm run check:archetype-assets
npm run check:sticker-pilot-assets
~~~

~~~bash
cd backend
python -m pytest
~~~

Compiler changes also require:

~~~bash
python -m pytest tools/archetype_compiler/tests/ -v
~~~

The current release checklist is in
[PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md).

## Repository layout

~~~text
backend/        FastAPI application, migrations, workers, and pytest suite
frontend/       React application, Vitest suite, and runtime web assets
tools/          Deterministic building and public-realm asset compilers
scripts/        Local launch, validation, and bounded generation helpers
docs/           Active product, pipeline, and quality documentation
artifacts/      Ignored local output; never commit generated review batches
~~~

Runtime archetype images belong only in:

~~~text
frontend/public/archetypes/buildings/
frontend/public/archetypes/openspaces/
frontend/public/archetypes/streets/
~~~

LEGO and Sticker Method work must follow
[the high-quality building memory](docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md) and
the repository's dry-run, one-archetype pilot, visual-review, then bounded
scale-up sequence.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), and
[CLAUDE.md](CLAUDE.md) before substantial work.

Report sensitive issues according to [SECURITY.md](SECURITY.md).

## License

Proprietary. All rights reserved.
