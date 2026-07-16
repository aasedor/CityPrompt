/**
 * GlobeBuildingModelsLayer — places generated Meshy .glb building models on
 * the 3D tiles globe, seated on terrain, oriented to their parcel.
 *
 * Each building with a model_url and a resolvable footprint gets a GLB
 * wrapped in an EastNorthUpFrame at the footprint's oriented-rect center:
 * recentered (base at ground), swizzled Y-up -> Z-up, contain-fit scaled to
 * the parcel, yawed to the footprint's long axis + rotation_degrees.
 *
 * The zone layer's purple prism doubles as the loading/error fallback: a
 * building's prism is suppressed (via onLoadedIdsChange) only once its GLB
 * has actually mounted, so a 404 or slow network never leaves a hole.
 */

import {
  Component,
  Suspense,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { Building, SiteZone } from '@/types';
import { resolveApiFileUrl } from '@/services/api';
import { computeFootprintFrame, computeModelPlacement } from './buildingPlacement';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { getObjectFilteredTerrainHeight, isPlausibleTerrainAnchor, resolveZoneTerrainHeight } from './globeTerrainUtils';
import { disposeArchitecturalCloneMaterials, prepareArchitecturalClone } from './modelMaterialQuality';

const DEG_TO_RAD = Math.PI / 180;
const MAX_PLACED_MODELS = 20;
const GROUND_EMBED_METERS = 0.3;
// Above depthTest-false road overlays (120), below zone prisms (200).
const MODEL_RENDER_ORDER = 150;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;

interface GlobeBuildingModelsLayerProps {
  buildings: Building[];
  zones: SiteZone[];
  /** Site-level elevation fallback (from the map's elevation fetch). */
  terrainHeight: number;
  /** Buildings whose GLB is actually mounted — drives prism suppression. */
  onLoadedIdsChange: (ids: Set<string>) => void;
}

/** useGLTF throws on bad/missing models; Suspense doesn't catch errors.
 *  Fallback is null so the zone prism simply stays visible. */
class SilentModelBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    console.warn('[GlobeModels] model failed to load', error);
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

function footprintRingFor(building: Building, zones: SiteZone[]): number[][] | null {
  if (building.footprint_coordinates && building.footprint_coordinates.length >= 3) {
    return building.footprint_coordinates;
  }
  const zone = zones.find((z) => z.building_id === building.id);
  return zone && zone.coordinates.length >= 3 ? zone.coordinates : null;
}

function zoneFor(building: Building, zones: SiteZone[]): SiteZone | undefined {
  return zones.find((z) => z.building_id === building.id);
}

function BuildingModelInstance({
  building,
  zone,
  ring,
  fallbackTerrainHeight,
  onLoaded,
  onUnloaded,
}: {
  building: Building;
  zone: SiteZone | undefined;
  ring: number[][];
  fallbackTerrainHeight: number;
  onLoaded: (id: string) => void;
  onUnloaded: (id: string) => void;
}) {
  const url = resolveApiFileUrl(building.lod_urls?.['0'] ?? building.model_url ?? '');
  const { scene } = useGLTF(url);
  const tiles = useContext(TilesRendererContext);
  const maxAnisotropy = useThree((state) => state.gl.capabilities.getMaxAnisotropy());

  const frame = useMemo(() => computeFootprintFrame(ring), [ring]);

  // Bbox once per cached scene (drei caches per URL; clones share buffers).
  const bbox = useMemo(() => new THREE.Box3().setFromObject(scene), [scene]);
  const size = useMemo(() => bbox.getSize(new THREE.Vector3()), [bbox]);
  const center = useMemo(() => bbox.getCenter(new THREE.Vector3()), [bbox]);

  const cloned = useMemo(() => {
    return prepareArchitecturalClone(scene, {
      renderOrder: MODEL_RENDER_ORDER,
      maxAnisotropy,
      restyleUntextured: true,
    });
  }, [maxAnisotropy, scene]);
  useEffect(() => () => disposeArchitecturalCloneMaterials(cloned), [cloned]);

  const placement = useMemo(
    () => (frame
      ? computeModelPlacement(frame, size, building.height_meters, building.rotation_degrees)
      : null),
    [frame, size, building.height_meters, building.rotation_degrees],
  );

  useEffect(() => {
    if (placement?.heightWarning) {
      console.warn(
        '[GlobeModels] scaled model height misses height_meters by >40%',
        building.id, { scaled: placement.scale * size.y, target: building.height_meters },
      );
    }
  }, [placement, building.id, building.height_meters, size]);

  // Prism suppression: only while this GLB is actually mounted.
  useEffect(() => {
    onLoaded(building.id);
    return () => onUnloaded(building.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [building.id]);

  // Terrain seating: stored zone elevation first (consistent with the prism it
  // replaces, and immune to the leftover-photogrammetry-roof trap), then
  // lower-quartile raycast probes (drape-and-freeze), then the site fallback.
  const zoneProps = zone?.properties as Record<string, unknown> | undefined;
  const storedRaw = Number(zoneProps?.terrain_elevation_m ?? zoneProps?.terrain_height);
  const storedTerrain = Number.isFinite(storedRaw) ? storedRaw : null;
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(0);
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);

  useFrame(() => {
    if (frozenRef.current || storedTerrain !== null || !frame) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const step = Math.max(1, Math.floor(ring.length / 4));
    const probes: Array<[number, number]> = [[frame.centroidLng, frame.centroidLat]];
    for (let i = 0; i < ring.length && probes.length < 5; i += step) {
      probes.push([ring[i][0], ring[i][1]]);
    }
    const samples = probes.map(([lng, lat]) => (
      raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current)
    ));
    const filtered = getObjectFilteredTerrainHeight(samples, null);
    // Gate against the unrefined-root-tile trap: the first finite sample can
    // land ~29km below the true surface and would sink the model with it
    // (see isPlausibleTerrainAnchor). Implausible samples burn an attempt
    // and retry next interval.
    if (filtered !== null && isPlausibleTerrainAnchor(filtered, fallbackTerrainHeight)) {
      setSampledTerrain(filtered);
      frozenRef.current = true;
    }
  });

  if (!frame || !placement) return null;

  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group
        position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], -GROUND_EMBED_METERS]}
        rotation={[0, 0, placement.yawRad]}
      >
        {/* Rx(+90°): glTF Y-up -> ENU Z-up (model Y becomes Up, Z becomes -North) */}
        <group rotation={[Math.PI / 2, 0, 0]} scale={placement.scale}>
          {/* Recenter in model space: bbox XZ center to origin, bbox MIN Y to
              ground — the base sits on terrain, not the vertical midpoint. */}
          <group position={[-center.x, -bbox.min.y, -center.z]}>
            <primitive object={cloned} />
          </group>
        </group>
      </group>
    </EastNorthUpFrame>
  );
}

