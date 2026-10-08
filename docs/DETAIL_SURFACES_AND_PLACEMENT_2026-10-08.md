# Detail surfaces and placement follow-up

## Scope

Follow-up to the Crossroads Plaza student trial: custom paving, reliable detail
placement, and visible separation between a park's reserved parcel and its fixed
model layout. No catalogue assets, existing park models, or deployment settings
were changed.

## Student controls

- Open **Add details → Custom paving**. Choose light concrete, warm brick, or
  asphalt, click at least three corners on the plan, then **Finish paving**.
- Select paving to change its material, move the whole area, move an individual
  corner, or remove it. Paving and furniture share Undo and Save details.
- **Move on plan** retains the intended object when the destination intersects
  another marker. A collision leaves that object selected for another attempt.
- A selected native park shows its reserved parcel with an amber dashed outline
  and its fixed layout with a solid green outline. These guides are excluded from
  walking and image capture. Enlarging the parcel does not stretch its equipment.

## Implementation

Paving is stored in project scene-details metadata with the existing ownership
checks and revision conflict control. Older clients that omit surfaces preserve
them; an explicit empty list removes them. Requests validate materials, unique
IDs, finite coordinates, non-crossing polygons, and limits of 64 surfaces and 64
corners per surface. Each surface is 1–250,000 square metres and at most 2 km across.

The globe triangulates each polygon and reuses lightweight street surface
textures. Heights resolve against authored site ground before falling back to
survey or Google terrain samples. Surfaces do not intercept selection or introduce
walking obstacles. They do not clear existing buildings or regrade terrain.
Outside prepared sites, height interpolation uses polygon vertices rather than
a densely sampled terrain mesh; uneven terrain may require smaller areas.

## Verification

- Seven focused Vitest files: 34 tests passed, including selection interception,
  paving editing/undo/save, triangulation, ground height, and existing detail and
  park-reservation behavior.
- Backend project-details suite: 16 tests passed, including ownership/revision
  controls and surface validation/round-trip/legacy preservation.
- TypeScript type-check, focused ESLint, and Git whitespace checks passed.
- Crossroads Plaza browser trial: two paving areas created, an asphalt corner
  edited, tree placement over another marker correctly retained selection, and a
  bicycle pump moved to the plaza. Both surfaces and all 38 details survived reload.
- Corrected a floating-surface issue discovered during 3D review; surfaces now
  follow the prepared site ground. Visually checked the distinction between the
  enlarged 36 × 40 m park parcel and its original 32 × 28 m layout.
- The final additional walking check was interrupted by an expired browser login;
  no walking performance result is claimed for this change.

Trial project: `9577e98b-99a9-4d1a-a78b-fd973acadc13`.
Local browser evidence and backend log are outside Git at
`C:/dev-artifacts/CityPrompt/detail-surfaces-2026-10-08/`.

This is a local source checkpoint, not a production deployment.
