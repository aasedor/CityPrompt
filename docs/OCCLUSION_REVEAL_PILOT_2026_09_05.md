# Occlusion and reveal pilot — 5 September 2026

## Result

Two paid image requests completed against the same saved Fort Calgary test
scene. The playground stayed hidden behind a bungalow in camera K and appeared
in the expected part of the park in camera I. This is encouraging occlusion
evidence, but neither image passed the existing precise geometry checks.

- **K, partially hidden park:** the pavilion remained visible through the gap
  and no displaced playground was evident. The AI redesigned the bungalow's
  porch, windows and gable. Overall geometry failed.
- **I, park reveal:** pavilion and play structure retained their broad source
  positions. Small planting details appeared. Global silhouette and semantic
  checks passed, but the weakest connected semantic component scored 0.678571
  against the 0.72 threshold. Exact local geometry was not verified.

Both responses were marked `review_required` and delivered the native source
using `authoritative_source`. Raw AI originals were saved separately for review.
An attractive image is not evidence of a faithful plan; thresholds were not
relaxed to accept these outputs.

## Reproducible camera and visibility evidence

Local project: `9535da89-4b5c-4839-aa7f-ccde56f1eded`, available through
`http://127.0.0.1:5174/projects/9535da89-4b5c-4839-aa7f-ccde56f1eded`.
The scene contains houses, a neighbourhood park and a street on the Fort Calgary
field. No authored objects moved between the views.

Coordinates below are local metres relative to longitude -114.0467655,
latitude 51.045496. Camera height is 1.7 m above the measured shared ground.
Both cameras aim toward park-local `(0, -23, 1.7)`.

| Camera | Local camera x/y | Field of view | Purpose |
| --- | --- | --- | --- |
| K | -12 / 45 | 40 degrees | Bungalow hides playground; pavilion visible through gap |
| I | -5 / 5 | 70 degrees | Reveal the same park from nearer the street |

A temporary component-ID capture identified `pavilion-1` and `tower-1` inside
the park. A second K diagnostic hid building-tagged nodes to distinguish actual
occlusion from an object outside the frame. These diagnostic images were never
sent to the provider. All temporary tags, visibility and camera changes were
restored after capture.

| Native capture | Pavilion pixels | Play tower pixels |
| --- | ---: | ---: |
| K, buildings visible | 2,465 | 0 |
| K, buildings hidden for diagnosis | 2,465 | 1,441 |
| I, reveal | 9,294 | 12,334 |

These component IDs are diagnostic evidence, not yet a production mechanism for
automatic playground-level acceptance.

## Fix implemented after the paid trial

The K request included catalogue instructions to reproduce facade openings,
roof character and a full-width porch with brick piers. That conflicts with
finishing the already placed 3D bungalow. The observed redesign resembles these
instructions, although this trial does not establish them as its sole cause.

For **precise, same-camera scene** requests:

- The frontend skips fetching and submitting whole-building catalogue images.
- The backend independently omits catalogue images and `design_identity` prose
  from provider conditioning, including for older clients.
- The original scene and seven source/control images remain authoritative.
  Full server inventory is preserved for validation, protection and auditing.
- Ordinary same-camera styles now default to Precise. Explicit Balanced mode
  and expressive/reprojected styles retain their existing conditioning paths.
- Default photorealistic art direction preserves existing openings and public
  realm features instead of requesting floor-to-ceiling glazing or new planting.
- The render panel explains the possible source fallback and removes the
  unsupported claim of a survey-grade structure lock.

The **paid images predate this fix**. No paid visual claim about the corrected
conditioning has been made. Network-free audits of the actual saved K and I
requests confirmed seven source/control images, no catalogue references, no
design-identity prose and all five server inventory entries retained.

## Verification and cost

- Backend: 155 Direct 3D tests and 14 presentation-first tests passed.
- Frontend: 20 focused hook, panel and API tests passed.
- TypeScript type check and touched-file ESLint passed.
- Backend Ruff and Black checks passed.
- Source diff whitespace check passed before checkpoint.

Two paid image calls, no automatic retries, no video:

| Request | Estimated USD |
| --- | ---: |
| K | 0.144471 |
| I | 0.129733 |
| This batch | 0.274204 |

The cumulative estimate, including earlier conservative failed-call holds and a
video reservation, is **US$6.890992**, within the authorized US$10 ceiling. These
are usage-based estimates, not a reconciled billing statement.

## Artifacts and next checkpoint

Generated captures, provider outputs and diagnostics remain ignored under
`artifacts/occlusion-pilot/`; they are not source deliverables:

- `reveal-pilot-review.html`: embedded source/AI comparisons and interactive divider.
- `reveal-pilot-review.json`: metrics, findings and implementation status.
- `reveal-pilot-paid-ledger.json`: bounded request ledger.
- `K-bundle.json`, `I-bundle.json`: frozen inputs.
- `K-component-visibility.json`, `I-component-visibility.json`: component evidence.
- `K-corrected-request-audit.json`, `I-corrected-request-audit.json`: network-free payload audits.

Next, run one corrected K request against its exact saved source and compare
porch, roof and openings with the pre-fix output. Continue only after reviewing
that finite checkpoint. If AI finishing still redesigns the scene, improve
native materials and lighting rather than weakening geometry checks. Stable
runtime component IDs would support stronger park-level regression coverage.

Changes are checkpointed locally on `codex/occlusion-finish-contract`. They have
not been pushed or deployed. Existing long-running backend processes were not
restarted; corrected payload audits used fresh isolated Python processes.
