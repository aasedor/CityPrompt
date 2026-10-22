You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, steam_clock, storefronts, name_frieze_pediment, glass_close, architecture_close, east_facade, facade_close, roof_skylights, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a Victorian red-brick and buff-sandstone corner commercial block in Gastown, Vancouver, on the corner of a cobbled street (south, the front) and an asphalt street (east), with brick sidewalks (the top view governs the plan: a nearly square block about 26 m by 24 m): three storeys, ground-floor shops and two upper floors; rusticated sandstone piers at the west end and at the corner, brick pilasters with carved stone capital panels between the bays; the south front has five bays, four with one wide round-arched three-light window on the top floor over a three-light window with a transom, and a wider corner bay with a pair of arched windows over a pair of sash windows; stone sill bands and lintel bands, a deep stone frieze lettered GASTOWN COMMERCE BUILDING, a bracketed modillion cornice with dentils, and a pediment over the central bay with a carved shell in the tympanum and an acanthus crest, flanked by short pedestals; the ground floor is a row of shopfronts between rusticated stone piers with panelled bulkheads, plate glass, small-paned transoms, recessed glazed timber doors, a dark signboard fascia with gilt lettering (a cafe sign) and a moulded shop cornice; the corner shop wraps onto the east street; the east front continues the frieze and cornice over the wide corner bay, four narrow bays of single sash windows on all three floors over a stone plinth, and a pilastered end bay with paired arched windows over paired sashes and a side door; flat tar roof inside a stone-coped parapet with a brick chimney, a clapboard stair penthouse, a small skylight and two glazed pyramid skylights; on the corner sidewalk the steam clock (stone base, bronze pedestal, glazed cabinet with brass works, four-faced clock head, small roof with steam whistles) among chained bollards; globe-cluster lamp posts on the sidewalks; a lower cream-painted neighbour adjoins on the west, a cobbled lane and brick blocks beyond, a brick block adjoins on the north, and brick warehouse blocks face it across the east street. The west and north walls (party walls rising above the neighbours) are not visible in the front or oblique; the steam whistles' plume of steam is not modelled; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (three-storey red brick and sandstone Gastown corner block with arched top-floor windows, a lettered frieze, a bracketed cornice and a crested pediment, shopfronts, and the steam clock on the corner),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, plan (top view, near-square, party walls), bay rhythm on both street fronts (five south bays; corner bay, four narrow bays and paired-arch end bay on the east), rusticated sandstone corner and end piers, brick pilasters and carved capitals, window types per floor (arched three-light top floor, transomed windows below, paired windows in the corner bays, narrow sashes on the east), sill and lintel bands, lettered frieze, modillion cornice and dentils, pediment (shell, crest, pedestals), shopfronts (bulkheads, glass, transoms, recessed doors, signboards, shop cornice), roof (parapet coping, chimney, penthouse, skylights), steam clock, bollards and chains, globe lamps, paving (brick sidewalks, setts, asphalt), neighbours, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v002/review/independent-review.md. Do not run the build.

## Context for this review (v002)

v001 was reviewed FAIL with P0 = 0, P1 = 5, P2 = 9 (`tools/clay_gastown_heritage_commercial/evidence/v001/independent-review.md`).
v002 is one targeted rework of those five P1s; judge each from the pixels and score against v001 (0 / 5).

| v001 P1 | v002 change | where to look |
|---|---|---|
| 1 Pure-black slots in the south jamb of the east corner-shop entrance | Every shop cut is now closed by continuous stone jamb liners from the wall face back to the shopfront frame, so no rustication course looks into the wall void | east_facade, right_side, front_corner |
| 2 Pediment raking members overshoot through the right pedestal, a dark wedge between them, a doubled raking edge | Raking cornices now stop 0.12 m inside the pedestals, which are deeper than the cornice, so the ends die cleanly into them; the cornices and the apex block run over the full tympanum depth, giving a closed sloping back with no second slab | front_corner, roof_skylights, name_frieze_pediment, rear_north |
| 3 Steam clock undersized, head below the shop cornice, too close to the facade | Clock scaled 1.42x in height and 1.3x in width about its base: the four-faced head now sits above the shop cornice and the whistles reach the lower second-floor windows; it stands about 2.1 m off the south face (top view) | front, steam_clock, front_corner, top |
| 4 Missing facade_close, architecture_close, glass_close | arched_windows became glass_close (one arched top-floor window: reveal, frame, fan); corner_pier became architecture_close (corner pier capital, frieze and bracketed cornice); cornice_brackets became facade_close (a typical south bay through all three floors). Still 18 views | glass_close, architecture_close, facade_close |
| 5 left_side and rear blocked by the neighbours | Both cameras are now elevated over the lower neighbours and show the west and north party walls from coping down to the neighbour roofs, the parapet and the roof footprint | left_side, rear |

Also (P2 #7): the north neighbour now runs east to the east building line, so the street wall is continuous.
Unchanged from v001 by design: the front, front_corner and top cameras (fitted to the locked views) and everything else.
Camera notes: steam_clock is re-aimed higher so the taller clock's head and whistles are in frame; rear_north now looks
down the gap west of the extended north block at the exposed north wall to grade (the north block covers the rest of
that wall, as the sources show a continuous street wall).
- Curbs on all three street edges now stand 2 cm proud of the sidewalk faces (coincident faces had left a thin black line along the south curb in front).
