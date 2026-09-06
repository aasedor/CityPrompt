/**
 * GlobeLegoAssemblyLayer — renders saved LEGO assembly recipes
 * (Building.specifications.legoAssembly) on the 3D tiles globe as stacked
 * module GLBs at the building's real footprint, with exact floor counts.
 *
 * Mirrors GlobeBuildingModelsLayer's placement stack (EastNorthUpFrame at the
 * footprint's oriented-rect center, terrain drape-and-freeze, Rx(+90°) Y-up ->
 * Z-up wrapper, renderOrder 150, SilentBoundary error isolation, prism
 * suppression handshake) — but instead of contain-fitting one bbox, it mounts
 * every recipe instance verbatim using the legoShared.ModuleInstance
 * conventions (backend Z-up -> three Y-up swizzle; planner fit scales already
 * baked into instance scales, so nothing is re-fit here).
 *
 * Repeated floor GLBs are cheap: drei's useGLTF caches per URL and each level
 * is a clone sharing geometry buffers. GPU instancing (InstancedMesh) is a
 * possible v2 optimization — deliberately not done in v1.
 */

import {
  Component,
  Suspense,
  useCallback,
  useContext,
  useEffect,
  useId,
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
import type { LegoAssemblyRecipe } from '@/features/legoAssembly/legoAssemblyApi';
import { centreNativeClayClone, isNativeClayPlan } from '@/features/legoAssembly/nativeClayPlacement';
import { authoredHomePlotFrame, preservesAuthoredPlotAxes } from '@/features/legoAssembly/detachedPlot';
import { resolveApiFileUrl } from '@/services/api';
import { createKtx2LoaderExtension } from '@/lib/ktx2GltfLoader';
import { computeFootprintFrame, type FootprintFrame } from './buildingPlacement';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { useSharedSiteGround } from './SharedSiteGroundProvider';
import { currentBuildingGroundingIssues, geographicFootprint, placedNativeFootprints, resolveBuildingGroundContact, updateBuildingGroundingIssues, type GroundPoint, type LegoGroundingIssue } from './buildingGroundContact';
import {
  isPlausibleTerrainAnchor,
  resolveMeasuredReplacementGround,
  resolveZoneTerrainHeight,
  terrainAnchorRevisionKey,
} from './globeTerrainUtils';
import {
  computeLegoStackBaseLift,
  computeLegoStackYaw,
  extractLegoRecipe,
  extractPlannedMassing,
  legoFootprintRing,
  legoInstanceTransform,
  type PlannedMassingSpec,
  uniqueModuleUrls,
} from './legoGlobePlacement';
import {
  disposeArchitecturalCloneMaterials,
  prepareArchitecturalClone,
  resolveArchitecturalGlazingLod,
  setArchitecturalGlazingLod,
  type ArchitecturalGlazingLod,
} from './modelMaterialQuality';
import { buildLegoMassingMeshData, legoMassingColor } from './legoMassingGeometry';
import {
  LEGO_DISTINCT_FAMILY_RENDER_BUDGET,
  LEGO_STACK_RENDER_BUDGET,
  partitionLegoStacksByDistanceAndFamily,
} from './legoStackBudget';
import {
  classifyLegoLayerReadiness,
  indexRenderableLegoScenes,
  isCompleteLegoModuleStack,
} from './legoModuleReadiness';
import { LocalModelSelectionOutline } from './GlobeModelSelectionOutline';
import {
  DIRECT_3D_CAPTURE_CONTEXT_USER_DATA,
  direct3DInstanceUserData,
  direct3DZoneInstanceDescriptor,
} from './direct3dCapture';

const DEG_TO_RAD = Math.PI / 180;
// Same convention as GlobeBuildingModelsLayer: above depthTest-false road
// overlays (120), below zone prisms (200).
const LEGO_RENDER_ORDER = 150;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
const MASSING_TERRAIN_SAMPLE_FRAME_INTERVAL = 300;
const MASSING_TERRAIN_SAMPLE_MAX_ATTEMPTS = 8;
const legoTerrainSampleCache = new Map<string, number>();

/** Corroborate plot hits with an independent ring outside its footprint.
 * Google photogrammetry includes roofs, so centre/corner rays alone cannot
 * establish the ground under a replacement building. */
function sampleReplacementGround(
  ring: number[][],
  frame: { centroidLat: number; centroidLng: number },
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
  stored: number | null,
  fallback: number,
): number | null {
  if (ring.length < 3) return null;
  const local: Array<[number, number]> = [[frame.centroidLng, frame.centroidLat]];
  const step = Math.max(1, Math.floor(ring.length / 4));
  for (let index = 0; index < ring.length && local.length < 5; index += step) local.push([ring[index][0], ring[index][1]]);
  const longitudePadding = 8 / Math.max(1, 111320 * Math.cos(frame.centroidLat * DEG_TO_RAD));
  const latitudePadding = 8 / 111320;
  const west = Math.min(...ring.map((point) => point[0])) - longitudePadding;
  const east = Math.max(...ring.map((point) => point[0])) + longitudePadding;
  const south = Math.min(...ring.map((point) => point[1])) - latitudePadding;
  const north = Math.max(...ring.map((point) => point[1])) + latitudePadding;
  const surrounding: Array<[number, number]> = [
    [west, south], [west, north], [east, south], [east, north],
    [(west + east) / 2, south], [(west + east) / 2, north],
    [west, (south + north) / 2], [east, (south + north) / 2],
  ];
  const heights = (points: Array<[number, number]>) => points.map(([lng, lat]) => raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycaster));
  return resolveMeasuredReplacementGround(heights(local), heights(surrounding), stored, fallback);
}

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

