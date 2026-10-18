# Five parkades — original-design local pilot, 2026-10-17

Branch: `codex/parkade-family-pilot`, based on the saved parking-lot checkpoint
`0ff598dfe`. Existing parking lots, scenes and production are unchanged.

## Approved brief and current scope

| Design | Native plan / parking levels | Status |
| --- | --- | --- |
| Classic Concrete | 60 × 36 m / 4 | v005 passed independent holistic architectural-clay review (P0=0/P1=0) and standalone browser checks. No catalogue activation. |
| Urban Brick | 54 × 36 m / 5 | Approved design brief; not built. |
| Green Terraces | 60 × 40 m / 4 | Approved design brief; not built. |
| Solar Ribbon | 66 × 36 m / 5 | Approved design brief; not built. |
| Mobility Courtyard | 64 × 48 m / 4 | Approved design brief; not built. |

These are fixed native buildings, not drawn parking-lot recipes. Intended final
discovery is Buildings → Parkades, with a Streets shortcut. That catalogue wiring
is not implemented at this pilot checkpoint. The repository requires a visible
one-archetype pilot before the finite next batch.

## Try the pilot

With the current local Vite server and recovered public directory, open
`http://127.0.0.1:5184/parkade-review.html`. The separate DEV review page provides
front, oblique, aerial, rear and stair cameras plus 1/5/20-copy samples. It does
not modify projects or enable an unreviewed catalogue entry. Production builds
do not mount this review component.

