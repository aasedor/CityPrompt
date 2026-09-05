# City Prompt performance and bloat review

**Date:** 2026-09-04
**Scope:** student-facing frontend startup, project-editor route, Google 3D scene,
runtime building assets, deployment payload, and this workstation's local
development services.

## Outcome

City Prompt's slow feeling comes from three separate costs:

1. The application shipped large editor engines and the full archetype
   catalogue before they were needed.
2. The live 3D scene can download very large building models and continuously
   renders an expensive Google Tiles scene.
3. The local development setup polls a large OneDrive-backed tree and currently
   has extra Docker and WebGL review services running.

The first set of safe bundle and watcher corrections is implemented on
`codex/performance-bloat-review`. The model and render-loop changes should be
handled as separate measured initiatives because they can affect architectural
appearance, grounding, and render fidelity.

## Measurements

### Frontend JavaScript

The baseline production build transformed 3,466 modules and emitted 8,117.8 KiB
of minified JavaScript. Opening the project editor made the browser eligible to
load about 7.8 MB of minified JavaScript (about 2.0 MB gzip), including:

| Baseline chunk | Minified | Gzip |
| --- | ---: | ---: |
| Archetype catalogue | 3,319.8 kB | 677.4 kB |
| Mapbox | 1,680.4 kB | 463.5 kB |
| Project editor | 1,277.4 kB | 377.3 kB |
| Three.js | 688.5 kB | 177.7 kB |
| React Three Fiber / Drei | 500.5 kB | 165.9 kB |

The object-form Rollup chunk configuration also absorbed React into the
`react-three` chunk. The login and project-list shell therefore downloaded
Three.js and React Three Fiber even though those pages render no 3D content.

After assigning manual chunks by module ID, keeping dependencies explicit, and
making the 2D and 3D maps separate lazy entries:

- initial shell JavaScript is 447.6 KiB minified, approximately 141 kB gzip;
- the prior shell path was about 1.50 MB minified, approximately 438 kB gzip;
- the reduction is about 70% minified and 68% gzip;
- the default 3D project route no longer statically imports the 463.5 kB gzip
  Mapbox engine;
- the project editor chunk fell from 1,277.4 kB to 1,204.1 kB.

The full build is still 8,115.7 KiB because code splitting changes when code is
loaded rather than deleting optional functionality.

### Archetype catalogue

The browser bundle contains the complete render metadata for 469 archetypes:

| Source | Entries | Source JSON |
| --- | ---: | ---: |
| Buildings | 224 | 2,309.4 KiB |
| Streets and paths | 115 | 794.9 KiB |
| Parks and open spaces | 130 | 767.8 KiB |

Those JSON files are imported by the editor, legend, render preparation,
street-view rendering, and direct-3D reference code. Rollup deduplicates the
data, but the browser still downloads and parses a 3.32 MB minified catalogue
chunk before a student chooses an archetype.

The catalogues reference 2,176 unique PNGs. The hydrated local copies total
about 2.8 GiB, with a median file size of 1.3 MiB. The picker uses lazy image
loading, so these images do not all transfer on page open. They still make
deployment, cache storage, and broad catalogue browsing unnecessarily heavy.

### Runtime building models

The seeded library contains 70 public compiler models totaling 1.37 GiB:

| Metric | Current value |
| --- | ---: |
| Median model | 16.1 MiB |
| 90th percentile | 40.0 MiB |
| Largest model | 55.1 MiB |
| Models with more than one LOD URL | 0 |
| Models using Draco | 0 |
| Models using Meshopt | 0 |
| Models using KTX2/Basis | 0 |

Embedded images account for about 1.36 GiB of the 1.37 GiB total. The problem
is overwhelmingly texture packaging rather than mesh geometry.

The globe's detailed-building budget is 20. Twenty median-sized, distinct
models can therefore represent roughly 322 MiB of model transfer before Google
Tiles and park/street assets. Twenty 90th-percentile models would be roughly
800 MiB. Browser caching helps repeat visits, but it does not solve the first
load or GPU texture-memory pressure.

### 3D frame work

The globe canvas currently uses:

- the default continuous React Three Fiber frame loop;
- device pixel ratio up to 2;
- antialiasing, shadows, a logarithmic depth buffer, stencil, and
  `preserveDrawingBuffer`;
- Google Photorealistic 3D Tiles plus environment lighting;
- 14 declared `useFrame` callbacks across building, LEGO, street, park, zone,
  residual-landscape, and shared-ground systems.

Some callbacks stop after terrain convergence, but other work remains active.
Building material LOD checks run for each detailed model on every frame, and
layer LOD selection checks every 60 frames.

Grounding is intentionally expensive. A site boundary can request a 1,200-point
surface grid, needs two stable passes, and performs recursive raycasts into
triangle-heavy visible Google tile scenes in batches capped at 4 ms per frame.
This protects the placement accuracy that City Prompt needs, but it can create
visible jank while a scene settles.

### Repository and deployment payload

`frontend/public` currently contains 26,149 files totaling 22.69 GiB:

