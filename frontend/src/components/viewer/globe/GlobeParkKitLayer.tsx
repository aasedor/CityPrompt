/**
 * GlobeParkKitLayer — scatters park kit props (trees, benches, playground,
 * pavilion) across green_space zones using the deterministic recipes in
 * parkKitRecipes + parkScatter. One InstancedMesh per prop part per zone
 * keeps draw calls bounded (500 trees = 2 draw calls, not 500).
 *
 * v1 ships a procedural placeholder kit (cone+cylinder tree, box bench) so
 * the scatter system works before any GLB exists; C2 swaps in Meshy-generated
 * kit assets behind the same placement list.
 *
 * Placement is seeded by zone.id — orbiting, re-selecting, or reloading
 * never reshuffles a park. renderOrder 145: under placed GLBs (150), above
 * road detail (122-130).
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
import type { SiteZone } from '@/types';
import { resolveApiFileUrl } from '@/services/api';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { getObjectFilteredTerrainHeight, isPlausibleTerrainAnchor, resolveZoneTerrainHeight } from './globeTerrainUtils';
import { resolveParkRecipe } from '@/data/parkKitRecipes';
import { PARK_KIT_MANIFEST } from '@/data/parkKitManifest';
import { computeParkPlacements, type ParkPropId, type PropPlacement } from './parkScatter';
import { getEzTreeKit, splitBySpecies } from './ezTreeKit';

const DEG_TO_RAD = Math.PI / 180;
// TEMP: raised 50 -> 120 for the park ortho pilot (Water Centre has 100
// zones across scenarios). Revisit with per-park instancing budgets before
// shipping; scatter cost scales with green_space count, not total zones.
const LIGHTWEIGHT_ZONE_THRESHOLD = 120;
const RENDER_ORDER_PROPS = 145;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
// Fold anchor bias above this into the frame height at freeze (see below).
const ANCHOR_RECENTER_THRESHOLD_METERS = 20;
const INSTANCES_PER_BATCH = 25;
const MAX_SAMPLE_PASSES = 3;

// Placeholder kit dims (metres) — aligned with PARK_FURNITURE /
// PLAYGROUND_EQUIPMENT in archetypeMetadataSchema (bench 1.8x0.6x0.45).
const TREE_TRUNK_HEIGHT = 2.2;
const TREE_TRUNK_RADIUS = 0.22;
const TREE_CANOPY_HEIGHT = 6.5;
const TREE_CANOPY_RADIUS = 2.6;
const BENCH_SIZE: [number, number, number] = [1.8, 0.6, 0.45];
const PLAYGROUND_SIZE: [number, number, number] = [3.2, 3.2, 2.4];
const PAVILION_SIZE: [number, number, number] = [6, 6, 3.4];

const COLOR_TRUNK = '#7a5b3a';
const COLOR_CANOPY = '#4d7c4a';
const COLOR_BENCH = '#8a7f6a';
const COLOR_PLAYGROUND = '#c98a3d';
const COLOR_PAVILION = '#9c8f7d';

interface KitPart {
  geometry: THREE.BufferGeometry;
  color?: string;
  /** Full material (e.g. EZ-Tree bark/leaves); takes precedence over color. */
  material?: THREE.Material;
}

/** Placeholder prop parts, base-at-origin, Z-up. Built once per module. */
function buildPlaceholderKit(): Record<ParkPropId, KitPart[]> {
  const trunk = new THREE.CylinderGeometry(TREE_TRUNK_RADIUS, TREE_TRUNK_RADIUS * 1.3, TREE_TRUNK_HEIGHT, 6);
  trunk.rotateX(Math.PI / 2);
  trunk.translate(0, 0, TREE_TRUNK_HEIGHT / 2);
  const canopy = new THREE.ConeGeometry(TREE_CANOPY_RADIUS, TREE_CANOPY_HEIGHT, 8);
  canopy.rotateX(Math.PI / 2);
  canopy.translate(0, 0, TREE_TRUNK_HEIGHT + TREE_CANOPY_HEIGHT / 2);

  const box = (size: [number, number, number]) => {
    const g = new THREE.BoxGeometry(size[0], size[1], size[2]);
    g.translate(0, 0, size[2] / 2);
    return g;
  };

  return {
    tree: [
      { geometry: trunk, color: COLOR_TRUNK },
      { geometry: canopy, color: COLOR_CANOPY },
    ],
    bench: [{ geometry: box(BENCH_SIZE), color: COLOR_BENCH }],
    playground: [{ geometry: box(PLAYGROUND_SIZE), color: COLOR_PLAYGROUND }],
    pavilion: [{ geometry: box(PAVILION_SIZE), color: COLOR_PAVILION }],
  };
}

const PLACEHOLDER_KIT = buildPlaceholderKit();

