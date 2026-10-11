# Independent RLASM v6.1 holistic review: clay campus shed office, v007

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** One P1 remains: the office box's west street face reads as three bays (a blank bay under the fourth monitor, plus two narrow bays across the terrace depth). The sources show two bays: a window-and-entrance bay under the gable and one wide X-braced bay. All five v006 P1 findings are resolved in the pixels.

**Counts: P0 = 0, P1 = 1, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | left_side.png (box west face x≈755-1065, y≈455-660); front_corner.png (x≈430-600, y≈520-740); entrance_corner.png (x≈220-930); sawtooth_contact.png (x≈890-1440) | The box's west face has four galvanised columns (left_side x≈755, 880, 970, 1065), which makes three bays. Bay 1 (x≈755-880) sits directly under the fourth monitor's gable and is blank, solid charcoal cladding over both storeys. Bay 2 (x≈880-970) is narrow, with an upper window and the double entrance door. Bay 3 (x≈970-1065) holds the X-brace over a glazed storefront. **Source:** front.png x≈240-530 and oblique.jpg x≈300-625 show exactly **two** bays. The bay under the gable (front x≈240-375) carries an upper multi-light window (x≈275-340, y≈320-390) and the glazed double entrance doors (x≈275-350, y≈490-610) under the CAMPUS HQ canopy. The single wider bay under the terrace (x≈375-530) carries the X-brace over strip glazing and a glazed/dark lower panel. The render moves the window and entrance off the gable bay, leaves the gable bay blank, and splits the terrace depth with an extra mid-terrace column. That column also has no partner on the east face: right_side.png shows the box's east face terrace depth as one bay, x≈345-545. | The terrace-depth framing was subdivided to place the entrance door clear of a column, instead of keeping one wide braced terrace bay and putting the entrance in the gable bay. | Remove the mid-terrace column (left_side x≈970), so the terrace depth becomes one X-braced bay matching the east face grid. Put the upper multi-light window and the glazed double entrance door in the bay under the fourth monitor gable (left_side x≈755-880). Under the X-brace bay, keep strip glazing over a glazed/dark lower panel. Run the thin entrance canopy across both west bays, from the sawtooth/box junction to the corner column. Keep it on the west face only. |
| 2 | P2 | left_side.png (sawtooth bays x≈375-755, y≈630-660); front_corner.png crop | The light-grey precast base now reaches the lower window sills. It is about 25% of the ground storey, as a light strip plus a beige plinth. The source front shows about 30-35%. | The lower windows are slightly too tall and low-set. | Raise the lower sills and the base top by about 0.3-0.4 m. |
| 3 | P2 | front.png (south face x≈420-1180, y≈555-615); dock_contact.png | Three sectional roller doors (bays 2, 4, 5 of the canopy run). The source front/oblique show about two in the visible span, with a personnel door, a window and a sign panel between them. | Door pattern repeated per bay. | Replace one middle roller door with a solid precast panel plus personnel door. |
| 4 | P2 | top.png (stair x≈690-715, y≈880-895); front.png (x≈685-710 and x≈1155-1180) | Apron stairs: one mid-dock and one at the dock's east end. Source top.jpg shows two stairs at about 43% and 72% of the box length (x≈540-580, 795-835). | Stair placement approximated. | Move the east stair to about 72% of the box length, facing south. |
| 5 | P2 | interior.png (x≈1150-1300, y≈560-780) | A desk sits directly under the stair stringer with almost no headroom. It reads as a near-clash, not as a usable desk. | Furniture layout ignores the stair footprint. | Move the desk at least 1 m clear of the stair run. |
| 6 | P2 | architecture_close.png (rod foot x≈560-620, y≈980-1080) | The lower anchorage of the canopy tie rods is lost in the dark canopy top. There is no visible clevis or edge beam where the rods land. | Rod ends meet the canopy surface without a fixing. | Add a small edge-beam plate where each rod lands. |
| 7 | P2 | dock_contact.png (dock edge x≈0-1440, y≈540-700) | The dock edge has a yellow nosing but no bumpers or dock levellers at the roller doors. | Detail omitted. | Add simple bumper blocks either side of each roller door at the dock edge. |
| 8 | P2 | rear.png, rear_side.png | The north wall (not in source) is coherent: portal grid, charcoal cladding, light plinth, a few windows. The only issue is that its window placement is random per bay. | Unsourced face. | Optional: regularise to one window per storey per bay. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (four south-glazed sawtooth monitors over a flat-roofed two-storey braced box) | conforms | front_corner, aerial, left_side vs front.png/oblique.jpg |
| Storey count (two) | conforms | front, left_side, entrance_corner |
| Bay rhythm, south | conforms (corner X bay, five canopy bays, east X bay). Door pattern P2 #3 | front, facade_close vs front.png/oblique.jpg |
| Bay rhythm, west | **deviates**: three bays where the source shows two, gable bay blank (P1 #1). Sawtooth bays conform | left_side, front_corner vs front.png |
| Entrance and canopy | deviates in placement: canopy is thin and on the west face only (conforms), but the entrance doors sit in the wrong bay (P1 #1) | entrance_corner, left_side |
| Dock | conforms: raised precast dock, yellow nosing, dock-level roller door, cantilevered dark canopy from the second bay to the east end | dock_contact, front, top |
| Ramp and stairs | ramp conforms: parallel to the facade, descending westward from the dock to the corner bay, outboard, with a handrail. Stairs: two present, east stair position P2 #4 | facade_close, front, front_corner |
| Portal frame and braces | conforms: galvanised columns and beams. X-braces only in the corner bay (south and west) and the east-end bay. Thin tie rods from column heads to the canopy edge in the canopy bays. No brace pierces a canopy | facade_close, architecture_close, front, terrace_roof |
| Monitors and clerestories | conforms: four monitors, vertical south glazing in two rows of about 28-30 narrow lights | clerestory_close, aerial, terrace_roof, front_corner |
| Terrace and rooftop plant | conforms: terrace about 1.45 monitor pitches deep (top.png 150 px vs 105 px pitch). Unit plus duct sit mid-deck at the west end. Continuous rail | top, terrace_roof vs top.jpg |
| Gable ends | west conforms (sloped gables, valley pilasters, two storeys of windows, precast base to sills; proportion P2 #2). East end not in source: coherent | left_side, right_side |
| Materials hierarchy | conforms: charcoal corrugated cladding, light galvanised frame, light-grey precast ground storey on the south, beige plinth, black window frames, dark canopy | all whole-envelope views |

## 4. Camera validity

All 18 renders are valid. No target is occluded or clipped, and all are legible. The front, left_side, right_side and rear elevations frame the building small (about 55% of the width) but readably. Interior and stairs are dark but legible. The phone boards (phone-01 to phone-04) show every view legibly.

## 5. Prior-version (v006) findings, judged from the pixels

| v006 finding | Status | Evidence |
|---|---|---|
| P1 Loading ramp perpendicular to the south facade | **resolved** | front.png x≈420-565: the ramp runs parallel to the facade, falling west from the dock to the corner bay with an outboard rail. Same in facade_close x≈800-1190 and front_corner x≈760-860 |
| P1 Roof terrace about 0.6 pitch deep, unit filling it | **resolved** | top.png: terrace y≈670-820 (150 px) vs monitor pitch about 105 px, about 1.45 pitches. The unit (x≈400-460) sits mid-deck with open deck around it. terrace_roof confirms |
| P1 Sawtooth west walls with only a thin plinth | **resolved** (proportion P2 #2) | left_side.png: the light-grey base rises to the lower window sills in every sawtooth bay |
| P1 Monitor clerestory about 8 wide panes | **resolved** | clerestory_close / aerial: about 28-30 narrow lights per monitor, in two rows |
| P1 Desk monitors and chairs floating | **resolved** | interior.png / stairs.png: screens rest on the desk tops and chairs stand on the floor with contact shadows |
| (v002) braces piercing canopy | resolved | facade_close, front: X-braces stop above the canopy line |
| (v002) door split by a column | resolved | entrance_corner: doors sit within a bay |
| (v002) one-bay west face | partly: now three bays instead of the source's two (P1 #1) | left_side |
| (v002) wrap-around canopy | resolved | entrance_corner, front: the entrance canopy is on the west face only |
| (v002) X-braces in every bay | resolved | front: only the corner and east-end bays are X-braced |
