You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entry_steps, side_entry, west_wall, roof_seams, garage, interior, garden (glass_close is the glazed corner, architecture_close the balcony fascia and railing))
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a compact two-storey Vancouver laneway house on a street corner, the front street south and a side street west (the top view governs the plan): a 7.4 x 8.1 m volume under one low hipped roof of dark standing-seam metal with a short ridge running front to back, thin dark fascias, a cedar soffit and a skylight on the west slope; every wall clad in vertical cedar boards of varied tone with fine dark joints on an exposed concrete plinth; at the south-west corner a two-storey glazed bay in heavy black frames projecting about a metre to the front line, two lights on each face per storey with a black spandrel at the upper floor; east of it, between the bay and a full-height cedar end fin, a recessed upper four-light sliding wall behind a balcony with a grey steel channel fascia with bolt heads and a frameless glass railing, and under the balcony a cedar-lined porch with a wood front door, a sidelight and a two-light window, reached by concrete steps and a walk from the front sidewalk; a deep cedar band across the whole front under the roof edge; on the side street a tall narrow window pair, a wall lamp, a cedar-lined recessed side entry with a wood door under a panel of horizontal boards, its own steps to the sidewalk, a small window over it and small rear windows; a one-storey cedar garage with a hipped metal roof against the rear wall, its board door facing the side street; planted beds of sword ferns, ornamental and feather reed grasses, blue fescue and a red Japanese maple; sidewalks and a rounded curb on both streets, two cars parked on the side street, a utility pole with wires, a two-and-a-half-storey stucco neighbour with a hipped shingle roof and a porch east of a board fence, and large trees behind. The east and rear walls and the interiors are not visible in the front, oblique or top views and are teaching assumptions; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (compact two-storey cedar-clad laneway house: low dark standing-seam hip roof, black-framed two-storey glazed corner, recessed balcony with a glass railing over a cedar-lined porch, deep cedar band under the front eave),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and roof (low hip, short ridge, standing seams, hip caps, thin fascia, skylight), plan (glazed bay and recessed porch at the front line, end fin, rear garage), storey heights and plinth, cedar cladding (vertical boards, tone variation, joints, horizontal panel over the side entry), glazed corner (black frames, two lights per face per storey, spandrel, transoms), balcony (steel fascia with bolts, glass railing, cap rail, sliding wall behind), porch (front door, sidelight, window, cedar ceiling, landing and steps), front cedar band, side-street wall (tall narrow windows, lamp, recessed side entry and steps, small windows, downpipe), garage (board door, hip roof), garden beds (ferns, grasses, fescue, maple), sidewalks, curb radius, walk, parked cars, utility pole and wires, neighbour house and fence, trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v003/review/independent-review.md. Do not run the build.

## Context for this review (v003)

v003 is v002 with one targeted fix for the v002 review's only P1 (N1: the front beds were a uniform low fern carpet, the
tall grass mass at the glazed corner was missing, and the ferns were about half the source height). Nothing else changed.
- **Bed in front of the glazed bay:** a back row of three tall feather-reed grass clumps (new prototype, plumes to about
  1.3-1.45 m) 0.74 m in front of the bay plinth, rising to the lower third of the glazing as in the source front and
  oblique; in front of it forest-grass mounds and blue fescue at larger scales; the bed is filled at 0.28 m spacing with
  forest grass, fescue, the smaller sword fern, a stiff spiky grass and some feather reed.
- **Sword ferns:** the prototype now has 24 fronds of 1.32 m and is placed at 0.35-0.55 plan scale with an upright
  stretch, so each fern stands about 0.8 m tall and 0.9-1.3 m across (was about 0.45 m); ferns are limited to roughly
  40-50% of each front bed (sparser fern pass in the bay-front bed), and still mass in the side-street beds.
- **Ground cover:** a low dark-green leafy carpet under both front beds, so the mulch shows only in small gaps.
- Where to look: front, front_corner, garden, entry_steps, glass_close, top.
Score against v002 (0 P0 / 1 P1). Confirm that F1-F8 (fixed in v002) still hold.
