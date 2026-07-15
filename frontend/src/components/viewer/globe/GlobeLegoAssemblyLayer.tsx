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
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { Building, SiteZone } from '@/types';
import type { LegoAssemblyRecipe } from '@/features/legoAssembly/legoAssemblyApi';
import { resolveApiFileUrl } from '@/services/api';
import { computeFootprintFrame } from './buildingPlacement';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { getObjectFilteredTerrainHeight, isPlausibleTerrainAnchor, resolveZoneTerrainHeight } from './globeTerrainUtils';
import {
  computeLegoStackYaw,
  extractLegoRecipe,
  legoFootprintRing,
  legoInstanceTransform,
  uniqueModuleUrls,
} from './legoGlobePlacement';

const DEG_TO_RAD = Math.PI / 180;
const MAX_LEGO_STACKS = 20;
const GROUND_EMBED_METERS = 0.3;
// Same convention as GlobeBuildingModelsLayer: above depthTest-false road
// overlays (120), below zone prisms (200).
const LEGO_RENDER_ORDER = 150;
const MODULE_ENV_INTENSITY = 0.6;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;

interface GlobeLegoAssemblyLayerProps {
  buildings: Building[];
  zones: SiteZone[];
  /** Site-level elevation fallback (from the map's elevation fetch). */
  terrainHeight: number;
  /** Buildings whose stack is actually mounted — drives prism suppression. */
  onLoadedIdsChange: (ids: Set<string>) => void;
}

/** useGLTF throws on bad/missing modules; Suspense doesn't catch errors.
 *  Fallback is null so the zone prism (or Meshy model) simply stays visible. */
class SilentLegoBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    console.warn('[GlobeLego] module failed to load', error);
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

function LegoStackInstance({
  building,
  recipe,
  ring,
  zone,
  fallbackTerrainHeight,
  onLoaded,
  onUnloaded,
}: {
  building: Building;
  recipe: LegoAssemblyRecipe;
  ring: number[][];
  zone: SiteZone | undefined;
  fallbackTerrainHeight: number;
  onLoaded: (id: string) => void;
  onUnloaded: (id: string) => void;
}) {
  // One suspension point for the whole stack: all distinct module GLBs load
  // before anything mounts, so the prism handoff is atomic (no half-stacks).
  const urls = useMemo(
    () => uniqueModuleUrls(recipe).map((url) => resolveApiFileUrl(url)),
    [recipe],
  );
  const gltfs = useGLTF(urls);
  const tiles = useContext(TilesRendererContext);

  const frame = useMemo(() => computeFootprintFrame(ring), [ring]);

  const sceneByUrl = useMemo(() => {
    const map = new Map<string, THREE.Object3D>();
    urls.forEach((url, index) => {
      const gltf = gltfs[index];
      if (gltf) map.set(url, gltf.scene);
    });
    return map;
  }, [urls, gltfs]);

  // Clone per instance (repeated floors share cached geometry buffers) and
  // restyle for the globe: renderOrder + no frustum culling + env intensity.
  const modules = useMemo(() => (
    recipe.instances
      .map((instance, index) => {
        const scene = sceneByUrl.get(resolveApiFileUrl(instance.model_url));
        if (!scene) return null;
        const cloned = scene.clone(true);
        cloned.traverse((obj) => {
          obj.renderOrder = LEGO_RENDER_ORDER;
          obj.frustumCulled = false;
          const mesh = obj as THREE.Mesh;
          if (mesh.isMesh) {
            const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
            for (const material of materials) {
              const standard = material as THREE.MeshStandardMaterial;
              if (standard.isMeshStandardMaterial) {
                standard.envMapIntensity = MODULE_ENV_INTENSITY;
              }
            }
          }
        });
        return {
          key: `${instance.asset_id}-${instance.level}-${index}`,
          cloned,
          transform: legoInstanceTransform(instance),
        };
      })
      .filter((entry): entry is NonNullable<typeof entry> => entry !== null)
  ), [recipe, sceneByUrl]);

  // Prism suppression: only while this stack is actually mounted AND placeable.
  useEffect(() => {
    if (!frame) return undefined;
    onLoaded(building.id);
    return () => onUnloaded(building.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [building.id, frame]);

  // Terrain seating — same priority chain as GlobeBuildingModelsLayer:
  // stored zone elevation first, then lower-quartile raycast probes
  // (drape-and-freeze), then the site-level fallback.
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
    // Unrefined-root-tile guard: implausible samples burn an attempt and retry.
    if (filtered !== null && isPlausibleTerrainAnchor(filtered, fallbackTerrainHeight)) {
      setSampledTerrain(filtered);
      frozenRef.current = true;
    }
  });

  if (!frame || modules.length === 0) return null;

  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
  // Recipe target width (stack X) vs depth (stack Z) fixes the plan
  // orientation, so the stack's long axis lands on the footprint's long axis
  // and the module front facade (+Z glTF) faces the short-axis street side.
  const yawRad = computeLegoStackYaw(frame.bearingRad, recipe.target, building.rotation_degrees);

  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrain}
    >
      <group
        position={[frame.rectCenterLocal[0], frame.rectCenterLocal[1], -GROUND_EMBED_METERS]}
        rotation={[0, 0, yawRad]}
      >
        {/* Rx(+90°): glTF Y-up -> ENU Z-up (stack Y becomes Up, Z becomes -North).
            Inside, the stack is built in glTF Y-up space per the legoShared
            ModuleInstance conventions. Modules are bottom-centre origin and the
            recipe origin is the building's bottom-centre, so no recentering:
            the frame transform alone positions the stack. */}
        <group rotation={[Math.PI / 2, 0, 0]}>
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
    </EastNorthUpFrame>
  );
}

export function GlobeLegoAssemblyLayer({
  buildings,
  zones,
  terrainHeight,
  onLoadedIdsChange,
}: GlobeLegoAssemblyLayerProps) {
  const [loadedIds, setLoadedIds] = useState<Set<string>>(() => new Set());

  const { placeable, skippedWithoutFootprint } = useMemo(() => {
    const entries: Array<{ building: Building; recipe: LegoAssemblyRecipe; ring: number[][] }> = [];
    let skipped = 0;
    for (const building of buildings) {
      const recipe = extractLegoRecipe(building);
      if (!recipe) continue;
      const ring = legoFootprintRing(building);
      if (!ring) {
        skipped += 1;
        continue;
      }
      entries.push({ building, recipe, ring });
    }
    entries.sort((a, b) => (
      (a.building.created_at ?? '').localeCompare(b.building.created_at ?? '')
      || a.building.id.localeCompare(b.building.id)
    ));
    return { placeable: entries.slice(0, MAX_LEGO_STACKS), skippedWithoutFootprint: skipped };
  }, [buildings]);

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

  // No recipes on this project: clean no-op (hooks above always run in the
  // same order, so this early return is safe).
  if (placeable.length === 0) return null;

  return (
    <>
      {placeable.map(({ building, recipe, ring }) => (
        <SilentLegoBoundary key={building.id}>
          <Suspense fallback={null}>
            <LegoStackInstance
              building={building}
              recipe={recipe}
              ring={ring}
              zone={zones.find((z) => z.building_id === building.id)}
              fallbackTerrainHeight={terrainHeight}
              onLoaded={handleLoaded}
              onUnloaded={handleUnloaded}
            />
          </Suspense>
        </SilentLegoBoundary>
      ))}
    </>
  );
}
