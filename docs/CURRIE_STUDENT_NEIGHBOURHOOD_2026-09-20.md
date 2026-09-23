# Currie student neighbourhood exercise — 2026-09-20

## Result and scope

Completed a bounded desktop author/edit/Undo/Redo/reload/exact-export exercise
in the existing disposable Currie project:
`http://127.0.0.1:5174/projects/7e1e9037-b98c-4d18-8502-839160315869`.
Runtime source: `b6af7734a`; browser viewport: 1440 × 900, mouse and keyboard.
This is an agent acting through student controls, not an independent student
usability study or a new-project-from-scratch test.

Reused the previously student-drawn irregular 12-corner site, explicit prepared
level, northern public-road connection, bent 10 m residential street, one house
and 40 × 35 m Rustic Timber & Gravel neighbourhood park. Added six individually
placed Calgary Modern Infill House / Flat Roof Minimal homes using Buildings
and Place another. The resulting scene contains seven two-storey native
12 × 16 m house plots, a street, a park and the site boundary: ten saved zones.
The houses form a low-rise cluster on both sides of the street, consistent with
the housing north of the parcel, with space between plots and park access from
the shared sidewalk. This is a small concept cluster within a larger parcel,
not a fully built-out neighbourhood or approved development plan.

All design writes used visible controls. API and runtime resolver calls were
read-only verification. No paid image generation, catalogue changes, protected
reference-project edits, production-code changes or remote push occurred.

## Exercise and acceptance evidence

| Action | Result |
| --- | --- |
| Inspect surrounding context in top and oblique views | Low-rise housing selected; buildings remain within the vacant irregular parcel, clear of the mapped perimeter roads. |
| Place six additional homes | Seven visible native homes total; individual plots remain separated, with four west and three east of the authored street. |
| Edit opposite-side orientation | Used Rotation and Apply shape to turn the east-side houses. Place another did not reliably face them toward the opposite sidewalk without this manual edit. |
| Undo then Redo an east-side rotation | The selected field returned to 90 degrees after Undo, then -90 degrees (equivalent to 270) after Redo. |
| Add six entrance connections | Used Connections, selected the street sidewalk and authored the entrance. Seven saved building routes resolve connected. |
| Inspect a native step in 3D | A pick near the step initially produced an obstruction warning. A later numeric adjustment produced a visible gap and an edge warning. Adjusting the anchor in the same UI resolved the join and warning; see `student-step-final.png`. |
| Repeat the same native model's entrance setup | Reused the setting established in this exercise through visible fields, then checked all routes. These are scene measurements, not universal archetype defaults or developer-supplied coordinates. |
| Park access | Existing automatic 2.2 m gateway/sidewalk/internal-loop connection remained connected. |
| Reload | Ten zones before and after; sorted zone IDs, geometry and properties exactly equal. Seven house routes and the park connection retained. No browser page errors; street ready; no reported grounding/entrance issues. |
| Free exact export after reload | Normal Render this view → Image → Export current 3D view → Download render succeeded in 2,542 ms from an already ready view. No page errors. Downloaded PNG visually inspected: seven homes, street, park and surrounding context retained. |

Reload resets the camera to the wider 30-degree view and clears in-session Undo
history. The presentation camera was reframed using ordinary zoom/orbit controls
after reload. The 2.5-second result is a warm, ready-scene export measurement;
it is not a cold-start timing claim.

## Student-readiness finding

The functional exercise passes on explicit prepared ground. No loss, stuck
save, invisible street, failed export, building overlap or reported grounding
issue remained at the end. The entrance workflow still asks too much precision
of a first-time student: an apparently reasonable surface pick can require
trial-and-adjustment using numerical fields. The next useful product improvement
is reliable exact-variant entrance defaults/snapping and clearer repeat-placement
orientation, proved on both sides of a bent street before catalogue expansion.
Do not advertise independent novice ease based only on this assisted completion.

The visual is a faithful concept image, not a polished finished development:
the large grass platform and exposed outer edge remain obvious; the seven-home
cluster leaves substantial land unprogrammed; the southern street end remains
an internal dead end without a designed turnaround. Northern junction grade,
vehicle turning/service access and step-free access are not certified by this
exercise. These limits must remain explicit if this scene is used in class.
Natural partial-ground coverage and AI image fidelity were not retested.

## Evidence

Local external evidence directory:
`C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-clear-route/`.

- `student-context.png`, `student-connected-plan.png`: context and seven-home plan.
- `student-step-picked.png`, `student-step-route.png`, `student-step-final.png`:
  entrance recovery, including the rejected/gapped intermediate states.
- `student-readback.json`, `student-park-readback.json`: saved scene and connections.
- `student-reload-result.json`: exact persisted-state comparison and error check.
- `student-export-result.json`: measured UI export result.
- `student-neighbourhood-exact.png`: downloaded 1440 × 836 exact presentation.
  SHA-256: `ee1121318d9b5db918eb4ebad9c239659863c5c38bd94b7c293fe6089667b70e`.
- `student-actions.cjs`, `student-reload.cjs`, `student-export.cjs`: browser actions
  and read-only acceptance checks. Local evidence is not a shared artifact backup.

Reusable findings are added to the runtime integration checklist and template.
The actual new-variant onboarding pilot remains separate and uncompleted.
