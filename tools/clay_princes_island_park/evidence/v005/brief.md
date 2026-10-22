You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, pavilion_close, glazing_close, green_roof, porch_northwest, promenade_beds, boardwalk, riprap_bank, bench_plaza, footbridge, west_path)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a park, not a building: Prince's Island Park in Calgary on the Bow (the top view governs the plan, about 22 px to the metre, the river on the east). A one-storey timber pavilion with a planted sedum roof stands at the centre, rotated about 27 degrees off the river line: cedar board-and-batten cladding, a fully glazed south-east face with dark mullions and a long table inside, a door and corner glazing on the long south-west face, an open porch under the roof at the north-west end with two doors, clerestory windows on the north-east face, slim timber posts at the roof corners and a thin dark metal fascia. A pale slab promenade with granite sett borders passes its south-west face from a paved south plaza (two trees in kerbed pits) to the north-west; a paved band crosses west; narrower slab paths lead to the porch and north to a footbridge landing. Two asphalt cycle paths with yellow dashed centre lines and flush concrete edges run north-south; the eastern one rises onto a raised concrete boardwalk with dark steel and mesh railings on both sides along a rip-rap bank. Kerbed lens-shaped beds of ornamental grasses, shrubs and pink, lavender and white perennials fill the spaces between the paths; groves of rounded deciduous trees stand north of the pavilion and along the boardwalk; timber benches on dark steel frames and corten bins sit on the paving. North of the top-view frame (inferred from the front and oblique) the boardwalk lands on a plaza at a cambered concrete footbridge on two piers that crosses the Bow to a wooded far bank. The downtown skyline in the sources is distant context and is not modelled. Judge it as a park: plan legibility, the pavilion as focal point, paths and edges, planting composition and density, river edge, furniture and pedestrian-scale finish against docs/HIGH_QUALITY_3D_PARK_MEMORY.md (the conservatory benchmark), not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (green-roofed timber pavilion with a glazed face on a wide slab promenade, lens-shaped beds of grasses and flowers, asphalt cycle paths with yellow dashes, a railed boardwalk along a rip-rap bank of the Bow, groves of rounded trees, a footbridge to the far bank),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan against the top view (pavilion position and rotation, promenade, cycle paths, beds, groves, boardwalk, bank), pavilion (green roof, fascia, cedar cladding, glazed south-east face, south-west door and glazing, porch, posts, interior), promenade (slabs, sett borders, joints), south plaza and tree pits, cycle paths (asphalt, yellow dashes, edges), boardwalk (deck, kerbs, railings, ramps), rip-rap and bank grasses, river, planting beds (kerbs, grasses, shrubs, flowers), trees, benches and bins, footbridge (deck, piers, abutments, railings, landings), far bank, materials hierarchy, aerial and pedestrian-scale finish against the park benchmark. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v005/review/independent-review.md. Do not run the build.

## Context for this review (v005)

v005 is the user-reopened second pass's last version under the stopping rule. It keeps the v004 kit plants (the
primitive-planting finding v004 fixed) and targets exactly the four P1s of the v004 review. Score against the
candidate v003 (0 P0 / 1 P1) and v004 (0 / 4).

- **P1 #1, bare fill at the bed margins** (front, promenade_beds, west_path, porch_northwest): a margin pass plants a
  low band on rings 0.44 m and 0.86 m inside every kerb (blue edging grass, white alyssum cushions, small salvias, in
  runs of 3 to 6); within 12 m of each eye-level camera small cushions also run on a ring 0.27 m inside the kerb; the
  groundcover now undulates (2.8 cm) instead of lying flat. The kit clearance rule still keeps every canopy 3 cm
  inside the kerb, so leaves do not spill over it. Look at the strip along each near kerb.
- **P1 #2, grove bed regressed to lawn** (right_side, rear_side, rear, front_corner, aerial, porch_northwest,
  boardwalk): the bed between the pavilion and the boardwalk is planted at 1.4 m spacing (was 2.1 m) with large, wide
  clumps of fountain and feather-reed grass, leafy shrubs, astilbe and panicles, plus two edging rings.
- **P1 #3, pure-black holes**: crossing joint lines now sit on two levels 0.8 mm apart (plaza slab grid, sett running
  joints, band ends), so no two joint quads share a plane; bench legs stop under the slats, the cross rail is
  narrower than the legs and the back post clears the slat faces; each pavilion door leaf runs 1 cm into the sill
  over a solid threshold that covers the plane the floor slab shared with the opening's floor. Check bench_plaza,
  front, promenade_beds, pavilion_close (SW door), porch_northwest (both doors) and west_path (bench back).
- **P1 #4, black seam along the footbridge deck edge**: each kerb is now one lofted piece 2 cm proud of the deck side
  face (the old segmented edge beams shared that face). Check footbridge and rear_side.

Also changed for the 4 MiB cap (GLB about 4.18 MB): grass crowns share their blade role; the front drifts carry
fewer pink coneflowers and more shrub and fountain-grass mass (towards v004 P2 #5); boardwalk pickets are 200 mm apart
(was 170 mm); kit instance nodes have short names and drop three constant tags. The P2s of v004 other than #5 are not
addressed.
