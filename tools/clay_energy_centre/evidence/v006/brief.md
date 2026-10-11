You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/energy/v006
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, plant_window, stack_contact, corten_block, roof_plant, corner_entry, interior, rear_service)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a corner district energy centre of two volumes: a lower two-storey buff-brick frame with full-height glazed bays exposing the plant room, a board-formed concrete panel in the upper corner bay, a recessed entrance bay at the south end of the west face, and a membrane roof with two three-fan cooling banks, duct runs, a cluster of three slender flues and one hourglass exhaust stack; and a taller corten-clad block with a narrow slot window and two rooftop units. The north and east faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick-framed glass plant showcase with the concrete corner panel, corten block, cooling banks, flue cluster and hourglass stack),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/energy/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, bay rhythm and glazing, concrete panel, entrance, corten block and slot, roof plant and stack, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/energy/v006/review/independent-review.md. Do not run the build.

## Builder context for v006 (for the reviewer; verify every claim in the pixels)

v005 review: 0 P0 / 5 P1 / 8 P2. v006 targets the five P1:
1. Stack: one slender constant tube with an open top inside a square cage; four corner struts run from a collar platform at about 75% height, pinch to the tube at about mid-height and splay to a square plinth; a tie ring at about 1/3 height. Moved to midway between the cooling banks.
2. West corner pier widened to about 3.8 m, with the west corner bay narrowed to 11.2 m (about 1.6x the 7 m glazed entrance bay). The pier returns onto the south face by the same width.
3. North service bay: a seven-light clerestory under the coping over a recessed board-formed concrete panel that fills the bay to grade, with the service door set in the panel at its north end and brick either side.
4. Roof ducts: two parallel 2 m rectangular trunks per bank from the bank's east face to a take-off box at the corten wall, with flanges; a 2 m N-S trunk between the inner trunks.
5. Storey split on both corner bays: ground glazing, concrete panel and upper curtain each about 1/3 of the wall; the curtain runs to 0.4 m below the coping.
P2s taken on the way: warmer buff-brown brick, mid-grey concrete, entrance curtain run up to the same head. Flue and corten-roof P2s are not addressed.
