/**
 * GlobeZoneLayer.tsx — Renders SiteForge zones on the 3D tile globe.
 *
 * Uses EastNorthUpFrame to position zones at their geographic centroid,
 * then renders geometry in local ENU meters (X=East, Y=North, Z=Up).
 * Buildings are extruded along Z (up). Flat zones (parks, roads) use
 * terrain draping via raycast to sit precisely on the tile mesh.
 */

import { useMemo, useContext, useRef, useEffect, useCallback, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { applyParkGroundUVs, useParkGroundTexture } from './parkGroundTexture';
import { useStreetNetworkGroundTexture } from './streetNetworkGroundTexture';
import {
  resolveZoneColor,
  resolveZoneLabel,
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { useGlobeDragRef } from './useGlobeDragRef';
import {
  getObjectFilteredTerrainHeight,
  getRepresentativeTerrainHeight,
  hasUsableElevationRelief,
  isPlausibleTerrainAnchor,
  rejectRaisedObjectTop,
  resolvePublicRealmGroundAnchor,
  resolveReplacementGroundAnchor,
  resolveZoneTerrainHeight,
  shouldFilterObjectTerrainHeight,
} from './globeTerrainUtils';
import { elevationApi } from '@/services/api';
import {
  isCommunity3DCompiled,
  resolveCommunity3DKind,
} from '@/features/community3d/community3d';
import {
  createSitePreparationGeometry,
  createSitePreparationTexture,
  createWoonerfPaverTexture,
  getPreparedSiteBoundaryIds,
  overlapPreparedGroundEdges,
  shouldRenderReplacementFootprintGround,
} from './sitePreparationSurface';
import { buildContainedTerrainGroundMesh } from './terrainGroundMesh';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import {
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  resolvePublicRealmGroundDepthPolicy,
  shouldUseLevelCompiledParkDatum,
} from './publicRealmDepthPolicy';
import {
  applyResidualLandscapeUVs,
  createResidualLandscapeTexture,
  getResidualLandscapeRecipe,
} from './residualLandscape';
import {
  DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA,
  direct3DGroundRoleForCommunityKind,
  direct3DInstanceUserData,
  direct3DProposalUserData,
  direct3DZoneInstanceDescriptor,
} from './direct3dCapture';
import {
  createMetricSurfaceGeometry,
  createStreetSurfaceAlbedoTexture,
  type StreetSurfaceMaterialKind,
} from './streetSurfaceMaterials';
import { resolveParkLegoContract } from './parkLegoFamilies';
import { useBatch21ParkBaseMaterial } from './parkBatch21BaseMaterial';

const DEG_TO_RAD = Math.PI / 180;
const OBJECT_FILTER_SAMPLE_RADIUS_METERS = 8;
const REPLACEMENT_GROUND_SAMPLE_RADII_METERS = [8, 20, 36] as const;
// With the live tile surface as the authoritative anchor, only a decal-scale
// clearance is needed. Normal depth testing prevents the ground from painting
// across buildings while polygon offset avoids coplanar terrain flicker.
const FLAT_ZONE_OUTLINE_LIFT_METERS = 0.11;
const FLAT_ZONE_MAX_EDGE_LENGTH_METERS = 12;
const FLAT_ZONE_MAX_RENDER_VERTICES = 96;
const FLAT_ZONE_DEPTH_OFFSET_FACTOR = -4;
const FLAT_ZONE_DEPTH_OFFSET_UNITS = -8;
const GLOBE_SCENE_HTML_Z_INDEX_RANGE: [number, number] = [1, 0];

// Above this many zones on screen, each zone switches to a cheaper render path:
// no per-vertex terrain raycasting and no tile-stencil volume. Big imported
// layers then sit at a single sampled elevation instead of hugging every bump —
// the trade that keeps the frame rate up. Tune if needed.
const LIGHTWEIGHT_ZONE_THRESHOLD = 50;
const TERRAIN_DRAPE_SPREAD_MS = 30_000;

function stableDelay(seed: string, spread = TERRAIN_DRAPE_SPREAD_MS): number {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash >>> 0) % spread;
}

interface GlobeZoneLayerProps {
  zones: SiteZone[];
  selectedZoneId: string | null;
  terrainHeight?: number;
  onZoneClick?: (zoneId: string) => void;
  selectionEnabled?: boolean;
  /** Buildings whose GLB model is mounted on the globe — their extruded prism
   *  is skipped (the model replaces it). Stencil volume + label stay. */
  suppressedBuildingIds?: Set<string>;
  /** Planning fills/outlines/labels can be hidden while generated park
   * orthophotos remain mounted as authored proposal content. */
  planningOverlaysVisible?: boolean;
}

function coordinatesNearlyEqual(a: number[], b: number[]): boolean {
  return Math.abs(a[0] - b[0]) < 1e-7 && Math.abs(a[1] - b[1]) < 1e-7;
}

function coordinateDistanceMeters(a: number[], b: number[]): number {
  const avgLat = (a[1] + b[1]) / 2;
  const dx = (b[0] - a[0]) * metersPerDegLon(avgLat);
  const dy = (b[1] - a[1]) * METERS_PER_DEG_LAT;
  return Math.hypot(dx, dy);
}

function densifyFlatZoneCoordinates(coords: number[][]): number[][] {
  const ring: number[][] = [];
  for (const coord of coords) {
    if (!coord || coord.length < 2) continue;
    if (ring.length === 0 || !coordinatesNearlyEqual(ring[ring.length - 1], coord)) {
      ring.push(coord);
    }
  }

  if (ring.length > 1 && coordinatesNearlyEqual(ring[0], ring[ring.length - 1])) {
    ring.pop();
  }

  if (ring.length < 3) return ring;

  const perimeter = ring.reduce((sum, coord, index) => (
    sum + coordinateDistanceMeters(coord, ring[(index + 1) % ring.length])
  ), 0);
  const maxEdgeLength = Math.max(
    FLAT_ZONE_MAX_EDGE_LENGTH_METERS,
    perimeter / FLAT_ZONE_MAX_RENDER_VERTICES,
  );
  const densified: number[][] = [];

  ring.forEach((coord, index) => {
    const next = ring[(index + 1) % ring.length];
    densified.push(coord);

    const segmentCount = Math.max(1, Math.ceil(coordinateDistanceMeters(coord, next) / maxEdgeLength));
    for (let step = 1; step < segmentCount; step += 1) {
      const t = step / segmentCount;
      densified.push([
        coord[0] + (next[0] - coord[0]) * t,
        coord[1] + (next[1] - coord[1]) * t,
      ]);
    }
  });

  return densified;
}

/**
 * Create polygon geometry in the ENU local frame.
 *
 * EastNorthUpFrame axes (from 3d-tiles-renderer):
 *   X = East
 *   Y = North
 *   Z = Up
 *
 * Ground plane = XY, height = Z.
 */
function createLocalGeometry(
  coords: number[][],
  centroidLng: number,
  centroidLat: number,
  extrudeHeight: number,
  useTerrainGridFlat: boolean,
): {
  fillGeo: THREE.BufferGeometry;
  fillCoords: number[][];
  outlineGeo: THREE.BufferGeometry;
  flatTopGeo?: THREE.BufferGeometry;
  localPts: { x: number; y: number }[];
} | null {
  if (coords.length < 3) return null;
  const mPerDegLon = metersPerDegLon(centroidLat);

  // Convert to local ENU meters relative to centroid
  const localPts = coords.map(c => ({
    x: (c[0] - centroidLng) * mPerDegLon,           // East
    y: (c[1] - centroidLat) * METERS_PER_DEG_LAT,   // North
  }));

  // Triangulate the 2D polygon (XY ground plane)
  const indices = THREE.ShapeUtils.triangulateShape(
    localPts.map(p => new THREE.Vector2(p.x, p.y)),
    [],
  );

  if (extrudeHeight > 0) {
    const baseZ = 0;
    const n = localPts.length;
    const allVerts: number[] = [];
    const allIdx: number[] = [];

    for (const p of localPts) allVerts.push(p.x, p.y, baseZ);
    for (const p of localPts) allVerts.push(p.x, p.y, extrudeHeight);

    for (const tri of indices) allIdx.push(tri[0], tri[1], tri[2]);
    for (const tri of indices) allIdx.push(tri[0] + n, tri[2] + n, tri[1] + n);

    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      allIdx.push(i, j, j + n);
      allIdx.push(i, j + n, i + n);
    }

    const fillGeo = new THREE.BufferGeometry();
    fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(allVerts, 3));
    fillGeo.setIndex(allIdx);
    fillGeo.computeVertexNormals();
    fillGeo.computeBoundingSphere();

    const outlineVerts: number[] = [];
    for (const p of localPts) outlineVerts.push(p.x, p.y, extrudeHeight + 0.05);
    outlineVerts.push(localPts[0].x, localPts[0].y, extrudeHeight + 0.05);
    const outlineGeo = new THREE.BufferGeometry();
    outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

    return { fillGeo, fillCoords: coords, outlineGeo, localPts };
  }

  // Flat zone
  if (!useTerrainGridFlat) {
    const flatVerts: number[] = [];
    for (const p of localPts) flatVerts.push(p.x, p.y, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS);

    const fillGeo = new THREE.BufferGeometry();
    fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
    const idxArray: number[] = [];
    for (const tri of indices) idxArray.push(tri[0], tri[1], tri[2]);
    fillGeo.setIndex(idxArray);
    fillGeo.computeVertexNormals();
    fillGeo.computeBoundingSphere();

    const outlineVerts: number[] = [];
    for (const p of localPts) outlineVerts.push(p.x, p.y, FLAT_ZONE_OUTLINE_LIFT_METERS);
    outlineVerts.push(localPts[0].x, localPts[0].y, FLAT_ZONE_OUTLINE_LIFT_METERS);
    const outlineGeo = new THREE.BufferGeometry();
    outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

    return { fillGeo, fillCoords: coords, outlineGeo, flatTopGeo: fillGeo, localPts };
  }

  const terrainGrid = buildContainedTerrainGroundMesh(localPts, indices);
  const flatVerts: number[] = [];
  const fillCoords: number[][] = [];
  for (const point of terrainGrid.vertices) {
    flatVerts.push(point.x, point.y, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS);
    fillCoords.push([
      centroidLng + point.x / mPerDegLon,
      centroidLat + point.y / METERS_PER_DEG_LAT,
    ]);
  }

  const fillGeo = new THREE.BufferGeometry();
  fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
  fillGeo.setIndex(terrainGrid.indices);
  fillGeo.computeVertexNormals();
  fillGeo.computeBoundingSphere();

  const outlineVerts: number[] = [];
  for (const p of localPts) outlineVerts.push(p.x, p.y, FLAT_ZONE_OUTLINE_LIFT_METERS);
  outlineVerts.push(localPts[0].x, localPts[0].y, FLAT_ZONE_OUTLINE_LIFT_METERS);
  const outlineGeo = new THREE.BufferGeometry();
  outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

  return { fillGeo, fillCoords, outlineGeo, flatTopGeo: fillGeo, localPts };
}

