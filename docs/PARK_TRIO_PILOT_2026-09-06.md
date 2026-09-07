# Three new park pilots — 2026-09-06

Status: local visual-review candidates on `codex/new-park-trio`. Not published
to the seed catalogue or Git main. No image/video generation calls were used.

## What was built

| Difficulty | New assembly | Contents | Minimum plot |
| --- | --- | --- | --- |
| Easy | Outdoor cinema lawn | Screen, optional projection booth, audience benches, perimeter trees and loop | 32 × 45 m |
| Medium | Teaching demonstration garden | Curved timber shelter, 6–12 raised beds and interpretation panels, gravel court and connected paths | 32 × 40 m |
| Complex | Wave-canopy concert lawn | Continuous curved stage roof, supporting structure, lighting, speakers, ramp, 16 four-chair units and audience routes | 80 × 80 m |

The source illustrations already existed in the catalogue. Searches of prior
work found no completed 3D trial for these exact variants. These are new 3D
assemblies, not newly commissioned reference images. All three source views
were inspected per park. The concert references disagree about the number of
stages; this candidate deliberately contains one coherent stage.

Native equipment stays at metric size. Paths and lawn adapt; whole modules are
added or omitted within bounded layouts. Unsupported narrow/concave plots
report a constraint instead of cropping equipment. Exact parent, variant and
`park_trio_layout: park-trio-v3` identify the assembly. Placement cards require
the development-only trial flag, so existing catalogue variants are unchanged.

## Local review

- App: http://127.0.0.1:5176/projects/527717ba-6204-4bee-a7a2-99ee094f54d3
- Geometry lab: http://127.0.0.1:5176/park-trio.html
- External outputs: `C:/dev-artifacts/CityPrompt/park-trio-2026-09-06`
- Build/launch instructions: `tools/park_trio/README.md`
- Reviewed source/model hashes: `tools/park_trio/candidates/*.json`

The existing frontend on port 5174 was left alone. The pilot uses the existing
isolated backend on port 8002. Provider image/video keys remain disabled.

The project and initial boundary were created through the student UI; the
concert park was placed through the UI. For the three-park comparison, cinema
and garden were added through API fixtures. The boundary was tightened through
the API to an open rectangle at Fort Calgary after canopy contamination caused
the existing ground sampler to reject the first boundary. This was not an
entirely manual three-park trial. No ground quality safeguard was disabled.

Save/reload retained all three variants and their layout revision. Ground
alignment passed with 1,107 samples, two passes, zero misses and maximum local
residual 0.130 m. It also returned to ready after zooming. Resampling took about
137 seconds at that camera; this existing terrain pipeline remains a usability
issue, and the parks are withheld while alignment is pending.

The free direct-capture check passed at 1600 × 936 with 9.6% proposal/park
coverage. Beauty and identification masks were displayed. This checks capture
plumbing, not AI image fidelity; no paid render was produced.

## Verification and fixes

- Narrow layout/profile/access/catalogue regression run: 150 tests passed.
- Subsequent final integration run covering layout, new cards, catalogue,
  automatic 3D and access: 44 tests passed. These runs overlap; do not add totals.
- TypeScript type-check and targeted ESLint passed after production edits.
- All seven GLBs loaded and had minimum Y = 0 and finite metric bounds.
  Combined model size is approximately 3.84 MB, excluding reused trees/textures.
- External public preparation script passed an idempotent run.
- Browser console had no reported errors during the trial.
- Visual checks include compact garden on a slope, compact concert,
  cinema overview and all three together on Google tiles. Narrow garden and
  concave cinema correctly reported layout constraints. Automated layout tests
  cover minimum, standard, large and rotated plots.

Corrections made during the pilot: garden labels no longer overlap beds;
circulation avoids bed footprints; tree spacing no longer produces a nearly
empty perimeter; concert walls follow the roof; lights/speakers fit below the
canopy; preview renders the selected park rather than the neighbourhood park;
all three cards appear under supported catalogue groups. Artificial audience
grading was removed because it introduced surface conflicts.

Useful inspected screenshots under the external output root:

- `three-parks-close.png`: all three on Google tiles after successful resampling.
- `garden-compact-verified.png`: compact garden on synthetic sloping ground.
- `concert-compact-slope-final.png`: compact concert review; inspect checkbox
  state in the image rather than infer terrain settings from its filename.
- `garden-narrow-constraint.png`: no equipment squeezed into a narrow strip.

Earlier screenshots can be stale following Vite HMR or failed browser control
commands. File names alone are not evidence of their selected park/settings.

## Remaining work before catalogue promotion

1. Review the actual visuals with the user. Garden plant clusters still look
   faceted; planting/material detail could be improved before a final candidate.
2. Resolve small Google mesh patches showing through sampled lawns. The shared
   terrain grid passes quality checks but cannot represent every photogrammetry
   bump. Raising the entire park would disguise the issue and risk floating.
3. Improve grading and path transitions around large level structure pads on
   slopes. `gradingReviewRequired` metadata is present but is not an engineered
   access design or a student-facing grading report. Audience terraces remain
   deferred. Moving previews use a flat datum; saved geometry uses shared ground.
4. Surface fit constraints clearly in the normal editing flow before supporting
   arbitrary polygon shapes. The lab exposes the constraint; it is not a
   complete general-purpose park packing solution.
5. After visual approval, promote only reviewed GLBs through the runtime asset
   process, update the main catalogue and run publication verification. Keep
   heavyweight experiments external. No push/publication was done in this task.
