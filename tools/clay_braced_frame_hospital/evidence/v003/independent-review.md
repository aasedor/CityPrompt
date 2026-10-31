# Independent holistic review: hospital v003 (RLASM v6.1 architectural clay)

Reviewer: independent, no relationship with the builder. I compared the pixels of 18 renders, 4 phone boards and 3 locked sources (front.png, oblique.jpg, top.jpg). I made zoomed crops only in a new scratch folder (`irev_hosp_v003_crops`). I did not use any metadata or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: All three v002 findings are resolved in the pixels. One new P1 contact defect remains: hanger rods on the cable-hung entrance canopy end on the clinical signage panel, on the perforated screen face and mid-pane on the atrium glass, not on structure.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close, front (zoomed), front_corner | The upper ends of the entrance-canopy hanger rods land on non-structural surfaces. In architecture_close one rod ends exactly on the left end of the signage panel's white graphic bar (~x112,y815). A second rod ends on the perforated screen strip between the signage panel and the atrium edge post (~x252,y877). A third ends mid-pane on the atrium glass, about 40 px off the nearest diagrid member and not at a node (~x372,y857). In the front view the two western rods rise to the signage panel and the screen panel beside it, not to the atrium. None of them shows an anchor plate or clevis. In the source the rods fan down from atrium diagrid nodes and edge posts, with the eastern ones taken from the ward frame. | Rod top points were placed by fixed offsets or heights, not snapped to structural nodes after the atrium moved 3 m forward and the canopy was relocated. | Re-target every rod top to a diagrid node or atrium edge post at one or two node levels. The eastern rods can go to a ward column or ring-beam node. Add a small node or clevis block at each end. Re-render architecture_close, entrance_canopy, front and front_corner. |
| 2 | P2 | top, aerial, rear_side, roof_plant | Each vent stack and plant box casts three soft shadows. On the roofs this makes three-bladed "propeller" shapes that read like rooftop wind turbines in top and aerial. | Three shadow-casting lights in the rig. | Let only the key light cast shadows, or merge the fill lights into a single sun plus world light. |
| 3 | P2 | top, aerial, front_corner | A narrow near-black slot (RGB ~43–57, about 10 px wide in top) runs the full length of the atrium, between the clinical block's east parapet and the atrium roof's west frame. It reads as a gutter or reveal, not as a hole. | The atrium roof frame stops short of the clinical parapet, so the dark interior shows through. | Close it with a flashing or coping strip, or carry the roof glazing to the parapet face. |
| 4 | P2 | rear_north, braced_frame, right_side | Exoskeleton cells are near-square, one X per tier, and floor slabs and spandrels behind them fall about 1.5 floors per tier. Some slabs cross mid-X at the node (rear_north). In the front source the X cells are taller (about 2 floors each) and the ring beams sit on floor lines. | The X tier module and the floor-to-floor height were set independently. | Make the tier height a whole number of floors (2 floors per X is closest to the front source) so ring beams line up with slabs. |
| 5 | P2 | facade_close, front, left_side | The perforated screens carry sparse, regular square perforations drawn as flat mid-grey squares. Only a few patterns repeat, and the strip glazing behind is barely legible. The source shows dense, high-contrast dot-matrix fields that vary in density. | A low-density perforation mask. The holes are flat insets and do not show the backing. | Raise perforation density with a density gradient per panel, and let the dark strip glazing read through the holes. |
| 6 | P2 | front_corner, aerial, front | The atrium now reads as a projecting glass prism, but it is still shallower than front.png and oblique.jpg suggest. Its top rises to the plant-storey level, above the clinical parapet. In the source the atrium stops at or just below the clinical parapet. | Atrium height tied to the plant-storey top. | Lower the atrium top to the clinical parapet line. A deeper projection is optional, because the top source supports a shallow one. |
| 7 | P2 | front_corner, roof_canopy | The recessed plant storey is a single dark louvre band over its full height. The oblique source shows a pale upper band above the dark louvre band. | Simplified plant wall. | Split the plant wall into a dark louvre band at the bottom with a pale cladding band above. |
| 8 | P2 | brick_base, interior | Brick reads as horizontal siding: continuous bed lines with no head joints or bond. | Coursing-only normal or texture pattern. | Add a stretcher-bond head-joint pattern, or plain untextured brick colour. |
| 9 | P2 | front, interior | The front render is a distant straight south elevation, with the building filling about 50% of the frame. It is not the source's low south-west three-quarter view, so atrium depth and ward-tower dominance can't be judged in the front role. Interior is underexposed. | Camera preset. | Add or replace with a low south-west three-quarter camera matched to front.png. Raise interior exposure by about 1 stop. |

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Silhouette | conforms | front_corner vs oblique, front vs front | Three readable volumes: the clinical block with its raised roof canopy, a narrow glass atrium, and the taller braced ward block. |
| Storey counts | conforms | front, left_side, right_side, rear | Clinical: 2 brick storeys + 5 screened storeys + recessed plant storey + canopy. Ward: 2-storey brick base + 5 braced tiers (the module issue is P2 #4). |
| Plan (three volumes) | conforms (per brief) | top vs top | Clinical block at the south-west, with its west face beyond the ward bar's west end. Ward north bar runs the full width, with an east wing down to the south street. Atrium between them, opening south, with the canopy in front. Note: top.jpg itself shows open paving east of the atrium at the south-east. The render follows the brief's L reading, and front.png supports that. |
| Clinical: brick base, large windows | conforms | brick_base, front | Two storeys of large windows with sills. Reveals are shallow but visible. |
| Clinical: perforated screens | conforms (density P2) | facade_close, front | Present over all five upper storeys on the south, west and north faces. |
| Clinical: signage panel | conforms | front, architecture_close | Tall dark panel with pale-blue display insets at the east end of the south face, from the top of the screens to the top of the brick base. |
| Clinical: louvre band, recessed plant storey | conforms | roof_canopy, front_corner, rear | Set back from the parapet. The north wall is now louvred. |
| Clinical: raised roof canopy frame | conforms | roof_canopy, front_corner, left_side | Raised slab on a frame with posts landing on the roof ledge, over the western roof. Matches the top source's extent. |
| Ward: exoskeleton bays, columns | conforms | right_side, rear, rear_side | Free-standing columns stand off the curtain wall with visible depth. |
| Ward: X braces, node blocks | conforms | braced_frame, rear_north | Full-height X braces with a node at each crossing. |
| Ward: ring beams | conforms (alignment P2) | braced_frame, rear_north | |
| Ward: brick base at the street | conforms | right_side, rear, front | Brick base set behind the columns, which run to the ground. |
| Atrium: diagrid | conforms | architecture_close, glass_close, entrance_canopy | Members stop inside the edge posts and the two sets interpenetrate, with a node block at every crossing. |
| Atrium: roof | conforms | top, aerial | Glazed roof with transverse members, running north to the ward bar. Dark edge slot is P2 #3. |
| Atrium: projection and returns | conforms | front_corner, aerial, entrance_canopy | Stands forward of both street faces, with a glazed east return (front_corner, aerial) and a glazed west return (entrance_canopy). Has its own roof edge. |
| Entrance canopy: glass plate, posts | conforms | front_corner, entrance_canopy, top | Glass plate in front of the atrium, wider than the atrium, on slender front posts that touch the ground. |
| Entrance canopy: rods | deviates (P1 #1) | architecture_close, front | Rods are present, but several end on the signage panel, the screen face or mid-pane glass. |
| Roof plant | conforms | roof_plant, top, aerial | Plant boxes and vents on the ward bar and on the lower clinical roof east of the plant storey. Shadow artefact is P2 #2. |
| Materials hierarchy | conforms | all | Red-brick bases, pale screens, a dark signage and louvre accent, light steel, blue-grey glass. Clay palette is consistent with the sources. |
| West and north faces of the ward (not in front or oblique) | coherent | left_side, rear, rear_north | Same exoskeleton grammar and brick base. No new seams. |

## 4. Camera validity

- No view has an occluded target, a clipped asset or illegible content.
- front: valid but distant and frontal. It does not match the source camera (P2 #9).
- interior: legible but underexposed (P2 #9). It reads as a view north inside the atrium: the clinical brick and screens on the left, the ward glazing and brick on the right, the north bar ahead.
- facade_close, braced_frame and rear_north crop tight by design. Each one frames its target.
- top, aerial, front_corner, left_side, right_side, rear and rear_side each frame the whole envelope with margin.

## 5. Previous-version (v002) findings: resolution in the pixels

| v002 finding | v003 status | evidence |
|---|---|---|
| P1: atrium reads as a flush infill slot; the 0.8 m projection and returns are invisible at building scale | **Resolved** | front_corner and aerial show the atrium as its own glass prism. It has a visible roof edge and a glazed east return, and the ward's south face sits back from it. entrance_canopy shows a glazed west return with depth. The canopy now sits forward of the atrium face. Residual height and depth tuning is P2 #6. |
| P1: pure-black void at the open north end of the clinical plant storey west of the ward bar | **Resolved** | rear_side (zoomed) and rear show a louvred north wall in the slot between the plant storey and the ward bar. No black void remains. |
| P1: black full-height seam at the ward bar's north-west corner | **Resolved** | left_side, rear and rear_side (zoomed) show a continuous corner column and glazed end bay, with no dark seam. |
| P1: diagrid members overshoot the edge frames; the two diagonal sets read as separate grilles without nodes | **Resolved** | architecture_close, glass_close and entrance_canopy show diagonals ending on node blocks at the edge posts. The two sets cross in one plane, with a square node block at every intersection. |
