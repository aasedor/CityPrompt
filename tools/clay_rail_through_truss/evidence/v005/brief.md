You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railtruss/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arch_span, column_base, lattice_detail, track_deck, train_cars, street_under, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an elevated steel rail viaduct over a city street (the top view governs the plan): a long run of riveted latticed steel arch spans springing from steel columns on concrete pedestals, a braced deck carrying twin tracks and a silver train, a street with a red cycle lane and footways beneath, brick apartment blocks as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (long elevated riveted steel arch viaduct on columns over a street, latticed spandrels, twin tracks and a train),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railtruss/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, span count and rhythm, arch ribs and lattice, columns and pedestals, deck and tracks, train, street, cycle lane and footways beneath, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railtruss/v005/review/independent-review.md. Do not run the build.
This is version 5. The v004 review found 1 P0, 1 P1 and 12 P2. The P0: the track_deck view was entirely black (every channel 0 to 1), so the deck, sleepers, rails and both tracks could not be inspected at detail scale; the camera stood inside the last car of the train. The P1: both rebuilt bowstring trusses showed pure-black wedges and panels (luminance 0), some with rivet dots on a black field, on their inner faces at the end panels next to the springing and bearing shoes (front_corner, aerial, top), reading as holes in the truss. The builder claims: the track_deck camera now stands above the deck between the two tracks north of the train, looking north along both tracks (deck, sleepers, rails, edge railings); the black panels were the two riveted gusset plates at the short end-panel verticals (next to each shoe), which overlapped with coincident faces and rendered black; at those verticals there is now one full-height riveted gusset on each face instead of two overlapping ones; the end panel between each shoe and the first vertical is now closed by a solid riveted plate between the bottom chord and the arched top chord, so no narrow wedge slot remains; the deck plate is a darker steel tone; the facade_close view is re-aimed as a bowstring close-up of the west truss's inner face at the south shoe and first panels (review P2 13). Verify in track_deck, facade_close, front_corner, aerial and top that no pixel on the bowstring is black and the deck view is legible; do not take the builder's word.

Earlier fixes that must still hold. Check each in the pixels:
- the bowstring is a heavy, low, open-topped riveted arched truss in each girder plane (crown near the car roof line), with deep built-up chords, verticals, main diagonals and counters and riveted gussets, no overhead struts (v003 P1);
- below the deck the same planes carry the viaduct's plate-rib deck arches with their spandrel lattice down to riveted columns on concrete pedestals, with a riveted transverse portal arch at the intermediate column pair, so the arcade rhythm runs on under the bowstring and the end bent is not a gantry (v003 P1);
- the train runs on the street-side (east) track; the context window frames have no black corner dots;
- solid riveted plate ribs with flanges and rivet rows and no lattice inside the rib (v001 P1-1);
- open bents with a riveted transverse portal arch and no X-bracing, the footway open beneath (v001 P1-2);
- real window openings with set-back glazing and recessed door leaves (v001 P1-3);
- closed riveted cap girders at the end bents and the bowstring bent with no black voids (v001 P1-4);
- rib crowns about 0.4 x rise below the girder with a continuous eleven-post spandrel lattice over the whole span, nothing lapping into the girder (v002 P1-1);
- car end skins inset between the sides with silver corner posts and no black strips (v002 P1-2).
Not changed: the rib facet count and rivet pitch, the base-shoe gusset and rib end plate at the column caps, the run length, the door-window recess and gangway, the top camera pitch, the north end bent.
