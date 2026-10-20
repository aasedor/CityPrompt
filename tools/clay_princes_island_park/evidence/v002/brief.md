You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v002
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan against the top view (pavilion position and rotation, promenade, cycle paths, beds, groves, boardwalk, bank), pavilion (green roof, fascia, cedar cladding, glazed south-east face, south-west door and glazing, porch, posts, interior), promenade (slabs, sett borders, joints), south plaza and tree pits, cycle paths (asphalt, yellow dashes, edges), boardwalk (deck, kerbs, railings, ramps), rip-rap and bank grasses, river, planting beds (kerbs, grasses, shrubs, flowers), trees, benches and bins, footbridge (deck, piers, abutments, railings, landings), far bank, materials hierarchy, aerial and pedestrian-scale finish against the park benchmark. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 0 P0 and 5 P1.
1. P1: the promenade's sett borders were missing. All three sources show wide, flush bands of dark grey granite setts along both edges of the promenade, crossing it, and framing the south plaza. The render had only narrow pale concrete ribs standing proud of the slabs, which read as trip kerbs and as thin grey lines from above.
2. P1: the planting read as primitives. The grasses were rigid single-tone cones, the perennials floating octahedral "gems" on hair-thin stems, and the shrubs large faceted boulders balanced on the soil. The pink, lavender and white flower drifts of the oblique and top sources were reduced to sparse specks, well below the conservatory benchmark.
3. P1: the sedum roof read as flagstones. It was a smooth lawn-green plane strewn with pale polygonal plates, not the fine continuous ochre-and-olive mat of the oblique and top sources.
4. P1: the boardwalk and footbridge railings were solid panels. Opaque grey sheets between dark posts read as sound-barrier walls; the oblique source shows an open steel picket railing you can see through.
5. P1: the far bank was not wooded. It was a bare strip with one straight row of five identical trees; the oblique source shows the footbridge landing in dense woodland.

The builder claims each is fixed:
1. Every slab path now has flush dark granite sett borders: 0.8 m bands on both edges of the promenade, 0.7 m on the west crossing and 0.4 m on the narrow paths, standing only 3 mm above the slabs in a dark warm-grey sett material. Dark joint lines lie across each band about every 0.45 m, with a running centre joint on the wide bands, so they read as two setts across. Dark sett bands about 0.8 m wide cross the promenade at about 13 m intervals. A 0.6 m sett frame with the same joints runs round the whole south plaza. The pale raised ribs are gone, and the slab joints are now flush lines.
2. The beds were replanted as authored landscape. All planting is smooth-shaded, so nothing reads faceted.
   - **Grasses:** arching clumps of seven or eight flat blades in mixed green, gold and straw, which rise steeply and bow outward.
   - **Perennials:** low mounded leafy drifts, each carrying a domed pink, lavender or white flower mass, with extra flower heads on its flanks.
   - **Shrubs:** rounded masses of two or three overlapping lobes, their bases sunk into the bed.
   - **Bed fill:** a dark planted-ground green instead of bare soil.
3. The sedum roof is now three interleaved, finely undulating mats (olive, ochre and rust) on 0.25 m grids, so the visible top changes colour in small patches across the whole roof, with about 170 small flowering clumps. The mat sits just below a thinner dark fascia; a timber beam band now runs under the fascia (a P2).
4. The boardwalk and the footbridge have open galvanised picket railings: light steel posts, a top rail, a bottom rail and slender round pickets about 140–160 mm apart, with no panels. You can see the deck edge, planting and water through them.
5. The far bank is now a wood. About thirty trees of varied size stand in up to four staggered rows round the bridge landing and two rows to the south, with crowns in three greens. Rounded understorey mounds run along the shore and under the trees, and boulders line the waterline.

Cheap P2s the builder claims:
- the rip-rap is now grey-brown rounded boulders of mixed size (2–3×), with grass clumps between them;
- tree crowns are rounder (smooth-shaded) in three greens;
- the rear camera is raised so the pavilion roof reads over the north grove;
- the green_roof camera is moved clear of the plaza tree that blocked its foreground.

Verify each in the pixels (front, promenade_beds, bench_plaza, aerial, top, front_corner, glazing_close, west_path, green_roof, boardwalk, right_side, footbridge, rear); do not take the builder's word. Compare the sett bands, planting and railing directly against the locked oblique and top. The things v001 got right must still hold:
- the plan and the pavilion position and rotation;
- the promenade, south plaza, west crossing and cycle paths with yellow dashes;
- the lens-shaped kerbed beds;
- the cedar pavilion with its glazed south-east face, door, corner glazing and porch;
- the raised boardwalk along the rip-rap bank;
- the footbridge on two piers;
- the benches and corten bins.
