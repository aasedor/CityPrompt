You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, gate_arch, gate_piers_fence, bandstand, bandstand_roof, carpet_beds, inner_lawn_beds, loop_benches, mature_trees, side_entrance, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a fenced rectangular Victorian public garden block (about 43 x 57 m, long axis north-south) between city streets on all four sides (the top view governs the plan). A straight brick-paved axis runs from the main south gate to the north fence; an east-west cross path meets it at a round paved circle holding an octagonal white timber bandstand with a pink-copper ogee roof, balustrade, fretwork arches and a front stair, ringed by a flower bed. An oval loop path leaves the axis north of the bandstand, swells out to cross the cross path near the side fences and returns straight south to the gate, framing four leaf-shaped inner lawns each with a long carpet bed (white hydrangeas on the spine, lavender, purple and pink flowers either side) and four outer lawns under big mature shade trees. Granite edging lines every path. A black wrought-iron picket fence on a granite curb closes the block; the south front has a grand gate of two tall brick piers on granite bases with iron lanterns, an iron arch with the gilded sign HALIFAX PUBLIC GARDENS / FOUNDED 1867 under a crest (lettering is abstract blocks in clay), double iron gates thrown open, and two lower ball-capped side piers with gates where the loop legs enter. Benches line the loop, lamp posts stand at the circle and side entrances; brick mid-rises and a glass office block line the streets as plain context. North and side entrances, bed planting mixes and the street blocks are teaching assumptions; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (fenced Victorian public garden: grand brick-and-iron sign gate on the south axis, white octagonal bandstand with a pink-copper roof at the centre of a paved circle, oval loop and cross paths framing leaf-shaped carpet beds of hydrangeas and mauve flowers, mature shade trees in the corner lawns, black iron picket fence),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (block ratio, axis, cross path, paved circle, oval loop legs and swell, four leaf lawns, four outer lawns), path paving colour and granite edging, gate (tall brick piers on granite bases, lanterns, iron sign arch with crest and two-line sign, open double gates, ball-capped side piers and side gates), fence (pickets, rails, posts, granite curb, continuity round the block), bandstand (octagon, posts, fretwork arches, balustrade, stair, ogee copper roof and finial, ring bed), carpet beds (shape, hydrangea spine, colour bands, soil edge), shade trees (count, placement, trunks at grade), benches and lamps, context streets and buildings, no coplanar paving or bed surfaces, all vertices at or above grade, framed locked views. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 0 P0 and 3 P1.
1. Aerial: a nearby context building's roof filled about 40 to 45% of the frame (lower right) and hid the east sidewalk, the east street and the east context frontage.
2. The free-standing hydrangeas and lawn shrubs were each one large faceted icosahedron, several balanced on a single lower vertex, so they read as white and green boulders or gems touching the lawn at a point.
3. The plan departed from the top source: the north half of the loop was a semicircle meeting the north axis in a right-angle T, so the north inner lawns were square-cornered fans rather than rounded leaf islands, and no lawn corner at a path junction was rounded.

The builder claims each is fixed:
1. The aerial camera now stands high over the south street (16, -52, 72 m, looking at the garden centre, 30 mm lens), so no context mass lies between it and the block; the garden, all four bounding streets and the context frontages should read.
2. Every free-standing shrub and hydrangea is now a cluster of grounded lobes: a broad green base dome whose flat base ring is sunk 3 cm into the lawn, with three or four smaller lobes and a crown lobe on top (white, pink or purple flower heads for the hydrangeas, foliage for the shrubs). The hedge mounds on the outer lawn strips are grounded domes too. No lobe stands on a vertex.
3. Each half of the loop now runs from the gate up its leg, through the S-bend to the cross path, then up a broad arc that swings in and joins the north axis in a Y at about y = 20 m (about 42 degrees to the axis), as in the top view; the two north inner lawns are leaf islands with rounded tips pointing up the axis. Broad filleted paving (about 2 m radius; about 0.7 m at the north lawn tips) now rounds every lawn corner where the circle meets the axis and the cross path and where each loop arc crosses the cross path, and the granite edging follows the rounded lawn outlines.

Cheap P2s the builder claims: the long paths are plain brick colour without plank-like transverse joints (the circle keeps its concentric and radial courses); the bandstand hip rolls overlap with no dark notches; every bench has a front arm support; the front-view bench now has its back to the camera and faces the garden; a south context row and far sidewalk now stand beyond the south street; the gate_piers_fence camera no longer has a lamp in the middle of the frame; the benches on the north arcs sit on the outer side of the arcs facing the path.

Verify each claim in the pixels; do not take the builder's word. Compare top and front_corner against the locked top view (the Y junction, the leaf-shaped north lawns, the filleted corners), check aerial for any blocking roof, and zoom on rear, rear_north, loop_benches, left_side, mature_trees, side_entrance and gate_piers_fence to confirm no shrub balances on a point. The v001 strengths must still hold: the brick-pier gate with lanterns and the gilded sign arch, the white octagonal bandstand with its pink-copper ogee roof and flower ring, the four carpet beds, the mature shade trees, the iron fence on its granite curb and the side gates.
