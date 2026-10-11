# Independent RLASM v6.1 holistic review: condo v005 (clay brick-podium condo tower)

Reviewer: independent; judged only from the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg), the 18 renders and the 4 phone boards. No build code, reports, README or VERSIONS files were read.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v004 P1s are fixed in the pixels: the corner bay, the lobby portal and the penthouse footprint and height now match the sources. One P1 remains: the mechanical penthouse renders as a sealed, solid-lidded block, not the open-topped louvred screen enclosure with equipment wells that the top source shows.

**Counts: P0 = 0, P1 = 1, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top.png (penthouse x≈500-1040, y≈322-725); aerial.png (x≈545-960, y≈240-560); front_corner.png (x≈555-945, y≈205-450); roof_crown.png (x≈0-1030, y≈280-780); rear_side.png (x≈515-890, y≈220-450) | The penthouse is a closed box with louvres on its sides and a flat, blank, unbroken lid. The only object on it is one small dark cube (top.png about x 830-878, y 507-543). In sources/top.jpg (x≈330-885, y≈245-520) the penthouse is a pale louvred screen wall around an **open-topped** enclosure: two large equipment wells (left x≈345-515, right x≈655-865) hold about 12-15 rooftop units, condensers and ducts, with a roofed central core (x≈520-655) and a smaller roofed block (x≈655-720, y≈315-410). sources/oblique.jpg also shows several units and stepped parts on the penthouse top (x≈380-790, y≈75-140). In the matched top/aerial roles the render reads as a sealed solid mass, not a mechanical screen enclosure. | The penthouse was modelled as one extruded solid with louvre grooves on the sides and a capped top, not as a screen ring around wells. | Keep the current outer footprint (about 75% x 77% of the tower roof) and height (about 2-2.5 storeys). Hollow it into a louvred screen ring about 1.5-2 m thick. Inside, add one roofed central core about 25% of the enclosure width and two open wells on its sides holding 10-15 simple pale boxes (RTUs, twin-fan condensers, duct runs) at about 1-2 m height. Optionally add a low lid strip only over the core. Re-render top, aerial, front_corner and roof_crown. |
| 2 | P2 | top.png (west terrace x≈285-410, east strip x≈1130-1150) | The tower is set back about 125 px from the podium edge on the west but only about 20 px on the east. The west terrace is the widest podium roof strip. In sources/top.jpg the tower roof reaches nearly to the west edge of the lot. (Retained from v004.) | Tower offset inside the podium rectangle | Move the tower about 60-80 px (scaled) west, or narrow the west terrace to match the south strip |
| 3 | P2 | top.png | The tower plan ratio is about 720:540 (≈1.33). sources/top.jpg reads about 1.55-1.6 long-to-short. (Retained from v004.) | Tower depth too large | Reduce the N-S depth of the tower by about 12-15% |
| 4 | P2 | front.png (y≈730-770); right_side.png (x≈515-930, y≈752-770) | The lowest tower storey, just above the podium terrace, has no balcony slab. The lowest balcony row serves the storey above it. sources/front.png shows a balcony row right above the podium roof (x≈300-440, y≈500-520). (Retained from v004.) | Balcony loop starts at tower floor 2 | Start the balcony stacks at the first tower floor, or explicitly use the terrace as that floor's outdoor space |
| 5 | P2 | rear.png (x≈688-752, y≈878-945); rear_lane.png (x≈178-545, y≈512-893); right_side.png (x≈895-962, y≈895-945) | Service and loading doors are flat white slabs with no frame, panel lines or visible reveal. sources/front.png (x≈785-820, y≈635-680) shows a dark grey panelled overhead door in a recess. (Retained from v004.) | Door is a single flat plane in a pale palette slot | Use a mid or dark grey door with 4-6 horizontal panel lines, a 100-150 mm reveal and a head/jamb frame |
| 6 | P2 | front.png (podium x≈345-1095, y≈780-950) | The ground (retail) storey is still a little shorter than the second storey: about 70 px vs 95 px, a ratio of ≈0.74. The source is about 78 vs 90 px (≈0.87) at the corner bay of sources/front.png (x≈515-635). Partly improved from v004. | Canopy band set slightly high in podium section | Lower the canopy/spandrel band about 0.4-0.6 m, or raise the ground floor by the same amount |
| 7 | P2 | corner_entry.png (x≈1150-1440, y≈320-395) | The lobby portal's own canopy sits directly on top of the continuous dark storefront canopy. This stacks two dark slabs over the door. In sources/front.png (x≈680-730, y≈615-630) the portal has a single projecting canopy. | Portal canopy added without trimming the run canopy | Interrupt the continuous canopy across the portal bay, or drop the portal canopy to the same level and merge them |
| 8 | P2 | corner_entry.png (x≈740-750, y≈0-860) | A thin brick sliver sits between the dark corner post and the east glazing of the corner bay, so the glass does not meet the corner mullion on the east side. The south side meets it cleanly. | East corner-bay glazing offset from the corner post | Close the east glazing onto the corner mullion so both faces meet symmetrically |

