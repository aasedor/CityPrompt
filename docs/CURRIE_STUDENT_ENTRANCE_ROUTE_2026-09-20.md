# Fresh Currie student entrance route — 20 September 2026

## Result

The disposable UI-authored Currie project
`0320bb4f-395c-41c6-a6c0-ad28bb1572ef` now has a saved native-step entrance
connected to its shared-street sidewalk. The house's automatic 90° orientation
was already correct. The earlier accepted but disconnected pick was a second,
rear low step on the model, not evidence that the plot needed rotating. From a
street-level camera on the east, the front door and low step are visible on the
street side; from the west, a separate low rear door and step are visible.

Using ordinary Select → Connections → Pick entrance step in 3D controls, a click
on the front step returned plot offset `(2.909, -5.875)` and **The approach fits
the current ground**. Save connections persisted that anchor. Review entrances
reported one generated step, a 0.05 m fall from sidewalk to model base, 1.80 m
clear walking width, and at most 0.06 m foundation support height. A fresh page
reload gave the same review. At a normal low east-side view, the walkway reaches
the native step without a conspicuous gap or floating segment. The free exact
3D export action opened a preview showing the same route; its image data was
saved for inspection. The automated download click canceled, so this run proves
capture/preview fidelity, not the browser's file-download gesture. No AI
generation was invoked.

The shared plan solver now gives a specific recovery when every candidate
sidewalk lies behind the chosen step: choose a step on the street-facing side,
or rotate the plot toward the street. A second UI pick on the visible rear step
returned `(-0.523, 5.875)` and showed that message. Cancel kept the saved front
anchor unchanged. The solver still rejects routes behind the entrance; it did
not move an anchor, cross the house, or loosen the 30 m/obstacle tests.

The project is explicitly prepared at 1102.62 m, not a natural-ground pass.
Review ground, park/partial-ground export recovery, the misleading native-body
drag hint, and a bounded image-fidelity test remain separate classroom work.
The protected original Currie project was not edited.

## Reuse for each new building variant

Treat automatic street-facing rotation as an initial orientation. If the exact
model has multiple low doors or steps, check which one faces the chosen sidewalk
in the rendered plot; a valid mesh pick alone does not establish a route. Record
the front and secondary step positions and directions against the variant's
actual bytes in B2 evidence, then pick and review the desired step through the
shared route and ground checks. Do not copy this house's numeric offsets into a
new variant or infer a door from a plot-guide dot. Keep the actionable
faces-away message and its rotated-house regression in the shared solver.

## Evidence and checks

External evidence in `C:/dev-artifacts/CityPrompt/grounding-batch-a/`:
`currie-route-before-zones.json`, `currie-route-front-view.png`,
`currie-route-click-result.png`, `currie-route-saved-review.png`,
`currie-route-saved-zones.json`, `currie-route-low-visual.png`,
`currie-route-export-preview.png`, `currie-route-free-export.png`,
`currie-route-rear-view.png`, and `currie-route-rear-feedback.png`.
`currie-route-evidence-sha256.json` records hashes and byte sizes for this
finite evidence set.

Focused route/pick tests, TypeScript and changed-file lint passed. Browser
checks used local Chrome at 1440×900 on the disposable project. This is a
concept-geometry and student-control pass, not accessibility or architectural
asset approval.
