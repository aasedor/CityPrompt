# Independent holistic review: clay-vaulted-lecture-hall v002 (RLASM v6.1 architectural clay)

Reviewer: independent (not the builder). Before writing I opened at full resolution the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders and the 4 phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/lect-v002-indrev-crops-7f3a/`, a new folder; no candidate file was touched. I judged pixels only and did not use metadata, counts or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v002 fixes most v001 defects, but one P0 and four P1s remain. The P0 is that the four louvred roof masses still don't read as a large pinwheel in the governing top view. The P1s are the unsculpted white mass, the kinked and segmented end-arch rims, the short sparse fin return on the south face, and a blank vault soffit seen through the open ends.

Counts: P0 = 1, P1 = 4, P2 = 7

### Orientation check (done before judging)
The top source governs. Seen from above, the crown's north and south edges bow outward and its west and east edges are straight. That is the perspective signature of arch ends on the north and south faces, with the springing on the west and east sides. So the render's orientation is correct: arch ends face south and north, and the vault springs from the west and east parapets. Read the same way, the source oblique is taken from the south-east. Its left face is the south face, with the fin return over its western part, and its right face is the east face with the slots. The source front looks at the south face. So the render's `front`, `front_corner` and `aerial` cameras match the source roles.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| F1 | **P0** | top, aerial, front_corner, front, rear, rear_side, roof_masses, architecture_close | **Governing top view:** the vault covers about 95% of the roof width. The four louvred masses show only as four small tabs, each about 15% of the roof width, sticking a few percent past the N and S end arches. Two of them (NE and SW) are still parallel to the grid and only NW and SE are rotated, so the layout is a two-fold, point-symmetric pair arrangement rather than a four-fold pinwheel. **Source top:** four large masses, each about 25–30% of the roof, every one rotated the same way, each running from under the crown edge out to its roof corner, with louvred tops that dominate the plan. **Source front:** three dark louvred faces rise well above the parapet and break the silhouette. **Render front:** one small louvred square plus a plain white wedge. The masses are now chamfered, grounded on the deck, under the arch and carry flush louvre panels, so this is only partly resolved. | Masses are sized and placed to fit inside the vault-end zone, and only two of them were given a rotation. | Scale each mass to about 0.25–0.3 of roof width and 0.6–0.7 of vault rise. Rotate all four 20–30° in the same sense. Place one at each roof corner (NW, NE, SE, SW), running from under the crown edge out past the end arch or flank toward the parapet corner, with the louvred slope facing outward. Re-check the top view against the source top until all four read as a pinwheel. |
| F2 | P1 | front, front_corner, facade_close, rear_north, right_side, architecture_close | The white composite-panel mass is still one extruded rectangular box with flat faces and level horizontal panel joints. There are no faceted or tilted planes, and the soffit over the glazed base is flat. The slots now have real reveals (facade_close shows jamb and sill depth), but they are short rectangular punched openings. In the sources, the mass is cut into angled planes, a sloping soffit rises and falls over the Y-column base, and the slots are long carved scoops with sloping sills that run around the faceted planes. The builder states that the faceting and soffit were not attempted. | Not built (acknowledged). | Split the mass into 3–5 planar facets: tilt the upper south and east bands about 5–10° outward, and step the parapet line where the masses rise. Slope the soffit from the SW fin corner up to a peak near the central Y-column and down toward the SE. Lengthen the two south and east slots into tapered recessed bands, about 1/3 of the facade width, with angled returns and sloping sills. |
| F3 | P1 | front (zoomed), rear, vault_ribs, architecture_close, roof_masses, front_corner | The end-arch rim is built from discrete straight box segments. At each end, where the crown arc meets the flank arc, the rim visibly kinks, and black triangular holes open in the rim: in architecture_close at about (300,405) and (1290,400), in front at about (395,280) and (1015,380), and in rear on the east foot. vault_ribs shows an S-shaped inflection at the left foot. Dark hairline seams show between segments in roof_masses. The rim is also about 2–3× deeper than the slender source rib (about 5% of span against about 1.7%), so it reads as a heavy band. | The rim is assembled from two arcs that are not tangent to each other, and from separate unbevelled blocks. | Sweep each end rim as one continuous profile along a single tangent-continuous semi-ellipse, or weld and bevel the segments so no gaps or seams remain. Cut the rim depth to about 40% of its current depth. Re-render front, rear and architecture_close and confirm no dark pixels on the rim. |
| F4 | P1 | front, front_corner, aerial, top | Fin-screen return on the south face. The render has 8 widely spaced bars (gap about 4× fin width) covering about 20% of the south face, with flat tops at the parapet, and a tall plain white end slab at the corner. The west face itself is correct and dense (left_side, fin_screen). In the source front and oblique, the dense fin rhythm continues around the SW corner across roughly half the south face, and the fin tops rise following the arch rim. | The return was modelled as a short separate group with a different pitch. | Carry the west-face fin pitch around the SW corner. Extend the south return to about 45–55% of the south face length. Let fin tops step up to sit just under the end-arch rim. Remove or narrow the plain corner slab so the corner is formed by fins. |
| F5 | P1 | front, rear, rear_north, facade_close, front_corner | Through the open vault ends, the crown's underside is one smooth uniform grey shell with no rib grid, cushion seams or translucency. In the hero front view it is the largest single area and reads as an empty void. In the source front, the crown seen through the open end shows the rib grid and cushion pattern. | Cushions and rib grid are modelled only on the outer surface, and the inner surface is a plain single-sided shell. | Give the crown underside its rib grid: extrude the ribs on the soffit, or make the cushion layer double-sided with the rib grid visible from below. Use a slightly translucent white for the membrane. Check front and rear for visible grid lines under the crown. |
| P2-a | P2 | fin_screen, left_side | Fins are straight identical bars in the same white as the mass. The source shows bowed, sculpted aluminium fins in a slightly darker silver-grey. | Simplified profile and material. | Add a slight bow or twist, and a cool grey aluminium tone one step darker than the mass. |
| P2-b | P2 | front (zoomed) | The top fin rail runs past the last fin on the south return with a short free end. | Rail length. | Trim the rail to the last fin or return it into the mass. |
| P2-c | P2 | rear_side, roof_masses | A mass's sloping apex grazes the end-arch rim (near-tangent clash). | Mass placement. | Give 0.3–0.5 m clearance, or pass the mass cleanly under the rim. |
| P2-d | P2 | rear, front | Vault rise to span is about 0.39, against an apparent 0.30–0.35 in the source, so it is slightly tall. | Ellipse ratio. | Flatten the rise by about 10–15%. |
| P2-e | P2 | entrance_steps, front, top | The steps are present but low-contrast. Planting is small boxes, where the source has long beds along the south front. | Minimal landscape. | Make the beds longer and continuous along the south front and add a slight tone step on the risers. |
| P2-f | P2 | y_columns, entrance_steps | A foreground tree canopy covers about 1/3 of the y_columns frame, and a tree trunk sits in the middle of entrance_steps. Both views stay legible. | Camera placement. | Move or hide the foreground trees for these two detail cameras. |
| P2-g | P2 | aerial vs front_corner | Both are taken from the same SE quadrant, with the building in about 25% of the frame, so they nearly duplicate each other. | Camera set. | Tighten framing, and move the aerial camera higher and closer to the source-oblique height. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | **deviates.** The overall block, vault and base are right, but the louvred masses don't break the parapet line as in the source front (F1), the mass has no facets (F2), and the rim is heavy and kinked (F3). | front, front_corner, rear |
| Storey count | **conforms.** Double-height glazed base, a three-storey white mass with slots on two levels, then the vault. | front, glass_close, facade_close |
| Vault span | **conforms.** Springs from the west and east outer parapet edges, with arch ends on N and S. | top, rear, left_side |
| Vault rise | **conforms (P2).** Semi-elliptic, about 0.39, slightly taller than the source. | rear, front |
| Vault ribs | **deviates.** Rib grid and rib feet on the springing blocks are correct. The end rims are segmented, kinked, notched and over-deep (F3). | architecture_close, vault_ribs, roof_masses |
| Cushions | **conforms.** Pillowed cushions on the rib grid across about 65% of the crown width and the full length. | roof_masses, top, rear_side |
| Glazed flanks | **conforms.** Clear lower flanks with ribs, down to the parapet. | roof_masses, left_side, right_side |
| Vault ends | **conforms on topology (open), deviates on soffit.** The underside seen through the ends is blank (F5). | front, rear, rear_north |
| White mass and slot windows | **deviates.** Plain box with no facets and no sloping soffit. Slots have depth but are short punched rectangles (F2). | front, facade_close, architecture_close |
| Fin screen | **west face conforms. SW return deviates.** The return is short and sparse (F4). | left_side, fin_screen, front |
| Y-columns and glazed base | **conforms.** Glazing is recessed behind the Y-columns, collars close the nodes, the arms meet the soffit, and the base is double-height. | glass_close, y_columns, front, interior |
| Louvred masses | **deviates (P0).** Present, angular, grounded, with flush framed louvre panels, but undersized, only half rotated, and hidden in plan (F1). | top, front, rear, roof_masses, architecture_close |
| Steps and planting | **conforms (P2).** Wide shallow steps along the south front, with small planters. | entrance_steps, front, top |
| Materials hierarchy | **mostly conforms.** White mass and ribs, light blue-grey glass and dark grey louvres are correct. The fins are not differentiated as aluminium (P2-a). | front, fin_screen, architecture_close |
| North face (no source) | **coherent.** Plain mass with one slot and a glazed base, in the same grammar. | rear, rear_north |
| East face (no source) | **coherent.** Two slots and a Y-column base. | right_side, front_corner |

## 4. Camera validity

- All 18 views are valid. No target is occluded so badly that it is illegible, no asset is clipped, and none is black.
- **front**: valid and role-matched to the source front (south face, arch end, fin return on the left).
- **front_corner / aerial**: valid and role-matched to the source oblique (SE quadrant: south and east faces). The building fills only about 25% of the frame, and the two views nearly duplicate each other (P2-g).
- **top**: valid nadir view, role-matched to the source top.
- **interior**: valid, now lit and legible (it was black in v001).
- **y_columns / entrance_steps**: legible, but foreground trees occlude part of each (P2-f).
- **rear_north / facade_close**: valid. They show the blank soffit through the open end (F5).

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | v002 status | Evidence |
|---|---|---|
| P0 interior view black | **Resolved** | The interior shows a lit double-height lobby, glazing, Y-columns and fins outside. |
| P0 louvred masses were small orthogonal boxes in mirrored pairs outside the vault ends, not a rotated pinwheel of large angular masses under the arch | **Partly resolved, still P0 (F1)** | They are now chamfered and angular, sit under or astride the open ends, and carry flush louvre panels. Only 2 of 4 are rotated, they are undersized, the layout is still two N/S pairs, and the pinwheel can't be read in the top view. |
| P1 louvred faces read as staircases | **Resolved** | architecture_close and vault_ribs show flush framed panels with light blade lines. |
| P1 vault was a full semicircle with closed flat glass ends | **Resolved** | Semi-elliptic (rise to span about 0.39), springing from the parapet edges, open ends (front, rear). New rim defects are logged separately as F3. |
| P1 crown cushions were flat pads in a narrow band | **Resolved** | Pillowed cushions on the rib grid over about 65% of the crown width (roof_masses, top). |
| P1 white mass was a plain box without faceted planes, sloping soffit or deep carved slots | **Partly resolved, still P1 (F2)** | Slot reveals now have depth (facade_close). No faceting and no sloping soffit. |
| P1 glazed ground floor too squat | **Resolved** | Double-height glazing with a transom, about 25% of the elevation height against about 30% in the source (front, glass_close). |
| P1 black holes at the Y-column nodes | **Resolved** | Node collars, and no dark pixels at the nodes (y_columns, glass_close). |
| P1 fin-screen return stopped in mid-air at the SW corner | **Resolved for contact** | Fins stand on the podium, and rails tie to the corner post (front, zoomed). There is a small rail overrun (P2-b). The return is too short and sparse, logged as new F4. |
| P1 gap at the east end-rib foot; end glazing floating above the deck | **Resolved** | Rib feet sit on the springing blocks on the parapet (architecture_close, rear east foot, rear_side). The ends are open, so there is no floating end glazing. |
