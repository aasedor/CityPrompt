/**
 * GlobeBuildingModelsLayer — places generated Meshy .glb building models on
 * the 3D tiles globe, seated on terrain, oriented to their parcel.
 *
 * Each building with a model_url and a resolvable footprint gets a GLB
 * wrapped in an EastNorthUpFrame at the footprint's oriented-rect center:
 * recentered (base at ground), swizzled Y-up -> Z-up, contain-fit scaled to
 * the parcel, yawed to the footprint's long axis + rotation_degrees.
 *
 * The camera-nearest generated buildings use their complete GLBs. Every
 * remaining building, plus any detailed GLB that is loading or fails, uses a
 * terrain-seated exact-footprint massing mesh. The zone prism is suppressed
 * only once one of those 3D representations has actually mounted.
 */

import {
  Component,
  Suspense,
  useCallback,
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
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { Building, SiteZone } from '@/types';
import { resolveApiFileUrl } from '@/services/api';
import { createKtx2LoaderExtension } from '@/lib/ktx2GltfLoader';
import { computeFootprintFrame, computeModelPlacement, type FootprintFrame } from './buildingPlacement';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import {
  getObjectFilteredTerrainHeight,
  isPlausibleTerrainAnchor,
  preferLowerGroundAnchor,
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import {
  disposeArchitecturalCloneMaterials,
  prepareArchitecturalClone,
  resolveArchitecturalGlazingLod,
  setArchitecturalGlazingLod,
  type ArchitecturalGlazingLod,
} from './modelMaterialQuality';
import { buildLegoMassingMeshData, legoMassingColor } from './legoMassingGeometry';
import {
  GENERATED_BUILDING_DETAIL_BUDGET,
  partitionGeneratedBuildingLod,
} from './generatedBuildingLod';
import { modelAssetAvailable } from './modelAssetAvailability';
import { LocalModelSelectionOutline } from './GlobeModelSelectionOutline';
import {
  DIRECT_3D_CAPTURE_CONTEXT_USER_DATA,
  direct3DInstanceUserData,
  direct3DZoneInstanceDescriptor,
} from './direct3dCapture';

const DEG_TO_RAD = Math.PI / 180;
// Above depthTest-false road overlays (120), below zone prisms (200).
const MODEL_RENDER_ORDER = 150;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
const MASSING_TERRAIN_SAMPLE_FRAME_INTERVAL = 300;
const MASSING_TERRAIN_SAMPLE_MAX_ATTEMPTS = 8;
const generatedTerrainSampleCache = new Map<string, number>();

function direct3DBuildingInstanceUserData(
  building: Building,
  zone: SiteZone | undefined,
): Record<string, unknown> {
  return direct3DInstanceUserData(zone
    ? direct3DZoneInstanceDescriptor(zone.id, 'building', { building_id: building.id })
    : {
      instance_id: `building:${building.id}:building`,
      semantic_class: 'building',
      building_id: building.id,
    });
}

interface GlobeBuildingModelsLayerProps {
  buildings: Building[];
  zones: SiteZone[];
  /** Exact server-claimed buildings editable by Direct 3D. */
  direct3DProposalBuildingIds?: ReadonlySet<string>;
  /** Site-level elevation fallback (from the map's elevation fetch). */
  terrainHeight: number;
  /** Authoritative prepared-site datum; overrides legacy per-zone elevations. */
  preparedSiteTerrainHeight?: number | null;
  /** Buildings whose detailed or massing representation is mounted. */
  onLoadedIdsChange: (ids: Set<string>) => void;
  selectedBuildingId?: string | null;
  onBuildingClick?: (buildingId: string) => void;
}

/** useGLTF throws on bad/missing models; Suspense doesn't catch errors. */
class SilentModelBoundary extends Component<{
  children: ReactNode;
  fallback?: ReactNode;
}, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    console.warn('[GlobeModels] model failed to load', error);
  }
  render() {
    return this.state.failed ? (this.props.fallback ?? null) : this.props.children;
  }
}

function setsEqual(a: ReadonlySet<string>, b: ReadonlySet<string>): boolean {
  return a.size === b.size && [...a].every((value) => b.has(value));
}

function stableFrameOffset(id: string, modulo: number): number {
  let hash = 0;
  for (let index = 0; index < id.length; index += 1) {
    hash = (Math.imul(hash, 31) + id.charCodeAt(index)) | 0;
  }
  return Math.abs(hash) % modulo;
}

