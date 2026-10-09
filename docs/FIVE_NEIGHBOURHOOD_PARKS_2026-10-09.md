# Five neighbourhood parks — local native trial

This finite initiative adds five new park programmes with original generated
photographic references and complete metric native assemblies. It does not alter
building families or street production. The user authorized a local browser trial;
native review, browser acceptance, human visual approval and publication remain
separate gates. Nothing in this checkpoint authorizes publication or a push.

| Park | Native footprint | Selected candidate | Native triangles | Assembly bytes |
| --- | --- | --- | --- | --- |
| Prairie Picnic Grove | 40 × 52 m | picnic-v003 | 787,025 | 41,206,364 |
| Sensory & Wellness Garden | 36 × 46 m | sensory-v003 | 546,482 | 27,081,832 |
| Urban Skate Plaza | 42 × 54 m | skate-v005 | 322,124 | 16,372,392 |
| Bicycle Pump-Track Park | 48 × 60 m | pump-v004 | 407,101 | 18,741,720 |
| Neighbourhood Sports Green | 48 × 66 m | sports-v002 | 261,830 | 11,960,268 |

## Authoring and source locks

`tools/public_realm_assets/build_five_neighbourhood_parks.py` contains distinct
source-driven constructors, shared metric geometry and the finite build entry
point. Each selected package preserves its exact constructor, `scene.py` and
`build_showcase_parks.py` bytes and hashes. Later constructor improvements do not
retroactively change an earlier selected assembly or its frozen source snapshot.

The built-in `image_gen` tool produced one original conceptual photograph per
park. These are invented design references, not photographs of real projects.
Authoritative originals and `source-provenance.json` records live under
`frontend/public/archetypes/openspaces/` in the five matching stable slugs.
The original photograph is the picker card; the selected native model remains
the authoritative geometry. No paid provider API generation was invoked.

All five references requested whole-site elevated oblique landscape-architecture
photography, realistic metric proportions, a broad clear entrance, coherent
native planting and no labels. Programme-specific prompt content:

- Picnic: two open timber gable shelters, communal tables, oval pale walking loop,
  central prairie meadow, layered flowering margins and mature shade trees.
- Sensory: continuous oval loop and crossing walk, four fragrant planting rooms,
  central lawn, raised herbs, curved timber benches and two rear pergolas.
- Skate: a smooth concrete bowl, two quarter pipes, low bank, grind ledge and rail,
  separate spectator loop, planted edges and an entry shade pergola.
- Pump track: a closed banked rolling asphalt circuit, separate low beginner loop,
  planted central island, bicycle racks and shaded gathering beside a pedestrian loop.
- Sports: a small marked grass field and netted goals, separate perimeter walk,
  front fitness bays, shade pavilion and trees beyond the playing/runoff reserve.

Observed features and explicit adaptations are recorded per exact recipe. The
conservatory benchmark guided composition and physical detail without copying its
programme. Planting uses the shared kit plus authored narrow grass blades, stems
and petals. Every tree remains over soft landscape and inside its native envelope.

## Bounded pilot and corrections

Dry runs preceded generation. Picnic was the isolated first pilot and received
independent offline review before local registration and browser work. Remaining
parks proceeded after the pilot browser checkpoint. Each programme stayed within
three correction candidates after its initial build, except one explicitly
authorized additional skate-v005 access correction after the v004 landing
introduced a 28 cm step. Failed outputs remain external.

Picnic corrections increased planting density, linked bench bays and moved tables
clear of the full shelter aisle. Sensory corrected a local-versus-world slat
rotation, closed-loop seam geometry and accessory clearance. Skate uses a raised
1.65 m bowl rather than terrain excavation; a positive-width landing joins its
access bank to the rim. Pump-track entrances join exact sampled outer-edge vertices
at measured heights, with real openings in the turf shoulders. The recreational
sports field is 26 × 40 m with a 32 × 47 m runoff reserve and 3.7 × 1.85 m goals;
it makes no competition-size or equipment-certification claim.

