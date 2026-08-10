# Moorish Sticker Landmark V89 Pilot

This is a bounded Sticker Method/select-and-place pilot for the two-storey
Moorish arcade bazaar. It is **not approved for catalogue release**. Machine
validation and source-to-GLB surface parity pass, but the final architect score
is 71/100 against an 85/100 release threshold.

## Exact references

- [Street archetype](./archetype-street.png)
- [Oblique archetype](./archetype-oblique.jpg)
- [Roof archetype](./archetype-roof.jpg)

## Baseline and final candidate

- [V88 baseline street match](./baseline-v88-archetype-match.png)
- [V88 baseline oblique](./baseline-v88-oblique.png)
- [V89 final archetype match](./final-v89-archetype-match.png)
- [V89 final street](./final-v89-street.png)
- [V89 final oblique](./final-v89-oblique.png)
- [V89 final rear oblique](./final-v89-rear-oblique.png)
- [V89 final roof audit](./final-v89-roof-audit.png)
- [V89 final facade close-up](./final-v89-facade-close.png)

## Quality-gate evidence

The preserved rejected street frames show why per-building architectural review
must remain independent from machine validation:

- [64/100: generic semicircular teal barrels](./rejected-64-v89-archetype-match.png)
- [77/100: inset plaster tunnel, but Gothic ogive profile](./rejected-77-v89-archetype-match.png)
- [69/100: over-corrected mushroom/spade profile](./rejected-69-v89-archetype-match.png)
- 71/100 final: smoother trace-based spline, still too broad and dominant.

See [architect-review.json](./architect-review.json),
[visual-approval.json](./visual-approval.json),
[validation-report.json](./validation-report.json) and
[surface-finish-report.json](./surface-finish-report.json).

## What worked

- Fixed 20 m × 15 m, two-storey select-and-place landmark contract.
- Three real 6.2 m deep street passages and two real 3 m deep return passages.
- Selective use of the accurate podium and one-row crown sheets; inaccurate
  metadata-authored extra storeys were discarded.
- Separate front/right sticker clearances, plaster tunnel lining, turquoise
  lower reveals, warm occupied backs, timber market counters and authored
  side/rear skins.
- Thin terracotta coping and a complete fine four-sided lattice parapet.
- 20 targeted compiler/quality-contract tests pass; GLB validation and neutral
  surface parity pass.

## Release blocker and pipeline lesson

The portal silhouette is the landmark identity. Approximate style formulas are
not adequate even when they produce real depth. The next implementation must
extract the actual binary **inner negative opening** contour, validate its
centre, neck, shoulder, crown and scale anchors, then use that exact contour to
cut the sticker and extrude an inset passage. The lining should read only as a
narrow reveal behind the decorated facade, never as a second foreground arch.

This lesson is now recorded in the V89 high-quality building memory. Until the
contour-extraction gate exists and this pilot clears 85/100, it remains
`rejected_research_pilot` and does not enter the catalogue.
