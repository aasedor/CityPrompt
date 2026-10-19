You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, y_column, ramp_curve, parapet_panel, deck_surface, street_under, landing_ramp, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an elevated cycle flyover (the top view governs the plan): a sinuous ribbon deck in S-curves over a city street, carried on slender concrete Y-columns, with solid bright orange powder-coated parapets and a dark surface with lane markings, ramps down to the ground at each end, brick blocks and trees as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (sinuous orange-parapeted cycle ribbon on Y-columns swooping in S-curves over a street),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, curve geometry, deck and markings, parapets, Y-columns, ramps and landings, street beneath, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0, 3 P1 and 9 P2. The P1s: from outside, the parapet and fascia were one plain orange slab from cap to soffit with no bars and no screen/fascia split, reading as a deep box girder (about 0.45 of the clear height against about 0.35 in the source); where each Y-arm met the soffit there was a crisp dark ring or flat disc, so the arms read as open cut tubes in sockets; the folded-sheet parapet leaked black triangles at the cap seam, had a sawtooth bottom edge on the deck, and the curved cap showed facets. The P2s: the deck about 25% narrower than the source; the orange too amber and dark; the front composition mirrored; faceted column shafts and a hard fork crease; the ribbon thin in far views; ground smudges in top; a black mark in each zebra crossing; sparse context planting; median column feet tight against the kerb. The v001 fixes that must still hold: both ramps descend gently (about 6%) to at-grade cycle paths with no squared box end, curl-over or parapet horns; landing_ramp frames a ramp foot on the ground; no Y-column stands in a traffic lane or crossing; columns are round, tapered and forked. The builder claims: each deck edge now has a separate smooth orange fascia band (about 0.6 m, its foot 0.14 m above the pale soffit so the soffit edge shows) projecting 5 cm past a bottom rail, giving a reveal line, and above it a screen of close vertical orange bars (about 9 cm wide at 16 cm centres, with open gaps) between the bottom rail and a smooth rounded top rail; the folded sheet is gone, the bars sink into the rail and the top rail so no seam or bar end shows, and the rounded rail is smooth-shaded so the curve shows no chord facets; each Y-arm now runs about 0.45 m up into the deck and carries a smooth flared head whose top face lies wholly inside the deck, so no rim or disc shows under the soffit; shafts and arms are 20-sided and smooth-shaded; the orange is redder (towards sRGB 200, 95, 45); the north-south centre dashes stop clear of the zebra crossings; road markings are flat faces and the context window frames are flat proud faces to keep the file small. Verify each in the pixels; do not take the builder's word.
