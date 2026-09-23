# Runtime integration review — neighborhood_park_v2 furniture

## Candidate and scope

- Park/open space: `neighborhood_park`, exact variant `neighborhood_park_v2`.
- First procedural revision: `meadowFurnitureGeometry.ts`, SHA-256
  `b51e4d879cc36dcf0569c35f73686144d88f73780bbf1e84ffecfe6bf9579855`.
- Runtime: commit containing this report, based on `8a83cbf41`, branch
  `codex/public-realm-visual-pilot`; integration checklist dated 2026-09-20.
- Agent visual review, 2026-09-22, desktop pointer, 1264 × 625 viewport.
- Existing disposable project: `54818ada-581f-4643-900a-78867b076c8c`,
  http://127.0.0.1:5176/projects/54818ada-581f-4643-900a-78867b076c8c .
  Previously vacant irregular Currie parcel, four buildings, greenway, meadow
  park and rain garden. No protected fixture edits or API-authored geometry.
- Furniture replaces existing placements in the approximately 50 × 40 m park.
  Metres, Z up, base zero plus the shared program lift. Uses the existing uniform
  placement scale, yaw and terrain offsets; no new routes, pads or scatter.
- Four opt-in meshes: bench, picnic table, bin, path light. One instanced draw
  per kind, fewer than 1800 triangles each, no added texture or asset requests.
  Horizontal radii remain within existing 1.15 / 1.42 / 0.4 / 0.34 m envelopes
  respectively before uniform instance scale. Rigid furniture is not terrain-bent.
- Prepared-site visual smoke only. Natural-ground placement still relies on
  the existing support pipeline; this pass does not certify its slope behavior.
- Local visual pilot; publication and independent human asset approval not given.

## Gates

| Gate | Status | Evidence / limitation |
| --- | --- | --- |
| C1 Exact identity | PASS | Saved exact variant readback; opt-in renderer; sibling defaults unchanged |
| C2 Dimensions and transformations | NOT TESTED | Geometry envelope and metric-base regression passes; full UI transformation matrix unrun |
| C3 Full footprint ground support | NOT TESTED | Prepared-site close view only; unchanged support pipeline |
| C4 Freshness and late results | NOT TESTED | Reload smoke only |
| C5 Pedestrian continuity | NOT TESTED | Existing routes and placements unchanged; close view is not a full route inspection |
| C6 Edit / Undo / save / reopen | NOT TESTED | Reopen smoke passed; no new design edits, full recovery matrix not repeated |
| C7 Failure and recovery | NOT TESTED | No injected ground/save failure |
| C8 Low/aerial views and capture | NOT TESTED | Close and aerial scene smoke completed; free capture produced preview; final downloaded bytes not verified |
| C9 Student controls and inputs | NOT TESTED | Visual replacement only, no new controls |
| B1–B5 | N/A | No building change |
| S1–S4 | N/A | No street change in this commit |
| P1 Exact program and rigid amenities | PASS | Same placement topology; geometry bounds tests; photographed runtime components |
| P2 Shared park terrain | NOT TESTED | Prepared-site smoke only |
| P3 Automatic remeasurement | NOT TESTED | No terrain solver or placement change |
| P4 Park access and grade review | NOT TESTED | Existing connections retained; natural grade matrix unrun |

## Bounded live matrix and evidence

External local directory:
`C:/dev-artifacts/CityPrompt/sol-empty-lot-trial-2026-09-22/browser/`

- `73-meadow-furniture-first.png`: native Currie scene with picnic tables,
  timber-clad bin and capped lights after reload.
- `74-meadow-furniture-close.png`: second closer view.
- `77-meadow-furniture-kit.png`: separate component review using the actual
  runtime generator, neutral ground and lighting. This is not Google Tiles or AI.
- `75-meadow-furniture-kit.png` records an initial Vite access restriction,
  not a successful visual review. The reviewer was then served inside Vite's
  existing frontend root and removed after use; no serving policy was relaxed.
