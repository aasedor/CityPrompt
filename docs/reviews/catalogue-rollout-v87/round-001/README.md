# Catalogue V87 — ten-building checkpoint

This checkpoint used ten exact variants across five parent archetypes before
any 100-building expansion. The result is intentionally mixed: six keeper
candidates, two provisional models and two rejected models. The 100-building
round therefore remains blocked.

![Exact archetype comparison](exact-reference-comparison.png)

![Roof and exposed-side audit](roof-and-side-audit.png)

## Results

| Variant | Human result | Machine result | Main finding |
| --- | --- | --- | --- |
| Federal Brownstone | Keeper candidate | Pass | Facade hierarchy and metal roof read correctly. |
| Greystone Brownstone | Keeper candidate | Blocked | Strong visual likeness; source-to-GLB appearance parity is 0.91995. |
| White Corbusian Civic | Keeper candidate | Pass | Mask-only modern glazing removed the floating cage; parity is 0.99199. |
| Precast Panel Civic | Provisional | Pass | A single paid rectangular-opening retry removed invented arches; a rear skin overlap remains. |
| Terracotta Fin Office | Rejected | Failed | Initial result was too tall and cage-like; the repair exceeded the acceptable module-export time. |
| Dark Frame Office | Provisional | Blocked | Identity is credible, but transparent source-to-GLB parity is 0.91599. |
| Charred Nordic Timber | Keeper candidate | Blocked | Real timber entry returns fixed material ownership; parity misses the threshold by 0.00486. |
| CLT Nordic Timber | Keeper candidate | Pass | Physical pine members fixed secondary-material export; parity is 0.97130. |
| Moorish Arcade | Keeper candidate | Pass | Three openings are construction-depth recessed passages rather than dark facade cards. |
| Catalan Modernista | Rejected | Failed | Rectified imagery still repeats as a flat collage and the box massing misses the organic archetype. |

`Keeper candidate` is a visual classification, not catalogue release. A model
with a blocked machine result still needs the named export repair.

## Cost and bounded execution

- 10 multimodal feature-contract calls: reserved USD 0.20.
- 10 first-pass 2K facade calls: reserved USD 1.10.
- 1 selective 2K facade retry for the Precast Panel Civic: reserved USD 0.11.
- Total reserved API cost: **USD 1.41**, below the authorized USD 20 cap.
- Blender/OpenCV work was local and added no API cost.

## Pipeline changes proven by this round

- External, versioned V87 PBR recipe manifests now drive exact-variant surface
  bakes without editing the global recipe table.
- Signature-profile overrides are explicit and auditable; undeclared duplicate
  profiles remain errors.
- Exact reference images are the authority. Multimodal output is normalized as
  a draft feature schedule, and catalogue metadata is disabled when it does not
  improve visible evidence.
- Every pilot receives four exposed-elevation skins, a roof material owner,
  floor-registered facade bands and an exact-reference/roof/rear comparison.
- Large repeated modern facades use lightweight registered glass masks. Deep
  returns are reserved for identity-bearing heritage openings and entrances.
- Recessed public space compiles as real topology. The Moorish arcade uses a
  three-opening block with lining, clearances and deeper occupied backs.
- Semantic facade invention is a human rejection even when technical checks
  pass. The Precast retry demonstrates the correction; the Catalan result
  demonstrates why a polished atlas cannot rescue wrong massing.
- Slow module export is a release failure. The terracotta result must be
  simplified before it can re-enter a finite batch.

## Decision

Do not start the 100-building run yet. The next bounded checkpoint should fix:

1. glTF optical parity for translucent/very dark materials;
2. rear/side skin intersections on the Precast model;
3. a lower-complexity terracotta module path; and
4. curve-native Modernista massing with facade bands cropped to one true
   storey rather than a repeated multi-storey image.
