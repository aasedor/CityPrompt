You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, facade_close, window_module, corner_cantilever, ground_entrance, arcade_soffit, sculpture_plaza, east_side, roof_penthouse, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a near-square four-storey 1960s brutalist office headquarters on a street corner (streets east and south): three office floors in a warm grey precast concrete box of 14 x 13 bays that cantilevers about 3 m over a recessed ground storey; a deep plain fascia band over the ground floor, then one deep-set window per bay and floor between tapered vertical fins, spandrel noses whose tops slope down from each sill, and a tall plain parapet band with a coping; solid corner piers. The ground storey stands back on a low podium with steps: dark storefront glazing between board-formed concrete mullions, board-formed wall panels at the west end of the south front, glazed double entrance doors facing the plaza and a second entrance on the east, freestanding board-formed columns carrying the cantilever. A set-back concrete mechanical penthouse towards the north with a louvre and steel doors, two air-handling units with round fans, small vents and a railed rooftop unit on the main roof. A paved plaza in the south-east with a round plinth carrying a ring of standing figures, a lawn to the south-west, brick neighbours west and north, sidewalks, street trees, a lamp and a crossing on the east street. Source notes: the top view governs the plan and the penthouse position; the front view puts the sculpture in front of the south face while the top view places it south-east of the building, and the top view governs; the west and north faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (cantilevered precast window-grid box over a recessed board-formed ground storey, deep-set windows between tapered fins with sloped spandrel noses, plain fascia and parapet bands, set-back mechanical penthouse, sculpture plaza),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, bay rhythm 14 x 13, window depth and fin/nose relief, fascia and parapet bands, cantilever over the recessed ground storey with board-formed columns, entrances and podium steps, penthouse and roof plant, sculpture plaza and site, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 1 P1: the windows were too small, about 0.55 of the bay width where the source is about 0.65, and sat at the back of a 0.9 m deep coffer. At oblique angles the jambs hid almost all of the glass, so the east face still read blank in the front, front_corner and aerial views, where the source oblique shows a large dark pane in every bay. This is the v001 façade-grid finding, only partly resolved; v003 is its second targeted fix.

The builder claims it is fixed. The glass in each cell is now 1.85 m wide by 2.4 m high, about 0.68 of the 2.7 m bay, and the cell grid in front of the carrier is now 0.55 m deep instead of 0.9 m. The jambs, head and sloped sill still splay inward on all four sides from the flush front frame to the glass, but they are shallower: the jamb splay is about 0.28 m wide over the 0.55 m depth, the head splay about 0.45 m and the sloped sill about 0.7 m. The flush cellular grid is unchanged in pattern: continuous horizontal members at the floor lines and one tapered vertical member per cell and storey. Head-on the glass measures about 0.66 of the bay in facade_close, and the foreshortened east face shows a dark pane in every cell in front, front_corner and aerial. Verify the glass-to-bay ratio in facade_close and window_module, and the east face in front, front_corner and aerial; do not take the builder's word.

Cheap P2s the builder claims:
- the front camera is moved toward the south-east corner and lowered to eye level, so the south face runs on the left and the foreshortened east face on the right, with the penthouse and its louvre above the parapet, as in the source front;
- the vertical panel joints across the ground-storey fascia are removed, so it reads as one plain band;
- the penthouse louvres are raised into the upper middle of their walls.

The earlier fixes must still hold: one continuous plain parapet band about 0.55 of the 4.0 m storey pitch, with the grid stopping at its foot; a tall recessed ground storey (5.8 m, 1.45 of the pitch) under a plain fascia, with two-tier storefronts; solid corner piers; the 14 x 13 bay rhythm; the cantilever of about 3 m over freestanding board-formed columns; the entrances and podium steps; the penthouse position and roof plant; the sculpture plaza in the south-east.
