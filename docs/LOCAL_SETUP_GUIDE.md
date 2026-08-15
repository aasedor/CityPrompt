# City Prompt local setup

This guide installs City Prompt for local student use. It intentionally
contains no real credentials. Never paste API keys, access keys, passwords, or
tokens into source files or documentation.

## What runs locally

Docker Compose starts:

| Service | Purpose |
|---|---|
| Frontend | City Prompt web application |
| Backend | FastAPI application and API documentation |
| Celery worker | Background processing |
| PostgreSQL/PostGIS | Projects, accounts, and spatial data |
| Redis | Queue and cache |
| MinIO | Local S3-compatible file storage |

## 1. Install prerequisites

Install:

- Git 2.40+;
- Git LFS;
- Docker Desktop with Docker Compose v2;
- a current browser; and
- optionally Node.js 20+ and Python 3.11 or 3.12 for code development.

Verify:

~~~bash
git --version
git lfs version
docker --version
docker compose version
~~~

## 2. Clone the canonical repository

~~~bash
git lfs install
git clone https://github.com/aasedor/CityPrompt.git
cd CityPrompt
git switch main
~~~

The asset catalogue uses Git LFS. If images or GLB files contain short text
beginning with `version https://git-lfs.github.com/spec/v1`, the binary objects
were not downloaded. Run `git lfs pull` from a network that can access the
repository's LFS storage.

## 3. Create local configuration

macOS/Linux/Git Bash:

~~~bash
cp .env.example .env
~~~

PowerShell:

~~~powershell
Copy-Item .env.example .env
~~~

Edit `.env` locally. For the map-based workflow, configure:

~~~dotenv
MAPBOX_ACCESS_TOKEN=pk.your-public-token
~~~

Optional features use the corresponding placeholders already documented in
`.env.example`, such as `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`,
`OPENAI_API_KEY`, and `MESHY_API_KEY`. Only configure services authorized by
your instructor.

The local database, Redis, and MinIO defaults are development credentials and
must never be reused in a deployed environment. Generate a unique
`JWT_SECRET_KEY` for any shared installation.

## 4. Start City Prompt

Make sure Docker Desktop is running, then:

~~~bash
docker compose up -d --build
docker compose ps
~~~

The first build can take several minutes.

Open:

| Service | URL |
|---|---|
| City Prompt | <http://localhost:5175> |
| API health | <http://localhost:8000/health> |
| API docs | <http://localhost:8000/docs> |
| MinIO console | <http://localhost:9001> |

To watch startup:

~~~bash
docker compose logs -f
~~~

Press `Ctrl+C` to leave the log view; the services keep running.

### Windows launcher

Windows contributors can use:

~~~powershell
.\scripts\start-local-city-prompt.ps1
~~~

It reuses the local data services, starts the API from the current worktree,
starts the frontend when necessary, and waits for health checks.

## 5. Student smoke test

1. Open <http://localhost:5175>.
2. Register a local account and sign in.
3. Create a project.
4. Locate or define a site.
5. Draw a zone and save it.
6. Assign an archetype marked available.
7. Generate or edit the plan.
8. Open the 3D view and confirm the scene loads.
9. Save, reload the browser, and reopen the project.

If an AI-provider feature is part of the lesson, confirm its key is configured
before the session. Core editing should not require students to discover or
purchase provider credentials unexpectedly.

## 6. Stop or restart

Stop services while keeping local data:

~~~bash
docker compose down
~~~

Rebuild after dependency changes:

~~~bash
docker compose up -d --build
~~~

Deleting volumes erases local accounts, projects, and uploaded files:

~~~bash
docker compose down -v
~~~

Use that command only when a deliberate fresh start is required.

## 7. Run checks

Frontend:

~~~bash
cd frontend
npm ci
npm run lint
npm run type-check
npm run test -- --run
npm run build
npm run check:archetype-assets
npm run check:sticker-pilot-assets
~~~

Backend:

~~~bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
~~~

## Troubleshooting

### A service is restarting

~~~bash
docker compose ps
docker compose logs backend
docker compose logs frontend
~~~

### The map is blank

Confirm `MAPBOX_ACCESS_TOKEN` is set in `.env`, then restart the frontend.
Inspect the browser console for a token or network error.

### An asset is a tiny text file

Run:

~~~bash
git lfs pull
git lfs fsck
~~~

If LFS reports a missing object, tell the instructor which path failed. Do not
replace it with an unrelated file.

### Port conflict

Stop the other application using ports 5175, 8000, 9001, 6379, or 5432, then
restart Compose. Do not silently change shared project ports in a student lab.

### Reset warning

`docker compose down -v` permanently deletes the local Docker volumes. Back up
student work before using it.

## Security note

The previous version of this guide contained historical cloud-storage
credentials. They have been removed from the current tree and must be treated
as compromised and rotated by the account owner. Repository cleanup alone
does not remove a secret from existing clones or Git history.
