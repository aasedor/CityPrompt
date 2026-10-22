You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v002
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and roof (low hip, short ridge, standing seams, hip caps, thin fascia, skylight), plan (glazed bay and recessed porch at the front line, end fin, rear garage), storey heights and plinth, cedar cladding (vertical boards, tone variation, joints, horizontal panel over the side entry), glazed corner (black frames, two lights per face per storey, spandrel, transoms), balcony (steel fascia with bolts, glass railing, cap rail, sliding wall behind), porch (front door, sidelight, window, cedar ceiling, landing and steps), front cedar band, side-street wall (tall narrow windows, lamp, recessed side entry and steps, small windows, downpipe), garage (board door, hip roof), garden beds (ferns, grasses, fescue, maple), sidewalks, curb radius, walk, parked cars, utility pole and wires, neighbour house and fence, trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/laneway/v002/review/independent-review.md. Do not run the build.

## Context for this review (v002)

v001 was reviewed FAIL with P0 = 0, P1 = 8, P2 = 10 (`tools/clay_vancouver_laneway_house/evidence/v001/independent-review.md`).
v002 targets each P1; judge every fix from the pixels and score against v001 (0 / 8).

| v001 P1 | v002 change | where to look |
|---|---|---|
| F1 black wedges at the side-entry head corners | Linings rebuilt: both returns lap 10 mm into the wall carrier and stop 1 cm inside the head; the head lining's face sits 7 mm behind the returns' faces (the v001 wedges were coplanar overlapping return and head faces); floor edge also set back | side_entry, west_wall |
| F2 black squares at the glazed-corner frame nodes | Rails and transoms are 12 mm shallower than the posts and mullions (no shared front or back planes at any crossing) | glass_close, facade_close, front |
| F3 black slot at the base of the east end fin | Fin plinth and bay plinth 4 mm proud of the main foundation and lapped 0.3 m along it (no shared face at the junction) | right_side, aerial |
| F4 side-entry door hidden in front / front_corner; flat lining | Recess depth 0.9 → 0.45 m; door moved toward the north return; returns, back wall and head lined in horizontal boards with joints; mailbox on the south return | front, front_corner, side_entry, west_wall |
| F5 garage roof turned 90° | Garage roof rebuilt: north slope plus two steeper hipped ends rising to a 2.4 m east-west ridge buried in the rear wall, with a wall flashing; seams run down each slope; garage depth 6.0 → 2.6 m (top view: its north eave now sits about 2.6 m beyond the main eave, closer to the source than v001); garage door and side door re-centred | top, rear, rear_side, garage |
| F6 sword ferns missing, side-street bed bare | New sword-fern prototype (arching pinnate fronds with 18 pairs of tapering leaflets, two sizes); fern masses placed first in every bed, then the other species; the kerbless side-street and front beds let fronds overhang the sidewalk edge and lean back against the wall | garden, front, front_corner, west_wall, entry_steps |
| F7 right_side too close | Now a high south-east oblique over the fence and the neighbour's eave: roof, front facade, fin and the upper east wall (the lower east wall stays hidden by the fence and neighbour in the 1.5 m side yard) | right_side |
| F8 top cuts off the garage | Ortho re-centred and widened (scale 19.3 → 20.6) to include the whole garage roof | top |

Cheap P2s also addressed: balcony fascia bolts reduced to 8 paired heads (F11), hip and ridge caps narrowed (F12).
Not addressed: F9 transom pattern, F10 porch transom, F13 extra side-entry steps and offset panel, F14 large backdrop
trees, F15 neighbour half-storey, F16 interior camera, F17 board dimming.
