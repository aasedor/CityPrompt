# Catalogue expansion Wave 2 review — 2026-08-19

## Start here

- Active worktree: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Active branch: `codex/catalogue-expansion-wave2`
- Local app: `http://127.0.0.1:5174/`
- Review gallery: `http://127.0.0.1:4174/`
- Gallery source: ignored `artifacts/catalogue-expansion-wave2/index.html`
- Publish status: local only; do not push without explicit user approval.

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

## Verified state

- Ten of ten structural validation reports pass with no errors.
- All 70 declared GLBs have valid `glTF` headers and are below the 75 MB upload cap.
- All 70 measured GLB bounds start at exactly `bottom_y = 0.000 m`; no family is
  floating or sunk relative to the City Prompt bottom-centre contract.
- Stack height, finite bounds, footprint allowances, and module-height contracts
  pass through `validate_outputs.py`.
- The latest quality memory is
  `2026-08-02-clean-3d-no-prisms-runtime-v118`.
- Forty-seven focused Wave 15 and catalogue-workflow regression tests pass.
- The only remaining quality finding on every family is the intentional visual
  gate: `photoreal_skin_approved` and `human_visual_approval` are still false.

`tools/archetype_compiler/prepare_family_review.py` safely upgrades older
manifests to the current evidence schema. It is dry-run-first and cannot grant
human approval.

## Continue safely

1. Open `http://127.0.0.1:4174/` and inspect the overview plus all ten full
   comparison boards.
2. Obtain explicit human approval for all ten, or a precise revision list.
3. If approved, run `approve_family_review.py --apply` for every manifest with
   the actual reviewer name. Never infer approval from the existence of renders.
4. Rerun `assess_wave15_families.py`; all ten must report `status: pass` and
   `high_quality_ready: true` with no findings.
5. Dry-run and then apply `tools/promote_compiled_families_to_seed.py` for the ten
   family directories. Confirm 70 unique new rows and object URLs.
6. Hydrate the running local stack and verify every object URL returns HTTP 200.
7. Test representative families through the live Draw Polygon → Generate to 3D
   path with map terrain enabled. Check contact with terrain and contacts between
   podium, repeatable floors, crown, and roof at several target sizes.
8. Run the focused compiler, backend, frontend, and TypeScript checks before a
   final local commit. Push only when explicitly requested.

If the gallery server is no longer running, restart it from the gallery source
directory with:

```powershell
python -m http.server 4174 --bind 127.0.0.1
```