| Folder | Files | Size |
| --- | ---: | ---: |
| `families` | 17,877 | 16.16 GiB |
| `archetypes` | 6,840 | 6.39 GiB |
| `park-skins` | 1,317 | 0.07 GiB |
| `park-kits` | 92 | 0.04 GiB |

25,795 public files are tracked, mostly through Git LFS. A browser does not
download this tree automatically. However, Vite copies its public directory
into a production build, and the checked-in Render configuration publishes
`frontend/dist`. The production asset boundary therefore risks turning
source images, review evidence, and every family variant into deployment
payload.

The separate seeded model-library checkout is another 5.85 GiB. It belongs in
object storage and a versioned runtime manifest, not in a frontend deployment.

### Local development overhead

- The first sampled Vite HTML request took 425 ms; the immediately repeated
  request took 11 ms. This points to cold transform/filesystem work rather than
  a slow HTML handler.
- The active Vite process had about 423 MiB private memory and 146 MiB working
  set during the review.
- Vite was configured to poll once per second while only two public
  subdirectories were ignored. The hydrated public tree has more than 25,000
  files.
- An older Docker backend on port 8000 is still running with file watching. Its
  watcher encountered a Windows/OneDrive I/O error and restarted.
- Two architectural-clay galleries are running on ports 4176 and 4177. Each
  gallery uses a permanent WebGL animation loop even while its model is idle.

The browser console showed no warnings or errors in the student project. The
active backend also responds; the extra services are local resource pressure,
not evidence of a production application failure.

## Changes implemented

1. Manual chunks now classify packages by module path and use
   `onlyExplicitManualChunks`. React remains in a normal React chunk, so
   non-3D pages do not import Three.js.
2. `SitePlannerMap` and `GlobeSitePlannerMap` are lazy map entries. The
   current default globe path does not fetch Mapbox.
3. Vite emits a build manifest and the budget checker now enforces:
   - initial JavaScript below 600 KiB;
   - no Three, React Three, Mapbox, or catalogue chunk in the app shell;
   - no Mapbox chunk in the default project route;
   - total JavaScript below 8.25 MiB;
   - largest chunk below 3.5 MiB.
4. The development watcher ignores the whole public asset tree. Public files
   are served verbatim and do not need HMR.

## Recommended implementation order

### 1. Build real delivery LODs and compressed textures

Make runtime delivery a required compiler stage:

- preserve full-resolution source and review GLBs outside the runtime library;
- package close-view textures with KTX2/UASTC and district/map textures with a
  smaller KTX2 profile;
- generate distinct hero, neighbourhood, and map LOD files;
- deduplicate textures and repeated family modules;
- enforce byte, triangle, texture-memory, and draw-call budgets before
  promotion;
- load the map LOD first and replace it with the close LOD only when camera
  distance and a scene-wide byte budget allow it.

Initial delivery targets should be tested visually, then made contractual:
map LOD at or below 1.5 MiB, close LOD normally below 8 MiB, and no single
catalogue model above 12 MiB without an explicit exception.

### 2. Replace the monolithic browser catalogue

Ship a small index containing only ID, title, category, suitability, dimensions,
thumbnail URL, and availability. Fetch the selected archetype's render prompts
and full reference set on demand. Fetch only the archetypes needed by the
current plan before render preparation. Use 256- or 384-pixel WebP/AVIF
thumbnails rather than full PNG references in catalogue grids.

The first target is to reduce the 677 kB gzip catalogue chunk below 150 kB gzip
for editor startup.

### 3. Make globe quality adaptive

Instrument before changing fidelity. Record frame time, FPS, visible tiles,
draw calls, triangles, texture memory, model bytes, ground-sampling state, and
camera motion in a development overlay and automated scene benchmark.

Then:

- render at DPR 1 while moving/drawing and raise quality after the camera rests;
- reserve DPR 2, full shadows, and preserved capture buffers for export;
- replace probabilistic and every-frame terrain retries with explicit,
  invalidation-driven state machines;
- use a coarse grounding surface for immediate editing and refine/persist the
  full surface before clean capture;
- stop per-model distance work when the camera has not moved;
- move toward a demand-driven frame loop after every frame-dependent sampler
  has an explicit wake-up mechanism.

This sequence keeps placement accuracy while removing idle GPU work.

### 4. Separate runtime assets from source and review evidence

Publish a reviewed runtime manifest to object storage/CDN. The frontend build
should contain the app shell, tiny UI assets, and catalogue thumbnails only.
Family source files, comparison boards, intermediate renders, and rejected
variants should stay in artifact storage. Add deployment checks for total
public bytes and for accidentally promoted source/review folders.

### 5. Finish route-level feature splitting

The default project chunk still contains render, video, LEGO, report,
street-view, and full catalogue logic. Load those panels when their buttons are
opened. The legacy Mapbox branch has no current UI switch and should either
remain an isolated fallback route or be removed after confirming no course
workflow depends on it.

## Verification completed

- Production build: passed, 3,466 modules.
- Bundle budget: passed, including route-graph checks.
- TypeScript `tsc --noEmit`: passed.
- Vite environment tests: 3 passed.
- Running student project: 3D map, buildings, park, controls, and lazy globe
  entry loaded successfully.
- Browser warnings/errors after the change: none.
