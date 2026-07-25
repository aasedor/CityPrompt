/**
 * GlobeParkKitLayer — mounts only fixed, programmed park structures in the
 * editable Google Tiles scene. Trees and benches are deliberately deferred
 * to the architectural render, and missing playground/pavilion GLBs never
 * fall back to cartoon procedural placeholders.
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
import {
  resolveCommunity3DKind,
  shouldRenderCommunityProps,
} from '@/features/community3d/community3d';
import { resolveApiFileUrl } from '@/services/api';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import {
  getObjectFilteredTerrainHeight,
  isPlausibleTerrainAnchor,
  preferLowerGroundAnchor,
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import { PARK_KIT_MANIFEST } from '@/data/parkKitManifest';
import {
  computeParkPlacements,
  resolveParkRecipeForZone,
  type ParkPropId,
  type PropPlacement,
} from './parkScatter';
import {
  JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M,
  WETLAND_BOARDWALK_PATHS,
  fitParkGroundGuides,
  resolveParkGroundProfile,
  resolveParkPlantingStructure,
  resolveParkSpecialtyStructureKind,
  shouldMountParkProgramFrame,
  type ParkSpecialtyStructureKind,
} from './parkGroundProfiles';
import {
  hasCurrentParkGroundSurface,
  shouldDeferParkFinishingProp,
  shouldRenderLiveParkProp,
} from './parkGroundTexture';

const DEG_TO_RAD = Math.PI / 180;
const RENDER_ORDER_PROPS = 145;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
// Fold anchor bias above this into the frame height at freeze (see below).
const ANCHOR_RECENTER_THRESHOLD_METERS = 20;
const INSTANCES_PER_BATCH = 25;
const MAX_SAMPLE_PASSES = 3;

function zoneStoredTerrain(zone: SiteZone): number | null {
  const props = zone.properties as Record<string, unknown> | undefined;
  const raw = Number(props?.terrain_elevation_m ?? props?.terrain_height);
  return Number.isFinite(raw) ? raw : null;
}

/** A missing fixed-structure asset is omitted without destabilizing the map. */
class SilentKitBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    // Expected until the one-time kit asset is generated.
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

function ProceduralParkFinishingProps({
  propId,
  placements,
  centroid,
  instanceZ,
}: {
  propId: 'tree' | 'bench';
  placements: PropPlacement[];
  centroid: { lng: number; lat: number };
  instanceZ: number[] | null;
}) {
  const mPerLon = metersPerDegLon(centroid.lat);
  return (
    <>
      {placements.map((placement, index) => {
        const x = (placement.lng - centroid.lng) * mPerLon;
        const y = (placement.lat - centroid.lat) * METERS_PER_DEG_LAT;
        const z = instanceZ?.[index] ?? 0;
        if (propId === 'tree') {
          const scale = Math.max(0.72, placement.scale);
          return (
            <group
              key={`tree-${index}`}
              position={[x, y, z]}
              rotation={[0, 0, placement.yawRad]}
              scale={[scale, scale, scale]}
              renderOrder={RENDER_ORDER_PROPS}
            >
              <mesh position={[0, 0, 2.7]} renderOrder={RENDER_ORDER_PROPS}>
                <cylinderGeometry args={[0.22, 0.34, 5.4, 10]} />
                <meshStandardMaterial color="#65503d" roughness={0.96} />
              </mesh>
              <mesh position={[-0.35, 0, 6.2]} scale={[1, 0.82, 1.05]} renderOrder={RENDER_ORDER_PROPS}>
                <dodecahedronGeometry args={[2.15, 1]} />
                <meshStandardMaterial color="#48663d" roughness={0.94} />
              </mesh>
              <mesh position={[1.05, 0.3, 5.85]} scale={[1.05, 0.9, 0.95]} renderOrder={RENDER_ORDER_PROPS}>
                <dodecahedronGeometry args={[1.55, 1]} />
                <meshStandardMaterial color="#587649" roughness={0.94} />
              </mesh>
              <mesh position={[-0.75, -0.9, 5.6]} scale={[0.9, 1.05, 0.9]} renderOrder={RENDER_ORDER_PROPS}>
                <dodecahedronGeometry args={[1.45, 1]} />
                <meshStandardMaterial color="#3f5d36" roughness={0.94} />
              </mesh>
            </group>
          );
        }
        return (
          <group
            key={`bench-${index}`}
            position={[x, y, z + 0.42]}
            rotation={[0, 0, placement.yawRad]}
            scale={[placement.scale, placement.scale, placement.scale]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <mesh renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[1.8, 0.48, 0.14]} />
              <meshStandardMaterial color="#80583d" roughness={0.86} />
            </mesh>
            <mesh position={[0, 0.2, 0.48]} rotation={[Math.PI / 12, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[1.8, 0.12, 0.85]} />
              <meshStandardMaterial color="#745038" roughness={0.86} />
            </mesh>
            {[-0.67, 0.67].map((legX) => (
              <mesh key={legX} position={[legX, 0, -0.25]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.1, 0.38, 0.5]} />
                <meshStandardMaterial color="#44494a" metalness={0.38} roughness={0.58} />
              </mesh>
            ))}
          </group>
        );
      })}
    </>
  );
}

