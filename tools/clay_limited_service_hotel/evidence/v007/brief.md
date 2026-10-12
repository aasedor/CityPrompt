You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hotel/v007
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, porte_cochere, lobby_tower, wing_contact, parapet_corner, roof_plant, interior, rear_entry)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a four-storey limited-service highway hotel: an L-plan block of beige and charcoal EIFS with paired punched guest-room windows and a dark accent band under the parapet, a full-height glazed lobby tower at the south-east corner, two glass-roofed porte-cocheres on stone-clad piers (east and south), a one-storey glazed breakfast and pool wing with a rooflight at the south-west, a white membrane roof with rooftop units, a parking court, drive loop and pylon sign. The north and west faces are only partly visible in the sources; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (L-block with paired windows and accent band, glass lobby tower, porte-cocheres on stone piers, low glazed wing, parking court),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hotel/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, window rhythm, lobby tower, porte-cocheres, low wing, roof plant, site elements, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hotel/v007/review/independent-review.md. Do not run the build.

This is version 7, the second and last of the two versions allowed after the user lifted the GLB size limit. The v006 independent review found 0 P0, 2 P1 and 9 P2: P1 the glazed lobby tower rose about half a storey to a storey above the main parapet where the sources put its banded header level with or just below the adjacent parapet caps and its own flat roof below the main roof; P1 the under-parapet accent band was navy on every block where the sources show navy only on the beige south leg's south and east faces and the tower header, and dark green on the charcoal north leg and on the beige leg's west end. The v005 findings (apron slot, frontage sequence and pylon, wing ribbon, cars on the verge) were verified resolved. v007 stops the tower glazing about 1 m below the main roof under a solid banded charcoal header box whose top is 0.2 m above the parapet cap, and gives the band its two-colour scheme. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v006 finding whether it is resolved in the pixels.
