# Image presentation checkpoint

The Present → Image panel keeps all 22 established styles in its main picker,
with their original names and Realistic, Accurate, Concept, Plan and Stylized
groups. On 16 September the user clarified that this full creative collection
must remain readily visible. The temporary five-preset simplification was
removed; styles no longer require opening Advanced image controls. Existing
style IDs, prompts, availability gates and rendering modes remain connected to
the same pipeline. Projection-changing styles explain that distinction when
selected, rather than pretending they preserve the source camera.

Add People and Add Vehicles default off. Explicit boolean selections persist
with the project-scoped session draft, survive panel reopening, travel through
the existing Direct 3D request and are recorded in its server source snapshot.
The server's final instructions override conflicting style/custom text, preserve
already captured context and constrain additions to plausible existing surfaces.
This controls requests; actual generated entourage still needs visual acceptance.

Provider comparison and custom directions remain under Advanced image controls. Normal image generation selects one account
default engine. Three-engine comparison remains an explicit advanced choice.
Source masks and diagnostics are under Source checks. A free current-view export
remains visible beside the generation action, including when generation is
unavailable. Known unavailable engines cannot be submitted. Network/availability
failures explain recovery without losing the draft or automatically retrying.

## Verification

Local evidence: `C:/dev-artifacts/CityPrompt/student-design-transformation/`.

- 41 frontend cases across presentation controls, draft persistence, model
  choice, Direct 3D adapter and panel contracts; TypeScript and changed-file
  ESLint pass.
- Existing Direct 3D tests plus render-fidelity/provenance tests exercised the
  provider request, strict defaults, four explicit toggle combinations, bounded
  final prompt and unchanged plan/camera hashes. The initial legacy wording
  assertion was resolved by preserving “existing cafe seating”; no test gate was
  weakened. 18 provenance cases and 8 provider-payload combinations pass after
  the adjustment; the other 166 Direct cases passed in the earlier full run.
- Actual browser controls preserve exact ECEF camera position/quaternion through
  style/toggle changes and closing/reopening. Free export produced the frozen
  aerial source. Keyboard Tab/Enter selected a preset with visible focus.
- Desktop 1600×1000, laptop 1366×768 and tablet 1024×768 screenshots inspected;
  export/generate actions remain within the viewport, without horizontal overflow.
- One real request reached the local API and stopped at configured-provider
  unavailability before reservation. Its extracted contract contains the chosen
  style, people=true, vehicles=false, camera and current source claims. A second
  request was deliberately aborted to exercise recovery. Neither retried.
  Temporary network routes were removed. No paid image request was made.

Screenshots use `PHASE10-*`; extracted request evidence omits headers/secrets.
These checks accept the controls, not finished-image fidelity or visual quality.
Those remain separate gates, as do video and the full first-time journey.

## Grounding finding retained

The frozen Gold Standard still has an unfinished prepared-site edge. Reviewing
the original Google surface measured 1096.4–1129.1 m, including captured roofs;
boundary samples imply up to 5.6 m fill and 24.5 m cut at its authored 1102 m level.
Automatically turning that profile into walls would misrepresent ground.
`phase7-prepared-review.json` and `PHASE7-PREPARED-REVIEW-ROOFS.png` retain evidence.
The benchmark was not moved, regraded or edited to conceal this release issue.

## Full style collection restored

All 22 buttons are outside collapsed controls and retain their original labels.
They use labelled category groups, visible selected states, keyboard focus and
44px minimum target heights. The panel has more desktop height, while smaller
viewports scroll the styles with the export/generate actions kept visible.
Fourteen focused cases cover full style discovery/selection, availability gates,
projection wording, original style contracts and draft persistence. This UI
correction makes no paid image calls and does not change saved render styles.

Browser selection of all 22 styles preserved the exact live camera and verified
that no style lives inside Advanced. Desktop 1600×1000, laptop 1366×768 and
1024×768 views were inspected; lower styles remain reachable by scrolling,
keyboard focus is visible and primary actions remain inside the viewport.
An extraction-time missing import was caught by type-check/browser, fixed and
retested; no new error followed the final style-selection loop and no failed
requests occurred. Evidence: `PHASE10-RESTORED-STYLES-*`,
`phase10-restored-styles.json`, `phase10-restored-style-viewports.json`.
The existing Documentary direction was restored to flat natural daylight;
explicit people/vehicle selection remains enforced. Another 28 Direct 3D
adapter cases pass (42 focused cases total for this correction).
