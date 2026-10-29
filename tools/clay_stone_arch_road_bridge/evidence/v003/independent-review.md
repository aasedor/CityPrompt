# Independent holistic review: clay stone arch road bridge, v003 (RLASM v6.1)

Reviewer: an independent reviewer, not the builder. I read only the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution and the four phone boards. For contact and depth I made zoomed crops into a new scratch folder (`stonebr-v003-indrev-crops-a13e0f54`). I did not use any metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: the pixels show a coherent three-arch cut-stone road bridge with a fourth land arch, cutwaters, a dentilled cornice, pedestalled balustrades and double-lantern lamps, spanning a river between quays in the source plan. All four v002 P1s are resolved, and no new defect rises above polish.

Counts: P0 = 0, P1 = 0, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | balustrade, architecture_close, glass_close, roadway_deck | Balusters are square, flat-faced profiles with notched tabs, not the turned vase balusters of the source. At close range they read as cut-outs. | Box-primitive baluster profile | Replace the baluster with a lathe (revolved) vase profile of 8–12 sides. Keep the spacing. |
| 2 | P2 | arch_spandrel, river_underside, rear_side | A grey quay-wall ledge still runs under the west arch springing, and the voussoir ring stops on grey wall instead of a sandstone springer. | Quay wall solid passes under the abutment face | Stop the quay wall at the abutment face, or add a sandstone springer/plinth course under the west springing. |
| 3 | P2 | top, aerial, rear | The river pier between the third river arch and the land arch has no cutwater. The source top shows a third cutwater on that pier. | Cutwater emitted only for mid-river piers | Add the same pointed cutwater to the east river pier (downstream face at least). |
| 4 | P2 | top vs source top | Plan proportion drift: the land arch is about 0.63 of a river span (source about 0.86), and the river is wider relative to bridge length (about 0.86 against 0.74). | Span and channel parameters | Widen the land arch span or narrow the river spans and channel toward the source ratios. |
| 5 | P2 | balustrade, roadway_deck | Streaky soft shadow smears on the footway and carriageway near the parapet. | Low-sample soft shadows/denoise on large flat planes | Raise the samples or the light size, or bake a uniform AO, for the deck planes. |
| 6 | P2 | front | The hero lamp's right lantern finial reaches pixel row 1 and touches the top edge. | Camera tilt/FOV marginally tight | Lower the camera aim 1–2° or widen the FOV slightly so the finial clears the frame. |
| 7 | P2 | facade_close, arch_spandrel, aerial | Context plots along the downstream quays are sparse. Through the arches the channel ends in bare sky above the quay walls, with no town beyond. | Few context blocks placed downstream | Add 2–4 simple blocks along each downstream quay, set back behind the quay road. |
| 8 | P2 | lamp_standard | White specks on the right edge of the right lantern's roof and base. | Sub-pixel gap or flipped normal at the lantern cap/base seams | Merge the cap and base vertices, or recalculate normals, on the lantern mesh. |
| 9 | P2 | left_side | Composition: about 40% of the frame is a blank grey quay wall. The bridge is cut by the right edge after the first river pier. The west end (abutment, quadrant, end lamp, arch, cutwater) is complete and legible, so this is not a camera failure. | Camera placed low and close along the west quay | Yaw 10–15° toward the bridge and pull back slightly, so the second arch enters the frame. |
| 10 | P2 | front vs source front | At the west quadrant the camera sees the inner face of the far half. The near half shows a bare broad rail top, and the smooth curved plinth bulges out behind the tangent pedestal. It reads as one barrier, but heavier and plainer than the source quadrant, which shows its balustered convex face. | Render camera sits further west and higher than the source viewpoint | Optionally move the front camera a little east and lower toward the source eye point. No geometry change is needed. |
| 11 | P2 | glass_close | Tiny dark notches where each volute tube meets the shaft collar. | Volute tube end caps intersect the collar face at an angle | Sink the volute start 1–2 cm deeper into the collar, or blend it with a small fillet. |
| 12 | P2 | left_side, rear_side (west), aerial (west) | The curved quay walls under the quadrants are smooth grey, without the coursing lines of the straight quay walls next to them. | Coursing material applied only to straight wall segments | Apply the same coursed quay material and UVs to the curved quay segments. |
| 13 | P2 | architecture_close, front | The quadrant rail top close to the camera reads wide compared with the bridge balustrade rail. | Rail width differs between the quadrant and the main balustrade | Match the quadrant rail section to the bridge balustrade rail. |

