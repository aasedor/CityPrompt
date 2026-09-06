# Fresh student workflow trial — Currie

Project: **Student journey - Currie empty-site trial**

Local URL: http://127.0.0.1:5174/projects/4befd3ec-277f-4bd3-803e-ef9addd32bdd

## Actions tested

- Signed out and signed back in using the local student account.
- Created the project through New Project, searched Currie Barracks, selected
  the suggested location and opened the project.
- Inspected the Google tiles and drew a roughly 9,000 square metre boundary
  inside a visibly unbuilt lot. This verifies the displayed imagery, not the
  current ownership or development status of the real land.
- Used the SITE action and overhead view to draw four corners and finish with
  Enter. Follow existing terrain was the default; shared ground reached ready.
- Placed an infill home. A 36 m width was correctly rejected because it crossed
  the boundary; 24 m succeeded and produced two whole homes.
- Placed a bungalow with its own 15 x 24 m plot.
- Filtered the catalogue to parks, placed a 40 x 35 m park, then reduced its
  depth to 30 m. The panel explained that play pockets and the pavilion were
  omitted while a swing remained. Geometry retained a walking loop.
- Filtered to local streets and drew a two-point, approximately 93 m route.
  The selected 16 m section appeared without a separate Generate action.
- Opened Team and inspected invitation and presentation-link controls. No
  invitations were sent or public links enabled; recipient access is not
  claimed tested in this run.
- Requested the existing free planning report, saved a student response and
  used Download printable report. The report explicitly noted missing saved
  local-policy passages and unresolved building floor-area quantities.
- Reloaded the project. All five zones retained their coordinates and asset
  identities. The student response also reappeared in the saved report.
- Used Focus Building and a wheel gesture to frame the scene more closely.
  A free capture reported 10.9% proposal coverage; the park extends below the
  image edge. Its controls included beauty, mask, class IDs and instance IDs.

The automated browser's mouse-wheel command emitted an event at (0,0), despite
the preceding pointer move. A wheel event dispatched to the visible canvas
tested the application's normal zoom handler. This was a driver limitation,
not evidence of an application zoom defect. All design creation and resizing
used the UI; no geometry was seeded directly into the database.

## Findings

1. **Fixed:** the selected-model hint still instructed students to regenerate.
   Placed catalogue objects now explain that 3D updates automatically after
   saving, and point to the reshape panel. Custom-drawing guidance is retained.
2. **Usability follow-up:** at 1264 x 625, the tall catalogue and toolbar require
   substantial scrolling. Keep actions easier to reach in a future compact
   layout pass; do not confuse this with a save or placement failure.
3. **Expected constraint:** increasing a plot around its centre can push it
   outside the boundary. The rejection message was correct, but a visual
   prospective outline would make the cause clearer before Apply.
4. **Ground continuity:** zooming into fresh tile detail temporarily hides
   authored geometry while the site is resampled. It recovered to ready.
   This remains a visible interruption, not proof of survey-grade alignment.
5. **Connections need deliberate design:** the drawn street is a dead-end
   internal route. This trial does not establish a valid connection to the
   surrounding real road or a complete accessible route into the park.
6. **Report capability correction:** report generation, saved responses and
   printable HTML already exist. The earlier conversational description of
   these as entirely future work was incomplete. Local policy grounding and
   complete quantities still need attention.

UI screenshots, source captures and reload evidence are ignored local artifacts
under `artifacts/occlusion-pilot/student-*`. No historical projects were changed.

## Render and final checkpoint

One paid Photo Realistic / Precise render was submitted through the normal
Render Direct 3D button, using the default instructions. The actual backend log
confirmed seven source/control images and no catalogue reference images.
It returned HTTP 200, with an estimated cost of US$0.130443. The cumulative
usage estimate plus earlier conservative reservations is US$7.021435, within
the US$10 allowance. No retry or video call was made.

The AI broadly retained the houses, street and partly cropped park, but changed
architectural finishes/details and added scene elements. Strict silhouette,
instance-presence and unsupported-structure checks failed. The app returned the
authoritative 3D source and retained the separate AI attempt in Project Renders.
The warning was visible before acceptance. This is a successful delivery and
safety-path test, not a passed image-fidelity test.

The diagnostic panel misleadingly described rejected candidate evidence as
missing instances in the returned source. For an authoritative-source fallback,
it now states that the original 3D view was returned and omits those intermediate
returned-image checks. Backend thresholds and generated images are unchanged.

The printable report was verified on disk:
`C:/Users/andre/Downloads/planning-report-ea5a2f7f-797e-44aa-993f-75876f3d206d.html`.

46 focused placement, report and render-panel tests passed, as did TypeScript
checking, scoped ESLint and the source diff whitespace check. The source edits
are limited to the two UI guidance fixes and this record; assets and student
trial evidence are separate. No production deployment or push was performed.