function zoneStoredTerrain(zone: SiteZone): number | null {
  const props = zone.properties as Record<string, unknown> | undefined;
  const raw = Number(props?.terrain_elevation_m ?? props?.terrain_height);
  return Number.isFinite(raw) ? raw : null;
}

/** useGLTF throws on missing kit assets; fall back to the placeholder. */
class SilentKitBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    // expected until the kit GLBs are generated — placeholder covers it
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

/**
 * Instanced GLB kit asset: every mesh inside the GLB becomes one
 * InstancedMesh sharing the placement list. Normalization (uniform scale to
 * targetHeight, base at origin, glTF Y-up -> ENU Z-up) is baked into each
 * instance matrix.
 */
function GLBInstancedProp({
  url,
  targetHeight,
  placements,
  centroid,
  instanceZ,
}: {
  url: string;
  targetHeight: number;
  placements: PropPlacement[];
  centroid: { lng: number; lat: number };
  instanceZ: number[] | null;
}) {
  const { scene } = useGLTF(resolveApiFileUrl(url));

  const parts = useMemo(() => {
    const bbox = new THREE.Box3().setFromObject(scene);
    const size = bbox.getSize(new THREE.Vector3());
    const center = bbox.getCenter(new THREE.Vector3());
    const normScale = size.y > 0 ? targetHeight / size.y : 1;
    // model-space: recenter XZ, base at min Y, swizzle Y-up -> Z-up, scale
    const norm = new THREE.Matrix4()
      .makeRotationX(Math.PI / 2)
      .multiply(new THREE.Matrix4().makeScale(normScale, normScale, normScale))
      .multiply(new THREE.Matrix4().makeTranslation(-center.x, -bbox.min.y, -center.z));

    const collected: Array<{ geometry: THREE.BufferGeometry; material: THREE.Material }> = [];
    scene.updateMatrixWorld(true);
    scene.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      const geometry = mesh.geometry.clone();
      geometry.applyMatrix4(mesh.matrixWorld);
      geometry.applyMatrix4(norm);
      const material = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
      collected.push({ geometry, material });
    });
    return collected;
  }, [scene, targetHeight]);

  // The clones above are full geometry copies per zone — dispose them on
  // recompute/unmount (materials stay owned by the drei GLTF cache).
  useEffect(
    () => () => {
      for (const part of parts) part.geometry.dispose();
    },
    [parts],
  );

  const mPerLon = metersPerDegLon(centroid.lat);
  const refs = useRef<Array<THREE.InstancedMesh | null>>([]);

  useEffect(() => {
    const m = new THREE.Matrix4();
    const q = new THREE.Quaternion();
    const pos = new THREE.Vector3();
    const scl = new THREE.Vector3();
    const zAxis = new THREE.Vector3(0, 0, 1);
    for (const mesh of refs.current) {
      if (!mesh) continue;
      placements.forEach((p, i) => {
        pos.set(
          (p.lng - centroid.lng) * mPerLon,
          (p.lat - centroid.lat) * METERS_PER_DEG_LAT,
          instanceZ?.[i] ?? 0,
        );
        q.setFromAxisAngle(zAxis, p.yawRad);
        scl.setScalar(p.scale);
        m.compose(pos, q, scl);
        mesh.setMatrixAt(i, m);
      });
      mesh.count = placements.length;
      mesh.instanceMatrix.needsUpdate = true;
    }
  }, [placements, centroid.lng, centroid.lat, mPerLon, instanceZ, parts]);

  return (
    <>
      {parts.map((part, i) => (
        <instancedMesh
          key={i}
          ref={(el) => {
            refs.current[i] = el;
          }}
          args={[part.geometry, part.material, Math.max(1, placements.length)]}
          renderOrder={RENDER_ORDER_PROPS}
          frustumCulled={false}
        />
      ))}
    </>
  );
}

function InstancedProp({
  part,
  placements,
  centroid,
  instanceZ,
}: {
  part: KitPart;
  placements: PropPlacement[];
  centroid: { lng: number; lat: number };
  instanceZ: number[] | null;
}) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const mPerLon = metersPerDegLon(centroid.lat);

  useEffect(() => {
    const mesh = meshRef.current;
    if (!mesh) return;
    const m = new THREE.Matrix4();
    const q = new THREE.Quaternion();
    const pos = new THREE.Vector3();
    const scl = new THREE.Vector3();
    const zAxis = new THREE.Vector3(0, 0, 1);
    placements.forEach((p, i) => {
      pos.set(
        (p.lng - centroid.lng) * mPerLon,
        (p.lat - centroid.lat) * METERS_PER_DEG_LAT,
        instanceZ?.[i] ?? 0,
      );
      q.setFromAxisAngle(zAxis, p.yawRad);
      scl.setScalar(p.scale);
      m.compose(pos, q, scl);
      mesh.setMatrixAt(i, m);
    });
    mesh.count = placements.length;
    mesh.instanceMatrix.needsUpdate = true;
  }, [placements, centroid.lng, centroid.lat, mPerLon, instanceZ]);

  return (
    <instancedMesh
      ref={meshRef}
      args={[part.geometry, part.material, Math.max(1, placements.length)]}
      renderOrder={RENDER_ORDER_PROPS}
      frustumCulled={false}
    >
      {/* transparent + depthWrite: composite above the floating flat zone
          ground washes (see ezTreeKit material note). */}
      {!part.material && <meshLambertMaterial color={part.color} transparent depthWrite />}
    </instancedMesh>
  );
}

