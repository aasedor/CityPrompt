# Company review handoff — 29 October 2026

Use an explicitly supplied review commit and its matching assets. The reviewed
desktop is usable locally, but it depends on an ignored runtime profile,
external hydrated files and existing database/storage state. This document does
not claim a fresh-machine installation, hosted deployment or paid-provider test.
Cloning `main` does not necessarily retrieve the local review commit.
See the [verification checkpoint](HANDOFF_VERIFICATION_2026-10-29.md) for exact
passes, the open total-JavaScript budget gate, and unfinished browser checks.

## What must accompany the review

- The exact Git commit and access to its source and required Git LFS objects.
- A freshly prepared portable asset packet (`assets.json` and `public/`), or
  permission for the recipient to fetch the finite required LFS inputs.
- For a hosted review, a production frontend built for the intended HTTPS API
  origin and restricted browser key, with its build receipt and `version.json`.
- A configured API, migrated database and exact Model Library objects/bindings.
  Frontend assets do not contain the private database, accounts or project media.
- Private credentials supplied through the recipient's own environment. Do not
  send desktop dotenv files or copy a developer's runtime profile verbatim.

The freshly prepared October 29 packet contains 3,723 files and 1,667,410,799 bytes (about
1.55 GiB), before packaging. This is storage size, not initial page download.
A 500 MB complete packet is not established. The older October 28 packet is stale against
the current source and must not be relabelled or reused without validation.
No current source/asset handoff download location has been established here.

## Prepare the portable frontend

These commands prepare files; they do not deploy, seed a database or approve
catalogue entries. Run from the supplied checkout with Node.js, installed locked
dependencies, Python and Git LFS. Use new external output directories. The
`--fetch-lfs` option downloads the selected tracked objects rather than all
historical artwork; it requires authorized repository/LFS access.

```powershell
git rev-parse HEAD
git status --short --branch
npm ci --prefix frontend
python scripts/hosted_assets.py --output C:/CityPrompt-review/assets-20261029 --fetch-lfs
```

For a hosted frontend, supply `VITE_API_URL` (HTTPS API origin without `/api`)
and `VITE_GOOGLE_MAPS_API_KEY` privately in the build environment first. Preserve
the packet's selected `VITE_CLAUDE_FIVE_TRIAL` profile. Then:

```powershell
python scripts/build_hosted_frontend.py --assets C:/CityPrompt-review/assets-20261029 --output C:/CityPrompt-review/dist-20261029 --work-dir C:/CityPrompt-review/build-evidence-20261029
```

