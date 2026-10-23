You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/spine/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, boulder_garden, rest_balconies, roof_terrace, retail_base, facade_close, architecture_close, glass_close, interior, rooftop_plant, east_facade)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a fifteen-storey mixed-use climbing tower on a downtown block about 52 m wide and 27 m deep (the top view governs the plan), on a plaza between two side streets with a street in front (south): a double-height glazed retail base, thirteen floors of dark bronze glass curtain wall with bronze vertical fins (wider-spaced on the street front, close fins and sunshade bars on the side faces) and a glazed roof amenity storey with bronze fins set back over the north part of the roof; the street front has a deep central notch between a west wing and an east wing, and in the notch stands the spine, a light warm-grey sculpted precast-concrete climbing strip about 7 m wide running from the plaza to about six metres above the roof, carved into vertical flakes and ledges with sparse holds, its foot flaring into the plaza; west of the spine the notch is dark recessed glazing; east of it a light concrete wall with doors carries six rest-station balconies (copper slab edges, timber decks and soffits, steel picket railings) spanning from the spine to the east wing and stepping a little past the wing; the roof of the street half is a U-shaped paved terrace inside a light coped parapet with L-shaped planting beds and large sculptural granite boulders; the amenity roof carries condensers, air handlers, ducts and a stair overrun; a white canopy runs in front of the west wing shopfronts; at the spine foot a boulder garden of curved kerbed planters with granite boulders, grasses and shrubs, a second planter to the east and a long planter to the west, street-tree pits and lamp posts on the sidewalk; tan and red brick walk-ups across the west street, a white mid-rise to the north, a white block and a glass tower across the east street, low brick blocks across the south street, as simple context massing. The north face, the north half of the side faces and the interiors are not visible in the sources; the catalogue text says 20-35 storeys but the pixels show fifteen; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (bronze glass tower with a full-height sculpted light concrete climbing spine in a street-front notch, six stacked rest-station balconies beside it, a boulder roof terrace around a glazed amenity storey, and a boulder garden at the spine foot),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/spine/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, plan (top view: 2:1 block, street-front notch, amenity block over the north half), curtain wall (vision glass, spandrels, fin rhythm, side-face sunshade bars), the spine (width, height above the roof, carved relief, holds, flared foot, cap), notch west glazing and notch east wall, rest-station balconies (count, levels, copper edges, railings, support), roof terrace (parapet coping, beds, boulders, paving), amenity block and roof plant, base (canopy, shopfronts, lobby glazing, entrances), boulder garden and plaza planters, street trees and lamps, streets and crossings, context massing, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/spine/v001/review/independent-review.md. Do not run the build.
