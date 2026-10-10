# Independent RLASM v6.1 holistic review — clay-arched-mill-mixed-use v002

Reviewer: independent (did not build). Judged only rendered pixels against the three locked sources
(`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). Builder notes, counts, hashes and
`build-report.json` were not used as evidence. All 18 renders, the three sources and the four phone boards
were opened at full resolution; zoomed crops were made in a separate scratch folder for bay counting.

Orientation used throughout (from `top.jpg`, north up, streets at left and bottom = west and south): the
eaves face carrying the pavilion is the west street face; the raked-gable face on the other street is the
south face; the chimney stands on the east (rear) eave in the southern third of the plan; the north gable
and the east face are not shown by any source.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the two v001 P0s (mirrored plan, chimney at the wrong end) are genuinely
fixed in the pixels, but the west street face still carries six bays where both locked ground views show
four, which stretches the whole envelope into a 1.44:1 bar that neither source shows, and the pavilion was
over-lengthened to suit it.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|----------|---------|--------------------------------|--------------|------------|
| 1 | **P0** | left_side, front_corner, aerial, top vs front.png, oblique.jpg, top.jpg | Render west (pavilion) face has **6** window bays and **6** shopfront arches per storey (left_side: windows at x≈390/520/650/780/915/1045). Locked `oblique.jpg` west face has **4** upper-window columns (src x≈293/363/440/527) and **4** shopfront arches (x≈290–580) before the corner pier at x≈610; locked `front.png` west face also has **4** (x≈195/257/330/422, building end at x≈145). The south gable face is 4 bays in both sources and 4 in the render, so the plan is near-square in the sources (top.jpg roof footprint ≈500–600 px E-W × ≈450–490 px N-S) but 1.44:1 (625×435 px) in `top.png`. v001's "seven bays" P1 was reduced to six, not to the source count, and the resulting elongation is an envelope defect, not just rhythm. | Family parameter for the eaves-face bay count still set from the builder's reading of the oblique rather than the counted columns; plan depth derived from bay count. | Set the west/east eaves faces to 4 bays with the same bay module as the south gable (plan ≈ square, ridge length ≈ gable width); rebuild shopfront arcade, upper panels, pilasters, cornice dentil count, roof length, rooflight spacing and chimney station from that. Re-render left_side, front_corner, aerial, top. |
| 2 | **P1** | roof_pavilion, left_side, top, aerial vs oblique.jpg, top.jpg | Pavilion glazing runs ≈86–90 % of the ridge (top.png y≈255–815 of 225–850; left_side x≈370–1080 of 320–1120) with only a thin west terrace strip and no end terraces. In `top.jpg` the glazed box is y≈230–600 of a 185–690 roof (≈73 %), leaving ≈9 % of railed terrace deck beyond its north end and ≈18 % of open slate before the south gable; `oblique.jpg` shows that railed deck at the north end (x≈240–330) and the slate run-out before the gable. v001's "too short" was over-corrected into "too long"; height is now acceptable (≈1 storey, matches front.png ≈1.0–1.15 storey). | Pavilion length tied to the (wrong) 6-bay ridge and set to near-full length. | On the corrected 4-bay ridge, run the glazing over ≈3 bays starting ≈0.35 bay south of the north parapet and stopping ≈0.7 bay short of the south gable; add the railed terrace deck across the north end and the small triangular railed deck at the pavilion's SW corner (top.jpg y≈600–650). |
| 3 | P2 | chimney_contact, right_side, top | Chimney base sits on the east slope ≈1 m inboard of the eave with slate between stack and parapet. Sources show the stack rising flush with the rear wall line (top.jpg base straddles the east eave at x≈930–960; oblique.jpg stack rises from the rear parapet). | Stack placed on roof surface, not on wall line. | Move stack to the east wall plane so it rises from the parapet. |
| 4 | P2 | rear, rear_side | North gable has a blank pilastered bay at its east end plus 3 window bays, while the chimney is not on this face. Not source-visible; mildly incoherent with the 4-bay gable grammar. | Blank flue bay placed on the wrong gable. | Make the north gable 4 bays like the south, or justify the blank bay by moving it to the south gable's east end (see 7). |
| 5 | P2 | rear_yard, right_side | Rear door is now a framed leaf with a shallow dark reveal and projecting threshold (reveal width matches the adjacent window reveals), but the leaf is a featureless flat plate. v001 "flat plate" P1 is reduced to polish. | Door leaf is a single quad. | Add a 50–80 mm leaf recess inside the frame and a simple rail/panel split. |
| 6 | P2 | roof_pavilion, aerial, top | Pavilion roof is a flat light-grey slab with a white frame. Source pavilion has a shallow mono-pitch standing-seam metal roof rising toward the main ridge (oblique.jpg seams run E-W). | Simplified roof slab. | Give the pavilion roof a shallow pitch with its ridge-side edge higher and a few seam lines. |
| 7 | P2 | front vs front.png, oblique.jpg | Source south gable has a narrow blank end bay at its east (rear) end with a small door (front.png x≈865–895); render gable is 4 equal window bays to the corner. | Bay layout simplified. | Add the narrow blank end bay with door at the east end of the south gable. |
| 8 | P2 | facade_close, arched_windows, glass_close | Window and shopfront glazing split into 2 lights only; source frames are dense multi-pane grids (≈4×6). Acceptable for clay; noted as polish. | Simplified mullions. | Add a 3×4 glazing-bar grid to upper windows and shopfront transom line. |
| 9 | P2 | chimney_contact (x≈265,y≈1000), left_side (x≈318,y≈485 and y≈755), right_side (x≈340,y≈485 and y≈750) | Small black gaps where the horizontal cornice band and the first-floor sill band meet the raked gable parapet returns. | Band end caps stop short of the gable coping. | Extend band ends into the parapet or add return caps. |

P0 = 1, P1 = 1, P2 = 7.

### v001 defects, verified in the pixels
- **Plan mirrored at the street corner (v001 P0): resolved.** `front_corner.png` seen from the street corner shows the 6-bay eaves face on the left with the pavilion on the near slope and the gable face on the right with the chimney beyond it — the same handedness as `front.png` and `oblique.jpg`. `top.png` matches `top.jpg`: pavilion on the west slope, rooflights on the east slope, chimney on the east eave.
- **Chimney at the wrong end (v001 P0): resolved.** `top.png` chimney at y≈630–680 of 225–850 (southern third, east eave); `top.jpg` base ≈0.55–0.75 of the way from the north on the east eave; `left_side.png` shows the stack at the south (gable-street) end behind the ridge, as in `front.png`.
- **Seven bays on the long face (v001 P1): not resolved** — now six, sources show four (finding 1, escalated because it also sets the envelope).
- **Pavilion too short and low (v001 P1): height resolved, length over-corrected** (finding 2).
- **Rear door a flat plate (v001 P1): reduced to P2** (finding 5).

## 3. Source conformance checklist

| Item | Status | Evidence (view used) |
|------|--------|----------------------|
| Silhouette (gabled block, pavilion on one slope, tall stack at rear) | **deviates** | aerial vs oblique.jpg: elements and handedness match, but the block is a 1.44:1 bar instead of the near-square footprint of top.jpg; see finding 1. |
| Storey count (ground + 3 upper) | conforms | front, left_side vs front.png / oblique.jpg: 4 storeys, top storey directly under the cornice. |
| Bay rhythm and pilasters | **deviates** | South gable 4 bays conforms (front vs front.png). West face 6 bays vs 4 in both ground sources (left_side vs oblique.jpg crop). Full-height proud pilasters with recessed panels conform (facade_close). |
| Arched openings (segmental shopfronts, segmental upper windows, depth/returns) | conforms | shopfront, glass_close, arched_windows, corner_entry: segmental heads, dark frames set back with visible jamb returns and projecting sills. Glazing-bar grid simplified (P2). |
| Cornice and band (dentil course under parapet, stone sill band over ground floor) | conforms | architecture_close, corner_entry: dentils under the coping, continuous band wrapping the corner. Band end-gaps at gable returns are P2. |
| Roof and gables (slate pitch, ridge on long axis, raked parapets on short faces) | conforms (geometry) / deviates (length) | front, rear, top: ridge N-S, raked coped parapets on N and S, pitch ≈23° vs ≈26° estimated from front.png — acceptable; roof length wrong by finding 1. |
| Pavilion and chimney | **deviates** | roof_pavilion, top: pavilion present, glazed, railed, ≈1 storey high, on the west slope (conforms) but ≈90 % of ridge with no end terraces (P1). Chimney: tall square stack with corbelled cap on the east eave in the southern third (conforms), inboard of the wall line (P2). |
| Materials hierarchy (brick body, stone bands/sills/copings, dark frames, slate roof, glazed pavilion) | conforms | front_corner, facade_close: brick-tone body, pale stone bands, sills and copings, dark grey frames, grey slate, glazed pavilion with pale frame. Clay palette only, as required. |
| North face and east face | not visible | rear, rear_side, right_side: no source; judged for coherence only (findings 4, 5). |

## 4. Camera validity

All 18 renders are valid: the target is in frame, unclipped and legible in each.

- `front.png` is an elevation of the south gable face, not of the principal west (pavilion) face that
  dominates the locked front photo; the board therefore pairs a corner perspective with an orthographic
  gable elevation. It is a usable view but a weak role match — `front_corner.png` is the true match for
  `front.png` and was used for that comparison. Recommend adding a west elevation or renaming.
- `interior.png` shows a bare brown room with one arched window and a white block; legible, shows the
  window reveal from inside, no architecture beyond that.
- `chimney_contact.png` is the only view that exposes the P2 band-end gap at the north gable return.
- Phone boards 01–04: all tiles legible at 1080×1920; board 03 has an empty tile slot (layout only).
