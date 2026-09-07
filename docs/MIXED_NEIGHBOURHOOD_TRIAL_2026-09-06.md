# Mixed neighbourhood local trial — 2026-09-06

Local project: http://127.0.0.1:5178/projects/75987ecb-95af-40af-9336-d07bf90ba216

Test checkout: `C:/dev/CityPrompt-building-next3`, branch `codex/mixed-neighbourhood-render-trial`. This combines main a63f3f7fc with the existing gated park pilot (cherry-pick eb4ea26fa). It does not publish the park pilots to the main catalogue. The user's original dirty workspace was preserved.

## Scene and method

Created a new project through the student UI on open ground west of the earlier Fort Calgary trial. Picked and placed six catalogue objects, avoiding existing buildings:

- Beltline brick mixed-use mid-rise — 39 × 39 m plot.
- Rammed-earth timber infill — 18 × 24 m plot.
- Classic courtyard motel — 29 × 42 m plot.
- Neighbourhood park — 40 × 35 m.
- Teaching demonstration garden — 32 × 40 m.
- Outdoor cinema lawn — 32 × 45 m.

Used catalogue cards, placement, selection, drag and camera controls. The existing development camera-framing helper assisted navigation, so this is assisted browser QA rather than a completely unaided novice usability trial. No project objects were inserted directly into the database. Database reads confirmed six saved zones. Reload restored all six objects and the saved 3D scene.

## Capture checks

Used the student Render panel's **Check Direct Capture** button. All three free checks returned beauty, mask, class-ID and instance-ID previews at 1600 × 936 without a capture error:

| View | Proposal coverage | Ground | Park | Building |
| --- | ---: | ---: | ---: | ---: |
| Aerial overview | 10.3% | 1.0% | 5.4% | 3.9% |
| Close oblique | 29.5% | 3.5% | 20.4% | 5.6% |
| Low angle, partial objects and tree occlusion | 35.6% | 2.8% | 11.0% | 21.8% |

These are source capture checks, **not AI output consistency tests**. No paid renders ran. Automatic approval review rejected enabling the paid provider in the isolated backend with only “blocked by policy.” The backend remained unchanged with paid providers disabled; the five-render allowance was unused. No bypass was attempted.

## Findings and next work

1. All three building identities loaded alongside three different park types. Automatic 3D saving and reload worked. No browser page errors were reported. The overlap guard rejected a motel placement clipping the park; moving to clear ground resolved it.
2. The trial still reads as separate plots. Existing Google paths are visual context; choosing a park does not automatically connect its internal routes to those paths. Add explicit entrance placement/snapping and a short connector workflow, with grade checks, before claiming automatic neighbourhood integration.
3. Flat ground pads have conspicuous rectangular edges against the Google surface. Pale edge seams and patchy surfaces were visible in some views. Refine local grade transitions and investigate the transient surface overlays independently of the catalogue assets. No numerical terrain-fit guarantee was established: the shared-ground debug state was inactive, with no reported grounding issues.
4. Right-dragging over a park also selected it and opened the reshape panel during the orbit. Reproduce with a normal desktop mouse and prevent selection after an orbit gesture if confirmed.
5. The low-angle view naturally hides elements behind trees/buildings and crops others. The source capture succeeded, but whether an AI finish preserves those occlusions remains untested until paid rendering is available.

## Verification and outputs

- 46 focused tests passed: park trio assets, park trio layout and community compiler.
- `npm run type-check` passed.
- `git diff --check` passed before this report was committed.
- Generated screenshots and capture transcripts are outside Git under `C:/dev-artifacts/CityPrompt/mixed-neighbourhood-2026-09-06/`.
- Useful images: `reloaded-scene.png`, `close-oblique.png`, `low-angle.png`.
- The browser-open request to the Codex panel was queued. The trial itself was exercised in the browser automation session.