/** Small deterministic structures that are part of an archetype's spatial
 * program but do not yet warrant a fetched GLB kit asset. */
function ParkSpecialtyStructures({
  structureKind,
  zone,
  centroid,
}: {
  structureKind: ParkSpecialtyStructureKind | null;
  zone: SiteZone;
  centroid: { lng: number; lat: number };
}) {
  const coordinates = zone.coordinates;
  const programFrame = useMemo(() => {
    const mPerLon = metersPerDegLon(centroid.lat);
    const points = coordinates.map(([lng, lat]) => ({
      x: (lng - centroid.lng) * mPerLon,
      y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
    }));
    const minX = Math.min(...points.map((point) => point.x));
    const maxX = Math.max(...points.map((point) => point.x));
    const minY = Math.min(...points.map((point) => point.y));
    const maxY = Math.max(...points.map((point) => point.y));
    const width = maxX - minX;
    const height = maxY - minY;
    const normalizedRing = points.map((point) => ([
      width > 0 ? (point.x - minX) / width : 0.5,
      height > 0 ? (maxY - point.y) / height : 0.5,
    ] as [number, number]));
    return { minX, maxX, minY, maxY, width, height, normalizedRing };
  }, [centroid.lat, centroid.lng, coordinates]);

  const fittedProgramGuides = useMemo(() => fitParkGroundGuides(
    resolveParkGroundProfile(zone).guides,
    { width: programFrame.width, height: programFrame.height },
    programFrame.normalizedRing,
  ).guides, [programFrame, zone]);

  const bridge = structureKind === 'japanese_garden_bridge'
    ? {
      x: programFrame.minX + programFrame.width * 0.43,
      // Ground-guide Y is measured downward from the north edge.
      y: programFrame.maxY - programFrame.height * 0.54,
      length: JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length,
    }
    : null;

  if (structureKind === 'wetland_boardwalk') {
    const routes = WETLAND_BOARDWALK_PATHS.map((route) => {
      const points = route.points.map(([normalizedX, normalizedY]) => ({
        x: programFrame.minX + programFrame.width * normalizedX,
        y: programFrame.maxY - programFrame.height * normalizedY,
      }));
      const segments = points.slice(1).map((point, index) => ({
        from: points[index],
        to: point,
      }));
      if (route.closed) segments.push({ from: points[points.length - 1], to: points[0] });
      return segments;
    }).flat();
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {routes.map(({ from, to }, index) => {
          const dx = to.x - from.x;
          const dy = to.y - from.y;
          const length = Math.hypot(dx, dy);
          return (
            <group
              key={`wetland-boardwalk-${index}`}
              position={[(from.x + to.x) / 2, (from.y + to.y) / 2, 0.28]}
              rotation={[0, 0, Math.atan2(dy, dx)]}
            >
              <mesh renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[length + 0.16, 2.4, 0.24]} />
                <meshStandardMaterial color={index % 2 === 0 ? '#9a7146' : '#a47b50'} roughness={0.88} />
              </mesh>
              <mesh position={[0, 0, 0.135]} renderOrder={RENDER_ORDER_PROPS}>
                <planeGeometry args={[length, 2.34, Math.max(1, Math.ceil(length / 0.45)), 1]} />
                <meshStandardMaterial color="#b18a5b" wireframe roughness={0.92} />
              </mesh>
            </group>
          );
        })}
        {[
          [0.49, 0.93, 6.0, 4.4],
          [0.88, 0.54, 4.8, 4.8],
        ].map(([normalizedX, normalizedY, width, depth], index) => (
          <mesh
            key={`wetland-overlook-${index}`}
            position={[
              programFrame.minX + programFrame.width * normalizedX,
              programFrame.maxY - programFrame.height * normalizedY,
              0.28,
            ]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <boxGeometry args={[width, depth, 0.24]} />
            <meshStandardMaterial color="#a47a4e" roughness={0.88} />
          </mesh>
        ))}
      </group>
    );
  }

  if (structureKind === 'sports_field_furniture') {
    const fieldGuide = fittedProgramGuides.find((guide) => guide.kind === 'soccer_field');
    const field = fieldGuide ? {
      x: programFrame.minX + programFrame.width * fieldGuide.x,
      y: programFrame.maxY - programFrame.height * fieldGuide.y,
      rotationZ: -((fieldGuide.rotationDeg ?? 0) * Math.PI) / 180,
    } : null;
    const tennisCourts = fittedProgramGuides
      .filter((guide) => guide.kind === 'tennis_court')
      .map((guide) => ({
        x: programFrame.minX + programFrame.width * guide.x,
        y: programFrame.maxY - programFrame.height * guide.y,
        rotationZ: -((guide.rotationDeg ?? 0) * Math.PI) / 180,
      }));
    if (!field && tennisCourts.length === 0) return null;
    const fieldHalfLength = 50;
    const fieldHalfWidth = 32;
    const bleacherRows = [0, 1, 2, 3];
    const lightPositions = [
      [-43, -34],
      [-43, 34],
      [43, -34],
      [43, 34],
    ] as const;
    const rotateFieldOffset = (offsetX: number, offsetY: number) => {
      if (!field) return { x: offsetX, y: offsetY };
      const cos = Math.cos(field.rotationZ);
      const sin = Math.sin(field.rotationZ);
      return {
        x: field.x + offsetX * cos - offsetY * sin,
        y: field.y + offsetX * sin + offsetY * cos,
      };
    };
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {field && [-1, 1].map((direction) => {
          const position = rotateFieldOffset(direction * fieldHalfLength, 0);
          return (
          <group key={`goal-${direction}`} position={[position.x, position.y, 0.06]} rotation={[0, 0, field.rotationZ]}>
            {[-3.66, 3.66].map((goalY) => (
              <mesh key={goalY} position={[0, goalY, 1.22]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.12, 0.12, 2.44]} />
                <meshStandardMaterial color="#e9ece5" roughness={0.72} />
              </mesh>
            ))}
            <mesh position={[0, 0, 2.44]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.12, 7.32, 0.12]} />
              <meshStandardMaterial color="#e9ece5" roughness={0.72} />
            </mesh>
          </group>
          );
        })}
        {field && [-1, 1].flatMap((side) => bleacherRows.map((row) => (
          <mesh
            key={`bleacher-${side}-${row}`}
            position={(() => {
              const position = rotateFieldOffset(0, side * (fieldHalfWidth + 1.1 + row * 0.78));
              return [position.x, position.y, 0.18 + row * 0.32] as [number, number, number];
            })()}
            rotation={[0, 0, field.rotationZ]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <boxGeometry args={[34, 0.72, 0.30]} />
            <meshStandardMaterial color={row % 2 === 0 ? '#9aa0a0' : '#7f8787'} metalness={0.36} roughness={0.58} />
          </mesh>
        )))}
        {field && lightPositions.map(([offsetX, offsetY]) => {
          const position = rotateFieldOffset(offsetX, offsetY);
          return (
          <group key={`light-${offsetX}-${offsetY}`} position={[position.x, position.y, 0]} rotation={[0, 0, field.rotationZ]}>
            <mesh position={[0, 0, 6]} rotation={[Math.PI / 2, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <cylinderGeometry args={[0.10, 0.15, 12, 10]} />
              <meshStandardMaterial color="#646b6d" metalness={0.52} roughness={0.54} />
            </mesh>
            <mesh position={[0, 0, 12]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.28, 3.4, 0.18]} />
              <meshStandardMaterial color="#555d60" metalness={0.46} roughness={0.52} />
            </mesh>
            {[-1.15, 0, 1.15].map((lampY) => (
              <mesh key={lampY} position={[0.16, lampY, 12.05]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.24, 0.44, 0.32]} />
                <meshStandardMaterial color="#d9ddd3" roughness={0.38} />
              </mesh>
            ))}
          </group>
          );
        })}
        {tennisCourts.map((court, index) => (
          <group key={`tennis-net-${index}`} position={[court.x, court.y, 0.04]} rotation={[0, 0, court.rotationZ]}>
            {[-5.49, 5.49].map((netY) => (
              <mesh key={netY} position={[0, netY, 0.54]} rotation={[Math.PI / 2, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
                <cylinderGeometry args={[0.045, 0.045, 1.08, 8]} />
                <meshStandardMaterial color="#4b5353" metalness={0.42} roughness={0.55} />
              </mesh>
            ))}
            <mesh position={[0, 0, 0.56]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <planeGeometry args={[10.97, 1.0]} />
              <meshStandardMaterial color="#30383a" transparent opacity={0.42} side={THREE.DoubleSide} roughness={0.9} />
            </mesh>
          </group>
        ))}
      </group>
    );
  }

  if (structureKind === 'tennis_court_furniture') {
    const courtCenters = fittedProgramGuides
      .filter((guide) => guide.kind === 'tennis_court')
      .map((guide) => ({
        x: programFrame.minX + programFrame.width * guide.x,
        y: programFrame.maxY - programFrame.height * guide.y,
        rotationZ: -((guide.rotationDeg ?? 0) * Math.PI) / 180,
      }));
    if (courtCenters.length === 0) return null;
    const fenceInset = 0.65;
    const fenceWidth = Math.max(1, programFrame.width - fenceInset * 2);
    const fenceDepth = Math.max(1, programFrame.height - fenceInset * 2);
    const fenceHeight = 3.05;
    const FenceMaterial = () => (
      <meshStandardMaterial
        color="#2f3d3d"
        transparent
        opacity={0.24}
        side={THREE.DoubleSide}
        metalness={0.22}
        roughness={0.74}
        depthWrite={false}
      />
    );
    const fencePosts = [
      [programFrame.minX + fenceInset, programFrame.minY + fenceInset],
      [programFrame.minX + fenceInset, programFrame.maxY - fenceInset],
      [programFrame.maxX - fenceInset, programFrame.minY + fenceInset],
      [programFrame.maxX - fenceInset, programFrame.maxY - fenceInset],
      [programFrame.minX + programFrame.width / 2, programFrame.minY + fenceInset],
      [programFrame.minX + programFrame.width / 2, programFrame.maxY - fenceInset],
      [programFrame.minX + fenceInset, programFrame.minY + programFrame.height / 2],
      [programFrame.maxX - fenceInset, programFrame.minY + programFrame.height / 2],
    ] as const;
    const lightPositions = [
      [programFrame.minX + 2.2, programFrame.minY + 2.2],
      [programFrame.minX + 2.2, programFrame.maxY - 2.2],
      [programFrame.maxX - 2.2, programFrame.minY + 2.2],
      [programFrame.maxX - 2.2, programFrame.maxY - 2.2],
      [programFrame.minX + programFrame.width / 2, programFrame.minY + 2.2],
      [programFrame.minX + programFrame.width / 2, programFrame.maxY - 2.2],
    ] as const;
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {courtCenters.map((court, index) => (
          <group key={`tennis-net-${index}`} position={[court.x, court.y, 0.04]} rotation={[0, 0, court.rotationZ]}>
            {[-5.49, 5.49].map((postY) => (
              <mesh key={postY} position={[0, postY, 0.64]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.075, 0.075, 1.28]} />
                <meshStandardMaterial color="#d7dcda" metalness={0.34} roughness={0.54} />
              </mesh>
            ))}
            <mesh position={[0, 0, 0.57]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <planeGeometry args={[10.97, 1.02, 22, 2]} />
              <meshStandardMaterial color="#e8ebe6" wireframe transparent opacity={0.54} side={THREE.DoubleSide} depthWrite={false} />
            </mesh>
            <mesh position={[0, 0, 1.08]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.035, 10.97, 0.055]} />
              <meshStandardMaterial color="#f1f2ed" roughness={0.72} />
            </mesh>
          </group>
        ))}
        <mesh position={[programFrame.minX + programFrame.width / 2, programFrame.minY + fenceInset, fenceHeight / 2]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceWidth, fenceHeight, 24, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[programFrame.minX + programFrame.width / 2, programFrame.maxY - fenceInset, fenceHeight / 2]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceWidth, fenceHeight, 24, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[programFrame.minX + fenceInset, programFrame.minY + programFrame.height / 2, fenceHeight / 2]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceDepth, fenceHeight, 16, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[programFrame.maxX - fenceInset, programFrame.minY + programFrame.height / 2, fenceHeight / 2]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceDepth, fenceHeight, 16, 6]} />
          <FenceMaterial />
        </mesh>
        {fencePosts.map(([x, y], index) => (
          <mesh key={`fence-post-${index}`} position={[x, y, fenceHeight / 2]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[0.09, 0.09, fenceHeight]} />
            <meshStandardMaterial color="#394747" metalness={0.45} roughness={0.58} />
          </mesh>
        ))}
        {lightPositions.map(([x, y], index) => (
          <group key={`court-light-${index}`} position={[x, y, 0]}>
            <mesh position={[0, 0, 6]} renderOrder={RENDER_ORDER_PROPS}>
              <cylinderGeometry args={[0.09, 0.14, 12, 10]} />
              <meshStandardMaterial color="#5d6668" metalness={0.55} roughness={0.5} />
            </mesh>
            <mesh position={[0, 0, 12.05]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[2.4, 0.24, 0.24]} />
              <meshStandardMaterial color="#525b5d" metalness={0.46} roughness={0.5} />
            </mesh>
            {[-0.78, 0, 0.78].map((lampX) => (
              <mesh key={lampX} position={[lampX, 0.16, 11.98]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.42, 0.24, 0.32]} />
                <meshStandardMaterial color="#daddd5" roughness={0.4} />
              </mesh>
            ))}
          </group>
        ))}
      </group>
    );
  }

  if (structureKind === 'botanical_conservatory') {
    const conservatory = {
      x: programFrame.minX + programFrame.width * 0.22,
      y: programFrame.maxY - programFrame.height * 0.24,
      width: 24,
      depth: 14,
    };
    const frameX = [-12, -6, 0, 6, 12];
    return (
      <group position={[conservatory.x, conservatory.y, 0.08]} renderOrder={RENDER_ORDER_PROPS}>
        <mesh position={[0, 0, 0.12]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[conservatory.width, conservatory.depth, 0.24]} />
          <meshStandardMaterial color="#a7aaa4" roughness={0.82} />
        </mesh>
        <mesh position={[0, 0, 1.92]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[23.7, 13.7, 3.45]} />
          <meshPhysicalMaterial
            color="#a9c9c5"
            transparent
            opacity={0.30}
            transmission={0.24}
            roughness={0.16}
            metalness={0.06}
            depthWrite={false}
          />
        </mesh>
        {frameX.map((framePositionX) => (
          <group key={framePositionX}>
            {[-6.85, 6.85].map((framePositionY) => (
              <mesh
                key={framePositionY}
                position={[framePositionX, framePositionY, 2.05]}
                renderOrder={RENDER_ORDER_PROPS}
              >
                <boxGeometry args={[0.13, 0.13, 3.85]} />
                <meshStandardMaterial color="#596666" metalness={0.48} roughness={0.48} />
              </mesh>
            ))}
          </group>
        ))}
        {[-1, 1].map((side) => (
          <mesh
            key={`roof-${side}`}
            position={[0, side * 3.45, 4.33]}
            rotation={[side * 0.32, 0, 0]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <boxGeometry args={[23.8, 7.35, 0.13]} />
            <meshPhysicalMaterial
              color="#c0d8d4"
              transparent
              opacity={0.48}
              transmission={0.32}
              roughness={0.14}
              metalness={0.04}
              depthWrite={false}
            />
          </mesh>
        ))}
        <mesh position={[0, 0, 5.47]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[24, 0.16, 0.16]} />
          <meshStandardMaterial color="#566362" metalness={0.50} roughness={0.46} />
        </mesh>
      </group>
    );
  }

  if (!bridge) return null;
  const segmentCount = 11;
  const segmentLength = bridge.length / segmentCount;
  const deckSegments = Array.from({ length: segmentCount }, (_, index) => {
    const t = (index + 0.5) / segmentCount;
    const x = (t - 0.5) * bridge.length;
    const crown = Math.sin(Math.PI * t) * 0.55;
    const slope = Math.atan(
      (Math.cos(Math.PI * t) * Math.PI * 0.55) / bridge.length,
    );
    return { index, x, crown, slope };
  });
  return (
    // The park drape itself is lifted 0.32 m above the sampled tile surface.
    // Keep the bridge deck clearly above that plane so its end segments do not
    // disappear under the orthophoto through depth fighting.
    <group position={[bridge.x, bridge.y, 0.42]} renderOrder={RENDER_ORDER_PROPS}>
      {deckSegments.map(({ index, x, crown, slope }) => (
        <group key={index}>
          <mesh position={[x, 0, 0.24 + crown]} rotation={[0, -slope, 0]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[segmentLength * 1.06, JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.width, 0.20]} />
            <meshStandardMaterial color={index % 2 === 0 ? '#a9342e' : '#bd4438'} roughness={0.62} />
          </mesh>
          {[-0.98, 0.98].map((railY) => (
            <group key={railY}>
              <mesh position={[x, railY, 1.10 + crown]} rotation={[0, -slope, 0]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[segmentLength * 1.08, 0.11, 0.11]} />
                <meshStandardMaterial color="#7f241f" roughness={0.68} />
              </mesh>
              {index % 2 === 0 && (
                <mesh position={[x, railY, 0.70 + crown]} renderOrder={RENDER_ORDER_PROPS}>
                  <boxGeometry args={[0.12, 0.12, 0.82]} />
                  <meshStandardMaterial color="#7f241f" roughness={0.68} />
                </mesh>
              )}
            </group>
          ))}
        </group>
      ))}
    </group>
  );
}

