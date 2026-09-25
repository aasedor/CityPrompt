# Pull and run the exact catalogue validation branch

This is a **rebuilt validation copy**, not access to Andrew's Windows localhost.
It carries the same exact 27 selected model hashes, native modules and reference
evidence. It does not claim Linux/browser acceptance or release approval.
Eleven fixed review assemblies still have explicitly missing extension integration.

## Fetch the branch and only the required LFS packet

Use the canonical repository `https://github.com/aasedor/CityPrompt.git`.
Preserve any existing work before changing checkouts. Prefer a separate clone:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --single-branch --branch codex/approved-catalogue-validation https://github.com/aasedor/CityPrompt.git CityPrompt-validation
cd CityPrompt-validation
git lfs install --local
git lfs pull --include="seed/validation/runtime-assets.zip" --exclude=""
python3 scripts/validation_bundle.py unpack
python3 scripts/validation_bundle.py init-env
```

The approximately 239 MB LFS packet is `seed/validation/runtime-assets.zip`.
`manifest.json` beside it pins every file hash; unpack checks the complete
inventory, rejects wrong bytes and preserves changed existing files. It
extracts into ignored `.validation/`; it does not regenerate any model.
Model Library bindings are in `seed/validation/model-bindings.json`.
All 27 roster entries remain in `frontend/src/data/validationCatalogue.json`.
Windows paths in that roster are historical provenance, not setup dependencies.
Runtime assets and the new bootstrap use portable relative paths.

## Private configuration and login

`init-env` creates private, ignored environment files and prints a newly generated
test password for **student-validation@example.com**. The password is also in
`.validation/env/backend.env` as `VALIDATION_STUDENT_PASSWORD`; do not copy it,
tokens or environment files into Git or the public evidence report.
This rebuilt copy does not use the previous Windows login password/database.

Supply map credentials **privately** before starting:

- `.validation/env/backend.env`: `GOOGLE_MAPS_API_KEY` for backend elevation/geocoding.
- `.validation/env/frontend/.env`: `VITE_GOOGLE_MAPS_API_KEY` for 3D map context,
  and `VITE_MAPBOX_TOKEN` for the fallback map.
- Credentials must permit this test environment's origin and required APIs.
  `init-env` can read these three values from environment variables if supplied
  before invocation. It never retrieves secrets from Andrew's computer.

Map/network availability is an environmental prerequisite. Missing credentials
must produce a blocked result, not substituted terrain or a model failure.
No AI generation keys are required. The runtime explicitly disables paid
generation providers; use free exact-view capture only.

## Docker setup (recommended when Docker is available)

```bash
docker compose -f deployment/validation/compose.yaml config --quiet
docker compose -f deployment/validation/compose.yaml up --build -d
docker compose -f deployment/validation/compose.yaml logs --tail=40 api web
curl --fail http://127.0.0.1:8006/health
curl --fail http://127.0.0.1:5180/
```

The first build installs dependencies and may take several minutes. The compose
project is named `cityprompt-validation` and uses its own PostGIS, Redis and MinIO
volumes. The bootstrap migrates the empty DB, creates the test account, and seeds
**only the twelve exact Model Library assets**. It does not seed projects,
boundaries, streets, parks or student design geometry. Asset seeding is permitted
and required; all actual design authoring must happen through the UI.

Open **http://127.0.0.1:5180/login** in a browser in the same environment. API
health is **http://127.0.0.1:8006/health**. Do not use `npm run build`/production
preview for this review: fixed candidate assemblies intentionally require Vite's
development runtime. The supplied web service uses that runtime.

Stop this isolated test stack with `docker compose -f deployment/validation/compose.yaml stop`.
Do not use `down -v` if results/projects must be preserved.

## If the cloud container cannot run Docker

Do not claim a completed browser run. If local PostGIS, Redis and S3-compatible
storage are already available, install Python 3.11/3.12 and Node 22 dependencies:

```bash
python3 -m venv .validation/venv
. .validation/venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm ci --no-audit --no-fund && cd ..
```

Configure `.validation/env/backend.env` with those local service addresses,
retaining database **cityprompt_validation_20260924** and bucket
**cityprompt-validation-20260924**. Create the empty PostGIS database first;
the database role must be able to create the PostGIS extension. Change Docker
hostnames `db`, `redis`, and `media` to the actual local addresses. Then:

```bash
python scripts/validation_runtime.py bootstrap
python scripts/validation_runtime.py serve
# In a second terminal from the checkout:
cd frontend
CITYPROMPT_PUBLIC_DIR="$PWD/../.validation/public" VITE_ENV_DIR="$PWD/../.validation/env/frontend" API_PROXY_TARGET=http://127.0.0.1:8006 npm run dev -- --host 127.0.0.1 --port 5180 --strictPort
```

If neither route is available, report the exact environment blocker. Do not
regenerate stand-in models, substitute an older branch, or call offline checks
a student/browser pass.

## Test and report

Follow [the complete student prompt](CLAUDE_STUDENT_VALIDATION.md). Save output in
`.validation/claude-review/`. Report the Git SHA, asset hashes, environment and
whether results came from this rebuilt copy. Runtime renders/reference images
are under `.validation/evidence/<placement_id>/`; the JSON inventory contains
each `placement_id`. No paid image generation is needed.

Publisher checks: the exact packet was extracted and verified on Windows;
47 focused frontend tests passed; three packet integrity tests passed; compose
configuration parsed successfully. No browser session or complete Linux Docker
startup is claimed by these checks.
