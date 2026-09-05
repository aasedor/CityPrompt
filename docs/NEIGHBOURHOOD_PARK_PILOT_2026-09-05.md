# Neighbourhood park: adaptive rustic pilot

Status: **reviewed functional pilot; not approved for catalogue or production**.
One archetype, `neighborhood_park / neighborhood_park_v0`. No other park,
street or building family was promoted. Work is isolated in
`C:/dev/CityPrompt-park`, branch `codex/neighbourhood-park-pilot`, based on
`5e65a2c3b`. The original dirty workspace was preserved.

## Try the result

- Interactive geometry review: http://127.0.0.1:5174/park-pilot.html
- Google tiles project: http://127.0.0.1:5174/projects/261a0c42-0b9e-4775-98db-17e62f8f51a7
- Local account: the existing isolated Studio Smoke Student account. The lab
  needs no login; the project uses the local backend on port 8001.

The lab provides four footprint cases, flat/sloping ground, overhead, aerial
and pedestrian inspection. It renders the same component as the Google scene;
its ground is synthetic and its lighting differs. It is a development review
entry, not part of the normal production build entry.

In the normal project, select the rustic neighbourhood park and use **Adapt
the park to my site**, then **Save Changes**. The option is specific to this
one variant and is off for existing projects unless explicitly saved.

## What was built

The exact source aerial pair owns the park's spatial character: dominant oval
lawn, continuous warm gravel loop, two separate play pockets, one gabled timber
picnic pavilion and one swing, framed by woodland and wildflowers. The ground
reference informs materials and human scale. Equipment dimensions and the
interpretation of differing play equipment between reference views are design
inferences, not surveyed measurements.

The deterministic composer fits that programme to the drawn boundary. It
reserves lawn before packing metric equipment, rejects envelopes that cross
concave edges, connects approaches to pad edges, and reports omitted elements.
It never stretches a play tower to fill a large polygon. Candidate searches,
tree/flower counts and the layout cache are bounded.

| Tested footprint | Result |
| --- | --- |
| 40 x 35 m | One play tower and pavilion; swing omitted explicitly |
| 70 x 55 m | Two towers, one pavilion and one swing |
| 105 x 75 m | Full programme, larger lawn and planted perimeter |
| Rotated L, 80 x 60 m overall | Two towers and pavilion; swing omitted |
| 8 x 80 m | Reports that the neighbourhood programme is too narrow |

This does not establish support for every arbitrary polygon or terrain.

Nine metric GLBs form the reusable candidate kit: gabled pavilion, play tower,
swing, split rail, boulders, bench and three branching oak variations. They total
5,263,548 bytes. Vegetation uses shared instanced geometry; assets load only
when this opted-in park mounts. Materials reuse the historical park's source
skins. The oak foliage texture is supporting MIT-licensed material; the licence
is included. No additional npm dependencies were added.

Ground surfaces follow the shared terrain triangles. Equipment remains rigid
on rounded level pads sampled over the entire pad, including interior humps.
Short graded approaches meet the pad rather than entering the play apparatus.
Rail feet share the pad datum. Deep grading is marked in object metadata for
review, not silently resolved by dropping equipment. This is a visual pilot,
not a grading or playground-safety certification.

The existing street-access solver uses the composed module envelopes and path
guides. It connects eligible nearby sidewalks, respects intervening building,
water and road barriers, and clears planting from derived entrance paths.
Unannotated building entrances are not invented. The Google fixture shows one
diagonal connection from the north-side sidewalk into the loop.

The same composition supplies the park diagram and render description, including
actual object counts and omissions. The prompt forbids relocating occluded
objects. The backend source fingerprint now includes the pilot flag so future
compiles detect mode changes; its narrow test passes. The already-running
port-8001 backend belongs to the earlier studio checkout and was not restarted
onto this source change.

## Verification and findings

- 154 frontend tests pass: layout, pad/approach geometry, park profiles,
  street-access connections and the existing properties panel suite.
- 14 residual-landscape backend tests pass.
- TypeScript check and scoped ESLint pass; `git diff --check` passes.
- Blender input dry run passes. All nine generated GLB hashes match the saved
  candidate manifest. Asset exports were visually inspected in the real viewer.
