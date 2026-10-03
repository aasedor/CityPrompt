# School and fourplex refinement — 2026-10-03

## Scope and state

Two original neighbourhood designs were refined as editable local 3D prototypes:
`school-v006` and `fourplex-v005`. The school has three classroom levels and an
attached gym. The fourplex has four separate dwellings over two levels. Each
contains furniture, enclosed rooms, open physical doorways, complete stairs,
roof details and a bounded planting scheme.

These are source-conditioned textured prototypes under RLASM v6.1. They are
outside the runtime/seed catalogue. They are not canonical texture-free clay
assets or approved textured keepers. The independent decisions and exact hashes
are recorded in the companion `NEIGHBORHOOD_REFINEMENT_2026-10-03.json`.

All generated files are external:

`C:/dev-artifacts/CityPrompt/neighborhood-refinement-2026-10-03`

The source branch is `codex/neighborhood-refinement`, based on church walking
commit `2f2c993669c94c25f5975c75fc192546be18dc88`. The original research worktree,
its pending reference images, the main dirty checkout, Wave 1/2 catalogue
reviews and the existing live project were preserved. No publication or push
was performed. No new image generation or paid provider calls were needed.

## What changed

**School:** unequal classroom sash, clear glazing, glazed entrance leaves and
transom, wider classrooms with desk rows/boards/books, corridor storage, complete
stair waists and guarded landings, a physical gym doorway with continuous floor,
court/hoop/net details, roof equipment screens, a graded entrance and varied
plant volumes. Original metric size remains an inferred 28 × 22 × 11.4 m.

**Fourplex:** two-tone source brick, a clear central stair window with the floor
properly cut back, open entry and four dwelling doors, bedroom and bathroom
partitions, showers, cooktops, refrigerators, beds and living furniture, solid switchback stairs,
roof vent boots, a graded entrance walk, shrubs and a young tree. Original metric
size remains an inferred 16 × 14 × 7.3 m.

`tools/neighborhood_refinement/` contains the generator, geometry helpers,
walking-network authoring, render boards, verification scripts and reproducible
standalone inspector. Its README includes commands and input paths. Heavy GLBs,
Blender scenes, source copies, material maps and images remain outside Git.

## Evidence

| Check | School v006 | Fourplex v005 |
|---|---:|---:|
| Exact exported/reimported GLB views | 19 | 18 |
| Actual app-solver routes | 6 passed | 15 passed |
| Furniture exclusion probes | 20 passed | 20 passed |
| Physical floor/head-clearance samples | 366 passed | 423 passed |
| Browser routes from embedded metadata | 6 passed | 15 passed |
| Source lock, carrier apertures, round-trip bounds | Passed | Passed |
| GLB triangles / merged meshes | 102,892 / 18 | 48,742 / 17 |

The standalone browser trial runs at `http://127.0.0.1:5201/`. Both models were
loaded, switched, hidden/shown, reloaded, and moved forward/back from the entrance.
Exterior and interior screenshots and browser route JSON are in each candidate's
`evidence` directory. The browser reported no warning/error console entries.
The inspector uses the actual app solver and untouched exported materials.
It does not validate main-app placement, globe terrain contact, arbitrary scale,
or terrain/building transitions. The live app on port 5199 was not changed.

Nineteen narrow Vitest tests passed across `buildingWalking.test.ts`,
`walkNavigation.test.ts` and `parkWalking.test.ts`. Python compilation and Node
syntax checks passed. No production TypeScript changed. Physical sampling checks
floor contact within 85 mm and 1.80 m head clearance along the recorded routes;
it is not an exhaustive collision or building-code certificate.

## Review limits and preserved history

Both independent reviews found zero remaining architectural/circulation P0/P1
findings for the local trial. Each model retains two P1 findings for full textured
keeper approval: conspicuous QA light reflections in glazing, and incomplete
source-specific material and landscape finish. The exact decisions remain in
the synchronized companion JSON and independent review files. Domestic fixtures
are schematic representations. Source images are original generated designs;
unseen sides and room plans remain explicit design inferences.

Failed school v003–v005 candidates remain external with their evidence. V004
exposed a second-flight solver conflict; v005 closed that conflict but still had
a physical floor gap at the gym passage. V006 closes that gap. Earlier source
pilots (`school-v002`, `fourplex-v001`) remain in the original
`neighborhood-essentials-2026-10-03` artifact root. Their decisions and files were
not overwritten. Fourplex v002 exposed rear window/partition and door/furniture
conflicts; v003 fixed those but failed the expanded bathroom routes. V004 was
stopped before export to fold in the shower-access and camera corrections. V005
widened the bathroom doorway, cleared fixture access, and passed all 15 routes. The companion JSON records their supersession relationships.

Any further finish pass must use a new candidate version, a complete render set,
and another independent holistic review. Catalogue promotion remains subject to
the existing explicit human approval boundary.
