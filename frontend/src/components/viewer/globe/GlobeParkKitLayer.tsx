import { GlobeParkTrioPilot } from './GlobeParkTrioPilot';
import { isParkTrio, parkTrioLayout } from './parkTrioLayout';
/**
 * GlobeParkKitLayer — mounts only fixed, programmed park structures in the
 * editable Google Tiles scene, including deterministic live canopy and
 * seating. Public Realm LEGO families use fixed-dimension procedural
 * playground, pavilion and shade assemblies, so a missing GLB or disabled
 * asset endpoint can never leave an authored activity pad empty.
 *
 * Placement is seeded by zone.id — orbiting, re-selecting, or reloading
 * never reshuffles a park. renderOrder 145: under placed GLBs (150), above
 * road detail (122-130).
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
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import {
  getObjectFilteredTerrainHeight,
  isPlausibleTerrainAnchor,
  resolvePublicRealmGroundAnchor,
  resolveZoneTerrainHeight,
} from './globeTerrainUtils';
import { PARK_KIT_MANIFEST } from '@/data/parkKitManifest';
import {
  computeParkPlacements,
  resolveContainedParkProgramAnchor,
  resolveParkRecipeForZone,
  type ParkPropId,
  type PropPlacement,
} from './parkScatter';
import {
  JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M,
  WETLAND_BOARDWALK_PATHS,
  fitParkGroundGuides,
  resolveParkGuideDimensionsM,
  resolveParkGroundProfile,
  resolveParkPlacementGuides,
  resolveParkPlantingStructure,
  resolveParkSpecialtyStructureKind,
  shouldMountParkProgramFrame,
  type ParkGroundGuide,
  type ParkSpecialtyStructureKind,
} from './parkGroundProfiles';
import {
  GlobeLandscapeBenchStand,
  GlobeLandscapeTreeStand,
} from './GlobeLandscapeKit';
import {
  CIVIC_FOUNTAIN_ASSEMBLY_SPEC,
  PARK_PROGRAM_MODULE_SPEC,
  isExecutableParkLegoFamily,
  resolveParkDressingAppearance,
  resolveParkDressingFamily,
  resolveParkLegoAppearance,
  resolveParkProgramAnchorLayout,
  type ParkLegoAppearance,
  type ParkLegoFamilyId,
  type ParkLegoPalette,
} from './parkLegoFamilies';
import {
  hasCurrentParkGroundSurface,
  shouldDeferParkFinishingProp,
  shouldRenderLiveParkProp,
} from './parkGroundTexture';
import {
  direct3DInstanceUserData,
  direct3DZoneInstanceDescriptor,
} from './direct3dCapture';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { derivedParkAccessGuides, getDerivedParkAccess, type ParkAccessConnection } from './parkAccessConnections';
import { buildParkAccessBridgeGeometry } from './parkAccessBridgeGeometry';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { useParkGround } from './useParkGround';
import { createSharedGroundTriangulation, type SharedGroundTriangulation } from './sharedGroundGeometry';
import { GlobeNeighborhoodParkPilot } from './GlobeNeighborhoodParkPilot';
import { isNeighborhoodParkPilot, neighborhoodParkLayoutForZone } from './neighborhoodParkLayout';
import {
  parkTerrainSampleOffset,
  selectBudgetedLiveParkZones,
} from './parkDetailLod';
import {
  buildParkMicrodetailFamily,
  resolveParkMicrodetailGuideKind,
  type ParkMicrodetailGuide,
  type ParkMicrodetailPlacement,
} from './parkMicrodetailFamilies';
import { GlobeParkMicrodetailInstances } from './GlobeParkMicrodetailInstances';
import { computeParkProgramAssetPlacements } from './parkProgramAssets';
import {
  fitTerrainContactPlane,
  resolveTerrainContactElevation,
  samplePlaneOffset,
  type TerrainContactSample,
  type TerrainContactPlane,
} from './terrainContactProfile';
import {
  buildGreenwayGatewayBollardAnchors,
  buildParkSpecialtyTerrainAnchors,
  parkSpecialtyGuideRoute,
  resolveStormwaterInfrastructureGuides,
} from './parkSpecialtyGeometry';
import {
  resolveParkBenchStyle,
  resolveParkTreeVariant,
  type PublicRealmBenchStyle,
} from './publicRealmPropPalettes';
import { GlobeCricketGroundAssembly } from './GlobeCricketGroundAssembly';
import { GlobeSkateParkAssembly } from './GlobeSkateParkAssembly';
import {
  GlobeArchetypeOwnedParkAssembly,
  GlobeRegulationParkAssembly,
  type RegulationParkFamilyId,
} from './GlobeArchetypeOwnedParkAssembly';
import { GlobeParkBatch5Assembly } from './GlobeParkBatch5Assembly';
import { GlobeNeighborhoodParkV0StickerAssembly } from './GlobeNeighborhoodParkV0StickerAssembly';

const DEG_TO_RAD = Math.PI / 180;
const RENDER_ORDER_PROPS = 145;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;
const INSTANCES_PER_BATCH = 25;
const MAX_SAMPLE_PASSES = 3;

interface LocalParkProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
  points: Array<{ x: number; y: number }>;
  normalizedRing: Array<[number, number]>;
}

function buildLocalParkProgramFrame(
  coordinates: number[][],
  centroid: { lng: number; lat: number },
): LocalParkProgramFrame {
  const mPerLon = metersPerDegLon(centroid.lat);
  const points = coordinates.map(([lng, lat]) => ({
    x: (lng - centroid.lng) * mPerLon,
    y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
  }));
  const minX = Math.min(...points.map(({ x }) => x));
  const maxX = Math.max(...points.map(({ x }) => x));
  const minY = Math.min(...points.map(({ y }) => y));
  const maxY = Math.max(...points.map(({ y }) => y));
  const width = Math.max(0.01, maxX - minX);
  const height = Math.max(0.01, maxY - minY);
  return {
    minX,
    maxX,
    minY,
    maxY,
    width,
    height,
    points,
    normalizedRing: points.map(({ x, y }) => [
      (x - minX) / width,
      (maxY - y) / height,
    ]),
  };
}

function guideCenter(
  guide: ParkGroundGuide,
  frame: LocalParkProgramFrame,
): { x: number; y: number } {
  return {
    x: frame.minX + frame.width * guide.x,
    y: frame.maxY - frame.height * guide.y,
  };
}

function ellipseGuidePoints(
  guide: ParkGroundGuide,
  frame: LocalParkProgramFrame,
  segments = 20,
): Array<{ x: number; y: number }> {
  const center = guideCenter(guide, frame);
  const dimensions = resolveParkGuideDimensionsM(guide, frame);
  const angle = -((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return Array.from({ length: segments }, (_, index) => {
    const theta = (index / segments) * Math.PI * 2;
    const dx = Math.cos(theta) * dimensions.width / 2;
    const dy = Math.sin(theta) * dimensions.height / 2;
    return { x: center.x + dx * cos - dy * sin, y: center.y + dx * sin + dy * cos };
  });
}

function lineGuidePoints(
  guide: ParkGroundGuide,
  frame: LocalParkProgramFrame,
): Array<{ x: number; y: number }> {
  if (guide.points && guide.points.length >= 2) {
    return guide.points.map(([x, y]) => ({
      x: frame.minX + frame.width * x,
      y: frame.maxY - frame.height * y,
    }));
  }
  if (guide.kind === 'path_loop') return ellipseGuidePoints(guide, frame, 28);
  const center = guideCenter(guide, frame);
  const dimensions = resolveParkGuideDimensionsM(guide, frame);
  const angle = -((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const length = Math.max(0.5, Math.hypot(dimensions.width, dimensions.height));
  const dx = Math.cos(angle) * length / 2;
  const dy = Math.sin(angle) * length / 2;
  return [{ x: center.x - dx, y: center.y - dy }, { x: center.x + dx, y: center.y + dy }];
}

function parkMicrodetailGuides(
  guides: ParkGroundGuide[],
  frame: LocalParkProgramFrame,
  familyId: ParkLegoFamilyId,
): ParkMicrodetailGuide[] {
  return guides.flatMap((guide): ParkMicrodetailGuide[] => {
    const guideKind = resolveParkMicrodetailGuideKind(familyId, guide.kind);
    const isLinear = ['line', 'axis', 'polyline', 'path_loop'].includes(guide.kind);
    if (guideKind && isLinear) {
      return [{
        kind: guideKind,
        points: lineGuidePoints(guide, frame),
        closed: guide.closed === true || guide.kind === 'path_loop',
        widthM: Math.max(0.5, guide.strokeWidthM ?? 2.4),
        bufferM: guideKind === 'circulation' ? 0.4 : 1.1,
      }];
    }
    if (!guideKind) return [];
    const points = guide.kind === 'ellipse' || guide.kind === 'track'
      ? ellipseGuidePoints(guide, frame)
      : (() => {
        const center = guideCenter(guide, frame);
        const dimensions = resolveParkGuideDimensionsM(guide, frame);
        const angle = -((guide.rotationDeg ?? 0) * Math.PI) / 180;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        return [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sx, sy]) => {
          const dx = sx * dimensions.width / 2;
          const dy = sy * dimensions.height / 2;
          return { x: center.x + dx * cos - dy * sin, y: center.y + dx * sin + dy * cos };
        });
      })();
    return [{
      kind: guideKind,
      points,
      closed: true,
      isArea: true,
      bufferM: guideKind === 'water' ? 0.85 : 1.1,
    }];
  });
}

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
  preserveHorizontalOrigin,
  placements,
  centroid,
  instanceZ,
}: {
  url: string;
  targetHeight: number;
  preserveHorizontalOrigin: boolean;
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
    // Generic entourage is recentered. Exact program assets retain an
    // authored horizontal anchor such as a basketball post base.
    const norm = new THREE.Matrix4()
      .makeRotationX(Math.PI / 2)
      .multiply(new THREE.Matrix4().makeScale(normScale, normScale, normScale))
      .multiply(new THREE.Matrix4().makeTranslation(
        preserveHorizontalOrigin ? 0 : -center.x,
        -bbox.min.y,
        preserveHorizontalOrigin ? 0 : -center.z,
      ));

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
  }, [preserveHorizontalOrigin, scene, targetHeight]);

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
          (instanceZ?.[i] ?? 0) + (p.surfaceOffsetM ?? 0),
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
  appearance,
}: {
  propId: 'tree' | 'bench';
  placements: PropPlacement[];
  centroid: { lng: number; lat: number };
  instanceZ: number[] | null;
  appearance: ParkLegoAppearance | null;
}) {
  const mPerLon = metersPerDegLon(centroid.lat);
  const resolved = placements.map((placement, index) => ({
    x: (placement.lng - centroid.lng) * mPerLon,
    y: (placement.lat - centroid.lat) * METERS_PER_DEG_LAT,
    z: (instanceZ?.[index] ?? 0)
      + (propId === 'bench' ? PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS : 0),
    yawRad: placement.yawRad,
    scale: propId === 'tree' ? Math.max(0.72, placement.scale) : placement.scale,
    ...(propId === 'tree' && appearance
      ? { treeVariant: resolveParkTreeVariant(
        appearance.materialPattern,
        `${appearance.archetypeId}:${placement.lng.toFixed(7)}:${placement.lat.toFixed(7)}:${index}`,
      ) }
      : {}),
  }));
  if (propId === 'tree') {
    return <GlobeLandscapeTreeStand placements={resolved} renderOrder={RENDER_ORDER_PROPS} />;
  }
  if (!appearance) {
    return <GlobeLandscapeBenchStand placements={resolved} renderOrder={RENDER_ORDER_PROPS} />;
  }
  return (
    <>
      {resolved.map((placement, index) => (
        <ParkFamilyBench
          key={`${Math.round(placement.x * 10)}-${Math.round(placement.y * 10)}-${index}`}
          placement={placement}
          palette={appearance.palette}
          style={resolveParkBenchStyle(appearance.materialPattern)}
        />
      ))}
    </>
  );
}

function ParkFamilyBench({
  placement,
  palette,
  style,
}: {
  placement: { x: number; y: number; z: number; yawRad: number; scale: number };
  palette: ParkLegoPalette;
  style: PublicRealmBenchStyle;
}) {
  if (style === 'minimal_slab') {
    return (
      <group
        position={[placement.x, placement.y, placement.z]}
        rotation={[0, 0, placement.yawRad]}
        scale={[placement.scale, placement.scale, placement.scale]}
        renderOrder={RENDER_ORDER_PROPS}
      >
        <mesh position={[0, 0, 0.48]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[1.95, 0.5, 0.14]} />
          <meshStandardMaterial color={palette.pavilionPad} roughness={0.9} />
        </mesh>
        {[-0.58, 0.58].map((legX) => (
          <mesh key={legX} position={[legX, 0, 0.24]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[0.18, 0.38, 0.48]} />
            <meshStandardMaterial color={palette.benchFrame} metalness={0.28} roughness={0.62} />
          </mesh>
        ))}
      </group>
    );
  }

  const hasBack = style !== 'backless_timber';
  const isHeritage = style === 'heritage_cast_iron';
  return (
    <group
      position={[placement.x, placement.y, placement.z]}
      rotation={[0, 0, placement.yawRad]}
      scale={[placement.scale, placement.scale, placement.scale]}
      renderOrder={RENDER_ORDER_PROPS}
    >
      {[-0.20, -0.10, 0, 0.10, 0.20].map((slatY) => (
        <mesh key={`seat-${slatY}`} position={[0, slatY, 0.48]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[1.86, 0.074, 0.055]} />
          <meshStandardMaterial color={palette.benchSeat} roughness={0.82} />
        </mesh>
      ))}
      {hasBack && [0.68, 0.81, 0.94].map((slatZ) => (
        <mesh key={`back-${slatZ}`} position={[0, 0.255, slatZ]} rotation={[Math.PI / 18, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <boxGeometry args={[1.86, 0.055, 0.075]} />
          <meshStandardMaterial color={palette.timberDark} roughness={0.84} />
        </mesh>
      ))}
      {[-0.68, 0.68].map((legX) => (
        <group key={`frame-${legX}`}>
          <mesh position={[legX, 0, 0.25]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[0.075, 0.42, 0.5]} />
            <meshStandardMaterial color={palette.benchFrame} metalness={0.54} roughness={0.48} />
          </mesh>
          <mesh position={[legX, -0.28, 0.72]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[0.075, 0.075, 0.56]} />
            <meshStandardMaterial color={palette.benchFrame} metalness={0.54} roughness={0.48} />
          </mesh>
        </group>
      ))}
      {isHeritage && [-0.84, 0.84].map((armX) => (
        <group key={`arm-${armX}`}>
          <mesh position={[armX, -0.02, 0.72]} renderOrder={RENDER_ORDER_PROPS}>
            <cylinderGeometry args={[0.035, 0.035, 0.5, 8]} />
            <meshStandardMaterial color={palette.benchFrame} metalness={0.62} roughness={0.42} />
          </mesh>
          <mesh position={[armX, -0.12, 0.93]} rotation={[Math.PI / 2, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
            <torusGeometry args={[0.16, 0.035, 6, 12, Math.PI]} />
            <meshStandardMaterial color={palette.benchFrame} metalness={0.62} roughness={0.42} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function ShadeCanopy({
  palette,
  style,
}: {
  palette: ParkLegoPalette;
  style: ParkLegoAppearance['shadeStyle'];
}) {
  const spec = PARK_PROGRAM_MODULE_SPEC.shade;
  const radius = spec.spanM / 2;
  const canopyGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute([
      -radius, -radius * 0.62, spec.lowEdgeHeightM,
      radius, -radius * 0.52, spec.highEdgeHeightM,
      0, radius, spec.lowEdgeHeightM + 0.22,
    ], 3));
    geometry.setIndex([0, 1, 2]);
    geometry.computeVertexNormals();
    return geometry;
  }, [radius, spec.highEdgeHeightM, spec.lowEdgeHeightM]);
  useEffect(() => () => canopyGeometry.dispose(), [canopyGeometry]);

  if (style === 'timber_pergola') {
    return (
      <group>
        {[-radius * 0.72, radius * 0.72].flatMap((x) => (
          [-radius * 0.48, radius * 0.48].map((y) => (
            <mesh key={`${x}-${y}`} position={[x, y, spec.lowEdgeHeightM / 2]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.16, 0.16, spec.lowEdgeHeightM]} />
              <meshStandardMaterial color={palette.timberDark} roughness={0.86} />
            </mesh>
          ))
        ))}
        {Array.from({ length: 9 }, (_, index) => (
          <mesh
            key={index}
            position={[(index - 4) * 0.72, 0, spec.lowEdgeHeightM + 0.08]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <boxGeometry args={[0.12, radius * 1.35, 0.16]} />
            <meshStandardMaterial color={palette.timber} roughness={0.84} />
          </mesh>
        ))}
      </group>
    );
  }

  const polePoints = [
    [-radius, -radius * 0.62, spec.lowEdgeHeightM],
    [radius, -radius * 0.52, spec.highEdgeHeightM],
    [0, radius, spec.lowEdgeHeightM + 0.22],
  ] as const;
  return (
    <group>
      <mesh geometry={canopyGeometry} renderOrder={RENDER_ORDER_PROPS}>
        <meshStandardMaterial
          color={palette.shade}
          side={THREE.DoubleSide}
          roughness={style === 'thatched' ? 0.96 : 0.72}
          metalness={style === 'steel_canopy' ? 0.22 : 0}
        />
      </mesh>
      {polePoints.map(([x, y, height], index) => (
        <mesh key={index} position={[x, y, height / 2]} rotation={[Math.PI / 2, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <cylinderGeometry args={[0.075, 0.11, height, 10]} />
          <meshStandardMaterial color={palette.metal} metalness={0.48} roughness={0.52} />
        </mesh>
      ))}
    </group>
  );
}

function PlaygroundModule({
  placement,
  index,
  appearance,
}: {
  placement: { x: number; y: number; z: number; yawRad: number; scale: number };
  index: number;
  appearance: ParkLegoAppearance;
}) {
  const { palette } = appearance;
  const spec = PARK_PROGRAM_MODULE_SPEC.playground;
  const moduleKind = index % 3;
  const metalPlay = appearance.playgroundStyle === 'steel'
    || appearance.playgroundStyle === 'contemporary';
  return (
    <group
      position={[placement.x, placement.y, placement.z + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS]}
      rotation={[0, 0, placement.yawRad]}
      renderOrder={RENDER_ORDER_PROPS}
    >
      {moduleKind === 0 && (
        <>
          {[-0.82, 0.82].flatMap((x) => [-0.82, 0.82].map((y) => (
            <mesh key={`${x}-${y}`} position={[x, y, spec.towerHeightM / 2]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.14, 0.14, spec.towerHeightM]} />
              <meshStandardMaterial
                color={metalPlay ? palette.metal : palette.timberDark}
                metalness={metalPlay ? 0.38 : 0}
                roughness={metalPlay ? 0.52 : 0.82}
              />
            </mesh>
          )))}
          <mesh position={[0, 0, 1.45]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[...spec.towerDeckM]} />
            <meshStandardMaterial color={palette.timber} roughness={0.80} />
          </mesh>
          <mesh position={[1.45, 0, 0.82]} rotation={[0, -0.45, 0]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[spec.slideLengthM, 0.78, 0.16]} />
            <meshStandardMaterial color={palette.accent} metalness={0.12} roughness={0.42} />
          </mesh>
          {metalPlay ? (
            <mesh position={[0, 0, 2.76]} rotation={[0, 0, Math.PI / 12]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[2.75, 2.45, 0.16]} />
              <meshStandardMaterial color={palette.accentSecondary} metalness={0.18} roughness={0.54} />
            </mesh>
          ) : (
            <mesh position={[0, 0, 2.65]} rotation={[Math.PI / 2, 0, Math.PI / 4]} renderOrder={RENDER_ORDER_PROPS}>
              <coneGeometry args={[1.55, 1.05, 4]} />
              <meshStandardMaterial color={palette.accentSecondary} roughness={0.70} />
            </mesh>
          )}
        </>
      )}
      {moduleKind === 1 && (
        <>
          {[-1.65, 1.65].flatMap((x) => [-0.72, 0.72].map((y) => (
            <mesh key={`${x}-${y}`} position={[x, y, 1.22]} rotation={[0, x < 0 ? -0.15 : 0.15, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[0.12, 0.12, 2.55]} />
              <meshStandardMaterial color={palette.metal} metalness={0.44} roughness={0.52} />
            </mesh>
          )))}
          <mesh position={[0, 0, 2.45]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[spec.swingBayM[0], 0.14, 0.16]} />
            <meshStandardMaterial color={palette.metal} metalness={0.44} roughness={0.52} />
          </mesh>
          {[-0.72, 0.72].map((seatX) => (
            <group key={seatX}>
              {[-0.28, 0.28].map((chainY) => (
                <mesh key={chainY} position={[seatX, chainY, 1.53]} renderOrder={RENDER_ORDER_PROPS}>
                  <boxGeometry args={[0.025, 0.025, 1.70]} />
                  <meshStandardMaterial color={palette.metal} metalness={0.62} roughness={0.42} />
                </mesh>
              ))}
              <mesh position={[seatX, 0, 0.68]} renderOrder={RENDER_ORDER_PROPS}>
                <boxGeometry args={[0.52, 0.62, 0.09]} />
                <meshStandardMaterial color={palette.accent} roughness={0.64} />
              </mesh>
            </group>
          ))}
        </>
      )}
      {moduleKind === 2 && (
        <>
          <mesh position={[0, 0, 1.20]} renderOrder={RENDER_ORDER_PROPS}>
            <icosahedronGeometry args={[1.55, 1]} />
            <meshStandardMaterial color={palette.accentSecondary} wireframe metalness={0.25} roughness={0.58} />
          </mesh>
          {[-2.0, -1.1, 1.1, 2.0].map((x, step) => (
            <mesh key={x} position={[x, 1.65, 0.18 + (step % 2) * 0.08]} rotation={[Math.PI / 2, 0, 0]} renderOrder={RENDER_ORDER_PROPS}>
              <cylinderGeometry args={[0.34, 0.42, 0.34 + (step % 2) * 0.16, 10]} />
              <meshStandardMaterial color={palette.timber} roughness={0.94} />
            </mesh>
          ))}
        </>
      )}
    </group>
  );
}

function ProceduralPlayground({
  placements,
  appearance,
}: {
  placements: Array<{ x: number; y: number; z: number; yawRad: number; scale: number }>;
  appearance: ParkLegoAppearance;
}) {
  if (placements.length === 0) return null;
  const center = placements.reduce(
    (sum, placement) => ({ x: sum.x + placement.x, y: sum.y + placement.y, z: sum.z + placement.z }),
    { x: 0, y: 0, z: 0 },
  );
  center.x /= placements.length;
  center.y /= placements.length;
  center.z /= placements.length;
  return (
    <group renderOrder={RENDER_ORDER_PROPS}>
      {placements.map((placement, index) => (
        <PlaygroundModule key={index} placement={placement} index={index} appearance={appearance} />
      ))}
      <group position={[center.x, center.y, center.z + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS]}>
        <ShadeCanopy palette={appearance.palette} style={appearance.shadeStyle} />
      </group>
    </group>
  );
}

function ProceduralPavilion({
  placements,
  appearance,
}: {
  placements: Array<{ x: number; y: number; z: number; yawRad: number; scale: number }>;
  appearance: ParkLegoAppearance;
}) {
  const spec = PARK_PROGRAM_MODULE_SPEC.pavilion;
  const { palette } = appearance;
  return (
    <>
      {placements.map((placement, index) => (
        <group
          key={index}
          position={[placement.x, placement.y, placement.z + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS]}
          rotation={[0, 0, placement.yawRad]}
          renderOrder={RENDER_ORDER_PROPS}
        >
          {[-1, 1].flatMap((sx) => [-1, 1].map((sy) => (
            <mesh
              key={`${sx}-${sy}`}
              position={[sx * (spec.widthM / 2 - 0.38), sy * (spec.depthM / 2 - 0.38), spec.clearHeightM / 2]}
              renderOrder={RENDER_ORDER_PROPS}
            >
              <boxGeometry args={[0.20, 0.20, spec.clearHeightM]} />
              <meshStandardMaterial
                color={appearance.shadeStyle === 'steel_canopy' ? palette.metal : palette.timberDark}
                metalness={appearance.shadeStyle === 'steel_canopy' ? 0.42 : 0}
                roughness={0.68}
              />
            </mesh>
          )))}
          <mesh position={[0, 0, spec.clearHeightM + spec.roofHeightM * 0.42]} rotation={[Math.PI / 2, 0, Math.PI / 4]} renderOrder={RENDER_ORDER_PROPS}>
            <coneGeometry args={[4.25, spec.roofHeightM, 4]} />
            <meshStandardMaterial
              color={palette.pavilionRoof}
              roughness={appearance.shadeStyle === 'thatched' ? 0.98 : 0.76}
              metalness={appearance.shadeStyle === 'steel_canopy' ? 0.24 : 0}
            />
          </mesh>
          <mesh position={[0, 0, 0.74]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[2.5, 0.85, 0.12]} />
            <meshStandardMaterial color={palette.timber} roughness={0.84} />
          </mesh>
          {[-0.86, 0.86].map((seatY) => (
            <mesh key={seatY} position={[0, seatY, 0.48]} renderOrder={RENDER_ORDER_PROPS}>
              <boxGeometry args={[2.6, 0.38, 0.12]} />
              <meshStandardMaterial color={palette.benchSeat} roughness={0.86} />
            </mesh>
          ))}
        </group>
      ))}
    </>
  );
}

function ProceduralParkProgramProps({
  propId,
  placements,
  centroid,
  instanceZ,
  appearance,
}: {
  propId: 'playground' | 'pavilion';
  placements: PropPlacement[];
  centroid: { lng: number; lat: number };
  instanceZ: number[] | null;
  appearance: ParkLegoAppearance;
}) {
  const mPerLon = metersPerDegLon(centroid.lat);
  const resolved = placements.map((placement, index) => ({
    x: (placement.lng - centroid.lng) * mPerLon,
    y: (placement.lat - centroid.lat) * METERS_PER_DEG_LAT,
    z: instanceZ?.[index] ?? 0,
    yawRad: placement.yawRad,
    scale: placement.scale,
  }));
  return propId === 'playground'
    ? <ProceduralPlayground placements={resolved} appearance={appearance} />
    : <ProceduralPavilion placements={resolved} appearance={appearance} />;
}

/** Small deterministic structures that are part of an archetype's spatial
 * program but do not yet warrant a fetched GLB kit asset. */
