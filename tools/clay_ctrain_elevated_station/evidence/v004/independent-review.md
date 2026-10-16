# Independent holistic review: clay-ctrain-elevated-station v004 (RLASM v6.1)

Reviewer: independent; did not build the candidate. Evidence used: only the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, the 18 `renders/*.png` (each opened at full resolution) and the four `boards/*.png`. Zoomed crops (reviewer-only, not part of the candidate) were written to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-v004-crops-7f3a/`. Builder notes, metadata and counts were not used as evidence.

## 1. Verdict

**PASS_ZERO_P0_P1**: every identity element in the brief is present, in the right place and in the right proportions across the matched views. The v003 P1 (glazed stair bays stopping on a sill above the sidewalk) is fixed in the pixels. What remains is polish only.

Counts: P0 = 0, P1 = 0, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| — | P0 | — | None found. | — | — |
| — | P1 | — | None found. | — | — |
| 1 | P2 | front | The camera is low and wide-angle with an upward tilt, so the verticals converge strongly. The SW tower, the stair bay and the deck piers all visibly lean. The source front keeps its verticals almost plumb. | The camera is tilted with no shift. | Level the camera and use a vertical lens shift, or raise the camera height and narrow the FOV. |
| 2 | P2 | skywalk_bridge, east_skywalk, front, facade_close | Small black specks at the skywalk truss nodes and at the glass-guard post tops. New black squares also appear at the transom and door-frame nodes of the new entry. | Coincident or interpenetrating member ends (z-fighting or zero-thickness gaps) at the nodes. | Cap the nodes with a small box or plate, or move the member ends back 2–5 mm so the faces do not coincide. |
| 3 | P2 | facade_close, front | Above the recessed entry, the inner bay mullions run past the lowest transom and end in mid-air as short stubs over the door head. They have no sill or head member under them. | The mullion length runs to the old sill height instead of to the new transom. | Cut the inner mullions at the transom bar, or add a head or transom member under them. |
| 4 | P2 | street_underpass | The deck soffit fills the upper 40% of the frame in flat charcoal. In the source front, the underside of the deck reads as mid-grey concrete. | No fill or bounce light under the deck, plus the camera exposure. | Add a weak area or fill light under the deck, or raise the soffit albedo slightly. |
| 5 | P2 | front, facade_close, aerial | Lit brick averages about RGB(118,82,69). Source brick averages about (90–97,59–62,49), so the render is still about 20 levels lighter and slightly more orange. It reads as red-brown brick and is within clay tolerance. | Albedo or exposure. | Lower the brick base colour by about 10–15% in value. |
| 6 | P2 | top, aerial | The E–W street sits further north under the platforms than in the source top. The pylons and the uncovered south platform ends land just south of the far curb, where the source puts them over the carriageway. | Street offset in the site layout. | Move the E–W street about 0.15–0.2 of the platform length south, or shorten the uncovered platform tail. |
| 7 | P2 | rear, rear_side, left_side, train_platform | The guideway ends at both ends. To the south, the track runs out to a deck edge with a guard rail across it. To the north, a short stub on a single pier ends at red-and-yellow buffer stops just outside the headhouse portal. Together they read as a terminus, while the sources imply a through line. (No source shows the north face.) | The asset boundary is modelled as track ends. | Remove the north buffers too, and end both deck stubs with a plain cut joint or expansion-joint line instead of a guard across the track. |
| 8 | P2 | glass_close, architecture_close | Below the glass the canopy posts read white; through the glass roof they read grey. The posts look two-tone. | Optical tint from the glazing over a pale post. | Darken the post albedo to match the mid-grey steel, or lower the glazing tint. |
| 9 | P2 | east_skywalk | Where the east link meets the long N–S skywalk, the link roof meets the skywalk side with a thin dark seam and a small step in height. | Link roof slab stops short of, or overlaps, the skywalk fascia. | Run the link roof into the skywalk fascia and add a flashing or cap strip. |
| 10 | P2 | front | Under the deck, the headhouse ground floor shows a single door and one punched window in a dark undercroft. The source front shows a glazed storefront entrance with a small canopy at this point. | The undercroft facade is simplified. | Replace it with a 2–3 bay glazed storefront and a thin canopy band. |
| 11 | P2 | front, front_corner | The glazed stair bay fills about 80% of the tower's west face. In the sources it fills about 65–70%, with a wider brick pier beside it. | The bay is slightly too wide. | Narrow the bay by one mullion module and widen the brick pier. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front_corner vs oblique, top vs top | The headhouse block has two projecting south-corner towers. The twin canopied platforms run south over the street. There is a W skywalk with a pavilion, an E link and a long N–S skywalk. The plan footprint and relative positions match the source top. |
| Storey count | conforms | front, left_side, right_side, rear | Three storeys: a tall ground-floor storefront level, a second storey of punched windows and a glazed third storey. No missing or extra storeys. |
| Headhouse and glazed band | conforms | front, architecture_close, tower_cap, rear, interior | The continuous glazed band runs around the top storey and across the south face between the towers above the platforms. It has visible mullion depth and a sill ledge. |
| Stair towers and caps | conforms | front, facade_close, tower_cap, top | The square brick towers sit at both south corners. Each has a full-height glazed stair bay on its outer (W or E) face, matching the source top and front. Each has a pale, projecting, layered cap above the roof parapet. The bays now run to grade on a stone base, with a projecting band at about the first floor and a recessed glazed entry. |
| Deck and piers | conforms | front, street_underpass, left_side, aerial | A concrete deck sits on round piers with hammerhead cap beams over the E–W street. The street clearance reads correctly. |
| Platforms: guards | conforms | platform_canopy, aerial, left_side | Glass guards on steel posts run along the outer edges. |
| Platforms: tactile edges | conforms | platform_canopy, train_platform, top | Continuous yellow strips at both track edges. |
| Platforms: pylons | conforms | aerial, front_corner, top, left_side | One red pylon with a pale panel near the south end of each platform. |
| Platforms: stairs | conforms | aerial, front_corner, left_side, top | A guarded stair runs from each platform's south end down to the sidewalk. |
| Canopies | conforms | platform_canopy, glass_close, aerial, top | Long glazed gable canopies on central steel posts, with rafters and purlins. They cover the northern 55–60% of each platform, as in the source top. |
| Skywalks | conforms | skywalk_bridge, east_skywalk, front, right_side | The glazed steel-truss Plus 15 skywalk with X bracing leaves the west face across the west street to a glazed stair pavilion. The east link runs to the long N–S skywalk on round columns, which ends in pavilions. Its run is now full length across the street. |
| Train | conforms | train_platform, aerial, front_corner, platform_canopy | A two-car articulated red-and-white light-rail train stands at the west platform. |
| Streets | conforms (minor offset, P2 #6) | top, aerial, left_side | The N–S street runs west under the W skywalk and the E–W street runs under the deck, both with crosswalks. The E–W street sits slightly north relative to the platforms. |
| Materials hierarchy | conforms | front, facade_close, aerial | Red-brown brick for the headhouse and towers, pale stone for caps and base, grey steel and glazing, pale concrete for the deck and piers, yellow tactile strips, red for the pylons and train. The brick is slightly light (P2 #5). |

## 4. Camera validity

- All 18 views are valid. None has its target hidden behind something, none clips the asset in a way that loses the target, and each one shows its intended subject clearly.
- front: valid but strongly distorted by perspective (P2 #1).
- front_corner, aerial, top: the asset fills about 40–55% of the frame width but reads clearly.
- street_underpass, interior: dimly lit, but the piers, cap beams, soffit and street are legible in street_underpass. The glazed band, sill and view to the canopies are legible in interior.
- Detail views (facade_close, architecture_close, glass_close, platform_canopy, skywalk_bridge, tower_cap, train_platform, east_skywalk): each frames its subject, and the depth of openings and the contact points are legible.

## 5. Previous-version (v003) findings: resolved in pixels?

| v003 finding | v003 severity | v004 status | evidence |
|---|---|---|---|
| Glazed stair bays stop on a projecting sill above the sidewalk; no first-floor band and no glazed entry. | P1 | **Resolved** | front, facade_close: both bays run to grade on a flush pale stone base. A projecting band sits at about 4.5 m. Below it is a recessed glazed entry with a door frame and head. New residual P2s: dangling mullion stubs (#3) and specks at the frame nodes (#2). The SE bay is seen to grade in east_skywalk, right_side and aerial. |
| Converging verticals in the front view. | P2 | Not resolved | front: the tower and piers still lean (#1). |
| Two-tone canopy posts. | P2 | Not resolved (optical) | glass_close, architecture_close (#8). Posts seen directly in platform_canopy are a uniform grey. |
| Specks at truss and guard nodes. | P2 | Not resolved | skywalk_bridge, east_skywalk, facade_close (#2). New specks also appear at the entry frame. |
| Charcoal underpass soffit. | P2 | Not resolved | street_underpass (#4). |
| Brick too light and salmon. | P2 | Partly resolved | The brick now reads red-brown rather than salmon, but it is still about 20 levels lighter than the shaded source brick (#5). I had no v003 pixels to compare against directly. |
| Platform/street relation. | P2 | Partly resolved | The street passes under the canopied platforms, but it is shifted north compared with the source (#6). |
| South deck end reads as a terminus. | P2 | Partly resolved | The south buffer stops are gone, but the south end still has a guard across the track ends, and buffer stops now sit at the north stub (#7). |
| Canopy hip junction. | P2 | Resolved | platform_canopy, architecture_close: the canopy's north gable end sits cleanly over the brick entry volume and the glazed-band ledge. No visible clash or gap. |
| Short east skywalk run. | P2 | Resolved | right_side, aerial, east_skywalk: the N–S skywalk spans the full length across the E–W street on four round columns, with a pavilion at each end. |
