# Scottish Baronial v68 rebuild

This no-install pilot used the existing OpenCV, NumPy and Blender toolchain to
reconstruct the Scottish Baronial railway hotel from its three exact archetype
views. It is a meaningful massing improvement, but remains **review-only**
rather than joining the four-family catalogue gold set.

![Street identity comparison](street-identity-comparison.png)

![Roof-plan comparison](roof-plan-comparison.png)

## What improved

- Replaced the inherited solid hotel box with a real open perimeter quadrangle.
- Centered the crenellated gate tower and arched arrival on the street facade.
- Added fixed crow-stepped gables, four cylindrical corner turrets, steep slate
  perimeter roofs, chimneys and a gate-tower bartizan.
- Wrapped facade treatment around exterior returns and the courtyard walls.
- Added a camera-locked OpenCV regression report for silhouette, roofline and
  aspect ratio without installing any additional software.

## Measured result

| Gate | v67 baseline | v68 rebuild | Threshold |
| --- | ---: | ---: | ---: |
| Silhouette IoU | 0.90118 | 0.89148 | >= 0.62 |
| Roofline RMSE | 0.04818 | 0.05409 | <= 0.12 |
| Aspect-ratio error | 0.09258 | 0.09258 | <= 0.16 |

Both pass. The nearly flat automated result is intentional evidence that an
outer-boundary metric cannot detect a missing courtyard or incorrectly assigned
tower peaks. The pipeline therefore treats OpenCV as a regression gate, not a
visual-approval replacement.

![Fidelity overlay](fidelity-overlay.png)

## Remaining review items

- Gable and cylindrical-turret opening patterns need archetype-specific local
  schedules rather than generic or duplicated physical window kits.
- The cached repeatable facade sheet is credible granite, but its cadence is
  more regular than the source building's localized tower and pavilion bays.
- The model should receive one live Google Tiles material/exposure review before
  any catalogue promotion.

Individual outputs: [archetype-match](final-archetype-match.png) and
[aerial](final-aerial.png).