function ParkSpecialtyStructures({
  structureKind,
  zone,
  centroid,
  terrainPlane,
  sharedTerrainZ,
  groundGrid,
}: {
  structureKind: ParkSpecialtyStructureKind | null;
  zone: SiteZone;
  centroid: { lng: number; lat: number };
  terrainPlane: TerrainContactPlane | null;
  sharedTerrainZ?: (x: number, y: number) => number | null;
  groundGrid?: SharedGroundTriangulation | null;
}) {
  const coordinates = zone.coordinates;
  const programFrame = useMemo(
    () => buildLocalParkProgramFrame(coordinates, centroid),
    [centroid, coordinates],
  );

  const programGuideFit = useMemo(() => fitParkGroundGuides(
    resolveParkGroundProfile(zone).guides,
    { width: programFrame.width, height: programFrame.height },
    programFrame.normalizedRing,
  ), [programFrame, zone]);
  const fittedProgramGuides = programGuideFit.guides;
  const placementProgramGuides = useMemo(
    () => resolveParkPlacementGuides(programGuideFit),
    [programGuideFit],
  );

  const terrainZ = useCallback((x: number, y: number): number => {
    if (sharedTerrainZ) {
      const height = sharedTerrainZ(x, y);
      // An older specialty assembly can request an extra support outside its
      // fitted anchors. Its boundary suppresses that assembly until covered;
      // never invent a zero-height support on a retained site.
      if (height === null || !Number.isFinite(height)) throw new Error('Park structure extends beyond the measured site ground.');
      return height;
    }
    return terrainPlane ? terrainPlane.originZ + samplePlaneOffset(terrainPlane, x, y) : 0;
  }, [sharedTerrainZ, terrainPlane]);

  if (structureKind === 'park_trio_assembly') return <SilentKitBoundary fallback={null}><Suspense fallback={null}><GlobeParkTrioPilot zone={zone} centroid={centroid} terrainZ={terrainZ} groundGrid={groundGrid}/></Suspense></SilentKitBoundary>;

  if (structureKind === 'skate_park_v0_assembly') {
    return (
      <SilentKitBoundary fallback={null}>
        <Suspense fallback={null}>
          <GlobeSkateParkAssembly boundary={programFrame.points} terrainZ={terrainZ} />
        </Suspense>
      </SilentKitBoundary>
    );
  }

  if (structureKind === 'neighborhood_park_v0_sticker_assembly') {
    return (
      <SilentKitBoundary fallback={null}>
        <Suspense fallback={null}>
          {isNeighborhoodParkPilot(zone) ? <GlobeNeighborhoodParkPilot
            zone={zone} centroid={centroid} terrainZ={terrainZ} groundGrid={groundGrid}
          /> : <GlobeNeighborhoodParkV0StickerAssembly
            boundary={programFrame.points}
            terrainZ={terrainZ}
          />}
        </Suspense>
      </SilentKitBoundary>
    );
  }

  const profileFamilyId = resolveParkGroundProfile(zone).legoFamilyId;
  if (structureKind === 'batch5_archetype_assembly' && profileFamilyId) {
    return (
      <GlobeParkBatch5Assembly
        familyId={profileFamilyId}
        guides={fittedProgramGuides}
        frame={programFrame}
        terrainZ={terrainZ}
      />
    );
  }
  const regulationFamily: RegulationParkFamilyId | null = structureKind === 'basketball_court_assembly'
    ? 'park_basketball_court_v0'
    : structureKind === 'tennis_cluster_v0_assembly'
      ? 'park_tennis_cluster_v0'
    : structureKind === 'caged_soccer_v0_assembly'
      ? 'park_caged_soccer_v0'
      : structureKind === 'sports_field_furniture' && profileFamilyId === 'park_athletics_fields_v0'
        ? 'park_athletics_fields_v0'
        : null;
  if (regulationFamily) {
    const guideKind = regulationFamily === 'park_basketball_court_v0' ? 'basketball_court'
      : regulationFamily === 'park_tennis_cluster_v0' ? 'tennis_court' : 'soccer_field';
    const modules = fittedProgramGuides
      .filter((guide) => guide.kind === guideKind)
      .map((guide) => {
        const dimensions = resolveParkGuideDimensionsM(guide, {
          width: programFrame.width,
          height: programFrame.height,
        });
        return {
          x: programFrame.minX + programFrame.width * guide.x,
          y: programFrame.maxY - programFrame.height * guide.y,
          rotationZ: -((guide.rotationDeg ?? 0) * Math.PI) / 180,
          widthM: dimensions.width,
          depthM: dimensions.height,
        };
      });
    return (
      <SilentKitBoundary fallback={null}>
        <Suspense fallback={null}>
          <GlobeRegulationParkAssembly
            familyId={regulationFamily}
            modules={modules}
            terrainZ={terrainZ}
            variantId={resolveParkGroundProfile(zone).variantId ?? String(
              (zone.properties as Record<string, unknown> | undefined)?.green_space_selected_variant_id ?? '',
            )}
          />
        </Suspense>
      </SilentKitBoundary>
    );
  }

  const exactFamily = structureKind === 'inclusive_playground_v0_assembly' ? 'park_inclusive_playground_v0'
    : structureKind === 'dog_park_v0_assembly' ? 'park_dog_archetype_v0'
      : structureKind === 'splash_pad_v0_assembly' ? 'park_splash_pad_v0'
        : structureKind === 'community_garden_v0_assembly' ? 'park_community_garden_v0'
          : structureKind === 'nature_play_v0_assembly' ? 'park_nature_play_v0'
              : structureKind === 'pump_track_v0_assembly' ? 'park_pump_track_v0'
                : structureKind === 'outdoor_fitness_v0_assembly' ? 'park_outdoor_fitness_v0'
                  : structureKind === 'memorial_garden_v0_assembly' ? 'park_memorial_garden_v0'
                    : structureKind === 'archetype_full_park_assembly'
                      && profileFamilyId === 'park_pickleball_community_v1' ? 'park_pickleball_community_v1'
                    : structureKind === 'archetype_full_park_assembly'
                      && profileFamilyId === 'park_track_oval_school_v2' ? 'park_track_oval_school_v2'
                    : structureKind === 'archetype_full_park_assembly'
                      && profileFamilyId === 'park_baseball_club_hub_v1' ? 'park_baseball_club_hub_v1'
                    : structureKind === 'archetype_full_park_assembly'
                      && profileFamilyId === 'park_cricket_village_green_v0' ? 'park_cricket_village_green_v0'
                    : structureKind === 'archetype_full_park_assembly'
                      && profileFamilyId === 'park_sports_complex_tournament_v0' ? 'park_sports_complex_tournament_v0'
                    : null;
  if (exactFamily) {
    return (
      <SilentKitBoundary fallback={null}>
        <Suspense fallback={null}>
          <GlobeArchetypeOwnedParkAssembly familyId={exactFamily} boundary={programFrame.points} terrainZ={terrainZ} />
        </Suspense>
      </SilentKitBoundary>
    );
  }

  if (structureKind === 'civic_fountain_assembly') {
    const spec = CIVIC_FOUNTAIN_ASSEMBLY_SPEC;
    const anchor = resolveContainedParkProgramAnchor(
      programFrame.points.map(({ x, y }) => [x, y]),
      [0.5, 0.5],
      spec.wholeElementClearanceM,
    );
    if (!anchor) return null;
    return (
      <group
        position={[
          anchor.x,
          anchor.y,
          PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + terrainZ(anchor.x, anchor.y),
        ]}
        renderOrder={RENDER_ORDER_PROPS}
      >
        <mesh
          position={[0, 0, spec.rimHeightM / 2]}
          rotation={[Math.PI / 2, 0, 0]}
          renderOrder={RENDER_ORDER_PROPS}
        >
          <cylinderGeometry args={[
            spec.outerRadiusM,
            spec.outerRadiusM,
            spec.rimHeightM,
            48,
          ]} />
          <meshStandardMaterial color="#aaa399" roughness={0.88} metalness={0.02} />
        </mesh>
        <mesh position={[0, 0, spec.waterHeightM + 0.015]} renderOrder={RENDER_ORDER_PROPS + 1}>
          <circleGeometry args={[spec.waterRadiusM, 48]} />
          <meshPhysicalMaterial
            color="#4f8890"
            transparent
            opacity={0.82}
            roughness={0.18}
            metalness={0.02}
            depthWrite
          />
        </mesh>
        <mesh
          position={[0, 0, spec.rimHeightM + 0.012]}
          renderOrder={RENDER_ORDER_PROPS + 2}
        >
          <ringGeometry args={[spec.waterRadiusM, spec.outerRadiusM, 48]} />
          <meshStandardMaterial color="#c3bdb2" roughness={0.82} metalness={0.02} />
        </mesh>
        <mesh
          position={[0, 0, spec.centerPlinthHeightM / 2]}
          rotation={[Math.PI / 2, 0, 0]}
          renderOrder={RENDER_ORDER_PROPS + 2}
        >
          <cylinderGeometry args={[
            spec.centerPlinthRadiusM,
            spec.centerPlinthRadiusM * 1.08,
            spec.centerPlinthHeightM,
            24,
          ]} />
          <meshStandardMaterial color="#9e978d" roughness={0.84} />
        </mesh>
        {[0, Math.PI / 2, Math.PI, Math.PI * 1.5].map((angle) => (
          <mesh
            key={angle}
            position={[
              Math.cos(angle) * 2.15,
              Math.sin(angle) * 2.15,
              spec.waterHeightM + 0.42,
            ]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_PROPS + 3}
          >
            <cylinderGeometry args={[0.035, 0.055, 0.82, 8]} />
            <meshPhysicalMaterial color="#c5e5e7" transparent opacity={0.68} roughness={0.08} />
          </mesh>
        ))}
      </group>
    );
  }

  if (structureKind === 'greenway_edge_assembly') {
    const trailGuide = fittedProgramGuides.find((guide) => (
      guide.kind === 'axis'
      || guide.kind === 'line'
      || guide.kind === 'polyline'
      || guide.kind === 'path_loop'
    ));
    if (!trailGuide) return null;
    const route = parkSpecialtyGuideRoute(trailGuide, programFrame);
    const clearHalfWidth = Math.max(1.75, (trailGuide.strokeWidthM ?? 3.5) / 2);
    const gatewayBollards = buildGreenwayGatewayBollardAnchors(
      route,
      clearHalfWidth * 2,
    );
    const segments = route.slice(1).map((to, index) => ({ from: route[index], to }));
    const postPoints = segments.flatMap(({ from, to }, segmentIndex) => {
      const length = Math.hypot(to.x - from.x, to.y - from.y);
      const count = Math.max(2, Math.min(10, Math.ceil(length / 5.5)));
      return Array.from({ length: count }, (_, index) => ({
        x: from.x + (to.x - from.x) * (index / Math.max(1, count - 1)),
        y: from.y + (to.y - from.y) * (index / Math.max(1, count - 1)),
        segmentIndex,
      }));
    });
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {segments.flatMap(({ from, to }, segmentIndex) => {
          const dx = to.x - from.x;
          const dy = to.y - from.y;
          const length = Math.hypot(dx, dy) || 1;
          const nx = -dy / length;
          const ny = dx / length;
          const yaw = Math.atan2(dy, dx);
          return [-1, 1].map((side) => (
            (() => {
              const x = (from.x + to.x) / 2 + nx * side * (clearHalfWidth + 0.75);
              const y = (from.y + to.y) / 2 + ny * side * (clearHalfWidth + 0.75);
              return (
                <mesh
                  key={`greenway-edge-${segmentIndex}-${side}`}
                  position={[
                    x,
                    y,
                    terrainZ(x, y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + 0.72,
                  ]}
                  rotation={[0, 0, yaw]}
                  renderOrder={RENDER_ORDER_PROPS}
                >
                  <boxGeometry args={[length, 0.11, 0.13]} />
                  <meshStandardMaterial color="#655340" roughness={0.86} metalness={0.04} />
                </mesh>
              );
            })()
          ));
        })}
        {postPoints.flatMap((point, index) => {
          const segment = segments[point.segmentIndex];
          const length = Math.hypot(segment.to.x - segment.from.x, segment.to.y - segment.from.y) || 1;
          const nx = -(segment.to.y - segment.from.y) / length;
          const ny = (segment.to.x - segment.from.x) / length;
          return [-1, 1].map((side) => (
            (() => {
              const x = point.x + nx * side * (clearHalfWidth + 0.75);
              const y = point.y + ny * side * (clearHalfWidth + 0.75);
              return (
                <mesh
                  key={`greenway-post-${index}-${side}`}
                  position={[
                    x,
                    y,
                    terrainZ(x, y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + 0.38,
                  ]}
                  rotation={[Math.PI / 2, 0, 0]}
                  renderOrder={RENDER_ORDER_PROPS}
                >
                  <cylinderGeometry args={[0.075, 0.095, 0.76, 8]} />
                  <meshStandardMaterial color="#544638" roughness={0.9} />
                </mesh>
              );
            })()
          ));
        })}
        {gatewayBollards.map((anchor, index) => (
          <group
            key={`greenway-gateway-${index}`}
            position={[
              anchor.x,
              anchor.y,
              terrainZ(anchor.x, anchor.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
            ]}
          >
              <mesh position={[0, 0, 0.48]} renderOrder={RENDER_ORDER_PROPS + 1}>
                <cylinderGeometry args={[0.07, 0.09, 0.96, 10]} />
                <meshStandardMaterial color="#3e4745" metalness={0.34} roughness={0.58} />
              </mesh>
          </group>
        ))}
      </group>
    );
  }

  if (structureKind === 'pond_dock_assembly' || structureKind === 'riparian_bridge_assembly') {
    const authoredLine = fittedProgramGuides.find((guide) => guide.kind === 'line');
    if (!authoredLine) return null;
    const route = parkSpecialtyGuideRoute(authoredLine, programFrame);
    const from = route[0];
    const to = route[route.length - 1];
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const length = Math.max(2, Math.hypot(dx, dy));
    const x = (from.x + to.x) / 2;
    const y = (from.y + to.y) / 2;
    const width = structureKind === 'pond_dock_assembly' ? 2.4 : 2.2;
    const yaw = Math.atan2(dy, dx);
    const rail = structureKind === 'riparian_bridge_assembly';
    return (
      <group position={[x, y, terrainZ(x, y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + 0.32]} rotation={[0, 0, yaw]}>
        <mesh renderOrder={RENDER_ORDER_PROPS + 2}>
          <boxGeometry args={[length, width, 0.24]} />
          <meshStandardMaterial color="#8b6846" roughness={0.88} />
        </mesh>
        <mesh position={[0, 0, 0.13]} renderOrder={RENDER_ORDER_PROPS + 3}>
          <planeGeometry args={[length - 0.15, width - 0.10, Math.max(2, Math.ceil(length / 0.45)), 1]} />
          <meshStandardMaterial color="#ad8258" wireframe roughness={0.94} />
        </mesh>
        {Array.from({ length: Math.max(3, Math.ceil(length / 3.2)) }, (_, index) => (
          [-1, 1].map((side) => {
            const along = -length / 2 + (index / Math.max(1, Math.ceil(length / 3.2) - 1)) * length;
            return (
              <mesh key={`${index}-${side}`} position={[along, side * width * 0.43, -0.25]} renderOrder={RENDER_ORDER_PROPS + 1}>
                <cylinderGeometry args={[0.09, 0.12, 1.15, 8]} />
                <meshStandardMaterial color="#5f4935" roughness={0.94} />
              </mesh>
            );
          })
        ))}
        {rail && [-1, 1].map((side) => (
          <group key={side} position={[0, side * width * 0.48, 0.72]}>
            <mesh renderOrder={RENDER_ORDER_PROPS + 3}>
              <boxGeometry args={[length, 0.08, 0.10]} />
              <meshStandardMaterial color="#684b32" roughness={0.9} />
            </mesh>
            {[-length / 2, 0, length / 2].map((along) => (
              <mesh key={along} position={[along, 0, -0.34]} renderOrder={RENDER_ORDER_PROPS + 2}>
                <boxGeometry args={[0.09, 0.09, 0.78]} />
                <meshStandardMaterial color="#684b32" roughness={0.9} />
              </mesh>
            ))}
          </group>
        ))}
      </group>
    );
  }

  if (structureKind === 'reservoir_edge_assembly') {
    const water = fittedProgramGuides.find((guide) => guide.kind === 'rectangle' || guide.kind === 'rounded_rectangle');
    const dam = fittedProgramGuides.find((guide) => guide.kind === 'line');
    if (!water || !dam) return null;
    const waterCenter = guideCenter(water, programFrame);
    const waterSize = resolveParkGuideDimensionsM(water, programFrame);
    const damRoute = parkSpecialtyGuideRoute(dam, programFrame);
    const from = damRoute[0];
    const to = damRoute[damRoute.length - 1];
    const length = Math.max(8, Math.hypot(to.x - from.x, to.y - from.y));
    const x = (from.x + to.x) / 2;
    const y = (from.y + to.y) / 2;
    const yaw = Math.atan2(to.y - from.y, to.x - from.x);
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        <mesh position={[waterCenter.x, waterCenter.y, terrainZ(waterCenter.x, waterCenter.y) + 0.025]} renderOrder={RENDER_ORDER_PROPS + 1}>
          <planeGeometry args={[waterSize.width, waterSize.height]} />
          <meshPhysicalMaterial color="#315f6a" roughness={0.18} transparent opacity={0.84} />
        </mesh>
        <group position={[x, y, terrainZ(x, y) + 0.48]} rotation={[0, 0, yaw]}>
          <mesh renderOrder={RENDER_ORDER_PROPS + 2}>
            <boxGeometry args={[length, 1.8, 0.96]} />
            <meshStandardMaterial color="#92928c" roughness={0.9} />
          </mesh>
          <mesh position={[0, -1.15, 0.22]} renderOrder={RENDER_ORDER_PROPS + 3}>
            <boxGeometry args={[Math.min(8, length * 0.2), 1.0, 0.42]} />
            <meshStandardMaterial color="#a7a49b" roughness={0.86} />
          </mesh>
          {Array.from({ length: Math.max(4, Math.ceil(length / 6)) }, (_, index) => {
            const along = -length / 2 + index * (length / Math.max(1, Math.ceil(length / 6) - 1));
            return <mesh key={index} position={[along, 0.85, 1.15]}><boxGeometry args={[0.08, 0.08, 1.4]} /><meshStandardMaterial color="#4e5656" metalness={0.5} roughness={0.55} /></mesh>;
          })}
          <mesh position={[0, 0.85, 1.78]}><boxGeometry args={[length, 0.07, 0.07]} /><meshStandardMaterial color="#4e5656" metalness={0.5} roughness={0.55} /></mesh>
        </group>
      </group>
    );
  }

  if (structureKind === 'amphitheater_lawn_assembly') {
    const tiers = fittedProgramGuides.filter((guide) => guide.kind === 'ellipse').slice(0, 4);
    const stage = fittedProgramGuides.find((guide) => guide.kind === 'rectangle');
    if (tiers.length === 0 || !stage) return null;
    const stageCenter = guideCenter(stage, programFrame);
    const stageSize = resolveParkGuideDimensionsM(stage, programFrame);
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {tiers.map((tier, index) => {
          const center = guideCenter(tier, programFrame);
          const dimensions = resolveParkGuideDimensionsM(tier, programFrame);
          return (
            <mesh key={index} position={[center.x, center.y, terrainZ(center.x, center.y) + 0.06 + index * 0.18]} scale={[dimensions.width / 2, dimensions.height / 2, 1]} renderOrder={RENDER_ORDER_PROPS + index}>
              <ringGeometry args={[0.92, 1, 64]} />
              <meshStandardMaterial color={index % 2 === 0 ? '#657f4f' : '#75915a'} roughness={0.98} />
            </mesh>
          );
        })}
        <mesh position={[stageCenter.x, stageCenter.y, terrainZ(stageCenter.x, stageCenter.y) + 0.28]} renderOrder={RENDER_ORDER_PROPS + 5}>
          <boxGeometry args={[stageSize.width, stageSize.height, 0.52]} />
          <meshStandardMaterial color="#8b623e" roughness={0.86} />
        </mesh>
      </group>
    );
  }

  if (structureKind === 'adventure_play_assembly') {
    const pads = fittedProgramGuides.filter((guide) => guide.kind === 'rounded_rectangle');
    if (pads.length < 2) return null;
    const towerPad = guideCenter(pads[0], programFrame);
    const swingPad = guideCenter(pads[1], programFrame);
    const towerOffsets = [[-5, -3, 2.6], [0, 2, 3.5], [5, -1, 3.0]] as const;
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        {towerOffsets.map(([offsetX, offsetY, deckHeight], index) => (
          <group key={index} position={[towerPad.x + offsetX, towerPad.y + offsetY, terrainZ(towerPad.x + offsetX, towerPad.y + offsetY)]}>
            {[-1.2, 1.2].flatMap((x) => [-1.2, 1.2].map((y) => <mesh key={`${x}-${y}`} position={[x, y, deckHeight / 2]}><cylinderGeometry args={[0.16, 0.22, deckHeight, 9]} /><meshStandardMaterial color={index % 2 === 0 ? '#705841' : '#80664b'} roughness={0.94} /></mesh>))}
            <mesh position={[0, 0, deckHeight]}><boxGeometry args={[3.0, 3.0, 0.24]} /><meshStandardMaterial color="#8b6c4d" roughness={0.92} /></mesh>
            <mesh position={[0, 0, deckHeight + 1.25]} rotation={[0, 0, Math.PI / 4]}><coneGeometry args={[2.55, 1.2, 4]} /><meshStandardMaterial color="#67513d" roughness={0.95} /></mesh>
            <mesh position={[2.2, 0, deckHeight - 0.8]} rotation={[0, -0.52, 0]}><boxGeometry args={[4.8, 0.72, 0.18]} /><meshStandardMaterial color="#a9aaa5" metalness={0.48} roughness={0.44} /></mesh>
          </group>
        ))}
        <group position={[swingPad.x, swingPad.y, terrainZ(swingPad.x, swingPad.y)]}>
          {[-3.8, 3.8].map((x) => <mesh key={x} position={[x, 0, 2.3]} rotation={[0, 0, x < 0 ? -0.16 : 0.16]}><cylinderGeometry args={[0.16, 0.22, 4.7, 9]} /><meshStandardMaterial color="#705841" roughness={0.94} /></mesh>)}
          <mesh position={[0, 0, 4.5]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.16, 0.20, 8.2, 9]} /><meshStandardMaterial color="#705841" roughness={0.94} /></mesh>
          {[-2.2, 0, 2.2].map((x) => <group key={x}><mesh position={[x, 0, 3.0]}><boxGeometry args={[0.035, 0.035, 2.8]} /><meshStandardMaterial color="#4e4940" metalness={0.12} roughness={0.86} /></mesh><mesh position={[x, 0, 1.58]}><boxGeometry args={[0.7, 0.35, 0.10]} /><meshStandardMaterial color="#6d563f" roughness={0.92} /></mesh></group>)}
        </group>
        {[[-7, 6, 1.1], [7, 6, 0.9], [-8, -7, 0.75], [8, -6, 1.0]].map(([offsetX, offsetY, scale], index) => (
          <mesh key={index} position={[towerPad.x + offsetX, towerPad.y + offsetY, terrainZ(towerPad.x + offsetX, towerPad.y + offsetY) + scale * 0.34]} scale={[scale * 1.2, scale, scale * 0.72]} rotation={[index * 0.15, index * 0.09, index * 0.62]}>
            <dodecahedronGeometry args={[0.82, 0]} />
            <meshStandardMaterial color={index % 2 === 0 ? '#85847d' : '#9a9588'} roughness={0.98} />
          </mesh>
        ))}
      </group>
    );
  }

  if (structureKind === 'stormwater_control_assembly') {
    const waterGuide = fittedProgramGuides
      .filter((guide) => guide.kind === 'ellipse')
      .sort((left, right) => (right.width * right.height) - (left.width * left.height))[0];
    if (!waterGuide) return null;
    const waterCenter = guideCenter(waterGuide, programFrame);
    const waterDimensions = resolveParkGuideDimensionsM(waterGuide, programFrame);
    const centerX = waterCenter.x;
    const centerY = waterCenter.y;
    const radiusX = Math.max(2.5, waterDimensions.width / 2);
    const radiusY = Math.max(2.5, waterDimensions.height / 2);
    const edgeX = radiusX + 1.25;
    const infrastructure = resolveStormwaterInfrastructureGuides(
      fittedProgramGuides,
      programFrame,
    );
    const inlet = infrastructure?.inlet ?? {
      center: { x: centerX - edgeX, y: centerY },
      width: 1.25,
      height: 3.2,
      rotationRad: 0,
    };
    const outlet = infrastructure?.outlet ?? {
      center: { x: centerX + edgeX, y: centerY },
      width: 1.15,
      height: 4.2,
      rotationRad: 0,
    };
    const riprap = Array.from({ length: 14 }, (_, index) => {
      const column = index % 5;
      const row = Math.floor(index / 5);
      const localX = ((column / 4) - 0.5) * inlet.width * 0.78;
      const localY = ((row / 2) - 0.5) * inlet.height * 0.72
        + (column % 2 === 0 ? 0 : inlet.height * 0.06);
      const cos = Math.cos(inlet.rotationRad);
      const sin = Math.sin(inlet.rotationRad);
      return {
        x: inlet.center.x + localX * cos - localY * sin,
        y: inlet.center.y + localX * sin + localY * cos,
        scale: Math.min(0.72, 0.34 + (index % 4) * 0.08),
      };
    });
    return (
      <group renderOrder={RENDER_ORDER_PROPS}>
        <mesh
          position={[
            centerX,
            centerY,
            terrainZ(centerX, centerY) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + 0.012,
          ]}
          scale={[radiusX, radiusY, 1]}
          renderOrder={RENDER_ORDER_PROPS + 1}
        >
          <circleGeometry args={[1, 64]} />
          <meshPhysicalMaterial
            color="#416f78"
            transparent
            opacity={0.78}
            roughness={0.2}
            metalness={0.04}
            depthWrite
          />
        </mesh>
        <mesh
          position={[
            centerX,
            centerY,
            terrainZ(centerX, centerY) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS + 0.018,
          ]}
          scale={[radiusX + 1.15, radiusY + 1.15, 1]}
          renderOrder={RENDER_ORDER_PROPS}
        >
          <ringGeometry args={[0.88, 1, 64]} />
          <meshStandardMaterial color="#73865d" roughness={0.98} />
        </mesh>
        <group
          position={[
            inlet.center.x,
            inlet.center.y,
            terrainZ(inlet.center.x, inlet.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
          ]}
          rotation={[0, 0, inlet.rotationRad]}
        >
          <mesh position={[0, 0, 0.45]} renderOrder={RENDER_ORDER_PROPS + 2}>
            <boxGeometry args={[
              Math.max(0.75, Math.min(1.4, inlet.width * 0.26)),
              Math.max(1.2, inlet.height * 0.68),
              0.9,
            ]} />
            <meshStandardMaterial color="#858984" roughness={0.9} />
          </mesh>
          <mesh
            position={[Math.max(0.45, Math.min(0.85, inlet.width * 0.16)), 0, 0.43]}
            rotation={[0, Math.PI / 2, 0]}
            renderOrder={RENDER_ORDER_PROPS + 3}
          >
            <cylinderGeometry args={[0.36, 0.36, 0.55, 16]} />
            <meshStandardMaterial color="#30383a" metalness={0.48} roughness={0.5} />
          </mesh>
        </group>
        <group
          position={[
            outlet.center.x,
            outlet.center.y,
            terrainZ(outlet.center.x, outlet.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
          ]}
          rotation={[0, 0, outlet.rotationRad]}
        >
          <mesh position={[0, 0, 0.32]} renderOrder={RENDER_ORDER_PROPS + 2}>
            <boxGeometry args={[outlet.width, outlet.height, 0.64]} />
            <meshStandardMaterial color="#a29c91" roughness={0.9} />
          </mesh>
          <mesh position={[0, 0, 0.66]} renderOrder={RENDER_ORDER_PROPS + 3}>
            <boxGeometry args={[0.18, Math.max(0.8, outlet.height * 0.84), 0.16]} />
            <meshStandardMaterial color="#535b5c" metalness={0.38} roughness={0.56} />
          </mesh>
          <mesh position={[outlet.width / 2 + 0.55, 0, 1.15]} renderOrder={RENDER_ORDER_PROPS + 3}>
            <boxGeometry args={[0.10, 1.05, 2.3]} />
            <meshStandardMaterial color="#5f695f" roughness={0.82} />
          </mesh>
        </group>
        {riprap.map((stone, index) => (
          <mesh
            key={`stormwater-riprap-${index}`}
            position={[
              stone.x,
              stone.y,
              terrainZ(stone.x, stone.y)
                + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS
                + stone.scale * 0.35,
            ]}
            scale={[stone.scale * 1.2, stone.scale, stone.scale * 0.7]}
            rotation={[index * 0.21, index * 0.13, index * 0.47]}
            renderOrder={RENDER_ORDER_PROPS + 1}
          >
            <dodecahedronGeometry args={[0.75, 0]} />
            <meshStandardMaterial color={index % 3 === 0 ? '#7e807a' : '#96948b'} roughness={0.98} />
          </mesh>
        ))}
      </group>
    );
  }

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
          const x = (from.x + to.x) / 2;
          const y = (from.y + to.y) / 2;
          return (
            <group
              key={`wetland-boardwalk-${index}`}
              position={[x, y, terrainZ(x, y) + 0.28]}
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
        ].map(([normalizedX, normalizedY, width, depth], index) => {
          const x = programFrame.minX + programFrame.width * normalizedX;
          const y = programFrame.maxY - programFrame.height * normalizedY;
          return (
            <mesh
              key={`wetland-overlook-${index}`}
              position={[x, y, terrainZ(x, y) + 0.28]}
              renderOrder={RENDER_ORDER_PROPS}
            >
              <boxGeometry args={[width, depth, 0.24]} />
              <meshStandardMaterial color="#a47a4e" roughness={0.88} />
            </mesh>
          );
        })}
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
          <group
            key={`goal-${direction}`}
            position={[position.x, position.y, terrainZ(position.x, position.y) + 0.06]}
            rotation={[0, 0, field.rotationZ]}
          >
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
              return [
                position.x,
                position.y,
                terrainZ(position.x, position.y) + 0.18 + row * 0.32,
              ] as [number, number, number];
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
          <group
            key={`light-${offsetX}-${offsetY}`}
            position={[position.x, position.y, terrainZ(position.x, position.y)]}
            rotation={[0, 0, field.rotationZ]}
          >
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
          <group
            key={`tennis-net-${index}`}
            position={[court.x, court.y, terrainZ(court.x, court.y) + 0.04]}
            rotation={[0, 0, court.rotationZ]}
          >
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

  if (structureKind === 'cricket_ground_assembly') {
    const ovalGuide = placementProgramGuides.find((guide) => guide.kind === 'track');
    if (!ovalGuide) return null;
    return (
      <GlobeCricketGroundAssembly
        zone={zone}
        guide={ovalGuide}
        frame={programFrame}
        terrainZ={terrainZ}
      />
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
          <group
            key={`tennis-net-${index}`}
            position={[court.x, court.y, terrainZ(court.x, court.y) + 0.04]}
            rotation={[0, 0, court.rotationZ]}
          >
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
        <mesh position={[
          programFrame.minX + programFrame.width / 2,
          programFrame.minY + fenceInset,
          terrainZ(programFrame.minX + programFrame.width / 2, programFrame.minY + fenceInset)
            + fenceHeight / 2,
        ]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceWidth, fenceHeight, 24, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[
          programFrame.minX + programFrame.width / 2,
          programFrame.maxY - fenceInset,
          terrainZ(programFrame.minX + programFrame.width / 2, programFrame.maxY - fenceInset)
            + fenceHeight / 2,
        ]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceWidth, fenceHeight, 24, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[
          programFrame.minX + fenceInset,
          programFrame.minY + programFrame.height / 2,
          terrainZ(programFrame.minX + fenceInset, programFrame.minY + programFrame.height / 2)
            + fenceHeight / 2,
        ]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceDepth, fenceHeight, 16, 6]} />
          <FenceMaterial />
        </mesh>
        <mesh position={[
          programFrame.maxX - fenceInset,
          programFrame.minY + programFrame.height / 2,
          terrainZ(programFrame.maxX - fenceInset, programFrame.minY + programFrame.height / 2)
            + fenceHeight / 2,
        ]} rotation={[0, Math.PI / 2, 0]} renderOrder={RENDER_ORDER_PROPS}>
          <planeGeometry args={[fenceDepth, fenceHeight, 16, 6]} />
          <FenceMaterial />
        </mesh>
        {fencePosts.map(([x, y], index) => (
          <mesh key={`fence-post-${index}`} position={[x, y, terrainZ(x, y) + fenceHeight / 2]} renderOrder={RENDER_ORDER_PROPS}>
            <boxGeometry args={[0.09, 0.09, fenceHeight]} />
            <meshStandardMaterial color="#394747" metalness={0.45} roughness={0.58} />
          </mesh>
        ))}
        {lightPositions.map(([x, y], index) => (
          <group key={`court-light-${index}`} position={[x, y, terrainZ(x, y)]}>
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
      <group
        position={[
          conservatory.x,
          conservatory.y,
          terrainZ(conservatory.x, conservatory.y) + 0.08,
        ]}
        renderOrder={RENDER_ORDER_PROPS}
      >
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
          <mesh
            position={[x, 0, terrainZ(bridge.x + x, bridge.y) + 0.24 + crown]}
            rotation={[0, -slope, 0]}
            renderOrder={RENDER_ORDER_PROPS}
          >
            <boxGeometry args={[segmentLength * 1.06, JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.width, 0.20]} />
            <meshStandardMaterial color={index % 2 === 0 ? '#a9342e' : '#bd4438'} roughness={0.62} />
          </mesh>
          {[-0.98, 0.98].map((railY) => (
            <group key={railY}>
              <mesh
                position={[
                  x,
                  railY,
                  terrainZ(bridge.x + x, bridge.y + railY) + 1.10 + crown,
                ]}
                rotation={[0, -slope, 0]}
                renderOrder={RENDER_ORDER_PROPS}
              >
                <boxGeometry args={[segmentLength * 1.08, 0.11, 0.11]} />
                <meshStandardMaterial color="#7f241f" roughness={0.68} />
              </mesh>
              {index % 2 === 0 && (
                <mesh
                  position={[
                    x,
                    railY,
                    terrainZ(bridge.x + x, bridge.y + railY) + 0.70 + crown,
                  ]}
                  renderOrder={RENDER_ORDER_PROPS}
                >
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
function liveProgrammedParkPlacements(zone: SiteZone): PropPlacement[] {
  const recipe = resolveParkRecipeForZone({
    properties: zone.properties,
    coordinates: zone.coordinates,
    zone_type: zone.zone_type,
  });
  const plantingStructure = resolveParkPlantingStructure(zone);
  return [
    ...computeParkPlacements(
      { id: zone.id, coordinates: zone.coordinates },
      recipe,
      plantingStructure,
      resolveParkProgramAnchorLayout(zone),
    ),
    ...computeParkProgramAssetPlacements(zone),
  ].filter((placement) => {
    const asset = PARK_KIT_MANIFEST[placement.propId];
    const hasProceduralFallback = placement.propId === 'tree'
      || placement.propId === 'bench'
      || (isExecutableParkLegoFamily(zone)
        && (placement.propId === 'playground' || placement.propId === 'pavilion'));
    return !shouldDeferParkFinishingProp(zone, placement.propId)
      && (Boolean(asset) || hasProceduralFallback);
  });
}

function hasLiveProgrammedParkGeometry(zone: SiteZone): boolean {
  return shouldMountParkProgramFrame(zone, liveProgrammedParkPlacements(zone).length)
    || Boolean(getDerivedParkAccess(zone)?.connections.length);
}

function ParkAccessBridge({ connection, centroid, offsets, groundAt, groundGrid }: {
  connection: ParkAccessConnection; centroid: { lng: number; lat: number }; offsets: [number, number];
  groundAt?: (x: number, y: number) => number | null;
  groundGrid?: SharedGroundTriangulation;
}) {
  const [startGroundM, endGroundM] = offsets;
  const geometry = useMemo(() => {
    const local = ([lng, lat]: [number, number]): [number, number] => [
      (lng - centroid.lng) * metersPerDegLon(centroid.lat), (lat - centroid.lat) * METERS_PER_DEG_LAT,
    ];
    return buildParkAccessBridgeGeometry({ start: local(connection.streetPoint), end: local(connection.gateway), widthM: connection.widthM,
      streetLiftM: connection.streetLiftM, startGroundM, endGroundM, groundAt, groundGrid });
  }, [connection, centroid, startGroundM, endGroundM, groundAt, groundGrid]);
  useEffect(() => geometry ? retainResourceForDeferredDisposal(geometry, (owned) => owned.dispose()) : undefined, [geometry]);
  if (!geometry) return null;
  return <mesh name={`park-access-${connection.id}`} geometry={geometry} renderOrder={144}>
    <meshStandardMaterial color="#a99f86" roughness={0.94} side={THREE.DoubleSide} depthTest depthWrite />
  </mesh>;
}

function hasCoreFixedParkProgram(zone: SiteZone): boolean {
  return resolveParkSpecialtyStructureKind(zone) !== null
    || liveProgrammedParkPlacements(zone).some((placement) => (
      placement.propId === 'playground' || placement.propId === 'pavilion'
    ));
}

function ParkKitInstance({
  zone,
  fallbackTerrainHeight,
  preparedTerrain = null,
}: {
  zone: SiteZone;
  fallbackTerrainHeight: number;
  preparedTerrain?: number | null;
}) {
  const tiles = useContext(TilesRendererContext);
  const sharedGround = useParkGround(zone);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(
    parkTerrainSampleOffset(zone.id, TERRAIN_SAMPLE_FRAME_INTERVAL),
  );
  const attemptsRef = useRef(0);
  const nextInstanceRef = useRef(0);
  const rawElevationRef = useRef<Array<number | null> | null>(null);
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
  const legoAppearance = useMemo(
    () => resolveParkLegoAppearance(zone),
    [zone],
  );
  const dressingAppearance = useMemo(
    () => resolveParkDressingAppearance(zone),
    [zone],
  );
  const programAnchors = useMemo(
    () => resolveParkProgramAnchorLayout(zone),
    [zone],
  );
  // A generated green-space drape is the spatial source of truth. Both
  // procedural and AI-upgraded grounds keep the same deterministic placement
  // recipe, so their live canopy and seating remain stable across reloads.
  const specialtyStructureKind = useMemo(
    () => resolveParkSpecialtyStructureKind(zone),
    [zone],
  );

  const centroid = useMemo(() => {
    let lng = 0;
    let lat = 0;
    for (const c of zone.coordinates) {
      lng += c[0];
      lat += c[1];
    }
    return { lng: lng / zone.coordinates.length, lat: lat / zone.coordinates.length };
  }, [zone.coordinates]);
  const sharedGroundOwned = sharedGround.status !== 'inactive'
    && (sharedGround.contains(centroid.lng, centroid.lat) || zone.coordinates.some(([lng, lat]) => sharedGround.contains(lng, lat)));
  const sharedAnchor = sharedGroundOwned
    ? sharedGround.heightAt(centroid.lng, centroid.lat) ?? sharedGround.heightAt(zone.coordinates[0][0], zone.coordinates[0][1]) : null;
  const sharedTerrainZ = useMemo(() => sharedGroundOwned && sharedAnchor !== null ? (x: number, y: number): number | null => {
    const height = sharedGround.heightAt(centroid.lng + x / metersPerDegLon(centroid.lat), centroid.lat + y / METERS_PER_DEG_LAT);
    return height === null ? null : height - sharedAnchor;
  } : undefined, [centroid, sharedAnchor, sharedGround, sharedGroundOwned]);
  const sharedTerrainGrid = useMemo(() => sharedGroundOwned && sharedGround.snapshot
    ? createSharedGroundTriangulation(sharedGround.snapshot, centroid.lng, centroid.lat) : undefined,
  [centroid, sharedGround.snapshot, sharedGroundOwned]);

  const localProgramFrame = useMemo(
    () => buildLocalParkProgramFrame(zone.coordinates, centroid),
    [centroid, zone.coordinates],
  );
  const dressingFamilyId = useMemo(
    () => resolveParkDressingFamily(zone),
    [zone],
  );
  const programGuideFit = useMemo(() => {
    return fitParkGroundGuides(
      resolveParkGroundProfile(zone).guides,
      { width: localProgramFrame.width, height: localProgramFrame.height },
      localProgramFrame.normalizedRing,
    );
  }, [localProgramFrame, zone]);
  const fittedProgramGuides = programGuideFit.guides;
  const fittedMicrodetailGuides = useMemo(() => {
    return parkMicrodetailGuides(
      [...resolveParkPlacementGuides(programGuideFit), ...derivedParkAccessGuides(zone)],
      localProgramFrame,
      dressingFamilyId,
    );
  }, [dressingFamilyId, localProgramFrame, programGuideFit, zone]);
  const placements = useMemo(() => [
    ...(specialtyStructureKind === 'basketball_court_assembly' ? [] : computeParkPlacements(
      { id: zone.id, coordinates: zone.coordinates },
      recipe,
      plantingStructure,
      programAnchors,
      fittedMicrodetailGuides,
    )),
    ...computeParkProgramAssetPlacements(zone),
  ].filter((placement) => (
    !isNeighborhoodParkPilot(zone) && !isParkTrio(zone) && !shouldDeferParkFinishingProp(zone, placement.propId)
    && !(
      specialtyStructureKind === 'neighborhood_park_v0_sticker_assembly'
      && (placement.propId === 'playground' || placement.propId === 'pavilion')
    )
  )), [
    fittedMicrodetailGuides,
    plantingStructure,
    programAnchors,
    recipe,
    specialtyStructureKind,
    zone,
  ]);
  const microdetailPlacements = useMemo<ParkMicrodetailPlacement[]>(() => {
    if (isNeighborhoodParkPilot(zone) || isParkTrio(zone)) return [];
    if (
      specialtyStructureKind === 'cricket_ground_assembly'
      || specialtyStructureKind === 'basketball_court_assembly'
    ) return [];
    const mPerLon = metersPerDegLon(centroid.lat);
    return buildParkMicrodetailFamily({
      zoneId: zone.id,
      familyId: dressingFamilyId,
      boundary: localProgramFrame.points,
      guides: fittedMicrodetailGuides,
      primaryPlacements: placements.map((placement) => ({
        x: (placement.lng - centroid.lng) * mPerLon,
        y: (placement.lat - centroid.lat) * METERS_PER_DEG_LAT,
        footprintRadiusM: placement.propId === 'tree'
          ? Math.max(1.05, placement.scale * 1.35)
          : placement.propId === 'bench'
            ? Math.max(0.8, placement.scale * 1.15)
            : placement.propId === 'playground'
              ? PARK_PROGRAM_MODULE_SPEC.playground.safetyDiameterM / 2
              : placement.propId === 'basketball_hoop_regulation'
                ? 1.45
              : Math.hypot(
                PARK_PROGRAM_MODULE_SPEC.pavilion.widthM,
                PARK_PROGRAM_MODULE_SPEC.pavilion.depthM,
              ) / 2,
        kind: placement.propId === 'basketball_hoop_regulation'
          ? 'fixed_program'
          : placement.propId,
      })),
      maxPlacements: 72,
      collisionClearanceM: 0.22,
    });
  }, [centroid, dressingFamilyId, fittedMicrodetailGuides, localProgramFrame.points, placements, specialtyStructureKind, zone]);

  const specialtyProgramGuides = useMemo(
    () => specialtyStructureKind === 'cricket_ground_assembly'
      ? resolveParkPlacementGuides(programGuideFit)
      : fittedProgramGuides,
    [fittedProgramGuides, programGuideFit, specialtyStructureKind],
  );

  const specialtyTerrainAnchors = useMemo(() => isParkTrio(zone) ? (() => { const layout = parkTrioLayout(zone, centroid); return [...layout.boundary, ...layout.modules.flatMap(m => [m.center, ...m.envelope]), ...layout.trees]; })() : isNeighborhoodParkPilot(zone)
    ? (() => {
        const layout = neighborhoodParkLayoutForZone(zone, centroid);
        return [...layout.boundary, ...layout.modules.flatMap(m => [m.center, ...m.envelope]), ...layout.trees];
      })()
    : buildParkSpecialtyTerrainAnchors(
    specialtyStructureKind,
    specialtyProgramGuides,
    localProgramFrame,
  ), [localProgramFrame, specialtyProgramGuides, specialtyStructureKind, zone, centroid]);

  const accessConnections = useMemo(() => getDerivedParkAccess(zone)?.connections ?? [], [zone]);

  const terrainTargets = useMemo(() => {
    const mPerLon = metersPerDegLon(centroid.lat);
    return [
      ...placements.map((placement) => ({
        lng: placement.lng,
        lat: placement.lat,
        x: (placement.lng - centroid.lng) * mPerLon,
        y: (placement.lat - centroid.lat) * METERS_PER_DEG_LAT,
      })),
      ...microdetailPlacements.map((placement) => ({
        lng: centroid.lng + placement.x / mPerLon,
        lat: centroid.lat + placement.y / METERS_PER_DEG_LAT,
        x: placement.x,
        y: placement.y,
      })),
      ...specialtyTerrainAnchors.map((anchor) => ({
        lng: centroid.lng + anchor.x / mPerLon,
        lat: centroid.lat + anchor.y / METERS_PER_DEG_LAT,
        x: anchor.x,
        y: anchor.y,
      })),
      ...accessConnections.flatMap((connection) => [connection.streetPoint, connection.gateway].map(([lng, lat]) => ({
        lng, lat, x: (lng - centroid.lng) * mPerLon, y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
      }))),
    ];
  }, [accessConnections, centroid, microdetailPlacements, placements, specialtyTerrainAnchors]);
  const sharedOffsets = useMemo(() => {
    if (!sharedGroundOwned || sharedAnchor === null) return null;
    const heights = terrainTargets.map((target) => sharedGround.heightAt(target.lng, target.lat));
    return heights.every((height) => height !== null) ? heights.map((height) => height! - sharedAnchor) : null;
  }, [sharedAnchor, sharedGround, sharedGroundOwned, terrainTargets]);

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
  const missesAtFreezeRef = useRef(0);
  const redrapesRef = useRef(0);

  // Coordinates/recipe changed under the same zone id — restart draping.
  useEffect(() => {
    frozenRef.current = false;
    attemptsRef.current = 0;
    nextInstanceRef.current = 0;
    passRef.current = 0;
    rawElevationRef.current = null;
    hitFlagsRef.current = null;
    missesAtFreezeRef.current = 0;
    redrapesRef.current = 0;
    setInstanceZ(null);
    setSampledTerrain(null);
  }, [terrainTargets]);

  // Self-healing re-drape: a freeze taken against unrefined tiles can seat the
  // kit tens of metres off the true surface (floating-tree bug, 2026-07-24).
  // When the tile set settles after a freeze, spot-check the anchor; if any
  // instance rays missed at freeze time or the centroid drifted, re-drape.
  useEffect(() => {
    const tilesRenderer = tiles;
    if (!tilesRenderer || preparedTerrain !== null || sharedGroundOwned) return;
    const handleLoadEnd = () => {
      if (!frozenRef.current || redrapesRef.current >= 3) return;
      const tilesGroup = tilesRenderer.group;
      if (!tilesGroup || tilesGroup.children.length === 0) return;
      const fresh = raycastTerrainHeightAtLatLng(
        centroid.lng,
        centroid.lat,
        tilesGroup,
        raycasterRef.current,
      );
      const anchorDrifted = (
        fresh !== null
        && sampledTerrain !== null
        && Number.isFinite(fresh)
        && Math.abs(fresh - sampledTerrain) > 2.5
      );
      if (!anchorDrifted && missesAtFreezeRef.current === 0) return;
      redrapesRef.current += 1;
      frozenRef.current = false;
      attemptsRef.current = 0;
      nextInstanceRef.current = 0;
      passRef.current = 0;
      rawElevationRef.current = null;
      hitFlagsRef.current = null;
      missesAtFreezeRef.current = 0;
      setInstanceZ(null);
      setSampledTerrain(null);
    };
    tilesRenderer.addEventListener('tiles-load-end', handleLoadEnd);
    return () => {
      tilesRenderer.removeEventListener('tiles-load-end', handleLoadEnd);
    };
  }, [tiles, centroid.lat, centroid.lng, sampledTerrain, preparedTerrain, sharedGroundOwned]);

  // Anchor the frame, then seat instances in interval-gated batches
  // (drape-and-freeze; z accumulates in refs, state set once at freeze).
  useFrame(() => {
    if (sharedGroundOwned || preparedTerrain !== null || frozenRef.current || terrainTargets.length === 0) return;
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
      const groundCandidate = resolvePublicRealmGroundAnchor(
        filtered,
        storedTerrain,
        fallbackTerrainHeight,
        4,
      );
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
    const n = terrainTargets.length;
    if (!rawElevationRef.current || rawElevationRef.current.length !== n) {
      rawElevationRef.current = new Array<number | null>(n).fill(null);
      hitFlagsRef.current = new Array<boolean>(n).fill(false);
      nextInstanceRef.current = 0;
      passRef.current = 0;
    }
    const rawElevations = rawElevationRef.current;
    const hits = hitFlagsRef.current!;
    let i = nextInstanceRef.current;
    let processed = 0;
    while (i < n && processed < INSTANCES_PER_BATCH) {
      if (!hits[i]) {
        const p = terrainTargets[i];
        const sampled = raycastTerrainHeightAtLatLng(p.lng, p.lat, tilesGroup, raycasterRef.current);
        if (isPlausibleTerrainAnchor(sampled, anchor)) {
          rawElevations[i] = sampled;
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
      const fitSamples: TerrainContactSample[] = terrainTargets.flatMap((target, index) => (
        Number.isFinite(rawElevations[index])
          ? [{ x: target.x, y: target.y, z: rawElevations[index] as number }]
          : []
      ));
      const plane = fitTerrainContactPlane(fitSamples, {
        fallbackElevationMeters: anchor,
        outlierToleranceMeters: 1.5,
      });
      const zs = terrainTargets.map((target, index) => (
        (resolveTerrainContactElevation(
          plane,
          rawElevations[index],
          target.x,
          target.y,
        ) ?? anchor) - anchor
      ));
      missesAtFreezeRef.current = misses;
      frozenRef.current = true;
      setInstanceZ(zs);
    }
  });

  const specialtyTerrainPlane = useMemo(() => {
    if (!instanceZ || specialtyTerrainAnchors.length === 0) return null;
    const start = placements.length + microdetailPlacements.length;
    return fitTerrainContactPlane(specialtyTerrainAnchors.map((anchor, index) => ({
      x: anchor.x,
      y: anchor.y,
      z: instanceZ[start + index] ?? 0,
    })), {
      fallbackElevationMeters: 0,
      outlierToleranceMeters: 1.5,
    });
  }, [instanceZ, microdetailPlacements.length, placements.length, specialtyTerrainAnchors]);
  if (terrainTargets.length === 0) return null;
  if (sharedGroundOwned && (sharedGround.status !== 'ready' || sharedAnchor === null || !sharedOffsets)) return null;
  const terrain = sharedAnchor ?? preparedTerrain ?? resolveZoneTerrainHeight(sampledTerrain, storedTerrain, fallbackTerrainHeight);
  const activeOffsets = sharedGroundOwned ? sharedOffsets : instanceZ;
  const microdetailZ = activeOffsets
    ? activeOffsets.slice(placements.length, placements.length + microdetailPlacements.length)
    : null;

  return (
    <EastNorthUpFrame
      lat={centroid.lat * DEG_TO_RAD}
      lon={centroid.lng * DEG_TO_RAD}
      height={terrain}
    >
      {accessConnections.map((connection, index) => {
        const offset = placements.length + microdetailPlacements.length + specialtyTerrainAnchors.length + index * 2;
        return <ParkAccessBridge key={connection.id} connection={connection} centroid={centroid}
          offsets={[activeOffsets?.[offset] ?? 0, activeOffsets?.[offset + 1] ?? 0]} groundAt={sharedTerrainZ} groundGrid={sharedTerrainGrid} />;
      })}
      <SilentKitBoundary key={`specialty-${zone.updated_at}-${sharedGround.revision}`} fallback={null}>
        <ParkSpecialtyStructures
          structureKind={specialtyStructureKind}
          zone={zone}
          centroid={centroid}
          terrainPlane={specialtyTerrainPlane}
          sharedTerrainZ={sharedTerrainZ}
          groundGrid={sharedTerrainGrid}
        />
      </SilentKitBoundary>
      <GlobeParkMicrodetailInstances
        placements={microdetailPlacements}
        terrainOffsets={microdetailZ}
        palette={dressingAppearance?.palette}
        renderOrder={RENDER_ORDER_PROPS}
      />
      {[...byProp.entries()].map(([propId, group]) => {
        const groupZ = activeOffsets
          ? group.map((g) => activeOffsets[placements.indexOf(g)] ?? 0)
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
              appearance={dressingAppearance}
            />
          );
        }
        if (
          legoAppearance
          && (propId === 'playground' || propId === 'pavilion')
        ) {
          return (
            <ProceduralParkProgramProps
              key={propId}
              propId={propId}
              placements={group}
              centroid={centroid}
              instanceZ={groupZ}
              appearance={legoAppearance}
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
                preserveHorizontalOrigin={Boolean(asset.preserveHorizontalOrigin)}
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
    () => selectBudgetedLiveParkZones(
      zones.filter((z) =>
        resolveCommunity3DKind(z) === 'park'
        && z.coordinates.length >= 3
        && shouldRenderCommunityProps(z)
        // Generate 3D always creates a current deterministic ground design;
        // optional AI orthophotos upgrade its material fidelity. Deterministic
        // surfaces can mount the full authored kit, while AI surfaces retain
        // only design-critical programmed structures.
        && hasCurrentParkGroundSurface(z)
        && hasLiveProgrammedParkGeometry(z)),
      hasCoreFixedParkProgram,
    ),
    [zones],
  );

  return (
    <>
      {parkZones.map((zone) => (
        <group
          key={zone.id}
          name={`siteforge-direct3d-park-${zone.id}`}
          userData={direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, 'park'))}
        >
          <ParkKitInstance
            key={`${zone.id}:${resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}`}
            zone={zone}
            fallbackTerrainHeight={terrainHeight}
            preparedTerrain={resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)}
          />
        </group>
      ))}
    </>
  );
}
