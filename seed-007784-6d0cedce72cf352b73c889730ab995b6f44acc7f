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
import { extractCenterline, effectiveRoadWidth } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import {
  getObjectFilteredTerrainHeight,
  isPlausibleTerrainAnchor,
  preferLowerGroundAnchor,
  resolvePublicRealmGroundAnchor,
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import { computeFootprintFrame } from './buildingPlacement';
import {
  buildCurbBandGeometry,
  buildAccessibleFourWayIntersectionGeometry,
  buildDashGeometry,
  buildOffsetCurbGeometry,
  buildRibbonBandGeometry,
  buildRoundaboutGeometry,
  densifyPolyline,
  type LocalPt,
} from './streetMesh3D';
import { STREET_DETAIL_3D } from '@/data/streetGeometryParams';
import {
  resolvePilotStreetSectionProfile,
} from './streetSectionProfiles';
import {
  selectDetailedStreetZones,
  selectTreeStreetIds,
  streetTerrainSampleOffset,
} from './streetDetailLod';
import {
  PUBLIC_REALM_DECAL_DEPTH,
  PUBLIC_REALM_DETAIL_DEPTH,
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
import { validateStreetRecipeProperties } from './streetLegoContract';
import { buildStreetFamilyFixturePlacements } from './streetFamilyFurniture';
import { GlobeStreetLightInstances } from './GlobeStreetLightInstances';

const DEG_TO_RAD = Math.PI / 180;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
const STATIONS_PER_BATCH = 12;
// Re-sample stations that missed (tile not yet streamed) up to this many
// passes before freezing — early rays against coarse LOD tiles miss a lot.
const MAX_SAMPLE_PASSES = 3;

const CURB_COLOR = '#9aa0a6';
const DASH_COLOR = '#e0e2e4';
const ASPHALT_COLOR = '#76787a';
const CONCRETE_COLOR = '#c7cbce';
const ISLAND_COLOR = '#96b08a';

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
  intersectionNodes,
  renderFamilyFurniture,
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
  intersectionNodes: FourWayStreetIntersection[];
  renderFamilyFurniture: boolean;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  // Across a district plan, distribute terrain rays over the full sampling
  // interval instead of making every street probe the tiles on one frame.
  const frameCountRef = useRef(streetTerrainSampleOffset(zone.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const nextStationRef = useRef(0);
  const stationZRef = useRef<number[] | null>(null);
  const frozenRef = useRef(false);
  const [stationZ, setStationZ] = useState<number[] | null>(null);
  const sectionProfile = useMemo(
    () => resolvePilotStreetSectionProfile(zone),
    [zone.properties],
  );

  // Centerline in lng/lat, densified so stations follow terrain.
  const { centerLngLat, centroid, halfWidth, sectionScale } = useMemo(() => {
    const center = extractCenterline(zone.coordinates);
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
    const back = densified.map((p) => [
      lng + p.x / mPerLon,
      lat + p.y / METERS_PER_DEG_LAT,
    ]);
    const resolvedHalfWidth = sectionProfile?.metricWidthLocked
      ? (sectionProfile.targetRowM ?? sectionProfile.rowM) / 2
      : effectiveRoadWidth(zone.properties) / 2;
    return {
      centerLngLat: { local: densified, lngLat: back },
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
  const frameElevation = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  // Geometry edits (vertex drag commits, re-buffering) change coordinates
  // under the SAME zone id — the frozen drape state must restart or curbs
  // keep the old location's elevations.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    nextStationRef.current = 0;
    passRef.current = 0;
    stationZRef.current = null;
    hitFlagsRef.current = null;
    setStationZ(null);
    setSampledTerrain(null);
  }, [centerLngLat]);

  // Drape-and-freeze: first resolve the frame anchor, then batch-sample
  // per-station elevations relative to it. Batches are interval-gated too —
  // consecutive-frame sampling right after mount rays against coarse LOD
  // tiles and bakes garbage; missed stations get re-sampled across passes.
  useFrame(() => {
    if (frozenRef.current || !centerLngLat) return;
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
    if (!stationZRef.current || stationZRef.current.length !== n) {
      stationZRef.current = new Array<number>(n).fill(0);
      hitFlagsRef.current = new Array<boolean>(n).fill(false);
      nextStationRef.current = 0;
      passRef.current = 0;
    }
    const zs = stationZRef.current;
    const hits = hitFlagsRef.current!;
    let i = nextStationRef.current;
    let processed = 0;
    while (i < n && processed < STATIONS_PER_BATCH) {
      if (!hits[i]) {
        const [lng, lat] = centerLngLat.lngLat[i];
        const sampled = raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current);
        const groundCandidate = preferLowerGroundAnchor(sampled, anchor, 4);
        if (
          groundCandidate !== null
          && isPlausibleTerrainAnchor(groundCandidate, anchor)
        ) {
          zs[i] = groundCandidate - anchor;
          hits[i] = true;
        }
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
      frozenRef.current = true;
      setStationZ(zs.slice());
    }
  });

  const geometries = useMemo(() => {
    if (!centerLngLat) return null;
    const zs = stationZ ?? undefined;
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
                dashLift_m: 0.17,
              },
              zs,
              marking.offsetM * sectionScale,
            )
            : buildRibbonBandGeometry(
              centerLngLat.local,
              (marking.offsetM - marking.widthM / 2) * sectionScale,
              (marking.offsetM + marking.widthM / 2) * sectionScale,
              0.17,
              zs,
            ),
        }))
        .filter((item): item is typeof item & { geometry: THREE.BufferGeometry } => Boolean(item.geometry))
      : [];
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
    };
  }, [centerLngLat, centroid, halfWidth, intersectionNodes, sectionProfile, sectionScale, stationZ, zone.id]);

  const woonerfPlanters = useMemo(() => {
    if (!centerLngLat || !sectionProfile?.archetypeId.includes('woonerf')) return [];
    const points = centerLngLat.local;
    const placements: Array<{
      x: number;
      y: number;
      centerX: number;
      centerY: number;
      z: number;
      rotation: number;
    }> = [];
    // Alternate traffic-calming planters along the flush shared surface. Keep
    // the first and last stations clear so the connection reads as an entry.
    for (let index = 2; index < points.length - 2; index += 3) {
      const previous = points[index - 1];
      const next = points[index + 1];
      const dx = next.x - previous.x;
      const dy = next.y - previous.y;
      const length = Math.hypot(dx, dy) || 1;
      const normalX = -dy / length;
      const normalY = dx / length;
      const side = placements.length % 2 === 0 ? -1 : 1;
      const offset = Math.max(0.8, halfWidth * 0.72) * side;
      placements.push({
        x: points[index].x + normalX * offset,
        y: points[index].y + normalY * offset,
        centerX: points[index].x,
        centerY: points[index].y,
        z: stationZ?.[index] ?? 0,
        rotation: Math.atan2(dy, dx),
      });
    }
    return placements;
  }, [centerLngLat, halfWidth, sectionProfile, stationZ]);

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
      stationZ,
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
    stationZ,
    zone.id,
  ]);

  // r3f does not dispose geometry props — without this every drape freeze,
  // edit commit, and zone delete leaks the previous buffers.
  useEffect(
    () => () => {
      geometries?.curbs?.dispose();
      geometries?.dashes?.dispose();
      geometries?.bands.forEach((item) => item.geometry.dispose());
      geometries?.markings.forEach((item) => item.geometry.dispose());
    },
    [geometries],
  );

  if (!centerLngLat || !centroid || !geometries) return null;

  return (
    <EastNorthUpFrame
      lat={centroid.lat * DEG_TO_RAD}
      lon={centroid.lng * DEG_TO_RAD}
      height={frameElevation}
    >
      {geometries.bands.map(({ band, geometry }) => (
        <mesh
          key={`${band.sourceType}-${band.startM}`}
          geometry={geometry}
          renderOrder={RENDER_ORDER_FLATWORK}
          frustumCulled={false}
        >
          {sectionProfile?.familyId ? (
            <meshStandardMaterial
              color={band.color}
              roughness={band.roughness ?? 0.9}
              metalness={band.metalness ?? 0.02}
              depthTest={PUBLIC_REALM_DETAIL_DEPTH.depthTest}
              depthWrite={PUBLIC_REALM_DETAIL_DEPTH.depthWrite}
              polygonOffset
              polygonOffsetFactor={-3}
              polygonOffsetUnits={-6}
              side={THREE.DoubleSide}
            />
          ) : (
            <meshBasicMaterial
              color={band.color}
              depthTest={PUBLIC_REALM_DETAIL_DEPTH.depthTest}
              depthWrite={PUBLIC_REALM_DETAIL_DEPTH.depthWrite}
              polygonOffset
              polygonOffsetFactor={-3}
              polygonOffsetUnits={-6}
              side={THREE.DoubleSide}
            />
          )}
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
      <GlobeLandscapeTreeStand placements={familyFixtures.trees} renderOrder={RENDER_ORDER_FURNITURE} />
      <GlobeLandscapeBenchStand placements={familyFixtures.benches} renderOrder={RENDER_ORDER_FURNITURE} />
      <GlobeStreetLightInstances
        placements={familyFixtures.lights}
        metalColor={sectionProfile?.appearance?.palette.fixtureMetal ?? '#30383a'}
        renderOrder={RENDER_ORDER_FURNITURE}
      />
      {woonerfPlanters.map((placement, index) => (
        <group key={`woonerf-planter-${index}`}>
          <mesh
            position={[placement.centerX, placement.centerY, placement.z + 0.17]}
            rotation={[0, 0, placement.rotation]}
            renderOrder={RENDER_ORDER_FURNITURE}
          >
            <boxGeometry args={[0.55, halfWidth * 1.55, 0.06]} />
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
              <mesh key={bollardX} position={[bollardX, 0, 0.42]} renderOrder={RENDER_ORDER_FURNITURE}>
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
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(streetTerrainSampleOffset(zone.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const sectionProfile = useMemo(
    () => resolvePilotStreetSectionProfile(zone),
    [zone.properties],
  );
  const appearance = sectionProfile?.appearance
    ?? STREET_APPEARANCE_KITS.classic_tree_lined_v1;

  const frame = useMemo(() => computeFootprintFrame(zone.coordinates), [zone.coordinates]);
  const geometry = useMemo(() => {
    if (!frame) return null;
    const inscribed = Math.min(frame.longDim, frame.shortDim) / 2;
    return buildRoundaboutGeometry(inscribed, frame.bearingRad);
  }, [frame]);

  useEffect(
    () => () => {
      if (!geometry) return;
      geometry.ring.dispose();
      geometry.apron.dispose();
      geometry.island.dispose();
      geometry.splitters.dispose();
    },
    [geometry],
  );

  // Zone moved/reshaped under the same id — resample the anchor.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    setSampledTerrain(null);
  }, [frame]);

  const storedTerrain = zoneStoredTerrain(zone);

  useFrame(() => {
    if (frozenRef.current || !frame) return;
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
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  if (!frame || !geometry) return null;
  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], 0]}>
        <mesh geometry={geometry.ring} renderOrder={RENDER_ORDER_FLATWORK} frustumCulled={false}>
          <meshStandardMaterial
            color={appearance.palette.motor ?? ASPHALT_COLOR}
            roughness={appearance.palette.roughness}
            metalness={appearance.palette.metalness}
            depthTest={PUBLIC_REALM_DETAIL_DEPTH.depthTest}
            depthWrite={PUBLIC_REALM_DETAIL_DEPTH.depthWrite}
            side={THREE.DoubleSide}
          />
        </mesh>
        <mesh geometry={geometry.apron} renderOrder={RENDER_ORDER_FLATWORK} frustumCulled={false}>
          <meshStandardMaterial
            color={appearance.palette.sidewalk ?? CONCRETE_COLOR}
            roughness={0.94}
            metalness={0}
            depthTest={PUBLIC_REALM_DETAIL_DEPTH.depthTest}
            depthWrite={PUBLIC_REALM_DETAIL_DEPTH.depthWrite}
            side={THREE.DoubleSide}
          />
        </mesh>
        <mesh geometry={geometry.island} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshStandardMaterial color={appearance.palette.planting ?? ISLAND_COLOR} roughness={0.98} metalness={0} />
        </mesh>
        <mesh geometry={geometry.splitters} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshStandardMaterial color={appearance.palette.planting ?? ISLAND_COLOR} roughness={0.98} metalness={0} />
        </mesh>
        <GlobeLandscapeTreeStand
          placements={[
            { x: 0, y: 0, z: STREET_DETAIL_3D.islandHeight_m, yawRad: 0.37, scale: 0.62 * geometry.scale },
            { x: 1.8 * geometry.scale, y: -1.1 * geometry.scale, z: STREET_DETAIL_3D.islandHeight_m, yawRad: 1.81, scale: 0.52 * geometry.scale },
            { x: -1.5 * geometry.scale, y: 1.25 * geometry.scale, z: STREET_DETAIL_3D.islandHeight_m, yawRad: 3.29, scale: 0.55 * geometry.scale },
          ]}
          renderOrder={RENDER_ORDER_FURNITURE}
        />
      </group>
    </EastNorthUpFrame>
  );
}

function AccessibleFourWayIntersectionDetail({
  node,
  zones,
  fallbackTerrainHeight,
}: {
  node: FourWayStreetIntersection;
  zones: SiteZone[];
  fallbackTerrainHeight: number;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(streetTerrainSampleOffset(node.id, TERRAIN_SAMPLE_FRAME_INTERVAL));
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const connectedZones = useMemo(
    () => zones.filter((zone) => node.zoneIds.includes(zone.id)),
    [node.zoneIds, zones],
  );
  const storedTerrain = useMemo(() => {
    const values = connectedZones.map(zoneStoredTerrain).filter((value): value is number => value !== null);
    return values.length > 0 ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  }, [connectedZones]);
  const appearance = STREET_APPEARANCE_KITS[node.appearanceKitId];
  const geometry = useMemo(() => buildAccessibleFourWayIntersectionGeometry(
    node.axisABearingRad,
    node.axisBBearingRad,
    node.axisAHalfWidthM,
    node.axisBHalfWidthM,
  ), [node]);

  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    setSampledTerrain(null);
  }, [node.id, node.latitude, node.longitude]);

  useFrame(() => {
    if (frozenRef.current) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;
    const sampled = raycastTerrainHeightAtLatLng(
      node.longitude,
      node.latitude,
      tilesGroup,
      raycasterRef.current,
    );
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
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  useEffect(() => () => {
    geometry?.crosswalks.dispose();
    geometry?.curbRamps.dispose();
    geometry?.tactilePads.dispose();
  }, [geometry]);

  if (!geometry) return null;
  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
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
    () => selectTreeStreetIds(detailedRoadZones),
    [detailedRoadZones],
  );
  return (
    <>
      {detailedRoadZones.map((zone) =>
        isRoundaboutZone(zone) ? (
          <RoundaboutDetail key={zone.id} zone={zone} fallbackTerrainHeight={terrainHeight} />
        ) : (
          <StreetRibbonDetail
            key={zone.id}
            zone={zone}
            fallbackTerrainHeight={terrainHeight}
            intersectionNodes={intersectionNodes}
            renderFamilyFurniture={furnitureStreetIds.has(zone.id)}
          />
        ),
      )}
      {intersectionNodes.map((node) => (
        <AccessibleFourWayIntersectionDetail
          key={node.id}
          node={node}
          zones={detailedRoadZones}
          fallbackTerrainHeight={terrainHeight}
        />
      ))}
    </>
  );
}