- Nine final browser evidence cases have asserted size/slope state, UI captures
  and raw canvas captures. The actual project also captures beauty, proposal
  mask, classes, depth and normals through its existing capture function.
- The pilot checkbox was disabled and restored through the real UI and API;
  successful save responses are recorded in `ui-evidence.json`.
- Browser error inventories were empty at the final check. Earlier development
  reloads and deliberately failed/mislabeled captures remain historical output.

The independent reviewer closed the overhead grass/path breakup after the lab
was changed to the same logarithmic depth handling as the globe. Source-quality
keeper approval was **not** granted. See
`reviews/NEIGHBOURHOOD_PARK_PILOT_2026-09-05_INDEPENDENT.md` for the findings and
exact reviewed-image hashes.

The live project sits on the open Fort Calgary field at approximately
51.04542, -114.04677, with a 90 x 93 m retained-ground boundary, one park,
two circulation zones and three building plots. Two buildings load detailed
models; the cafe remains planned massing under its existing family fit rules.
The park is the pilot under review, not a new building-family result.

Google ground sampling settled at 1,190 samples, two stable passes and zero
maximum pass-to-pass delta. No grounding issues were reported at the reviewed
aerial camera. Those are stability measurements, not proof of centimetre-level
terrain accuracy. Recorded maximum local residual was about 0.165 m.

**Open limitation:** at a cold pedestrian camera, Google tile loading does not
reliably supply the entire site grid required by the existing shared-ground
provider. The provider then withholds assemblies rather than placing them on
unknown ground. The local lab's slope/contact evidence does not fix or validate
this separate live tile-loading issue. Its next fix should retain a validated
ground snapshot through camera/LOD changes and deliberately obtain missing
coverage, with quality/freshness checks.

## Presentation render trial

One built-in image edit used the actual Google beauty capture with an explicit
material/light-only prompt. No external image/video API was called for this
pilot; this does not measure Google Maps usage or built-in account usage.

The generated image improves foliage, timber, grass and scene coherence, but
changes framing, apparent scale and some equipment/building detail. It is an
**illustrative appearance experiment, rejected as geometry-faithful proof**.
This was not a successful test of the application's image-render backend.
The input, output and exact prompt are retained separately. Do not use the
attractive result to claim hallucination or consistency problems are solved.

The next render experiment should preserve the captured camera and apply bounded
appearance changes guided by the captured depth, mask and object identities,
then check registered before/after images and object counts before accepting it.

## Reproduce and continue

Generated assets and screenshots are ignored under `artifacts/park-pilot/`.
Source code, tests, this report, the independent review and the small hashed
asset manifest are the intentional source deliverables. No generated folder
is staged wholesale and no production catalogue references were changed.

With Blender 5.2 and a hydrated source checkout:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/neighborhood_park_pilot/build_assets.py -- --source-root 'C:/Users/andre/OneDrive/Documents/CityPrompt' --output-dir artifacts/park-pilot/public/landscape-pilots/neighborhood-rustic-v2 --dry-run
```

For a new checkout with no candidate output, repeat without `--dry-run` to build
the finite nine-asset kit. Existing nonempty output is refused: a visual revision
needs a new directory and an intentional URL change. The builder reads the
historical material helper but does not modify or approve it.

```powershell
./tools/neighborhood_park_pilot/serve.ps1 -SourceRoot 'C:/Users/andre/OneDrive/Documents/CityPrompt'
```

This starts the isolated frontend, reuses the hydrated public assets through
junctions, and points to the existing local backend. It does not launch paid
generation. `create_local_fixture.py --output-dir artifacts/park-pilot` reuses
its local project checkpoint; it refuses to silently duplicate an incomplete
project. Run it only against the isolated backend it explicitly targets.

Evidence in `artifacts/park-pilot/`: `verified-*`, `canvas-*`,
`review-evidence.json`, `top-live.png`, `beautyImageBase64.png`,
`google-capture.json`, the geometry-pass PNGs, `ui-evidence.json`,
`ai-presentation-preview-v1.png` and its prompt. Failed initial depth evidence
is retained in `review-v2-before-depth-fix/`.

Next bounded revision: vary tree silhouettes and heights, replace isolated
flowers with coherent planted beds, refine gravel/activity edges in Google
lighting, and obtain source-matched close and opposite views. Finish this
single archetype before applying the recipe to further parks or plazas.
