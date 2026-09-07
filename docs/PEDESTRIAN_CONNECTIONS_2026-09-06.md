# Editable pedestrian connections

## Student workflow

Select a building, park or street and open **Connections**. The button is
available in the simple reshape panels and in the advanced zone panel.

- **Building:** enable a linked entrance, choose a street/path target, and set
  the door or bottom-of-steps position in the plot's local metre frame. The
  walkway follows translation and rotation. Proportional offsets follow plot
  resizing when enabled; native unscaled houses default to fixed metre offsets.
- **Park:** choose an edge, a position along it and a sidewalk target. This locks
  the entrance to that edge through movement, rotation and resizing. Disable the
  lock to return to automatic placement. Legacy authored access points are only
  replaced when the student explicitly saves these controls.
- **Street:** add up to eight deliberate raised crossings. Each uses a fraction
  of the route length, so it follows street movement and reshaping. A crossing
  joins both sidewalks across the boulevards, includes zebra markings and short
  vehicle ramps, and reserves clearance in the procedural furniture layout.

Save uses the existing revision-checked zone update and undo/redo infrastructure.
The connection check in the dialog explains unresolved geometry. It does not
prevent the student from saving their design.

## Data and rendering

Authored relationships live in `SiteZone.properties`:

- `pedestrian_building_entrance`: version, local metre offsets, reference plot
  dimensions, proportional-scaling choice, target street ID and width.
- `pedestrian_park_entrance`: version, polygon edge index, fraction and target
  street ID. The existing park solver handles the entrance-to-internal-network
  route, obstacle checks and furniture clearances.
- `pedestrian_crossings`: stable IDs, route fractions and widths.

No independent generated walkway zone is written. The same saved relationships
derive the visible 3D geometry after every edit/reload. They participate in the
authored-change key and the existing capture source-signature checks. New
geometry carries explicit street-class and source-zone tags for direct capture.

Surfaces use the measured shared ground triangulation, or the prepared site
datum. Unknown ground does not produce a guessed floating strip. The crossing
surface sits at sidewalk level; its vehicle ramps meet the motor/cycle bands.
This is conceptual design geometry, not accessibility or engineering approval.

## Bounds and remaining limitations

- The first release supports **one manually positioned entrance per rectangular
  building plot**. Door locations have not been automatically inferred or
  verified for the entire catalogue. Check the actual model, especially if
  increasing a native-house plot adds dwellings.
- Building approaches are straight, up to 30 m, and target the near pedestrian
  band. They do not create an unplanned road crossing or a route through another
  building. A door facing away from the target remains unresolved.
- Editable parks use the layouts supported by the existing access solver:
  neighbourhood/pocket park variants and the park trio. Unsupported parks and
  nonrectangular building plots show an explanation.
- Crossings require supported sidewalks on both sides and room away from route
  ends, bends, intersections, other crossings and obstacles. Street furniture
  uses the existing conservative junction-clearance distance around them.
- Automatic routing around a building, verified catalogue door metadata,
  multiple doors per plot, tactile-detail design and a complete pedestrian
  network/accessibility report remain future work.

## Local trial

Project: http://127.0.0.1:5178/projects/3df7bca4-d9a5-48d0-b04f-956c114d72db

Used the existing two-house, street and neighbourhood-park fixture. Removed its
two manually authored test approaches through the local API, then configured
both replacement entrance links, the park entrance and a crossing through the
new browser controls. No other projects were changed.

Browser checks:

- Building entrance save, undo and redo verified against persisted data.
- Bungalow plot width changed from 15 to 16 m and restored using the reshape UI.
- Dragged the bungalow approximately 3.8 m west and 0.85 m south; the saved
  walkway endpoint moved with it and stayed connected. Undo restored the scene.
- Park entrance locked to its front edge at 25%; crossing placed halfway along
  the street. The overhead view shows a continuous route from both approaches
  along the sidewalk, across the street and into the park loop.
- Reload retained all four authored relationships. Shared ground reached ready;
  both approach meshes and all 13 crossing surface/marking/ramp meshes mounted.
- Free direct capture passed at 1600 by 936: 11.8% proposal coverage, including
  street 4.7%, park 5.4% and building 1.7%. This validates the 3D source passes,
  not the fidelity of a paid AI finish.

The trial caught and fixed an overly conservative crossing clearance check and
a capture-layer semantic mismatch. Dedicated regression tests cover both.

Tests cover transform/serialization behavior, native versus proportional
offsets, missing/hidden targets, obstacles, outward-facing approaches, crossing
clearance and overlap, editable park constraints, save failure/cancel, numeric
validation, terrain draping and capture-class ownership. TypeScript and targeted
ESLint checks passed. Across the eight targeted files, 103 tests passed. No paid
AI images or video were generated.

Visual and JSON evidence stays outside Git:
`C:/dev-artifacts/CityPrompt/connections-pilot-2026-09-06/`.

The existing ground resampling interruption remains; this initiative did not
alter terrain sampling or publish catalogue assets.
