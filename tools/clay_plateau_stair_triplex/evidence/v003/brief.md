You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/triplex/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, iron_stair, balcony_canopy, cornice_parapet, east_side, roof_skylights, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a flat-roofed two-storey Montreal Plateau plex over a half-basement on a street corner, the street south and a side street east, an attached brick neighbour west (the top view governs the plan): a grey limestone front with block coursing and long-and-short quoins; a recessed central porch on both floors, the ground porch with a green door, steps and an iron railing, the upper porch behind a projecting stone balcony with an iron railing and a pair of red glazed doors, sheltered by a flat canopy on two black iron lattice columns; wide timber-framed windows with transoms in the side bays with stone sills and lintels; small basement windows at grade; a black iron exterior stair climbing from the yard to the upper balcony and curling at its foot; a projecting bracketed cornice with a raised central parapet and cartouche; plain grey brick side and rear walls with narrow windows; a pale membrane roof with three skylights and a roof hatch; a small lawn behind an iron fence, sidewalks and street trees. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (grey limestone plex front with quoins, curling black iron exterior stair to a canopied upper balcony on lattice columns, red upper and green lower doors, bracketed cornice with raised central parapet),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/triplex/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and basement, limestone coursing and quoins, porch recess (both floors), doors (colours), balcony and railing, canopy and lattice columns, windows (frames, transoms, sills, lintels), iron stair (flight, curl, rails, newel), cornice, consoles and raised parapet, side walls and windows, roof (membrane, skylights, hatch), yard, lawn, fence, sidewalks, neighbour, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/triplex/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 6 P1 (v001: 7 P0+P1): the south-east cornice return built as stacked slabs with black slits; an open black hole at the east end of the raised central cornice; the raised parapet reading as a plank set back behind the corona, with a loose cartouche; the consoles reading as cube piles hanging onto the window heads; the top view framed too wide; the porch walls stopping short of the ceiling inside, leaving a black band and slots. The builder claims every one is fixed (one continuous cornice whose east return starts behind each front band; the raised run replaced by a flush stone attic panel on the cornice with a cap and the cartouche on its face; one shaped console each side, clear of the window heads; a tight top view on the plex; porch walls up to the roof deck and floors run into the walls). Verify each in the pixels; do not take the builder's word.
