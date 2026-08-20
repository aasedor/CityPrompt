# Catalogue expansion Wave 2 review — 2026-08-19

## Start here

- Active worktree: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Active branch: `codex/catalogue-expansion-wave2`
- Local app: `http://127.0.0.1:5174/`
- Review gallery: `http://127.0.0.1:4174/`
- Gallery source: ignored `artifacts/catalogue-expansion-wave2/index.html`
- Publish status: local only; do not push without an explicit user request.

The ignored root `.env` contains the frontend and server Google Maps keys copied
from the user's sibling City Prompt folder. The values were never printed or
committed. The local browser confirmed that the app recognizes the key and
loads the Google/Landsat map integration.

## Ten-family bounded batch

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

This roster covers seven previously uncovered parent programs plus three
distinctive sibling variants. Each family contains one fixed assembled GLB,
six semantic LEGO modules, registered source imagery, near/far PBR atlases,
locked review renders, a comparison sheet, a manifest, and validation/quality
reports.

## Approved and promoted state

- Ten of ten structural validation reports pass with no errors.
- All 70 declared GLBs have valid `glTF` headers and are below the 75 MB upload cap.
- All 70 measured GLB bounds start at exactly `bottom_y = 0.000 m`; no family is
  floating or sunk relative to the City Prompt bottom-centre contract.
- Stack height, finite bounds, footprint allowances, and module-height contracts
  pass through `validate_outputs.py`.
- The latest quality memory is
  `2026-08-02-clean-3d-no-prisms-runtime-v118`.
- Forty-seven focused Wave 15 and catalogue-workflow regression tests pass.
- Human approval is recorded for all ten families by `wbesh` with the note
  "Approved all ten from the local Wave 2 comparison gallery."
- All ten quality assessments now report `status: pass` and
  `high_quality_ready: true` with no findings.
- The durable seed contains 775 rows, including 70 Wave 2 rows. The 70 GLBs and
  ten previews are hydrated in the local object store.
- All 70 model URLs returned HTTP 200 with `glTF` magic headers.
- Promoted seed families are public catalogue modules. This was corrected after
  a clean-project test proved private seed rows were invisible to other project
  owners and caused fallback to an older broken market family.
- Exact-family planning passes for all ten families using the same
  project-scoped catalogue inventory as the browser.
- Live terrain QA placed the iron-and-glass market, 25-floor greenhouse tower,
  and steel-rib intermodal hub as detailed models without massing fallbacks.
  Their bases stayed on the sampled surface and no component floated, sank, or
  detached from its assembly.

`tools/archetype_compiler/prepare_family_review.py` safely upgrades older
manifests to the current evidence schema. It is dry-run-first and cannot grant
human approval.

## Live QA project

- Project: `Catalogue Wave 2 Terrain QA`
- Project id: `e861fdf4-1963-4528-a54a-ad90adc67ed1`
- Current final scene: `steel-rib-intermodal-hub`
- Earlier successful scene recipes in the same zone:
  `historic-iron-glass-market` and `glass-greenhouse-vertical-farm`

The tower and hub were deliberately exercised in the original 75.1 × 47.2 m
market footprint as a stress test, so their UI fit scores are low. Native-size
planner checks pass at 104.0 for all ten families.

## Continue safely

1. Treat all ten as approved, promoted, and locally hydrated.
2. Do not regenerate them unless a deliberate source revision is requested.
3. Run focused checks and inspect Git LFS status before publication.
4. Push only when the user explicitly requests it.

If the gallery server is no longer running, restart it from the gallery source
directory with:

```powershell
python -m http.server 4174 --bind 127.0.0.1
```
