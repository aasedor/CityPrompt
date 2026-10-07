# Neighbourhood refinement pilot

This bounded RLASM v6.1 pilot contains one school and one fourplex. It builds
editable Blender scenes, GLBs with native walking metadata, exact-export review
renders and an isolated browser inspector. It does not update the runtime or seed
catalogue. See `docs/NEIGHBORHOOD_REFINEMENT_2026-10-03.md` and its JSON companion
for the reviewed versions and remaining limitations.

## Inputs and outputs

The reference checkout must contain the original front design and its generated
oblique/roof continuations at:

```
frontend/public/archetypes/buildings/neighborhood-elementary-school/variant_0*.png
frontend/public/archetypes/buildings/neighborhood-fourplex/variant_0*.png
```

The output root must already contain `materials/red_brick.png`,
`materials/buff_brick.png`, and `reference-generation.json`. The recorded local
inputs are in `C:/dev-artifacts/CityPrompt/neighborhood-refinement-2026-10-03`.
Reference authority remains in the preserved `neighborhood-essentials` worktree.
Each candidate copies its three source images, materials and generation prompts;
the source manifest records hashes and original paths. Rear layouts, room plans
and metric dimensions are design assumptions.

Blender 5.1, Python with Pillow, and the repository's installed frontend
dependencies are required. Run from the repository root in PowerShell:

```powershell
$artifactRoot = 'C:/dev-artifacts/CityPrompt/neighborhood-refinement-2026-10-03'
$referenceRepo = 'C:/Users/andre/.codex/worktrees/neighborhood-essentials/CityPrompt'
$blenderExe = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $blenderExe --background --python tools/neighborhood_refinement/build_neighborhood.py -- --kind school --version v007 --output-root $artifactRoot --reference-repo $referenceRepo --dry-run
# After inspecting the dry run, execute the same command without --dry-run.
```

Use `--kind fourplex` for the second family. Always choose a new version; the
builder refuses to reuse an existing candidate directory. Geometry construction
precedes material-role merging. The saved `.blend` retains editable component
objects. The GLB embeds the walking network; the matching JSON is preserved in
`evidence/walking-network.json`. Renders use that exported GLB reimported into
Blender, with no geometry or material substitution. QA lights are not exported.

## Review and walking checks

```powershell
$candidate = "$artifactRoot/school-v006"
node tools/neighborhood_refinement/check-walking.mjs $candidate
& $blenderExe --background --python tools/neighborhood_refinement/check-physical-walk.py -- $candidate
python tools/neighborhood_refinement/boards.py $candidate
node tools/neighborhood_refinement/preview.mjs $artifactRoot 5201
```

The inspector is served only on `127.0.0.1`. It copies its two UI source files
into the external root and imports the app's actual `parkWalking.ts` solver.
Select a model, inspect exterior/interior cameras, use **Walk from entrance**,
and move with W/S (A/D turns) or the half-metre step buttons. The route button
tests the walking metadata embedded in the loaded GLB. This is a standalone
asset trial; project placement, globe terrain, scale transforms and transitions
between terrain and building navigation are outside its scope.

The Node check exercises the app solver and furniture exclusions. The Blender
check raycasts sampled solver positions against the actual exported geometry
for floor contact within 85 mm and 1.80 m head clearance. It does not prove every
possible route or certify building-code compliance. The reviewed school has six
routes; the fourplex has fifteen. Keep these records separate from independent
visual approval.

## Source ownership

`build_neighborhood.py` retains the original two-family composition and calls
`refinements.py` for the corrected openings, program, stairs and landscape.
`geometry_core.py` is the unchanged low-level utility inherited from the earlier
pilot. `walking.py` authors metre-scale Z-up surfaces; the app handles its own
coordinate conversion. Candidate script snapshots preserve the generating
versions, including earlier failed revisions. Heavy assets and review images
stay outside Git. Any further candidate needs complete renders, phone/source
boards and an independent holistic review before a keeper decision.
