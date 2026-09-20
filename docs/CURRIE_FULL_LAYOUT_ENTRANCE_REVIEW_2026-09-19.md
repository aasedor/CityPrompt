# Vacant Currie seven-house entrance layout review — 19 September 2026

This is the next bounded check after `CURRIE_ENTRANCE_BROWSER_QA_2026-09-19.md`.
The source is the visibly vacant Currie project
`f5bffc94-def9-4c43-942e-9ae7411872e9`. Its seven houses, park, street,
and eight-vertex boundary were copied into disposable project
`54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`. The bungalow `Shared street west 2`
received the previously measured entrance anchor and a westward plot shift.
The main fixture was read-only: all ten live zone coordinates still match
`currie-final-api.json`, and its entrance is still unresolved.

| Check | 1.2 m west | 2.4 m west |
| --- | --- | --- |
| Plot inside original boundary | Yes; minimum clearance 3.413 m | Yes; minimum clearance 2.213 m |
| Gap from six-metre street zone | 1.592 m | 2.792 m |
| Nearest other plot | 2.983 m | 2.983 m |
| Overlap with other six plots, park, street | None | None |
| Browser ground | Ready, two passes, seven visible native houses | Ready, two passes, seven visible native houses |
| Bungalow grounding issue | None | None |
| Other six houses | `entrance_connection_required` | `entrance_connection_required` |

The local metre-scale clearance check uses the live saved zone polygons, not
screen pixels. The 2.4 m result is a single bounded alternative, not a
recommendation to consume the smaller boundary margin. It extends the
one-house street-to-entry run from roughly 4.118 m to roughly 5.318 m, using
the same explicit native-step anchor; the latter length is inferred from the
1.2 m lateral extension, not remeasured from the rendered mesh.

The overhead and oblique browser views show the copied seven-house layout and
the park in context. The east pedestrian views at both setbacks show the
stair from the bungalow foundation toward the street. At 2.4 m the run reads
less steep, but the solid step skirts, exposed high foundation face, and long
unguarded edge still read as rough concept geometry. The current ground solver
accepts support and route geometry; that is not visual or pedestrian-design
acceptance. Browser page errors were empty. The other six warnings correctly
remain and still block full-site capture.

Evidence outside Git is in
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`:

- `currie-original-layout-clearances.json` — live original coordinates and
  clearances at zero, 0.6, 1.2, 1.8, and 2.4 m west.
- `currie-full-layout-entrance-pilot.json` — disposable copy and ID mapping.
- `currie-full-layout-setback-2p4.json` — the single further edit to that copy.
- `currie-full-layout-top.png`, `currie-full-layout-oblique.png`, and
  `currie-full-layout-entrance-east.png` — seven-house context at 1.2 m.
- `currie-full-layout-entrance-east-2p4.png` and
  `currie-full-layout-entrance-southeast-2p4.png` — 2.4 m pedestrian review.

**Decision:** The first house's setback is geometrically feasible within the
saved full layout. Do not promote either alternative to the main fixture yet:
the entrance and high foundation still need an intentional visible design,
including a reviewed stair/landing/edge treatment or a different layout
strategy. Keep native model geometry and measured terrain truthful. Then
author and review the six remaining houses one at a time, make the Connections
anchor task usable without raw coordinates, and resume the park, street, edit
recovery, novice journey, and student-pilot gates in
`STUDENT_TRANSFORMATION_GATES.md`.

No source runtime code changed in this review. No paid generation or push ran.
