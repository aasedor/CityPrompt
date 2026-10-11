# Independent RLASM v6.1 holistic review: courtyard v008

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** There is no P0, and both v007 P0s are gone from the pixels. One P1 remains: the set-back penthouses and their terraces are finished in neutral tan and grey instead of the source's cedar, under a thin lid instead of the deep dark canopy, so a named identity element reads as a different material.

**Counts: P0 = 0, P1 = 1, P2 = 6**

Inputs: the three locked sources, all 18 renders at full resolution (1440x1080) and the 4 phone boards. I did not read any build code, reports or notes.

### Wall-material ruling (sampled from source pixels, median RGB)

| Sample | Location | Median RGB |
|---|---|---|
| Oblique, east street face of the east wing, sunlit | (940-1010, 300-500) | 142,122,95 |
| Oblique, east street face, lower | (880-930, 420-620) | 139,116,87 |
| Oblique, east street face, upper | (960-1000, 250-290) | 139,122,103 |
| Oblique, sunlit concrete stair wall (reference) | (500-540, 600-680) | 171,166,153 |
| Front, east street face (grazing sun) | (900-1000, 180-500) | 182,171,149 |
| Front, sunlit concrete stair wall (reference) | (445-500, 520-600) | 162,162,151 |
| Oblique, south face of the east wing, ribbed | (770-800, 560-640) | 34,36,39 |
| Front, south face of the east wing | (650-780, 300-500) | 37,40,40 |
| Front, south face of the west wing | (60-280, 260-500) | 60,68,63 |
| Oblique, west wing's courtyard (east-facing) face, sunlit columns x 450-490 | (450-490, 250-470) | 172,141,107 down to 104,85,61 |
| Oblique, deeper courtyard / rear bar in shade (x 500-550) | (500-550, 250-470) | 25-55 |

- Under the same sun, the east-facing street wall is about 0.82x as bright as sunlit concrete. Near-black ribbed metal (the south faces sample at 34-37) cannot reach that value under any lighting.
- The textures differ too. Zoomed crops of both sources show the east faces as smooth panels with widely spaced vertical joints and tall narrow punched windows. The dark, densely ribbed metal stops at the south ends and turns the corner only as a narrow return.

**Ruling:** I agree with the v005/v006 reading (warm taupe panel on the east-facing walls, about RGB 140,120,95 in sun; near-black ribbed metal only on the south faces). I reject the v007 reading that the east street elevation and the courtyard faces must be dark ribbed metal. The brief's phrase "U-plan in dark ribbed metal" holds for the south (street-front) faces and the wing ends. It is contradicted for the east-facing walls by the locked pixels. The render's tan east face (167,156,142 in right_side; 164,152,138 in aerial) is in the right family. It is slightly paler and greyer than the source taupe, which is P2 at most.

## 2. Findings table

