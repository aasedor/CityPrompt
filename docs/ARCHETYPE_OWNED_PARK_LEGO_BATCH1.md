# Archetype-Owned Park LEGO — Batch 1

## Decision under test

Replace AI park draping with an archetype-owned assembly when, and only when,
the selected catalog variant has a reviewed skin, a metric module set, an
authored placement program, and a receiving-envelope contract. AI rendering
may finish a compiled scene, but it is not the source of the park layout.

The pilot deliberately leaves the old drape path available for archetypes that
have not passed this contract. A global drape removal would make unsupported
parks generic or empty.

## Executable cohort

| Family | Exact catalog identity | Fixed program | Authored systems |
| --- | --- | ---: | --- |
| `park_skate_archetype_v0` | `skate_park/skate_park_v0` | 40 × 30 m | two bowls, hubba/stairs, rail, ledge, bench |
| `park_inclusive_playground_v0` | `inclusive_playground/inclusive_playground_v0` | 50 × 40 m | five safety islands, five accessible-play GLBs, benches |
| `park_dog_archetype_v0` | `dog_park/dog_park_v0` | 80 × 50 m | five exercise pens, timber fence, gate, three shelters, boulders |
| `park_splash_pad_v0` | `splash_pad_area/splash_pad_area_v0` | 30 × 25 m | dry/wet pads, water tower, spray arch, five jets, fence |
| `park_community_garden_v0` | `community_garden/community_garden_v0` | 50 × 50 m | 18 beds, greenhouse, trellis, compost, fence |

Every family owns a different appearance-kit ID and skin directory. These are
not generic themes. The live renderer uses the GLBs at their Blender-authored
metric scale and instances prototype modules at the reference-derived
locations. People and large buildings are excluded.

## One-park test protocol

1. Keep exactly one `green_space` zone in the project.
2. Give it the exact catalog archetype and v0 variant.
3. Size and rotate a receiving polygon for the authored program; never stretch
   the program to the polygon.
4. Run Generate to 3D without the master planner.
5. Confirm the persisted recipe family, variant, appearance kit, and target.
6. Review a 30-degree oblique live view for placement, grade contact, material
   identity, missing modules, and generic prop leakage.
7. Run the free Direct 3D capture check before a paid image call.
8. Save one photorealistic render, then replace the single zone with the next
   archetype. Never test overlapping parks.

## Batch-1 implementation

- General fixed-program containment works for rotated and irregular polygons.
- Backend capability planning rejects undersized or concave receivers.
- Frontend recipe resolution requires the exact family/archetype/variant/skin
  identity and a current recipe hash.
- Exact families bypass paid AI ground draping, generic park scatter, and
  generic microdetail.
- The renderer retains a site-shaped grass buffer while the authored program
  remains fixed at scale 1.0.
- Direct 3D reference collection now rejects Git LFS pointer text even when a
  dev server labels it `image/png` or `image/jpeg`; this prevents a refunded
  provider failure from recurring.

## City Prompt trial results — 2026-08-05

The signed-in `Park Test 2` project was tested sequentially with one park zone
and no master-planner run. Four photorealistic Direct 3D results are saved in
Project Renders, in this order: inclusive playground, dog park, splash pad,
and community garden. The project is intentionally left on Trial 5, Community
Garden, with exactly one compiled green-space zone.

- Inclusive playground: the live scene retained all five safety islands and
  the accessible equipment hierarchy; the photo finish remained recognizable.
- Dog park: the five-pen plan and timber enclosure system read clearly in the
  live scene and photo finish. This is the strongest proof that a surface-plus-
  module program can replace an AI-painted diagram.
- Splash pad: the tower, jets, central wet pad, apron and fence survived. The
  photo finish enlarged the surrounding landscape character, so the compiled
  live scene remains the geometry authority.
- Community garden: the live scene retained the authored 18-bed program and
  small greenhouse. The photo finish added more garden beds than the compiled
  source despite an explicit instruction not to; Direct 3D therefore needs a
  stricter instance-count/structure gate before its output can be treated as
  dimensional evidence.

The first inclusive photo attempt found a 132-byte Git LFS pointer masquerading
as `image/png`. OpenAI rejected the fifth input image and City Prompt refunded
the reservation. After hydrating the four exact references and adding the file-
signature guard, all four subsequent calls completed and saved normally.

## Replacement gate

This method can replace draping for a catalog identity after all of the
following are true:

- the park reads as the intended archetype in both near-nadir and oblique view;
- primary program geometry is present, correctly scaled, and on grade;
- exact skin character survives live 3D and the photo finish;
- the full program fits without parcel scaling or boundary overlap;
- no generic trees, furniture, people, roads, or buildings corrupt the layout;
- a saved recipe round-trips and Direct 3D capture names the park, ground, and
  landscape instances; and
- the authored reference is available as a real LFS image, not a pointer.

## Further work

1. Add a machine-readable park-kit manifest containing module transforms,
   surface primitives, texture roles, program envelope, clearance, and QA
   reference IDs. This removes hand-coded placement arrays from React.
2. Add near-nadir and oblique golden captures per variant and automated
   silhouette/module-presence checks.
3. Improve site fitting from rectangle-only programs to authored sub-program
   graphs so irregular parks can choose valid path/gate orientation without
   scaling equipment.
4. Add explicit fence-section end treatment and gate alignment, especially for
   dog parks and gardens.
5. Add terrain contact probes per repeated module rather than one program
   centre elevation on sloped sites.
6. Promote one reviewed variant at a time. Variants must own their own skin and
   may own different geometry; do not assume v1–v3 are recolours of v0.
7. Use Meshy only for distinctive organic or sculptural modules that are poor
   procedural candidates. Keep slabs, beds, fences, courts, paths, and other
   dimension-critical systems authored in Blender/procedural geometry.
8. Retire AI draping per identity as coverage grows. Remove the global legacy
   system only after catalog coverage and fallback behavior are explicitly
   reviewed.
