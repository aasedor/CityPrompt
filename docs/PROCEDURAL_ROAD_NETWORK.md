# Procedural road network — initial vertical slice (2026-09-08)

## Architecture assessment before implementation

1. **Drawing:** `frontend/src/components/viewer/SitePlannerMap.tsx` and
   `globe/GlobeSitePlannerMap.tsx` smooth drawn polylines and buffer them into
   polygons. Buffer helpers also exist in `utils/roadGeometry.ts` and
   `viewer/mapEngine/geoUtils.ts`. Previously the drawing completion paths did
   not persist their source lines.
2. **Persistence:** `SiteZone` in `backend/app/models/models.py` stores a WGS84
   PostGIS Geography POLYGON and JSONB properties. Roads are zone_type `road`.
   `api/v1/site_zones.py` provides CRUD/history; `schemas/schemas.py` validates
   requests. A centreline can be retained in `properties.plan_centerline`.
3. **Profiles:** `width`, `lane_count`, `road_archetype_id`, and `street_role`
   live in properties. `effectiveRoadWidth` applies the existing motor-lane
   minimum, with exceptions for trails, paths, and laneways. Catalogue sections
   and `public_realm_lego` recipes provide richer ROW and band information.
   `globe/streetSectionProfiles.ts` resolves carriageway, cycle, sidewalk,
   median, planting, material, and curb offsets for compiled streets.
4. **Geometry libraries:** backend planner geometry already uses Shapely in
   local metric coordinates. Frontend uses custom strip/mesh geometry, Turf
   helpers, Mapbox, and Three.js. No new geometry dependency is required.
5. **Snapping:** existing polygon-close gestures and the specialised four-way
   detector provide some proximity logic, but there was no general semantic
   endpoint-to-road snap/save pipeline.
6. **Crossings:** saved road polygons may overlap. The planner unions ROW and
   computes intersection points; the globe infers certain four-way assemblies.
   Neither is a persistent editable road-edge/node database.
7. **Flow:** drawing → `useSiteZones` / React Query → zone API → PostGIS polygon
   and JSON properties → Mapbox polygon features or globe terrain-draped fills.
   Explicit community compilation additionally supplies street section meshes,
   ground textures and supported intersection assemblies.
8. **Identity dependencies:** undo/redo actions, saved snapshots, selection,
   building links, master-plan locked layers, compiled recipe source hashes,
   graph claims and Direct 3D capture refer to zone IDs. Splitting database
   zones would disrupt these systems, so this implementation does not do it.
9. **Existing graph:** `services/plan_geometry/street_graph.py` has
   `StreetSegment` and `StreetNetwork` (full-span lines, widths, unioned area,
   points, roundabouts and planner metrics). It is a plan-generation structure,
   not an editor graph. Leave its existing algorithm and consumers intact.
10. **Existing intersections:** `globe/streetGraphIntersections.ts` derives
    specialised four-way nodes for supported executable street families.
    Its recipe/proof contracts must not be silently broadened to arbitrary
    roads or T-junctions.

## Implemented contract

New hand-drawn roads set `procedural_road: 1` and retain `plan_centerline`.
Parent zone IDs and the existing polygon serialization remain unchanged.
`road_source.py` synchronizes source lines and paired strip polygons on API
create/update, including width edits, translations and rotations. Existing
zone history therefore captures all source inputs together. Undo/redo or
snapshot restore triggers the same derived-network query as any other change.

`GET /api/v1/site-zones/projects/{project_id}/road-network` requires project
read access. It resolves a versioned graph from saved road properties without
writing zones or creating history entries. The endpoint returns:

- nodes: geographic-stable ID, metric location, level, incident edge IDs,
  classification, ordered approach angles, optional intersection ID;
- edges: stable parent ID, end-node IDs, split polyline, profile, width,
  original envelope and trimmed surface;
- intersections: STANDARD type, node ID, radius setting, ordered independent
  approaches, resolved surface and curb-boundary geometry;
- approach metadata: tangent, width/profile, sidewalk/median widths, termination
  distance and candidate stop/crossing lines. Candidates are hooks, not final
  traffic-engineering layouts;
- WGS84 GeoJSON `features` with `node`, `edge`, `envelope`, `road_surface`,
  `intersection`, and `approach` roles, plus the metric frame and warnings.

The metric kernel is independent of FastAPI and the planner. It snaps terminal
vertices, intersects polylines, splits by distance along each parent, classifies
nodes, constructs per-approach envelopes, rounds re-entrant corners by a Shapely
closing operation, partitions close intersection footprints, and subtracts
owned junction geometry from road surfaces. Surface ownership eliminates
coincident road surfaces, including unequal widths. Geometry is deterministic;
there are no AI calls.

V1 uses the existing **total road width/ROW planning surface**, not an invented
carriageway width. `corner_radius` is a metric property, default 4 m; a node uses
the maximum requested by its approaches. It is not presented as a municipal
design standard. The kernel accepts a configurable snap tolerance (default
1.5 m, 0–20 m). `road_level` is an explicit layer ID, default 0. Different layers
never connect. Terrain elevation is deliberately not treated as a road layer.

