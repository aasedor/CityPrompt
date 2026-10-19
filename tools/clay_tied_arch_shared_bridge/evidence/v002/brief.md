You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/tiedarch/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arch_springing, hangers, planter_divider, cycle_lane, deck_edge, quay_under, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a bowstring tied-arch shared cycle and pedestrian bridge over a canal (the top view governs the plan): two inclined silver-grey steel arches leaning towards each other with cross ties, vertical hangers to a wide deck with a red cycle lane and a pale footway separated by a raised linear planter of grasses, glass or steel railings, brick quays and apartment blocks as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (twin inclined steel tied arches with hangers over a canal, red cycle lane and pale footway split by a raised planter),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/tiedarch/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, arch form and inclination, cross ties, hangers, deck, cycle lane and footway, planter, railings, quays and landings, water, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/tiedarch/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 0 P0, 3 P1 and 7 P2 (plus one recorded source conflict). The P1s: the bridge crossed the canal at exactly 90 degrees where the governing top source shows the deck axis skewed about 13 degrees to the quays, with wedge-shaped landings; there were 5 cross ties where source top and oblique show 7 evenly spaced box ties over the central part of the span; the deck fascia was about 1.4 times the railing height and the soffit sat barely above the water, so the deck read as a thick slab on a flooded channel with almost no brick quay wall showing and no bearing seat at the quays. The P2s: arches, ties, fascia and railing in the same pale grey as the footway; generic office-slab context with ribbon windows, some tan, and a visible world edge; the front camera mid-deck instead of on the landing left of the axis; each springing a pad with a stray box stuck to its end; spiky cone planting; a context parapet over the east springing in aerial and narrow side views. The builder claims: the whole bridge (deck, arches, ties, hangers, railings, planter, plinths) is turned 13 degrees anticlockwise in plan against the square canal, the span is 46 m so every square deck end lands on a quay, and the wedges between the deck ends and the quay copings are brick paving; seven box ties evenly spaced over the central 57% of the span; the quays are raised so about 3.3 m of brick quay wall shows above the water, the edge-tie fascia is 0.85 m (about 0.7 times the railing), the soffit clears the water by about 2.7 m, and each quay wall carries a concrete bearing shelf with a seat face and dark bearings under both edge ties; P2s fixed: cool silver-blue arches, ties, fascia and railing against the warm pale footway; brick-red context blocks with punched windows and balcony slabs, ground, quays and canal extended well beyond every frame; front moved onto the west landing left of the axis with the near-left springing in frame; one chamfered concrete plinth under each springing, the edge ties ending inside it; clumped ochre and green grasses with fewer cones; aerial and side views re-aimed and tightened, and every view except the plan turned with the bridge. Verify each in the pixels; do not take the builder's word.