export type { LegoGroundingIssue } from './buildingGroundContact';
type GroundingStatusReporter = (buildingId: string, rendererId: string, reason: string | null) => void;

interface GlobeLegoAssemblyLayerProps {
  buildings: Building[];
  zones: SiteZone[];
  /** Exact server-claimed buildings editable by Direct 3D. */
  direct3DProposalBuildingIds?: ReadonlySet<string>;
  /** Site-level elevation fallback (from the map's elevation fetch). */
  terrainHeight: number;
  /** Buildings whose stack is actually mounted — drives prism suppression. */
  onLoadedIdsChange: (ids: Set<string>) => void;
  /** Blocking contact issues, separate from asset-loading/prism suppression. */
  onGroundingIssuesChange?: (issues: LegoGroundingIssue[]) => void;
  selectedBuildingId?: string | null;
  onBuildingClick?: (buildingId: string) => void;
}

/** useGLTF throws on bad/missing modules; Suspense doesn't catch errors.
 *  Fallback is null so the zone prism (or Meshy model) simply stays visible. */
class SilentLegoBoundary extends Component<{
  children: ReactNode;
  fallback?: ReactNode;
}, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    console.warn('[GlobeLego] module failed to load', error);
  }
  render() {
    return this.state.failed ? (this.props.fallback ?? null) : this.props.children;
  }
}

type GlobeBuildingEntry = {
  building: Building;
  ring: number[][];
  frame: FootprintFrame;
} & (
  | { kind: 'lego'; recipe: LegoAssemblyRecipe }
  | { kind: 'massing'; massing: PlannedMassingSpec }
);

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

function useBuildingFoundation(footprints: GroundPoint[][], frame: FootprintFrame, buildingId: string, report?: GroundingStatusReporter) {
  const sharedGround = useSharedSiteGround();
  const rendererId = useId();
  const contact = useMemo(() => resolveBuildingGroundContact(footprints, frame.centroidLng, frame.centroidLat, sharedGround),
    [footprints, frame.centroidLng, frame.centroidLat, sharedGround]);
  const geometry = useMemo(() => {
    if (contact.status !== 'ready') return null;
    const result = new THREE.BufferGeometry();
    result.setAttribute('position', new THREE.Float32BufferAttribute(contact.positions, 3));
    result.setIndex(contact.indices);
    result.computeVertexNormals();
    result.computeBoundingSphere();
    return result;
  }, [contact]);
  useEffect(() => () => geometry?.dispose(), [geometry]);
  const reason = contact.status === 'unresolved' ? contact.reason ?? 'incomplete_footprint_ground' : null;
  useEffect(() => {
    report?.(buildingId, rendererId, reason);
    return () => report?.(buildingId, rendererId, null);
  }, [buildingId, rendererId, reason, report]);
  return { contact, geometry };
}

