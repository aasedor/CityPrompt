You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arch_spandrel, cutwater_pier, balustrade, lamp_standard, roadway_deck, river_underside, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a heritage stone arch road bridge over a river (the top view governs the plan): three semicircular cut-stone arches on piers with pointed cutwaters, solid spandrel walls with a moulded cornice, stone balustrades with pedestals, ornate double-lantern lamp standards, a carriageway with lane markings and footways, splayed approach walls and quays at both ends, old town blocks as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (three-arch cut-stone road bridge with cutwaters, cornice, balustrades and double-lantern lamps over a river between quays),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, arch count and form, voussoirs and spandrels, piers and cutwaters, cornice, balustrades and pedestals, lamp standards, carriageway and footways, approaches and quays, river, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found no P0s, 4 P1s and 9 P2s.

**P1s:**
- The west quadrant corners read as two concentric barriers in front and front_corner: a heavy curved slab, with balusters showing on its outer face, beside a lighter balustrade.
- The lamp C-scroll arms and volutes were chains of straight box segments, with black gaps at every joint.
- Every pier pilaster panel frame had black void squares at all four corners.
- rear_side clipped the east end: the east abutment, its quadrant and the end lamp were off the left edge.

**P2s:**
- square balusters;
- saw-tooth tabs under the quadrant plinth;
- a grey quay ledge under the west springing;
- no cutwater at the east river pier;
- plan proportion drift;
- shadow smears on the deck;
- a hero-lamp finial touching the top edge of the front view;
- sparse context plots by the quays;
- white specks at a lantern post.

**The builder's claimed fixes:**
- **Corners.**
  - The plan has only one barrier at each corner; an analysis of the v002 geometry shows a single quadrant balustrade at one radius. The doubling was a reading problem: seen from the low front camera, the near half of the quadrant showed its wide rail top, and the solid quay parapet ran straight into the balustrade with a stepped coping joint.
  - Each quadrant balustrade now ends on a tangent pedestal (0.9 m square with a cap) where the solid coped quay parapet begins. This applies at all four corners: at the west quay parapet and at the top of the east retaining wall.
  - Each corner therefore reads as bridge pedestal, quadrant balustrade, tangent pedestal and solid parapet.
  - The quadrant plinth and rail are slimmed to 0.48 m.
- **Lamps.** Each C-scroll arm is now one smooth swept tube: an 8-sided circle carried along 13 points with parallel-transport frames and capped ends, running from inside the shaft into the lantern seat. Each volute is one swept spiral tube from the shaft. Both are smooth-shaded, so there are no joints and no black gaps.
- **Pier panels.** The two rails run the full frame width, 7 cm deep. The two stiles stand between the rails, 1 cm shallower and stopping under the rails. No two bars share a face plane and no corner is open.
- **rear_side.** The camera is moved over the low east quay north-north-east of the bridge, at (20, 70, 30) aimed at (7, 0, 5) with a 24 mm lens. The whole bridge sits inside the frame, from the land arch and east end over the low quay road to the west abutment, with the narrower upstream channel beyond. No block or tree stands in the sight line.

**Earlier fixes that must still hold:**
- **v001 fixes:**
  - the source plan: a fourth land arch over the low east quay road, a curved north-east quay and a narrower upstream channel;
  - quadrant walls at all four corners, seated on curved quays with no overhang;
  - cutwaters 5 cm proud of the jambs, with no slit;
  - ornate double-lantern lamps;
  - river, quays and town running on past every frame;
  - warm sandstone, dark olive water, and distinct quay and paving tones;
  - framed front, front_corner, left_side and right_side views.
- **v002 fixes:**
  - a single centreline;
  - a lowered keystone with the dentils returned round it;
  - no bus in front of the deck in roadway_deck.

The P2s listed above are unchanged in v003.
