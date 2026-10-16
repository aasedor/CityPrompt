# Independent holistic review: clay-braced-frame-hospital v005 (RLASM v6.1)

Reviewer: independent (did not build the candidate). Evidence used: the three locked sources, all 18 renders opened at full resolution, the four phone boards, and zoomed crops written to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-hosp-v005-crops/`. I did not use builder metadata, counts or notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v004 storefront finding is fixed and the three-volume plan, the storey counts and every named identity element are present, but three clearly visible P1 defects remain. The exoskeleton bay rhythm is about twice as fine as the source. The atrium rises to the plant roof instead of stopping about one storey below the clinical parapet. Exoskeleton columns cut across brick-base windows on the ward block.

Counts: P0 = 0, P1 = 3, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, rear_side, right_side, rear, rear_north, braced_frame vs source top, oblique and front | **The exoskeleton bay rhythm is about twice as fine as the source.** In the source top, the braced south face of the north wing carries **6** X-bays across the full ward width (each about 1/6 of the ward width, about 0.19 of the clinical frontage). The oblique shows the same 6 large X-bays on that face and about 4 on the street face. The render carries **11** bays on the north wing (rear) and 11 on the east wing (right_side), each about 0.11 of the clinical frontage. As a result the frame reads as a dense, small-mesh lattice rather than the source's few bold X modules (board 1: oblique vs front_corner). | The column pitch is set at about half the source pitch (about 5–6 m instead of about 9–10 m at the render's scale). | Re-pitch the exoskeleton columns so the north wing's south face carries 6 bays and the street faces scale to match (about 6 on each long face, 2 on the east wing's south face as now). Keep the 5 tiers, ring beams and per-bay X-braces, then regenerate the braces and base columns from the new grid. |
| 2 | P1 | front, front_corner, aerial, architecture_close vs source front and oblique | **The atrium's silhouette and proportions differ from the source.** Both the source front and the oblique show the glass atrium topping out about **one storey below** the clinical block's main parapet, with the pale clinical wall and the ward frame visible above it, so it reads as a broad glass box. The render takes the atrium to the **plant-storey roof**, about one storey **above** the clinical parapet (front: atrium top y≈386 against a panel top of y≈430, with a storey of about 41 px). That is roughly 2 storeys too tall. It is also narrower (about 11% of the south frontage in the render top against about 14–16% in the source top), so it reads as a thin full-height slot, not a glass volume. | The atrium height is tied to the plant/roof datum ("full-height") instead of the source datum, and the slot is narrowed by the wide east wing. | Lower the atrium roof (glass roof and diagonal-net top edge) to about one storey below the clinical main parapet. Close the face above it with the clinical's pale panel return and the ward frame behind. Widen the atrium by about 30% (to about 15% of the frontage) by taking that width from the east wing, and keep the storefront, transom and canopy as built. |
| 3 | P1 | right_side (east street elevation), rear, rear_north, rear_side | **Exoskeleton columns cut across the brick-base windows.** The base window grid is not coordinated with the column grid. In right_side (zoom), a column runs down in front of an upper base window. In rear_north, columns stand in front of the edges of two window openings (x≈440–480 and x≈870–915 in the crop), and windows sit off-centre, butting against columns elsewhere. In the source front, the ward's brick base has its windows between the columns. | The base windows are laid out on their own module, separate from the column pitch. | Generate the ward base openings from the column grid: 1–2 windows centred in each bay, with brick piers behind every column. Re-check right_side, rear and rear_north for clear brick around each column. |
| 4 | P2 | front, architecture_close vs source front and oblique | The sign is a narrow dark strip with only a thin pale margin, inserted into the perforated field. The sources set it on a broad, solid pale concrete-panel field with no perforations. | The sign zone width is reduced to the panel strip. | Widen the solid pale-panel field around the sign to about 1.5–2× the sign width. |
| 5 | P2 | facade_close | The perforations read as flat mid-grey squares with no see-through darkness or depth. The strip glazing behind is only legible in the panel joints. | The holes are shallow insets or a mid-grey material, not cut-throughs over dark glass. | Make the perforations through-cuts (or darken the inset) so the glazing behind reads. |
| 6 | P2 | front_corner, braced_frame, roof_plant | The steel exoskeleton and the pale screens are almost the same light grey. In the source the steel is a distinctly darker mid-grey than the pale panels. | One shared palette value. | Shift the steel one step darker within the source palette. |
| 7 | P2 | top, front vs source top | The east wing runs flush to the south street beside the atrium. The source top shows pavement east of the atrium's south end, with the ward's east face stepping back. The sources are ambiguous here and the brief's L-plan is accepted. | The east wing's length is set to the full clinical depth. | Optionally stop the east wing about 1 bay short of the south building line. |
| 8 | P2 | top, aerial, rear_side | The roof flues cast three-way multi-light shadow fans that read as three-bladed "rotor" shapes on the ward roof in the plan view. | The lighting rig has several sun or area lights. | Use a single key light for plan views, or disable flue shadows. |
| 9 | P2 | interior | The interior is very dark (legible, but under-lit). | There is no fill light inside the atrium. | Add an interior fill light or raise the exposure for this view. |
| 10 | P2 | front, entrance_canopy vs source front | There are two revolving drums. The source front shows one revolving door between storefront panels. | The builder chose to show two. | Optional: keep one drum and a swing-door pair. |
| 11 | P2 | roof_canopy, front vs source top and front | The raised roof canopy is a plain flat slab. The source shows a framed, panelled or slatted surface. | Simplification. | Add a panel or slat grid to the canopy surface. |

(P2s are polish and do not block the verdict.)

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette | deviates: the atrium rises about 2 storeys above the source datum (F2), and the dense exoskeleton lattice changes how the ward reads (F1). Otherwise the overall stepped mass, the raised west canopy and the taller ward conform. | front, front_corner, aerial vs front, oblique |
| Storey counts | conforms: clinical has a 2-storey brick base, 5 storeys of screens and a recessed plant storey. The ward has a 2-storey brick base, 5 X-tiers and is taller than the clinical block. | front, left_side, right_side |
| Plan (three volumes) | conforms (with P2 F7): clinical block in the south-west, L-shaped ward to the north and east, glass atrium slot between them opening south with the canopy, streets south, west and east. | top, aerial vs source top |
| Clinical: brick base, large windows | conforms (window reveal depth modest but present: frames, sills) | brick_base, front |
| Clinical: perforated pale screens | conforms (P2 F5: perforation depth) | facade_close, front, left_side |
| Clinical: sign panel | conforms, with P2 F4 on the solid field | front, architecture_close |
| Clinical: louvre band, recessed plant storey | conforms | roof_canopy, front, left_side |
| Clinical: raised roof canopy frame over the west roof | conforms (P2 F11) | roof_canopy, left_side, top |
| Ward: exoskeleton bays | **deviates (P1 F1)**: 11 bays where the source has about 6 | rear, right_side, front_corner vs top, oblique |
| Ward: X-braces, ring beams | conforms per tier: full-height stack, ring beam at each tier, nodes, stand-off from the glazing with visible shadow depth | braced_frame, rear_north |
| Ward: brick base | present, but **deviates (P1 F3)**: columns clash with windows | right_side, rear_north |
| Atrium: diagonal mullion net | conforms (nodes, glass behind, depth) | glass_close, architecture_close |
| Atrium: roof and height | **deviates (P1 F2)**: the glass roof is present but sits at plant-roof height | front, front_corner, aerial |
| Entrance canopy: rods and posts | conforms: glass canopy hung on tension rods from the atrium, clinical and ward faces, thin front posts landing on the paving, storefront below | entrance_canopy, front, front_corner |
| Roof plant | conforms: ward roof boxes and flues, units on the clinical plant deck | roof_plant, top, aerial |
| Materials hierarchy | mostly conforms: red brick base, pale panels, grey glass, dark louvre and sign. Deviates slightly because steel and panels share one value (P2 F6). | front_corner, braced_frame |

## 4. Camera validity

No camera is invalid. All 18 views are legible, and none has an occluded target or a clipped asset.

- **front:** the building fills only about half the frame width, but it is fully legible.
- **top:** an orthographic nadir view against an oblique source top. That is acceptable for the plan role, apart from the shadow artefacts (F8).
- **interior:** dark, but the atrium walls, glazing and brick are legible (F9).
- **Detail views** (facade_close, architecture_close, glass_close, braced_frame, entrance_canopy, roof_canopy, roof_plant, brick_base, rear_north): each frames its named target.

## 5. Previous-version (v004) findings

| v004 finding | v005 status in pixels |
|---|---|
| P1: the atrium's diagonal mullion net ran down to the pavement across the main entrance, with the revolving doors behind the lattice. The source has a straight vertical-mullion storefront with a revolving door below the canopy line. | **RESOLVED.** In entrance_canopy and the front zoom, everything below the canopy line is a storefront: straight vertical mullions, a door-head transom, and two glass revolving drums set in the facade line between storefront glass panels. A horizontal steel transom runs at the canopy line, and the diagonal net starts above it. No diagonal members reach the pavement or cross the doors. |
