You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/overhang/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, climbing_face, wall_base_contact, rim_interior, pool_deck, facade_close, architecture_close, glass_close, interior, plaza_planters, entrance)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is "The Overhang": a white precast and glass recreation centre on a corner block (the top view governs the plan: about 39 m on the south plaza and 36 m deep along a west street), with a dramatic faceted climbing wall of honey-toned cross-laminated timber leaning out over its granite plaza. The pool block on the west is three storeys: a recessed glazed ground floor behind white columns, two upper storeys of tall recessed windows between white precast fins and spandrel bands, and a deep white parapet band; its roof is a deck with a long infinity pool running north-south along the west edge (water to a glass weir and an overflow trough at the parapet), glass balustrades on the parapet, a row of white loungers along the pool and a roof garden of raised planters with grasses and small yellow-green trees at the north end. A one-storey white penthouse stands on the middle of the roof, glazed to the pool deck at its south end and solid with a door to the north, with an air-handling unit and fan on its roof; a four-storey east block with a membrane roof, two skylights and small plant completes the plan. On the south front the pool block shows a projecting white frame box holding two storeys of glass ribbons over recessed ground-floor glazing with two pairs of entrance doors. The climbing wall is a hollow, open-topped CLT shell about 21 m tall in folded planes: its foot stands on the plaza in front of the facade, it leans east as it rises, its west faces flare out at the foot and meet the pool block parapet at a fold, and its level rectangular rim (with a light timber fascia) cantilevers about 10 m over the plaza and the white ground-floor facade beside the pool block; the south face is a triangle widening from its foot and the east face overhangs the white facade below; dark and white climbing holds dot the faces (densest on the south face), three climbers are on the south face, and the open top shows the inner walls with white holds and a crash mat at the bottom. A grey granite plaza in two-tone bands with two raised planters of tall straw-coloured ornamental grasses lies to the south, a low planted strip along the east edge, bollards and lamp posts; a concrete west sidewalk with street trees in pits and lamp posts, a west street with crossings, an east street with parked cars, and brick mid-rise and residential blocks around. The north and east fronts are not shown by any source; the hollow interior and the building interiors are authored assumptions; the people on the plaza are not modelled; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (white precast and glass recreation centre with a rooftop infinity pool, glass balustrades, loungers and roof garden, a glazed penthouse, a projecting white frame box with glass ribbons over the entrance, and the faceted honey-timber climbing shell leaning out over the plaza with holds and climbers and an open top),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/overhang/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count (three-storey pool block, penthouse, four-storey east block), plan (top view), climbing shell form (foot on the plaza, lean and overhang, folded faces, level open rim and light fascia, contact with the plaza and the facade), holds and climbers, open top and inner walls, west front rhythm (fins, spandrels, recessed windows, glazed ground floor), south frame box and glass ribbons, entrance doors, parapet band, pool deck (infinity pool, weir and trough, balustrades, loungers), roof garden (planters, grasses, small trees), penthouse (glazing, solid end, roof plant), east block roof (skylights, plant), white facade under the overhang, plaza (paving bands, grass planters, bollards, lamp posts), sidewalks, street trees, streets and crossings, parked cars, neighbours, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/overhang/v004/review/independent-review.md. Do not run the build.

Context for v004 (built from v003; what changed; judge the pixels independently):
- West street front re-moduled from 10 to 13 fin bays (about 2.77 m) over the same length, keeping the fins, spandrels and two-pane recessed windows.
- Shell holds: the upper flare and the big west faces are now plain timber. White holds are kept only in a band of about 1.7 m along the west/south fold (about 18 holds). The south-face dark holds, the climbers and the inner-wall holds are unchanged.
- Smaller changes:
  - The SW corner's stray parapet stub is closed.
  - The wall under the east overhang is plain white, with glass ribbons only beyond it.
  - Frame-box ribbons now have 5 panes.
  - The plaza grass is about 1.5x denser.
  - There are 8 west street trees.
  - The crash mat is lighter and the CLT slightly lighter and less saturated.
  - facade_close is raised above the tree crowns.