function BuildingModelInstance({
  building,
  zone,
  ring,
  frame,
  fallbackTerrainHeight,
  preparedSiteTerrainHeight,
  onLoaded,
  onUnloaded,
  selected,
  proposalForDirect3D,
  onBuildingClick,
}: {
  building: Building;
  zone: SiteZone | undefined;
  ring: number[][];
  frame: FootprintFrame;
  fallbackTerrainHeight: number;
  preparedSiteTerrainHeight?: number | null;
  onLoaded: (id: string) => void;
  onUnloaded: (id: string) => void;
  selected: boolean;
  proposalForDirect3D: boolean;
  onBuildingClick?: (buildingId: string) => void;
}) {
  const url = resolveApiFileUrl(building.lod_urls?.['0'] ?? building.model_url ?? '');
  const gl = useThree((state) => state.gl);
  const extendLoader = useMemo(() => createKtx2LoaderExtension(gl), [gl]);
  const { scene } = useGLTF(url, true, true, extendLoader);
  const tiles = useContext(TilesRendererContext);
  const maxAnisotropy = gl.capabilities.getMaxAnisotropy();

  // Bbox once per cached scene (drei caches per URL; clones share buffers).
  const bbox = useMemo(() => new THREE.Box3().setFromObject(scene), [scene]);
  const size = useMemo(() => bbox.getSize(new THREE.Vector3()), [bbox]);
  const center = useMemo(() => bbox.getCenter(new THREE.Vector3()), [bbox]);
  const preserveSourceMaterials = building.generation_engine?.toLowerCase() === 'rlasm';

  const cloned = useMemo(() => {
    return prepareArchitecturalClone(scene, {
      renderOrder: MODEL_RENDER_ORDER,
      maxAnisotropy,
      // RLASM keepers carry source-locked material roles even when a finish is
      // represented by PBR colour rather than a bitmap. Preserve the complete
      // authored material state; globe lighting may illuminate it, but must
      // not reinterpret its maps, finish values, glass, alpha, or visibility.
      preserveSourcePbr: preserveSourceMaterials,
      restyleUntextured: !preserveSourceMaterials,
    });
  }, [maxAnisotropy, preserveSourceMaterials, scene]);
  useEffect(() => () => disposeArchitecturalCloneMaterials(cloned), [cloned]);

  const placement = useMemo(
    () => computeModelPlacement(frame, size, building.height_meters, building.rotation_degrees),
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
    if (!placement) return undefined;
    onLoaded(building.id);
    return () => onUnloaded(building.id);
  }, [building.id, onLoaded, onUnloaded, placement]);

  // Terrain seating: reconcile a stored elevation with lower-quartile tile
  // probes and take the lower material surface (ground beats a legacy roof
  // click), then freeze. The site height remains the loading fallback.
  const zoneProps = zone?.properties as Record<string, unknown> | undefined;
  const storedRaw = Number(zoneProps?.terrain_elevation_m ?? zoneProps?.terrain_height);
  const storedTerrain = Number.isFinite(storedRaw) ? storedRaw : null;
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(0);
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  // The zone moved: unfreeze and re-sample terrain at the new centroid so the
  // model seats on the ground it now stands over (sinking-on-move fix).
  const anchorKey = `${frame.centroidLat.toFixed(6)}:${frame.centroidLng.toFixed(6)}`;
  useEffect(() => {
    setSampledTerrain(null);
    frozenRef.current = false;
    attemptsRef.current = 0;
  }, [anchorKey]);
  const modelRootRef = useRef<THREE.Group>(null);
  const modelWorldPositionRef = useRef(new THREE.Vector3());
  const glazingLodRef = useRef<ArchitecturalGlazingLod>('far');

  useFrame(({ camera }) => {
    if (!preserveSourceMaterials && modelRootRef.current) {
      modelRootRef.current.getWorldPosition(modelWorldPositionRef.current);
      const distance = camera.position.distanceTo(modelWorldPositionRef.current);
      const nextLod = resolveArchitecturalGlazingLod(distance, glazingLodRef.current);
      if (nextLod !== glazingLodRef.current) {
        setArchitecturalGlazingLod(cloned, nextLod);
        glazingLodRef.current = nextLod;
      }
    }
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

    const step = Math.max(1, Math.floor(ring.length / 4));
    const probes: Array<[number, number]> = [[frame.centroidLng, frame.centroidLat]];
    for (let i = 0; i < ring.length && probes.length < 5; i += step) {
      probes.push([ring[i][0], ring[i][1]]);
    }
    const samples = probes.map(([lng, lat]) => (
      raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current)
    ));
    const filtered = getObjectFilteredTerrainHeight(samples, storedTerrain);
    // A legacy stored click can be a valid ground anchor or an old roof hit.
    // Prefer the lower of two materially different plausible anchors; this
    // seats the replacement model on ground in both cases.
    const groundCandidate = preferLowerGroundAnchor(filtered, storedTerrain);
    // Gate against the unrefined-root-tile trap: the first finite sample can
    // land ~29km below the true surface and would sink the model with it
    // (see isPlausibleTerrainAnchor). Implausible samples burn an attempt
    // and retry next interval.
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
    ) {
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  if (!placement) return null;

  const terrain = preparedSiteTerrainHeight
    ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group
        ref={modelRootRef}
        position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], 0]}
        rotation={[0, 0, placement.yawRad]}
        userData={proposalForDirect3D
          ? direct3DBuildingInstanceUserData(building, zone)
          : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
        onClick={(event) => {
          event.stopPropagation();
          onBuildingClick?.(building.id);
        }}
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
      {selected && <LocalModelSelectionOutline ring={ring} frame={frame} />}
    </EastNorthUpFrame>
  );
}