function LegoMassingStack({
  building,
  heightMeters,
  colorSeed,
  ring,
  frame,
  zone,
  fallbackTerrainHeight,
  preparedSiteTerrainHeight,
  onLoaded,
  onUnloaded,
  onGroundingStatus,
  selected,
  proposalForDirect3D,
  onBuildingClick,
}: {
  building: Building;
  heightMeters: number | null | undefined;
  colorSeed: string;
  ring: number[][];
  frame: FootprintFrame;
  zone: SiteZone | undefined;
  fallbackTerrainHeight: number;
  preparedSiteTerrainHeight?: number | null;
  onLoaded?: (id: string) => void;
  onUnloaded?: (id: string) => void;
  onGroundingStatus?: GroundingStatusReporter;
  selected: boolean;
  proposalForDirect3D: boolean;
  onBuildingClick?: (buildingId: string) => void;
}) {
  const height = Math.max(
    2.5,
    Number(heightMeters)
      || Number(building.height_meters)
      || Number(building.floor_count) * 3.2
      || 10,
  );
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

  const groundFootprints = useMemo(() => [geographicFootprint(ring, frame.centroidLng, frame.centroidLat)], [ring, frame.centroidLng, frame.centroidLat]);
  const foundation = useBuildingFoundation(groundFootprints, frame, building.id, onGroundingStatus);

  const tiles = useContext(TilesRendererContext);
  const properties = zone?.properties as Record<string, unknown> | undefined;
  const storedRaw = Number(properties?.terrain_elevation_m ?? properties?.terrain_height);
  const storedTerrain = Number.isFinite(storedRaw) ? storedRaw : null;
  const anchorKey = terrainAnchorRevisionKey(building.id, frame.centroidLng, frame.centroidLat, zone?.updated_at, storedTerrain, fallbackTerrainHeight);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(
    () => legoTerrainSampleCache.get(anchorKey) ?? null,
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
    const cached = legoTerrainSampleCache.get(anchorKey) ?? null;
    setSampledTerrain(cached);
    frozenRef.current = cached !== null;
    attemptsRef.current = 0;
  }, [anchorKey]);
  useEffect(() => {
    if (!tiles) return undefined;
    const refresh = () => {
      legoTerrainSampleCache.delete(anchorKey);
      frozenRef.current = false;
      attemptsRef.current = 0;
    };
    tiles.addEventListener('tiles-load-end', refresh);
    return () => tiles.removeEventListener('tiles-load-end', refresh);
  }, [tiles, anchorKey]);
  useFrame(() => {
    if (foundation.contact.status !== 'outside' || preparedSiteTerrainHeight != null || frozenRef.current || !geometry) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % MASSING_TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= MASSING_TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const groundCandidate = sampleReplacementGround(ring, frame, tilesGroup, raycasterRef.current, storedTerrain, fallbackTerrainHeight);
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(
        groundCandidate,
        storedTerrain ?? fallbackTerrainHeight,
      )
    ) {
      legoTerrainSampleCache.set(anchorKey, groundCandidate);
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  useEffect(() => {
    if (!geometry || foundation.contact.status === 'unresolved') return undefined;
    onLoaded?.(building.id);
    return () => onUnloaded?.(building.id);
  }, [building.id, geometry, foundation.contact.status, onLoaded, onUnloaded]);

  if (!geometry || foundation.contact.status === 'unresolved') return null;
  const terrain = (foundation.contact.status === 'ready' ? foundation.contact.anchorHeight : null) ?? preparedSiteTerrainHeight ?? resolveZoneTerrainHeight(
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
        renderOrder={LEGO_RENDER_ORDER}
        userData={proposalForDirect3D
          ? direct3DBuildingInstanceUserData(building, zone)
          : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
        onClick={(event) => {
          event.stopPropagation();
          onBuildingClick?.(building.id);
        }}
      >
        <meshStandardMaterial
          color={legoMassingColor(`${colorSeed}:${building.id}`)}
          roughness={0.82}
          metalness={0.02}
          side={THREE.DoubleSide}
        />
      </mesh>
      {foundation.geometry && <mesh geometry={foundation.geometry} renderOrder={LEGO_RENDER_ORDER}
        userData={proposalForDirect3D ? direct3DBuildingInstanceUserData(building, zone) : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}>
        <meshStandardMaterial color="#8f8c84" roughness={0.95} side={THREE.DoubleSide} />
      </mesh>}
      {selected && <LocalModelSelectionOutline ring={ring} frame={frame} />}
    </EastNorthUpFrame>
  );
}

function LegoStackInstance({
  building,
  recipe,
  ring,
  frame,
  zone,
  fallbackTerrainHeight,
  preparedSiteTerrainHeight,
  onLoaded,
  onUnloaded,
  onGroundingStatus,
  selected,
  proposalForDirect3D,
  onBuildingClick,
  incompleteFallback,
}: {
  building: Building;
  recipe: LegoAssemblyRecipe;
  ring: number[][];
  frame: FootprintFrame;
  zone: SiteZone | undefined;
  fallbackTerrainHeight: number;
  preparedSiteTerrainHeight?: number | null;
  onLoaded: (id: string) => void;
  onUnloaded: (id: string) => void;
  onGroundingStatus?: GroundingStatusReporter;
  selected: boolean;
  proposalForDirect3D: boolean;
  onBuildingClick?: (buildingId: string) => void;
  incompleteFallback: ReactNode;
}) {
  // One suspension point for the whole stack: all distinct module GLBs load
  // before anything mounts, so the prism handoff is atomic (no half-stacks).
  const urls = useMemo(
    () => uniqueModuleUrls(recipe).map((url) => resolveApiFileUrl(url)),
    [recipe],
  );
  const gl = useThree((state) => state.gl);
  const extendLoader = useMemo(() => createKtx2LoaderExtension(gl), [gl]);
  const gltfs = useGLTF(urls, true, true, extendLoader);
  const tiles = useContext(TilesRendererContext);
  const maxAnisotropy = gl.capabilities.getMaxAnisotropy();

  const sceneByUrl = useMemo(
    () => indexRenderableLegoScenes(urls, gltfs),
    [urls, gltfs],
  );

  // Clone per instance (repeated floors share cached geometry buffers) and
  // restyle for the globe: renderOrder + no frustum culling + env intensity.
  const modules = useMemo(() => {
    // A partially resolved family is not a valid architectural stack. Avoid
    // preparing half the clones; retain the height-bearing massing until every
    // distinct source scene has real mesh geometry.
    if (!urls.every((url) => sceneByUrl.has(url))) return [];
    return recipe.instances
      .map((instance, index) => {
        const scene = sceneByUrl.get(resolveApiFileUrl(instance.model_url));
        if (!scene) return null;
        const prepared = prepareArchitecturalClone(scene, {
          renderOrder: LEGO_RENDER_ORDER,
          maxAnisotropy,
          ambientOcclusion: 'disable',
        });
        const cloned = isNativeClayPlan(recipe) ? centreNativeClayClone(prepared) : prepared;
        return {
          key: `${instance.asset_id}-${instance.level}-${index}`,
          cloned,
          transform: legoInstanceTransform(instance),
          bounds: isNativeClayPlan(recipe)
            ? new THREE.Box3().setFromObject(cloned, true)
            : new THREE.Box3().setFromObject(scene),
        };
      })
      .filter((entry): entry is NonNullable<typeof entry> => entry !== null);
  }, [maxAnisotropy, recipe, sceneByUrl, urls]);
  const detailedReady = isCompleteLegoModuleStack(recipe.instances.length, modules.length);
  const authoredPlot = preservesAuthoredPlotAxes(zone?.properties) ? authoredHomePlotFrame(ring) : undefined;
  const yawRad = authoredPlot ? authoredPlot.yawRad + (building.rotation_degrees ?? 0) * DEG_TO_RAD
    : computeLegoStackYaw(frame.bearingRad, recipe.target, building.rotation_degrees);
  const groundFootprints = useMemo(() => isNativeClayPlan(recipe) || recipe.fit?.placement_mode === 'detached_lots'
    ? placedNativeFootprints(modules, yawRad, frame.rectCenterLocal)
    : [geographicFootprint(ring, frame.centroidLng, frame.centroidLat)],
  [recipe, modules, yawRad, frame.rectCenterLocal, ring, frame.centroidLng, frame.centroidLat]);
  const foundation = useBuildingFoundation(groundFootprints, frame, building.id, onGroundingStatus);
  const stackBaseLift = useMemo(() => computeLegoStackBaseLift(
    modules.map(({ bounds, transform }) => ({
      positionY: transform.position[1],
      scaleY: transform.scale[1],
      boundsMinY: bounds.min.y,
      boundsMaxY: bounds.max.y,
    })),
  ), [modules]);
  useEffect(() => () => {
    modules.forEach(({ cloned }) => disposeArchitecturalCloneMaterials(cloned));
  }, [modules]);

  // Prism suppression: only while this stack is actually mounted AND placeable.
  useEffect(() => {
    if (!detailedReady || foundation.contact.status === 'unresolved') return undefined;
    onLoaded?.(building.id);
    return () => onUnloaded?.(building.id);
  }, [building.id, detailedReady, foundation.contact.status, onLoaded, onUnloaded]);

  useEffect(() => {
    if (detailedReady || !import.meta.env.DEV) return;
    console.warn(
      `[GlobeLego] ${building.id} resolved an incomplete detailed stack `
      + `(${modules.length}/${recipe.instances.length} instances); retaining massing fallback`,
    );
  }, [building.id, detailedReady, modules.length, recipe.instances.length]);

  // Terrain seating — same priority chain as GlobeBuildingModelsLayer:
  // stored zone elevation first, then lower-quartile raycast probes
  // (drape-and-freeze), then the site-level fallback.
  const zoneProps = zone?.properties as Record<string, unknown> | undefined;
  const storedRaw = Number(zoneProps?.terrain_elevation_m ?? zoneProps?.terrain_height);
  const storedTerrain = Number.isFinite(storedRaw) ? storedRaw : null;
  const anchorKey = terrainAnchorRevisionKey(building.id, frame?.centroidLng ?? 0, frame?.centroidLat ?? 0, zone?.updated_at, storedTerrain, fallbackTerrainHeight);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(
    () => legoTerrainSampleCache.get(anchorKey) ?? null,
  );
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(0);
  const attemptsRef = useRef(0);
  const frozenRef = useRef(sampledTerrain !== null);
  // The zone moved: drop the stale frozen anchor and re-sample at the new spot.
  useEffect(() => {
    const cached = legoTerrainSampleCache.get(anchorKey) ?? null;
    setSampledTerrain(cached);
    frozenRef.current = cached !== null;
    attemptsRef.current = 0;
  }, [anchorKey]);
  useEffect(() => {
    if (!tiles) return undefined;
    const refresh = () => {
      legoTerrainSampleCache.delete(anchorKey);
      frozenRef.current = false;
      attemptsRef.current = 0;
    };
    tiles.addEventListener('tiles-load-end', refresh);
    return () => tiles.removeEventListener('tiles-load-end', refresh);
  }, [tiles, anchorKey]);
  const stackRef = useRef<THREE.Group>(null);
  const stackWorldPositionRef = useRef(new THREE.Vector3());
  const glazingLodRef = useRef<ArchitecturalGlazingLod>('far');

  useFrame(({ camera }) => {
    if (stackRef.current) {
      stackRef.current.getWorldPosition(stackWorldPositionRef.current);
      const distance = camera.position.distanceTo(stackWorldPositionRef.current);
      const nextLod = resolveArchitecturalGlazingLod(distance, glazingLodRef.current);
      if (nextLod !== glazingLodRef.current) {
        modules.forEach(({ cloned }) => setArchitecturalGlazingLod(cloned, nextLod));
        glazingLodRef.current = nextLod;
      }
    }
    if (foundation.contact.status !== 'outside' || preparedSiteTerrainHeight != null || frozenRef.current || !frame) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
      frozenRef.current = true;
      return;
    }
    attemptsRef.current += 1;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const groundCandidate = sampleReplacementGround(ring, frame, tilesGroup, raycasterRef.current, storedTerrain, fallbackTerrainHeight);
    // Unrefined-root-tile guard: implausible samples burn an attempt and retry.
    if (
      groundCandidate !== null
      && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
    ) {
      legoTerrainSampleCache.set(anchorKey, groundCandidate);
      setSampledTerrain(groundCandidate);
      frozenRef.current = true;
    }
  });

  if (!detailedReady) return incompleteFallback;
  if (foundation.contact.status === 'unresolved') return null;

  const terrain = (foundation.contact.status === 'ready' ? foundation.contact.anchorHeight : null) ?? preparedSiteTerrainHeight
    ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
  // Recipe target width (stack X) vs depth (stack Z) fixes the plan
  // orientation, so the stack's long axis lands on the footprint's long axis
  // and the module front facade (+Z glTF) faces the short-axis street side.

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group
        ref={stackRef}
        position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], 0]}
        rotation={[0, 0, yawRad]}
        userData={proposalForDirect3D
          ? direct3DBuildingInstanceUserData(building, zone)
          : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
        onClick={(event) => {
          event.stopPropagation();
          onBuildingClick?.(building.id);
        }}
      >
        {/* Rx(+90°): glTF Y-up -> ENU Z-up (stack Y becomes Up, Z becomes -North).
            Inside, the stack is built in glTF Y-up space per the legoShared
            ModuleInstance conventions. Native clay clones have been translated
            to bottom-centre without scaling; legacy modules retain their
            authored stack origins. */}
        <group rotation={[Math.PI / 2, 0, 0]}>
          <group position={[0, stackBaseLift, 0]}>
            {modules.map(({ key, cloned, transform }) => (
              <primitive
                key={key}
                object={cloned}
                position={transform.position}
                rotation={[0, transform.rotationYRad, 0]}
                scale={transform.scale}
              />
            ))}
          </group>
        </group>
      </group>
      {foundation.geometry && <mesh geometry={foundation.geometry} renderOrder={LEGO_RENDER_ORDER}
        userData={proposalForDirect3D ? direct3DBuildingInstanceUserData(building, zone) : DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}>
        <meshStandardMaterial color="#8f8c84" roughness={0.95} side={THREE.DoubleSide} />
      </mesh>}
      {selected && <LocalModelSelectionOutline ring={ring} frame={frame} />}
    </EastNorthUpFrame>
  );
}

