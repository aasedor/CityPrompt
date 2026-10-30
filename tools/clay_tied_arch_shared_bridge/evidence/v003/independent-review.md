# Independent holistic review: clay-tied-arch-shared-bridge v003 (RLASM v6.1)

Reviewer: independent; did not build the candidate. Evidence used: only `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` and the four `boards/*.png`, all opened at full resolution, plus zoomed crops written to a new folder (`scratchpad/tiedarch-v003-review-crops-21cd1bed/`). Metadata, hashes, build reports and builder notes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the contact defect is fixed: the deck ends now land on the coping lines with no overrun and no wedge. But the plan the top source governs is still wrong. The render is a uniform 13-degree parallelogram on a straight canal whose banks run vertically in the image. The source shows a skew of about 6 degrees at the west end. At the east end the source deck end runs the opposite way along an angled landing pier. The east end is therefore about 19 to 20 degrees away from the source.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (vs source top), aerial, rear_side, left_side, right_side | **Render:** both quay copings and both deck ends are exactly vertical in the image. The deck axis is about 12-13 deg off horizontal, so the deck is a 13-degree parallelogram: NW and SE corners about 103 deg, NE and SW corners about 77 deg. The south corner of each end sits back toward the west (about 65-70 px along the axis at both ends).<br>**Source top, measured on ground-level edges (footway edges, coping and pier railing):** the axis is about 14 deg. The west end and west quay lean about 8 deg from image vertical, so the west end is about 6 deg off square to the axis. The canal wall south of the bridge on the east side also leans about 8 deg, so the canal skew is only about 6 deg. The east deck end runs along the angled east landing pier at about 20-21 deg, which is about 6-7 deg past square in the *opposite* sense: its south corner sits about 28 px further *east*, and its NE corner is obtuse (about 96 deg), where the render's is acute (77 deg).<br>**Net:** the render roughly doubles the skew at the west end (13 vs about 6 deg) and reverses it at the east end (about 19-20 deg discrepancy). Side by side, the source deck reads as near-rectangular, slightly trapezoidal, with an angled east pier. The render reads as a strongly sheared parallelogram. Even if the source top is read with an assumed 10-degree keystone (which would make both source ends square to the axis), the render ends are still 13 deg off, so the deviation is larger than any plausible perspective error. | The v002 fix was read as "both ends parallel to straight, vertical quays". The canal and quays were kept vertical in the image and the deck was sheared to match them, so the skew was moved into the deck rather than taken from the source. The source's canal banks are about 8 deg off the building grid and its east landing is a separate angled pier. | Re-take the plan from the source top. Rotate the canal banks to about 6 deg off square to the bridge axis (west quay and the east canal wall south of the bridge). Model the east landing as the angled railed pier, with the deck east end on its coping about 6 deg past square in the opposite sense, giving a slightly trapezoidal deck with the south edge about 5% longer than the north. Keep the ends on the coping lines, the equal plinth setbacks, ties parallel to the local end or quay, and lanes ending at the deck ends. Re-render top, aerial, rear_side, left_side and right_side. |
| 2 | P2 | planter_divider, cycle_lane, architecture_close, top | The planter "grasses" are faceted tan and green polyhedra that read as rocks or crystals in close-up, not as feathery grasses (persists from v002). | Low-poly icosphere clumps used as plants | Swap for upright clay grass tufts (thin blades or cones), leaving the clay palette as it is |
| 3 | P2 | all | The overall palette and light are flat, cold and overcast; the source is warm, with low evening sun (persists from v002). | World and lighting settings | Use warmer key light and world colour; keep clay albedos |
| 4 | P2 | front, arch_springing, left_side, right_side | The deck end lands on the coping line but is only a flush colour change from deck to brick. There is no steel end edge, joint or kerb band like the grey landing line and kerb step in the source front. | No landing element modelled | Add a thin steel end-edge or expansion-joint strip along each deck end, collinear with the coping |
| 5 | P2 | front_corner | A tree hides the south arch's west springing and a context roof hides the SE deck corner. The viewpoint looks along the canal, whereas the source oblique looks diagonally along the bridge from above its near end (all four springings show in aerial, top and rear_side). | Camera placement and context tree position | Move the camera to match the source oblique (high, over the west landing south of the axis) or move the tree |
| 6 | P2 | front, architecture_close, arch_springing | The arch box section shows polygonal kinks or facets along its curve. | Low segment count on the arch sweep | Raise the arch segment count or add a smooth bevel |
| 7 | P2 | front_corner, rear_side, architecture_close | The water and ground planes end in a hard straight cut against the sky with no far bank, reading as the edge of the world. | Finite context plane | Extend the canal and quays, or close the vista with a far bank or blocks |
| 8 | P2 | left_side | The foreground context block has very deep, unrailed balcony slabs; they now touch the facade but read crude at this distance. | Context balcony generator scale | Shrink the slab depth and add a simple parapet |
| 9 | P2 | quay_under, deck_edge | Only one pale bearing block can be read under each edge tie. The rest of the seat is in deep shadow, so the claimed three blocks per edge tie cannot be confirmed in the pixels. | Bearings sit under the soffit in shadow | Add a fill light or a quay_under angle that shows the whole seat line |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Plan and proportions | **deviates** (P1 #1: skew angle and east end orientation); span-to-width ratio and the axis angle to the image frame are close | top vs source top, aerial |
| Arch form and inclination | conforms. Two silver-grey box arches lean toward each other, with springings at the deck corners on chamfered plinths. Minor faceting (P2 #6) | front, left_side, right_side, hangers |
| Cross ties | conforms. Seven evenly spaced box ties over the central part of the span, parallel to the quays | top, aerial, rear_side |
| Hangers | conforms. Thin vertical hangers from each arch to the edge ties along the full span | hangers, facade_close, rear, top |
| Deck | conforms in section (thin fascia about 0.75-0.8 of the railing height, soffit low over the water); deviates in plan (P1 #1) | deck_edge, facade_close, rear |
| Cycle lane and footway | conforms. Red dashed cycle lane on the north side, pale footway on the south side, both ending at the deck ends | cycle_lane, top, architecture_close, arch_springing |
| Planter | conforms in position (raised concrete box, near full length, between lane and footway); finish P2 #2 | planter_divider, top |
| Railings | conforms (steel posts and bars) | glass_close, hangers |
| Quays and landings | **deviates**. Copings and walls are straight and vertical in the image, where the source has about 8-degree banks and an angled east pier (P1 #1). No landing edge (P2 #4). Brick quay wall height and bearing shelf conform | top, quay_under, deck_edge, rear |
| Water | conforms | rear, rear_north, top |
| Context | conforms as simplified context (brick apartment blocks, trees, lamps). World edge visible in elevated views (P2 #7) | front_corner, rear_side, left_side |
| Materials hierarchy | conforms. Silver-blue steel, pale footway, red lane, brick quays, concrete planter and shelf | all |

## 4. Camera validity

- No view has its target occluded so much that it becomes illegible, and none clips the asset in a way that invalidates it.
- rear (full north elevation) and rear_north (high three-quarter) now each hold the whole span, both deck ends, both abutment shelves and the near springings.
- front_corner hides the SW springing and the SE deck corner (P2 #5); aerial, top and rear_side cover them.
- The detail views (facade_close, deck_edge, quay_under) are legible. In quay_under the bearing seat is mostly in shadow (P2 #9).

## 5. Previous-version findings: resolved in the pixels?

**v002 P1 (1), the skew / overrun / plinth setbacks / landing line:** partly resolved.
- Resolved:
  - Both deck ends now land on the coping line with no overrun and no wedge (top crops, left_side, right_side).
  - The two plinths at each quay sit at the same setback, on a line parallel to the coping (top, left_side, right_side).
  - The ties run parallel to the quays (top).
  - The lane, footway and planter stop at the deck ends, with no lane surfacing on the quay beyond the railing line (architecture_close, arch_springing).
- Not resolved:
  - A distinct landing element is still missing (P2 #4).
  - The plan skew itself does not match the source top. The shear exaggerates the west skew and reverses the east end, which is now P1 #1.

**v002 P1 (2), rear framing:** resolved. rear and rear_north each show the whole span with both abutments, and rear shows the near springings.

**v002 P2s:**

| v002 P2 | status in v003 |
|---|---|
| Rock-like grasses | not resolved (P2 #2) |
| Dark cold palette | not resolved (P2 #3) |
| Floating balcony slabs | resolved as far as visible; slabs now touch the facades (crudeness P2 #8) |
| Aerial roof occluding the SE springing | resolved in aerial; similar occlusion now in front_corner (P2 #5) |
| Context corner in arch_springing | resolved |
| Landing surfacing beyond the railing line | resolved |
| Thin dark bearings | partly resolved; one pale block per edge tie is legible (P2 #9) |

**Earlier fixes that must still hold:**

| earlier fix | holds? |
|---|---|
| Seven evenly spaced box ties | holds |
| Thin edge-tie fascia (about 0.75-0.8 of the railing) with a low soffit | holds |
| Raised brick quays with wall showing | holds |
| Concrete bearing shelf with seat face on each quay wall | holds (quay_under, deck_edge, rear) |
| Silver-blue steel against the pale footway | holds |
| Front camera on the west landing left of or near the axis | holds |
| One chamfered plinth under each springing, with the edge ties ending in it | holds |
| Context, quays and canal extended beyond every frame | mostly holds; the world edge reads as a hard horizon in elevated views (P2 #7) |
