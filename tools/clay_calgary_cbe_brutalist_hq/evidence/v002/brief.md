You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v002
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, bay rhythm 14 x 13, window depth and fin/nose relief, fascia and parapet bands, cantilever over the recessed ground storey with board-formed columns, entrances and podium steps, penthouse and roof plant, sculpture plaza and site, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cbe/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 0 P0 and 3 P1.
1. The parapet band was not plain and was too shallow: fins ran up to the coping and split it into recessed panels, and it was about 0.39 of the storey pitch where the source has one continuous plain band of about 0.55.
2. The façade grid hierarchy was inverted: continuous full-height pilaster fins stood proud of flat box spandrels, where the source has a flush cellular precast grid of deep coffers splayed on all four sides. The shallow splays did not read at whole-envelope scale, and the east face looked almost blank in the front view.
3. The recessed ground storey was too short, about 0.9 of the office storey pitch where the source has about 1.4 to 1.5, so the building was about 15% too low.

The builder claims each is fixed:
1. The parapet is one continuous plain precast band 2.2 m tall (0.55 of a new 4.0 m storey pitch) with a single horizontal joint and a coping. No fin or cell member enters it; the grid stops at its foot.
2. The upper box is now a flush cellular grid: one precast cell per bay and storey, 2.7 m by 4.0 m. Each cell is a 0.9 m deep coffer whose jambs, head and a deep sloped sill splay inward on all four sides to a 1.6 by 2.2 m glass opening, so the sill plane is about a third of the glass height. The cells' front frames are flush, giving continuous horizontal members at every floor line and one tapered vertical member per cell and storey. The old continuous pilaster fins and spandrel noses are gone, and solid corner piers close the grid at the four corners.
3. The ground storey is 5.8 m from podium to soffit (1.45 of the pitch), with a 1.4 m plain fascia above it. The storefront glazing is two-tier with a transom, under a board-formed band, and the board-formed columns rise to the new soffit.

Cheap P2s the builder claims:
- warmer beige-grey concrete;
- the front camera moved east and back so the SE corner and the foreshortened east face show;
- one more board-formed bay at the west end of the south ground storey;
- slimmer, taller sculpture figures;
- dark penthouse doors, one west of the louvre and one near the east end;
- the east street trees moved off the east entrance.

Verify each in the pixels (front, right_side, east_side, facade_close, window_module, corner_cantilever, sculpture_plaza, roof_penthouse); do not take the builder's word. The things v001 got right must still hold: the 14 x 13 bay rhythm; the cantilever of about 3 m over freestanding board-formed columns; the entrances and podium steps; the penthouse position and roof plant; the sculpture plaza in the south-east.