function GeneratedBuildingMassing({
  building,
  zone,
  ring,
  frame,
  fallbackTerrainHeight,
  preparedSiteTerrainHeight,
  onLoaded,
  onUnloaded,
  selected,
  proposalForDirect3D,
  onBuildingClick,
}: {
  building: Building;
  zone: SiteZone | undefined;
  ring: number[][];
  frame: FootprintFrame;
  fallbackTerrainHeight: number;
  preparedSiteTerrainHeight?: number | null;
  onLoaded: (id: string) => void;
  onUnloaded: (id: string) => void;
  selected: boolean;
  proposalForDirect3D: boolean;
  onBuildingClick?: (buildingId: string) => void;
}) {
  const height = Math.max(2.5, Number(building.height_meters) || 3.2);
  const geometry = useMemo(() => {
    const data = buildLegoMassingMeshData(
      ring,
      frame.centroidLng,
      frame.centroidLat,
      height,
    );
    if (!data) return null;
    const next = new THREE.BufferGeometry();
    next.setAttribute('position', new THREE.Float32BufferAttribute(data.positions, 3));
    next.setIndex(data.indices);
    next.computeVertexNormals();
    next.computeBoundingSphere();
    return next;
  }, [frame.centroidLat, frame.centroidLng, height, ring]);
  useEffect(() => () => geometry?.dispose(), [geometry]);

  const tiles = useContext(TilesRendererContext);
  const properties = zone?.properties as Record<string, unknown> | undefined;
  const storedRaw = Number(properties?.terrain_elevation_m ?? properties?.terrain_height);
  const storedTerrain = Number.isFinite(storedRaw) ? storedRaw : null;
  const anchorKey = `${building.id}:${frame.centroidLat.toFixed(6)}:${frame.centroidLng.toFixed(6)}`;
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(
    () => generatedTerrainSampleCache.get(anchorKey) ?? null,
  );
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(stableFrameOffset(
    building.id,
    MASSING_TERRAIN_SAMPLE_FRAME_INTERVAL,
  ));
  const attemptsRef = useRef(0);
  const frozenRef = useRef(sampledTerrain !== null);
  // The zone moved: drop the stale frozen anchor and re-sample at the new spot.
  useEffect(() => {
    const cached = generatedTerrainSampleCache.get(anchorKey) ?? null;
    setSampledTerrain(cached);
    frozenRef.current = cached !== null;
    attemptsRef.current = 0;
  }, [anchorKey]);

  useFrame(() => {
    if (frozenRef.current || !geometry) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % MASSING_TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= MASSING_TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const step = Math.max(1, Math.floor(ring.length / 4));
    const probes: Array<[number, number]> = [[frame.centroidLng, frame.centroidLat]];
    for (let index = 0; index < ring.length && probes.length < 5; index += step) {
      probes.push([ring[index][0], ring[index][1]]);
    }
    const samples = probes.map(([longitude, latitude]) => (
      raycastTerrainHeightAtLatLng(longitude, latitude, tilesGroup, raycasterRef.current)
    ));
    const filtered = getObjectFilteredTerrainHeight(samples, storedTerrain);
    const groundCandidate = preferLowerGroundAnchor(filtered, storedTerrain);
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(
        groundCandidate,
        storedTerrain ?? fallbackTerrainHeight,
      )
    ) {
      generatedTerrainSampleCache.set(anchorKey, groundCandidate);
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  useEffect(() => {
    if (!geometry) return undefined;
    onLoaded(building.id);
    return () => onUnloaded(building.id);
  }, [building.id, geometry, onLoaded, onUnloaded]);

  if (!geometry) return null;
  const terrain = preparedSiteTerrainHeight ?? resolveZoneTerrainHeight(
    sampledTerrain,
    storedTerrain,
    fallbackTerrainHeight,
  );

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <mesh
        geometry={geometry}
        position={[0, 0, 0]}
        renderOrder={MODEL_RENDER_ORDER}
        userData={proposalForDirect3D
          ? direct3DBuildingInstanceUserData(building, zone)
          : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
        onClick={(event) => {
          event.stopPropagation();
          onBuildingClick?.(building.id);
        }}
      >
        <meshStandardMaterial
          color={legoMassingColor(`generated:${building.architectural_style ?? building.name ?? building.id}`)}
          roughness={0.82}
          metalness={0.04}
          side={THREE.DoubleSide}
        />
      </mesh>
      {selected && <LocalModelSelectionOutline ring={ring} frame={frame} />}
    </EastNorthUpFrame>
  );
}

export function GlobeBuildingModelsLayer({
  buildings,
  zones,
  direct3DProposalBuildingIds,
  terrainHeight,
  preparedSiteTerrainHeight = null,
  onLoadedIdsChange,
  selectedBuildingId = null,
  onBuildingClick,
}: GlobeBuildingModelsLayerProps) {
  const [loadedIds, setLoadedIds] = useState<Set<string>>(() => new Set());
  const camera = useThree((state) => state.camera);

  const zoneByBuildingId = useMemo(() => {
    const map = new Map<string, SiteZone>();
    for (const zone of zones) {
      if (zone.building_id) map.set(zone.building_id, zone);
    }
    return map;
  }, [zones]);

  const entries = useMemo(() => buildings
    .map((building) => {
      if (!(building.lod_urls?.['0'] ?? building.model_url)) return null;
      const zone = zoneByBuildingId.get(building.id);
      // Zone-first: the owning zone's live ring drives placement so edits
      // (rotate/move/reshape) move the model immediately, before regenerate.
      // The stored footprint is the compile-time fallback for zone-less models.
      const ring = zone?.coordinates && zone.coordinates.length >= 3
        ? zone.coordinates
        : building.footprint_coordinates && building.footprint_coordinates.length >= 3
          ? building.footprint_coordinates
          : undefined;
      const frame = ring && ring.length >= 3 ? computeFootprintFrame(ring) : null;
      return ring && frame ? { building, zone, ring, frame } : null;
    })
    .filter((entry): entry is NonNullable<typeof entry> => entry !== null)
    .sort((a, b) => (
      (a.building.created_at ?? '').localeCompare(b.building.created_at ?? '')
      || a.building.id.localeCompare(b.building.id)
    )), [buildings, zoneByBuildingId]);

  const entryWorldPositions = useMemo(() => {
    const positions = new Map<string, THREE.Vector3>();
    for (const entry of entries) {
      const position = new THREE.Vector3();
      WGS84_ELLIPSOID.getCartographicToPosition(
        entry.frame.centroidLat * DEG_TO_RAD,
        entry.frame.centroidLng * DEG_TO_RAD,
        terrainHeight,
        position,
      );
      positions.set(entry.building.id, position);
    }
    return positions;
  }, [entries, terrainHeight]);

  const selectDetailedIds = useCallback((cameraPosition: THREE.Vector3) => {
    const selection = partitionGeneratedBuildingLod(
      entries,
      (entry) => entryWorldPositions.get(entry.building.id)?.distanceToSquared(cameraPosition) ?? Infinity,
    );
    return new Set(selection.detailed.map((entry) => entry.building.id));
  }, [entries, entryWorldPositions]);
  const [detailedIds, setDetailedIds] = useState<Set<string>>(() => new Set());
  const [availableModelUrls, setAvailableModelUrls] = useState<Set<string>>(() => new Set());
  const lodFrameRef = useRef(0);
  useEffect(() => {
    setDetailedIds(selectDetailedIds(camera.position));
  }, [camera, selectDetailedIds]);
  useFrame(() => {
    lodFrameRef.current += 1;
    if (lodFrameRef.current % 60 !== 0) return;
    const next = selectDetailedIds(camera.position);
    setDetailedIds((previous) => (setsEqual(previous, next) ? previous : next));
  });

  useEffect(() => {
    let cancelled = false;
    const urls = [...new Set(entries.map(({ building }) => (
      resolveApiFileUrl(building.lod_urls?.['0'] ?? building.model_url ?? '')
    )))].filter(Boolean);
    setAvailableModelUrls(new Set());
    void Promise.all(urls.map(async (url) => ({
      url,
      available: await modelAssetAvailable(url),
    }))).then((results) => {
      if (cancelled) return;
      setAvailableModelUrls(new Set(
        results.filter(({ available }) => available).map(({ url }) => url),
      ));
    });
    return () => {
      cancelled = true;
    };
  }, [entries]);

  useEffect(() => {
    onLoadedIdsChange(loadedIds);
  }, [loadedIds, onLoadedIdsChange]);

  useEffect(() => {
    if (
      import.meta.env.DEV
      && entries.length > 0
      && loadedIds.size === entries.length
    ) {
      console.debug(
        `[GlobeModels] Mounted all ${entries.length} generated buildings `
        + `(${Math.min(entries.length, GENERATED_BUILDING_DETAIL_BUDGET)} detailed budget, `
        + `${Math.max(0, entries.length - GENERATED_BUILDING_DETAIL_BUDGET)} massing LOD)`,
      );
    }
  }, [entries.length, loadedIds.size]);

  // Clear suppression for everything when the layer unmounts (toggle off).
  useEffect(() => () => onLoadedIdsChange(new Set()), [onLoadedIdsChange]);

  const handleLoaded = useCallback((id: string) => setLoadedIds((prev) => {
    if (prev.has(id)) return prev;
    const next = new Set(prev);
    next.add(id);
    return next;
  }), []);
  const handleUnloaded = useCallback((id: string) => setLoadedIds((prev) => {
    if (!prev.has(id)) return prev;
    const next = new Set(prev);
    next.delete(id);
    return next;
  }), []);

  return (
    <>
      {entries.map(({ building, zone, ring, frame }) => {
        const modelUrl = resolveApiFileUrl(building.lod_urls?.['0'] ?? building.model_url ?? '');
        const massing = (
          <GeneratedBuildingMassing
            building={building}
            zone={zone}
            ring={ring}
            frame={frame}
            fallbackTerrainHeight={terrainHeight}
            preparedSiteTerrainHeight={preparedSiteTerrainHeight}
            onLoaded={handleLoaded}
            onUnloaded={handleUnloaded}
            selected={selectedBuildingId === building.id}
            proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
            onBuildingClick={onBuildingClick}
          />
        );
        if (!detailedIds.has(building.id) || !availableModelUrls.has(modelUrl)) {
          return (
            <GeneratedBuildingMassing
              key={building.id}
              building={building}
              zone={zone}
              ring={ring}
              frame={frame}
              fallbackTerrainHeight={terrainHeight}
              preparedSiteTerrainHeight={preparedSiteTerrainHeight}
              onLoaded={handleLoaded}
              onUnloaded={handleUnloaded}
              selected={selectedBuildingId === building.id}
              proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
              onBuildingClick={onBuildingClick}
            />
          );
        }
        return (
          <SilentModelBoundary key={building.id} fallback={massing}>
            <Suspense fallback={massing}>
              <BuildingModelInstance
                building={building}
                zone={zone}
                ring={ring}
                frame={frame}
                fallbackTerrainHeight={terrainHeight}
                preparedSiteTerrainHeight={preparedSiteTerrainHeight}
                onLoaded={handleLoaded}
                onUnloaded={handleUnloaded}
                selected={selectedBuildingId === building.id}
                proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
                onBuildingClick={onBuildingClick}
              />
            </Suspense>
          </SilentModelBoundary>
        );
      })}
    </>
  );
}
