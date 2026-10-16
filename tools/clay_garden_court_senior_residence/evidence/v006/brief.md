You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/senior/v006
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, loggia_arcade, dormer_roof, hub_cupola, garden_beds, pergola_terrace, interior, court_view)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a garden-court senior residence: a ring of red-brick three-storey blocks round a landscaped court (two pavilions at the north, one at the south-west, a long east wing and a long south wing) under copper standing-seam roofs (the pavilions hipped to a flat top with rooftop units, the wings hipped to a ridge, gabled dormers on every slope), one-storey brick loggias with round-arched openings and copper roofs linking the blocks, an octagonal glazed garden room with a copper roof and a glass cupola on the link between the north pavilions; white double-hung windows, arched garden doors with iron balconies above on the court faces; in the court brick paths, lawns, rose beds, a tiered fountain, a fenced garden of raised timber beds and a timber pergola over a dining terrace; a circular lawn with a fountain and a drive loop to the north. The front and oblique sources disagree with the top view on where the blocks sit; the builder followed the top view for the plan. The front and front_corner renders are whole-envelope views from high above the south; court_view is the source-matched view into the court. The outer faces of the ring are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick blocks with hipped copper roofs and dormers round the garden court, arched brick loggias, octagonal glazed garden room with copper roof and glass cupola, fountain, raised beds, pergola),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/senior/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, plan (ring of blocks, court), roofs and dormers, loggias and arches, garden room and cupola, window rhythm and balconies, garden elements (paths, fountain, beds, pergola), forecourt, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/senior/v006/review/independent-review.md. Do not run the build.
This is version 6. The previous independent review (v005) found: P1 the garden room's court face reading as fixed glazing down to grade with no door frame or step, where the sources show a white double French door with a transom and a stone step. The builder claims: on the court (south) and forecourt (north) faces a pair of glazed French doors 1.8 m wide recessed in a heavy white casing with a proud head, a centre meeting stile, kick rails and brass handles, narrow sidelights either side, the three-pane transom above, a threshold through the wall and a projecting stone step where the court path arrives. Verify it in the pixels and record whether the v005 finding is resolved.
