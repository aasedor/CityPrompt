# Independent holistic review: clay-exoskeleton-research-lab v005 (RLASM v6.1)

Reviewer: independent, adversarial. I judged only rendered pixels against the locked source pixels: `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders and the 4 phone boards at full resolution. I made zoomed crops only in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-v005-crops-7f3a/`. I ignored the builder's notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** v005 fixes most of the v004 joint, glazing, stack and bay-count defects. The match is still not production quality: the roof plant is a blank box on a curb, the cantilever is about half the source depth, the south-front pilotis rhythm and SE corner do not match the source, and the coloured services read as a uniform plaid instead of the source's clustered ductwork.

Counts: P0 = 0, P1 = 4, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | aerial, front_corner, top, roof_screen, stacks, rear_side | **The roof plant is still under-modelled.** Inside the screen, the "penthouse" is one large plain white box with six small hatches. It fills almost the whole enclosure. The "duct loop" reads as a flat curb or plinth ring hugging the box at a constant offset: a light rectangle in top, a step in aerial and front_corner. There are no AHU boxes, fan units or duct runs with bends, and none of the stack clusters stand on plant. The source oblique and top show a busy plant ring: big AHU boxes (W, N, S), a box with a door on the E, ducts with elbows round the penthouse, and stacks rising out of fan or AHU units. Penthouse size, wider south walkway and the fourth (west) cluster are fixed. | Duct loop built as a closed extruded rectangle at a constant offset with no breaks or elbows. No AHU or fan primitives placed. Penthouse footprint grown into the ring. | Cut the penthouse back to roughly the source's plan proportion (top.jpg: about 0.70 x 0.53 of the screen box) so a readable plant ring remains. Break the loop into round or rectangular duct runs with elbows and risers on the W, S and E sides, as in top.jpg. Add 3 to 4 AHU boxes (W pair, N row, S unit under the S stacks, E unit) that rise to about screen height or above. Seat each 3-stack cluster on a fan or AHU base. |
| 2 | P1 | front, front_corner, rear, cantilever | **The cantilever is under-scaled.** In the front render the west overhang is about 16% of the south-face width (box x 390 to 1000, ground-floor wall starts at about x 485). In rear (near-orthographic) it is about 23% (135/590 px). The source front shows about 32% (glass box x 110 to 700, soffit meets the base at about x 300). The source oblique shows about 30%. Both are foreshortened, so the real source overhang is larger still. In the front view the angled soffit reads as a small wedge instead of the source's dramatic dark underside. | West ground-floor wall or plinth placed too far west, or the box length kept while the base was lengthened. | Move the ground-floor west wall east so the overhang is about 33 to 38% of the south-face length. Re-derive the angled soffit between the slab-band underside and the new wall line. Keep the soffit bedded into the first-floor slab as now. |
| 3 | P1 | front, front_corner, architecture_close, v_pilotis | **The south-front ground-floor rhythm is off and there is an extra framed corner bay.** Render, west to east: V, portal, V, two more glazed bays, then a full-height white column at about x 915 (front). That column frames a separate narrow glazed corner bay up to the SE corner. In the source (front, oblique) the order is V, portal, V. The right V's east leg lands at the SE corner exoskeleton column, and the curtain-wall glass runs uninterrupted to that corner column. The source has no intermediate full-height column and no framed glazed return bay on the south face. | The exoskeleton "corner wrap" was read as a one-bay return onto the south face. The pilotis were then spaced on the shortened glazed span. | Delete the intermediate south-face column and return frame, and run the curtain wall to the SE corner column. Respace the V-pilotis so the east V's outer leg meets the slab next to the SE corner column and the west V sits at about 45% of the south face from the corner, with the portal between them. Let the corner wrap read only through the roof and slab-edge band and the corner column. |
| 4 | P1 | front, facade_close, glass_close, front_corner, left_side | **The coloured services read as a uniform plaid, not the source's clustered ductwork.** Flat rectangular blue and green bars repeat across every bay of every floor, including the cantilevered west bays. Vertical blue, green and yellow drops run at regular intervals. A continuous green bar runs across the whole facade at about 65 to 70% of each storey's height, so each storey again reads as split by a horizontal line (the v004 transom complaint, now in colour). In the source the coloured ducts are round, run near the ceiling with elbows and drops, and cluster in the central and east bays (front x 430 to 690, oblique x 510 to 640). The west and cantilever bays read as clear glass with white lab interiors and ceiling lights. | Services generated as a parametric grid over the full floor plate, not a placed cluster. Rectangular section. A lower duct tier at bench-top height. | Drop the bench-height green run. Keep ducts in the upper 30% of each storey with vertical drops. Concentrate the coloured runs in the central and east bays and leave the west and cantilever third mostly clear (white benches and ceiling only). Use round sections, or at least chamfered ones, with a few elbows. |
| 5 | P2 | front, right_side, roof_screen, stacks | Stacks now rise about 1.0 to 1.3 times the screen height above the screen top. The source shows about 0.4 to 0.6 times. In the front view the two clusters sit centre-right and far east; the source front has them centre-left and right. | Overshoot of the v004 fix (7.5 m). | Lower the stacks to about 5.5 to 6 m. In the front view, nudge the south/NW cluster west. |
| 6 | P2 | roof_screen, stacks, front, right_side | The screen reads as solid white panels with a sparse grid of small square holes. The source has a dense round or hex perforation that reads as a semi-open mesh. | Low open-area perforation pattern. | Use a denser round perforation (about 40% open) so plant shows through at aerial distance. |
| 7 | P2 | front, right_side, architecture_close | The east exoskeleton has louvre and white infill on only the 3 lab tiers, above a full-storey blank concrete base with shutters. The source front shows a 4th, lower tier of louvre or diagonal infill over the service bays in bays 2 to 4, with diagonals crossing the louvre bays, above a lower concrete plinth. | Infill tied to lab-floor levels only. | Add the lower partial tier (louvres in bays 2 to 3, diagonals in bays 2 to 4) above shutter-head height. |
| 8 | P2 | aerial, front_corner, stacks | At aerial scale, long soft stack and screen shadows across the large blank penthouse roof read as an undulating, draped surface. | Large untextured flat plane with soft area-light shadows. | Breaks once finding 1 adds plant. Otherwise add roof-panel joints or a lower key-light softness. |
| 9 | P2 | top, aerial, front_corner | The south and east street slabs do not meet. A plinth gap separates them, so there is no corner intersection; top.jpg shows the two streets meeting at the SE corner. | Context slabs placed independently. | Extend the east street to meet the south street with a kerb radius. |
| 10 | P2 | top | The top view is low-contrast and hazy, so roof detail reads faintly. | Exposure or ambient on the nadir camera. | Raise contrast or sun strength for the top camera. |
| 11 | P2 | v_pilotis | A soft elliptical highlight floats on the lobby glass. | Interior light reflection. | Lower the interior lamp or the glass specularity. |
| 12 | P2 | v_pilotis, front | The V-pilotis carry boxy capital blocks under the soffit. The source pins them straight to the slab with a small plate. | Cap primitive oversized. | Shrink the caps to thin plates. |
| 13 | P2 | aerial, left_side, right_side | The building fills only about a third of the frame, which limits detail reading. Every target is still legible, so this is not a camera defect. | Framing distance. | Tighten the framing by about 20%. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette / footprint (plan ratio about 1.22, streets S and E) | conforms (plan ratio 1.21 vs 1.23); street corner gap is P2 | top vs top.jpg, front vs front.png |
| Storey count (ground + 3 lab floors + roof plant) | conforms | front, left_side, rear, right_side |
| Curtain wall and slab bands (one pane per storey, thin bands) | conforms: transoms gone, bands about 7% of storey height, clean crossings (the green bar in finding 4 visually re-splits the storeys) | facade_close, glass_close, front |
| Coloured services behind glass | deviates (P1 #4): present, but wrong distribution, section and height | front, facade_close, glass_close vs front.png and oblique.jpg |
| Cantilever and angled soffit | deviates (P1 #2): soffit form and contact are correct, overhang depth about half | front, rear, cantilever vs front.png |
| V-pilotis and recessed glazed ground floor | deviates (P1 #3): two Vs, portal and recessed glazing present, rhythm shifted west, extra corner bay | front, v_pilotis, front_corner vs front.png and oblique.jpg |
| Concrete base walls (west end, service bays) | conforms (west wall under cantilever, east service bays with shutters) | cantilever, left_side, right_side, rear |
| Exoskeleton: columns and floor beams | conforms | right_side, architecture_close, exoskeleton |
| Exoskeleton: alternating diagonals | conforms in the end bays (direction alternates by tier); missing from louvre bays and the lower tier (P2 #7) | right_side |
| Exoskeleton: louvre and white infill (4 bays, 2 louvre) | conforms (4 bays, white braced end bays, 2 louvre bays, blades with depth) | right_side, exoskeleton, front |
| Exoskeleton: corner wrap | deviates: rendered as an extra framed south bay (P1 #3) | front, front_corner |
| Roof: pale edge walkway | conforms (wide south walkway, narrow W, N and E) | top, aerial |
| Roof: perforated screen | conforms in form, posts and caps; perforation density is P2 #6 | roof_screen, stacks |
| Roof: penthouse | deviates (P1 #1): oversized blank box | aerial, top, roof_screen |
| Roof: ducts and units | deviates (P1 #1): loop reads as a curb, no AHUs or fans | top, aerial, stacks |
| Roof: stacks (4 clusters of 3) | conforms in count and plan positions (N, W, E, S); height overshoot P2 #5 | top, right_side, left_side, stacks |
| Materials hierarchy (white steel, clear glass, grey louvres, pale concrete, pale roof) | conforms for clay | all |

## 4. Camera validity

No view has an occluded target, a clipped asset or an illegible subject.
- **Top:** hazy and low-contrast (P2 #10), but the roof and plan are readable.
- **Aerial, left_side and right_side:** the building is small in frame (P2 #13), but legible.
- **Interior:** dark ceiling, but the benches and coloured ducts are legible.
- **v_pilotis:** the frame cuts the V feet and the slab above, which is intended for a detail.
- **No P0 defects:** I found no floating or intersecting parts. Stacks, V-pilotis, exoskeleton columns and trees all meet their supports.

## 5. Status of previous-version findings

| v004 finding | Resolved in pixels? | Evidence |
|---|---|---|
| P1 black hairline between the slab band and the angled soffit; dark block at the cantilever NW corner | **Resolved** | cantilever: continuous slab-band-to-soffit joint, no dark line. rear (NW corner zoom): clean tapering soffit end, no dark block. |
| P1 black squares at mullion/transom crossings; black caps on screen posts | **Resolved** | front and facade_close zooms: clean white crossings. roof_screen and stacks: posts stand proud with white rounded tops. |
| P1 mid-height transom per floor; heavy slab bands | **Resolved geometrically**, but the continuous bench-height green duct now re-reads as a horizontal split (folded into P1 #4) | facade_close, glass_close |
| P1 exhaust stacks barely clearing the screen and hidden in the front view | **Resolved** (now overshoots, P2 #5) | front: clusters clearly visible above the screen. right_side, left_side. |
| P1 roof plant under-scaled (penthouse, duct loop, missing west stack cluster, narrow south walkway) | **Partly resolved: NOT closed.** West cluster, wider south walkway and larger penthouse are present. The duct loop reads as a curb, AHUs and units are absent, and the penthouse is now oversized and blank (P1 #1). | top, aerial, roof_screen, stacks |
| P1 five exoskeleton bays with three louvre bays | **Resolved** (4 bays, 2 louvre, braced white end bays) | right_side, architecture_close, front |

Earlier resolved findings, checked for regression:
- **Cameras:** not regressed (section 4).
- **Lobby:** recessed glazed ground floor present; not regressed.
- **Portal:** white door frame between the Vs, no black joints; not regressed.
- **Services:** present, not regressed in presence. The distribution is a new P1 (#4).
- **Pilotis:** two white Vs; contact clean; rhythm is P1 #3.
- **Trees:** low-poly, seated; not regressed.
- **Screen perforations:** present (density P2); not regressed.
- **Louvre blades:** present with depth; not regressed.
- **Black joints at the portal and column tops:** none visible; not regressed.