function ParkKitInstance({
  zone,
  fallbackTerrainHeight,
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
}) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(0);
  const attemptsRef = useRef(0);
  const nextInstanceRef = useRef(0);
  const instanceZRef = useRef<number[] | null>(null);
  const frozenRef = useRef(false);
  const [sampledTerrain, setSampledTerrain] = useState<number | null>(null);
  const [instanceZ, setInstanceZ] = useState<number[] | null>(null);

  const props = zone.properties as Record<string, unknown> | undefined;
  const recipe = useMemo(
    () => resolveParkRecipe(String(props?.green_space_archetype_id ?? '')),
    [props?.green_space_archetype_id],
  );
  // Landscape pattern stamped by the backend plan generator (green zones and
  // courtyards); absent on hand-drawn zones -> legacy edge-biased scatter.
  const plantingStructure =
    typeof props?.planting_structure === 'string' ? props.planting_structure : undefined;

  const { placements, centroid } = useMemo(() => {
    const list = computeParkPlacements(
      { id: zone.id, coordinates: zone.coordinates },
      recipe,
      plantingStructure,
    );
    let lng = 0;
    let lat = 0;
    for (const c of zone.coordinates) {
      lng += c[0];
      lat += c[1];
    }
    return {
      placements: list,
      centroid: { lng: lng / zone.coordinates.length, lat: lat / zone.coordinates.length },
    };
    // updated_at covers geometry edits committed by the edit mode
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zone.id, zone.coordinates, zone.updated_at, recipe, plantingStructure]);

  const byProp = useMemo(() => {
    const groups = new Map<ParkPropId, PropPlacement[]>();
    for (const p of placements) {
      const list = groups.get(p.propId) ?? [];
      list.push(p);
      groups.set(p.propId, list);
    }
    return groups;
  }, [placements]);

  const storedTerrain = zoneStoredTerrain(zone);
  const hitFlagsRef = useRef<boolean[] | null>(null);
  const passRef = useRef(0);

  // Coordinates/recipe changed under the same zone id — restart draping.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    nextInstanceRef.current = 0;
    passRef.current = 0;
    instanceZRef.current = null;
    hitFlagsRef.current = null;
    setInstanceZ(null);
    setSampledTerrain(null);
  }, [placements]);

  // Anchor the frame, then seat instances in interval-gated batches
  // (drape-and-freeze; z accumulates in refs, state set once at freeze).
  useFrame(() => {
    if (frozenRef.current || placements.length === 0) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return;

    const anchored = sampledTerrain !== null || storedTerrain !== null;
    if (!anchored) {
      if (attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) {
        frozenRef.current = true;
        return;
      }
      attemptsRef.current += 1;
      // Multi-probe: a single centroid ray under photogrammetry canopy
      // anchors the whole park on a treetop; quartile-filter several probes
      // (same rationale as GlobeBuildingModelsLayer).
      const ring = zone.coordinates;
      const step = Math.max(1, Math.floor(ring.length / 4));
      const probes: Array<[number, number]> = [[centroid.lng, centroid.lat]];
      for (let i = 0; i < ring.length && probes.length < 5; i += step) {
        probes.push([ring[i][0], ring[i][1]]);
      }
      const samples = probes.map(([lng, lat]) =>
        raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycasterRef.current),
      );
      const filtered = getObjectFilteredTerrainHeight(samples, null);
      // Gate against the unrefined-root-tile trap: the first finite sample
      // can be ~29km below the true surface (see isPlausibleTerrainAnchor).
      // An implausible sample burns an attempt and retries next interval —
      // by then the tiles near the zone have usually refined.
      if (filtered !== null && isPlausibleTerrainAnchor(filtered, storedTerrain ?? fallbackTerrainHeight)) {
        setSampledTerrain(filtered);
      }
      return;
    }

    const anchor = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
    const n = placements.length;
    if (!instanceZRef.current || instanceZRef.current.length !== n) {
      instanceZRef.current = new Array<number>(n).fill(0);
      hitFlagsRef.current = new Array<boolean>(n).fill(false);
      nextInstanceRef.current = 0;
      passRef.current = 0;
    }
    const zs = instanceZRef.current;
    const hits = hitFlagsRef.current!;
    let i = nextInstanceRef.current;
    let processed = 0;
    while (i < n && processed < INSTANCES_PER_BATCH) {
      if (!hits[i]) {
        const p = placements[i];
        const h = raycastTerrainHeightAtLatLng(p.lng, p.lat, tilesGroup, raycasterRef.current);
        if (h !== null) {
          zs[i] = h - anchor;
          hits[i] = true;
        }
        processed++;
      }
      i++;
    }
    nextInstanceRef.current = i;
    if (i >= n) {
      const misses = hits.filter((x) => !x).length;
      if (misses > n * 0.2 && passRef.current < MAX_SAMPLE_PASSES) {
        passRef.current += 1;
        nextInstanceRef.current = 0;
        return;
      }
      // Self-recentering: if the anchor is biased despite the plausibility
      // gate (e.g. sampled against partially refined tiles), every seated
      // instance shares that bias. Fold the median offset back into the
      // anchor so per-instance Z stays near zero and z=0 means "on the
      // ground" for unseated instances too. World altitude is unchanged:
      // (anchor + median) + (z - median) === anchor + z.
      const hitZs = zs.filter((_, idx) => hits[idx]).sort((a, b) => a - b);
      if (hitZs.length > 0) {
        const median = hitZs[Math.floor(hitZs.length / 2)];
        if (Math.abs(median) > ANCHOR_RECENTER_THRESHOLD_METERS) {
          for (let k = 0; k < n; k += 1) {
            zs[k] = hits[k] ? zs[k] - median : 0;
          }
          setSampledTerrain(anchor + median);
        }
      }
      frozenRef.current = true;
      setInstanceZ(zs.slice());
    }
  });

  if (placements.length === 0) return null;
  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  return (
    <EastNorthUpFrame
      lat={centroid.lat * DEG_TO_RAD}
      lon={centroid.lng * DEG_TO_RAD}
      height={terrain}
    >
      {[...byProp.entries()].map(([propId, group]) => {
        const groupZ = instanceZ
          ? group.map((g) => instanceZ[placements.indexOf(g)] ?? 0)
          : null;
        // Trees render as a mixed stand of runtime-generated EZ-Tree species
        // (pilot 2026-07-11); placeholder cones only if generation failed.
        const ezKit = propId === 'tree' ? getEzTreeKit() : null;
        if (ezKit) {
          const buckets = splitBySpecies(group, ezKit.length);
          return (
            <group key={propId}>
              {buckets.flatMap((idxs, s) =>
                idxs.length === 0
                  ? []
                  : ezKit[s].map((part, partIndex) => (
                      <InstancedProp
                        key={`ez-${s}-${partIndex}`}
                        part={part}
                        placements={idxs.map((i) => group[i])}
                        centroid={centroid}
                        instanceZ={groupZ ? idxs.map((i) => groupZ[i]) : null}
                      />
                    )),
              )}
            </group>
          );
        }
        const placeholder = PLACEHOLDER_KIT[propId].map((part, partIndex) => (
          <InstancedProp
            key={`ph-${propId}-${partIndex}`}
            part={part}
            placements={group}
            centroid={centroid}
            instanceZ={groupZ}
          />
        ));
        const asset = PARK_KIT_MANIFEST[propId];
        // Real GLB kit asset when generated (C2); placeholder until then —
        // and as the Suspense/error fallback so a missing file never crashes.
        return asset ? (
          <SilentKitBoundary key={propId} fallback={<>{placeholder}</>}>
            <Suspense fallback={<>{placeholder}</>}>
              <GLBInstancedProp
                url={asset.url}
                targetHeight={asset.targetHeight_m}
                placements={group}
                centroid={centroid}
                instanceZ={groupZ}
              />
            </Suspense>
          </SilentKitBoundary>
        ) : (
          <group key={propId}>{placeholder}</group>
        );
      })}
    </EastNorthUpFrame>
  );
}

export function GlobeParkKitLayer({
  zones,
  terrainHeight,
}: {
  zones: SiteZone[];
  terrainHeight: number;
}) {
  const parkZones = useMemo(
    () => zones.filter((z) => z.zone_type === 'green_space' && z.coordinates.length >= 3),
    [zones],
  );

  if (zones.length > LIGHTWEIGHT_ZONE_THRESHOLD) return null;

  return (
    <>
      {parkZones.map((zone) => (
        <ParkKitInstance key={zone.id} zone={zone} fallbackTerrainHeight={terrainHeight} />
      ))}
    </>
  );
}
