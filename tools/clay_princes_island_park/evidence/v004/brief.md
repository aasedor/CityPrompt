You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan against the top view (pavilion position and rotation, promenade, cycle paths, beds, groves, boardwalk, bank), pavilion (green roof, fascia, cedar cladding, glazed south-east face, south-west door and glazing, porch, posts, interior), promenade (slabs, sett borders, joints), south plaza and tree pits, cycle paths (asphalt, yellow dashes, edges), boardwalk (deck, kerbs, railings, ramps), rip-rap and bank grasses, river, planting beds (kerbs, grasses, shrubs, flowers), trees, benches and bins, footbridge (deck, piers, abutments, railings, landings), far bank, materials hierarchy, aerial and pedestrian-scale finish against the park benchmark. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/pisland/v004/review/independent-review.md. Do not run the build.

## Context for this review (v004)

The user reopened the family for a second pass that replaces its planting with the shared planting kit (kit v003.1,
`tools/clay_planting_kit_showcase`). v004 = v003 with only the bed planting changed; score it against the candidate
v003 (P0 = 0, P1 = 1: at eye level the beds read as primitives, faceted cone flower heads, flat straw-ribbon grasses
and bare fill between mounds).

What changed:
- Every bed's own primitives (cone heads, ribbon grasses, dome mounds, the hummock berm and the flat bed fill) are gone.
  Each bed keeps its kerb and plan; inside it is a kit groundcover carpet (lapped under the kerb) planted with
  instanced kit plants: feather-reed grass with straw plumes, green fountain grass, pink coneflower, lavender salvia,
  white panicles, pink astilbe, a small blue edging grass and a 0.8 m leafy shrub kept to a minority.
- Planting is a dense drift: species grouped by low-frequency noise, the big masses (scaled up to 1.5x in plan,
  not in height) fill the middle of each bed, smaller copies of the same species run out to the kerb, and a second
  pass fills the margins with small edging plants. The kit clearance rule keeps every delivered canopy inside its
  kerb and clear of tree trunks (audit 0).
- The two grove beds under the trees (north-west of the pavilion and along the boardwalk) are planted more sparsely
  with grasses, shrubs and a few perennials; the bed beside the promenade (seen close in promenade_beds) is denser.
- The south plaza tree pits carry groundcover and a ring of small grasses and salvias.
- The family build now keeps kit instances out of the per-role join (glTF node instancing, as in the kit showcase).

Where to look: front, promenade_beds, west_path, bench_plaza, glazing_close and porch_northwest for eye-level planting;
aerial, top and front_corner for the bed pattern from the air, which must still match the top source. Everything
else (pavilion, sedum roof, paving and setts, cycle paths, boardwalk and railings, rip-rap, trees, footbridge) is
unchanged from v003 apart from random jitter in the sedum roof and far-bank understorey (their random stream no
longer follows the old planting). Check that no earlier fix regressed.
