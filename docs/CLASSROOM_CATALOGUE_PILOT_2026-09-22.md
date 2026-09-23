# Classroom catalogue entry pilot — 22 September 2026

## Result and scope

The next bounded runtime pilot reuses three existing assets: Beltline brick
mixed-use mid-rise (`beltline_brick_modern`, clay v003), Calgary local street
(`calgary_local_v0`, 16 m), and teaching demonstration garden
(`research_garden_teaching_arboretum_variant_3`, `park-trio-v3`). These are new
to this classroom acceptance exercise, not newly built or newly approved assets.
No Wave 2 family was activated. No model geometry or RLASM method changed.

The disposable project is `3a52b4df-8508-408e-ac20-2f674d7c23b9`, served at
`http://127.0.0.1:5175/projects/3a52b4df-8508-408e-ac20-2f674d7c23b9`.
It uses the previously reviewed irregular vacant Currie boundary between the
straight eastern road and curving western context. Boundary setup was copied
through the API; all buildings, street, garden, plot resize, route extension,
garden move and landscape application used ordinary UI controls. This is an
assisted runtime trial, not an independent novice usability result.

The final scene contains two five-storey native buildings, one bent local
street, one 42 × 50 m teaching garden and the free neighbourhood-gardens preset.
The original landscaping project `7e1e9037-b98c-4d18-8502-839160315869` remains
unchanged: all eleven objects, properties and timestamps match, normalizing
only the renewed surface-image access URL to its path.

## Changes carried into future archetypes

- `reviewedEntrances.ts` holds runtime entrance measurements separately from
  generated catalogue cards. It requires the exact asset, variant, revision
  and fixed-native placement mode. The existing infill metadata still works.
- A `fixedNative` entrance follows one centred, unscaled building when its
  surrounding rectangular plot grows. It requires native plot axes, excludes
  repeated-home layouts, and rejects plots below the reviewed minimum. Manual
  overrides retain their existing behaviour. Other buildings gain no default.
- New park-trio placements start at their recommended programme size. Their
  smaller supported dimensions remain available for deliberate resizing; saved
  plots are unchanged. The default garden now has twelve beds, twelve labels,
  one shelter and two benches rather than starting with the compact programme.
- The saved-representation notice distinguishes an explicitly selected adaptive
  park from a genuinely unsupported fallback. A backend family-pending marker
  alone no longer tells students that the visible adaptive garden is unavailable.
  Unrecognized variants still display the fallback warning.

## Exact building entrance evidence

The served GLB was hashed in the browser and matches the activation manifest:
`1ed0f47bb38a6879233fe54d441ba734f60f533f97a21b5e894a0706472cef41`
(5,022,608 bytes). Both saved recipes use one instance at `[1,1,1]` scale with
native dimensions 34.16 × 34.16 × 20.43 m and five floors.

The immutable v003 authoring script locates the front retail door at x=-0.30 m,
y=-15 m. The generated approach meets the complete support apron at
x=-0.30, y=-17.08 m in the rotating plot frame, outside the canopy columns.
Its walking width is 1.8 m and base offset is zero. This is an apron connection,
not a claim that the door itself lies at the envelope edge. The low live view
`entrance-close.png` shows the route meeting the entrance apron below the door.
It is not an accessibility or construction-design approval.

Both street sides were placed through the UI without opening Connections.
The eastern building was resized from 39 × 39 m to 48 × 48 m. Placement snapping
adjusted its position to preserve street clearance; model scale stayed one and
the entrance remained attached. Undo restored the smaller footprint, Redo
restored the larger footprint exactly, and both retained the entrance metadata.
Place another produced a west-facing/east-facing pair with connected approaches.
Final native approaches have a 1.8 m clear width and two small steps each.

## Live findings and practical limits

The garden initially stood too far from the street for its bounded 8 m access
search. One ordinary move closer produced a 2.2 m connection to the actual
sidewalk and internal circulation loop. The original unresolved result was
retained in the session record; access was not fabricated across the larger gap.

The local street was drawn with three points, then its public-road option was
enabled and its northern endpoint dragged to the visible road edge. The route
and proposed connection survived reload. Detailed junction-grade and curb
continuity were not reviewed at ground level, so this does not close that gate.

Free landscaping kept the authored plots and paths clear. Custom GPT artwork
was not generated again; it remains covered only by the previous landscape-base
pilot. Final ground status was ready with no reported grounding issues and two
rendered building approaches. The known exposed white prepared-site edge remains
visible: a colour blend cannot close that geometry gap. Natural terrain, maximum
plot sizes, save conflicts and late-measurement races were not re-tested here.

After reload, the free exact-view export produced a valid 1440 × 936 PNG
(3,120,851 bytes), visually inspected with both buildings, garden, street and
landscaping present. The browser automation cancelled the Download render action,
including an attempt with downloads explicitly allowed. The identical PNG was
saved directly from the existing download link's data URL. Therefore capture and
PNG validity pass; the download-button delivery check remains OPEN. Do not claim
a fully verified student export workflow from this run.

QA used the established isolated 5175/8001 services and a 1440 × 1000 desktop
viewport. Docker initially failed on stale runtime sockets. Only socket runtime
directories were renamed to dated backups; database/storage volumes were not
reset. The isolated database, Redis and media containers were restarted. The
frontend public assets still come from the external reviewed public directory.
Paid providers stayed disabled; credits stayed at 4,057.

## Verification and evidence

- 86 focused Vitest checks across nine files passed, including native entrance
  connection/resize, original infill behaviour, park programmes and notices.
- `npm run type-check` and focused ESLint passed.
- Exact variant reviews: [building](RUNTIME_BELTLINE_2026-09-22.md),
  [street](RUNTIME_CALGARY_LOCAL_2026-09-22.md),
  [garden](RUNTIME_TEACHING_GARDEN_2026-09-22.md).
- Machine manifest: `CLASSROOM_CATALOGUE_PILOT_2026-09-22.json`.
- Heavy evidence: `C:/dev-artifacts/CityPrompt/catalogue-pilot-2026-09-22/`.
  Key files: `served-assets.json`, `before-undo.json`, `after-undo.json`,
  `after-redo.json`, `final-reloaded.json`, `access.json`, `verification.json`,
  `entrance-close.png`, `exact-export.png`. These local files are not a shared
  durable backup; preserve them before moving this work to another machine.

## Next bounded step

Resolve the download-button cancellation in a clean browser session and repair
the visible prepared-ground edge on this same fixture. Then run a short student
trial before extending the starter catalogue. The asset population already
contains useful variety; new families should fill a demonstrated student need
and complete the shared entry checklist rather than merely increase card count.