type LocalZoneGeometry = NonNullable<ReturnType<typeof createLocalGeometry>>;

function disposeLocalZoneGeometry(resource: LocalZoneGeometry) {
  resource.fillGeo.dispose();
  if (resource.flatTopGeo && resource.flatTopGeo !== resource.fillGeo) {
    resource.flatTopGeo.dispose();
  }
  resource.outlineGeo.dispose();
}

function useDeferredLocalGeometryDisposal(resource: LocalZoneGeometry | null) {
  useEffect(() => (
    resource
      ? retainResourceForDeferredDisposal(resource, disposeLocalZoneGeometry)
      : undefined
  ), [resource]);
}

function useDeferredDisposable(resource: { dispose: () => void } | null | undefined) {
  useEffect(() => (
    resource
      ? retainResourceForDeferredDisposal(resource, (value) => value.dispose())
      : undefined
  ), [resource]);
}

/**
 * Raycast from high altitude straight down onto the tile mesh at a given lat/lng.
 * Returns the hit point in ECEF, or null if no hit.
 * Exported for GlobeBuildingModelsLayer (same seating logic for placed GLBs).
 */
export function raycastTerrainAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): THREE.Vector3 | null {
  const origin = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, 50000, origin);
  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(lat * DEG_TO_RAD, lng * DEG_TO_RAD, normal);
  raycaster.set(origin, normal.negate());
  raycaster.far = 100000;

  const hits = raycaster.intersectObjects(tilesGroup.children, true);
  return hits.length > 0 ? hits[0].point.clone() : null;
}

export function raycastTerrainHeightAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): number | null {
  const hit = raycastTerrainAtLatLng(lng, lat, tilesGroup, raycaster);
  return hit ? WGS84_ELLIPSOID.getPositionElevation(hit) : null;
}

export function raycastObjectFilteredTerrainHeightAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
  fallback: number | null | undefined,
  sampleRadiiMeters: readonly number[] = [OBJECT_FILTER_SAMPLE_RADIUS_METERS],
): number | null {
  const mPerDegLon = Math.max(1, Math.abs(metersPerDegLon(lat)));
  const offsets: Array<[number, number]> = [[0, 0]];
  for (const radius of sampleRadiiMeters) {
    const safeRadius = Math.max(1, Number(radius) || OBJECT_FILTER_SAMPLE_RADIUS_METERS);
    const diagonal = safeRadius * 0.7;
    offsets.push(
      [safeRadius, 0],
      [-safeRadius, 0],
      [0, safeRadius],
      [0, -safeRadius],
      [diagonal, diagonal],
      [diagonal, -diagonal],
      [-diagonal, diagonal],
      [-diagonal, -diagonal],
    );
  }
  const samples = offsets.map(([eastMeters, northMeters]) => (
    raycastTerrainHeightAtLatLng(
      lng + eastMeters / mPerDegLon,
      lat + northMeters / METERS_PER_DEG_LAT,
      tilesGroup,
      raycaster,
    )
  ));

  return getObjectFilteredTerrainHeight(samples, samples[0] ?? fallback);
}

function getTerrainProbePoints(
  coords: number[][],
  centroid: [number, number],
): Array<[number, number]> {
  const probes: Array<[number, number]> = [centroid];
  if (coords.length === 0) {
    return probes;
  }

  const step = Math.max(1, Math.ceil(coords.length / 8));
  for (let index = 0; index < coords.length; index += step) {
    probes.push([coords[index][0], coords[index][1]]);
  }

  const last = coords[coords.length - 1];
  if (last) {
    probes.push([last[0], last[1]]);
  }

  return probes;
}