- Review HTML retained in ignored `artifacts/meadow-furniture-review.html`.

These are local-only evidence, not a durable shared delivery. The existing
browser accumulated historical asset/material errors, so console cleanliness
is not claimed. The ordinary free export created a preview, but download was
cancelled by the automated browser. A native Windows download-path retry did
not produce a verified file; the browser connection subsequently became
unavailable. This pass does not claim a successful download or attribute the
browser termination to the application. No paid calls or credit changes.

## Classroom impact and decision

Agent simulation, not independent novice testing. The small meadow park's
existing recipe omits a pavilion below its area threshold; its ground pad remains.
This is recorded follow-up, not solved by shrinking a pavilion or bypassing fit.
The kit adds finer timber slats, connected supports and armrests, a recessed bin
opening and a capped luminaire. Construction/accessibility certification is not
claimed. The picnic table has recessed supports; it is not an accessibility claim.

154 tests passed across `meadowFurnitureGeometry`, `parkMicrodetailFamilies`,
`parkScatter`, `parkLegoFamilies`. `npm run type-check` passed after final behavior
changes. React review: memoized geometry, instanced rendering, layout-time matrix
updates, StrictMode-safe deferred disposal, no per-frame allocations or new fetches.

Runtime decision: bounded visual checkpoint; full acceptance NOT REVIEWED.
Asset decision: agent-reviewed prototype; human decision open.
Next bounded action: recover a browser session and verify an actual downloaded
exact image, then use the furniture in one further compatible park variant with
its own appearance, dimensions and terrain review. Keep other variants opt-out.

## Bounded expansion — three additional pieces

Following the user's positive review of the original furniture and request for
more, the next local batch adds three pieces in the same timber/charcoal palette:

| Geometry kind | Dimensions / envelope | Integration status |
| --- | --- | --- |
| `backless_bench` | 1.86 m long, 0.49 m high; 1.15 m horizontal envelope radius | Reusable component, not automatically scattered |
| `bike_rack` | Three inverted-U hoops, 0.6 m centres, approximately 0.94 m high; within 1.02 m radius | Replaces only the meadow variant's existing rack at its current scale, yaw and ground offset |
| `planter` | Approximately 1.61 × 0.60 m container, 0.61 m rim; grass under 1.4 m total; 0.9 m envelope radius | Reusable component, not automatically scattered |

The planter has actual side cladding, rim, recessed soil and blade geometry,
including the existing deterministic botanical colours. No image textures or
provider calls. All seven furniture geometries stay below 1800 triangles each
and share the same instanced renderer. Existing four designs are unchanged.
Do not scatter the two new candidate pieces without reserving their full
envelopes, testing support and reviewing route clearance. The rack envelope
covers the metalwork, not parked bicycles: bike occupancy needs its own clearance
review before representing bicycle capacity or a dimensioned parking layout.

Expanded working source SHA-256:
`9e1a98b7cfcccfcc0bee5f1a6a4a964b426649c58594fdf5ba83ec0ec1253acf`.
Base commit: `cfb6d8646`; source revision is the commit containing this appendix.
32 focused tests passed (`meadowFurnitureGeometry`, `parkMicrodetailFamilies`);
TypeScript passed. Browser component review had zero captured page errors.

Evidence: `79-meadow-furniture-expansion.png` in the external directory above,
showing the actual runtime geometry under neutral review lighting. The rack is
rotated in this review composition to expose its open hoops. Review generator:
ignored `artifacts/meadow-furniture-expansion.html`. Temporary frontend review
page removed after inspection. No images added to Git.

C2 component dimensions and deterministic geometry: PASS within stated bounds.
C8 isolated visual review: PASS; in-site review of the new rack, natural terrain,
edit/Undo, reload and final export remain NOT TESTED for this revision. All other
applicable unrun gates in the original matrix remain open. New seat/planter are
component candidates, not additional student picker entries. This is a local
furniture expansion, not a new park catalogue release or publication approval.
