# Independent holistic review — clay-campus-shed-office v002 (RLASM v6.1)

Reviewer: independent, no relationship with the builder. All 18 renders, the 4 phone boards and the three locked sources were opened at full resolution; the regions cited below were additionally inspected at 2x-5x crops of the same pixels. Builder notes, counts and hashes were not used as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the massing, sawtooth rhythm, terrace, dock and corner entrance all read as the source building, but the X-braces physically pass through the dock canopy slab, a portal column bisects the north-wall door, and the hero south-west corner is wrong against both street sources (west-face X-brace bay missing, canopy wrapped onto the south face, X-braces on every south bay instead of end-bay X + tie-rods).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | architecture_close, terrace_roof, facade_close, dock_contact | The X-brace bars are drawn across the TOP surface of the dock canopy (architecture_close: the "\" bar runs from the column head down over the dark canopy top to its front edge; terrace_roof: three brace ends lie on the canopy top mid-depth) and the same bars emerge BELOW the soffit (dock_contact: diagonal stubs hang under the canopy at every column, landing on the spandrel beam). The canopy root is flush to the wall, so the brace bars pierce the slab — intersecting parts. | Brace lower chord is set at the spandrel beam, while the canopy slab (~0.8 m thick) is attached ~1 m above the spandrel; braces are not clipped to the canopy top. | Move the canopy root down to the spandrel/brace-bottom level (as in the sources, where the braces terminate exactly at the canopy line), or terminate the brace members at the canopy top plane; thin the slab to a ~0.3 m steel deck so nothing passes through it. |
| 2 | P0 | rear, rear_side | The north-wall personnel door (rear x≈705-735) is split by the portal column: the light-grey column runs straight down through the middle of the dark door opening to a beige threshold. A door you cannot walk through. | Door placed on a bay grid line instead of inside a bay. | Offset the door half a bay into the adjacent panel (clear of the column), keep the threshold and a visible reveal. |
| 3 | P1 | front_corner, left_side, entrance_corner vs sources/front.png + sources/oblique.jpg | The source west (street) face of the two-storey corner block has TWO bays separated by a full-height galvanised column: an entrance bay (upper grid window; CAMPUS HQ canopy and glazed doors below) and a corner bay (upper X-brace; glazing under the continuing canopy below). The render has ONE wide bay with a single upper window and no X-brace anywhere on the west elevation; the next sawtooth bay north of it has only a ground-floor window (upper window absent in all three views), where the source shows a full two-storey fenestrated bay. | Office box modelled one bay deep on the west with the brace assembly only on the south face. | Split the west face of the box into two bays with a column; add the X-brace to the upper corner bay; keep the window above the entrance bay; add the missing upper window to the first sawtooth bay. |
| 4 | P1 | entrance_corner, front_corner, facade_close, interior, top vs sources/front.png + oblique.jpg | The entrance canopy wraps around the corner column and continues along the south face over the big ground-floor window. In both street sources the canopy runs along the west face only and stops at the corner column; the south corner bay's big grid window has no canopy. The two render canopy slabs also meet at the corner with a stepped notch (facade_close crop, entrance_corner x≈1000-1080). | Canopy built as an L around the corner at two slightly different heights. | Delete the south-face canopy leg; keep one west-face canopy spanning the two west bays and ending flush at the corner column. |
| 5 | P1 | front, front_corner, aerial, facade_close vs sources/front.png, oblique.jpg, top.jpg | Render has an X-brace in all six south bays and the dock canopy is a plain cantilever. The sources show X-braces only in the corner bay and the east-end bay; in the canopy bays the wall panels are plain and thin tie-rods run from each column head down to the outer edge of the dock canopy (visible in front.png, oblique.jpg and as thin lines perpendicular to the wall in top.jpg). | Brace rhythm generalised as "X every bay"; hanger rods omitted. | Keep X in bays 1 and 6, replace bays 2-5 with plain panels, add a ~40 mm tie-rod per column from column head to canopy edge. |
| 6 | P2 | terrace_roof, top | The round duct from the rooftop unit ends on a glass pane of monitor 1's clerestory (dark collar on the glass). Source ducts enter the monitor's solid base. | Duct end placed at the glazing line. | End the duct in a solid louvre panel or spandrel below the glass. |
| 7 | P2 | aerial, front, top vs sources/top.jpg, oblique.jpg | One dock stair (east end). The sources show a second stair mid-dock and the ramp; also no dock bumpers. | Simplified dock. | Add the mid-dock stair with rail. |
| 8 | P2 | rear, rear_side | North-wall fenestration alternates upper-only / lower-only windows per bay with no logic; coherent with the grammar otherwise. | Arbitrary placement. | Use one pattern (upper + lower per bay, as the west gable does). |
| 9 | P2 | clerestory_close, sawtooth_contact | Clerestory glass sits directly on the lower monitor roof with no curb/sill; monitor roof edges have no gutter or fascia depth. Clay-acceptable but reads flat. | Glass plane meets roof plane. | Add a 150 mm curb and a fascia return. |
| 10 | P2 | interior (camera) | The "interior" view is an exterior shot of the south corner window; the interior is only faintly legible through frosted glass (two desks). Not invalid, but the target barely reads. | Camera outside, glass too diffuse. | Use the stairs camera for interior evidence or reduce the glass roughness. |
| 11 | P2 | front, facade_close, dock_contact | Dock and entrance canopies are ~0.8 m thick slabs; the sources show thin (~0.3 m) steel canopies with a visible edge profile. | Slab thickness. | Thin to 0.3 m with a dark soffit (partly resolved by fix #1). |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (corner-lot two-storey box + four sawtooth monitors behind, monitor 1 slightly taller next to the terrace) | conforms | front_corner, aerial, left_side vs front.png, oblique.jpg |
| Storey count (two storeys in the box and gable bays) | conforms | front, left_side, right_side vs front.png |
| Bay rhythm — south face (6 bays, dock canopy over 5) | conforms | front, top vs top.jpg |
| Bay rhythm — west face of office box (2 bays with column) | deviates (finding 3) | left_side, entrance_corner vs front.png, oblique.jpg |
| Entrance and canopy (corner entrance under low canopy, west face only) | deviates (findings 3, 4) | entrance_corner, front_corner vs front.png, oblique.jpg |
| Dock and ramp (raised dock, roller doors, ramp from the west with rail, stair at the east) | conforms (minor: one stair, finding 7) | front, aerial, dock_contact vs front.png, oblique.jpg, top.jpg |
| Portal frame and braces (galvanised columns, X in end bays, tie-rods to canopy) | deviates (findings 1, 5) | front, facade_close, architecture_close vs front.png, oblique.jpg, top.jpg |
| Sawtooth monitors and clerestories (four E-W monitors, vertical south glazing, roof sloping north, two rows of panes) | conforms | aerial, top, sawtooth_contact, clerestory_close vs oblique.jpg, top.jpg |
| Terrace and rooftop plant (flat roof along the south edge, rail on S/E/W edges, unit + duct at the west end) | conforms (duct end, finding 6) | terrace_roof, top, aerial vs top.jpg, oblique.jpg |
| Gable ends — west | conforms in profile; fenestration deviates in first bay (finding 3) | left_side, sawtooth_contact vs front.png |
| Gable ends — east, north wall | not visible in sources; coherent with grammar except finding 2 and finding 8 | right_side, rear, rear_side |
| Materials hierarchy (charcoal corrugated cladding, galvanised frame, dark glazing frames, concrete plinth/dock, grey roof deck) | conforms (clay palette) | facade_close, dock_contact, glass_close vs front.png |

## 4. Camera validity

- All 18 renders have the asset fully inside the frame with the intended target legible; no view is occluded or clipped.
- `front`: the low-poly tree sits in front of the west-face canopy end but does not occlude the south elevation; valid.
- `front_corner`: distant (building ~55% of frame width) but all elements legible; valid.
- `interior`: valid but weak — exterior camera, target only faintly visible through frosted glass (finding 10). `stairs` carries the interior evidence.
- `top`: true nadir, so the vertical clerestory glazing is necessarily invisible; compared against top.jpg on footprint, roof bands, terrace, unit and canopy only.
