# Street junction network follow-up

Date: 2026-09-23. Branch: `codex/compiled-street-network-junctions`.

The ten-street Currie review stays development-only. This follow-up repairs the
shared street graph and verifies the existing compiled section junction path.
It does not promote a native GLB to the student picker or replace the published
Public Realm LEGO recipe contract.

## Reusable rules for every new street archetype

- A street contributes its **route axis**, metric width and directed approaches
  to the shared graph. Rigid native review rectangles have local X across the
  section and local Y along the route. Their polygon ring must be the exact
  four-corner placement rectangle. The browser takes midpoints of its two
  short end edges, matching the server's longest-axis recovery. A generic
  buffered-polygon pairing does **not** describe this asset format.
- An extra collinear saved station, including a public-road extension station
  exactly on a junction, does not split a through arm. A real turn within the
  junction envelope blocks automatic surface ownership until an authored turn
  transition exists; a bend farther along the route is allowed.
- A node owns one clipped surface. Its source streets retain their native or
  compiled detail outside that footprint. A T has exactly three directed arms
  and no fourth paved stub. Native sections must share a prepared datum and
  provide enough physical length along every present approach.
- A compiled street may claim a T/X only through a valid canonical segment
  recipe, a metric section profile, a compatible 45–135 degree approach and
  sufficient physical reach. The server independently proves the claimed
  topology and source revisions before a paid Direct 3D render.

When adding a street, register its section, width, surface/finish metadata and
recipe capability; add that exact variant to both the T and X contract tests.
Review a mixed-width vehicle junction and a pedestrian/shared-space junction
in a prepared parcel before adding more variants. Do not rely on a visual
reference image alone to imply an executable network capability.

## Verified now

- Every one of the 12 registered native review streets forms an orthogonal X
  and a T against another registered section in the focused tests. Both T stem
  directions preserve the closed side; junction ground contains no fourth
  strip. Native ground and rigid props are trimmed at the owned node.
- The compiled path accepts T and X junctions, 45–135 degree skew approaches,
  different compiled street sections, a remote route bend, and a straight
  public-road connection with a redundant station. It rejects a turn inside
  the node envelope, a short T stem, and stale or omitted source claims.
- The vacant Currie ten-street project reloaded with five native nodes. An
  overhead browser review showed the five crossing surfaces, and a free
  Direct 3D capture registered all five with nonzero instance pixels. Browser
  console errors and warnings: none. No paid image renders were used.
- The saved 20-building Currie neighbourhood reloaded with three compiled T
  nodes; a free overhead capture registered all three as three-arm instances
  with visible pixels. That historical project has missing building GLBs in
  this checkout (404), so it is not a whole-neighbourhood visual sign-off.
  Its live check also exposed a street-material cleanup error: React Three
  Fiber's `dispose={null}` prop overwrote explicitly owned material disposal.
  Removing that prop from the owned street materials eliminated this error on
  a fresh load; explicit deferred resource cleanup remains in place.

## Remaining publication boundary

Rigid native review modules still cannot bend, change grade or automatically
join a native module to a compiled street. Public-road endpoint connections
are the compiled street inspector's bounded extension; they do not infer
public curb returns or sidewalk geometry from Google tiles. The registered
review assets remain outside the student catalogue. A future native-family
promotion needs an executable compiler representation and the exact S1–S4
checks in [ARCHETYPE_RUNTIME_INTEGRATION.md](ARCHETYPE_RUNTIME_INTEGRATION.md).
