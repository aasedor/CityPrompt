# Lux Modus context delivery contract

This is an integration specification, not a claim about Lux Modus's available
formats, accuracy or delivery service. Obtain explicit delivery metadata before
production integration. Unknown vertical references must not become guessed offsets.

## Ownership

City Prompt's saved zones, building representations and camera remain authoritative.
Existing context is a separate visual input. A suitable classified LiDAR/DTM may
be the elevation authority; a textured mesh supplies existing visual conditions.
Switching the displayed mesh does not change the elevation authority or rewrite
proposal coordinates. Changing design ground is a separate, explicit edit with
revision, undo, reload and capture checks.

Use existing zone/source/representation fingerprints and ground snapshots. Do not
create a second editable copy of the design. Retain Google for coverage and fallback.

## Required delivery information

| Area | Metadata to obtain and validate |
| --- | --- |
| Dataset | Stable ID, capture name/date, geographic coverage, revision, attribution, licence and permitted hosting/export uses |
| Horizontal | CRS/EPSG or complete definition, datum/epoch where relevant, axis order, coordinate units, local origin and explicit local-to-world transform if used |
| Vertical | Vertical datum, units, orthometric versus ellipsoidal heights, geoid model/version and required grid files; surveyed control points and stated accuracy |
| LiDAR | LAS/LAZ/E57/other format/version, point density, classification schema, ground class availability, returns, RGB/intensity, noise flags, tile bounds and sizes |
| Terrain | DTM and/or DSM availability, grid resolution and origin, nodata convention, breaklines, interpolation assumptions, accuracy/quality checks, revision |
| Mesh | 3D Tiles/3D Tiles Next/GLB/OBJ/FBX/other version, LOD hierarchy, geometric error, tile bounds, transforms, up axis, texture formats/dimensions and compression extensions |
| Imagery | Orthophoto format, GSD, georeferencing, bounds, colour information, nodata and capture date |
| Delivery | Storage/streaming method, total and largest-tile sizes, request limits, update cadence, authentication/expiry, CORS and cache policy |

Require a small representative delivery first: ground, building edges, a slope,
vegetation and one textured mesh tile. Keep its source checksums and unmodified
metadata outside the source tree. Establish one documented transformation into
City Prompt's WGS84 Earth-centred frame and ellipsoidal metres. A projected XY
conversion alone does not convert orthometric elevations. Missing geoid data or
ambiguous registration keeps the new elevation source unavailable.

## Adapter behaviour

- Separate visual-source readiness from elevation-source validity. Loading a new
  mesh cannot clear the saved design or replace the current ground snapshot.
- Normalize validated elevation data into the existing ground-sampling contract;
  preserve coverage/nodata, source revision, vertical reference and quality evidence.
  Reject queries outside coverage rather than extrapolating unknown terrain.
- Preserve rigid RLASM geometry. Resolve footprint contact, foundation limits,
  streets, parks and entrances against the chosen elevation authority.
- Retain existing polygon context suppression; test clipping, depth/normal capture
  and boundaries on a small tile before scaling. Do not destructively edit captures.
- Stream bounded LODs and profile actual draw calls, textures, triangles/points,
  transfers, first usable view and interaction. Cache targets are not hard GPU caps.
- Use project-authorized dataset IDs resolved by the server. Constrain storage
  paths and content URLs, redirects, formats, decompression sizes and dependency
  origins. Do not accept unrestricted user-supplied tile URLs or expose credentials.
- If capture loading fails, retain/fall back to Google and explain that the design
  is unchanged. Log technical details separately; no automatic paid retry loop.

## Acceptance before production

Compare surveyed controls and independent elevation samples, not just visual fit.
Freeze proposal coordinates, orientation, rendered world transforms, grade and
camera; verify them through both providers, terrain-only display, reload and
asynchronous refinement. Test flat/slope/edge/nodata cases and older saved projects.
Verify source attribution, authorization, replacement zones and deterministic
capture provenance. A visually plausible manual nudge is not registration proof.

## Current implementation boundary

The development-only context pilot reuses `TilesRenderer`, the existing spatial
mask and saved prepared ground. It switches visual materials without remounting
the proposal. Its fixed local sample loader accepts no arbitrary URL. It is not a
production dataset registry, LiDAR importer, DTM normalization service or geoid
conversion pipeline. Those require validated delivery metadata and separate pilots.
