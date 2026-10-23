You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v003
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, plan (top view, near-square, party walls), bay rhythm on both street fronts (five south bays; corner bay, four narrow bays and paired-arch end bay on the east), rusticated sandstone corner and end piers, brick pilasters and carved capitals, window types per floor (arched three-light top floor, transomed windows below, paired windows in the corner bays, narrow sashes on the east), sill and lintel bands, lettered frieze, modillion cornice and dentils, pediment (shell, crest, pedestals), shopfronts (bulkheads, glass, transoms, recessed doors, signboards, shop cornice), roof (parapet coping, chimney, penthouse, skylights), steam clock, bollards and chains, globe lamps, paving (brick sidewalks, setts, asphalt), neighbours, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/gastown/v003/review/independent-review.md. Do not run the build.

## Context for this review (v003)

v003 is v002 with targeted fixes for the v002 review's P1s (v002 scored 0 P0 / 3 P1; v001 0 / 5):
- P1 #1, black recess floors: the door thresholds' top faces shared the plane z = G0 with the cut and shop floors.
  Thresholds now stand 15 mm proud, every shop cut has a stone floor liner 5 mm above the cut floor from the wall face
  to the glass line, and the east side-door step stands 12 mm above the hall floor. Look at storefronts, front_corner,
  steam_clock and right_side: recess floors should read as lit stone, never 0 luminance.
- P1 #2, buried north-wall windows: the north face runs along -x (u = -x), so the v002 holes landed inside the north
  block. The windows now sit at x -9.6 and -11.2 on the exposed wall west of the north block (second and third floors).
  rear_north is re-aimed (level, 24 mm) to show that wall from grade to coping. Check rear and rear_north.
- P1 #3, the missing locked front source, was a pipeline pruning error, not the model; the build now copies all three
  locked sources.
- P2 #6: a meeting stile closes the light slit between the double-door leaves.
Nothing else changed. Score against v002 (0 / 3) and v001 (0 / 5), and confirm the v001 fixes still hold.
