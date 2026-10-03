# Charcoal Gable Fourplex — local RLASM v6.1 pilot

This pilot interprets the supplied street photograph as four attached homes. It
is a review candidate, not an approved RLASM keeper or construction model.
The source shows one front oblique only. The rear, complete side elevations,
room layout, measured dimensions, and concealed roof junctions are explicit
inferences. No address or architect has been verified for the source image.

## Source and generated evidence

- Locked source: `frontend/public/archetypes/buildings/reference-fourplex/hero.jpg`,
  SHA-256 `349c1f261e63918f6e19f6fc3f61570d0af3ae39e286498ac5453a8f710255ed`.
- Material specimen: a photo-conditioned generated 2×2 atlas of charcoal
  battens, ivory lap siding, charcoal brick, and dark shingles. The atlas and
  its deterministic albedo/normal/roughness/AO derivatives remain in external
  candidate artifacts. They are generated interpretations, not extracted
  source pixels. Atlas SHA-256:
  `f1e4853259e2918de946be5f14aa8bad564ca2b4683d66fe00ed90b709082592`.
- Blender source: `build_fourplex.py`. Candidate GLBs, renders, screenshots,
  phone boards and review manifests remain outside the active source tree.
- `make_review_boards.py` composes two 1080×1920 boards from the locked photo
  and final 12-view Blender render set.

## Rebuild

Run `prepare_materials.py ATLAS.png OUTPUT_DIR`, then:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python tools/fourplex_pilot/build_fourplex.py -- --output C:/dev-artifacts/CityPrompt/reference-fourplex-2026-10-01/full-v6 --materials-dir C:/dev-artifacts/CityPrompt/reference-fourplex-2026-10-01/materials
```

The local browser fixture loads the generated GLB from
`frontend/public/validation-assets/reference-fourplex-v1/reference-fourplex-v1.glb`.
That file is intentionally ignored; install the independently reviewed pilot
GLB there for local testing. Its exact SHA-256 is recorded in
`frontend/src/data/validationCatalogue.json` and the external candidate
manifest. Do not publish the candidate by staging the ignored model or
promoting it into the seed catalogue.

The pilot card is labelled `app_eligible: false`. Promotion requires a
complete source set and a fresh independent holistic review with no P0/P1
findings under `docs/RLASM_LATEST_METHOD.md` and
`docs/RLASM_REPOSITORY_POLICY.md`.
