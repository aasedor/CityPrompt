# Independent holistic review: oldmtl v001 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate.
Evidence I used: `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`, all 18 PNGs in `renders/` at full resolution, and the four phone boards. I also made zoomed crops of the sources and renders, in a separate new folder outside the candidate. I did not use any metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plan, the range storeys, the dome group and the north porch are good, but two named identity elements are a storey short of the locked source pixels. The Tuscan portico is not a giant order rising to the eave, and the east end pavilion has no attic storey and a wrong tier hierarchy.

Counts: P0 = 0, P1 = 2, P2 = 8

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | portico, front, front_corner, aerial (vs oblique, front source) | **The portico is about one storey too short.** In the oblique source (portico at x≈250–370) and the front source (x≈20–130), the Tuscan columns are a giant order. They rise from the podium through all three storeys, the entablature sits at the range eave/cornice level, and the whole pediment stands above the eave line against the dome-block attic. In the render (portico.png), the entablature sits at the second-floor sill band (y≈400–490) and the columns cover only the ground and first floors. The pediment hides the second-floor windows, and its apex (y≈210) barely reaches the range eave (y≈235). The front render shows the same thing: the pediment apex is at or below the range cornice, whereas in the source it clearly rises above. | Column height was set to two floor heights, not to the eave height of the range, so the entablature was placed at the second-floor band. | Set the column shaft plus capital so that the top of the entablature equals the range eave cornice height. Keep the stepped podium. Raise the pediment so that its base sits on that entablature and its apex rises above the slate roof, as in the oblique. Re-seat the portico roof against the range/dome-block wall, and re-render the portico, front, front_corner and aerial views. |
| 2 | P1 | front, front_corner, end_pavilion_arches, right_side, east_door (vs front, oblique) | **The end pavilion has the wrong tier hierarchy and no attic storey.** In both the front and oblique sources, the pavilion has two tall round-arched tiers. The ground tier has iron grilles, plus an arched door on the south face; the first tier is the tallest and carries the iron balconettes. Above them is a main cornice that continues the range eave. Above that cornice the pavilion rises **one attic storey above the range eave**, with **rectangular** six-over-six windows on the long faces, a top cornice, and the eaves balustrade with a separate low hipped slate roof and skylight behind it. The east pediment springs from the main cornice, and its tympanum holds a **round-arched fanlit window** (front source x≈950,y≈40; oblique x≈958,y≈600). The render instead has three arched tiers of about equal height packed into the range height, with the ground tier tallest. The pavilion cornice and balustrade sit level with the range eave, the pediment sits on the top cornice, and the tympanum has a round oculus. The range roof runs straight into the pediment, with no separate pavilion roof. Two of the arched tiers and the balconettes do conform. | The pavilion was modelled as a re-skin of the three range storeys, following the brief's wording ("arches on all three floors", "blind oculus"), not the source pixels. The source shows an attic above the eave. | Rebuild the pavilion section only. (a) Use two arched tiers whose heights match the range's three floors, with the first-floor balconette tier as the tallest, ground-tier grilles and the south-face arched door. (b) Add the main cornice continuous with the range eave. (c) Add an attic storey above it with rectangular six-over-six windows on the south/north faces, then the top cornice and the balustrade with pedestals. (d) Give the pavilion a separate low hipped slate roof inside the balustrade, with a chimney and skylight. (e) Spring the east pediment from the main cornice, with an arched fanlit tympanum window. If the brief's oculus is deliberate, record that as a source exception. Keep the east door and steps. |
| 3 | P2 | front_corner, aerial, portico, dome_drum | In the source, the portico roof and the dome-block attic deck are silver tin. The render uses dark slate on the portico roof, and the dome is only slightly lighter than the walls (sampled about 148 against about 120). The tin/slate/limestone hierarchy is weak. | Roof material assigned by roof type, not by source. | Give the portico roof, the attic deck and the dome a light-silver tin clay tone that is distinct from the limestone. |
| 4 | P2 | dome_drum, rear_north | The source drum is taller relative to the dome, with a plain stone base course under the arched windows. In the render, the windows start almost at the drum base, and the dome-to-drum ratio is about 1.1 against about 0.9 in the source. The dome has 16 heavy ribs, whereas the source dome has fine, closely spaced tin seams. | Simplified drum section; rib count was chosen for readability. | Add a plain base course under the windows (about 1/4 of drum height) and lengthen the drum slightly. Use 24–32 lighter ribs. |
| 5 | P2 | portico | The frieze "triglyphs" read as plain hanging blocks (mutules or dentils). There is a dark open slot along the raking cornice under the portico roof slab. The tympanum oculus differs from the carved ornament in the source pediment. | Triglyphs modelled as plain boxes; the roof slab is offset from the raking cornice. | Score the triglyphs with two vertical grooves and add metopes. Close the gap between the roof slab and the raking cornice. |
| 6 | P2 | long_facade, front | The pilaster strips are plain bands. In the source they carry small capitals or imposts under the cornice. | Simplified pilaster profile. | Add a shallow capital block under the eave cornice on each strip. |
| 7 | P2 | top, aerial, west_range, long_facade | The trees are faceted icosahedral blobs on Y-fork trunks, and they read as stylised. The source top shows 3 trees on the north sidewalk in front of the west range, plus a cobbled square with 5 more trees beyond the north street. The render has 2+2 trees and no north square. The squares are a flat tone with no edge kerb or paving distinction. | Generic low-poly tree asset; site trimmed to one block. | Use rounder, multi-lobed crowns with a single trunk. Match the north tree count, and optionally add the north square. Give the cobbled squares a slightly different tone or a kerb line. |
| 8 | P2 | top, rear_north | The north porch spans about 65% of the dome-block width; the source top shows about 85%. The small east annex on the dome block (source top x≈710–760, y≈390–510) is omitted. | Porch width set from bay count, not from the plan. | Widen the porch to about 85% of the block width. Add the low annex if the plan is to follow the top view strictly. |
| 9 | P2 | front, left_side, right_side, rear | In the front view, the street and ground plane stop at x≈160 and leave an empty grey void. In the side and rear views, the building fills only about 25–30% of the frame width. | Site plane cropped to the block; the cameras are far out. | Extend the street and ground plane past the camera frustum. Move the side and rear cameras in so the building fills about 50–60% of the frame. |
| 10 | P2 | (coverage) | The brief's view list names `facade_close`, `architecture_close` and `glass_close`, but no such renders exist; the set holds 18 files, which matches the brief's "18 views". Those roles are covered in practice by long_facade, end_pavilion_arches, balconettes and interior, where glazing depth and reveals are visible. | The view list and the render set are out of sync. | Either render the three named views or correct the brief's list. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | deviates: the overall long hall with offset ranges, dome block and dome reads correctly, but the pavilion lacks its attic rise above the eave and the portico pediment does not rise above the roof (findings #1, #2) | front, front_corner, aerial vs oblique/front |
| Storey count | conforms for the ranges and dome block (3 storeys over a low basement); deviates for the end pavilion (2 arched tiers + attic in source; 3 arched tiers in render, finding #2) | long_facade, front, end_pavilion_arches |
| Plan (offset ranges, dome block, portico, porch) | conforms: west range in line with the square dome block; east range stepped south by a full depth and starting at the dome-block west edge; portico at the west end of the south face of the east range; porch on the north of the dome block. Proportions match the top view to within about 5%. Porch slightly narrow (P2 #8) | top vs top, aerial |
| Limestone coursing | conforms (fine horizontal coursing lines are visible on all walls in the close views) | portico, balconettes, long_facade |
| Window tiers: vents | conforms (barred basement vents on the plinth throughout) | long_facade, east_door |
| Window tiers: three tiers of sashes | conforms (six-over-six sashes with stone sills and flat lintel caps, three tiers, regular bays) | long_facade, west_range |
| Window tiers: pavilion arches and fanlights | deviates: radial fanlights, keystones and arches are present, but the tier heights and count are wrong, there is no attic of rectangular windows, there are no ground-floor grilles, and the south arched door is missing (#2) | end_pavilion_arches, balconettes, front |
| Pilaster strips | conforms (capitals missing: P2 #6) | long_facade, front |
| Plinth | conforms | long_facade, east_door |
| Sill bands | conforms | long_facade, west_range |
| Eave cornice | conforms (modillioned) | long_facade, portico, roofs_dormers |
| End pavilion: balconettes | conforms (iron balconettes on the first floor, on stone slabs, in contact with the wall) | balconettes, east_door |
| End pavilion: balustrade | partial: present on both long sides, but at the range eave level, not above an attic storey (#2) | front, front_corner, rear_side |
| End pavilion: pediment | deviates: full-width, but springs from the top cornice, not from the main cornice (#2) | right_side, front_corner |
| End pavilion: oculus | deviates from the source pixels (an arched fanlit window); matches the brief text (#2) | right_side vs front/oblique |
| End pavilion: east door and hood | conforms (corniced square door on consoles with a transom and steps, in the middle of the east face) | east_door, right_side |
| Portico: podium and steps | conforms | portico |
| Portico: columns | deviates: four Tuscan columns, but two storeys tall, not a giant order to the eave (#1) | portico, front |
| Portico: entablature | deviates: at the second-floor band, not at the eave (#1); triglyphs simplified (P2 #5) | portico |
| Portico: pediment | deviates: does not rise above the roof line (#1); oculus present | portico, front |
| Attic: panels | conforms (sunk panels) | dome_drum, rear_north |
| Attic: pedestals and urns | conforms (corner pedestals with urns) | dome_drum, rear_north |
| Drum: arched windows | conforms (about 16 round-arched windows) | dome_drum |
| Drum: engaged columns | conforms | dome_drum |
| Drum: entablature | conforms; base course and proportion are P2 #4 | dome_drum |
| Dome: ribs and profile | conforms (ribbed, near-hemispherical); rib density and drum ratio are P2 #4 | dome_drum, rear |
| Lantern, cupola and cross | conforms (open columned lantern, cupola, cross) | dome_drum |
| Roofs: hips | conforms (low hipped slate on both ranges) | west_range, top, front_corner |
| Roofs: gable ends | deviates: the east end runs into the pediment, with no separate pavilion hip (#2) | front_corner |
| Roofs: chimneys | conforms (stone chimneys) | roofs_dormers, west_range |
| Roofs: vent dormers | conforms (5 small vent dormers on the north court slope of the east range) | roofs_dormers, top |
| Roofs: skylight | conforms on the west range; the pavilion skylight is missing (#2) | west_range, top |
| North porch | conforms: a flat-roofed porch of three arches with a balustrade, steps and doors in the central arch, with visible depth (slightly narrow, P2 #8) | rear_north, rear |
| Streets, squares and trees | conforms in substance: streets on four sides, sidewalks, a south-west square with trees, and trees on the south and north sidewalks. The north square and tree counts are P2 #7 | top, aerial, west_range |
| Materials hierarchy | partial: limestone clay and dark slate read correctly; tin roofs (portico, attic deck, dome) are not distinguished (P2 #3) | front_corner, portico, dome_drum |

## 4. Camera validity

- **All 18 renders are valid.** No target is occluded and nothing is illegible.
- **front:** the dome is largely hidden behind the near pavilion, showing only the lantern and the top of the dome. The brief accepts this as a consequence of the top-view plan, so it is not a finding. The east door is cropped at the right edge, consistent with the source, which also crops the east face.
- **left_side, right_side, rear:** these are legible but distant; the building fills only about 25–30% of the frame (P2 #9).
- **interior:** a legible view out through a six-over-six window with a visible reveal.
- **Three views named in the brief's list are missing:** `facade_close`, `architecture_close` and `glass_close` were not rendered (P2 #10). The total of 18 matches the brief's count, and the other close views cover those roles.

## 5. Previous-version findings

This is the first version (v001), so there are no previous-version findings to carry forward or close.
