# Connected street T/X pilot — 2026-09-04

This bounded extension joins the executable local/main street sections in the
isolated mixed-neighbourhood pilot. It creates deterministic geometry; it does
not generate an image, atlas, building asset, or traffic-engineering approval.

## Geometry and ownership

`streetGraphIntersections.ts` retains the four-way adapter and existing node IDs.
The connected adapter additionally retains three directed approaches for an
orthogonal T. The through street is axis A; axis B has only its actual stem
direction. The new T check uses metric endpoint tolerance (2 m), rather than a
percentage of a potentially very long street. Opposing, clipped fragments can
still form one node. All participating source IDs survive bearing grouping.

`streetJunctionGeometry.ts` decomposes a short union of the actual ROW corridors
into disjoint pavement and sidewalk cells. It uses the compiled section's actual
outer carriageway curb offsets. A T has a continuous back sidewalk and no fourth
road stub, zebra set, or pair of curb ramps. The new node has three crossing sets,
six 1.8 m ramp wedges, tactile pads, and curb faces with physical ramp openings.
The crossing setback is 2.9 m so adjacent corner ramps do not overlap. The legacy
four-way geometry builder's default dimensions and signal policy are preserved.
The close GPU view exposed mirrored ramp/pad tops facing downward on one side;
the builder now preserves upward top winding on both sides (six T/eight X pads)
without disabling culling or depth testing.

`GlobeStreetDetailLayer.tsx` clips every overlapping segment band, marking and
curb triangle out of the node-owned footprint, interpolating position, grade and
UV attributes. This is exact polygon clipping, including vertical curb walls;
it does not remove a whole long street based on sparse station samples. Raised
details keep normal depth testing. Node pavement and sidewalk reuse the same source-band material recipe as the
segments: deterministic texture seed, metre repeat scale, tint and roughness.
The node UV frame follows the through street's orientation and phase. No new
texture asset or provider call is involved. The node uses the prepared site datum when
all linked streets resolve to it, otherwise the existing terrain contact plane.
The prepared-site pilot is the accepted scope for a continuous shared grade.

## Capture provenance

Existing four-way descriptors retain `junction:zones-…:street` IDs and their
existing independent server proof. New T descriptors have an anchor-qualified
ID and a `junction_topology` object containing version 1, arm count, longitude,
latitude and `sj1|sorted-zone-id:source-hash:representation-hash|…`.

The source and representation hashes are the existing server-authored SHA256
community compilation identities. The API checks those identities, independently
reconstructs the exact arm count and orthogonal bearings at the claimed anchor
(0.5 m numerical tolerance), and rejects omitted nearby road contributors. The
normal scene revision/compilation gate still runs before this inventory binding.
Stale revisions, an invented fourth arm, another anchor, and a bent/skew T fail
before any provider call. Verified topology is retained in the server inventory.
This is source-graph validation, not a new claim that generated pixels are
geometrically certified.

## Deliberate limits

- New owned surfaces require orthogonality within one degree and symmetric curb
  offsets with room for the ramps. Every approach must extend far enough to
  contain the owned patch; a short stub is never lengthened to fit it. Skew T, asymmetric section transitions, and
  five/six-arm nodes do not receive a synthesized intersection.
- A reviewed street-network atlas retains its existing ground ownership. A T
  that needs a new atlas is not silently painted over or sent for generation.
- The first visual pilot uses local streets. Bicycle lane continuity, dedicated
  turn lanes, swept vehicle paths, T signal placement and intersection traffic
  controls need their own explicit contracts before broader street rollout.
- Source street geometry remains the persistent plan. Topology is deterministically
  derived from the current sources and revision-bound in captures; there is no
  separately editable persistent street graph yet.

## Verification

Focused Vitest covers north/south and split-source T detection, retained X IDs,
skew/bent rejection, the absent fourth arm, closed-side sidewalk coverage,
physical ramp openings, exact source triangle clipping, UV/grade interpolation,
rotated frames and three-vs-four capture metadata. Backend tests cover accepted
T inventory, source revision changes, wrong anchor/count, omitted fourth road,
unrelated distant streets, nonvehicle paths, and bent approach rejection.

The combined free browser/GPU visual pilot is recorded by the root task with
the mixed-block fixture; no paid image or asset generation is part of this work.


Initial real GPU views in `artifacts/mixed-neighbourhood/browser/` show the
three crossings, continuous closed-side sidewalk and clear central carriageway.
The actual T capture passed schema, server source/graph binding, pixel preparation
and provenance checks against the isolated DB without a provider call. The
initial downtown fixture is functional evidence only. Empty-lot ground alignment
and final visual evidence are recorded in
[the mixed-neighbourhood pilot](MIXED_NEIGHBOURHOOD_PILOT_2026-09-04.md).

The active retained-site integration samples the shared site ground field for
every street station (left/center/right), final ribbon vertex, and final junction
vertex. Before draping, the geometry helper intersects authored faces with the
snapshot's exact grid cells and SW–NE triangle boundaries. Each resulting face
lies within one terrain plane, preserving ground contact across its interior as
well as at its vertices, together with authored lifts, UVs and material groups.
Every ENU frame uses its own sampled center elevation and subtracts that frame
from the shared height. Shifted roundabout geometry translates the same grid
and sample origins together. Rigid furniture and X signals sit at individual
shared heights; fixture metadata such as station counts is preserved unchanged.
Owned geometry waits while the common field is sampling/unavailable and rebuilds
when its revision changes. Inactive/outside-site behavior retains the legacy
sampler. Tests cover an authored face smaller than 4 m crossing a terrain
diagonal, transformed local origins, preserved construction lifts, and actual
fixture-builder output when measured ground becomes ready. Final empty-lot GPU
measurements remain the acceptance evidence for the real terrain.
