You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (block ratio, axis, cross path, paved circle, oval loop legs and swell, four leaf lawns, four outer lawns), path paving colour and granite edging, gate (tall brick piers on granite bases, lanterns, iron sign arch with crest and two-line sign, open double gates, ball-capped side piers and side gates), fence (pickets, rails, posts, granite curb, continuity round the block), bandstand (octagon, posts, fretwork arches, balustrade, stair, ogee copper roof and finial, ring bed), carpet beds (shape, hydrangea spine, colour bands, soil edge), shade trees (count, placement, trunks at grade), benches and lamps, context streets and buildings, no coplanar paving or bed surfaces, all vertices at or above grade, framed locked views. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v004/review/independent-review.md. Do not run the build.

## Context for this review (v004, second pass reopened by the user)

The family had stopped at v003 with v002 as the candidate (0 P0 / 1 P1: the carpet-bed, ring-bed and strip-bed plants
read as faceted gems; v003's smaller smooth heads still showed hard 6-8-sided outlines and pointed crowns). The user
reopened it to replace the bed planting with the shared planting kit (`tools/clay_planting_kit_showcase`, kit v003.1).

v004 = v003 (its non-planting fixes kept: the continuous hip-roll tubes and the turned front bench, both confirmed by
the v003 review) + kit planting. Nothing else changed: plan, paths, bandstand, gate, fence, trees, free-standing shrubs,
hedges and context are v003's.

What changed, and where to look:
- Four leaf-shaped inner beds (top, front_corner, aerial, carpet_beds, inner_lawn_beds, loop_benches, rear): a flat
  clipped carpet-bedding rim (pink or magenta begonia with bronze-leaf and floret flecks, 0.34 m), a low groundcover band
  inside it, white mophead hydrangeas along the spine, and blocks of lavender, ageratum cushions and salvia either side.
- Bandstand flower ring (bandstand, bandstand_roof, front_corner, top): clipped magenta edge bands and a pink centre band,
  with white hydrangeas, lavender and salvia along its middle.
- North axis borders (rear_north, rear): a clipped ageratum rim and groundcover band, white hydrangeas alternating with
  pairs of lavender and salvia.
- Plants are instanced kit prototypes (4 prototypes, about 260 plants); the kit's clearance audit is 0 (no canopy
  crosses a bed edge) and the build fails otherwise.

Score against the candidate v002 (0 / 1). Judge whether the bed planting still reads as gems, pebbles, gumdrops or
tubes at eye level (carpet_beds, inner_lawn_beds, bandstand, loop_benches), and whether the aerial bed pattern (white
spines, purple and pink bands, a coloured ring round the bandstand) still matches the top and oblique sources.
Known risks from the builder: the clipped rims are flat colour bands with sparse flecks and may read as felt at eye
level; the hydrangea bodies show leaf shade between leaves; the free-standing shrubs, hedges and tree crowns are v003's
(P2s #2 and #3 of the v003 review are not addressed).