export function GlobeBuildingModelsLayer({
  buildings,
  zones,
  terrainHeight,
  onLoadedIdsChange,
}: GlobeBuildingModelsLayerProps) {
  const [loadedIds, setLoadedIds] = useState<Set<string>>(() => new Set());

  const placeable = useMemo(() => (
    buildings
      .filter((b) => (b.lod_urls?.['0'] ?? b.model_url) && footprintRingFor(b, zones))
      .sort((a, b) => (a.created_at ?? '').localeCompare(b.created_at ?? '') || a.id.localeCompare(b.id))
      .slice(0, MAX_PLACED_MODELS)
  ), [buildings, zones]);

  useEffect(() => {
    onLoadedIdsChange(loadedIds);
  }, [loadedIds, onLoadedIdsChange]);

  // Clear suppression for everything when the layer unmounts (toggle off).
  useEffect(() => () => onLoadedIdsChange(new Set()), [onLoadedIdsChange]);

  const handleLoaded = (id: string) => setLoadedIds((prev) => {
    if (prev.has(id)) return prev;
    const next = new Set(prev);
    next.add(id);
    return next;
  });
  const handleUnloaded = (id: string) => setLoadedIds((prev) => {
    if (!prev.has(id)) return prev;
    const next = new Set(prev);
    next.delete(id);
    return next;
  });

  return (
    <>
      {placeable.map((building) => {
        const ring = footprintRingFor(building, zones);
        if (!ring) return null;
        return (
          <SilentModelBoundary key={building.id}>
            <Suspense fallback={null}>
              <BuildingModelInstance
                building={building}
                zone={zoneFor(building, zones)}
                ring={ring}
                fallbackTerrainHeight={terrainHeight}
                onLoaded={handleLoaded}
                onUnloaded={handleUnloaded}
              />
            </Suspense>
          </SilentModelBoundary>
        );
      })}
    </>
  );
}