/** Avoid mounting terrain-sampling frames for parks that have only render-time
 * planting/furniture. Unlike the former count threshold, this never drops an
 * authored bridge or a real fixed-structure asset merely because a district
 * contains many parks. */
function hasLiveProgrammedParkGeometry(zone: SiteZone): boolean {
  const recipe = resolveParkRecipeForZone({
    properties: zone.properties,
    coordinates: zone.coordinates,
    zone_type: zone.zone_type,
  });
  const plantingStructure = resolveParkPlantingStructure(zone);
  const liveAssetPlacementCount = computeParkPlacements(
    { id: zone.id, coordinates: zone.coordinates },
    recipe,
    plantingStructure,
  ).filter((placement) => {
    const asset = PARK_KIT_MANIFEST[placement.propId];
    const hasProceduralFallback = placement.propId === 'tree' || placement.propId === 'bench';
    return !shouldDeferParkFinishingProp(zone, placement.propId)
      && (Boolean(asset) || hasProceduralFallback);
  }).length;
  return shouldMountParkProgramFrame(zone, liveAssetPlacementCount);
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

  // Shared zone-level resolution (archetype id, else plan-role/area fallback).
  // MUST stay the same call parkGroundTexture.buildParkDiagram makes, or the
  // painted pads and the standing props disagree.
  const recipe = useMemo(
    () => resolveParkRecipeForZone({
      properties: zone.properties,
      coordinates: zone.coordinates,
      zone_type: zone.zone_type,
    }),
    [zone.properties, zone.coordinates, zone.zone_type],
  );
  // Landscape pattern stamped by the backend plan generator (green zones and
  // courtyards); absent on hand-drawn zones -> legacy edge-biased scatter.
  const plantingStructure = resolveParkPlantingStructure(zone);
  // A generated green-space drape is the spatial source of truth. Procedural
  // grounds share this kit's deterministic recipe and can therefore show real
  // manifest trees and benches live; AI-resolved grounds still defer those
  // finishing props because their detailed layout is not deterministic.
  const hasCurrentParkGround = hasCurrentParkGroundSurface(zone);
  const specialtyStructureKind = useMemo(
    () => resolveParkSpecialtyStructureKind(zone),
    [zone.properties, zone.zone_type],
  );

  const { placements, centroid } = useMemo(() => {
    const list = computeParkPlacements(
      { id: zone.id, coordinates: zone.coordinates },
      recipe,
      plantingStructure,
    ).filter((placement) => !shouldDeferParkFinishingProp(zone, placement.propId));
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
  }, [
    zone.id,
    zone.coordinates,
    zone.updated_at,
    recipe,
    plantingStructure,
    hasCurrentParkGround,
  ]);

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
    if (frozenRef.current || (placements.length === 0 && !specialtyStructureKind)) return;
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
      const filtered = getObjectFilteredTerrainHeight(samples, storedTerrain);
      const groundCandidate = preferLowerGroundAnchor(filtered, storedTerrain);
      // Gate against the unrefined-root-tile trap: the first finite sample
      // can be ~29km below the true surface (see isPlausibleTerrainAnchor).
      // An implausible sample burns an attempt and retries next interval —
      // by then the tiles near the zone have usually refined.
      if (
        groundCandidate !== null
        && isPlausibleTerrainAnchor(groundCandidate, storedTerrain ?? fallbackTerrainHeight)
      ) {
        setSampledTerrain(groundCandidate);
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
        const sampled = raycastTerrainHeightAtLatLng(p.lng, p.lat, tilesGroup, raycasterRef.current);
        const groundCandidate = preferLowerGroundAnchor(sampled, anchor, 3);
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

  if (placements.length === 0 && !specialtyStructureKind) return null;
  const terrain = resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);

  return (
    <EastNorthUpFrame
      lat={centroid.lat * DEG_TO_RAD}
      lon={centroid.lng * DEG_TO_RAD}
      height={terrain}
    >
      <ParkSpecialtyStructures
        structureKind={specialtyStructureKind}
        zone={zone}
        centroid={centroid}
      />
      {[...byProp.entries()].map(([propId, group]) => {
        const groupZ = instanceZ
          ? group.map((g) => instanceZ[placements.indexOf(g)] ?? 0)
          : null;
        const asset = PARK_KIT_MANIFEST[propId];
        if (shouldDeferParkFinishingProp(zone, propId)) return null;
        if (!asset && (propId === 'tree' || propId === 'bench')) {
          return (
            <ProceduralParkFinishingProps
              key={propId}
              propId={propId}
              placements={group}
              centroid={centroid}
              instanceZ={groupZ}
            />
          );
        }
        if (!shouldRenderLiveParkProp(zone, propId, Boolean(asset)) || !asset) return null;
        return (
          <SilentKitBoundary key={propId} fallback={null}>
            <Suspense fallback={null}>
              <GLBInstancedProp
                url={asset.url}
                targetHeight={asset.targetHeight_m}
                placements={group}
                centroid={centroid}
                instanceZ={groupZ}
              />
            </Suspense>
          </SilentKitBoundary>
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
    () => zones.filter((z) =>
      resolveCommunity3DKind(z) === 'park'
      && z.coordinates.length >= 3
      && shouldRenderCommunityProps(z)
      // Generate 3D always creates a current deterministic ground design;
      // optional AI orthophotos upgrade its material fidelity. Deterministic
      // surfaces can mount the full authored kit, while AI surfaces retain
      // only design-critical programmed structures.
      && hasCurrentParkGroundSurface(z)
      && hasLiveProgrammedParkGeometry(z)),
    [zones],
  );

  return (
    <>
      {parkZones.map((zone) => (
        <ParkKitInstance key={zone.id} zone={zone} fallbackTerrainHeight={terrainHeight} />
      ))}
    </>
  );
}
