You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v002
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, curve geometry, deck and markings, parapets, Y-columns, ramps and landings, street beneath, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/flyover/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 2 P0, 6 P1 and 7 P2. The P0s: no view showed the deck reaching the ground (in left_side the far end stopped as a squared box at full deck height on Y-columns); landing_ramp missed its subject (the deck left the frame still about 3 m up and about 40% of the frame was empty ground). The P1s: the deck was about half the source width against the street (about 0.6 of a traffic lane against 1.4); the parapets were an open picket fence with a chunky separate top rail instead of a dense near-solid orange screen; Y-columns stood in traffic lanes, one in a zebra crossing; the Y-columns were square boxes with arm blocks notching through the shaft top instead of slender, rounded, tapered columns with a smooth fork; the other end curled over and dropped almost vertically within one deck width; at the far end both parapets swept up into horn tips with no deck under them. The P2s: a browner orange than the source's red-orange; faceting on the curved rail and fascia; mirrored front handedness; the ribbon a thin band in front_corner, aerial and rear; ground-plane smudges in top; sparse context planting; stripe banding on the deck. The builder claims: the centre line now continues past the junction on long straight approaches, and both ends descend over 100 m of ribbon (about 6%, parabolic knees) to at-grade cycle paths with kerbs on the south footway (west) and the north footway (east), the parapets running down with the deck and closed with end caps at the foot (the v001 end-point bug that folded the east end back on itself is gone); landing_ramp now stands on the west at-grade path looking up the ramp from just beyond its foot; left_side and right_side are pulled back to show each ramp with its foot; the deck is 6.2 m between the parapets (about 1.4 lanes); each parapet is one orange skin from the fascia to a slim cap, with close vertical slats as a folded sheet on its inner face; column feet are placed only in the planted median or on the footways, clear of lanes, the north-south street, crossings and street trees; each column is a round tapered shaft forking into two round tapered arms seated in the soffit, with short round posts where the ramp is low; a redder orange; trees that grew through the ribbon are removed and low shrub masses sit on the median under it. Verify each in the pixels; do not take the builder's word.
