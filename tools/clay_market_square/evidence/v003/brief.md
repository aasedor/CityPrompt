You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v003
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (plaza flare, bowl arcs and chord, stage on axis), paving slabs and joints, bollard grid (rows, spacing, offset, size), floor drains, seating tiers (count, steps, stone risers, concrete treads, terraces), cheek walls, raised meadow beds and stone retaining walls with copings, upper terrace, stage platform and curved fascia, pavilion (slat cladding, returns, roof slab, loudspeakers, backstage door), floodlight masts and lamp heads, trees and meadow, lawn and context, materials hierarchy, grounding (nothing floating or below grade). Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 3 P1:
1. P1: the pavilion and stage were under-scaled for the bowl, and the bowl did not wrap the stage. The pavilion roof spanned about 0.37 of the bowl-foot chord against about 0.62 in the source, and the stage about 0.44 against about 0.75. All three tiers ended well south of the stage front, so the stage sat in a narrow slot between two large rectangular beds.
2. P1: the three steps per tier were not legible. The stepped band of each tier was about 0.55 m deep against terrace walks of about 2.6 m, and the treads were the same warm stone as the risers with no nosing line, so each tier read as one coursed stone wall instead of stone risers under pale concrete treads.
3. P1: the plaza did not fan out at the bowl foot. In the source the stone bed walls leave each foot end about 20 to 25 degrees off the foot line, so the plaza fans wide at once and the low bed walls flank the bowl foot in the front view. The render's plaza edges ran nearly parallel to the axis, and large rectangular beds replaced the source's low wedge beds.

The builder claims each is fixed:
1. The stage platform is now 27 m wide (about 0.75 of the 36 m foot chord), with the same dark curved front fascia. The slatted pavilion is 21.6 m wide (about 0.6 of the foot chord) and taller (5.6 m under the roof slab), with its loudspeakers, end caps and backstage door moved to suit. The stacked-stone cheek walls moved out to the stage ends (about 14.5 m off the axis), still stepping up toward the back with the stage side steps between wall and stage. The tier lines are no longer concentric circles. Each is y = u + c x^2, and the bend c changes through the bowl: the foot is concave to the plaza, as before, the tiers straighten as they rise, and the top tier bends forward. Its ends reach the stage-front line, so the top walk wraps around the stage at upper-terrace level and the cheek walls close it. The top tier spans about 58 m.
2. Each tier is now three distinct steps. Treads are 0.55 m deep and the terrace walks narrower (1.0 m plus the last tread), so the stepped band is about as deep as the walk. Every riser stays coursed warm-grey ledgestone. Every tread is now PALE concrete, 6 cm thick, with a 5 cm nosing that throws a dark shadow line over the stone riser below, so three pale tread lines and three stone risers read per tier.
3. The low bed walls now leave each foot end 22 degrees off the foot line and run out to the edge of the site. The plaza fans wide at once, and bollard row 1 is now about 1.5 times the foot chord. Each low bed is a wedge between that splayed wall and the high bed, with a shade tree. The front camera stands closer with a wider lens, so the low bed walls show at both edges of the frame as in the source front.

Cheap P2s the builder claims:
- each floor drain is a single square slotted grate centred in a slab;
- the left_side, right_side and rear views are framed tight on the site;
- extra shade trees on the low wedge beds beside the bowl ends.

Verify each in the pixels (top, aerial, front_corner, front, seating_tiers, cheek_walls, stage_pavilion, meadow_beds, paving_drain, left_side, right_side, rear); do not take the builder's word. Measure the pavilion and stage against the bowl-foot chord and the splay of the bed walls against the locked top and oblique.

The v002 fixes must still hold: the lowest tier concave to the plaza, as in the source; stubby drum bollards on the 3 m grid, five rows with alternate rows offset; stacked-stone cheek walls at both stage ends. The v001 fixes must also hold: stacked ledgestone on every riser, with bed and staggered head joints reading as dark lines. So must everything the source shows that earlier versions got right: square slabs with stronger 6 m joints; the slatted open-fronted stage pavilion under a deep dark roof with loudspeakers; the two floodlight masts with stacked lamp heads; the raised stone-walled meadow beds with shade trees; the meadow and lawn beyond.