function ZoneMesh({ zone, isSelected, terrainHeight, onZoneClick, selectionEnabled, lightweight = false, suppressed = false, planningOverlaysVisible = true, sitePrepared = false }: {
  zone: SiteZone;
  isSelected: boolean;
  terrainHeight: number;
  onZoneClick?: (zoneId: string) => void;
  selectionEnabled?: boolean;
  lightweight?: boolean;
  suppressed?: boolean;
  planningOverlaysVisible?: boolean;
  sitePrepared?: boolean;
}) {
  const color = resolveZoneColor(zone);
  const label = resolveZoneLabel(zone);
  const centroid = computeCentroid(zone.coordinates);
  const tiles = useContext(TilesRendererContext);
  const zoneProps = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProps?.terrain_elevation_m
    ?? zoneProps?.terrain_height
    ?? zoneProps?.terrainElevation,
  );
  const storedTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : null;

  const buildingHeight = (zone.properties?.height_m as number)
    || (zone.properties?.height as number)
    || ((zone.properties?.floors as number) || 0) * 3.2
    || 0;
  const isBuilding = zone.zone_type === 'building' || zone.zone_type === 'residential';
  const isSiteBoundary = zone.zone_type === 'site_boundary';
  const isPreparedBoundary = isSiteBoundary && sitePrepared;
  const residualLandscapeRecipe = useMemo(
    () => (isPreparedBoundary ? getResidualLandscapeRecipe(zone) : null),
    [isPreparedBoundary, zone],
  );
  const isReplacementFootprintGround = shouldRenderReplacementFootprintGround(
    zone,
    suppressed,
    sitePrepared,
  );
  const communityKind = resolveCommunity3DKind(zone);
  const isCompiledCommunity = isCommunity3DCompiled(zone);
  const isCompiledGround = (
    (communityKind === 'park' || communityKind === 'street')
    && isCompiledCommunity
  );
  const parkLegoContract = useMemo(
    () => (communityKind === 'park' ? resolveParkLegoContract(zone) : null),
    [communityKind, zone],
  );
  const batch21ParkBaseMaterial = useBatch21ParkBaseMaterial(
    parkLegoContract?.archetypeId ?? '',
    parkLegoContract?.variantId ?? '',
    communityKind === 'park' && isCompiledGround,
  );
  const usesLevelCompiledParkDatum = shouldUseLevelCompiledParkDatum(
    communityKind,
    isCompiledGround,
  );
  const showThisPlanningOverlay = planningOverlaysVisible && !isCompiledGround;
  // Match the mid-grey value range of Google photogrammetry instead of using
  // near-black planning asphalt. The street section layer still supplies the
  // darker travel lanes, pale sidewalks, planting bands and markings above
  // this base, so the right-of-way reads as a composed street rather than one
  // flat black polygon at neighbourhood scale.
  const isPlazaGround = communityKind === 'park' && (
    zone.zone_type === 'parking'
    || typeof zoneProps?.plaza_archetype_id === 'string'
    || typeof zoneProps?.plaza_aesthetic === 'string'
  );
  const isWoonerfGround = communityKind === 'street'
    && String(zoneProps?.road_archetype_id ?? '').toLowerCase().replace(/-/g, '_').includes('woonerf');
  const compiledSurfaceColor = communityKind === 'park'
    ? (isPlazaGround ? '#b5b1a7' : '#66874f')
    : (isWoonerfGround ? '#9b674f' : '#656765');
  const isImported = typeof zoneProps?._imported_from === 'string';
  // Imported reference layers (and big layers) drape ONCE then freeze — stable,
  // no per-frame re-draping that makes long corridors shimmer/jitter while orbiting.
  const freezeDrape = lightweight || isImported || isPreparedBoundary;
  // Compiled streets can cross former buildings just like parks. Sample the
  // lower local surface for every authored public-realm polygon so source
  // photogrammetry roofs never become the new ground plane.
  const filterObjectHeights = (
    isPreparedBoundary
    || isCompiledGround
    || shouldFilterObjectTerrainHeight(zone.zone_type)
  );
  // Drawn buildings share the same planning contract as parks and streets:
  // archetype selection changes only the flat polygon and label. Height is
  // instantiated only after Generate to 3D stamps the compiled marker.
  const extrudeHeight = isBuilding && isCompiledCommunity
    ? Math.max(buildingHeight, 10)
    : 0;
  const useTerrainGridFlat = isCompiledGround || communityKind === 'park' || isPreparedBoundary;
  // Densify imported flat zones too (not just green_space): a long corridor needs
  // vertices along its length so the draped surface follows the terrain instead of
  // flat triangles spanning dips/humps — which is what reads as parallax drift.
  const renderCoordinates = useMemo(
    () => ((useTerrainGridFlat || isImported) && !isBuilding && zone.coordinates.length >= 3
      ? densifyFlatZoneCoordinates(zone.coordinates)
      : zone.coordinates),
    [useTerrainGridFlat, isImported, isBuilding, zone.coordinates],
  );

  const geoData = useMemo(() => {
    return createLocalGeometry(
      renderCoordinates, centroid[0], centroid[1], extrudeHeight, useTerrainGridFlat,
    );
  }, [renderCoordinates, centroid, extrudeHeight, useTerrainGridFlat]);

  const woonerfGroundGeo = useMemo(
    () => (
      isWoonerfGround && geoData?.flatTopGeo
        ? createSitePreparationGeometry(geoData.flatTopGeo, `${zone.id}-woonerf`)
        : null
    ),
    [geoData, isWoonerfGround, zone.id],
  );
  useDeferredDisposable(woonerfGroundGeo);
  const woonerfGroundTexture = useMemo(
    () => (isWoonerfGround ? createWoonerfPaverTexture(zone.id) : null),
    [isWoonerfGround, zone.id],
  );
  useDeferredDisposable(woonerfGroundTexture);

  const publicRealmBaseKind = useMemo((): StreetSurfaceMaterialKind | null => {
    if (!isCompiledGround || isWoonerfGround) return null;
    if (communityKind === 'park') return isPlazaGround ? 'unit_pavers' : 'planting_grass';
    const lego = zoneProps?.public_realm_lego && typeof zoneProps.public_realm_lego === 'object'
      ? zoneProps.public_realm_lego as Record<string, unknown>
      : undefined;
    const appearanceKitId = String(lego?.appearance_kit_id ?? '').toLowerCase();
    return appearanceKitId.includes('european_cobblestone') ? 'buffer_stone' : 'asphalt';
  }, [communityKind, isCompiledGround, isPlazaGround, isWoonerfGround, zoneProps]);
  const publicRealmBaseGeo = useMemo(
    () => (
      publicRealmBaseKind && geoData?.flatTopGeo
        ? createMetricSurfaceGeometry(geoData.flatTopGeo)
        : null
    ),
    [geoData, publicRealmBaseKind],
  );
  useDeferredDisposable(publicRealmBaseGeo);
  const publicRealmBaseTexture = useMemo(
    () => (
      publicRealmBaseKind
        ? createStreetSurfaceAlbedoTexture(publicRealmBaseKind, {
          seed: `public-realm-base:${zone.id}`,
          size: 128,
          anisotropy: 8,
        })
        : null
    ),
    [publicRealmBaseKind, zone.id],
  );
  useDeferredDisposable(publicRealmBaseTexture);

  const replacementGroundData = useMemo(
    () => (
      isReplacementFootprintGround
        ? createLocalGeometry(
          densifyFlatZoneCoordinates(zone.coordinates),
          centroid[0],
          centroid[1],
          0,
          true,
        )
        : null
    ),
    [centroid, isReplacementFootprintGround, zone.coordinates],
  );
  useDeferredLocalGeometryDisposal(replacementGroundData);

  // All geometry from createLocalGeometry is component-owned. Reuse it
  // directly in JSX (instead of cloning on every state render) and dispose it
  // when the polygon changes or unmounts. A long drape session otherwise
  // leaked one fill/outline pair per terrain update.
  useDeferredLocalGeometryDisposal(geoData);

  const preparedSiteGeo = useMemo(
    () => {
      if (!isPreparedBoundary || !geoData?.flatTopGeo) return null;
      const geometry = createSitePreparationGeometry(geoData.flatTopGeo, zone.id);
      if (residualLandscapeRecipe) {
        applyResidualLandscapeUVs(geometry, geoData.fillCoords, zone.coordinates);
      }
      // The Google-Tiles spatial mask and replacement surface are rasterized
      // independently. A tightly coincident edge can reveal a one-pixel white
      // seam; the bounded excess remains hidden below surviving source tiles.
      return overlapPreparedGroundEdges(geometry);
    },
    [geoData, isPreparedBoundary, residualLandscapeRecipe, zone.coordinates, zone.id],
  );
  useDeferredDisposable(preparedSiteGeo);
  const preparedSiteTexture = useMemo(
    () => {
      if (!isPreparedBoundary) return null;
      return residualLandscapeRecipe
        ? createResidualLandscapeTexture(zone, residualLandscapeRecipe)
        : createSitePreparationTexture(zone.id);
    },
    [isPreparedBoundary, residualLandscapeRecipe, zone],
  );
  useDeferredDisposable(preparedSiteTexture);
  const replacementGroundGeo = useMemo(
    () => (
      replacementGroundData?.flatTopGeo
        ? overlapPreparedGroundEdges(
          createSitePreparationGeometry(replacementGroundData.flatTopGeo, `${zone.id}-footprint`),
        )
        : null
    ),
    [replacementGroundData, zone.id],
  );
  useDeferredDisposable(replacementGroundGeo);
  const replacementGroundTexture = useMemo(
    () => (
      isReplacementFootprintGround
        ? createSitePreparationTexture(`${zone.id}-footprint`)
        : null
    ),
    [isReplacementFootprintGround, zone.id],
  );
  useDeferredDisposable(replacementGroundTexture);

  // Authored public-realm material on the zone fill. Parks own a per-zone
  // texture; streets share one north-up atlas so intersections have no seams.
  const parkGround = useParkGroundTexture(zone);
  const streetGround = useStreetNetworkGroundTexture(zone);
  const groundMeta = streetGround.meta ?? parkGround.meta;
  const groundTexture = streetGround.texture ?? parkGround.texture;
  const [bakedElevations, setBakedElevations] = useState<number[] | null>(null);
  // Buildings never use flat fill geometry, and compiled parks/streets must
  // follow the live Google tile surface. Reserve the external bare-earth bake
  // for ordinary imported reference overlays only.
  const shouldBakeImportedTerrain = isImported && !isBuilding && !isCompiledGround;
  const hasBakedElevationRelief = (
    shouldBakeImportedTerrain && hasUsableElevationRelief(bakedElevations)
  );
  const orthoGeo = useMemo(() => {
    if (!groundMeta || !geoData?.flatTopGeo) return null;
    const geo = geoData.flatTopGeo.clone();
    applyParkGroundUVs(geo, geoData.fillCoords, groundMeta);
    return geo;
  }, [groundMeta, geoData]);
  useDeferredDisposable(orthoGeo);
  const drapeActive = Boolean(orthoGeo && groundTexture);
  const publicRealmDepthPolicy = resolvePublicRealmGroundDepthPolicy({
    isCompiledGround,
    hasAuthoredGroundTexture: drapeActive,
    isPreparedBoundary,
    isSiteBoundary,
  });

  // --- Terrain draping for flat zones ---
  // Raycast each vertex onto the tile mesh to get precise ground elevation offsets
  const flatMeshRef = useRef<THREE.Mesh>(null);
  const flatOutlineRef = useRef<any>(null);
  const buildingMeshRef = useRef<THREE.Mesh>(null);
  const buildingOutlineRef = useRef<any>(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const drapedRef = useRef(false);
  const drapeAttemptRef = useRef(0);
  // Set once a lightweight zone has draped successfully — then it never re-drapes
  // (no per-frame raycasting, no re-storm on navigation). The drape-and-freeze.
  const frozenRef = useRef(false);
  const [sampledTerrainHeight, setSampledTerrainHeight] = useState<number | null>(null);
  const zoneTerrainHeight = resolveZoneTerrainHeight(
    sampledTerrainHeight,
    storedTerrainHeight,
    terrainHeight,
  );
  const terrainReferenceHeight = storedTerrainHeight ?? terrainHeight;
  const hasAuthoredGroundTextureMeta = Boolean(
    zoneProps?.park_ground_texture || zoneProps?.street_network_ground_texture,
  );
  const terrainScheduleDelay = isPreparedBoundary || isSelected || hasAuthoredGroundTextureMeta
    ? 400
    : isCompiledGround
      ? 300 + stableDelay(zone.id, 6_000)
      : 1_000 + stableDelay(zone.id);

  // ── Drag performance: useFrame-based geometry update ──
  // Reads the shared drag ref and updates BufferGeometry positions directly,
  // bypassing React state to avoid re-rendering the entire scene.
  const dragRef = useGlobeDragRef();
  const lastDragVersionRef = useRef(0);

  const sampleZoneTerrainHeight = useCallback(() => {
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return false;

    const raycaster = raycasterRef.current;
    const representativeHeight = getRepresentativeTerrainHeight(
      getTerrainProbePoints(zone.coordinates, centroid).map(([lng, lat]) => (
        filterObjectHeights
          ? raycastObjectFilteredTerrainHeightAtLatLng(
              lng,
              lat,
              tilesGroup,
              raycaster,
              null,
              isCompiledGround || isPreparedBoundary
                ? REPLACEMENT_GROUND_SAMPLE_RADII_METERS
                : undefined,
            )
          : raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycaster)
      )),
      terrainReferenceHeight,
    );
    const sampledHeight = filterObjectHeights
      ? (communityKind === 'park' || communityKind === 'street'
        ? resolvePublicRealmGroundAnchor(
            representativeHeight,
            storedTerrainHeight,
            terrainHeight,
            4,
          )
        : resolveReplacementGroundAnchor(
            representativeHeight,
            storedTerrainHeight,
            terrainHeight,
          ))
      : representativeHeight;
    if (!isPlausibleTerrainAnchor(sampledHeight, terrainReferenceHeight)) {
      return false;
    }
    const trustedSampledHeight = sampledHeight as number;

    setSampledTerrainHeight((previousHeight) => (
      previousHeight !== null && Math.abs(previousHeight - trustedSampledHeight) < 0.01
        ? previousHeight
        : trustedSampledHeight
    ));
    return true;
  }, [centroid, communityKind, filterObjectHeights, isCompiledGround, isPreparedBoundary, storedTerrainHeight, terrainHeight, terrainReferenceHeight, tiles, zone.coordinates]);

  useFrame(() => {
    const drag = dragRef.current;
    if (drag.zoneId !== zone.id) return;
    if (drag.version === lastDragVersionRef.current) return;
    lastDragVersionRef.current = drag.version;

    // Recompute local ENU positions from drag coords
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const coords = drag.coords;
    const n = coords.length;

    // Update fill geometry
    const meshRef = isBuilding ? buildingMeshRef : flatMeshRef;
    const outRef = isBuilding ? buildingOutlineRef : flatOutlineRef;
    const renderDragCoords = isBuilding ? coords : densifyFlatZoneCoordinates(coords);
    const renderN = renderDragCoords.length;

    if (meshRef.current && !useTerrainGridFlat) {
      const posAttr = meshRef.current.geometry.attributes.position;
      if (posAttr) {
        for (let i = 0; i < renderN && i < posAttr.count; i++) {
          const localX = (renderDragCoords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (renderDragCoords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
          posAttr.setX(i, localX);
          posAttr.setY(i, localY);
          // For extruded buildings, also update the top ring (indices n..2n-1)
          if (isBuilding && i + n < posAttr.count) {
            posAttr.setX(i + n, localX);
            posAttr.setY(i + n, localY);
          }
        }
        posAttr.needsUpdate = true;
        meshRef.current.geometry.computeBoundingSphere();
      }
    }

    // Update outline geometry
    if (outRef.current) {
      const outPos = outRef.current.geometry.attributes.position;
      if (outPos) {
        for (let i = 0; i < renderN && i < outPos.count; i++) {
          const localX = (renderDragCoords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (renderDragCoords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
          outPos.setX(i, localX);
          outPos.setY(i, localY);
        }
        // Close-loop vertex
        if (outPos.count > renderN) {
          outPos.setX(renderN, outPos.getX(0));
          outPos.setY(renderN, outPos.getY(0));
        }
        outPos.needsUpdate = true;
      }
    }
  });

  const drapeToTerrain = useCallback(() => {
    // A persisted height may have been captured from a photogrammetry roof.
    // Do not deform or freeze the surface until a current, plausible tile
    // sample has anchored this render session.
    const hasTrustedAnchor = sampledTerrainHeight !== null;
    if (
      !tiles?.group
      || !geoData
      || isBuilding
      || hasBakedElevationRelief
      || !hasTrustedAnchor
      || frozenRef.current
    ) return;
    if (drapedRef.current && !freezeDrape) return; // freeze mode keeps refining until frozen
    if (!flatMeshRef.current) return;
    drapeAttemptRef.current++;

    const raycaster = raycasterRef.current;
    let hitCount = 0;

    // For each vertex, raycast to find terrain Z in ENU frame
    const posAttr = flatMeshRef.current.geometry.attributes.position;
    if (!posAttr) return;

    // Generate-to-3D parks replace the source site with a prepared parcel.
    // Seat every triangle on the same sampled datum instead of independently
    // raycasting vertices onto roofs, trees and coarse tile faces.
    if (usesLevelCompiledParkDatum) {
      for (let i = 0; i < posAttr.count; i += 1) {
        posAttr.setZ(i, PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS);
      }
      posAttr.needsUpdate = true;
      flatMeshRef.current.geometry.computeVertexNormals();
      flatMeshRef.current.geometry.computeBoundingSphere();
      drapedRef.current = true;
      frozenRef.current = true;
      return;
    }

    // The terrain-grid geometry stores its densified parcel boundary first,
    // followed by interior rings/vertices. Boundary points receive the full
    // multi-probe object filter. Interior points use a single raycast and the
    // nearest trusted boundary result to reject roofs and tree canopies. This
    // avoids both the former park "starburst" spikes and a 9x raycast cost on
    // every interior vertex across district-scale plans.
    const trustedBoundaryGround: Array<{
      coord: number[];
      elevation: number;
    }> = [];

    const nearestBoundaryGround = (coord: number[]): number => {
      let bestDistance = Number.POSITIVE_INFINITY;
      let bestElevation = zoneTerrainHeight;
      for (const sample of trustedBoundaryGround) {
        const distance = coordinateDistanceMeters(coord, sample.coord);
        if (distance < bestDistance) {
          bestDistance = distance;
          bestElevation = sample.elevation;
        }
      }
      return bestElevation;
    };

    for (let i = 0; i < geoData.fillCoords.length && i < posAttr.count; i++) {
      const coord = geoData.fillCoords[i];
      const isBoundaryPoint = i < renderCoordinates.length;
      const rawHitElev = filterObjectHeights && isBoundaryPoint
        ? raycastObjectFilteredTerrainHeightAtLatLng(
            coord[0], coord[1], tiles.group, raycaster, zoneTerrainHeight,
          )
        : raycastTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster);
      const hitElev = filterObjectHeights
        ? rejectRaisedObjectTop(
            rawHitElev,
            isBoundaryPoint ? zoneTerrainHeight : nearestBoundaryGround(coord),
          )
        : rawHitElev;
      if (hitElev !== null && isPlausibleTerrainAnchor(hitElev, zoneTerrainHeight)) {
        // Z offset in ENU = hitElev - zoneTerrainHeight (the ENU frame origin elevation)
        const zOffset = hitElev - zoneTerrainHeight + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS;
        posAttr.setZ(i, zOffset);
        if (isBoundaryPoint) {
          trustedBoundaryGround.push({ coord, elevation: hitElev });
        }
        hitCount++;
      }
    }

    if (hitCount > 0) {
      posAttr.needsUpdate = true;
      flatMeshRef.current.geometry.computeBoundingSphere();

      // Also update outline
      if (flatOutlineRef.current) {
        const outPos = flatOutlineRef.current.geometry.attributes.position;
        if (outPos) {
          for (let i = 0; i < renderCoordinates.length && i < outPos.count - 1; i++) {
            const coord = renderCoordinates[i];
            const hitElev = filterObjectHeights
              ? raycastObjectFilteredTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster, zoneTerrainHeight)
              : raycastTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster);
            if (hitElev !== null && isPlausibleTerrainAnchor(hitElev, zoneTerrainHeight)) {
              const zOffset = hitElev - zoneTerrainHeight + FLAT_ZONE_OUTLINE_LIFT_METERS;
              outPos.setZ(i, zOffset);
            }
          }
          // Close the loop vertex
          if (outPos.count > renderCoordinates.length) {
            outPos.setZ(renderCoordinates.length, outPos.getZ(0));
          }
          outPos.needsUpdate = true;
        }
      }

      const coverage = hitCount / geoData.fillCoords.length;
      if (freezeDrape) {
        // Conform thoroughly before locking: freeze only once nearly every vertex
        // has draped (steep, slow-loading tiles need several passes) or the budget
        // is spent. Freezing at 50% left the steep section flat -> parallax drift.
        if (coverage >= 0.92 || drapeAttemptRef.current >= 30) {
          drapedRef.current = true;
          frozenRef.current = true;
        }
      } else if (coverage >= 0.5) {
        drapedRef.current = true;
      }
    }
  }, [tiles, geoData, isBuilding, hasBakedElevationRelief, sampledTerrainHeight, storedTerrainHeight, filterObjectHeights, renderCoordinates, zoneTerrainHeight, freezeDrape, usesLevelCompiledParkDatum]);

  useEffect(() => {
    if (sampledTerrainHeight !== null) return undefined;
    const timers = [
      setTimeout(sampleZoneTerrainHeight, terrainScheduleDelay),
      setTimeout(sampleZoneTerrainHeight, terrainScheduleDelay + 4_000),
      setTimeout(sampleZoneTerrainHeight, terrainScheduleDelay + 10_000),
    ];

    return () => timers.forEach(clearTimeout);
  }, [sampleZoneTerrainHeight, sampledTerrainHeight, terrainScheduleDelay, zone.id, zone.updated_at]);

  // Progressive drape: raycast each vertex onto the tiles at 2s/5s/10s as they
  // stream in. Lightweight zones drape ONCE then freeze (frozenRef) instead of
  // re-draping forever — terrain-accurate without the per-frame storm.
  useEffect(() => {
    if (isBuilding || !tiles || hasBakedElevationRelief || frozenRef.current) return;
    if (!freezeDrape) {
      // Live mode (hand-drawn zones): re-drape from scratch on tile changes.
      drapedRef.current = false;
      drapeAttemptRef.current = 0;
    }
    const timers = [
      setTimeout(drapeToTerrain, terrainScheduleDelay + 500),
      setTimeout(drapeToTerrain, terrainScheduleDelay + 5_000),
      setTimeout(drapeToTerrain, terrainScheduleDelay + 12_000),
    ];
    return () => timers.forEach(clearTimeout);
  }, [tiles, drapeToTerrain, hasBakedElevationRelief, isBuilding, zoneTerrainHeight, freezeDrape, terrainScheduleDelay]);

  // Drape convergence. Heavy mode re-drapes continuously for live accuracy;
  // lightweight mode keeps trying only until the zone freezes, then stops dead.
  useFrame(() => {
    if (sampledTerrainHeight === null && tiles?.group && Math.random() < 0.0002) {
      sampleZoneTerrainHeight();
    }
    if (hasBakedElevationRelief) return;
    if (isBuilding || !tiles?.group) return;
    if (freezeDrape) {
      if (frozenRef.current) return; // drapeToTerrain self-limits via coverage / attempt budget
      if (Math.random() < 0.0002) drapeToTerrain();
      return;
    }
    if (drapedRef.current || drapeAttemptRef.current >= 15) return;
    if (Math.random() < 0.005) drapeToTerrain(); // ~0.5% chance per frame
  });

  const handleZonePointerDown = useCallback((e: { stopPropagation: () => void }) => {
    // When the zone is already selected, let the edit surface behind it
    // receive the pointer event so body dragging can start.
    if (isSelected || selectionEnabled === false) return;
    e.stopPropagation();
    onZoneClick?.(zone.id);
  }, [isSelected, onZoneClick, selectionEnabled, zone.id]);

  // --- Imported zones: drape onto a bare-earth elevation model ---------------
  // Fetch smooth ground heights once (no canopy, no photogrammetry noise) and
  // bake them into a static geometry — no per-frame raycasting, so it's accurate
  // on steep slopes AND cheap. Absolute height is anchored to the sampled tile
  // surface (zoneTerrainHeight); the bare-earth data only supplies relative
  // shape, so the rough geoid estimate cancels out.
  useEffect(() => {
    if (!shouldBakeImportedTerrain || renderCoordinates.length < 3) {
      setBakedElevations(null);
      return;
    }
    let cancelled = false;
    elevationApi
      .getBatch(renderCoordinates)
      .then((elevs) => {
        if (!cancelled && Array.isArray(elevs) && elevs.length >= renderCoordinates.length) {
          setBakedElevations(elevs);
        }
      })
      .catch(() => { /* fall back to flat; non-fatal */ });
    return () => { cancelled = true; };
  }, [renderCoordinates, shouldBakeImportedTerrain]);

  const bakedReference = useMemo(() => {
    if (!hasBakedElevationRelief || !bakedElevations) return null;
    const sorted = bakedElevations.filter(Number.isFinite).slice().sort((a, b) => a - b);
    return sorted.length ? sorted[Math.floor(sorted.length / 2)] : null;
  }, [bakedElevations, hasBakedElevationRelief]);

  const importedFillGeo = useMemo(() => {
    if (!hasBakedElevationRelief || !geoData?.flatTopGeo || !bakedElevations || bakedReference == null) return null;
    const geo = geoData.flatTopGeo.clone();
    const pos = geo.attributes.position;
    const n = Math.min(geoData.fillCoords.length, pos.count, bakedElevations.length);
    for (let i = 0; i < n; i += 1) {
      const e = bakedElevations[i];
      if (Number.isFinite(e)) pos.setZ(i, e - bakedReference + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS);
    }
    pos.needsUpdate = true;
    geo.computeBoundingSphere();
    return geo;
  }, [hasBakedElevationRelief, geoData, bakedElevations, bakedReference]);
  useDeferredDisposable(importedFillGeo);

  // A persisted park orthophoto must use the same bare-earth-conforming mesh
  // as every other imported plan surface. Previously `orthoGeo` won the render
  // choice and silently discarded these baked Z values, producing a flat card
  // on sloping sites. UVs are added to a clone of the conformed geometry.
  const importedOrthoGeo = useMemo(() => {
    if (!groundMeta || !importedFillGeo || !geoData) return null;
    const geo = importedFillGeo.clone();
    applyParkGroundUVs(geo, geoData.fillCoords, groundMeta);
    return geo;
  }, [geoData, groundMeta, importedFillGeo]);

  useDeferredDisposable(importedOrthoGeo);

  const importedOutlineGeo = useMemo(() => {
    if (!hasBakedElevationRelief || !geoData?.outlineGeo || !bakedElevations || bakedReference == null) return null;
    const geo = geoData.outlineGeo.clone();
    const pos = geo.attributes.position;
    const n = Math.min(renderCoordinates.length, pos.count, bakedElevations.length);
    for (let i = 0; i < n; i += 1) {
      const e = bakedElevations[i];
      if (Number.isFinite(e)) pos.setZ(i, e - bakedReference + FLAT_ZONE_OUTLINE_LIFT_METERS);
    }
    if (pos.count > renderCoordinates.length && Number.isFinite(bakedElevations[0])) {
      pos.setZ(renderCoordinates.length, bakedElevations[0] - bakedReference + FLAT_ZONE_OUTLINE_LIFT_METERS);
    }
    pos.needsUpdate = true;
    return geo;
  }, [hasBakedElevationRelief, geoData, bakedElevations, bakedReference, renderCoordinates]);
  useDeferredDisposable(importedOutlineGeo);

  if (!geoData) return null;

  const authoredGroundTexture = drapeActive
    ? groundTexture
    : batch21ParkBaseMaterial?.maps.map ?? woonerfGroundTexture ?? publicRealmBaseTexture;
  const hasAuthoredGroundTexture = Boolean(authoredGroundTexture);

  return (
    <EastNorthUpFrame
      lat={centroid[1] * DEG_TO_RAD}
      lon={centroid[0] * DEG_TO_RAD}
      height={zoneTerrainHeight}
    >
      {/* Fill — flat zones with terrain draping */}
      {/* Fill — flat zones: layered by type */}
      {/* Render order: site_boundary(100) < road(120) < green_space(120.5) <
          street detail strips(122+) < park props(145) < buildings(200).
          Parks sit ABOVE road-zone fills: plan generators emit the street
          network as one solid ground polygon that contains park parcels
          (no carve-out), so a lower park order leaves parks hidden under a
          gray slab. Real roadway strips (street detail) still draw above. */}
      {!isBuilding && geoData.flatTopGeo && (showThisPlanningOverlay || drapeActive || isCompiledGround || isPreparedBoundary) && (
        <mesh
          ref={flatMeshRef}
          geometry={importedOrthoGeo ?? orthoGeo ?? importedFillGeo ?? preparedSiteGeo ?? woonerfGroundGeo ?? publicRealmBaseGeo ?? geoData.flatTopGeo}
          renderOrder={isSiteBoundary ? 100 : communityKind === 'park' ? 120.5 : 120}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
          // Pure planning washes (the translucent boundary/zone fills) are
          // editor chrome, not design content: exclude them from Direct 3D
          // captures so they never tint the render. Compiled/drape surfaces
          // stay captured — they ARE the designed ground.
          userData={
            !isPreparedBoundary && !isCompiledGround && !drapeActive && !isWoonerfGround
              ? DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA
              : undefined
          }
        >
          {/* key remounts the material when the ground drape toggles so the
              map define recompiles (toggling `map` in place leaves it white) */}
          {isPreparedBoundary ? (
            <meshStandardMaterial
              key="prepared-site"
              color="#d5d0c6"
              map={preparedSiteTexture ?? undefined}
              roughness={0.98}
              metalness={0}
              side={THREE.DoubleSide}
              depthTest
              depthWrite
              polygonOffset
              polygonOffsetFactor={4}
              polygonOffsetUnits={8}
            />
          ) : isCompiledGround || drapeActive || isWoonerfGround ? (
            <meshStandardMaterial
              key={drapeActive ? groundMeta?.document_id ?? 'drape' : batch21ParkBaseMaterial ? `batch21-${batch21ParkBaseMaterial.spec.slug}-${batch21ParkBaseMaterial.spec.role}` : isWoonerfGround ? 'woonerf-pavers' : `compiled-${publicRealmBaseKind ?? 'plain'}`}
              color={hasAuthoredGroundTexture ? '#ffffff' : compiledSurfaceColor}
              map={authoredGroundTexture ?? undefined}
              normalMap={batch21ParkBaseMaterial?.maps.normalMap}
              normalScale={batch21ParkBaseMaterial ? new THREE.Vector2(0.38, 0.38) : undefined}
              roughnessMap={batch21ParkBaseMaterial?.maps.roughnessMap}
              roughness={communityKind === 'street' ? 0.94 : 0.98}
              metalness={0}
              transparent={publicRealmDepthPolicy.transparent}
              opacity={1}
              side={THREE.DoubleSide}
              depthTest={publicRealmDepthPolicy.depthTest}
              depthWrite={publicRealmDepthPolicy.depthWrite}
              polygonOffset
              polygonOffsetFactor={FLAT_ZONE_DEPTH_OFFSET_FACTOR}
              polygonOffsetUnits={FLAT_ZONE_DEPTH_OFFSET_UNITS}
            />
          ) : (
            <meshBasicMaterial
              key="plain"
              color={isSiteBoundary ? '#ffffff' : color}
              transparent={publicRealmDepthPolicy.transparent}
              opacity={isSiteBoundary ? 0.15 : 1.0}
              side={THREE.DoubleSide}
              depthTest={publicRealmDepthPolicy.depthTest}
              depthWrite={publicRealmDepthPolicy.depthWrite}
              polygonOffset
              polygonOffsetFactor={isBuilding ? -1 : FLAT_ZONE_DEPTH_OFFSET_FACTOR}
              polygonOffsetUnits={isBuilding ? -1 : FLAT_ZONE_DEPTH_OFFSET_UNITS}
            />
          )}
        </mesh>
      )}

      {/* Fill — buildings on top of everything (skipped when a placed GLB
          model replaces this prism; see GlobeBuildingModelsLayer) */}
      {replacementGroundGeo && (
        <mesh
          geometry={replacementGroundGeo}
          renderOrder={101}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
        >
          <meshBasicMaterial
            key="replacement-footprint-ground"
            color="#9b9488"
            map={replacementGroundTexture ?? undefined}
            side={THREE.DoubleSide}
            depthTest
            depthWrite
            toneMapped={false}
            polygonOffset
            polygonOffsetFactor={4}
            polygonOffsetUnits={8}
          />
        </mesh>
      )}

      {showThisPlanningOverlay && isBuilding && !suppressed && (
        <mesh
          ref={buildingMeshRef}
          geometry={geoData.fillGeo}
          renderOrder={200}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
        >
          <meshBasicMaterial
            color={color}
            transparent
            opacity={1.0}
            side={THREE.DoubleSide}
            depthTest
            depthWrite={false}
            polygonOffset
            polygonOffsetFactor={-1}
            polygonOffsetUnits={-1}
          />
        </mesh>
      )}

      {/* Outline geometry is spread because JSX line resolves to SVG typings here. */}
      {showThisPlanningOverlay && !(isBuilding && suppressed) && (
        <line
          ref={isBuilding ? buildingOutlineRef : flatOutlineRef as any}
          {...({ geometry: !isBuilding ? (importedOutlineGeo ?? geoData.outlineGeo) : geoData.outlineGeo } as any)}
          renderOrder={isBuilding ? 201 : isSiteBoundary ? 101 : communityKind === 'park' ? 120.6 : 121}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
        >
          <lineBasicMaterial
            color={isSelected ? '#ffffff' : color}
            linewidth={isSelected ? 3 : 1.5}
            depthTest
            depthWrite={false}
          />
        </line>
      )}

      {/* Label — positioned above the zone */}
      {showThisPlanningOverlay && (!lightweight || isSelected) && (
        <group position={[0, 0, extrudeHeight + 8]}>
          <Html
            center
            zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
            style={{ pointerEvents: 'none' }}
          >
            <div className="whitespace-nowrap rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-medium text-white backdrop-blur-sm">
              {label}
            </div>
          </Html>
        </group>
      )}
    </EastNorthUpFrame>
  );
}