| # | Severity | View(s) | Symptom (what the pixels show) | Likely cause | Finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | front (penthouse bands x 320-640 / 890-1120, y 352-415); front_corner (x 580-1080, y 360-560); aerial (x 400-850, y 400-640); roof_terrace (x 560-1160, y 420-700); top (x 310-1130, y 755-860) | The set-back penthouse storeys are neutral tan (render 139,125,109). The source penthouse walls are cedar (front source (790-815, 165-175) = 117,69,41) under a dark, deeply cantilevered roof canopy with a cedar soffit (soffit 39,53,67 dark edge; the slab projects well over the terrace). The render's lid is a thin slab with a short overhang, and its top shows a white/light-grey edge strip in the aerial, top and roof_terrace views. The terrace decks render grey (161,158,153). The source top view shows cedar decking (300-560, 565-600 = 173,134,104). Taken together, the penthouses read as a tan box with a pale lid, not the cedar pavilion under a dark canopy that identifies the source. | The penthouse wall material was mapped to the east-wall taupe instead of the cedar used in the balcony reveals. The canopy depth and the deck finish were never matched to the source. | On the south and courtyard faces of both wing penthouses, switch the wall material to the existing cedar used in the balcony reveals (keep the flush east-face top storey taupe). Deepen the wing roof slab's south cantilever to roughly 70-80% of the terrace depth, with a dark fascia and a cedar soffit. Give both terrace decks the cedar deck colour. Re-render front, front_corner, aerial, top and roof_terrace. |
| 2 | P2 | facade_close, balcony_close, front, front_corner | The south "ribbed" cladding is broad standing-seam panels (about 2 seams per window bay; rear_lane is denser). At whole-building distance it reads as smooth mid-grey (91,94,97). The source shows dense fine ribs in near-black (shaded 27-47). | Coarse seam pitch and a light base colour | Halve the seam/rib pitch on the south faces, and darken the base colour to about 50-60 in render space. |
| 3 | P2 | right_side, architecture_close, aerial | The east street face has 6 paired, near-square casements per floor (right_side shows 47x68 px). The source shows about 8-9 tall, narrow, near floor-height windows per floor, partly paired. | Window module reused from another facade | Use taller, narrower single and paired windows on the east face, about 8 per floor. |
| 4 | P2 | courtyard_stair, front, top | The stair is a plain concrete flight centred in the opening. The source stair sits toward the east, with cedar seat-steps beside it (top source x 725-805) and a raised planted patio to the west. | Simplified stair layout | Shift the stair east, add cedar bench treads on its east side, and put a planted raised patio on the west side. |
| 5 | P2 | top, rear_side | The footprint is a plain rectangle. The source top shows the rear bar projecting north between notched NW and NE corners (source top x 440-920, y 70-130). | Simplified north outline | Add the rear-bar projection and the corner notches. |
| 6 | P2 | facade_close, balcony_close, retail_corner, rear_lane | Rows of short vertical tick marks under each window row and under the balcony slabs read as stray dashes. | Fastener/drip detail at the wrong scale | Remove them or merge them into a continuous drip flashing. |
| 7 | P2 | left_side | The west party wall is a blank dark mass with a single column of slot windows. It is not shown in any source; it is coherent but monotonous. | Party-wall treatment | Optional: add faint panel jointing to match the rear. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette | Conforms. Two wings with a front terrace step, a continuous rear bar, a lower courtyard gap and rooftop units, matching oblique and front. The north notch is missing (P2 #5). | front, front_corner, aerial vs front, oblique |
| Storey count | Conforms. Retail base, plus 3 residential storeys, plus a set-back penthouse on the wings. The rear bar has 4 floors above the courtyard, as in the source. The east face shows 4 window rows above retail, as in the source. | front, right_side vs front, oblique |
| U-plan and courtyard | Conforms. Courtyard width is about 32% of the frontage (source 34%) and depth about 68% (source 76%). The west wing is wider than the east wing, as in the source. The courtyard is raised one storey on the retail podium and opens south. | top vs top source, courtyard_stair |
| Street stair | Conforms in identity: a wide concrete stair from the sidewalk to the courtyard deck, with cheek walls and handrails. Its layout deviates (P2 #4). | courtyard_stair, front |
| Balconies and cedar reveals | Conforms. Recessed balcony stacks on the courtyard side of each wing front, with cedar-lined reveals (76,52,24), glass balustrades, slab edges and visible depth and returns. The rear bar has cedar walls with continuous glass balconies. | balcony_close, front, courtyard_stair |
| Window rhythm | South faces conform. The east face deviates (P2 #3). | facade_close, right_side |
| Penthouses and terraces | Deviates (P1 #1). The geometry and set-back terraces are present, but the walls are not cedar, the canopy is thin and the decks are grey. | front, roof_terrace, top |
| Retail base | Conforms. Dark base with full-height black-framed storefronts on the south, wrapping the SE corner onto the east face, plus a canopy band. | retail_corner, cladding_contact, front |
| Materials hierarchy | Conforms in the main: dark south fronts, taupe east and courtyard walls, cedar reveals, grey membrane roofs. The penthouse cedar is missing (P1 #1), and the dark value is too light (P2 #2). | all whole-envelope views |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every view is legible. The interior view is dim but legible, showing windows, floor and furniture contact. In glass_close the frames and the reflection/depth read correctly. No view frames empty space or cuts through the asset.

## 5. Prior-version (v007) findings, judged from v008 pixels

| v007 finding | Status | Evidence |
|---|---|---|
| P0: rooftop mechanical units on the wings hover above the membrane with detached shadows | **Resolved** | In the roof_terrace crop (x 180-1160, y 150-400), the aerial and the rear view, every unit base meets the membrane with an attached contact shadow and no gap. |
| P0: east street elevation above retail is flat tan instead of dark ribbed metal | **Resolved (finding withdrawn)** | v008 is still tan on the east face (167,156,142). The source pixels show a taupe panel there (139-142,116-122,87-103 in sun, about 0.82x sunlit concrete) with a different texture from the ribbed south faces. The tan conforms to the source. Only a minor hue and window-rhythm polish remains (P2 #3). |
| P1: courtyard-facing walls tan with punched windows instead of dark ribbed metal | **Resolved (finding withdrawn)** | The source's west-wing courtyard face samples as sunlit taupe (172,141,107) with punched windows and cedar strips. The darker values deeper in the courtyard are shade and the rear bar's dark frames. v008 shows tan wing courtyard faces with punched windows, cedar-lined recessed balconies, and a cedar/glass rear bar. This is consistent with the source. |
| The six v007 P2s were not itemised in the brief | Not individually verifiable | The remaining polish items are listed above as P2 #2 to #7. |
