# Sports and reading gardens — native 3D asset batch

User requested more high-quality parks/streets including sports parks and actual
3D assets. Park work is isolated on `codex/sports-garden-asset-batch`, based on
`601694de8`. First checkpoint: `f0e2e7878` (verified pickleball pilot). These are
original local model candidates, not replacement identities for existing parks.

| Exact concept ID | Footprint | Programme | Triangles | GLB bytes |
| --- | --- | --- | --- | --- |
| student_pickleball_garden_v1 | 34 x 34 m | One court, shaded social terrace, four planted beds | 163,760 | 4,075,048 |
| student_futsal_park_v1 | 42 x 60 m | One court, two goals/nets, offset entry, team terrace | 171,820 | 4,504,836 |
| student_reading_garden_v1 | 30 x 26 m | Two pergolas, reading seats, picnic tables, planted rooms | 153,654 | 2,508,992 |

## Delivered files and construction

External root: `C:/dev-artifacts/CityPrompt/public-realm-batch3-2026-09-22/`.
Accepted packages: `pickleball-final`, `futsal-final`, `reading-final`.
Each has an assembly-preview GLB, native-origin reusable component GLBs,
placement/surface recipe, builder sources, three rendered views, geometry check
and a pending runtime review. Sport packages additionally have `sport-module.glb`.
The companion JSON records exact hashes and byte counts. Experimental v1/v2
packages are retained separately. Binary output is not committed to Git.

`export_kit.cjs` exports actual current furniture/vegetation geometry and linear
vertex colours from the frontend. It does not substitute a similar-looking kit.
Static fence wires, surfaces and markings are consolidated by material; shared
plant/furniture geometry is preserved. No textures or paid image calls. Court
lines, sagging pickleball net tape, goal nets, slatted pergolas, furniture,
layered plants and tree branching are real geometry.

Surface cells have one owner. Recipe regions retain that priority explicitly;
runtime must rebuild surfaces from shared ground, not drape the complete GLB.
Native pergolas and sport modules can be reused without stretching. Kit trees
retain their native height; full delivered bounds include their crowns.

## Dimensions and visual review

Pickleball: 6.096 x 13.4112 m playing rectangle inside a 10.8 x 20 m reserved
module. Court/net basis: [USA Pickleball construction guidance](https://usapickleball.org/construction/).
Futsal: chosen 20 x 40 m playing rectangle inside a 26 x 46 m concept reserve;
goals have 3 x 2 m clear openings, as described in the
[FA futsal handbook](https://www.thefa.com/-/media/cfa/global/files/mini-soccer-youth-futsal-handbook.ashx?la=en).
Outdoor park finishes/run-off are design choices; no competition, accessibility
or engineering certification is claimed.

Dry run preceded the pilot. Reimported exported GLBs were inspected in aerial,
top and detail views. Agent visual review: suitable model candidates. Independent
human approval remains open. The initial top framing cropped ends; final top
cameras account for output aspect ratio. Reading seats originally landed on
lawn; final pergolas have connected paving. Futsal entry is offset from the goal.

Verification passes self-contained buffers, finite bounds, exact asset hashes
and material-aware walking rays: 105 pickleball, 159 futsal, 483 reading garden.
Checks inspect actual delivered mesh surfaces at pedestrian height, not just
placement metadata. Static consolidation reduced the pickleball preview to
133 mesh instances. District FPS is untested; runtime should instance the kit.

## Runtime handoff

Not installed in the student picker, seeded or published. All runtime gates in
each package's copied review template remain NOT TESTED: authoritative terrain,
access, collision/edit/Undo/reload, residual landscape and exact capture need a
bounded integration pass on disposable vacant Currie land. Use exact new IDs;
never stretch courts, omit run-off, or crop a rigid assembly into a polygon.
Offline previews do not prove site grounding or novice usability. This batch
completes asset creation and review, not student runtime activation.

Replay: export shared kit with Node, then run Blender 5.2 using
`--background --python-exit-code 1 --python tools/public_realm_assets/build_parks.py`
and `-- --kind <pickleball|futsal|reading> --kit <kit.json> --output <fresh-dir>`.
Use `--dry-run` first, then `verify.py -- <package>` and `package_review.py`.