export function GlobeZoneLayer({
  zones,
  selectedZoneId,
  terrainHeight = 1045,
  onZoneClick,
  selectionEnabled = true,
  suppressedBuildingIds,
  planningOverlaysVisible = true,
}: GlobeZoneLayerProps) {
  // Render-time clean capture (cc_clean_composite): useGlobeAIRender hides the
  // zone overlays for one frame so the composite-back base holds real tiles,
  // not grey zone fill, at the feathered seam ring.
  const [overlaysHidden, setOverlaysHidden] = useState(false);
  useEffect(() => {
    const onToggle = (e: Event) => {
      setOverlaysHidden(Boolean((e as CustomEvent).detail?.hidden));
    };
    window.addEventListener('cityprompt:hide-zone-overlays', onToggle);
    return () => window.removeEventListener('cityprompt:hide-zone-overlays', onToggle);
  }, []);
  const showPlanningOverlays = planningOverlaysVisible && !overlaysHidden;
  const sitePrepared = useMemo(
    () => getPreparedSiteBoundaryIds(zones).size > 0,
    [zones],
  );
  // Big layers (e.g. an imported shapefile) switch every zone to a cheaper path.
  const lightweight = zones.length > LIGHTWEIGHT_ZONE_THRESHOLD;
  return (
    <>
      {zones.map((zone) => {
        const role = direct3DGroundRoleForCommunityKind(resolveCommunity3DKind(zone));
        return (
          <group
            key={zone.id}
            name={`siteforge-direct3d-zone-${zone.id}`}
            userData={{
              ...direct3DProposalUserData(role),
              ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(
                zone.id,
                role,
                zone.building_id ? { building_id: zone.building_id } : {},
              )),
            }}
          >
            <ZoneMesh
              zone={zone}
              isSelected={zone.id === selectedZoneId}
              terrainHeight={terrainHeight}
              onZoneClick={onZoneClick}
              selectionEnabled={selectionEnabled}
              lightweight={lightweight}
              suppressed={Boolean(zone.building_id && suppressedBuildingIds?.has(zone.building_id))}
              planningOverlaysVisible={showPlanningOverlays}
              sitePrepared={sitePrepared}
            />
          </group>
        );
      })}
    </>
  );
}