The build validates packet fingerprints and payload hashes and refuses stale
inputs. It also hydrates the tracked landing media imports from their exact LFS
objects; overriding the public directory alone does not provide those source
imports. Keep the completed build and receipt together. A static build needs
the configured API and SPA hosting; opening `index.html` from disk is not a
complete application installation. Use the
[hosted release procedure](RENDER_RELEASE_2026-10-13.md) and its
[build/data-transfer details](RENDER_RELEASE_2026-10-07.md#reproducible-build-and-asset-delivery)
for hosting. Historical catalogue counts in those reports are not current counts.

## Run a Windows developer review

The prepared production packet covers **186 production choices** (92 buildings,
41 parks and 53 streets). The current development browser exposes **201 choices**
(105 buildings, 43 parks and 53 streets). Its fifteen additional choices are
seven local teaching buildings, five Claude buildings, the twisting glass tower,
beach-volleyball courts and the stepped terraced plaza. They are real asset
dependencies. The production packet alone does not certify this larger local
review profile; supply and audit its exact supplement before claiming desktop
parity. Production publication remains separate from local review visibility.
The development-only stepped terraced plaza still records one unresolved P1
visual finding (`rework_required`) and pending runtime review in its release
manifest. Local visibility and successful file delivery do not approve it for
publication. The company handoff baseline is the 186-choice production profile;
the additional fifteen local choices remain outside that baseline.

Use a separate checkout and review database/storage. Install the frontend and
backend dependencies from their locked/package requirements. Configure backend
connections and secrets privately using `.env.example`; configure the frontend
browser key in an external directory containing `.env`. The frontend needs
`VITE_GOOGLE_MAPS_API_KEY`; backend address/elevation features need
`GOOGLE_MAPS_API_KEY`. `MAPBOX_ACCESS_TOKEN` in the root configuration supplies
the Compose fallback map token; direct Vite uses `VITE_MAPBOX_TOKEN`.

After preparing the packet above, create ignored `artifacts/local-runtime.json`
with paths that exist on the recipient's machine. This is a template, not a
copy of the current desktop configuration:

```json
{
  "schema": "cityprompt.local-runtime@1",
  "port": 5174,
  "apiProxyTarget": "http://127.0.0.1:8000",
  "envDir": "C:/CityPrompt-review/frontend-env",
  "publicDir": "C:/CityPrompt-review/assets-20261029/public"
}
```

Leave `infrastructureContainers` unset to use the launcher's standard local
containers. Set it only when deliberately reusing three existing review
database, Redis and storage containers with matching backend connection settings.
The profile's `envDir` configures Vite; it does not configure the backend.

Before opening the frontend, the target database must be prepared with the
current migrations. The Windows launcher runs `python -m scripts.prepare_database`
from `backend/`; the hosted API startup/pre-deploy procedure does the same.
The generic Compose API command currently invokes Uvicorn directly and does
not run that bootstrap. Do not interpret `/health` alone as operational readiness.

The exact approved Model Library seeds must also be installed into the target
database and bucket. This is a separate data operation: the launcher checks
storage and refuses an incomplete catalogue, but does not create all bindings.
Use the finite candidate selection, dry run, conflict refusal and `--verify`
workflow in the
[seed handoff](RENDER_RELEASE_2026-10-13.md#exact-private-model-seed-handoff).
Resolve any remaining local-only approval gate before a remote installation.
The older `scripts/validation_runtime.py` bootstraps a named September validation
database and twelve bindings; it is not the current full-catalogue installer.

After the database/storage preparation, run:

```powershell
.\scripts\start-local-city-prompt.ps1
Invoke-RestMethod http://127.0.0.1:8000/ready
```

The launcher manages consumers for `celery`, `direct3d`, `direct3d-maintenance`
and `classroom-documents`, plus one Celery beat scheduler. Its `/ready` wait
checks operational dependencies and enabled worker/recovery requirements.
The generic Compose worker command and lack of beat service do not provide
this complete queue/recovery configuration. Review at
`http://127.0.0.1:5174/`; the generic Compose frontend uses port 5175 instead.

## Read-only acceptance and known limits

From the checkout, with the same backend environment as the running API:

```powershell
$env:CITYPROMPT_PUBLIC_DIR = 'C:/CityPrompt-review/assets-20261029/public'
node frontend/scripts/check-catalogue-delivery.mjs --report=C:/CityPrompt-review/catalogue-delivery.json
python scripts/check_model_library_storage.py --require-catalogue --report C:/CityPrompt-review/model-library-storage.json
```

For a hosted target, use the explicit target-storage verification and URL audit
in the hosted release procedure. A local source-asset audit is not hosted
storage readback or browser acceptance.

The October 29 production-profile audit of the existing hydrated desktop root found
**186 production catalogue choices, 578 distinct image/model dependencies and zero
failures**. Catalogue JSON/model-contract checks passed; the citywide policy-map
check found 12 maps and 724 hydrated images. These results certify that local
asset source, not a new machine. The Beltline concept maps are tracked source
JSON addressed by Vite `new URL(..., import.meta.url)` imports; they do not
depend on the desktop public directory or PDF extraction at runtime.

Two broader gates remain visibly failed: the historical runtime manifest's
hydration check reported 1,981 required files missing or still LFS pointers in
that external root, and hydrated publication preflight in the source checkout
encountered an unhydrated reference image. The metadata-only publication check
now passes for 81 buildings after the comparator was corrected to recognize
equivalent finite numeric spellings; changed values, strings and wrapper code
still fail. The active catalogue audit passing does not turn the separate
hydration checks into passes. Preserve their evidence and resolve the applicable
gate before claiming publication readiness.

Finish with a browser rehearsal on the recipient's actual installation: sign
in, create a site, inspect zoning/policy, place building/park/street/details,
edit dimensions and supported storeys, walk, save/reload, delete/undo, and
export a free source preview. Confirm the frontend/API commit identities and
all asset/storage audits. Test paid images/video only within a separately
agreed finite allowance. Existing local success is not evidence that those
recipient checks have run.
