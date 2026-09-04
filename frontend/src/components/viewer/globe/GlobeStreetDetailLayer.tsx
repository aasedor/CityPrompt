/**
 * GlobeStreetDetailLayer — subtle procedural 3D for road zones: raised curb
 * bands along both edges, a dashed centerline, and a parametric roundabout
 * for roundabout-archetype zones. Pure-vector geometry (streetMesh3D.ts),
 * never AI image→3D (proven to mangle plan diagrams, 2026-07-10 pilot).
 *
 * Terrain: each zone gets one EastNorthUpFrame at its resolved elevation;
 * stations are then drape-sampled in per-frame batches (drape-and-freeze,
 * same budget pattern as GlobeBuildingModelsLayer) so curbs follow slopes.
 *
 * Render order: road fill 120 < dashes 122 < ring/apron 123 < curbs/island
 * 130 (depth-tested) < placed GLBs 150 < prisms 200.
 */

import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import {
  resolveCommunity3DKind,
  shouldRenderCommunityGround,
} from '@/features/community3d/community3d';
import { extractRenderableStreetCenterline, effectiveRoadWidth } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import {
  getObjectFilteredTerrainHeight,
  isPlausibleTerrainAnchor,
  resolvePublicRealmGroundAnchor,
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import { computeFootprintFrame } from './buildingPlacement';
import {
  buildCurbBandGeometry,
  applyTerrainPlaneToStreetGeometry,
  buildAccessibleFourWayIntersectionGeometry,
  buildDashGeometry,
  buildOffsetCurbGeometry,
  buildParkingStallMarkingGeometry,
  buildRibbonBandGeometry,
  buildRoundaboutGeometry,
  buildSharrowGeometry,
  densifyPolyline,
  stationNormals,
  type LocalPt,
  type StreetStationTerrain,
} from './streetMesh3D';
import {
  fitTerrainContactPlane,
  resolveTerrainContactElevation,
  samplePlaneOffset,
  type TerrainContactSample,
} from './terrainContactProfile';
import { ROUNDABOUT_PARAMS, STREET_DETAIL_3D } from '@/data/streetGeometryParams';
import {
  resolvePilotStreetSectionProfile,
} from './streetSectionProfiles';
import {
  selectDetailedStreetZones,
  selectFurnishedStreetIds,
  selectTreeStreetIds,
  streetTerrainSampleOffset,
} from './streetDetailLod';
import {
  PUBLIC_REALM_DECAL_DEPTH,
  PUBLIC_REALM_DETAIL_DEPTH,
  PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';
import {
  GlobeLandscapeBenchStand,
  GlobeLandscapeTreeStand,
} from './GlobeLandscapeKit';
import {
  detectFourWayStreetIntersections,
  type FourWayStreetIntersection,
} from './streetGraphIntersections';
import { STREET_APPEARANCE_KITS } from './streetFamilyCatalog';
import {
  direct3DInstanceUserData,
  direct3DStreetJunctionInstanceDescriptor,
  direct3DZoneInstanceDescriptor,
} from './direct3dCapture';
import { validateStreetRecipeProperties } from './streetLegoContract';
import {
  buildStreetFamilyFixturePlacements,
  buildWoonerfPlanterPlacements,
  buildWoonerfPlayPlacements,
  buildYieldStreetEntrySignPlacements,
} from './streetFamilyFurniture';
import { GlobeStreetLightInstances } from './GlobeStreetLightInstances';
import { GlobeStreetMicrodetailInstances } from './GlobeStreetMicrodetailInstances';
import { GlobeIntersectionSignalInstances } from './GlobeIntersectionSignalInstances';
import { GlobeStreetVehicleInstances } from './GlobeStreetVehicleInstances';
import { GlobeStreetTransitShelterInstances } from './GlobeStreetTransitShelterInstances';
import { resolveFourWayIntersectionControl } from './streetIntersectionControlPolicy';
import {
  createStreetSurfacePaletteTint,
  createStreetSurfaceMaterialResources,
  resolveStreetAppearanceMaterialKind,
  resolveStreetSurfaceMaterialKind,
  type StreetSurfaceMaterialResources,
} from './streetSurfaceMaterials';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { getStreetNetworkGroundMeta } from './streetNetworkGroundTexture';

const DEG_TO_RAD = Math.PI / 180;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
// Three cross-section rays (left/centre/right) per station. Four stations keep
// the previous 12-ray frame budget while adding real cross-slope contact.
const STATIONS_PER_BATCH = 4;
// Re-sample stations that missed (tile not yet streamed) up to this many
// passes before freezing — early rays against coarse LOD tiles miss a lot.
const MAX_SAMPLE_PASSES = 3;

const CURB_COLOR = '#9aa0a6';
const DASH_COLOR = '#e0e2e4';
const RENDER_ORDER_DASHES = 122;
const RENDER_ORDER_FLATWORK = 123;
const RENDER_ORDER_RAISED = 130;
const RENDER_ORDER_FURNITURE = 135;
function isRoundaboutZone(zone: SiteZone): boolean {
  const props = zone.properties as Record<string, unknown> | undefined;
  const validation = validateStreetRecipeProperties(props);
  if (validation.valid) return validation.recipe.familyId === 'street_compact_roundabout';
  return [props?.road_archetype_id, props?.street_role]
    .some((value) => String(value ?? '').toLowerCase().replace(/-/g, '_').includes('roundabout'));
}

function zoneStoredTerrain(zone: SiteZone): number | null {
  const props = zone.properties as Record<string, unknown> | undefined;
  const raw = Number(props?.terrain_elevation_m ?? props?.terrain_height);
  return Number.isFinite(raw) ? raw : null;
}

/** One road zone's curbs + dashes, draped station-by-station. */
function StreetRibbonDetail({
  zone,
  fallbackTerrainHeight,
  preparedTerrain = null,
  intersectionNodes,
  renderFamilyFurniture,
  renderFamilyTrees,
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
  intersectionNodes: FourWayStreetIntersection[];
  renderFamilyFurniture: boolean;
  renderFamilyTrees: boolean;
  preparedTerrain?: number | null;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  // Across a district plan, distribute terrain rays over the full sampling
  // interval instead of making every street probe the tiles on one frame.
  const frameCountRef = useRef(streetTerrainSampleOffset(zone.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const nextStationRef = useRef(0);
  const rawTerrainRef = useRef<Array<{
    center: number | null;
    left: number | null;
    right: number | null;
  }> | null>(null);
  const frozenRef = useRef(false);
  const [stationTerrain, setStationTerrain] = useState<StreetStationTerrain[] | null>(null);
  const sectionProfile = useMemo(
    () => resolvePilotStreetSectionProfile(zone),
    [zone],
  );
  const hasAuthoredNetworkGround = Boolean(getStreetNetworkGroundMeta(zone));
  const bandMaterials = useMemo(() => {
    if (!sectionProfile) return [];
    const resourcesByKey = new Map<string, StreetSurfaceMaterialResources>();
    return sectionProfile.bands
      .filter((band) => band.sourceType !== 'setback')
      .map((band) => {
      const baseKind = resolveStreetSurfaceMaterialKind({
        kind: band.kind,
        sourceType: band.sourceType,
        surface: band.surface,
        label: band.label,
      });
      const kind = resolveStreetAppearanceMaterialKind(
        baseKind,
        sectionProfile.appearanceKitId,
        band.kind,
      );
      const palette = sectionProfile.appearance?.palette;
      const paletteColor = (() => {
        if (!palette) return band.color;
        switch (band.kind) {
          case 'motor': return palette.motor;
          case 'parking': return palette.parking;
          case 'cycle': return palette.cycle;
          case 'sidewalk': return palette.sidewalk;
          case 'planting':
          case 'median': return palette.planting;
          case 'buffer': return palette.buffer;
          case 'shoulder': return palette.shoulder;
          case 'path': return palette.path;
          default: return band.color;
        }
      })();
      const tint = createStreetSurfacePaletteTint(paletteColor);
      const key = [kind, tint.getHexString(), band.roughness, band.metalness].join('|');
      const existing = resourcesByKey.get(key);
      if (existing) return existing;
      const resources = createStreetSurfaceMaterialResources(kind, {
        seed: `${sectionProfile.archetypeId}:${sectionProfile.variantId ?? 'base'}:${kind}`,
        tint,
        roughness: band.roughness,
        metalness: band.metalness,
        anisotropy: 8,
      });
      Object.assign(resources.material, {
        depthTest: PUBLIC_REALM_DETAIL_DEPTH.depthTest,
        depthWrite: PUBLIC_REALM_DETAIL_DEPTH.depthWrite,
        polygonOffset: true,
        polygonOffsetFactor: -3,
        polygonOffsetUnits: -6,
      });
      resourcesByKey.set(key, resources);
      return resources;
    });
  }, [sectionProfile]);
  useEffect(
    () => retainResourceForDeferredDisposal(bandMaterials, (ownedMaterials) => {
      new Set(ownedMaterials).forEach((resources) => resources.dispose());
    }),
    [bandMaterials],
  );

  // Centerline in lng/lat, densified so stations follow terrain.
  const { centerLngLat, centroid, halfWidth, sectionScale } = useMemo(() => {
    const center = extractRenderableStreetCenterline(zone);
    if (center.length < 2) return {
      centerLngLat: null, centroid: null, halfWidth: 0, sectionScale: 1,
    };
    let lng = 0;
    let lat = 0;
    for (const c of center) {
      lng += c[0];
      lat += c[1];
    }
    lng /= center.length;
    lat /= center.length;
    const mPerLon = metersPerDegLon(lat);
    const localPts: LocalPt[] = center.map((c) => ({
      x: (c[0] - lng) * mPerLon,
      y: (c[1] - lat) * METERS_PER_DEG_LAT,
    }));
    const densified = densifyPolyline(localPts, STREET_DETAIL_3D.stationStep_m);
    const normals = stationNormals(densified);
    const back = densified.map((p) => [
      lng + p.x / mPerLon,
      lat + p.y / METERS_PER_DEG_LAT,
    ]);
    const resolvedHalfWidth = sectionProfile?.metricWidthLocked
      ? (sectionProfile.targetRowM ?? sectionProfile.rowM) / 2
      : effectiveRoadWidth(zone.properties) / 2;
    return {
      centerLngLat: { local: densified, lngLat: back, normals },
      centroid: { lng, lat },
      halfWidth: resolvedHalfWidth,
      sectionScale: sectionProfile?.metricWidthLocked
        ? (sectionProfile.targetRowM ?? sectionProfile.rowM) / sectionProfile.rowM
        : (sectionProfile ? (resolvedHalfWidth * 2) / sectionProfile.rowM : 1),
    };
    // zone.updated_at covers property edits that re-buffer the polygon
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zone.coordinates, zone.updated_at, zone.properties, sectionProfile]);

  const storedTerrain = zoneStoredTerrain(zone);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const hitFlagsRef = useRef<boolean[] | null>(null);
  const passRef = useRef(0);
  const frameElevation = preparedTerrain ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  // Geometry edits (vertex drag commits, re-buffering) change coordinates
  // under the SAME zone id — the frozen drape state must restart or curbs
  // keep the old location's elevations.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    nextStationRef.current = 0;
    passRef.current = 0;
    rawTerrainRef.current = null;
    hitFlagsRef.current = null;
    setStationTerrain(null);
    setSampledTerrain(null);
  }, [centerLngLat]);

  // Drape-and-freeze: first resolve the frame anchor, then batch-sample
  // per-station elevations relative to it. Batches are interval-gated too —
  // consecutive-frame sampling right after mount rays against coarse LOD
  // tiles and bakes garbage; missed stations get re-sampled across passes.
  useFrame(() => {
    if (preparedTerrain !== null || frozenRef.current || !centerLngLat || !centroid) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const anchored = sampledTerrain !== null;
    if (!anchored) {
      if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
        frozenRef.current = true;
        return;
      }
      attemptsRef.current += 1;
      const mid = centerLngLat.lngLat[Math.floor(centerLngLat.lngLat.length / 2)];
      const samples = [centerLngLat.lngLat[0], mid, centerLngLat.lngLat[centerLngLat.lngLat.length - 1]]
        .map(([lng, lat]) => raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current));
      const filtered = getObjectFilteredTerrainHeight(samples, storedTerrain);
      const groundCandidate = resolvePublicRealmGroundAnchor(
        filtered,
        storedTerrain,
        fallbackTerrainHeight,
        4,
      );
      if (
        groundCandidate !== null
        && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
      ) setSampledTerrain(groundCandidate);
      return;
    }

    // Anchor known — drape stations in gated batches, accumulated in refs
    // (state is set ONCE at freeze so geometry rebuilds once).
    const anchor = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
    const n = centerLngLat.lngLat.length;
    if (!rawTerrainRef.current || rawTerrainRef.current.length !== n) {
      rawTerrainRef.current = Array.from({ length: n }, () => ({
        center: null,
        left: null,
        right: null,
      }));
      hitFlagsRef.current = new Array<boolean>(n).fill(false);
      nextStationRef.current = 0;
      passRef.current = 0;
    }
    const rawTerrain = rawTerrainRef.current;
    const hits = hitFlagsRef.current!;
    const mPerLon = metersPerDegLon(centroid.lat);
    let i = nextStationRef.current;
    let processed = 0;
    while (i < n && processed < STATIONS_PER_BATCH) {
      if (!hits[i]) {
        const point = centerLngLat.local[i];
        const normal = centerLngLat.normals[i];
        const probeAt = (offsetM: number): number | null => {
          const lng = centroid.lng + (point.x + normal.x * offsetM) / mPerLon;
          const lat = centroid.lat + (point.y + normal.y * offsetM) / METERS_PER_DEG_LAT;
          const sampled = raycastTerrainHeightAtLatLng(
            lng,
            lat,
            tilesGroup,
            raycasterRef.current,
          );
          return isPlausibleTerrainAnchor(sampled, anchor) ? sampled : null;
        };
        rawTerrain[i] = {
          center: probeAt(0),
          left: probeAt(halfWidth),
          right: probeAt(-halfWidth),
        };
        hits[i] = Object.values(rawTerrain[i]).some(Number.isFinite);
        processed++;
      }
      i++;
    }
    nextStationRef.current = i;
    if (i >= n) {
      const misses = hits.filter((x) => !x).length;
      if (misses > n * 0.2 && passRef.current < MAX_SAMPLE_PASSES) {
        passRef.current += 1;
        nextStationRef.current = 0;
        return;
      }
      const fitSamples: TerrainContactSample[] = [];
      rawTerrain.forEach((sample, stationIndex) => {
        const point = centerLngLat.local[stationIndex];
        const normal = centerLngLat.normals[stationIndex];
        ([
          [0, sample.center],
          [halfWidth, sample.left],
          [-halfWidth, sample.right],
        ] as const).forEach(([offsetM, elevation]) => {
          if (!Number.isFinite(elevation)) return;
          fitSamples.push({
            x: point.x + normal.x * offsetM,
            y: point.y + normal.y * offsetM,
            z: elevation as number,
          });
        });
      });
      const plane = fitTerrainContactPlane(fitSamples, {
        fallbackElevationMeters: anchor,
        outlierToleranceMeters: 1.5,
      });
      const profile = rawTerrain.map((sample, stationIndex): StreetStationTerrain => {
        const point = centerLngLat.local[stationIndex];
        const normal = centerLngLat.normals[stationIndex];
        const elevationAt = (offsetM: number, sampled: number | null): number => {
          const x = point.x + normal.x * offsetM;
          const y = point.y + normal.y * offsetM;
          return (resolveTerrainContactElevation(plane, sampled, x, y) ?? anchor) - anchor;
        };
        return {
          centerZ: elevationAt(0, sample.center),
          leftZ: elevationAt(halfWidth, sample.left),
          rightZ: elevationAt(-halfWidth, sample.right),
          halfWidthM: halfWidth,
        };
      });
      frozenRef.current = true;
      setStationTerrain(profile);
    }
  });

  const geometries = useMemo(() => {
    if (!centerLngLat) return null;
    const zs = stationTerrain ?? undefined;
    const mPerLon = centroid ? metersPerDegLon(centroid.lat) : 1;
    const connectedIntersectionNodes = intersectionNodes.filter((node) => node.zoneIds.includes(zone.id));
    const curbRampClearanceMask = centerLngLat.local.map((point) => (
      Boolean(centroid) && connectedIntersectionNodes.some((node) => {
        const localX = (node.longitude - centroid!.lng) * mPerLon;
        const localY = (node.latitude - centroid!.lat) * METERS_PER_DEG_LAT;
        const clearanceM = Math.max(node.axisAHalfWidthM, node.axisBHalfWidthM) + 4;
        return Math.hypot(point.x - localX, point.y - localY) <= clearanceM;
      })
    ));
    const bands = sectionProfile
      ? sectionProfile.bands
        .filter((band) => band.sourceType !== 'setback')
        .map((band) => ({
          band,
          geometry: buildRibbonBandGeometry(
            centerLngLat.local,
            band.startM * sectionScale,
            band.endM * sectionScale,
            band.liftM,
            zs,
          ),
        }))
        .filter((item): item is typeof item & { geometry: THREE.BufferGeometry } => Boolean(item.geometry))
      : [];
    const markings = sectionProfile
      ? sectionProfile.markings
        .map((marking) => ({
          marking,
          geometry: marking.dashed
            ? buildDashGeometry(
              centerLngLat.local,
              {
                ...STREET_DETAIL_3D,
                dashLength_m: 3,
                dashGap_m: 5,
                dashWidth_m: marking.widthM * sectionScale,
                dashLift_m: PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
              },
              zs,
              marking.offsetM * sectionScale,
            )
            : buildRibbonBandGeometry(
              centerLngLat.local,
              (marking.offsetM - marking.widthM / 2) * sectionScale,
              (marking.offsetM + marking.widthM / 2) * sectionScale,
              PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
              zs,
            ),
        }))
        .filter((item): item is typeof item & { geometry: THREE.BufferGeometry } => Boolean(item.geometry))
      : [];
    const isCompleteMainStreet = sectionProfile?.archetypeId === 'main_street_complete';
    const parkingMarkings = isCompleteMainStreet
      ? sectionProfile.bands
        .filter((band) => band.kind === 'parking')
        .map((band) => buildParkingStallMarkingGeometry(
          centerLngLat.local,
          band.startM * sectionScale,
          band.endM * sectionScale,
          zs,
          6,
          13,
          curbRampClearanceMask,
        ))
        .filter((geometry): geometry is THREE.BufferGeometry => Boolean(geometry))
      : [];
    const sharrows = isCompleteMainStreet
      ? buildSharrowGeometry(
        centerLngLat.local,
        sectionProfile.bands
          .filter((band) => band.kind === 'motor')
          .map((band) => band.centerM * sectionScale),
        zs,
        28,
        18,
        curbRampClearanceMask,
      )
      : null;
    return {
      curbs: sectionProfile
        ? (sectionProfile.renderCurbs
          ? buildOffsetCurbGeometry(
            centerLngLat.local,
            sectionProfile.curbOffsetsM.map((offset) => offset * sectionScale),
            STREET_DETAIL_3D,
            zs,
            curbRampClearanceMask,
          )
          : null)
        : buildCurbBandGeometry(centerLngLat.local, halfWidth, STREET_DETAIL_3D, zs),
      dashes: sectionProfile ? null : buildDashGeometry(centerLngLat.local, STREET_DETAIL_3D, zs),
      bands,
      markings,
      parkingMarkings,
      sharrows,
    };
  }, [centerLngLat, centroid, halfWidth, intersectionNodes, sectionProfile, sectionScale, stationTerrain, zone.id]);

  const woonerfPlanters = useMemo(() => {
    if (
      !centerLngLat
      || !sectionProfile
      || !['woonerf_shared_street', 'yield_street'].includes(sectionProfile.archetypeId)
    ) return [];
    return buildWoonerfPlanterPlacements(centerLngLat.local, halfWidth, stationTerrain);
  }, [centerLngLat, halfWidth, sectionProfile, stationTerrain]);

  const woonerfTrees = useMemo(
    () => woonerfPlanters.map((placement, index) => ({
      x: placement.x,
      y: placement.y,
      z: placement.z + 0.54,
      yawRad: placement.rotation + index * 0.73,
      scale: 0.68 + (index % 3) * 0.07,
    })),
    [woonerfPlanters],
  );

  const woonerfPlayNodes = useMemo(
    () => sectionProfile?.archetypeId === 'woonerf_shared_street'
      ? buildWoonerfPlayPlacements(woonerfPlanters)
      : [],
    [sectionProfile?.archetypeId, woonerfPlanters],
  );

  const yieldStreetSigns = useMemo(() => (
    centerLngLat && sectionProfile?.archetypeId === 'yield_street'
      ? buildYieldStreetEntrySignPlacements(centerLngLat.local, halfWidth, stationTerrain)
      : []
  ), [centerLngLat, halfWidth, sectionProfile?.archetypeId, stationTerrain]);

  const woonerfBenches = useMemo(
    () => woonerfPlanters
      .filter((_, index) => index % 2 === 1)
      .map((placement) => {
        const offset = -1.52;
        return {
          x: placement.x - Math.sin(placement.rotation) * offset,
          y: placement.y + Math.cos(placement.rotation) * offset,
          z: placement.z,
          yawRad: placement.rotation,
          scale: 0.92,
        };
      }),
    [woonerfPlanters],
  );

  const familyFixtures = useMemo(() => {
    const mPerLon = centroid ? metersPerDegLon(centroid.lat) : 1;
    return buildStreetFamilyFixturePlacements({
      points: centerLngLat?.local ?? [],
      stationZ: stationTerrain,
      profile: sectionProfile,
      sectionScale,
      enabled: renderFamilyFurniture,
      clearancePoints: centroid
        ? intersectionNodes
          .filter((node) => node.zoneIds.includes(zone.id))
          .map((node) => ({
            x: (node.longitude - centroid.lng) * mPerLon,
            y: (node.latitude - centroid.lat) * METERS_PER_DEG_LAT,
          }))
        : [],
    });
  }, [
    centerLngLat,
    centroid,
    intersectionNodes,
    renderFamilyFurniture,
    sectionProfile,
    sectionScale,
    stationTerrain,
    zone.id,
  ]);

  // r3f does not dispose geometry props — without this every drape freeze,
  // edit commit, and zone delete leaks the previous buffers.
  useEffect(() => {
    if (!geometries) return undefined;
    return retainResourceForDeferredDisposal(geometries, (ownedGeometries) => {
      ownedGeometries.curbs?.dispose();
      ownedGeometries.dashes?.dispose();
      ownedGeometries.bands.forEach((item) => item.geometry.dispose());
      ownedGeometries.markings.forEach((item) => item.geometry.dispose());
      ownedGeometries.parkingMarkings.forEach((geometry) => geometry.dispose());
      ownedGeometries.sharrows?.dispose();
    });
  }, [geometries]);

  if (!centerLngLat || !centroid || !geometries) return null;

  return (
    <EastNorthUpFrame
      lat={centroid.lat * DEG_TO_RAD}
      lon={centroid.lng * DEG_TO_RAD}
      height={frameElevation}
    >
      {!hasAuthoredNetworkGround && geometries.bands.map(({ band, geometry }, index) => (
        <mesh
          key={`${band.sourceType}-${band.startM}`}
          geometry={geometry}
          renderOrder={RENDER_ORDER_FLATWORK}
          frustumCulled={false}
        >
          <primitive object={bandMaterials[index].material} attach="material" />
        </mesh>
      ))}
      {geometries.markings.map(({ marking, geometry }, index) => (
        <mesh
          key={`${marking.offsetM}-${index}`}
          geometry={geometry}
          renderOrder={RENDER_ORDER_DASHES}
          frustumCulled={false}
        >
          <meshBasicMaterial
            color={marking.color}
            depthTest={PUBLIC_REALM_DECAL_DEPTH.depthTest}
            depthWrite={PUBLIC_REALM_DECAL_DEPTH.depthWrite}
            polygonOffset
            polygonOffsetFactor={-4}
            polygonOffsetUnits={-8}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
      {[...geometries.parkingMarkings, ...(geometries.sharrows ? [geometries.sharrows] : [])]
        .map((geometry, index) => (
          <mesh
            key={`street-signature-marking-${index}`}
            geometry={geometry}
            renderOrder={RENDER_ORDER_DASHES + 1}
            frustumCulled={false}
          >
            <meshBasicMaterial
              color={sectionProfile?.appearance?.palette.marking ?? DASH_COLOR}
              depthTest={PUBLIC_REALM_DECAL_DEPTH.depthTest}
              depthWrite={PUBLIC_REALM_DECAL_DEPTH.depthWrite}
              polygonOffset
              polygonOffsetFactor={-5}
              polygonOffsetUnits={-10}
              side={THREE.DoubleSide}
            />
          </mesh>
        ))}
      {geometries.curbs && (
        <mesh geometry={geometries.curbs} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshStandardMaterial
            color={sectionProfile?.appearance?.palette.curb ?? CURB_COLOR}
            roughness={0.94}
            metalness={0}
            polygonOffset
            polygonOffsetFactor={-2}
            polygonOffsetUnits={-4}
          />
        </mesh>
      )}
      {geometries.dashes && (
        <mesh geometry={geometries.dashes} renderOrder={RENDER_ORDER_DASHES} frustumCulled={false}>
          <meshBasicMaterial
            color={DASH_COLOR}
            depthTest={PUBLIC_REALM_DECAL_DEPTH.depthTest}
            depthWrite={PUBLIC_REALM_DECAL_DEPTH.depthWrite}
            polygonOffset
            polygonOffsetFactor={-4}
            polygonOffsetUnits={-8}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      <GlobeLandscapeTreeStand placements={woonerfTrees} renderOrder={RENDER_ORDER_FURNITURE} />
      <GlobeLandscapeBenchStand placements={woonerfBenches} renderOrder={RENDER_ORDER_FURNITURE} />
      <GlobeLandscapeTreeStand
        placements={renderFamilyTrees ? familyFixtures.trees : []}
        renderOrder={RENDER_ORDER_FURNITURE}
      />
      <GlobeLandscapeBenchStand placements={familyFixtures.benches} renderOrder={RENDER_ORDER_FURNITURE} />
      <GlobeStreetLightInstances
        placements={familyFixtures.lights}
        metalColor={sectionProfile?.appearance?.palette.fixtureMetal ?? '#30383a'}
        renderOrder={RENDER_ORDER_FURNITURE}
      />
      <GlobeStreetMicrodetailInstances
        fixtures={familyFixtures}
        fixtureMetalColor={sectionProfile?.appearance?.palette.fixtureMetal ?? '#30383a'}
        renderOrder={RENDER_ORDER_FURNITURE}
      />
      <GlobeStreetVehicleInstances
        placements={familyFixtures.parkedVehicles}
        renderOrder={RENDER_ORDER_FURNITURE + 2}
      />
      <GlobeStreetTransitShelterInstances
        placements={familyFixtures.transitShelters.map((placement) => ({
          ...placement,
          z: placement.z + placement.surfaceLiftM,
        }))}
        renderOrder={RENDER_ORDER_FURNITURE + 3}
      />
      {yieldStreetSigns.map((placement, index) => (
        <group
          key={`yield-street-entry-sign-${index}`}
          position={[placement.x, placement.y, placement.z]}
          rotation={[0, 0, placement.yawRad]}
        >
          <mesh
            position={[0, 0, 0.82]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_FURNITURE + 1}
          >
            <cylinderGeometry args={[0.032, 0.042, 1.64, 8]} />
            <meshStandardMaterial color="#353b3c" metalness={0.55} roughness={0.42} />
          </mesh>
          <mesh
            position={[0, 0, 1.7]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_FURNITURE + 2}
          >
            <circleGeometry args={[0.36, 3, -Math.PI / 2]} />
            <meshStandardMaterial color="#c93434" roughness={0.65} side={THREE.DoubleSide} />
          </mesh>
        </group>
      ))}
      {woonerfPlayNodes.map((placement, index) => (
        <group
          key={`woonerf-play-node-${index}`}
          position={[placement.x, placement.y, placement.z]}
          rotation={[0, 0, placement.rotation]}
          scale={placement.scale}
        >
          <mesh
            position={[0, 0, 0.045]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_FLATWORK + 1}
          >
            <cylinderGeometry args={[1.08, 1.08, 0.09, 20]} />
            <meshStandardMaterial color="#b89163" roughness={0.96} />
          </mesh>
          {[-0.62, 0, 0.62].map((localX, boulderIndex) => (
            <mesh
              key={`play-boulder-${boulderIndex}`}
              position={[localX, boulderIndex % 2 === 0 ? -0.24 : 0.2, 0.2 + boulderIndex * 0.035]}
              scale={[0.34, 0.3, 0.28 + boulderIndex * 0.03]}
              renderOrder={RENDER_ORDER_FURNITURE}
            >
              <dodecahedronGeometry args={[1, 0]} />
              <meshStandardMaterial color={boulderIndex === 1 ? '#a98f6c' : '#8c806d'} roughness={1} />
            </mesh>
          ))}
          <mesh position={[0, 0.62, 0.28]} renderOrder={RENDER_ORDER_FURNITURE + 1}>
            <boxGeometry args={[1.55, 0.16, 0.16]} />
            <meshStandardMaterial color="#72513a" roughness={0.9} />
          </mesh>
        </group>
      ))}
      {woonerfPlanters.map((placement, index) => (
        <group key={`woonerf-planter-${index}`}>
          <mesh
            position={[placement.centerX, placement.centerY, placement.centerZ + 0.17]}
            rotation={[0, 0, placement.rotation]}
            renderOrder={RENDER_ORDER_FURNITURE}
          >
            <boxGeometry args={[
              sectionProfile?.archetypeId === 'woonerf_shared_street' && index % 4 === 2
                ? 3.2
                : 0.55,
              halfWidth * 1.55,
              0.06,
            ]} />
            <meshStandardMaterial color="#d2bea0" roughness={0.90} />
          </mesh>
          <group
            position={[placement.x, placement.y, placement.z]}
            rotation={[0, 0, placement.rotation]}
            renderOrder={RENDER_ORDER_FURNITURE}
          >
            <mesh position={[0, 0, 0.25]} renderOrder={RENDER_ORDER_FURNITURE}>
              <boxGeometry args={[2.4, 1.2, 0.5]} />
              <meshStandardMaterial color="#765442" roughness={0.80} metalness={0.08} />
            </mesh>
            <mesh position={[0, 0, 0.53]} renderOrder={RENDER_ORDER_FURNITURE}>
              <boxGeometry args={[2.14, 0.94, 0.08]} />
              <meshStandardMaterial color="#3c3228" roughness={1} />
            </mesh>
            {[-0.72, 0, 0.72].map((shrubX, shrubIndex) => (
              <mesh
                key={`shrub-${shrubX}`}
                position={[shrubX, shrubIndex === 1 ? -0.18 : 0.16, 0.72 + shrubIndex * 0.03]}
                scale={[0.72, 0.58, 0.62 + shrubIndex * 0.08]}
                renderOrder={RENDER_ORDER_FURNITURE}
              >
                <icosahedronGeometry args={[0.46, 2]} />
                <meshStandardMaterial
                  color={shrubIndex === 1 ? '#6f8452' : '#587447'}
                  roughness={0.96}
                />
              </mesh>
            ))}
            {[-1.45, 1.45].map((bollardX) => (
              <mesh
                key={bollardX}
                position={[bollardX, 0, 0.42]}
                rotation={[Math.PI / 2, 0, 0]}
                renderOrder={RENDER_ORDER_FURNITURE}
              >
                <cylinderGeometry args={[0.09, 0.11, 0.84, 10]} />
                <meshStandardMaterial color="#343b3b" metalness={0.48} roughness={0.5} />
              </mesh>
            ))}
          </group>
        </group>
      ))}
    </EastNorthUpFrame>
  );
}

/** Parametric roundabout for roundabout-archetype zones. */
function RoundaboutDetail({
  zone,
  fallbackTerrainHeight,
  preparedTerrain = null,
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
  preparedTerrain?: number | null;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(streetTerrainSampleOffset(zone.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const [terrainPlane, setTerrainPlane] = useState<ReturnType<typeof fitTerrainContactPlane>>(null);
  const sectionProfile = useMemo(
    () => resolvePilotStreetSectionProfile(zone),
    [zone],
  );
  const hasAuthoredNetworkGround = Boolean(getStreetNetworkGroundMeta(zone));
  const appearance = sectionProfile?.appearance
    ?? STREET_APPEARANCE_KITS.classic_tree_lined_v1;
  const roundaboutMaterials = useMemo(() => {
    const ring = createStreetSurfaceMaterialResources('asphalt', {
      seed: `${appearance.id}:roundabout:ring`,
      anisotropy: 8,
    });
    const concrete = createStreetSurfaceMaterialResources('concrete', {
      seed: `${appearance.id}:roundabout:apron`,
      anisotropy: 8,
    });
    const planting = createStreetSurfaceMaterialResources('planting_grass', {
      seed: `${appearance.id}:roundabout:planting`,
      anisotropy: 8,
    });
    for (const resources of [ring, concrete, planting]) {
      Object.assign(resources.material, {
        depthTest: PUBLIC_REALM_DETAIL_DEPTH.depthTest,
        depthWrite: PUBLIC_REALM_DETAIL_DEPTH.depthWrite,
      });
    }
    return { ring, concrete, planting };
  }, [appearance.id]);
  useEffect(
    () => retainResourceForDeferredDisposal(roundaboutMaterials, (ownedMaterials) => {
      ownedMaterials.ring.dispose();
      ownedMaterials.concrete.dispose();
      ownedMaterials.planting.dispose();
    }),
    [roundaboutMaterials],
  );

  const frame = useMemo(() => computeFootprintFrame(zone.coordinates), [zone.coordinates]);
  const storedTerrain = zoneStoredTerrain(zone);
  const terrain = preparedTerrain ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
  const geometry = useMemo(() => {
    if (!frame) return null;
    const inscribed = Math.min(frame.longDim, frame.shortDim) / 2;
    const result = buildRoundaboutGeometry(inscribed, frame.bearingRad);
    if (!result || !terrainPlane) return result;
    for (const item of [
      result.ring,
      result.apron,
      result.island,
      result.splitters,
      result.splitterPlanting,
      result.sidewalks,
      result.approachMarkings,
    ]) {
      applyTerrainPlaneToStreetGeometry(
        item,
        terrainPlane,
        terrain,
        frame.rectCenterLocal[0],
        frame.rectCenterLocal[1],
      );
    }
    return result;
  }, [frame, terrain, terrainPlane]);

  useEffect(() => {
    if (!geometry) return undefined;
    return retainResourceForDeferredDisposal(geometry, (ownedGeometry) => {
      ownedGeometry.ring.dispose();
      ownedGeometry.apron.dispose();
      ownedGeometry.island.dispose();
      ownedGeometry.splitters.dispose();
      ownedGeometry.splitterPlanting.dispose();
      ownedGeometry.sidewalks.dispose();
      ownedGeometry.approachMarkings.dispose();
    });
  }, [geometry]);

  // Zone moved/reshaped under the same id — resample the anchor.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    setSampledTerrain(null);
    setTerrainPlane(null);
  }, [frame]);

  useFrame(() => {
    if (preparedTerrain !== null || frozenRef.current || !frame) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;
    const ring = zone.coordinates;
    const step = Math.max(1, Math.floor(ring.length / 4));
    const probes: Array<[number, number]> = [[frame.centroidLng, frame.centroidLat]];
    for (let index = 0; index < ring.length && probes.length < 5; index += step) {
      probes.push([ring[index][0], ring[index][1]]);
    }
    const samples = probes.map(([lng, lat]) => (
      raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current)
    ));
    const filtered = getObjectFilteredTerrainHeight(samples, storedTerrain);
    const groundCandidate = resolvePublicRealmGroundAnchor(
      filtered,
      storedTerrain,
      fallbackTerrainHeight,
      4,
    );
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
    ) {
      const mPerLon = metersPerDegLon(frame.centroidLat);
      const contactSamples: TerrainContactSample[] = probes.flatMap(([lng, lat], index) => (
        isPlausibleTerrainAnchor(samples[index], groundCandidate)
          ? [{
            x: (lng - frame.centroidLng) * mPerLon,
            y: (lat - frame.centroidLat) * METERS_PER_DEG_LAT,
            z: samples[index] as number,
          }]
          : []
      ));
      setTerrainPlane(fitTerrainContactPlane(contactSamples, {
        fallbackElevationMeters: groundCandidate,
        outlierToleranceMeters: 1.5,
      }));
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  if (!frame || !geometry) return null;
  const roundaboutTerrainZ = (x: number, y: number): number => terrainPlane
    ? terrainPlane.originZ + samplePlaneOffset(
      terrainPlane,
      x + frame.rectCenterLocal[0],
      y + frame.rectCenterLocal[1],
    ) - terrain
    : 0;
  const signRadiusM = (
    ROUNDABOUT_PARAMS.ICD / 2
    + ROUNDABOUT_PARAMS.SETBK
    + ROUNDABOUT_PARAMS.CW
    + 1.4
  ) * geometry.scale;
  const approachSigns = Array.from({ length: 4 }, (_, index) => {
    const angle = frame.bearingRad + index * Math.PI / 2;
    const x = Math.cos(angle) * signRadiusM;
    const y = Math.sin(angle) * signRadiusM;
    return {
      angle,
      x,
      y,
      z: roundaboutTerrainZ(x, y),
    };
  });
  const lampRadiusM = (
    ROUNDABOUT_PARAMS.ICD / 2
    + ROUNDABOUT_PARAMS.SETBK
    + ROUNDABOUT_PARAMS.CW
    + 1.8
  ) * geometry.scale;
  const lampLateralOffsetM = (ROUNDABOUT_PARAMS.APP / 2 + 1.15) * geometry.scale;
  const approachLights = Array.from({ length: 4 }, (_, index) => {
    const angle = frame.bearingRad + index * Math.PI / 2;
    const tangentX = Math.cos(angle);
    const tangentY = Math.sin(angle);
    const normalX = -tangentY;
    const normalY = tangentX;
    return [-1, 1].map((side) => {
      const x = tangentX * lampRadiusM + normalX * lampLateralOffsetM * side;
      const y = tangentY * lampRadiusM + normalY * lampLateralOffsetM * side;
      return {
        angle,
        x,
        y,
        z: roundaboutTerrainZ(x, y),
        stationIndex: 0,
        stationM: 0,
        tangentX,
        tangentY,
        normalX,
        normalY,
        yawRad: angle + (side < 0 ? Math.PI / 2 : -Math.PI / 2),
        offsetM: lampLateralOffsetM * side,
      };
    });
  }).flat();
  const approachTreeRadiusM = (
    ROUNDABOUT_PARAMS.ICD / 2
    + ROUNDABOUT_PARAMS.SETBK
    + ROUNDABOUT_PARAMS.CW
    + 3.8
  ) * geometry.scale;
  const approachTreeLateralOffsetM = (ROUNDABOUT_PARAMS.APP / 2 + 2.35) * geometry.scale;
  const roundaboutAppearanceStyle = (() => {
    switch (appearance.id) {
      case 'modern_minimalist_v1':
        return { canopyClass: 'columnar_deciduous' as const, lightStyle: 'contemporary' as const };
      case 'european_cobblestone_v1':
        return { canopyClass: 'pollarded_deciduous' as const, lightStyle: 'traditional' as const };
      case 'tropical_boulevard_v1':
        return { canopyClass: 'tropical_palm' as const, lightStyle: 'contemporary' as const };
      default:
        return { canopyClass: 'mature_deciduous' as const, lightStyle: 'traditional' as const };
    }
  })();
  const approachTrees = Array.from({ length: 4 }, (_, index) => {
    const angle = frame.bearingRad + index * Math.PI / 2;
    const tangentX = Math.cos(angle);
    const tangentY = Math.sin(angle);
    const normalX = -tangentY;
    const normalY = tangentX;
    return [-1, 1].map((side) => {
      const x = tangentX * approachTreeRadiusM + normalX * approachTreeLateralOffsetM * side;
      const y = tangentY * approachTreeRadiusM + normalY * approachTreeLateralOffsetM * side;
      return {
        x,
        y,
        z: roundaboutTerrainZ(x, y) + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
        yawRad: angle + side * 0.67,
        scale: Math.max(0.42, 0.58 * geometry.scale),
        canopyClass: roundaboutAppearanceStyle.canopyClass,
      };
    });
  }).flat();

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], 0]}>
        {!hasAuthoredNetworkGround && (
          <>
            <mesh geometry={geometry.ring} renderOrder={RENDER_ORDER_FLATWORK} frustumCulled={false}>
              <primitive object={roundaboutMaterials.ring.material} attach="material" />
            </mesh>
            <mesh geometry={geometry.apron} renderOrder={RENDER_ORDER_FLATWORK} frustumCulled={false}>
              <primitive object={roundaboutMaterials.concrete.material} attach="material" />
            </mesh>
            <mesh geometry={geometry.sidewalks} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
              <primitive object={roundaboutMaterials.concrete.material} attach="material" />
            </mesh>
          </>
        )}
        <mesh geometry={geometry.island} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <primitive object={roundaboutMaterials.planting.material} attach="material" />
        </mesh>
        <mesh geometry={geometry.splitters} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <primitive object={roundaboutMaterials.concrete.material} attach="material" />
        </mesh>
        <mesh geometry={geometry.splitterPlanting} renderOrder={RENDER_ORDER_RAISED + 1} frustumCulled={false}>
          <primitive object={roundaboutMaterials.planting.material} attach="material" />
        </mesh>
        <mesh geometry={geometry.approachMarkings} renderOrder={RENDER_ORDER_DASHES + 1} frustumCulled={false}>
          <meshBasicMaterial
            color={appearance.palette.marking}
            depthTest={PUBLIC_REALM_DECAL_DEPTH.depthTest}
            depthWrite={PUBLIC_REALM_DECAL_DEPTH.depthWrite}
            side={THREE.DoubleSide}
          />
        </mesh>
        <GlobeLandscapeTreeStand
          placements={[
            { x: 0, y: 0, z: roundaboutTerrainZ(0, 0) + PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + STREET_DETAIL_3D.islandHeight_m, yawRad: 0.37, scale: 0.72 * geometry.scale, canopyClass: roundaboutAppearanceStyle.canopyClass },
            ...approachTrees,
          ]}
          renderOrder={RENDER_ORDER_FURNITURE}
        />
        <GlobeStreetLightInstances
          placements={approachLights.map((placement) => ({
            ...placement,
            fixtureStyle: roundaboutAppearanceStyle.lightStyle,
          }))}
          metalColor={appearance.palette.fixtureMetal}
          renderOrder={RENDER_ORDER_FURNITURE}
        />
        {approachSigns.map((placement, index) => (
          <group
            key={`roundabout-yield-sign-${index}`}
            position={[placement.x, placement.y, placement.z]}
            rotation={[0, 0, placement.angle + Math.PI / 2]}
          >
            <mesh
              position={[0, 0, 0.9]}
              rotation={[Math.PI / 2, 0, 0]}
              renderOrder={RENDER_ORDER_FURNITURE + 1}
            >
              <cylinderGeometry args={[0.035, 0.045, 1.8, 8]} />
              <meshStandardMaterial color={appearance.palette.fixtureMetal} metalness={0.5} roughness={0.45} />
            </mesh>
            <mesh
              position={[0, 0, 1.82]}
              rotation={[Math.PI / 2, 0, 0]}
              renderOrder={RENDER_ORDER_FURNITURE + 2}
            >
              <circleGeometry args={[0.43, 3, -Math.PI / 2]} />
              <meshStandardMaterial color="#c93434" roughness={0.65} side={THREE.DoubleSide} />
            </mesh>
          </group>
        ))}
      </group>
    </EastNorthUpFrame>
  );
}

function AccessibleFourWayIntersectionDetail({
  node,
  zones,
  fallbackTerrainHeight,
  preparedTerrain = null,
}: {
  node: FourWayStreetIntersection;
  zones: SiteZone[];
  fallbackTerrainHeight: number;
  preparedTerrain?: number | null;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(streetTerrainSampleOffset(node.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const [terrainPlane, setTerrainPlane] = useState<ReturnType<typeof fitTerrainContactPlane>>(null);
  const connectedZones = useMemo(
    () => zones.filter((zone) => node.zoneIds.includes(zone.id)),
    [node.zoneIds, zones],
  );
  const intersectionControl = useMemo(
    () => resolveFourWayIntersectionControl(connectedZones),
    [connectedZones],
  );
  const storedTerrain = useMemo(() => {
    const values = connectedZones.map(zoneStoredTerrain).filter((value): value is number => value !== null);
    return values.length > 0 ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  }, [connectedZones]);
  const appearance = STREET_APPEARANCE_KITS[node.appearanceKitId];
  const terrain = preparedTerrain ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
  const geometry = useMemo(() => {
    const result = buildAccessibleFourWayIntersectionGeometry(
      node.axisABearingRad,
      node.axisBBearingRad,
      node.axisAHalfWidthM,
      node.axisBHalfWidthM,
    );
    if (!result || !terrainPlane) return result;
    for (const item of [result.crosswalks, result.curbRamps, result.tactilePads]) {
      applyTerrainPlaneToStreetGeometry(item, terrainPlane, terrain);
    }
    return result;
  }, [node, terrain, terrainPlane]);

  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    setSampledTerrain(null);
    setTerrainPlane(null);
  }, [
    node.id,
    node.latitude,
    node.longitude,
    node.axisABearingRad,
    node.axisBBearingRad,
    node.axisAHalfWidthM,
    node.axisBHalfWidthM,
  ]);

  useFrame(() => {
    if (preparedTerrain !== null || frozenRef.current) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;
    const axisA = { x: Math.cos(node.axisABearingRad), y: Math.sin(node.axisABearingRad) };
    const axisB = { x: Math.cos(node.axisBBearingRad), y: Math.sin(node.axisBBearingRad) };
    const reachA = node.axisBHalfWidthM + 4;
    const reachB = node.axisAHalfWidthM + 4;
    const localProbes = [
      { x: 0, y: 0 },
      { x: axisA.x * reachA, y: axisA.y * reachA },
      { x: -axisA.x * reachA, y: -axisA.y * reachA },
      { x: axisB.x * reachB, y: axisB.y * reachB },
      { x: -axisB.x * reachB, y: -axisB.y * reachB },
    ];
    const mPerLon = metersPerDegLon(node.latitude);
    const samples = localProbes.map((probe) => raycastTerrainHeightAtLatLng(
      node.longitude + probe.x / mPerLon,
      node.latitude + probe.y / METERS_PER_DEG_LAT,
      tilesGroup,
      raycasterRef.current,
    ));
    const sampled = getObjectFilteredTerrainHeight(samples, storedTerrain);
    const groundCandidate = resolvePublicRealmGroundAnchor(
      sampled,
      storedTerrain,
      fallbackTerrainHeight,
      4,
    );
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
    ) {
      const contactSamples: TerrainContactSample[] = localProbes.flatMap((probe, index) => (
        isPlausibleTerrainAnchor(samples[index], groundCandidate)
          ? [{ ...probe, z: samples[index] as number }]
          : []
      ));
      setTerrainPlane(fitTerrainContactPlane(contactSamples, {
        fallbackElevationMeters: groundCandidate,
        outlierToleranceMeters: 1.5,
      }));
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  useEffect(() => {
    if (!geometry) return undefined;
    return retainResourceForDeferredDisposal(geometry, (ownedGeometry) => {
      ownedGeometry.crosswalks.dispose();
      ownedGeometry.curbRamps.dispose();
      ownedGeometry.tactilePads.dispose();
    });
  }, [geometry]);

  if (!geometry) return null;
  return (
    <EastNorthUpFrame
      lat={node.latitude * DEG_TO_RAD}
      lon={node.longitude * DEG_TO_RAD}
      height={terrain}
    >
      <mesh geometry={geometry.crosswalks} renderOrder={RENDER_ORDER_DASHES + 2} frustumCulled={false}>
        <meshStandardMaterial
          color={appearance.palette.marking}
          roughness={0.78}
          metalness={0}
          depthTest={PUBLIC_REALM_DECAL_DEPTH.depthTest}
          depthWrite={PUBLIC_REALM_DECAL_DEPTH.depthWrite}
          polygonOffset
          polygonOffsetFactor={-5}
          polygonOffsetUnits={-10}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh geometry={geometry.curbRamps} renderOrder={RENDER_ORDER_RAISED + 1} frustumCulled={false}>
        <meshStandardMaterial color={appearance.palette.sidewalk} roughness={0.94} metalness={0} />
      </mesh>
      <mesh geometry={geometry.tactilePads} renderOrder={RENDER_ORDER_RAISED + 2} frustumCulled={false}>
        <meshStandardMaterial color={appearance.palette.tactile} roughness={0.82} metalness={0} />
      </mesh>
      {intersectionControl === 'traffic_signal' ? (
        <GlobeIntersectionSignalInstances
          node={node}
          metalColor={appearance.palette.fixtureMetal}
          renderOrder={RENDER_ORDER_FURNITURE}
          terrainPlane={terrainPlane}
          frameElevation={terrain}
        />
      ) : null}
    </EastNorthUpFrame>
  );
}

export function GlobeStreetDetailLayer({
  zones,
  terrainHeight,
}: {
  zones: SiteZone[];
  terrainHeight: number;
}) {
  const roadZones = useMemo(
    () => zones.filter((z) =>
      resolveCommunity3DKind(z) === 'street'
      && z.coordinates.length >= 4
      && shouldRenderCommunityGround(z)),
    [zones],
  );
  const detailedRoadZones = useMemo(
    () => selectDetailedStreetZones(roadZones),
    [roadZones],
  );
  const intersectionNodes = useMemo(
    () => detectFourWayStreetIntersections(detailedRoadZones),
    [detailedRoadZones],
  );
  const furnitureStreetIds = useMemo(
    () => selectFurnishedStreetIds(detailedRoadZones),
    [detailedRoadZones],
  );
  const treeStreetIds = useMemo(
    () => selectTreeStreetIds(detailedRoadZones),
    [detailedRoadZones],
  );
  return (
    <>
      {detailedRoadZones.map((zone) => (
        <group
          key={zone.id}
          name={`siteforge-direct3d-street-${zone.id}`}
          userData={direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, 'street'))}
        >
          {isRoundaboutZone(zone) ? (
            <RoundaboutDetail key={`${zone.id}:${resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}`} zone={zone} fallbackTerrainHeight={terrainHeight} preparedTerrain={resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)} />
          ) : (
            <StreetRibbonDetail
              key={`${zone.id}:${resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}`}
              zone={zone}
              fallbackTerrainHeight={terrainHeight}
              preparedTerrain={resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}
              intersectionNodes={intersectionNodes}
              renderFamilyFurniture={furnitureStreetIds.has(zone.id)}
              renderFamilyTrees={treeStreetIds.has(zone.id)}
            />
          )}
        </group>
      ))}
      {intersectionNodes.map((node) => (
        <group
          key={node.id}
          name={`siteforge-direct3d-junction-${node.id}`}
          userData={direct3DInstanceUserData(
            direct3DStreetJunctionInstanceDescriptor(node.zoneIds),
          )}
        >
          <AccessibleFourWayIntersectionDetail
            key={`${node.id}:${node.zoneIds.map((id) => resolvePreparedSiteTerrainForZone(zones.find((zone) => zone.id === id), zones, terrainHeight)).join(':')}`}
            node={node}
            zones={detailedRoadZones}
            fallbackTerrainHeight={terrainHeight}
            preparedTerrain={node.zoneIds.every((id) => resolvePreparedSiteTerrainForZone(zones.find((zone) => zone.id === id), zones, terrainHeight) !== null)
              ? resolvePreparedSiteTerrainForZone(zones.find((zone) => zone.id === node.zoneIds[0]), zones, terrainHeight)
              : null}
          />
        </group>
      ))}
    </>
  );
}
