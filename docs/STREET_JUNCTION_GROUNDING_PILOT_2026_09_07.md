# Street junction and public-road connection pilot

Local branch: `codex/street-junction-grounding`. Not published to main.

Trial project: **Student trial - Currie 20-building community**, ID
`3c12dda6-3b15-4151-bf8b-eb59628a99ff`.
Local URL: http://127.0.0.1:5178/projects/3c12dda6-3b15-4151-bf8b-eb59628a99ff

This isolated checkout uses port 5178 to avoid the separate working copy on
5174. Source is in `C:/dev/CityPrompt-building-next3`. The original OneDrive
checkout and its unrelated building work were not edited.

## Result

- Retained all twenty buildings, the measured neighbourhood park and original
  parcel boundary. The final shared ground status was ready with no building
  grounding issues.
- Extended the existing 20 m collector approximately 15 m east to the visible
  edge of Quesnay Wood Drive SW. No whole-site boundary extension or flattening.
- The collector/shared street, shared street/park approach, and shared
  street/5 m green alley now form three actual T-junctions.
- Junctions own disjoint pavement and pedestrian surfaces. Crossings follow
  the carriageway bounds, including support for asymmetric and reversed
  sections. A closed T side stays closed. Raised sidewalks have physical ramp
  openings and sloped warning pads; flush shared streets do not get invented
  raised sidewalks. The collector junction has three crossings and six ramps.
- Removed planters, associated trees, benches and signs from junction clearance
  areas. Close inspection caught and removed a yield sign in a ramp approach.

## Ground and editing changes

The street inspector now offers **Connect to a public road**. With this option
enabled, one end may extend up to 30 m beyond the parcel. The server checks the
route, full street buffer, outside distance and parcel overlap. This does not
allow buildings or parks outside the site. A connection must be brought back
inside before its option can be disabled; the inspector explains this inline.

An extending street receives a bounded ground grid aligned with the original
site grid. It reuses verified overlapping vertices, measures new vertices in
two stable passes, and retains the existing slope/discontinuity checks. It
does not re-grid the twenty building foundations. Capture waits for this
additional ground field instead of silently omitting a loading street.

Close views exposed two independent defects: an old independently seated road
fill covered the collector bands, and original Google mesh fragments pierced
crossings. The detailed connection now owns its visible surface, while an
invisible editor hit target preserves street selection. New fixed-section
catalogue streets clear the original Google surface inside constructed bands;
the four pilot roads were also opted in. Transparent outer setbacks retain
Google terrain. Ray measurements still use the actual Google mesh, and the
park and surrounding terrain remain unchanged. Existing explicit mask
preferences on other saved projects are not migrated.

## Verification and evidence

- 67 frontend tests passed across eleven focused files, including junction
  geometry, topology, shared-ground triangulation, extension alignment, capture
  readiness, street masking, placement and the section inspector.
- TypeScript type-check passed. ESLint passed on changed TypeScript files.
- 185 backend tests passed across direct-render validation, public connections,
  optional boundaries and site-zone utilities. The 24 boundary/connection/utils
  tests were rerun after the final validation refinement and passed.
- Live project persisted/reloaded the extension, retained twenty buildings,
  and reported ready site and street ground. Street selection opened the new
  inspector. A trial of disabling an external connection preserved the saved
  road; the UI was then refined to explain returning the endpoint first.
- Free capture checks passed for the overview and close junction view, including
  a close frame with 71.9% proposal coverage (18.4% street, 53.5% building).
  These were capture checks, not paid AI finishes. App balance stayed 8,935.

Generated evidence and project backups are outside Git:
`C:/dev-artifacts/CityPrompt/street-junction-grounding-2026-09-07/`.
Useful images: `07-junction-cleared-ground.png` (before removing the yield sign),
`10-junction-top.png` (final unobstructed crossing layout), and
`11-public-road-tie-in.png` (public-road end). Earlier numbered images document
the defects; they must not be presented as the final state.

## Limits and next pilot

This is conceptual planning geometry, not a surveyed or approved road design.
The public-road end reaches the mapped road edge; it does not reconstruct
existing public-road curb returns or automatically infer sidewalk geometry
from photogrammetry. A next bounded pilot should use an explicitly selected
imported road/sidewalk edge to author those returns and the terminal crossing.
Reference layers remain optional.

Automatic owned junction surfaces remain limited to sufficiently long,
near-orthogonal T/X connections with compatible opposing sections. Skewed
junctions, turning radii, drainage and verified accessible grades need further
work. Shared-street junctions currently use the through street's material for
the junction patch; mixed material transitions can be refined separately.
