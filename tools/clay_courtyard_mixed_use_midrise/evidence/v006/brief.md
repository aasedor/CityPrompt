You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/courtyard/v006
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, courtyard_stair, retail_corner, balcony_close, roof_terrace, cladding_contact, interior, rear_lane)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a corner mixed-use mid-rise with streets south and east: street-level retail with dark storefronts across the ground floor, above it a U-plan of three residential storeys in dark vertically ribbed metal cladding around a raised courtyard that opens south and is reached by a wide concrete stair from the sidewalk, balconies recessed into the volumes with cedar-lined reveals and glass balustrades, tall black-framed windows, a set-back penthouse storey with roof terraces at the front end of each wing and rooftop units on the rear bar. The north and west faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (dark ribbed U-plan over street retail, raised courtyard with the wide street stair, cedar-lined recessed balconies, set-back penthouses with terraces),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/courtyard/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, U-plan and courtyard, street stair, balconies and cedar reveals, window rhythm, penthouses and terraces, retail base, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/courtyard/v006/review/independent-review.md. Do not run the build.

This is version 6. The user lifted the three-version cap and asked for every building to be carried to a review with zero P0 and zero P1. The v005 independent review found 0 P0, 4 P1 and 8 P2: P1 the rear bar's floating roof slab was not visible (no slab, fascia, soffit or posts past the top-storey glazing); P1 the wing roof terraces were a 1.5 m ledge under the eave where the sources show decks 5 to 6 m deep, open to the sky in their outer part; P1 the wing courtyard faces were dark ribbed metal where both sources show tan panel and cedar; P1 a pure-black crevice under the right wing's roof slab where it overhung the rear-bar roof. P2s: rear walkway near-black from above, three roof tones, penthouse walls beige not cedar and pale slab edges, sparse ribs, stair without wood seating tiers or a mid-flight landing, plant positions, a tree in the glass close-up, corner bay rhythm. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v005 finding whether it is resolved in the pixels.