No P0 findings. Contact and depth checks pass on every detail view:
- Storefront mullions and podium windows have visible reveals and returns, and the ribbon windows have projecting precast sills (podium_retail, architecture_close, rear_lane).
- Balcony slabs bear on the slab line, with glass balustrades seated on them (facade_close, balcony_stack, glass_close).
- The podium terrace glass balustrade sits on the precast cornice (front, architecture_close, podium_setback).
- Trees sit on the ground.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (low full-lot brick podium plus a tall rectangular glass tower plus a pale penthouse block) | conforms (tower plan ratio and west offset P2) | front_corner vs oblique; top vs top |
| Storey count (2-storey podium; about 11 tower storeys; penthouse about 2 storeys) | conforms: 2 podium storeys; 11 tower storeys counted on rear.png and front.png (spandrels y≈205→770); penthouse ≈2-2.5 storeys | front, rear, roof_crown |
| Podium bays and storefronts (brick piers, tall storefront glazing, dark canopy band, ribbon windows with precast sills, double-height glazed SE corner bay on a thin mullion with dark spandrel, stone-framed lobby portal in 2nd east bay) | conforms (canopy doubling and brick sliver are P2) | front, right_side, corner_entry, podium_retail, architecture_close vs sources/front.png |
| Podium terrace and setback (roof terrace behind glass balustrade on precast cornice, tower near-flush to the street faces) | conforms; west terrace wider than source (P2) | front, podium_setback, architecture_close, top |
| Tower curtain wall and spandrels (continuous mullions, spandrel band every floor, corner columns) | conforms | facade_close, glass_close, balcony_stack, front |
| Balcony stacks (projecting slabs with glass balustrades in vertical stacks on each face) | conforms (lowest floor missing, P2) | facade_close, balcony_stack, front, right_side, rear |
| Penthouse (large pale louvred mechanical enclosure, about 75% of roof each way, behind a guard rail) | **deviates** on top form: footprint, height, louvres and guard rail conform, but it is a sealed solid lid, not an open screen enclosure with equipment (Finding 1, P1) | top, aerial, front_corner, roof_crown vs sources/top.jpg, sources/oblique.jpg |
| Materials hierarchy (red brick podium < pale precast trim < blue-grey glass tower with pale spandrels < pale metal penthouse) | conforms | all whole-envelope views |

## 4. Camera validity

All 18 views are valid: the target is unoccluded, unclipped and legible. The trees in podium_retail.png (x≈1015-1440, y≈0-990) and architecture_close.png (x≈515-1440, y≈640-1080) cover part of the frame but leave the storefront and window grammar readable. interior.png shows a lobby reception desk against tall glazing, which is legible. front.png is a head-on south elevation, not the source's two-point corner view, but the corner and the south face are both legible, and front_corner covers the oblique role.

## 5. Prior-version (v004) findings, judged from v005 pixels

| v004 finding | sev | v005 status | evidence |
|---|---|---|---|
| Solid brick pier at the SE corner; single-height storefronts under the canopy at the corner; lobby in the 1st east bay. The source shows a double-height glazed corner bay on a thin mullion with a dark spandrel, and a stone-framed lobby portal with its own canopy in the 2nd east bay | P1 | **resolved** | corner_entry.png: a double-height glazed bay wraps the corner on a thin dark post (x≈705-740), with a dark spandrel band at mid height (y≈215-365) and no corner pier. A pale stone-framed portal with its own canopy sits in the 2nd east bay (x≈1190-1380). front.png and right_side.png agree. (Canopy doubling and brick sliver are new P2s.) |
| Penthouse a one-storey box over about 60% of the roof. The source shows a large pale louvred screen enclosure about 2-3 storeys tall over about 75% of the roof each way | P1 | **partly**: size and height resolved; enclosure form not | top.png: the penthouse covers about 75% (W) x 77% (D) of the tower roof. front.png: its height is ≈107 px vs ≈52 px per tower floor, ≈2 storeys (≈2.5 in roof_crown). But it is a solid lid with no equipment wells (new Finding 1, P1) |
| Wide west terrace | P2 | not resolved | top.png: west strip ≈125 px vs south ≈60 px and east ≈20 px |
| Tower plan ratio | P2 | not resolved | top.png ≈1.33 vs source ≈1.55-1.6 |
| No balcony on the lowest tower floor | P2 | not resolved | front.png, right_side.png: no slab at the first tower floor above the terrace |
| Flat white service doors | P2 | not resolved | rear.png, rear_lane.png, right_side.png |
| Short retail storey | P2 | partly | ground/upper ratio ≈0.74 vs source ≈0.87 |
| Opaque interior glass | P2 | resolved | podium_retail, corner_entry, glass_close and podium_setback show interior floors, mullions beyond and furniture through the glass. interior.png shows a furnished lobby |
