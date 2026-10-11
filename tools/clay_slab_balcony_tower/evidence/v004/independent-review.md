# Independent RLASM v6.1 holistic review: clay slab-balcony tower, v004

Reviewer: independent (no build code, reports or builder notes read). I judged only the pixels of `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`, all 18 renders at full resolution (1440x1080), and the 4 phone boards. I also checked zoomed crops of the front roofline, the front base, the front_corner roof and the aerial roof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the four v003 defects are fixed in the pixels, but the outer-bay balcony plates sit flush between the fins as recessed loggias. In the source they cantilever well past the fin and corner lines as stacked trays, so the silhouette and plan outline read as a plain framed box.

**Counts: P0 = 0, P1 = 1, P2 = 6**

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front.png (outer bays x~505-650 and x~790-935, y~185-870; left/right silhouette edges x~470 and x~965); left_side.png and right_side.png (silhouette edges x~485 and x~945, every storey); architecture_close.png (balcony plate x~640-1165 ends flush against the corner fin x~240-640); front_corner.png and aerial.png (corner piers x~690-730 and x~540-580 run clean from parapet to grade); top.png (plain square outline x~418-1020, y~238-842) | The outer-bay balcony slabs and glass balustrades stop at the front plane of the fins and at the side faces of the corner piers. No plate projects past a fin or past a building corner. There is no glass end return, and nothing sticks out of the elevation silhouette or the roof outline. The tower reads as a framed box with recessed loggias. **Source:** in front.png the left stack (x~218-300) and the outer stacks (x~385-655, x~745-935) cantilever clearly beyond the fin and corner lines. In oblique.jpg the west-face plates (x~215-370) and the south-face outer stacks (x~420-640, x~830-1030) project as serrated trays with glass returns at their ends. In top.jpg the slab plates show past the roof parapet on the south edge (y~680-720) and the east edge (x~880-910), so the outline is notched, not square. | The balcony depth is held inside the fin depth: the fins are as deep as the balconies, or deeper. The plates are modelled as infill between fins instead of cantilevered slab extensions. | On every residential storey of the outer bays: extend each balcony slab plate about 1.2-1.5 m beyond the outer face of the bay-line fins. On the bays at the corners, also carry it about 0.8-1.0 m past the corner pier along the face. Keep the fins at their current depth or shallower, so the plates read in front of them. Add glass balustrade end returns on the exposed plate ends. Re-check the top view: plate edges should show beyond the parapet on the south and west faces. |
| 2 | P2 | glass_close.png (white ellipses x~620-1180, y~0-80 and y~490-570); front.png (an oval highlight near the top of every centre-bay window, x~680-760); left_side.png and right_side.png (white glow in the outer-bay glazing, y~460-640) | Large soft white ovals repeat on every centre-bay window and inside the balcony glazing. They read as reflections of interior lamps or as smeared highlights. | Interior ceiling-light emitters or an area light reflecting in glass with high specular. | Lower the interior emitter strength or the glass specular, or move the interior light above the window head, so the glazing reads as an even dark grey. |
| 3 | P2 | top.png, aerial.png, roof_penthouse.png | The three grey rooftop units sit at three roof corners, far from the penthouse. Source top.jpg and oblique.jpg cluster the condensers and units tight against the north and east sides of the penthouse (top x~615-740, y~265-430). | Placeholder RTU positions. | Move the units next to the penthouse's north and east walls, as in the source. |
| 4 | P2 | top.png (penthouse group x~612-912, y~372-565), aerial.png, rear.png | The penthouse is a main box plus a raised upper block plus a lower side annex with a door (x~825-912). The source shows one simple tall concrete cube. | An added stair or door annex. | Merge the annex into the main volume, or shrink it so the silhouette reads as one cube. |
| 5 | P2 | front.png, glass_close.png, lobby_entry.png (brick jamb x~1185-1230) | Centre-bay brick wraps every window on all four sides as a frame. The source oblique.jpg centre bay reads as brick spandrel bands under a continuous window band, with no brick jambs. | The brick frame is modelled as a ring. | Keep the brick as horizontal spandrel bands only, and run the window band from fin to fin. |
| 6 | P2 | base_corner.png (tree x~750-1205, y~300-1080) | The foreground tree covers most of the right half of the frame: the lobby canopy, the corner pier and the entry. | Tree placed on the camera axis. | Move the tree or the camera about 2 m along the curb so the lobby corner is unobstructed. |
| 7 | P2 | interior.png | The frame is almost entirely one glazing pane and railing seen from inside: a mullion at x~505, a rail at y~565. It carries little information about the room (floor, ceiling and slab edge are barely legible). | The camera is pushed too close to the glazing. | Pull the camera back about 2-3 m and widen it, so the floor, ceiling soffit, slab edge and balcony read. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | **deviates** | front, left_side, right_side, top vs source front/oblique/top. Clean box; no cantilevered tray serration (finding 1). |
| Storey count | conforms | front.png: 12 residential storeys (balcony rows at y~222 through ~857) over a ground floor; matches the brief's recorded 12. |
| Balcony stacks and slab bands | **deviates** | facade_close, architecture_close, balcony_close: the plates, glass balustrades and slab bands exist and are stacked, but they are recessed flush with the fins instead of projecting (finding 1). |
| Fins and corners | conforms (with finding 1) | front, front_corner, fin_contact: full-height concrete fins at the bay lines and corners. The fins stop cleanly under the parapet, with no stubs. |
| Centre-bay spandrels and windows | conforms (P2 note) | glass_close, rear_lane: coursed brick spandrels under the window band in the centre bay. The extra brick jamb frame is finding 5. |
| Recessed ground floor and lobby | conforms | front, lobby_entry, fin_contact, base_corner: glazing set back behind columns, an entry canopy on a column, doors with depth and returns. |
| Penthouse and roof plant | conforms (P2 notes) | roof_penthouse, aerial, front_corner: a roughly two-storey concrete penthouse with louvre and door, a flat roof, a low parapet, rooftop units and a vent. Composite massing and unit placement are findings 3 and 4. |
| Materials hierarchy | conforms | Light concrete for fins, slabs and parapet; terracotta brick for spandrels and the rear ground infill; grey glass; dark glazing frames. All untextured clay in source-palette colours. |

## 4. Camera validity

- All 8 whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) show the whole asset, unclipped and legible.
- base_corner: the target is partly occluded by the foreground tree, but the corner pier, ground-floor recess and canopy edge are still readable. P2 (finding 6), not invalid.
- interior: legible but low-information. P2 (finding 7).
- No view is invalid.

## Prior-version (v003) findings

| v003 finding | status in v004 pixels | evidence |
|---|---|---|
| Black band along the canopy fascia | **resolved** | fin_contact.png (canopy x~215-1035, y~420-530) and lobby_entry.png (x~0-655, y~230-345): the fascia is uniform light concrete with no dark band. In front.png the canopy at x~555-670, y~895-905 is light grey. |
| Black caps at the parapet corners | **resolved** | aerial.png, front_corner.png and rear_side.png (all four parapet corners) and the zoomed aerial and front_corner crops: the coping is continuous light concrete, with no dark corner blocks. |
| Fin stubs proud of the parapet (crenellated roofline) | **resolved** | front.png, left_side.png, rear.png and right_side.png roofline (y~160-235): the parapet is one continuous horizontal band. The fins end beneath it and no stub rises above. |
| Rear roller door split by a fin | **resolved** | rear.png (door x~555-630, y~885-940) and rear_lane.png (door x~135-510, y~515-795): the door sits whole inside the left bay's brick infill, clear of the fin at x~610-690. |