The frontend query runs on source revisions, never on animation frames.
Source-keyed server snapshots, spatial-component caches and local-junction
solution caches avoid repeating unchanged work. These are bounded in-process
caches, not a database graph: after restart the graph reconstructs from saved
source lines. A change inside a connected component reruns its topology;
unchanged local junction solutions can still be reused. Moving the metric
origin may invalidate component caches, but public IDs remain geographic.

Both map views adapt the GeoJSON to **display-only** surface pieces. They retain
parent IDs for selection/capture and separate keys for rendering. Original
editable polygons remain the inputs to drag handles, CRUD, history and the
planner. A pending/failed network request falls back to source polygons rather
than showing the previous revision's junctions. Holes are not silently filled:
the simple-ring display adapter falls back if a future result requires them.

## Compatibility and limitations

- Existing roads are not automatically migrated. Only roads explicitly marked
  `procedural_road: 1` join this network. This preserves clipped planner geometry
  and compiled-family proof contracts. New procedural roads do not yet connect
  semantically to non-migrated roads. An explicit migration must establish a
  trustworthy centreline and reconcile compiled recipes first.
- This is a planning-surface and globe-ground integration. Existing compiled
  street-band/assembly generation is unchanged; trimming its detailed sidewalks,
  curbs, markings, and furniture against these general junctions remains a next
  milestone. The new graph is not yet a planner/export topology input.
- There is no live hover snap ring yet. `roadSnapTarget` is the reusable cursor
  hook; both completion paths snap endpoints before smoothing/saving. Wire its
  return value to the editor's pointer/centre reticle for live feedback.
- Per-corner editing, graph-edge deletion UI, roundabouts, signals, raised
  surfaces, lane connectivity, ramp construction and crosswalk generation are
  not implemented. Deleting a parent road rebuilds affected topology; a parent
  spanning an intersection still edits/deletes as one road. Test fixtures with
  separate leg parents exercise four-way → T → dead-end transitions.
- Collinear duplicate roads emit warnings and retain distinct approaches. They
  need a future merge policy. Self-crossing source polylines are rejected.
- Very short/acute intersections use bounded approach extents. Metadata is not
  a swept-path or engineering compliance guarantee. WGS84 conversion is a
  site-scale local approximation; polar coordinates are rejected.
- Generated corner additions are not parcel-boundary-clipped. The existing API
  validates the authored strip against the boundary; a future ownership policy
  must reconcile corner additions with adjacent parcels and site boundaries.
- No new SQL schema/migration, no changes to the planner algorithm, no AI calls,
  no catalogue publication. Unrelated pre-existing working-tree changes remain.

## Files in this initiative

| File | Responsibility |
| --- | --- |
| `backend/app/services/road_network.py` | Metric topology, resolver, bounded caches, WGS84 adapter |
| `backend/app/services/road_source.py` | Validate/synchronize editable centreline and strip |
| `backend/app/api/v1/site_zones.py` | Read endpoint and CRUD source synchronization |
| `frontend/src/hooks/useRoadNetwork.ts` | Shared revision-keyed network query |
| `frontend/src/utils/proceduralRoadNetwork.ts` | Snap utility and display-only surface adapter |
| `frontend/src/components/viewer/SitePlannerMap.tsx` | Save source line, snap endpoints, render surfaces in Mapbox |
| `frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx` | Equivalent globe integration |
| `frontend/src/components/viewer/globe/GlobeZoneLayer.tsx` | Separate piece render keys while keeping parent IDs |
| `backend/tests/test_road_network.py` | Topology/geometry/source regression cases |
| `backend/tests/test_road_network_api.py` | Project authorization and read-only endpoint contract |
| `frontend/src/utils/proceduralRoadNetwork.test.ts` | Snap, identity and immutable display adapter tests |
| `tools/render_road_network_debug.py` | Finite six-case debug-render batch |

## Verification and debug evidence

Run from repository root:

```powershell
backend/.venv/Scripts/python.exe tools/render_road_network_debug.py
```

This creates ignored `artifacts/road-network/road-network-debug.png` and six
metric graph JSON files. It draws the actual generated geometry and node/approach
data for perpendicular, unequal-width T, angled T, angled four-way, close-node
and curved cases. The authenticated API also exposes WGS84 debug features for
Mapbox or GIS inspection.

Backend validation: 106 tests passed across road network/API, site-zone utilities
and schemas, existing plan geometry and master-plan 2D renderer suites.
Frontend validation: 45 tests passed across the new adapter and existing road
geometry, four-way graph and street mesh suites. `npm run type-check` and
`git diff --check` passed. A browser smoke check reached
the local sign-in page with no captured console errors. The test browser had no
authenticated editor session, so interactive draw/edit/Generate 3D was not verified in
the running application. Debug renders are kernel evidence, not editor screenshots.

Recommended next milestone: an authenticated editor acceptance pass, live snap
feedback, and profile-band clipping against the network's owned surfaces; then
explicit migration of existing planner/compiled roads with source-hash tests.
