You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plaza/v007
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, anchor_entrance, inline_shops, endcap_corner, parking_court, roof_units, interior, rear_service)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a single-storey L-plan prairie plaza: an anchor grocery at the west end as a taller box with a projecting entrance tower and green sign band, a lower cafe wing on its west flank, an inline run of glazed shop fronts under a continuous canopy along the north edge of the parking court, an end-cap wing turning south along the east edge with a drive-through at its south end, beige EIFS over a brick base with brick pilasters, dark cornice bands, flat roofs with rooftop units, a striped parking court with cars, a pylon sign and lawn verges. Rear faces are not visible in any source; signage text is not required in clay; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (L-plan wrapping the court, anchor tower and sign band, continuous shop canopy, brick base and pilasters, pylon sign),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plaza/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, L-plan and wings, anchor tower, shop-front rhythm and canopy, end-cap and drive-through, parking court, roof units, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plaza/v007/review/independent-review.md. Do not run the build.

This is version 7. The user lifted the three-version cap and asked for every building to be carried to a review with zero P0 and zero P1. The v006 independent review found 0 P0, 4 P1 and 6 P2: P1 the east end-cap was a thin bar equal to the inline wing's depth, where the source top shows it about 1.5-1.8 times the inline depth and the second-largest volume; P1 the site pad stopped 2-3 m from the north, east and west walls, with no wrap-around drive, no readable drive-through route round the end-cap's south end and up its east side, and no west perimeter parking row along the cafe; P1 the cafe was still mostly beige with a canopy and no brick pier at the east end, where the source shows the cafe's whole ground storey brick with wide piers at both ends, beige only as the sign band over a dark lintel, and no canopy; P1 the end-cap's south face was beige with brick only as a base, where the sources show a brick corner pier at the west corner and a full-height brick panel at the south-east corner. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v006 finding whether it is resolved in the pixels.
