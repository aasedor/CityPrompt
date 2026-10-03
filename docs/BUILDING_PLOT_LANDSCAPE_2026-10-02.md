# Building lot landscaping and continuous ground

## Scope

Local runtime change on `codex/building-landscape-surrounds`, based on
`2180bb118`. No building GLBs, catalogue bindings, source materials, model
dimensions, saved plots, elevation contracts or RLASM method files were changed.
This is shared display landscaping, not a new building-family approval.

The user requested landscaping around every building and then asked for
archetype-specific cues, blended lot edges and close-up inspection.

## Result

- Building plots now continue the surrounding site's ground texture. The old
  neutral holes and dark rectangular foundation bands no longer frame each lot.
- Shared foundation caps use the same geographically aligned texture as the
  prepared site. Shallow edges up to 15 cm share that finish; taller retaining
  faces retain their concrete material and original geometry.
- Low beds use the exact building's ground-floor/frontage/public-realm notes
  and landscape palette from `frontend/src/data/buildingArchetypes.json`.
  Matching variant notes are included; roof planting is excluded.
- All 32 current building choices resolve their archetype. Thirty-one have
  ground-level notes. Grand Iron & Glass Market has no ground-level landscaping
  notes, so its design is explicitly marked as a conservative fallback.
- Minimalist frontage uses restrained evergreen planting; native planting cues
  use low grass clusters; planted residential frontage can use flowering shrubs.
  Existing authored gardens remain visible. The complete model envelope plus
  1.2 m circulation clearance controls where extra planting fits.
- Narrow plots, repeated houses and unmeasured models receive ground cover
  without speculative shrub placement. Roads, parks, neighboring plots and
  saved entrance corridors are clipped out. Front/rear ends stay clear.
- Compiled sites use one continuous boundary surface instead of a second lawn
  rectangle. Existing custom site-base imagery remains in control of its surface.
- A capture smoke test exposed a missing stable instance tag on loaded local
  review buildings. Loaded GLBs now carry their exact zone/building identity;
  loading/error placeholders remain untagged and cannot pass as finished models.

## Verification

Agent simulation in Chrome at 1600 x 1000, localhost:5197. This preserves the
existing isolated terrain-trial server and external asset root.

Disposable project: `80264412-126d-495c-a11d-e800b5fc5480`,
**QA - Building gardens and clear entrances**, a 180 m prepared test site.
Project/boundary setup used the API; four buildings were placed through the
ordinary catalogue and canvas controls. Camera positioning used the development
scene handle for repeatable close views. Walking and visibility used the UI.
The existing Currie Fourplex Commons project was inspected without editing it.

| Exact variant | Close review |
| --- | --- |
| `reference_charcoal_gable_fourplex_v1` | Original four front gardens, stoops and walk retained; added lot rectangle removed; overhead, oblique and pedestrian views inspected |
| `minimalist_infill_brick_monolith` | Low evergreen side beds outside the full model and circulation clearance; frontage left open; lot border blended |
| `bungalow_postwar_ranch` | Front lawn and original porch/steps retained; narrow margins not crowded; foundation texture aligned to the site |
| `mass_timber_biophilic_barn` | Ground-level native-planting notes resolved; current narrow plot receives no forced extra plants; original entrances and model retained |

- 116 tests passed across 9 relevant Vitest files, including all 32 building
  choices, clearance, rotation, neighboring roads, side entrances, custom imagery,
  unchanged foundation positions/indices, exact note selection and texture blending.
- TypeScript check passed.
- Four landscape owners survive save/reload. No grounding issues in the mixed site.
- Walk test moved about 2.9 m along the fourplex frontage at the unchanged
  1107.2 m ground datum; model visibility off/on produced no page errors.
- Direct 3D capture succeeds with an instance manifest and landscape geometry.
  This tests exact scene capture, not paid AI image generation.
- Browser testing found and fixed an InstancedMesh cleanup error on unmount:
  a `dispose={null}` primitive prop had replaced the method owned by cleanup.

## Limits and evidence

Four representative variants received close browser review; all 32 received
configuration/geometry checks. This is not a claim that every building's full
runtime acceptance matrix has passed. Stairs, interiors, entrance authoring,
sloped terrain and all edit/recovery combinations were not recertified here.
The new planted beds apply to supported prepared sites. Natural terrain keeps
existing grounding behavior. No tall trees or furniture are inserted from text
notes without measured clearance.

Evidence is outside Git at
`C:/dev-artifacts/CityPrompt/building-landscape-2026-10-02/`:
`archetype-notes-audit.json`, `walk-result.json`, `ui-result.json`,
`capture-instance-manifest.json`, `zoom-0.png` through `zoom-3.png`,
`fourplex-final-overhead.png`, `fourplex-walk.png`, and
`library-exact-capture.png`. Scripts and private test authentication are also
external; authentication is not part of the deliverables. No generated output
is staged and nothing is pushed.
