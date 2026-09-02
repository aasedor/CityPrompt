# Inglewood Victorian Brick clay-first pilot

This is City Prompt's first architectural-clay building authored directly from
an exact catalogue source lock rather than derived from an already finished
RLASM model. It proves that the clay workflow can retain the architectural
parts the image model must not invent, while omitting final textures and PBR
material authorship.

Status: `BUILDER_VERIFIED_FOR_USER_VISUAL_REVIEW`. This is a saved candidate,
not a keeper and not a live runtime-catalogue entry.

| Front | Front corner |
| --- | --- |
| ![Front architectural-clay view](01-front.png) | ![Front-corner architectural-clay view](02-front-corner.png) |

| Aerial | True top |
| --- | --- |
| ![Aerial architectural-clay view](03-aerial.png) | ![True-top architectural-clay proof](08-true-top.png) |

| Left | Right |
| --- | --- |
| ![Left-side architectural-clay view](04-left.png) | ![Right-side architectural-clay view](05-right.png) |

| Rear | Rear corner |
| --- | --- |
| ![Rear architectural-clay view](06-rear.png) | ![Rear-corner architectural-clay view](07-rear-corner.png) |

| Entrance detail | Facade detail | Roof detail |
| --- | --- | --- |
| ![Monumental entrance detail](09-entrance-close.png) | ![Window and cornice detail](10-facade-close.png) | ![Closed roof and equipment detail](11-roof-close.png) |

## Exact source lock

Only one catalogue identity was used: `inglewood_victorian_brick`, variant 0
of `inglewood-heritage-brick-commercial`.

| View | Repository source | SHA-256 |
| --- | --- | --- |
| Front | [variant_0.png](../../../../frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0.png) | `e5122ce4dc9277ade776a994de8cf6eb173a3458657e3d2c5c45f3edab4287ab` |
| Oblique aerial | [variant_0_angle_60.jpg](../../../../frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0_angle_60.jpg) | `26d1413d8434fcdbcdfaab8dc151cd346daab3fda486738b04fa067eca7747b9` |
| Near true top | [variant_0_angle_90.jpg](../../../../frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0_angle_90.jpg) | `67b91bf68860537f9fb0f2022e506f025fc9ed5ceaada2e30a04ae468ed2fa7e` |

The rear is not visible in the locked triplet. Its service-door and window
schedule is therefore a conservative inference, recorded as inference rather
than source fact. The flat roof, parapet, short gabled entry cap, and equipment
types are visible in the aerial evidence.

## Result

- Measured envelope: 20.4 m wide by 24.0 m deep, 10.35 m parapet, and
  13.25 m gable height.
- Native grammar: three storefront/upper-window bays on each side of a fixed
  central entry, with six repeatable depth bays.
- Authoring source: 553 named modular mesh objects, 39,924 polygons, and
  518,342 bytes.
- Runtime GLB: eight semantic-role mesh nodes, 39,924 polygons, and
  6,193,032 bytes.
- Payload: eight flat semantic materials, zero images, and zero textures.
- Grounding: bottom-centre contract retained at `z = 0`.
- Round-trip: Blender 5.2 reimported all eight semantic meshes with the same
  bounds and no images.

No percentage reduction against a full RLASM version is claimed because this
is a clay-first build; a fully textured version of this exact geometry does
not yet exist. The relevant runtime gain is already concrete: the editable
source's 553 objects are collapsed to eight mesh nodes/draw-role groups.

## LEGO scaling grammar

The central monumental arch, gable, corner piers, cornice returns, and rear
service entry are fixed modules. Width changes insert or remove complete
storefront plus upper-window bay pairs symmetrically. Depth changes insert or
remove complete side/roof bays before the fixed rear module. The compiler must
never stretch the arch, gable, windows, or ornamental bands.

Only the native pilot was generated in this bounded run. Small and large
discrete variants should be generated after human visual approval of this
module and its bay grammar.

## RLASM scope retained

The build retains the RLASM v6.1 source lock, camera-first measurement,
complete envelope, recessed openings, front/side/rear ownership, closed roof,
ground contacts, occupied depth, semantic material ownership, and full QA
roster. It deliberately stops before source-specific texture, UV, weathering,
and final optical-polish work.

The deterministic builder is
`tools/archetype_compiler/build_inglewood_heritage_clay.py`. Machine-readable
provenance and measurements are in `BUILD_RESULT.json`, and the candidate is
indexed in `tools/archetype_compiler/architectural_clay_catalogue.json`.

The authoring Blend, runtime GLB, and complete build report remain outside Git
at `artifacts/inglewood-heritage-clay-first-2026-09-01/`. The reviewed images
above are the intentional Git LFS deliverables.
