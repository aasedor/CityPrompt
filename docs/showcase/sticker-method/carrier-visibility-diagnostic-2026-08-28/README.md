# RLASM carrier-visibility diagnostic — 2026-08-28

Status: **diagnostic evidence, not approved final buildings**

The prior ten-building batch was incorrectly marked as passed. Coastal and
Chateauesque exposed large rectangular support carriers from aerial/oblique
views. The paired images preserve the failure and the bounded topology repair:

- `coastal-before-exposed-box.png` — rejected full rectangular upper carrier.
- `coastal-topology-correction-not-approved.png` — U-shaped upper wings and a
  physical hip roof; material prework still requires replacement.
- `chateau-before-exposed-box.png` — rejected solid hotel block and flat cap.
- `chateau-topology-correction-not-approved.png` — perimeter wings, open court,
  and physical wing roofs; material prework still requires replacement.

The corrections are intentionally labeled **not approved** because the same
audit found that the original prework generator treated arbitrary photo crops
containing sky, gables, or other unique architecture as repeatable material
swatches. RLASM 1.8.0 now blocks both failure classes:

1. front-corner, aerial/top, and side/rear carrier-visibility review is
   mandatory;
2. hidden boxes, flat caps, and topology-substitute slabs are hard failures;
3. materials bind by declared role ID rather than list position; and
4. material crops require explicit repeatable-field/atomicity approval before
   a build or final comparison can pass.
