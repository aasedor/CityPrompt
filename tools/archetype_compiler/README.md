# Archetype Compiler

Turns a **real** building archetype from the SiteForge catalogue into a family of
reusable GLB modules (podium / alternating floors / setback / crown / roof), an assembled
preview building, and a preview render — deterministically, with Blender running
headless. The generated family is what the LEGO assembly planner
(`/api/v1/lego-assembly/plan`) stacks into buildings.

```text
buildingArchetypes.json + aestheticCatalog.ts   (existing source of truth)
        │  export_catalog.ts (vite-node — runs the app's own derivation code)
        ▼
archetype-source.json                            (full Urban Intelligence payload)
        │  compiler.py (deterministic derivation, every decision logged)
        ▼
grammar.json                                     (Building Grammar, schema v3)
        │  blender_generate.py (Blender 4.x/5.x headless)
        ▼
<family>_podium/floor variants/setback/crown/roof.glb + assembled.glb + preview.png + manifest
        │  validate_outputs.py (trimesh)
        ▼
validation_report.json                           (pass/fail gates the pipeline)
        │  import_manifest.py → POST /api/v1/lego-assembly/import-manifest
        ▼
ModelLibraryEntry rows with metadata.lego        (planner-ready modules)
```

## One command

Windows (friendly wrapper — checks Python/Node, installs frontend deps, finds Blender):

```powershell
.\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise"
```

Direct (any OS):

```bash
python tools/archetype_compiler/generate_family.py --archetype-id nordic_timber_midrise
```

Kinnaird-quality heritage pilot:

```bash
python tools/archetype_compiler/generate_family.py \
  --archetype-id london_heritage_mansion_block \
  --variant-id london-heritage-mansion-portland-stone \
  --floors 5 \
  --textures tools/archetype_compiler/textures_kinnaird_v6 \
  --presentation-engine cycles --presentation-samples 64
```

Useful flags: `--variant-id nordic_timber_charred_wood`, `--floors 6`, `--width 24
--depth 18` (clamped to catalogue bounds), `--output <dir>`, `--blender-path <exe>`,
`--skip-thumbnail`, `--keep-blend`, `--verbose` (prints every derivation note).

List every archetype id (223 buildings):

```powershell
.\scripts\generate-archetype-family.ps1 -List
# or: cd frontend && npx vite-node ../tools/archetype_compiler/export_catalog.ts -- --list
```

Register the generated family in the model library (backend must be running):

```bash
python tools/archetype_compiler/import_manifest.py build/archetypes/nordic_timber_midrise \
  --email you@example.com --password ...   # or --token / SITEFORGE_TOKEN
```

## How catalogue data maps to grammar

| Catalogue field | Grammar effect |
|---|---|
| `suggestedWidth_m` / `suggestedDepth_m` (+min/max) | module footprint; CLI overrides are clamped to the catalogue bounds |
| `minFloors` / `maxFloors` | floor range; default = midpoint |
| `suggestedFloorHeight` | floor height; podium = 4.5 m (retail) or ~1.25× floor height |
| `developmentType` / `generationTags` / `facadeDetail.groundFloor` | retail storefront podium vs residential lobby podium |
| `facadeDetail.primaryMaterial` etc. (prose) | keyword → PBR colour table (shou sugi ban → charcoal, CLT → warm timber, white plaster → off-white, …) |
| `palette.window` | glass colour |
| `roofDetail.form` / `styleProfile.roofForm` | flat / gabled / mono-pitch / mansard (+ parapet) |
| `roofDetail.material`/`features` | green roof, mechanical screen |
| `styleProfile.massing` + floors | setback floor on/off |
| residential type or balcony prose | balcony mode (projecting/recessed) + frequency |
| primary/secondary/ground-floor facade prose | facade system, reveal depth, feature bays, entrance type, balcony guard and planting rules |
| `generationStyleInput.downstreamHints.reuseKeys` | preserved verbatim into grammar, manifest, and library metadata |

Every decision is written to `grammar.json` → `notes[]` so you can trace a wall
colour back to the catalogue sentence that produced it.

## Coordinate contract

- metres; Blender source is **Z-up**; GLB export uses `export_yup=True`
- origin at **bottom centre** of every module (geometry spans ±w/2 × ±d/2 × [0,h])
- front facade faces **−Y in Blender** → **+Z in glTF** (toward the default three.js camera)
- transforms applied; one mesh node per module (`MOD_Podium`, `MOD_Floor`,
  `MOD_Setback`, `MOD_Roof`); materials named `MAT_*`
- bottom must sit within ±0.02 m of 0 (validated)
- footprint tolerance ±0.6 m; balconies may protrude the front up to 3 m; roof
  eaves may overhang up to 1.2 m (validated)

## Blender discovery

Order: `--blender-path` → `BLENDER_PATH` env var → `C:\Program Files\Blender
Foundation\Blender *\blender.exe` (highest version wins) → `/Applications/Blender.app`
→ `blender` on PATH. Tested on Blender 5.1; anything ≥4.2 should work.

## Expected output files

```
build/archetypes/<archetype-id>[--<variant-id>]/
  archetype-source.json      exported catalogue payload
  grammar.json               compiled Building Grammar (with notes[])
  <family>_podium.glb        \
  <family>_floor_typical_a.glb |
  <family>_floor_typical_b.glb |  one mesh node each, bottom-centre origin
  <family>_setback_upper.glb   |
  <family>_crown_crown.glb     |
  <family>_roof.glb           /
  <family>_assembled.glb     podium + floors (+setback) + roof stack
  <family>_preview.png       three-quarter daylight render (EEVEE)
  <family>_street.png        street-level facade review render
  <family>_aerial.png        roof/massing review render
  <family>_context.png       high-oblique urban-block review render
  <family>_manifest.json     module metadata + provenance + coordinate contract
  validation_report.json     pass/fail + measured extents
  logs/blender.log           full Blender output
```

## Tests

```bash
backend/.venv/Scripts/python -m pytest tools/archetype_compiler/tests/ -v
```

Unit tests always run; the export+compile smoke needs `frontend/node_modules`;
the full-pipeline smoke additionally needs Blender (skipped otherwise).

## Troubleshooting

- **"frontend dependencies are not installed"** → `cd frontend && npm install`
  (the .ps1 wrapper does this automatically).
- **"Blender was not found"** → install from blender.org or `set BLENDER_PATH=...`.
- **Validation FAIL** → read `validation_report.json`; each error names the file
  and the measured vs expected number. `logs/blender.log` has the full trace.
- **Garbled characters in the console** → cosmetic; the tools force UTF-8 where
  possible, but some archetype labels contain unicode dashes.

## Current visual limits

Generator v0.8 adds an architecture-specific `heritage_stone` kit and a true
mansard roof primitive. The kit includes deep occupied sash windows, rusticated
podiums, classical surrounds and pediments, projecting pavilions, quoins,
dentilled cornices, porticos, balustrades, dormers, chimneys, occupied corner
roof pavilions and a lantern. It also supports versioned GPT Image material
sources with deterministic PBR derivation and module AO bakes.

The generated modules are architectural visualization assets, not survey-grade
photogrammetry. Background-city realism comes from the tile layer; loose props,
vegetation and review-rig buildings remain deliberately lightweight. The new
detail can push assembled review GLBs above the 8 MB / 100k-triangle advisory
budgets, so a future rollout should add distance LODs rather than removing the
close-view geometry.