`verify_five_neighbourhood_parks.py` reimports the delivered GLB and verifies
self-contained dependencies, byte hashes, finite contained metric bounds,
material-aware full-width pedestrian rays and soft tree-root contacts. Pump-track
verification additionally checks the actual cycle-entry surface heights and
materials. Independent review reimports reusable modules and checks metric
envelopes/base contacts as well as source, aerial and walking images.

## Integration and verification

`scripts/register_five_neighbourhood_parks.py` admits only the finite exact hashes
and independent zero-P0/zero-P1 reviews. It requires locked recipe, assembly and
geometry evidence, preserves conflicting frontend/backend mirrors and existing
same-variant records, backs up catalogue files, and stages only hash-matching
assets. Frozen selected source and evidence accompany the LFS-backed seed files.
The model stays at native size when its surrounding parcel expands.

Rebuild in a fresh external candidate directory with Blender 5.2:

```text
blender -b --python tools/public_realm_assets/build_five_neighbourhood_parks.py -- --kind picnic --kit <shared-kit.json> --reference-root frontend/public/archetypes/openspaces --output <fresh-external-candidate> --dry-run
blender -b --python tools/public_realm_assets/build_five_neighbourhood_parks.py -- --kind picnic --kit <shared-kit.json> --reference-root frontend/public/archetypes/openspaces --output <fresh-external-candidate>
blender -b --python tools/public_realm_assets/verify_five_neighbourhood_parks.py -- <fresh-external-candidate>
python scripts/register_five_neighbourhood_parks.py --package <independently-reviewed-exact-candidate> --public-dir frontend/public
```

Other finite kinds are `sensory`, `skate`, `pump` and `sports`. The reusable kit
is preserved externally as `parks/shared-kit.json` with the recipe's SHA-256;
its source was `autumn-nine-2026-09-30/shared-kit/kit.json`. Selected GLBs embed
their geometry and colours and require no external textures. Rebuilding changes
an asset candidate; it does not inherit previous exact-byte approval.

Narrow checks cover registration failure paths, exact catalogue identities,
source-photo cards, native dimensions, existing park asset/access/walking behaviour
and backend native-park admission. Runtime source files were not changed. The
machine companion records exact selected hashes and offline results; per-candidate
`runtime-review.md` starts at NOT TESTED and must be updated only from actual
browser evidence. A passing level-fixture review does not establish natural-terrain
support, continuous user walking, export fidelity or novice classroom acceptance.

External evidence root:
`C:/dev-artifacts/CityPrompt/parks-streets-ten-2026-10-09/parks/`.
This local directory is not a shared evidence backup. Selected models, photographs,
source locks and concise review records are intentional repository deliverables;
render experiments, unselected candidates and bulk QA remain external.

## Bounded local browser result

All five parks were placed through the ordinary picker in disposable project `879957be-ef27-4af6-9e73-dffd6a72ffb6`, separately rotated, saved and verified after hard reload. The saved rotations are picnic 15 degrees, sensory 8 degrees, skate -8 degrees, pump 5 degrees and sports 10 degrees. Walking entrance screenshots show each native programme, and read-only database evidence confirms all exact variants and content revisions.

Picnic additionally passed parcel expansion to 44 x 56 m with its 40 x 52 m native programme preserved, move/Undo, rotation/Undo/Redo and a free capture preview. Actual download remains unverified. A combined resize-and-rotation edit was rejected recoverably; separate edits work. This is an open shared-editor follow-up.

Final checks: 48 focused frontend tests, TypeScript type-check, 13 registration/staging tests and 51 backend native-park tests passed. This bounded local checkpoint does not establish sustained walking, slope traversal, laptop performance, natural-terrain support, complete access/grade acceptance, actual download or novice classroom usability. These remain explicitly untested. Evidence hashes and exact per-park scope are in the machine companion and seed runtime reviews.
