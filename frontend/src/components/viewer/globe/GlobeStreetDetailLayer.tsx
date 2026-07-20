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
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import { computeFootprintFrame } from './buildingPlacement';
import {
  buildCurbBandGeometry,
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
  streetTerrainSampleOffset,
} from './streetDetailLod';

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
function isRoundaboutZone(zone: SiteZone): boolean {
  const id = String((zone.properties as Record<string, unknown> | undefined)?.road_archetype_id ?? '');
  return id.toLowerCase().replace(/-/g, '_').includes('roundabout');
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
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
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
    const resolvedHalfWidth = effectiveRoadWidth(zone.properties) / 2;
    return {
      centerLngLat: { local: densified, lngLat: back },
      centroid: { lng, lat },
      halfWidth: resolvedHalfWidth,
      sectionScale: sectionProfile ? (resolvedHalfWidth * 2) / sectionProfile.rowM : 1,
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
      const groundCandidate = preferLowerGroundAnchor(filtered, storedTerrain);
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
          )
          : null)
        : buildCurbBandGeometry(centerLngLat.local, halfWidth, STREET_DETAIL_3D, zs),
      dashes: sectionProfile ? null : buildDashGeometry(centerLngLat.local, STREET_DETAIL_3D, zs),
      bands,
      markings,
    };
  }, [centerLngLat, halfWidth, sectionProfile, sectionScale, stationZ]);

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
          <meshBasicMaterial
            color={band.color}
            depthTest
            depthWrite={false}
            polygonOffset
            polygonOffsetFactor={-3}
            polygonOffsetUnits={-6}
            side={THREE.DoubleSide}
          />
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
            depthTest
            depthWrite={false}
            polygonOffset
            polygonOffsetFactor={-4}
            polygonOffsetUnits={-8}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
      {geometries.curbs && (
        <mesh geometry={geometries.curbs} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshLambertMaterial color={CURB_COLOR} polygonOffset polygonOffsetFactor={-2} polygonOffsetUnits={-4} />
        </mesh>
      )}
      {geometries.dashes && (
        <mesh geometry={geometries.dashes} renderOrder={RENDER_ORDER_DASHES} frustumCulled={false}>
          <meshBasicMaterial
            color={DASH_COLOR}
            depthTest
            depthWrite={false}
            polygonOffset
            polygonOffsetFactor={-4}
            polygonOffsetUnits={-8}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
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
    const groundCandidate = preferLowerGroundAnchor(filtered, storedTerrain);
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
          <meshBasicMaterial color={ASPHALT_COLOR} depthTest={false} side={THREE.DoubleSide} />
        </mesh>
        <mesh geometry={geometry.apron} renderOrder={RENDER_ORDER_FLATWORK} frustumCulled={false}>
          <meshBasicMaterial color={CONCRETE_COLOR} depthTest={false} side={THREE.DoubleSide} />
        </mesh>
        <mesh geometry={geometry.island} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshLambertMaterial color={ISLAND_COLOR} />
        </mesh>
        <mesh geometry={geometry.splitters} renderOrder={RENDER_ORDER_RAISED} frustumCulled={false}>
          <meshLambertMaterial color={ISLAND_COLOR} />
        </mesh>
      </group>
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
          />
        ),
      )}
    </>
  );
}