There are no P0 or P1 findings. On the v002 P2 "saw-tooth tabs under the quadrant plinth": I could not see separate tabs at review resolution in front, front_corner, aerial or rear_side. I have not counted it as a finding.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan and proportions | conforms (with the P2 drift noted in #4) | top vs source top, aerial. Four spans (three river spans plus an east land arch over the low quay road). Narrower upstream channel with a curved north-east quay. Low east quay road continuing south. Rounded quay corners at all four ends. Cross street at the west end. |
| Arch count and form | conforms | front, rear, rear_side, aerial, facade_close. Three semicircular river arches on short jambs, plus a smaller semicircular land arch. |
| Voussoirs and spandrels | conforms | arch_spandrel, facade_close, architecture_close. Voussoir ring is a lighter course with a lowered keystone. Spandrels are solid, coursed ashlar. |
| Piers and cutwaters | conforms (east river pier lacks a cutwater, P2 #3) | cutwater_pier, facade_close, top, rear_north. Pointed prismatic cutwaters with pyramidal caps on both faces of the two mid-river piers. Pier pilasters with closed panel frames. |
| Cornice | conforms | architecture_close, arch_spandrel, front_spring crop. Moulded cornice with a dentil course, returned around the keystone. |
| Balustrades and pedestals | conforms (square balusters, P2 #1) | front, roadway_deck, architecture_close, balustrade. Continuous balustrade with intermediate pedestals and larger pier and end pedestals. |
| Lamp standards | conforms | glass_close, lamp_standard, front. Ornate double-lantern standards with a central finial, smooth swept C-scroll arms and spiral volutes, on pier and end pedestals. |
| Carriageway and footways | conforms | top, roadway_deck, front_corner. Four-lane carriageway with one solid centreline, dashed lane lines and kerbed footways on both sides. |
| Approaches and quays | conforms | front, front_corner, aerial, top, rear_side. At every corner: bridge end pedestal, then quadrant balustrade, then tangent pedestal, then solid coped quay parapet. Quadrants sit on curved quays. Low east quay road runs under the land arch. |
| River | conforms | front, rear, aerial, river_underside. Dark olive water between quay walls, continuing out of every frame. |
| Context | conforms (sparse downstream, P2 #7) | front, front_corner, aerial, rear_side. Old-town blocks with hipped tile roofs and window grids. |
| Materials hierarchy | conforms | all views. Warm sandstone bridge, lighter voussoir and keystone tone, grey coursed quay walls, grey paving, dark asphalt, dark green-grey lamp metal, cream lantern glass. |

## 4. Camera validity

- **front**: valid. The bridge, west quadrant and hero lamp are legible. The finial touches the top edge (P2 #6).
- **front_corner**: valid. The whole bridge is framed, including the near quadrants and the far land arch.
- **aerial**: valid. The whole bridge and both banks are in frame.
- **top**: valid. Nadir view showing the full plan.
- **left_side**: valid but weakly composed (P2 #9). The west end is complete, and the far spans leave the frame.
- **right_side**: valid. The land arch, the low quay road through it, one river arch and the east retaining wall are legible.
- **rear**: valid. All four arches, both ends and the curved north-east quay are in frame.
- **rear_side**: valid. The whole bridge is in frame, from the east quadrant and end lamp at the left to the west abutment at the right. Nothing occludes it.
- **Detail views** (facade_close, architecture_close, glass_close, arch_spandrel, cutwater_pier, balustrade, lamp_standard, roadway_deck, river_underside, rear_north): all valid. Each target is unoccluded and legible. Clipping at the frame edges is expected in detail framing.

No view has an occluded, clipped or illegible target at P0 or P1 level.

## 5. Previous-version findings: resolved in the pixels?

**v002 P1s**

1. **West quadrant read as two concentric barriers (front, front_corner): resolved.** The front and front_corner crops show one barrier at each corner: bridge pedestal, then quadrant balustrade, then a square capped tangent pedestal, then the solid coped quay parapet. No second slab runs beside the balustrade. Some heaviness remains from the camera angle (P2 #10 and #13).
2. **Lamp C-scroll arms and volutes made of box segments with black gaps: resolved.** In glass_close, lamp_standard and front, the arms are continuous smooth curved tubes running into the lantern seats, and the volutes are smooth spirals. The black joint gaps are gone. Only tiny collar notches remain (P2 #11).
3. **Black void squares at the pier panel frame corners: resolved.** Crops of architecture_close, facade_close and front show the rails running full width, with the stiles seated between them. All four corners are closed.
4. **rear_side clipped the east end: resolved.** The east quadrant, end pedestal lamp and land arch are now inside the left part of the frame, and the west abutment is inside the right. Nothing occludes them.

**v002 P2s, all still present except one not seen**

- Square balusters: present (#1).
- Saw-tooth tabs under the quadrant plinth: not seen at review resolution, so not counted.
- Grey quay ledge under the west springing: present (#2).
- No cutwater at the east river pier: present (#3).
- Plan proportion drift: present (#4).
- Deck shadow smears: present (#5).
- Hero-lamp finial touching the top edge: present (#6).
- Sparse context plots by the quays: present (#7).
- White specks at a lantern: present (#8).

**Earlier fixes that must still hold**

| Earlier fix | Holds? | Seen in |
|---|---|---|
| v001: source plan with fourth land arch, curved north-east quay and narrower upstream channel | yes | top, aerial, rear, rear_side |
| v001: quadrant walls at all four corners, seated on curved quays without overhang | yes | top, aerial, rear_side |
| v001: cutwaters proud of the jambs, without slit | yes | cutwater_pier, facade_close |
| v001: ornate double-lantern lamps | yes | glass_close, lamp_standard |
| v001: river, quays and town continue past every frame | yes (sparse downstream, #7) | — |
| v001: warm sandstone, dark olive water, distinct quay and paving tones | yes | — |
| v001: framed front, front_corner, left_side and right_side views | yes (left_side composition P2, #9) | — |
| v002: single centreline | yes | top, roadway_deck |
| v002: lowered keystone with dentils returned around it | yes | arch_spandrel, river_underside |
| v002: no bus in front of the deck in roadway_deck | yes | roadway_deck |
