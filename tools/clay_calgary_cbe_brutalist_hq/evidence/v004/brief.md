You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, bay rhythm 14 x 13, window depth and fin/nose relief, fascia and parapet bands, cantilever over the recessed ground storey with board-formed columns, entrances and podium steps, penthouse and roof plant, sculpture plaza and site, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v004/review/independent-review.md. Do not run the build.
This is version 4, a second pass the user approved after the family stopped at v003. The v003 review found 0 P0 and 1 P1. The geometry now matched the source head-on, with glass about 0.68 of the bay: facade_close measured 0.687, and the east elevations 0.676 to 0.689. But the front_corner camera grazed the east face. The east face projected to about 120 px against about 580 px for the south face, where the source oblique shows about 400 px against 530 px. At that grazing angle the jambs hid every pane, and the east face read as a blank embossed wall. The reviewer's fix was to re-aim front_corner to the source-oblique azimuth and elevation, and not to deepen the cells again.

The builder claims it is fixed. The geometry is unchanged from v003; only cameras moved:
- **front_corner** now looks from about 41 degrees east of south and about 32 degrees down, with a 35 mm lens. The south and east faces project in a ratio of about 1.3:1, as in sources/oblique.jpg, and every east cell on all three floors shows a dark pane.
- **aerial** is unchanged. The v003 review already found a pane in every east cell there.

Compare front_corner against sources/oblique.jpg for the viewpoint: azimuth, elevation and the share of the building width each face takes. Zoom to 3x on the east face of front_corner and count dark panes cell by cell. Do not take the builder's word for either.

Cheap P2s the builder claims:
- **front (v003 P2 #2).** The camera was fitted to the locked front from its parapet and soffit corners, the penthouse corners and the sculpture plinth, with an rms of about 14 px. It now sits farther back at eye level with a long lens (68 mm), so verticals are near-parallel. The south face runs on the left and the foreshortened east face on the right, with the corner about two-thirds across the frame. The plinth is in the foreground, and the penthouse with its louvre shows above the south parapet. The penthouse shows less above the parapet than in the source. The source's near-parallel verticals cannot be matched exactly by a tilted camera, so check whether the penthouse and louvre read, not their exact height.
- **Duplicate east views (v003 P2 #3).** The detail camera east_side duplicated right_side, so it is replaced by **west_side**. This is an elevated west coherence view over the three-storey brick neighbour. It shows the 13-bay west face, with a pane in every cell, and the penthouse with its west louvre and door. The west face appears in no source, so judge it for coherence with the visible grammar only. right_side still covers the east face and the east entrance.

The v003 P2s on the brief's view list, the aerial pane width and the east door are not addressed.

The earlier fixes must still hold:
- **Cell grid:** the flush cellular precast grid of four-way splayed coffers. Continuous horizontal members run at the floor lines, with one tapered vertical member per cell and storey.
- **Glass:** 1.85 m wide by 2.4 m high, about 0.68 of the 2.7 m bay, at the back of 0.55 m deep coffers. The jamb splay is about 0.28 m, the head splay about 0.45 m and the sloped sill about 0.7 m.
- **Parapet:** one continuous plain band about 0.55 of the 4.0 m storey pitch, with the grid stopping at its foot.
- **Ground storey:** tall and recessed, 5.8 m or 1.45 of the pitch, under a plain fascia with no vertical panel joints. It has two-tier storefronts.
- **Massing and structure:** solid corner piers, the 14 x 13 bay rhythm, and the cantilever of about 3 m over freestanding board-formed columns.
- **Site and roof:** the entrances and podium steps; the penthouse position, its louvres in the upper middle of its walls, and the roof plant; the sculpture plaza in the south-east.
- **Materials:** the warmer concrete palette, with the board-formed ground storey slightly darker than the precast box.
