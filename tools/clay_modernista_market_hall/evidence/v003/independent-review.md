# Independent holistic review: clay-modernista-market-hall v003 (RLASM v6.1)

Reviewer: independent, no relationship with the builder. Evidence used: only the rendered pixels in `renders/` (all 18 opened at full resolution, with zoomed crops of the lantern crossing, the gablets, the aerial roofscape and the interior ceiling), the four phone boards, and the three locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I did not use the builder's notes, metadata, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v002 P0 truss fault, the monitor and ridge-seam fault and the quadrant geometry are fixed in the pixels. Three P1 defects remain:
- the interior still shows an opaque ceiling with no glazed lantern well;
- the lantern-to-roof junction has a floating corner post over a glowing white patch and a blank translucent triangle;
- the quadrant stained glass reads as giant primary-colour poster triangles, not the sources' leaded pane grid.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | interior (and int-top crop), compare lantern_roofs / aerial | Looking up from the hall, the ceiling over the nave is a matte brown hipped soffit with a flat brown panel at its crown. No lantern clerestory glazing, no glass pyramid and no wing skylight strips are visible from inside, and no trusses appear under the near nave roof (trusses show only over the aisles and at the far gable). From outside, the lantern is all glass and every wing slope has two glazed strips showing trusses beneath. The inside and outside contradict each other. The v002 "opaque ceiling, lantern well unlit" finding is only half fixed: the ceiling is lighter, but it is still closed. | An opaque interior liner or ceiling mesh (or a single-sided, backface-opaque roof shell) is still under the wing roofs and the lantern. The extra lighting brightened it but did not open it. | Remove or hole-cut the interior ceiling liner under the lantern square and under each skylight strip. Make the lantern pyramid and clerestory glazing render as glass from inside as well. Expose the pitch-following hall trusses under the nave. Re-render the interior with the camera pitched up enough to show the lantern well. |
| 2 | P1 | lantern_roofs, front_corner, aerial, rear_side, crest_contact | At each re-entrant corner of the cross, the lantern's black corner post stops in mid-air on a bright, over-exposed white parallelogram. Below it, a blank grey translucent triangle with no mullions fills the gap down to the wing-roof valley (crop `lr_cross`). In crest_contact the same blank grey wall with a floating white patch fills the area under the lantern clerestory. The lantern does not land on a curb or the roofs at its corners. | The lantern box sits above the crossing, and its corners fall over the wing valleys. A plain glass skirt was extruded down to the valley without a corner post, sill or mullions. An interior light emitter or lit floor plate under the lantern shows through and blows out. | Give the lantern a proper sill or curb that sits on the four wing roofs, with the corner posts carried down to it. Close each corner with valley flashing or a stepped base instead of the blank skirt (or carry the mullion grid down). Hide the light emitter or lower its intensity so no white patch shows through the glass. |
| 3 | P1 | top, aerial, front_corner, rear_side, architecture_close, plaza_awnings | Each quadrant pyramid facet carries one or two huge flat triangles in saturated red, yellow, blue and green, forming an "X" or "A" graphic over the whole facet. The panes are not set in a glazing-bar grid, and their scale does not follow the bar rhythm. In matched roles, the top source shows small rectangular leaded panes, mostly muted teal, blue and green with a little amber, on the inner part of each facet, with opaque metal on the outer zones. The oblique source shows the same muted teal-green pane grid. The render reads as a painted flag or poster, not stained glass, and it is the most dominant colour in the roofscape. | Stained glass was modelled as a few large coloured triangle planes per facet, with primary awning colours used for glass, instead of a pane grid. | Subdivide each facet into a grid of panes (roughly 6–10 per row) aligned to the glazing bars. Use the source glass palette: teal, blue-green, muted blue and a little amber, with little or no red. Keep the outer facet zones opaque metal, as the top source shows. |
| 4 | P2 | top, lantern_roofs, front_corner | The lantern pyramid is all clear glass. Both the top and oblique sources show an opaque metal four-hip pyramid, with glazed monitors and stained gables around it. (The v002 review accepted the glazed lantern; noted here for the record.) | Lantern roof given the glass material | Make the pyramid skin metal and keep the glazed clerestory |
| 5 | P2 | top, aerial, lantern_roofs | Every wing slope has two long glazed skylight strips. In the top source, the wing roofs are opaque standing-seam metal, glazed only at the monitors next to the crossing. | Added skylight strips | Reduce or remove the strips; add standing-seam lines |
| 6 | P2 | facade_close, great_arch, crest_contact | The tympanum panes are rotated slabs scattered across the radial leading, overlapping bars instead of filling the cells. (The tympanum was accepted in v002.) | Panes placed independently of the leading | Clip the panes to the leading cells |
| 7 | P2 | crest_contact, great_arch | The crest is a spoked wheel on a post. The source shows a tall scrolled iron finial with rake cresting. | Simplified crest primitive | Replace with a tall finial silhouette |
| 8 | P2 | front, plaza_awnings | Only 2 gablets per quadrant face. The source front shows a dense run of about 9 gablets. | Low gablet count | Raise to 3–4 per face |
| 9 | P2 | front_corner, aerial vs oblique | No awnings on the gable-end bays beside the piers. The oblique source continues awnings past the gables. | Awning rule excludes gable bays | Add awnings to the outer pier bays |
| 10 | P2 | interior | The stalls are bare orange boxes with no produce massing | Clay simplification | Add simple produce mounds |
| 11 | P2 | left_side, right_side, rear | Quadrant pyramid pitch is about 35°, slightly flatter than the oblique source | Pitch parameter | Raise to about 40° |
| 12 | P2 | glass_close | A cast-iron column covers the centre of the frame, so little glazing frame detail is legible | Camera placed on a column line | Shift the camera half a bay |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (single storey, square pinwheel plan, central lantern highest) | conforms | front, left_side, top vs top/oblique |
| Roof pinwheel and lantern | conforms in massing. Deviates in the lantern roof material (glass, not metal; P2) and the lantern-to-roof junction (P1 #2) | top, aerial, lantern_roofs |
| Great arch: archivolt | conforms (dark archivolt with bosses) | great_arch, facade_close |
| Great arch: tympanum | conforms in identity; pane registration is P2 | great_arch |
| Great arch: crest and coat of arms | the coat of arms (red and yellow shield) conforms; the crest form deviates (P2) | crest_contact |
| Great arch: stone piers | conforms | great_arch, aisle_arcade |
| Aisle walls: tiled dado, cast-iron columns, glazing | conforms (terracotta dado with stone cap, columns with branching brackets, iron-framed glazing) | aisle_arcade, plaza_awnings |
| Awnings (red, yellow and blue over every bay) | conforms on the quadrant faces; deviates at the gable-end bays (P2) | plaza_awnings, architecture_close |
| Gablets and quadrant roofs | geometry conforms (steep-enough glazed pyramids with gablets on their eaves); stained glazing deviates (P1 #3) | architecture_close, top, aerial |
| Clerestories | conforms (glazed clerestory bands on the wing side walls above the quadrants; monitors at the crossing) | aerial, lantern_roofs |
| Entrance | conforms (glazed screen and doors between the south piers) | great_arch |
| Interior | deviates: stalls present, but the opaque ceiling hides the lantern well (P1 #1) | interior |
| Plaza | conforms (paved plaza with bollards, lamps and trees) | front_corner, plaza_awnings |
| Materials hierarchy | deviates: quadrant glass uses awning primaries (P1 #3); the lantern roof is glass rather than metal (P2) | top, aerial |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every target is legible.
- **front:** the building is small in frame, but the elevation, arch and piers are legible.
- **left_side, right_side and rear:** close to symmetric with one another, which is acceptable for coherence views.
- **glass_close:** half-blocked by a column (P2 #12), but still legible.
- **interior:** legible, but pitched so that the lantern well cannot be shown (see P1 #1).

## 5. Previous-version (v002) findings: resolved in the pixels?

| v002 finding | status in v003 pixels | evidence |
|---|---|---|
| **P0:** semicircular hall trusses pierce the pitched wing roofs and float above them | **Resolved.** No arch or truss shows above any roof plane in front, sides, rear, aerial, front_corner, rear_side or lantern_roofs. Trusses are seen only below the skylight glass and inside. | lantern_roofs, aerial, glass_close |
| **P1:** black monitor-end triangles and ridge seams | **Resolved.** Monitor ends are closed dark-grey trapezoid panels, not black voids, and each wing roof reads as one continuous piece with no ridge seam. | lantern_roofs, front_corner |
| **P1:** quadrant roofs are low hips with small skylights; the sources show steep glazed stained-glass pyramids | **Geometry resolved, finish not.** The quadrants now carry glazed pyramids with gablets. The stained glazing is rendered as giant primary-colour triangles rather than a leaded pane grid, so it is carried forward as new P1 #3. | top, architecture_close, aerial |
| **P1:** opaque dark interior ceiling with the lantern well unlit | **Not resolved.** The ceiling is lighter, but it is still an opaque brown soffit, and no lantern glazing or skylight strip is visible from inside (P1 #1). | interior |
