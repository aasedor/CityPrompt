# Planted green bridge (RLASM v6.1 architectural clay)

Candidate H8 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `landscape_park_pedestrian_bridge / variant_2`
(catalogue variant id `landscape_park_pedestrian_bridge_v2`) from `frontend/public/archetypes/streets/landscape-park-pedestrian-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,653,127 | `fd3f4b85a8f168fb` |
| oblique | `variant_2_angle_60.jpg` | 967,340 | `fa6886dd4070716e` |
| top | `variant_2_angle_90.jpg` | 1,031,836 | `e865fb21f5bbf2da` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 32 x 80 m, 14.0 m to the highest point; 0 storeys (street option: a level planted pedestrian bridge over a river; the banks, trees and blocks are context).
- storey programme: street option: a level planted pedestrian bridge over a river; the banks, trees and blocks are context
- plan: 14 m deck (3.6 m path between two planting beds) on an 80 m run across a 20 m river (top view), two hexagonal planted viewing pods projecting 8.5 m each side near mid-river
- facade: pale path, dense beds of grasses, shrubs, lavender, red flowers and small trees, low steel inner rails with bollard lights, timber-capped picket railings on weathering-steel edge beams, rusted pod fascias, concrete cross-heads and round columns
- inferred: the deck structure under the planting, the far banks and the blocks are teaching assumptions; the bridge is shown as a section cut at both ends
- levels (m): 0.00, 2.20, 6.00

## Construction and delivery (Phases C to F)

`family_greenbridge.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, planting_bed, central_path, viewing_pod, pier_column, rail_bollard, water_under, rear_north`.

Run:

```
python tools/clay_planted_green_bridge/lock_sources.py
python tools/clay_planted_green_bridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_planted_green_bridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_planted_green_bridge
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v001 (v002 reworks these six)

1. P1: the front camera sits too low and far back; pods and water hidden behind shrubs and trees, both outer edge railings out of frame.
2. P1: each planting bed is about 1.5x the path width against about 1.0x in the source; the deck reads as a narrow path through wide lawns.
3. P1: the pods are chamfered rectangles instead of the source's half-hexagons with long angled sides, and about 15% too long along the axis.
4. P1: no paved route reaches the pods; the spur stops at the pod planting and the perimeter walk ends at its inner corners.
5. P1: the beds read as flat mown lawn with scattered shrubs and cones below the rail top, not dense mounded beds reaching the rail cap.
6. P1: the planting lacks variety: lavender as small flat purple pieces, grasses as single spikes, poppies as a few balls.
