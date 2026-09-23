# Currie entrance stair body — bounded browser pilot

The full seven-house disposable Currie copy from
`CURRIE_FULL_LAYOUT_ENTRANCE_REVIEW_2026-09-19.md` exposed a wall-like body
under the 14-tread bungalow approach. The approach renderer now keeps each
tread body no deeper than 0.24 m and adds two narrow continuous stringers
beneath the run. It still checks the full area of every tread against the
shared measured ground before displaying the geometry. Native building
models, plot and street coordinates, terrain, and authored entrance data are
unchanged by this source change.

The browser pilot used the same seven-house disposable project
`54bb844c-1ff4-4d67-bc7f-0c8c36d0030e` at its 2.4 m westward bungalow
setback. In the frozen east view, the earlier full-height step skirts read as
a wide retaining wall. The new stair reads as a thinner continuous flight
from the foundation toward the street. A second wide pedestrian view shows
the whole run and nearby house. Shared ground reached `ready` with two passes,
all seven native houses visible, and the bungalow without a grounding issue.
The other six houses still report `entrance_connection_required`. Browser
page errors were empty.

The visual result remains **provisional**. The high exposed foundation,
length of the flight, absent landing and edge treatment, and six unresolved
neighbour entrances are still apparent. Stringers are display massing, not
structural design; the route does not establish accessibility or constructed
stair compliance. This is not permission to promote the setback to the main
Currie fixture or to accept Batch A.

Evidence outside Git under
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`:

- Before: `currie-full-layout-entrance-east-2p4.png` and
  `currie-full-layout-entrance-southeast-2p4.png`.
- Thin treads without stringers, rejected visually:
  `currie-stair-body-east-2p4.png` and
  `currie-stair-body-southeast-2p4.png`.
- Current stringer pilot: `currie-stair-stringers-east-2p4.png`,
  `currie-stair-stringers-southeast-2p4.png`, and
  `currie-stair-stringers-wide-ready-2p4.png`.

Focused Vitest: **43 tests across seven files passed**, covering approach
geometry, model ownership, capture and resource lifecycle, and route planning.
TypeScript type-check and changed-file ESLint passed. No paid generation or
push occurred.
