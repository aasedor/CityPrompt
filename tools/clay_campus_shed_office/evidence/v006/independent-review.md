# Independent RLASM v6.1 holistic review: clay campus shed office, v006

Reviewed: sources/front.png, sources/oblique.jpg and sources/top.jpg; all 18 renders at full resolution (1440x1080); boards phone-01 to phone-04. I did not read any build code, reports, README or VERSIONS files. Every judgement below comes from the pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** All four v005 P1s and all five v002 defects are fixed in the pixels. However, the ramp fix swapped one defect for another (the ramp now runs at right angles to the facade, where the sources show it parallel). Four further P1 fidelity and contact defects also remain.

**Counts: P0 = 0, P1 = 5, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (strip at x 600-625, y 865-980); front_corner (railed ramp from ~880,690 down to ~990,765); facade_close (rails at x 1190-1440, y 640-770); front (x 555-600, y 615-670); aerial (x 320-440, y 650-740) | The loading ramp is a narrow railed ramp **perpendicular** to the south facade. It runs about 9 m straight south from the west end of the dock, and in top its foot overruns the apron pad edge (pad ends at y ~970). In the sources it runs **parallel** to the facade: oblique shows the yellow-edged ramp running along the apron from the dock (~950,580) down westward to the corner (~740,790); front shows it from (930,580) down to (660,640); top shows the stepped low strip at x 215-535, y 715-760, west of the dock. | The v005 "ramp crosses roller door" fix rotated the ramp instead of offsetting it outboard. | Restore a ramp parallel to the south facade that descends westward from the dock's west end to grade at the corner-bay column. Set it outboard of the roller-door bay with a narrow level landing strip between the door and the ramp's outer, yellow-edged kerb, so it passes in front of the roller door without intersecting it (as the oblique shows). Remove the perpendicular ramp and its rails. Keep the ramp inside the apron pad. |
| 2 | P1 | top (terrace y 735-805 against monitor pitch ~115 px); terrace_roof (AC unit at x 465-820 spans from the front rail almost to the monitor glazing); front_corner and aerial (the terrace reads as a narrow walkway) | The roof terrace is a shallow strip, about 0.6 of one monitor pitch deep. The rooftop unit fills almost its whole depth, so the terrace reads as a walkway, not a deck. In source top the terrace deck (y 440-580) is about 1.5 monitor pitches deep (pitch ~95 px). Source oblique shows a broad deck with the unit and ductwork sitting mid-deck and open floor all round. | The south monitor is set too far forward over the office box (or the box is too shallow). | Move the south monitor's glazing line north (or deepen the box) so the terrace is roughly 1.4-1.5x the monitor pitch. Place the unit and duct in the west third, with clear deck on all sides, as in source top (330-490, 430-530). |
| 3 | P1 | left_side (sawtooth west walls x 375-820: beige plinth only y 665-680); entrance_corner (x 0-320: plinth y 650-700 against a ground storey of about y 320-700); sawtooth_contact | On the west faces of the sawtooth bays, the light-grey precast base is only a thin beige plinth, about 12-15% of the ground storey, with charcoal cladding down to near grade. Sources front (x 0-230, y 545-600) and oblique (x 180-300, y 540-610) show a light-grey precast base running up to the ground-floor window sills, about 35% of the ground storey. | The v005 precast fix was applied only to the box's south bays. | Raise the west-face precast base on all four sawtooth bays to sill height (~35% of the ground storey) in light grey, the same tone as the south precast, not the beige plinth. |
| 4 | P1 | clerestory_close (2 panes visible across the full frame); front (x 285-1155, y 405-470: 8 panes per monitor); terrace_roof; front_corner | The monitor glazing is divided into about 8 very wide panes per monitor, split by one transom. In source oblique and source top, each monitor band has a dense rhythm of about 25-30 narrow vertical mullions (pane width about a third of the render's). The coarse division makes the clerestories read as a different curtain-wall type. | Mullion spacing is set to the structural bay instead of the glazing module. | Subdivide each monitor's glazing into narrow lights at about one third of the current pane width (about 25-30 lights per monitor run), keeping the transom and cap. |
| 5 | P1 | interior (monitors at x 205-355, y 695-820 and x 605-745, y 755-930 with detached shadows below; chair at x 1085-1160 with its shadow ~40 px below); stairs (chairs at x 420-470 and 650-720 with floating shadows at y ~820 and ~845) | The desk monitors hover visibly above the desktops, with a gap and a separate cast shadow, and the task chairs float above the floor. These are floating parts in a delivered detail view. | Entourage z-offsets are wrong: monitors are not seated on the desk top and chair bases are missing or raised. | Seat each monitor on a stand that touches the desk top, give chairs a pedestal or legs that reach the floor, and re-render interior and stairs. |
| 6 | P2 | left_side (x 820-970, y 400-470); right_side (x 455-610, y 392-470) | The south (office-box) monitor peaks ~35-40 px above the other three, and its sloped roof plane shows above the west and east gable walls. In the sources the monitor caps read as one consistent height. | The south tooth uses a different height. | Match the south monitor's ridge height to the others, and carry the gable cladding up to close the roof edge. |
| 7 | P2 | front (canopy end x 1170-1190); top (canopy x 470-1095 against box edge ~1095, pad) | The dock canopy runs slightly past the east-end column. | Canopy length is not snapped to the gridline. | Stop the canopy at the east-end column face. |
| 8 | P2 | left_side, entrance_corner, front_corner | The street tree is a thin two- or three-stick trunk with a lollipop cluster of low-poly balls. | Placeholder entourage. | Use a single trunk with a canopy massing proportioned like the source tree. |
| 9 | P2 | rear, rear_side | North-wall windows are irregular: some bays have upper and lower windows, some only an upper, two are blank, and there is a lone door. This face is not in any source, so this is a coherence-only note. | Ad hoc window placement. | Use a regular two-storey window rhythm per bay, with the door in one bay. |
| 10 | P2 | entrance_corner (white plaque on canopy x 300-425) | The canopy sign is a white bar that is not centred on the entrance door. | Sign placement. | Centre the fascia sign over the entrance bay. |
| 11 | P2 | glass_close | The window reveal is very shallow; the frame almost sits flush with the precast. It is still acceptable as clay. | Small inset. | Increase the inset to about 150-200 mm with a visible return. |
| 12 | P2 | interior, stairs | The interior is very dark, which makes the walls hard to read. | Lighting. | Add fill light. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (four south-glazed sawtooth monitors over a flat-roofed office box) | conforms (the south monitor is slightly taller, finding 6) | left_side, front_corner, aerial against front and oblique |
| Storey count (two) | conforms | front, left_side, right_side, rear |
| Bay rhythm, south (X-braced corner bay, tie-rod canopy bays, X-braced east-end bay) | conforms | front, facade_close, terrace_roof |
| Bay rhythm, west (two box bays: window-over-entrance bay and X-braced corner bay, separated by an exposed galvanised column) | conforms | entrance_corner, left_side |
| Entrance and canopy (thin canopy on the west face only, door clear of the column) | conforms | entrance_corner, left_side |
| Dock (raised dock with yellow nosing under the cantilevered canopy) | conforms | dock_contact, front_corner |
| Ramp and stairs | **deviates**: the ramp is perpendicular instead of parallel (finding 1); the two stairs are present | top, front_corner, facade_close |
| Portal frame and braces (galvanised columns, X-braces in corner and east-end bays only, tie rods from the columns to the canopy edge, no piercing) | conforms | front, architecture_close, facade_close |
| Monitors and clerestories | **deviates**: the mullion rhythm is too coarse (finding 4) | clerestory_close, front against oblique and top |
| Terrace and rooftop plant (rail, unit, duct) | **deviates**: the terrace is too shallow and the unit fills it (finding 2) | top, terrace_roof against top and oblique |
| Gable ends | west conforms in profile; east gable and north wall are not in any source and are coherent (findings 6 and 9 are P2) | left_side, right_side, rear |
| Materials hierarchy (charcoal corrugated cladding, galvanised frame, light-grey precast ground storey) | **deviates** on the sawtooth west walls, where the precast base is too low (finding 3); conforms on the south box bays | entrance_corner, left_side, facade_close |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every view is legible. sawtooth_contact cuts the tree tops at the bottom edge, but the target is fully legible. interior and stairs are dark but readable. top is a true nadir view, which is valid for the role, although it cannot show the vertical monitor glazing that the source top shows obliquely.

## 5. Prior findings: verification from pixels

| prior finding | status | evidence |
|---|---|---|
| v005 P1: a black strip hid the galvanised column between the west window bay and the corner bay | resolved | entrance_corner x 615-645: a light-grey column runs full height to grade; the canopy passes in front without masking it |
| v005 P1: the sloped ramp crossed the roller door in the bay east of the corner | resolved, but with a regression | facade_close and front_corner: nothing crosses the roller door any more, but the ramp is now perpendicular to the facade, against the sources (new finding 1) |
| v005 P1: the corner-window bay and roller-door bay were charcoal where the sources show light-grey precast with precast jambs | resolved | facade_close, glass_close, entrance_corner: both bays are light-grey precast through the ground storey, the window sits in a precast surround and the roller door has precast jambs |
| v005 P1: north-wall upper windows in the end bays ran into the portal columns | resolved | rear x 270-330 and 1110-1170: the end-bay windows are centred and clear of the columns |
| v002: braces piercing the canopy | resolved | architecture_close and facade_close: the tie rods end at the canopy edge and the X-braces stop at the bay beam above the canopy |
| v002: door split by a column | resolved | entrance_corner: the entrance door (x 440-535) sits whole within its bay; the column is at x 615-645 |
| v002: one-bay west face | resolved | entrance_corner and left_side: two bays on the box's west face |
| v002: wrap-around canopy | resolved | entrance_corner and front_corner: the canopy is on the west face only and stops at the corner column; the south corner bay has no canopy |
| v002: X-braces in every bay | resolved | front and facade_close: X-braces only in the corner and east-end bays; tie rods in the canopy bays |