The served GLB is a verified copy at
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/models/parkade-pilot/parkade-classic-concrete-clay-v005.glb`.
It is external to Git. Restore that exact file from the immutable candidate if
restarting on another machine; no placeholder or developer database is required
for this standalone viewer. This does not establish reproducible app catalogue
installation, which is a later gate.

## Exact pilot and source authority

- Candidate: `parkade-classic-concrete-clay-v005`.
- GLB SHA-256: `e1333f02e199e5c59408667a36c488f7ad6e38737ebd7735977f7f51ec9484d3`.
- Bytes: 961,992; triangles: 18,120; meshes/materials: 7/7; embedded images/textures: 0/0.
- Reimported native envelope: 60 × 36 × 12.80000019 m; round-trip bound delta: 0.
- Export is metres, +Y up, base Y=0, front +Z. Authoring is Z-up/front -Y.
- Parking surface datums: 0.15, 3.45, 6.75, 10.05 m. Height and level count are fixed.
- Three parallel same-direction rear ramps: 46 m run, 3.3 m rise, at least 6 m
  clear lane. Main floors exclude the ramp well; end landings join side aisles.
- Two open-entry glazed stair cores contain authored switchback stairs, landings
  and inner deck doorways. No operable-door or elevator simulation is claimed.

Source package is `classic-cad-sources-v003` under the external evidence root.
The authoritative front/oblique/top and rear circulation section are original
metric design drawings, independently reviewed before v004 authoring. Their
exact hashes, authority, inferred details and review are retained in provenance.
The two AI concept sheets are aesthetic exploration only: their inconsistent
bay counts, proportions and rear partitions cannot establish exact geometry.
This is a revised original design, not an exact-fidelity pass to the earlier AI
sheet or a reconstruction of an existing building. Architectural clay is not a
textured RLASM keeper.

## Verification and preserved failures

- Source contracts: five pytest cases, including missing ramp authority,
  changed bytes, original-authored design provenance, open stair wells and
  nonintersecting ramps. Combined with promotion regressions: 23 tests passed.
- Existing material-quality, placement-palette and paving-editor regressions:
  46 Vitest tests across three files passed.
- TypeScript and changed-file ESLint passed.
- Actual v005 GLB audit: 111 checks passed. Samples cover ramp surfaces and
  headroom, end landings, stair-to-main-deck joins and absence of opaque beams
  across outer glazing. Minimum sampled ramp headroom: 3.14999949 m.
- HTTP readback from the active local server: 200, valid GLB container and exact
  approved candidate hash. Fifteen offline views are renders of the actual
  optimized GLB reimport, with no material substitution; three 1080 × 1920
  comparison boards use the current CAD source authority.
- Separate source and code reviews were performed. v005 independent holistic
  architectural-clay review passed with zero P0/P1 findings. Its review SHA-256
  is `72ee8e470275c73a4ccac0fc21734f82f11b1999080af2474efd59ef72390afc`.
  Records remain alongside each exact candidate; a failed version is never
  relabelled as passing. Application integration is not covered by this review.

Preserved versions: v001 failed its below-ground datum; v002 had a narrow
landing/deck gap and unsupported rear horizontal guards; v003 failed source
coherence, glazing hierarchy, entry legibility, ramp support and close-view
proof; v004 closed all except side beams crossing outer core glazing. The
v004 regression produced six failing opaque-return rays; v005 shortened those
beams and all 111 rays passed. Every version and its available logs/reviews
remains external. The phone-board utility now refuses existing output files;
its refusal and unchanged pre-existing board hash were verified.

## Browser measurement limits

The diagnostic uses the same native-clay material-preservation options as the
globe loader and shares cached geometry between placement-owned material clones.
No recentering, scaling, global material edits or paid provider calls occur.
Performance is measured with all selected bounds framed in **Oblique**; the
close Stairs camera is for one-model inspection, not a complete repeated-grid
benchmark. Timing samples reset after changing camera or count.

Evidence files `browser-single.txt`, `browser-five.txt`, `browser-twenty.txt` and
corresponding PNGs record the actual final sample, buffer size, draw calls,
renderer triangles and frame intervals. Geometry attributes/index total about
930 KiB once; cloned materials, JS objects and GPU allocations are additional.
The model embeds no textures. Renderer texture counters also include shadow and
transmission buffers and are not a measurement of model texture memory.

| Visible copies / Oblique | Reported draw calls | Renderer triangles | Frame interval median / p95 |
| --- | --- | --- | --- |
| 1 | 17 | 37,588 | 17.5 / 18.1 ms |
| 5 | 77 | 187,924 | 17.5 / 18.1 ms |
| 20 | 302 | 751,684 | 17.5 / 18.2 ms |

Renderer totals include extra shadow/transmission passes and the review ground,
not just the GLB's 18,120 triangles. Eight geometries and two renderer textures
were reported at each count, consistent with shared source geometry. Local
model-ready sample: 123 ms; this is not a cold network benchmark. Independent
code review checked that the complete 5/20-copy bounds fit the Oblique frustum.

This is a desktop isolated-model test on an RTX 5060 / i5-14400F with a 1280 × 569
render buffer, DPR 1, shadows enabled. It is not a Google Tiles scene, a station
comparison, a student laptop or a mobile hardware measurement.

## Remaining gates

Before publication: human pilot visual check, finite remaining four models,
each independent clay review, catalogue thumbnails and categories/shortcut,
exact-byte local seeding/readback, ordinary student placement/move/rotate/delete,
Undo/Redo and save/reload, prepared and unsupported/sloped terrain recovery,
pedestrian/vehicle approach checks, mixed-scene capture and target-device cost.
No engineering, accessible-route, fire-egress, vehicle swept-path, parking-demand
or construction approval is implied. Stall capacity is not certified.

No changes were made to the production catalogue, database, API, asset-storage
policy or existing buildings. No models were added to Git, pushed or deployed.
Two image-generation-tool calls produced the preserved design studies; no
CityPrompt paid image/video render tests or account-credit changes were made.
Generated sources/models/render evidence are external at
`C:/dev-artifacts/CityPrompt/parkade-family-2026-10-17/`; these local paths are not
yet a collaborator-accessible evidence backup.

Source changes are limited to `tools/parkade_family/`, the standalone review
HTML/TSX and this report. The tools preserve source hashes, fail closed on missing
review/authority, write new versioned candidates and retain failed evidence.
