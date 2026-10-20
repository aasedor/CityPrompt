You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, stage_pavilion, slat_wall, seating_tiers, cheek_walls, bollard_grid, paving_drain, light_mast, backstage_door, meadow_beds, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a serviced civic market and event square (the top view governs the plan). A large plaza of pale square concrete slabs (1.5 m slabs, a stronger joint every 6 m) flares outward toward the south and is set out with a regular 3 m grid of short grey utility bollards in five rows (alternate rows offset) with small square floor drains; there are no stalls or chalets in the source. At its north head a curved seating bowl of three concentric tiers on 29 m arcs (about 38 m chord), each tier three low steps of stacked warm-grey stone risers under pale concrete treads, with a wide terrace walk between tiers, rising to an upper terrace. On it a raised stage platform with a gently curved dark front edge and an open-fronted pavilion: back and side walls clad in vertical timber slats of mixed widths, depths and three tones, a deep flat dark roof slab, a loudspeaker near each end of the back wall. Two slender dark floodlight masts with six stacked lamp heads stand just outside the pavilion. Stacked-stone cheek walls step up beside the bowl; raised meadow beds retained by stacked stone line both flared plaza edges, planted with broad shade trees; lawn, a meadow field and a tree belt beyond. The backstage door in the east return, the stage side steps and the far lawn and tree belt are teaching assumptions; the meadow grass is abstracted as clumps. The source is backlit at golden hour; judge form and material hierarchy, not lighting.; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (flared bollard-gridded plaza of square slabs facing a curved three-tier stone-and-concrete seating bowl and a timber-slatted stage pavilion under a flat dark roof, framed by stacked-stone meadow beds with shade trees and two floodlight masts),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (plaza flare, bowl arcs and chord, stage on axis), paving slabs and joints, bollard grid (rows, spacing, offset, size), floor drains, seating tiers (count, steps, stone risers, concrete treads, terraces), cheek walls, raised meadow beds and stone retaining walls with copings, upper terrace, stage platform and curved fascia, pavilion (slat cladding, returns, roof slab, loudspeakers, backstage door), floodlight masts and lamp heads, trees and meadow, lawn and context, materials hierarchy, grounding (nothing floating or below grade). Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 1 P0 and 3 P1.
1. P0: the seating bowl curved the wrong way. In all three sources the tier edges are concave to the plaza (∩ in the top and oblique views): the plaza pushes into the bowl on the centre line, the tier ends sweep south toward the viewer, and the tiers get longer as they rise, with the stone bed walls diverging northward. The render had arcs centred on the stage, convex toward the plaza and narrowing toward the stage, with the inner bed walls converging northward.
2. P1: the risers read as smooth, thin, low-contrast beige strips under thick pale treads, with no stacked-stone coursing, so the bowl read as a plain concrete stair.
3. P1: the bollards were about 3:1 height to width; the source bollards are short and stubby, about 1.5:1.
4. P1: the stacked-stone cheek walls at both ends of the stage were missing, leaving the upper terrace open beside the stage.

The builder claims each is fixed:
1. The tier arcs are now centred on the plaza axis 40 m south of the bowl foot (radii 40 m at the plaza to 47.4 m at the upper terrace edge), so every tier is concave to the plaza and the tiers widen as they rise, from a 36 m chord at the foot to about a 50 m chord at the terrace. The stone bed walls beside the bowl run along a straight line from the foot ends that diverges northward, and a high-bed retaining wall follows a concentric arc about 1.6 m behind the top tier before returning to the stage. The stage front stays convex toward the plaza. The plaza flares wider toward the south and the bollard rows moved south so the first row stands in front of the bowl ends.
2. Each riser is now full height (0.30 m, so the first tier top matches the 0.9 m low bed wall as in the source front) under a thin 30 mm tread. Every riser face carries stacked ledgestone: two or three courses of long flat stones in three warm-grey tones, standing proud of a dark bedding mass so the bed and staggered head joints read as dark lines. Step treads are warm stone; the terrace walks between tiers stay pale concrete.
3. The bollards are short drums, 0.43 m above the paving on a 0.32 m diameter (about 1.35:1), with a slightly smaller cap; the 3 m grid, five rows and alternate-row offset are kept.
4. A pair of stacked-stone cheek walls with concrete copings stands at each stage end on the upper terrace, stepping up toward the back (0.75 m then 1.15 m above the terrace), parallel to the pavilion returns, with the stage side steps between each wall and the pavilion.

Cheap P2s the builder claims:
- wider slat tone spread (lighter and darker timber);
- flush, slotted floor drains instead of proud plates;
- the two stray benches on the outer lawn removed;
- the front camera raised and pulled back so the bowl reads as tiered;
- the back face of the upper terrace dressed in coursed stone.

Verify each in the pixels (top, aerial, front_corner, front, seating_tiers, cheek_walls, bollard_grid, paving_drain, meadow_beds, rear_north); do not take the builder's word. Compare the bowl curvature directly against the locked top and oblique. The things v001 got right must still hold: the flared bollard-gridded plaza with square slabs and stronger 6 m joints; the three tiers of three steps; the slatted open-fronted stage pavilion under a deep dark roof with loudspeakers; the two floodlight masts with stacked lamp heads; the raised stone-walled meadow beds with shade trees; the meadow and lawn beyond.
