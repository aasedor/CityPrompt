# Catalogue expansion handoff — updated 2026-08-20

## Start here

- Active worktree: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Active branch: `codex/catalogue-expansion-wave2`
- Current local checkpoint before approval/promotion: `737bb2ca6`
- Canonical integration remote/branch: `cityprompt/main`
- Full Wave 2 evidence: `docs/CATALOGUE_EXPANSION_WAVE2_REVIEW_2026-08-19.md`
- Local app: `http://127.0.0.1:5174/`
- API health: `http://127.0.0.1:8000/health`
- Wave 2 review gallery: `http://127.0.0.1:4174/`
- Publish status: pushed to `origin/codex/catalogue-expansion-wave2` on
  `aasedor/CityPrompt`; not merged into `main`.

Do not use `C:\Users\wbesh\OneDrive\Documents\ChatGPT\Cityprompt` as a source
worktree. It is a redirect for older Codex tasks. The redirect's `AGENTS.md`
points new tasks here.

The ignored root `.env` contains the frontend/server Google Maps keys copied
from the user's sibling City Prompt folder. The values were never printed or
committed. The local browser loaded Google/Landsat tiles successfully.

## Current Wave 2 state

The ten-family Wave 2 batch is human-approved by `wbesh`, quality-passing, and
promoted into the durable seed catalogue:

1. `copenhill-ski-slope-energy-plant`
2. `parametric-wave-natatorium`
3. `second-empire-clocktower-city-hall`
4. `glass-greenhouse-vertical-farm`
5. `steel-rib-intermodal-hub`
6. `monumental-silo-cluster`
7. `titanium-fold-art-museum`
8. `historic-iron-glass-market`
9. `bronze-curve-concert-hall`
10. `deconstructivist-concrete-fire-station`

Each family contains one fixed assembled GLB, six semantic LEGO modules,
registered source imagery, near/far PBR atlases, locked review renders, a
comparison sheet, a manifest, and validation/quality reports.

- Seed catalogue: 775 rows total; Wave 2 contributes 70 deterministic rows.
- Object storage: 80 Wave 2 objects (70 GLBs and 10 previews) are hydrated.
- Every Wave 2 GLB URL returned HTTP 200 and a `glTF` magic header.
- All 70 measured bounds begin at `bottom_y = 0.000 m`.
- All ten structural and quality assessments pass against memory
  `2026-08-02-clean-3d-no-prisms-runtime-v118`.
- All ten select their exact family through the project-scoped live catalogue
  planner at native dimensions.
- Live Draw/Generate-to-3D testing placed the iron-and-glass market, 25-floor
  greenhouse tower, and steel-rib intermodal hub as detailed buildings with no
  massing fallback. Visual map checks showed ground contact and no detached or
  exploded components.

The live test exposed and fixed an important clean-user bug: promotion had
marked shared seed catalogue rows private to the seed owner, causing a new
project to select an older broken market family. Promoted families are now
public by default, with a regression assertion. Existing local Wave 2 rows were
updated to public and the market rebuilt as `historic-iron-glass-market`.

The Windows launcher was also hardened: if the `uvicorn` console shim is not on
PATH but the Python module is installed, it now starts the API with
`python -m uvicorn`. The launcher was exercised successfully.

## Wave 1 baseline

The earlier four-family pilot remains approved and promoted:

- `modern-black-screen-machiya`
- `red-machiya-cafe-gallery`
- `mid-century-wood-stone-pavilion`
- `mid-century-white-brise-soleil-pavilion`

That pilot measured roughly 63–75% smaller modular files, about 5x faster
modular rebuilds, and planning calls around 2.6 seconds instead of 26.5 seconds
(about 10x faster). Treat those figures as measured pilot results, not a
guarantee for every archetype.

## Continue safely

1. Confirm this worktree and branch, then read this file and the Wave 2 review.
2. Do not repeat visual approval or regenerate the ten families unless their
   source manifests intentionally change.
3. Run focused compiler/backend tests and inspect Git LFS status before any
   publication.
4. The Wave 2 branch is published. Do not merge it or publish later changes
   without a new explicit user request.
5. For another catalogue wave, preserve the bounded sequence: generate,
   validate, render, human review, explicit approval, promote, hydrate, then
   live map/terrain QA.

Never copy API keys into documentation, source, manifests, logs, or Git
history.
