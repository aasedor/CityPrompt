You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/beltline/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, storefront_patio, lobby_slot, balcony_stack, penthouse_terrace, roof_bulkhead, interior, rear_lane)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a five-storey Calgary Beltline corner mid-rise with streets south and east: a retail ground storey projecting 1.6 m in front of the upper south face, storefronts between brick piers under dark sign bands (a brewery taproom with a fenced umbrella patio at the west, the residential lobby under a dark canopy in the middle, a market wrapping the south-east corner); above it three storeys of red brick in two wings either side of a recessed full-height glazed slot over the lobby, the floor-2 flats opening onto the retail roof behind a glass guard, projecting concrete balconies with glass balustrades on floors 3 and 4 (two stacks on the west wing, one wide stack on the east wing) and on all three floors in two stacks on the east face, a dark metal parapet cap; a dark-panelled penthouse set back behind wood-decked terraces with planters and a glass guard, its gravel roof carrying paver walkways and a stair and lift bulkhead with an L-shaped notch. The north face is not visible in any source; the west face is a party condition above a lower neighbour (not modelled). Signage text is not required in clay; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick wings either side of the glazed slot, projecting glass-balustraded balconies, retail storey with dark sign bands and the corner market, set-back dark penthouse with decked terraces, patio),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/beltline/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, wing and slot composition, balcony stacks (south and east), retail storey and sign bands, lobby, corner market, floor-2 terrace, penthouse and terraces, roof bulkhead and walkways, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/beltline/v001/review/independent-review.md. Do not run the build.
This is version 1, the first build of this family; there is no previous review. Record every P0 and P1 precisely, with the view that shows it, so the builder can fix each one in the next version.