export function GlobeLegoAssemblyLayer({
  buildings,
  zones,
  direct3DProposalBuildingIds,
  terrainHeight,
  onLoadedIdsChange,
  onGroundingIssuesChange,
  selectedBuildingId = null,
  onBuildingClick,
}: GlobeLegoAssemblyLayerProps) {
  const [loadedIds, setLoadedIds] = useState<Set<string>>(() => new Set());
  const [detailedReadyIds, setDetailedReadyIds] = useState<Set<string>>(() => new Set());
  const [temporaryFallbackIds, setTemporaryFallbackIds] = useState<Set<string>>(() => new Set());
  // Renderer identity prevents a departing Suspense fallback from clearing a
  // still-unresolved detailed renderer for the same building.
  const [groundingIssues, setGroundingIssues] = useState<ReadonlyMap<string, LegoGroundingIssue>>(() => new Map());
  const handleGroundingStatus = useCallback<GroundingStatusReporter>((buildingId, rendererId, reason) => {
    setGroundingIssues((previous) => updateBuildingGroundingIssues(previous, buildingId, rendererId, reason));
  }, []);
  useEffect(() => {
    const ids = new Set(buildings.map((building) => building.id));
    onGroundingIssuesChange?.(currentBuildingGroundingIssues(groundingIssues, ids));
  }, [buildings, groundingIssues, onGroundingIssuesChange]);
  useEffect(() => () => onGroundingIssuesChange?.([]), [onGroundingIssuesChange]);
  const camera = useThree((state) => state.camera);

  const zoneRingByBuildingId = useMemo(() => {
    const map = new Map<string, number[][]>();
    for (const zone of zones) {
      if (zone.building_id && Array.isArray(zone.coordinates)) {
        map.set(zone.building_id, zone.coordinates);
      }
    }
    return map;
  }, [zones]);

  const { entries, skippedWithoutFootprint } = useMemo(() => {
    const nextEntries: GlobeBuildingEntry[] = [];
    let skipped = 0;
    for (const building of buildings) {
      const recipe = extractLegoRecipe(building);
      const massing = recipe ? null : extractPlannedMassing(building);
      if (!recipe && !massing) continue;
      // Zone-first: the owning zone's live ring drives placement so edits
      // (rotate/move/reshape) move the stack immediately, before regenerate.
      const ring = legoFootprintRing(building, zoneRingByBuildingId.get(building.id));
      const frame = ring ? computeFootprintFrame(ring) : null;
      if (!ring || !frame) {
        skipped += 1;
        continue;
      }
      nextEntries.push(recipe
        ? { kind: 'lego', building, recipe, ring, frame }
        : { kind: 'massing', building, massing: massing!, ring, frame });
    }
    nextEntries.sort((a, b) => (
      (a.building.created_at ?? '').localeCompare(b.building.created_at ?? '')
      || a.building.id.localeCompare(b.building.id)
    ));
    return { entries: nextEntries, skippedWithoutFootprint: skipped };
  }, [buildings, zoneRingByBuildingId]);

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
    const legoEntries = entries.filter(
      (entry): entry is Extract<GlobeBuildingEntry, { kind: 'lego' }> => entry.kind === 'lego',
    );
    const selection = partitionLegoStacksByDistanceAndFamily(
      legoEntries,
      (entry) => entry.recipe.module_family,
      (entry) => (
        entry.building.id === selectedBuildingId
          ? -1
          : entryWorldPositions.get(entry.building.id)?.distanceToSquared(cameraPosition) ?? Infinity
      ),
    );
    return new Set(selection.detailed.map((entry) => entry.building.id));
  }, [entries, entryWorldPositions, selectedBuildingId]);
  // Start the in-budget detailed loads during the first render. Initializing
  // empty mounted every recipe as a final LOD massing for one commit, which
  // could report a false all-ready state before the GLBs even began loading.
  const [detailedIds, setDetailedIds] = useState<Set<string>>(
    () => selectDetailedIds(camera.position),
  );
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
  const zoneByBuildingId = useMemo(() => {
    const map = new Map<string, SiteZone>();
    for (const zone of zones) {
      if (zone.building_id) map.set(zone.building_id, zone);
      for (const buildingId of zone.building_ids ?? []) map.set(buildingId, zone);
    }
    return map;
  }, [zones]);

  useEffect(() => {
    if (import.meta.env.DEV && skippedWithoutFootprint > 0) {
      console.debug(
        `[GlobeLego] ${skippedWithoutFootprint} building(s) have a saved LEGO recipe but no footprint_coordinates — skipped`,
      );
    }
  }, [skippedWithoutFootprint]);

  useEffect(() => {
    onLoadedIdsChange(loadedIds);
  }, [loadedIds, onLoadedIdsChange]);

  const layerReadiness = classifyLegoLayerReadiness({
    entryCount: entries.length,
    visibleRepresentationCount: loadedIds.size,
    detailedTargetCount: detailedIds.size,
    detailedReadyCount: detailedReadyIds.size,
    temporaryFallbackCount: temporaryFallbackIds.size,
  });
  useEffect(() => {
    if (!import.meta.env.DEV) return;
    if (layerReadiness === 'ready') {
      const legoCount = entries.filter((entry) => entry.kind === 'lego').length;
      const plannedMassingCount = entries.length - legoCount;
      console.debug(
        `[GlobeLego] Detailed readiness complete for ${entries.length} building representations `
        + `(${detailedReadyIds.size}/${legoCount} detailed, `
        + `${Math.max(0, legoCount - detailedReadyIds.size)} final LOD massing, `
        + `${Math.min(legoCount, LEGO_STACK_RENDER_BUDGET)} stack budget, `
        + `${LEGO_DISTINCT_FAMILY_RENDER_BUDGET} distinct-family budget, `
        + `${plannedMassingCount} planned-family massing)`,
      );
    }
    if (layerReadiness === 'fallback-visible') {
      console.debug(
        `[GlobeLego] ${temporaryFallbackIds.size} detailed stack(s) still loading; `
        + 'showing full-height massing fallback',
      );
    }
  }, [detailedReadyIds.size, entries, layerReadiness, temporaryFallbackIds.size]);

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
  const handleDetailedLoaded = useCallback((id: string) => {
    handleLoaded(id);
    setDetailedReadyIds((previous) => {
      if (previous.has(id)) return previous;
      const next = new Set(previous);
      next.add(id);
      return next;
    });
  }, [handleLoaded]);
  const handleDetailedUnloaded = useCallback((id: string) => {
    handleUnloaded(id);
    setDetailedReadyIds((previous) => {
      if (!previous.has(id)) return previous;
      const next = new Set(previous);
      next.delete(id);
      return next;
    });
  }, [handleUnloaded]);
  const handleFallbackLoaded = useCallback((id: string) => {
    handleLoaded(id);
    setTemporaryFallbackIds((previous) => {
      if (previous.has(id)) return previous;
      const next = new Set(previous);
      next.add(id);
      return next;
    });
  }, [handleLoaded]);
  const handleFallbackUnloaded = useCallback((id: string) => {
    handleUnloaded(id);
    setTemporaryFallbackIds((previous) => {
      if (!previous.has(id)) return previous;
      const next = new Set(previous);
      next.delete(id);
      return next;
    });
  }, [handleUnloaded]);

  // No recipes on this project: clean no-op (hooks above always run in the
  // same order, so this early return is safe).
  if (entries.length === 0) return null;

  return (
    <>
      {entries.map((entry) => {
        const { building, ring, frame } = entry;
        const zone = zoneByBuildingId.get(building.id);
        // A boundary must not flatten unrelated buildings or those in its notch.
        // Detail, loading fallback and distance massing use the same datum.
        const preparedSiteTerrainHeight = resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight);
        if (entry.kind === 'massing') {
          return (
            <LegoMassingStack
              key={building.id}
              building={building}
              heightMeters={entry.massing.height_meters}
              colorSeed={entry.massing.archetype_id ?? 'planned-massing'}
              ring={ring}
              frame={frame}
              zone={zone}
              fallbackTerrainHeight={terrainHeight}
              preparedSiteTerrainHeight={preparedSiteTerrainHeight}
              onLoaded={handleLoaded}
              onUnloaded={handleUnloaded}
              onGroundingStatus={handleGroundingStatus}
              selected={selectedBuildingId === building.id}
              proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
              onBuildingClick={onBuildingClick}
            />
          );
        }
        const { recipe } = entry;
        const massing = (
          <LegoMassingStack
            building={building}
            heightMeters={recipe.assembled_height_m}
            colorSeed={recipe.module_family}
            ring={ring}
            frame={frame}
            zone={zone}
            fallbackTerrainHeight={terrainHeight}
            preparedSiteTerrainHeight={preparedSiteTerrainHeight}
            onLoaded={handleFallbackLoaded}
            onUnloaded={handleFallbackUnloaded}
            onGroundingStatus={handleGroundingStatus}
            selected={selectedBuildingId === building.id}
            proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
            onBuildingClick={onBuildingClick}
          />
        );
        if (!detailedIds.has(building.id)) {
          return <LegoMassingStack
            key={building.id}
            building={building}
            heightMeters={recipe.assembled_height_m}
            colorSeed={recipe.module_family}
            ring={ring}
            frame={frame}
            zone={zone}
            fallbackTerrainHeight={terrainHeight}
            preparedSiteTerrainHeight={preparedSiteTerrainHeight}
            onLoaded={handleLoaded}
            onUnloaded={handleUnloaded}
            onGroundingStatus={handleGroundingStatus}
            selected={selectedBuildingId === building.id}
            proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
            onBuildingClick={onBuildingClick}
          />;
        }
        return (
          <SilentLegoBoundary key={building.id} fallback={massing}>
            <Suspense fallback={massing}>
              <LegoStackInstance
                building={building}
                recipe={recipe}
                ring={ring}
                frame={frame}
                zone={zone}
                fallbackTerrainHeight={terrainHeight}
                preparedSiteTerrainHeight={preparedSiteTerrainHeight}
                onLoaded={handleDetailedLoaded}
                onUnloaded={handleDetailedUnloaded}
                onGroundingStatus={handleGroundingStatus}
                selected={selectedBuildingId === building.id}
                proposalForDirect3D={direct3DProposalBuildingIds?.has(building.id) ?? false}
                onBuildingClick={onBuildingClick}
                incompleteFallback={massing}
              />
            </Suspense>
          </SilentLegoBoundary>
        );
      })}
    </>
  );
}
