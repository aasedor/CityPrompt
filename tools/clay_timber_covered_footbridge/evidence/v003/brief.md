You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/covered/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, portal_end, louvre_wall, roof_eaves, deck_inside, pier_abutment, stream_under, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a contemporary covered timber footbridge over a stream (the top view governs the plan): glulam portal frames with knee braces, vertical timber louvres along both sides, a standing-seam zinc roof with deep eaves, a timber deck, concrete piers and abutments, paved stone approaches with steel railings, a planted bank and apartment blocks as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (timber covered footbridge with glulam frames, vertical louvres and a grey standing-seam roof over a stream, concrete piers, stone paved approaches),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/covered/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, frames and braces, louvres, roof and eaves, deck, piers and abutments, approaches and railings, stream and banks, planting, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/covered/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0, 1 P1 and 12 P2, and confirmed all nine v001 P1s fixed in the pixels. The P1: each side wall read as 10 narrow bays — a louvre-only end bay, then an open bay carrying the long diagonal, six open knee-braced bays, an open diagonal bay and a louvre-only end bay — where the sources (oblique posts at about x 515/665/770/855/920/980/1040; top posts at an even ~97 px pitch) show 6 equal bays between 7 posts, each end bay holding full-height louvres with the one long diagonal laid over them, and 4 open knee-braced interior bays; the render bays were also about 30% narrower relative to the roof width. This is the last targeted fix for the side-bracing finding. The builder claims these changes: the frames are now seven, at an equal pitch of one sixth of the post-to-post length (about 4.33 m), giving six equal side bays; each end bay has full-height louvres on a bottom rail, set 9 cm inside the post line, and the single long diagonal laid over them on the outside, rising from the post foot on the portal side to the post head on the midspan side; the four interior bays are open, with knee braces at both post heads under the continuous rail and one louvre layer between that rail and the wall plate; the separate louvre-only bay and the open diagonal bay are gone; the glass balustrade runs along the four open bays. These v001 and v002 fixes must still hold: one regular louvre layer with a bottom rail in the end bays; nothing piercing the zinc roof at the hips; no black voids at the portal post tops; straight, shallow, square-ended edge beams bearing on concrete abutments cut into both banks; round piers with concentric headstocks; the front camera holding the whole near portal, roof corner and eaves; the aerial view clear of the foreground tree; the landing glass on the landing boards. Verify each in the pixels; do not take the builder's word.
