import { useEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import type { SiteZone, LayoutRoadData, LayoutGreenSpaceData, LayoutOption, Building } from '@/types';
import { useViewerStore } from '@/store';

// =============================================================================
// Public API
// =============================================================================

export interface BuildingGenerationStatus {
  status: string;
  progress?: number;
}

interface SiteZonesGroupProps {
  zones: SiteZone[];
  projectLat?: number;
  projectLng?: number;
  buildingStatuses?: Map<string, BuildingGenerationStatus>;
  buildings?: Building[];
  onZoneClick?: (id: string) => void;
}

export function SiteZonesGroup({ zones, projectLat, projectLng, buildingStatuses, onZoneClick }: SiteZonesGroupProps) {
  if (!projectLat || !projectLng || zones.length === 0) return null;

  const origin = { lat: projectLat, lon: projectLng };

  // Build a set of zone IDs that have linked buildings (hide procedural geometry)
  const zonesWithBuildings = useMemo(() => {
    const result = new Set<string>();
    for (const zone of zones) {
      if (zone.building_id || (zone.building_ids && zone.building_ids.length > 0)) {
        result.add(zone.id);
      }
    }
    return result;
  }, [zones]);

  return (
    <group name="site-zones">
      {zones.map((zone) => (
        <SiteZoneMesh
          key={zone.id}
          zone={zone}
          origin={origin}
          generationStatus={zone.building_id ? buildingStatuses?.get(zone.building_id) : undefined}
          hasLinkedBuildings={zonesWithBuildings.has(zone.id)}
          onClick={onZoneClick ? () => onZoneClick(zone.id) : undefined}
        />
      ))}
      <LayoutPreviewOverlay zones={zones} origin={origin} />
    </group>
  );
}

// =============================================================================
// Coordinate helpers
// =============================================================================

const METERS_PER_DEG_LAT = 111320;

function metersPerDegLon(lat: number) {
  return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180);
}

/** Convert lng/lat polygon to local meters (Three.js XZ plane). */
function toLocalPoints(
  coords: number[][],
  origin: { lat: number; lon: number },
): THREE.Vector2[] {
  const mLon = metersPerDegLon(origin.lat);
  const rawPts = coords.map((p) => {
    const x = (p[0] - origin.lon) * mLon;
    const z = (p[1] - origin.lat) * METERS_PER_DEG_LAT;
    // Shape y maps to 3D z = -y after rotateX(-PI/2), so y=z gives 3D z=-z (north=-Z)
    return new THREE.Vector2(x, z);
  });

  // De-duplicate nearly-identical points
  const pts: THREE.Vector2[] = [];
  for (const p of rawPts) {
    if (pts.length === 0 || p.distanceTo(pts[pts.length - 1]) > 0.01) {
      pts.push(p);
    }
  }
  return pts;
}

// =============================================================================
// Seeded PRNG (deterministic)
// =============================================================================

function makeRand(seed: number) {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return s / 2147483647;
  };
}

// =============================================================================
// Geometry: point-in-polygon
// =============================================================================

function pointInPolygon(x: number, y: number, polygon: THREE.Vector2[]): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x, yi = polygon[i].y;
    const xj = polygon[j].x, yj = polygon[j].y;
    const intersect =
      yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

type TreeVariant = 'deciduous' | 'conifer' | 'ornamental';

interface PolygonBounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
  area: number;
}

function computePolygonBounds(points2D: THREE.Vector2[]): PolygonBounds {
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  for (const p of points2D) {
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  }
  const width = Math.max(0, maxX - minX);
  const height = Math.max(0, maxY - minY);
  return {
    minX,
    maxX,
    minY,
    maxY,
    width,
    height,
    area: width * height,
  };
}

function polylineLength(points: { x: number; z: number }[]): number {
  let total = 0;
  for (let i = 1; i < points.length; i++) {
    const dx = points[i].x - points[i - 1].x;
    const dz = points[i].z - points[i - 1].z;
    total += Math.sqrt(dx * dx + dz * dz);
  }
  return total;
}

function sampleCenterlineAtDistance(
  centerPoints: { x: number; z: number }[],
  targetDistance: number,
): PlacementPoint | null {
  if (centerPoints.length < 2) return null;
  const total = polylineLength(centerPoints);
  const clamped = Math.max(0, Math.min(total, targetDistance));

  let acc = 0;
  for (let i = 1; i < centerPoints.length; i++) {
    const a = centerPoints[i - 1];
    const b = centerPoints[i];
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const len = Math.sqrt(dx * dx + dz * dz);
    if (len < 0.001) continue;

    if (acc + len >= clamped) {
      const t = (clamped - acc) / len;
      const dirX = dx / len;
      const dirZ = dz / len;
      const nx = -dirZ;
      const nz = dirX;
      return {
        x: a.x + dx * t,
        z: a.z + dz * t,
        nx,
        nz,
        angle: Math.atan2(dirX, dirZ),
      };
    }
    acc += len;
  }

  const tailA = centerPoints[Math.max(0, centerPoints.length - 2)];
  const tailB = centerPoints[centerPoints.length - 1];
  const tdx = tailB.x - tailA.x;
  const tdz = tailB.z - tailA.z;
  const tlen = Math.sqrt(tdx * tdx + tdz * tdz) || 1;
  const tDirX = tdx / tlen;
  const tDirZ = tdz / tlen;
  return {
    x: tailB.x,
    z: tailB.z,
    nx: -tDirZ,
    nz: tDirX,
    angle: Math.atan2(tDirX, tDirZ),
  };
}
// =============================================================================
// Polygon edge utilities
// =============================================================================

interface WallSegment {
  // All coordinates are in 3D world space (XZ ground plane)
  startX: number;
  startZ: number;
  endX: number;
  endZ: number;
  length: number;
  dirX: number;      // unit direction along wall (3D X)
  dirZ: number;      // unit direction along wall (3D Z)
  normalX: number;   // outward-facing normal (3D X)
  normalZ: number;   // outward-facing normal (3D Z)
  midX: number;
  midZ: number;
  angle: number;     // Y rotation to face outward
}

/**
 * Compute wall segments in 3D world coordinates from 2D shape points.
 * ExtrudeGeometry + rotateX(-PI/2) maps shape (x, y) → world (x, _, -y).
 * We convert here so all downstream code (windows, doors, cornices) uses
 * correct 3D positions directly.
 */
function computeWallSegments(pts2D: THREE.Vector2[]): WallSegment[] {
  // Convert shape space to 3D ground plane: (x, y) → (x, -y)
  const pts = pts2D.map((p) => ({ x: p.x, z: -p.y }));

  // Compute centroid to determine outward normal direction
  let cx = 0, cz = 0;
  for (const p of pts) { cx += p.x; cz += p.z; }
  cx /= pts.length;
  cz /= pts.length;

  const walls: WallSegment[] = [];
  for (let i = 0; i < pts.length; i++) {
    const p1 = pts[i];
    const p2 = pts[(i + 1) % pts.length];
    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const length = Math.sqrt(dx * dx + dz * dz);
    if (length < 0.5) continue;

    const dirX = dx / length;
    const dirZ = dz / length;

    // Candidate normal: perpendicular to wall direction in XZ plane
    let nx = -dirZ;
    let nz = dirX;

    // Ensure normal points OUTWARD (away from centroid)
    const midX = (p1.x + p2.x) / 2;
    const midZ = (p1.z + p2.z) / 2;
    const toCenterX = cx - midX;
    const toCenterZ = cz - midZ;
    if (nx * toCenterX + nz * toCenterZ > 0) {
      nx = -nx;
      nz = -nz;
    }

    const angle = Math.atan2(nx, nz);

    walls.push({
      startX: p1.x, startZ: p1.z,
      endX: p2.x, endZ: p2.z,
      length, dirX, dirZ, normalX: nx, normalZ: nz,
      midX, midZ, angle,
    });
  }
  return walls;
}

function getDefaultHeight(zoneType: string): number {
  switch (zoneType) {
    case 'building':
      return 30;
    case 'residential':
      return 12;
    default:
      return 0;
  }
}

// =============================================================================
// Zone router
// =============================================================================

function SiteZoneMesh({
  zone,
  origin,
  generationStatus,
  hasLinkedBuildings,
  onClick,
}: {
  zone: SiteZone;
  origin: { lat: number; lon: number };
  generationStatus?: BuildingGenerationStatus;
  hasLinkedBuildings?: boolean;
  onClick?: () => void;
}) {
  const pts = useMemo(() => toLocalPoints(zone.coordinates, origin), [zone.coordinates, origin]);

  if (pts.length < 3) return null;

  let content: React.ReactNode = null;

  switch (zone.zone_type) {
    case 'site_boundary':
      content = <SiteBoundaryZone zone={zone} points2D={pts} />;
      break;
    case 'building':
    case 'residential':
      // Once buildings are linked to this zone, hide the procedural placeholder
      // to avoid duplicate geometry (the real buildings render via SceneViewer)
      // But still render AI-generated layout infrastructure (roads, green spaces)
      if (hasLinkedBuildings) {
        const layoutRoads = zone.properties?._layout_roads as LayoutRoadData[] | undefined;
        const layoutGreens = zone.properties?._layout_green_spaces as LayoutGreenSpaceData[] | undefined;
        if (layoutRoads?.length || layoutGreens?.length) {
          content = <LayoutInfrastructure zone={zone} origin={origin} roads={layoutRoads} greenSpaces={layoutGreens} />;
        } else {
          return null;
        }
        break;
      }
      content = <DetailedBuildingZone zone={zone} points2D={pts} generationStatus={generationStatus} />;
      break;
    case 'road':
      content = <RoadZone zone={zone} points2D={pts} />;
      break;
    case 'green_space':
      content = <GreenSpaceZone zone={zone} points2D={pts} />;
      break;
    case 'parking':
      content = <ParkingZone zone={zone} points2D={pts} />;
      break;
    case 'water':
      content = <WaterZone zone={zone} points2D={pts} />;
      break;
    default:
      content = <FallbackZone zone={zone} points2D={pts} />;
      break;
  }

  if (onClick) {
    return (
      <group onClick={(e) => { e.stopPropagation(); onClick(); }}>
        {content}
      </group>
    );
  }

  return <>{content}</>;
}

// =============================================================================
// 0. SITE BOUNDARY ZONE — Dashed outline loop, no fill
// =============================================================================

function SiteBoundaryZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const lineRef = useRef<THREE.Line>(null);

  const geometry = useMemo(() => {
    // Convert 2D shape points to 3D positions (XZ plane at y=0.1)
    // Shape (x, y) → 3D (x, 0.1, -y) to match the rotated ShapeGeometry convention
    const points3D: THREE.Vector3[] = [];
    for (const p of points2D) {
      points3D.push(new THREE.Vector3(p.x, 0.1, -p.y));
    }
    // Close the loop
    if (points3D.length > 0) {
      points3D.push(points3D[0].clone());
    }
    const geom = new THREE.BufferGeometry().setFromPoints(points3D);
    geom.computeBoundingSphere();
    return geom;
  }, [points2D]);

  // LineDashedMaterial requires computeLineDistances on the Line object
  useEffect(() => {
    if (lineRef.current) {
      lineRef.current.computeLineDistances();
    }
  }, [geometry]);

  return (
    <line ref={lineRef as React.RefObject<THREE.Line>} geometry={geometry}>
      <lineDashedMaterial
        color={zone.color || '#f59e0b'}
        dashSize={2}
        gapSize={1}
        linewidth={1}
      />
    </line>
  );
}

// =============================================================================
// 1. BUILDING / RESIDENTIAL ZONE — Detailed facades
// =============================================================================

// =============================================================================
// Generation Indicator — pulsing overlay + progress label
// =============================================================================

function GenerationIndicator({
  status,
  height,
  points2D,
}: {
  status: BuildingGenerationStatus;
  height: number;
  points2D: THREE.Vector2[];
}) {
  const overlayRef = useRef<THREE.Mesh>(null);
  const flashRef = useRef<THREE.Mesh>(null);
  const flashOpacity = useRef(0);

  const overlayGeometry = useMemo(() => {
    try {
      const shape = new THREE.Shape(points2D);
      const geom = new THREE.ExtrudeGeometry(shape, {
        steps: 1,
        depth: height + 0.2,
        bevelEnabled: false,
      });
      geom.rotateX(-Math.PI / 2);
      return geom;
    } catch {
      return null;
    }
  }, [points2D, height]);

  // Compute centroid for label positioning
  const centroid = useMemo(() => {
    let cx = 0, cy = 0;
    for (const p of points2D) { cx += p.x; cy += p.y; }
    cx /= points2D.length;
    cy /= points2D.length;
    return [cx, height + 3, -cy] as [number, number, number];
  }, [points2D, height]);

  useFrame((_, delta) => {
    if (overlayRef.current && status.status === 'generating') {
      const mat = overlayRef.current.material as THREE.MeshStandardMaterial;
      mat.emissiveIntensity = 0.3 + 0.2 * Math.sin(performance.now() * 0.003);
      mat.opacity = 0.12 + 0.06 * Math.sin(performance.now() * 0.003);
    }
    // Completion flash
    if (flashRef.current) {
      if (status.status === 'completed' && flashOpacity.current < 0.01) {
        flashOpacity.current = 0.5;
      }
      if (flashOpacity.current > 0) {
        flashOpacity.current = Math.max(0, flashOpacity.current - delta * 0.8);
        const mat = flashRef.current.material as THREE.MeshStandardMaterial;
        mat.opacity = flashOpacity.current;
      }
    }
  });

  if (!overlayGeometry) return null;
  if (status.status !== 'generating' && status.status !== 'completed') return null;

  const progress = status.progress ?? 0;

  return (
    <>
      {status.status === 'generating' && (
        <>
          <mesh ref={overlayRef} geometry={overlayGeometry}>
            <meshStandardMaterial
              color="#9333ea"
              emissive="#9333ea"
              emissiveIntensity={0.3}
              transparent
              opacity={0.15}
              depthWrite={false}
            />
          </mesh>
          <Html position={centroid} center distanceFactor={100}>
            <div className="pointer-events-none flex items-center gap-1.5 rounded-full bg-purple-600/90 px-3 py-1 text-[11px] font-medium text-white shadow-lg backdrop-blur-sm whitespace-nowrap">
              <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-white" />
              Generating...{progress > 0 ? ` ${Math.round(progress * 100)}%` : ''}
            </div>
          </Html>
        </>
      )}
      {status.status === 'completed' && (
        <mesh ref={flashRef} geometry={overlayGeometry}>
          <meshStandardMaterial
            color="#22c55e"
            emissive="#22c55e"
            emissiveIntensity={1}
            transparent
            opacity={0}
            depthWrite={false}
          />
        </mesh>
      )}
    </>
  );
}

function DetailedBuildingZone({
  zone,
  points2D,
  generationStatus,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
  generationStatus?: BuildingGenerationStatus;
}) {
  const height = zone.properties?.height ?? getDefaultHeight(zone.zone_type);
  const floors = zone.properties?.floors ?? Math.max(1, Math.round(height / 3));
  const floorHeight = zone.properties?.floor_height ?? height / floors;
  const isResidential = zone.zone_type === 'residential';
  const color = zone.color;

  const { mainGeometry, roofGeometry } = useMemo(() => {
    try {
      const shape = new THREE.Shape(points2D);
      const mainGeom = new THREE.ExtrudeGeometry(shape, {
        steps: 1,
        depth: height,
        bevelEnabled: false,
      });
      mainGeom.rotateX(-Math.PI / 2);

      const roofGeom = new THREE.ShapeGeometry(shape);
      roofGeom.rotateX(-Math.PI / 2);
      roofGeom.translate(0, height, 0);

      return { mainGeometry: mainGeom, roofGeometry: roofGeom };
    } catch {
      return { mainGeometry: null, roofGeometry: null };
    }
  }, [points2D, height]);

  const walls = useMemo(() => computeWallSegments(points2D), [points2D]);

  const roofColor = useMemo(() => {
    const c = new THREE.Color(color);
    c.multiplyScalar(0.75);
    return '#' + c.getHexString();
  }, [color]);

  // Find longest wall for door + balconies
  const longestWallIdx = useMemo(() => {
    let maxLen = 0;
    let idx = 0;
    walls.forEach((w, i) => {
      if (w.length > maxLen) {
        maxLen = w.length;
        idx = i;
      }
    });
    return idx;
  }, [walls]);

  if (!mainGeometry) return null;

  return (
    <group>
      {/* Main extruded body */}
      <mesh geometry={mainGeometry} receiveShadow castShadow>
        <meshStandardMaterial color={color} roughness={0.7} metalness={0.05} />
      </mesh>

      {/* Roof cap */}
      <mesh geometry={roofGeometry} receiveShadow>
        <meshStandardMaterial color={roofColor} roughness={0.6} metalness={0.05} />
      </mesh>

      {/* Windows on every wall segment */}
      <PolygonWindows walls={walls} height={height} floors={floors} floorHeight={floorHeight} />

      {/* Front door on longest wall */}
      {walls.length > 0 && (
        <PolygonDoor wall={walls[longestWallIdx]} />
      )}

      {/* Floor divider lines */}
      <PolygonFloorDividers walls={walls} height={height} floors={floors} floorHeight={floorHeight} color={color} />

      {/* Cornice at roofline */}
      <PolygonCornice walls={walls} height={height} />

      {/* Balconies for residential on longest wall, upper floors */}
      {isResidential && walls.length > 0 && (
        <PolygonBalconies
          wall={walls[longestWallIdx]}
          height={height}
          floors={floors}
          floorHeight={floorHeight}
        />
      )}

      {/* Generation status overlay */}
      {generationStatus && (
        <GenerationIndicator status={generationStatus} height={height} points2D={points2D} />
      )}
    </group>
  );
}

// =============================================================================
// Windows along polygon edges
// =============================================================================

function PolygonWindows({
  walls,
  height,
  floors,
  floorHeight,
}: {
  walls: WallSegment[];
  height: number;
  floors: number;
  floorHeight: number;
}) {
  const winWidth = 1.2;
  const winHeight = 1.4;
  const spacing = 3.5;
  const edgeMargin = 1.5;

  const windowData = useMemo(() => {
    const result: { pos: [number, number, number]; rotY: number }[] = [];

    for (const wall of walls) {
      const usableLength = wall.length - edgeMargin * 2;
      if (usableLength < 1.5) continue;

      const numWins = Math.max(1, Math.floor(usableLength / spacing));
      const actualSpacing = usableLength / numWins;

      for (let floor = 0; floor < floors; floor++) {
        const y = floor * floorHeight + floorHeight * 0.45;

        for (let w = 0; w < numWins; w++) {
          const t = edgeMargin + (w + 0.5) * actualSpacing;
          const wx = wall.startX + wall.dirX * t + wall.normalX * 0.05;
          const wz = wall.startZ + wall.dirZ * t + wall.normalZ * 0.05;

          result.push({
            pos: [wx, y, wz],
            rotY: wall.angle,
          });
        }
      }
    }
    return result;
  }, [walls, height, floors, floorHeight]);

  return (
    <>
      {windowData.map((win, i) => (
        <mesh key={i} position={win.pos} rotation={[0, win.rotY, 0]}>
          <planeGeometry args={[winWidth, winHeight]} />
          <meshStandardMaterial
            color="#87ceeb"
            roughness={0.1}
            metalness={0.8}
            transparent
            opacity={0.6}
            side={THREE.DoubleSide}
            polygonOffset
            polygonOffsetFactor={-1}
            polygonOffsetUnits={-1}
          />
        </mesh>
      ))}
    </>
  );
}

// =============================================================================
// Front door on a wall segment
// =============================================================================

function PolygonDoor({ wall }: { wall: WallSegment }) {
  const doorWidth = 1.2;
  const doorHeight = 2.2;
  const frameWidth = 1.35;
  const frameHeight = 2.35;

  // Place door at the center of the wall, at ground level
  const x = wall.midX + wall.normalX * 0.05;
  const z = wall.midZ + wall.normalZ * 0.05;
  const y = doorHeight / 2;

  return (
    <group>
      {/* Door frame (behind door) */}
      <mesh position={[x, y, z]} rotation={[0, wall.angle, 0]}>
        <planeGeometry args={[frameWidth, frameHeight]} />
        <meshStandardMaterial color="#3d2815" roughness={0.8} metalness={0.05} side={THREE.DoubleSide} polygonOffset polygonOffsetFactor={-1} polygonOffsetUnits={-1} />
      </mesh>
      {/* Door panel */}
      <mesh
        position={[x + wall.normalX * 0.02, y, z + wall.normalZ * 0.02]}
        rotation={[0, wall.angle, 0]}
      >
        <planeGeometry args={[doorWidth, doorHeight]} />
        <meshStandardMaterial color="#5c3a1e" roughness={0.7} metalness={0.05} side={THREE.DoubleSide} polygonOffset polygonOffsetFactor={-2} polygonOffsetUnits={-2} />
      </mesh>
    </group>
  );
}

// =============================================================================
// Floor divider lines along every wall
// =============================================================================

function PolygonFloorDividers({
  walls,
  height,
  floors,
  floorHeight,
  color,
}: {
  walls: WallSegment[];
  height: number;
  floors: number;
  floorHeight: number;
  color: string;
}) {
  const dividerColor = useMemo(() => {
    const c = new THREE.Color(color);
    c.multiplyScalar(0.65);
    return '#' + c.getHexString();
  }, [color]);

  const dividers = useMemo(() => {
    const result: { pos: [number, number, number]; rotY: number; width: number }[] = [];
    for (let f = 1; f < floors; f++) {
      const y = f * floorHeight;
      for (const wall of walls) {
        result.push({
          pos: [wall.midX + wall.normalX * 0.06, y, wall.midZ + wall.normalZ * 0.06],
          rotY: wall.angle,
          width: wall.length + 0.1,
        });
      }
    }
    return result;
  }, [walls, floors, floorHeight]);

  return (
    <>
      {dividers.map((d, i) => (
        <mesh key={i} position={d.pos} rotation={[0, d.rotY, 0]}>
          <planeGeometry args={[d.width, 0.08]} />
          <meshStandardMaterial color={dividerColor} roughness={0.9} side={THREE.DoubleSide} polygonOffset polygonOffsetFactor={-1} polygonOffsetUnits={-1} />
        </mesh>
      ))}
    </>
  );
}

// =============================================================================
// Cornice ledge around roofline perimeter
// =============================================================================

function PolygonCornice({
  walls,
  height,
}: {
  walls: WallSegment[];
  height: number;
}) {
  return (
    <>
      {walls.map((wall, i) => (
        <mesh
          key={i}
          position={[
            wall.midX + wall.normalX * 0.15,
            height + 0.15,
            wall.midZ + wall.normalZ * 0.15,
          ]}
          rotation={[0, wall.angle, 0]}
        >
          <boxGeometry args={[wall.length + 0.3, 0.3, 0.3]} />
          <meshStandardMaterial color="#c0b8ac" roughness={0.8} />
        </mesh>
      ))}
    </>
  );
}

// =============================================================================
// Balconies on a wall (residential, upper floors)
// =============================================================================

function PolygonBalconies({
  wall,
  height,
  floors,
  floorHeight,
}: {
  wall: WallSegment;
  height: number;
  floors: number;
  floorHeight: number;
}) {
  const balconyWidth = Math.min(2.5, wall.length * 0.3);
  const balconyDepth = 1.2;

  const balconies = useMemo(() => {
    const result: { pos: [number, number, number]; rotY: number }[] = [];
    for (let f = 1; f < floors; f++) {
      const y = f * floorHeight;
      result.push({
        pos: [
          wall.midX + wall.normalX * (balconyDepth / 2 + 0.01),
          y,
          wall.midZ + wall.normalZ * (balconyDepth / 2 + 0.01),
        ],
        rotY: wall.angle,
      });
    }
    return result;
  }, [wall, floors, floorHeight, balconyDepth]);

  return (
    <>
      {balconies.map((b, i) => (
        <group key={i} position={b.pos} rotation={[0, b.rotY, 0]}>
          {/* Slab */}
          <mesh castShadow>
            <boxGeometry args={[balconyWidth, 0.15, balconyDepth]} />
            <meshStandardMaterial color="#b0a898" roughness={0.85} />
          </mesh>
          {/* Railing */}
          <mesh position={[0, 0.5, balconyDepth / 2]}>
            <boxGeometry args={[balconyWidth, 1.0, 0.05]} />
            <meshStandardMaterial color="#888888" roughness={0.6} metalness={0.3} />
          </mesh>
        </group>
      ))}
    </>
  );
}

// =============================================================================
// 2. ROAD ZONE — Ribbon mesh + center line + sidewalks
// =============================================================================

// Visual style per road surface type
interface RoadSurfaceStyle {
  color: string;
  roughness: number;
  metalness: number;
  sidewalkColor?: string;
  lineColor?: string;
  showLaneMarkings?: boolean;
}

const ROAD_SURFACE_STYLES: Record<string, RoadSurfaceStyle> = {
  asphalt: {
    color: '#3a3a3a',
    roughness: 0.90,
    metalness: 0.0,
    sidewalkColor: '#a0a0a0',
    lineColor: '#e0e0e0',
    showLaneMarkings: true,
  },
  cobblestone: {
    color: '#7a6b5a',
    roughness: 0.98,
    metalness: 0.0,
    sidewalkColor: '#9a9080',
    showLaneMarkings: false,
  },
  concrete: {
    color: '#8a8a88',
    roughness: 0.80,
    metalness: 0.0,
    sidewalkColor: '#a8a8a6',
    lineColor: '#d0d0d0',
    showLaneMarkings: true,
  },
  brick: {
    color: '#8b5e4b',
    roughness: 0.95,
    metalness: 0.0,
    sidewalkColor: '#a09080',
    showLaneMarkings: false,
  },
  gravel: {
    color: '#9a9080',
    roughness: 1.0,
    metalness: 0.0,
    sidewalkColor: '#a8a098',
    showLaneMarkings: false,
  },
  paver: {
    color: '#7a7068',
    roughness: 0.88,
    metalness: 0.02,
    sidewalkColor: '#9a9088',
    lineColor: '#c8c8c4',
    showLaneMarkings: true,
  },
};

// =============================================================================
// Road geometry helpers (module scope — used by RoadZone and RoadAestheticFurniture)
// =============================================================================

function buildFlatRibbon(
  _points: { x: number; z: number }[],
  verts: number[],
  idxs: number[],
): THREE.BufferGeometry | null {
  if (verts.length < 12) return null;
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geom.setIndex(idxs);
  const normals = new Float32Array(verts.length);
  for (let j = 1; j < normals.length; j += 3) normals[j] = 1;
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  return geom;
}

function buildOffsetRibbon(
  points: { x: number; z: number }[],
  innerDist: number,
  outerDist: number,
  yPos: number,
): THREE.BufferGeometry | null {
  if (points.length < 2) return null;

  const vertices: number[] = [];
  const indices: number[] = [];

  const d0 = Math.min(innerDist, outerDist);
  const d1 = Math.max(innerDist, outerDist);

  for (let i = 0; i < points.length; i++) {
    let dx = 0, dz = 0;
    if (i < points.length - 1) {
      dx += points[i + 1].x - points[i].x;
      dz += points[i + 1].z - points[i].z;
    }
    if (i > 0) {
      dx += points[i].x - points[i - 1].x;
      dz += points[i].z - points[i - 1].z;
    }
    const len = Math.sqrt(dx * dx + dz * dz) || 1;
    const nx = -dz / len;
    const nz = dx / len;

    vertices.push(
      points[i].x + nx * d0, yPos, points[i].z + nz * d0,
      points[i].x + nx * d1, yPos, points[i].z + nz * d1,
    );

    if (i < points.length - 1) {
      const base = i * 2;
      indices.push(base, base + 1, base + 2);
      indices.push(base + 1, base + 3, base + 2);
    }
  }

  return buildFlatRibbon(points, vertices, indices);
}

// =============================================================================
// Centerline walker — evenly-spaced placement points along road center
// =============================================================================

interface PlacementPoint {
  x: number; z: number;       // world position
  nx: number; nz: number;     // perpendicular normal (left = positive)
  angle: number;              // Y rotation (along road direction)
}

function walkCenterline(
  centerPoints: { x: number; z: number }[],
  spacing: number,
  startOffset = 0,
): PlacementPoint[] {
  if (centerPoints.length < 2 || spacing <= 0) return [];
  const result: PlacementPoint[] = [];
  let accDist = -startOffset;

  for (let i = 1; i < centerPoints.length; i++) {
    const prev = centerPoints[i - 1];
    const cur = centerPoints[i];
    const sdx = cur.x - prev.x;
    const sdz = cur.z - prev.z;
    const segLen = Math.sqrt(sdx * sdx + sdz * sdz);
    if (segLen < 0.001) continue;

    const dirX = sdx / segLen;
    const dirZ = sdz / segLen;
    const nx = -dirZ;
    const nz = dirX;
    const angle = Math.atan2(dirX, dirZ);

    const segStart = accDist;
    accDist += segLen;

    // Emit points at each spacing interval within this segment
    let nextEmit = Math.ceil(segStart / spacing) * spacing;
    while (nextEmit <= accDist) {
      const t = (nextEmit - segStart) / segLen;
      if (t >= 0 && t <= 1) {
        result.push({
          x: prev.x + sdx * t,
          z: prev.z + sdz * t,
          nx, nz, angle,
        });
      }
      nextEmit += spacing;
    }
  }
  return result;
}

// =============================================================================
// Road aesthetic furniture configs
// =============================================================================

interface FurnitureSlot {
  type: 'tree' | 'lightpole' | 'bollard' | 'bench' | 'railing';
  side: 'left' | 'right' | 'both';
  spacing: number;
}

interface AestheticConfig {
  furniture: FurnitureSlot[];
  median?: boolean;          // green median strip with trees (4+ lanes only)
}

const ROAD_AESTHETIC_CONFIGS: Record<string, AestheticConfig> = {
  grand_boulevard: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 10 },
      { type: 'lightpole', side: 'both', spacing: 15 },
    ],
    median: true,
  },
  neighborhood_high_street: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 8 },
      { type: 'lightpole', side: 'both', spacing: 12 },
    ],
  },
  curvilinear_residential: {
    furniture: [
      { type: 'tree', side: 'left', spacing: 12 },
      { type: 'lightpole', side: 'right', spacing: 20 },
    ],
  },
  pedestrian_focused: {
    furniture: [
      { type: 'lightpole', side: 'both', spacing: 10 },
      { type: 'bollard', side: 'both', spacing: 3 },
      { type: 'bench', side: 'right', spacing: 15 },
    ],
  },
  kyoto_philosophers_path: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 8 },
      { type: 'bench', side: 'both', spacing: 18 },
      { type: 'lightpole', side: 'both', spacing: 16 },
      { type: 'railing', side: 'left', spacing: 2 },
    ],
  },
  water_centric: {
    furniture: [
      { type: 'lightpole', side: 'right', spacing: 12 },
      { type: 'railing', side: 'left', spacing: 1.5 },
    ],
  },
  copenhagen_stroget: {
    furniture: [
      { type: 'bollard', side: 'both', spacing: 3.2 },
      { type: 'bench', side: 'both', spacing: 16 },
      { type: 'lightpole', side: 'both', spacing: 14 },
    ],
  },
  barcelona_la_rambla: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 8 },
      { type: 'bench', side: 'both', spacing: 18 },
      { type: 'lightpole', side: 'both', spacing: 16 },
    ],
  },
  venice_fondamenta_walk: {
    furniture: [
      { type: 'bench', side: 'both', spacing: 18 },
      { type: 'lightpole', side: 'both', spacing: 15 },
      { type: 'railing', side: 'both', spacing: 2.2 },
    ],
  },
  amsterdam_canal_street: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 9 },
      { type: 'bench', side: 'right', spacing: 16 },
      { type: 'railing', side: 'left', spacing: 2.4 },
      { type: 'lightpole', side: 'both', spacing: 16 },
    ],
  },
  copenhagen_cycle_superhighway: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 11 },
      { type: 'lightpole', side: 'both', spacing: 18 },
      { type: 'bollard', side: 'both', spacing: 4.5 },
    ],
  },
  bogota_cicloruta: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 10 },
      { type: 'lightpole', side: 'both', spacing: 14 },
    ],
    median: true,
  },
  utrecht_fietsstraat: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 11 },
      { type: 'bench', side: 'right', spacing: 20 },
      { type: 'lightpole', side: 'both', spacing: 18 },
    ],
  },
  seville_protected_cycle_track: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 9 },
      { type: 'lightpole', side: 'both', spacing: 14 },
      { type: 'bollard', side: 'both', spacing: 5 },
    ],
  },
  curitiba_brt_axis: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 12 },
      { type: 'lightpole', side: 'both', spacing: 15 },
      { type: 'bench', side: 'both', spacing: 24 },
    ],
    median: true,
  },
  bogota_transmilenio_avenue: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 11 },
      { type: 'lightpole', side: 'both', spacing: 14 },
    ],
    median: true,
  },
  hong_kong_tram_street: {
    furniture: [
      { type: 'lightpole', side: 'both', spacing: 12 },
      { type: 'bench', side: 'right', spacing: 20 },
      { type: 'tree', side: 'both', spacing: 13 },
    ],
  },
  zurich_tram_boulevard: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 10 },
      { type: 'lightpole', side: 'both', spacing: 13 },
    ],
    median: true,
  },
  portland_complete_street: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 10 },
      { type: 'bench', side: 'both', spacing: 18 },
      { type: 'lightpole', side: 'both', spacing: 15 },
      { type: 'bollard', side: 'both', spacing: 6 },
    ],
  },
  barcelona_superblock: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 8 },
      { type: 'bench', side: 'both', spacing: 14 },
      { type: 'bollard', side: 'both', spacing: 3.5 },
      { type: 'lightpole', side: 'both', spacing: 16 },
    ],
  },
  london_exhibition_road: {
    furniture: [
      { type: 'bollard', side: 'both', spacing: 3.5 },
      { type: 'bench', side: 'both', spacing: 17 },
      { type: 'lightpole', side: 'both', spacing: 14 },
      { type: 'tree', side: 'both', spacing: 12 },
    ],
  },
  paris_champs_elysees: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 9 },
      { type: 'lightpole', side: 'both', spacing: 14 },
      { type: 'bench', side: 'both', spacing: 20 },
    ],
    median: true,
  },
  mexico_city_reforma: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 9 },
      { type: 'lightpole', side: 'both', spacing: 13 },
      { type: 'bench', side: 'both', spacing: 18 },
    ],
    median: true,
  },
  tokyo_local_service_lane: {
    furniture: [
      { type: 'tree', side: 'both', spacing: 14 },
      { type: 'lightpole', side: 'both', spacing: 16 },
      { type: 'bench', side: 'right', spacing: 20 },
    ],
  },
  industrial_freight_collector: {
    furniture: [
      { type: 'lightpole', side: 'both', spacing: 24 },
    ],
  },
  industrial_collector: {
    furniture: [
      { type: 'lightpole', side: 'both', spacing: 24 },
    ],
  },
};


function DetailedTree({
  position,
  scale = 1,
  variant = 'deciduous',
}: {
  position: [number, number, number];
  scale?: number;
  variant?: TreeVariant;
}) {
  const canopyColor =
    variant === 'ornamental' ? '#d79ac8' :
    variant === 'conifer' ? '#2f6f35' :
    '#3c8743';

  return (
    <group position={position} scale={scale}>
      <mesh position={[0, 1.55, 0]} castShadow>
        <cylinderGeometry args={[0.14, 0.2, 3.1, 10]} />
        <meshStandardMaterial color="#6a4526" roughness={0.88} metalness={0.02} />
      </mesh>

      {variant === 'conifer' ? (
        <>
          <mesh position={[0, 2.9, 0]} castShadow>
            <coneGeometry args={[1.0, 2.2, 10]} />
            <meshStandardMaterial color="#2f6f35" roughness={0.82} />
          </mesh>
          <mesh position={[0, 3.8, 0]} castShadow>
            <coneGeometry args={[0.82, 2.0, 10]} />
            <meshStandardMaterial color="#316f39" roughness={0.82} />
          </mesh>
          <mesh position={[0, 4.6, 0]} castShadow>
            <coneGeometry args={[0.62, 1.6, 10]} />
            <meshStandardMaterial color="#2a6131" roughness={0.82} />
          </mesh>
        </>
      ) : (
        <>
          <mesh position={[0, 3.7, 0]} castShadow>
            <sphereGeometry args={[1.45, 14, 12]} />
            <meshStandardMaterial color={canopyColor} roughness={0.82} />
          </mesh>
          <mesh position={[0.95, 4.1, 0.2]} castShadow>
            <sphereGeometry args={[1.05, 12, 10]} />
            <meshStandardMaterial color={variant === 'ornamental' ? '#e4add6' : '#4a9550'} roughness={0.82} />
          </mesh>
          <mesh position={[-0.85, 4.0, -0.15]} castShadow>
            <sphereGeometry args={[0.95, 12, 10]} />
            <meshStandardMaterial color={variant === 'ornamental' ? '#d18ec1' : '#4f9654'} roughness={0.82} />
          </mesh>
        </>
      )}
    </group>
  );
}

function ZebraCrosswalk({
  position,
  angle,
  span,
  stripeCount = 7,
}: {
  position: [number, number, number];
  angle: number;
  span: number;
  stripeCount?: number;
}) {
  const stripeDepth = 0.34;
  const stripeGap = 0.26;
  const totalDepth = stripeCount * stripeDepth + (stripeCount - 1) * stripeGap;

  return (
    <group position={position} rotation={[0, angle, 0]}>
      {Array.from({ length: stripeCount }).map((_, idx) => {
        const z = -totalDepth / 2 + stripeDepth / 2 + idx * (stripeDepth + stripeGap);
        return (
          <mesh key={idx} position={[0, 0.176, z]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[span, stripeDepth]} />
            <meshStandardMaterial color="#f8f8f4" roughness={0.45} metalness={0.0} transparent opacity={0.86} depthWrite={false} />
          </mesh>
        );
      })}
    </group>
  );
}
function RoadZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const {
    roadGeometry, centerLineGeometry, leftSidewalk, rightSidewalk, measuredWidth,
    edgeLineLeftGeo, edgeLineRightGeo, laneDividerGeos, centerDividerGeo,
    gutterLeftGeo, gutterRightGeo, leftJointGeo, rightJointGeo, surfacePatternGeo,
    hasLeftSidewalk, hasRightSidewalk,
    centerPoints, halfWidth, laneCount, sidewalkWidth,
    crosswalkDescriptors,
  } = useMemo(() => {
    const n = points2D.length;
    if (n < 4) return {
      roadGeometry: null, centerLineGeometry: null, leftSidewalk: null, rightSidewalk: null, measuredWidth: 0,
      edgeLineLeftGeo: null, edgeLineRightGeo: null, laneDividerGeos: [] as THREE.BufferGeometry[],
      centerDividerGeo: null, gutterLeftGeo: null, gutterRightGeo: null,
      leftJointGeo: null, rightJointGeo: null, surfacePatternGeo: null,
      hasLeftSidewalk: false, hasRightSidewalk: false,
      centerPoints: [] as { x: number; z: number }[], halfWidth: 0, laneCount: 0, sidewalkWidth: 0,
      crosswalkDescriptors: [] as { position: [number, number, number]; angle: number; span: number }[],
    };

    // Reconstruct centerline from the buffered polygon:
    // polygon = [left0, left1, ..., leftM, rightM, ..., right0]
    // centerline[i] = midpoint(vertices[i], vertices[n-1-i])
    // Shape (x, y) → 3D (x, -y), so negate the y midpoint for world z
    const half = Math.floor(n / 2);
    const centerPoints: { x: number; z: number }[] = [];
    let totalWidth = 0;
    for (let i = 0; i < half; i++) {
      const a = points2D[i];
      const b = points2D[n - 1 - i];
      centerPoints.push({
        x: (a.x + b.x) / 2,
        z: -((a.y + b.y) / 2),
      });
      // Measure actual width from opposing polygon vertices
      totalWidth += a.distanceTo(b);
    }

    if (centerPoints.length < 2) return {
      roadGeometry: null, centerLineGeometry: null, leftSidewalk: null, rightSidewalk: null, measuredWidth: 0,
      edgeLineLeftGeo: null, edgeLineRightGeo: null, laneDividerGeos: [] as THREE.BufferGeometry[],
      centerDividerGeo: null, gutterLeftGeo: null, gutterRightGeo: null,
      leftJointGeo: null, rightJointGeo: null, surfacePatternGeo: null,
      hasLeftSidewalk: false, hasRightSidewalk: false,
      centerPoints: [] as { x: number; z: number }[], halfWidth: 0, laneCount: 0, sidewalkWidth: 0,
      crosswalkDescriptors: [] as { position: [number, number, number]; angle: number; span: number }[],
    };

    // Use the actual polygon width (average of opposing vertex distances)
    // instead of zone.properties.width which may not be saved/loaded correctly
    const roadWidth = half > 0 ? totalWidth / half : (zone.properties?.width ?? 10);
    const halfWidth = roadWidth / 2;
    const sidewalkWidth = 2.0;


    // Build ribbon geometry from centerline
    function buildRibbon(
      points: { x: number; z: number }[],
      hw: number,
      yPos: number,
    ): THREE.BufferGeometry | null {
      if (points.length < 2) return null;

      const vertices: number[] = [];
      const indices: number[] = [];

      for (let i = 0; i < points.length; i++) {
        let dx = 0, dz = 0;
        if (i < points.length - 1) {
          dx += points[i + 1].x - points[i].x;
          dz += points[i + 1].z - points[i].z;
        }
        if (i > 0) {
          dx += points[i].x - points[i - 1].x;
          dz += points[i].z - points[i - 1].z;
        }
        const len = Math.sqrt(dx * dx + dz * dz) || 1;
        const nx = -dz / len;
        const nz = dx / len;

        // Swap vertex order: right edge first, then left edge
        // This produces CCW winding (normals up) for the index pattern below
        vertices.push(
          points[i].x - nx * hw, yPos, points[i].z - nz * hw,
          points[i].x + nx * hw, yPos, points[i].z + nz * hw,
        );

        if (i < points.length - 1) {
          const base = i * 2;
          indices.push(base, base + 1, base + 2);
          indices.push(base + 1, base + 3, base + 2);
        }
      }

      return buildFlatRibbon(points, vertices, indices);
    }

    // Build a dashed ribbon (thin flat mesh with dash/gap pattern) at an offset from centerline
    function buildDashedRibbon(
      points: { x: number; z: number }[],
      offset: number,
      ribbonHalfW: number,
      yPos: number,
      dashLen: number,
      gapLen: number,
    ): THREE.BufferGeometry | null {
      if (points.length < 2) return null;

      // Precompute normals at each point
      const normals: { nx: number; nz: number }[] = [];
      for (let i = 0; i < points.length; i++) {
        let dx = 0, dz = 0;
        if (i < points.length - 1) { dx += points[i + 1].x - points[i].x; dz += points[i + 1].z - points[i].z; }
        if (i > 0) { dx += points[i].x - points[i - 1].x; dz += points[i].z - points[i - 1].z; }
        const len = Math.sqrt(dx * dx + dz * dz) || 1;
        normals.push({ nx: -dz / len, nz: dx / len });
      }

      // Walk the centerline accumulating distance, emitting ribbon segments during "dash" phases
      const dashSegments: { x: number; z: number }[][] = [];
      let accDist = 0;
      let currentSeg: { x: number; z: number }[] = [];
      const cycleLen = dashLen + gapLen;

      for (let i = 0; i < points.length; i++) {
        if (i > 0) {
          const segDx = points[i].x - points[i - 1].x;
          const segDz = points[i].z - points[i - 1].z;
          accDist += Math.sqrt(segDx * segDx + segDz * segDz);
        }

        const phase = accDist % cycleLen;
        const inDash = phase < dashLen;

        const px = points[i].x + normals[i].nx * offset;
        const pz = points[i].z + normals[i].nz * offset;

        if (inDash) {
          currentSeg.push({ x: px, z: pz });
        } else {
          if (currentSeg.length >= 2) {
            dashSegments.push(currentSeg);
          }
          currentSeg = [];
        }
      }
      if (currentSeg.length >= 2) dashSegments.push(currentSeg);

      // Combine all dash segments into one geometry
      const allVerts: number[] = [];
      const allIdx: number[] = [];
      let vertOffset = 0;

      for (const seg of dashSegments) {
        for (let i = 0; i < seg.length; i++) {
          // Compute local perpendicular for ribbon width
          let dx = 0, dz = 0;
          if (i < seg.length - 1) { dx += seg[i + 1].x - seg[i].x; dz += seg[i + 1].z - seg[i].z; }
          if (i > 0) { dx += seg[i].x - seg[i - 1].x; dz += seg[i].z - seg[i - 1].z; }
          const len = Math.sqrt(dx * dx + dz * dz) || 1;
          const rnx = -dz / len;
          const rnz = dx / len;

          allVerts.push(
            seg[i].x - rnx * ribbonHalfW, yPos, seg[i].z - rnz * ribbonHalfW,
            seg[i].x + rnx * ribbonHalfW, yPos, seg[i].z + rnz * ribbonHalfW,
          );

          if (i < seg.length - 1) {
            const base = vertOffset + i * 2;
            allIdx.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
          }
        }
        vertOffset += seg.length * 2;
      }

      return buildFlatRibbon([], allVerts, allIdx);
    }

    // Build perpendicular joint lines across sidewalk at regular intervals
    function buildSidewalkJoints(
      points: { x: number; z: number }[],
      innerDist: number,
      outerDist: number,
      yPos: number,
      spacing: number,
    ): THREE.BufferGeometry | null {
      if (points.length < 2) return null;

      const positions: number[] = [];
      let accDist = 0;
      let nextJoint = spacing;

      for (let i = 1; i < points.length; i++) {
        const segDx = points[i].x - points[i - 1].x;
        const segDz = points[i].z - points[i - 1].z;
        const segLen = Math.sqrt(segDx * segDx + segDz * segDz);
        accDist += segLen;

        while (accDist >= nextJoint && i < points.length) {
          // Interpolate position along segment
          const overshoot = accDist - nextJoint;
          const t = 1 - overshoot / segLen;
          const px = points[i - 1].x + segDx * t;
          const pz = points[i - 1].z + segDz * t;

          // Perpendicular normal
          const len = segLen || 1;
          const nx = -segDz / len;
          const nz = segDx / len;

          // Line from inner edge to outer edge of sidewalk
          positions.push(
            px + nx * innerDist, yPos, pz + nz * innerDist,
            px + nx * outerDist, yPos, pz + nz * outerDist,
          );

          nextJoint += spacing;
        }
      }

      if (positions.length < 6) return null;

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      return geom;
    }

    // Build surface pattern lines (grid for cobblestone/paver, herringbone for brick)
    function buildSurfacePattern(
      points: { x: number; z: number }[],
      hw: number,
      yPos: number,
      surface: string,
    ): THREE.BufferGeometry | null {
      if (points.length < 2) return null;

      const positions: number[] = [];

      // Precompute normals
      const normals: { nx: number; nz: number; dx: number; dz: number }[] = [];
      for (let i = 0; i < points.length; i++) {
        let dx = 0, dz = 0;
        if (i < points.length - 1) { dx += points[i + 1].x - points[i].x; dz += points[i + 1].z - points[i].z; }
        if (i > 0) { dx += points[i].x - points[i - 1].x; dz += points[i].z - points[i - 1].z; }
        const len = Math.sqrt(dx * dx + dz * dz) || 1;
        normals.push({ nx: -dz / len, nz: dx / len, dx: dx / len, dz: dz / len });
      }

      if (surface === 'brick') {
        // Herringbone: diagonal lines at ~45 degrees across the road
        let accDist = 0;
        const spacing = 0.6;

        for (let i = 1; i < points.length; i++) {
          const segDx = points[i].x - points[i - 1].x;
          const segDz = points[i].z - points[i - 1].z;
          const segLen = Math.sqrt(segDx * segDx + segDz * segDz);
          accDist += segLen;

          while (accDist >= spacing) {
            accDist -= spacing;
            const t = 1 - accDist / segLen;
            const px = points[i - 1].x + segDx * t;
            const pz = points[i - 1].z + segDz * t;
            const n = normals[i];

            // Diagonal line: offset perpendicular + along direction
            const diagLen = hw * 0.8;
            positions.push(
              px + n.nx * diagLen + n.dx * diagLen * 0.3, yPos, pz + n.nz * diagLen + n.dz * diagLen * 0.3,
              px - n.nx * diagLen - n.dx * diagLen * 0.3, yPos, pz - n.nz * diagLen - n.dz * diagLen * 0.3,
            );
          }
        }
      } else {
        // Cobblestone / paver: transverse + longitudinal grid
        const transverseSpacing = 0.5;
        const longitudinalSpacing = 0.8;

        // Transverse lines (across road)
        let accDist = 0;
        for (let i = 1; i < points.length; i++) {
          const segDx = points[i].x - points[i - 1].x;
          const segDz = points[i].z - points[i - 1].z;
          const segLen = Math.sqrt(segDx * segDx + segDz * segDz);
          accDist += segLen;

          while (accDist >= transverseSpacing) {
            accDist -= transverseSpacing;
            const t = 1 - accDist / segLen;
            const px = points[i - 1].x + segDx * t;
            const pz = points[i - 1].z + segDz * t;
            const n = normals[i];

            positions.push(
              px + n.nx * hw, yPos, pz + n.nz * hw,
              px - n.nx * hw, yPos, pz - n.nz * hw,
            );
          }
        }

        // Longitudinal lines (along road at fixed offsets)
        const numLong = Math.floor(hw * 2 / longitudinalSpacing);
        for (let li = 1; li < numLong; li++) {
          const offset = -hw + li * longitudinalSpacing;
          for (let i = 0; i < points.length - 1; i++) {
            const n0 = normals[i];
            const n1 = normals[i + 1];
            positions.push(
              points[i].x + n0.nx * offset, yPos, points[i].z + n0.nz * offset,
              points[i + 1].x + n1.nx * offset, yPos, points[i + 1].z + n1.nz * offset,
            );
          }
        }
      }

      if (positions.length < 6) return null;

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      return geom;
    }

    const roadGeom = buildRibbon(centerPoints, halfWidth, 0.15);

    // --- Shared surface info ---
    const surface = (zone.properties?.road_surface as string) || 'asphalt';
    const style = ROAD_SURFACE_STYLES[surface] || ROAD_SURFACE_STYLES.asphalt;

    // Add per-vertex color variation to road surface for weathered look
    if (roadGeom) {
      const posAttr = roadGeom.getAttribute('position');
      const vertCount = posAttr.count;
      const colors = new Float32Array(vertCount * 3);
      const baseColor = new THREE.Color(style.color);
      const rand = makeRand(centerPoints.length * 7 + 31);
      for (let v = 0; v < vertCount; v++) {
        const noise = (rand() - 0.5) * 0.04; // ±0.02 RGB
        colors[v * 3] = Math.max(0, Math.min(1, baseColor.r + noise));
        colors[v * 3 + 1] = Math.max(0, Math.min(1, baseColor.g + noise));
        colors[v * 3 + 2] = Math.max(0, Math.min(1, baseColor.b + noise));
      }
      roadGeom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    }

    // Center line points
    const linePoints = centerPoints.map((p) => new THREE.Vector3(p.x, 0.18, p.z));
    const centerLineGeom = new THREE.BufferGeometry().setFromPoints(linePoints);

    // Sidewalks: left side (positive normal direction), right side (negative)
    const gap = 0.3; // gap between road edge and sidewalk (curb)
    const leftInner = halfWidth + gap;
    const leftOuter = halfWidth + gap + sidewalkWidth;
    const rightInner = -(halfWidth + gap);
    const rightOuter = -(halfWidth + gap + sidewalkWidth);

    // Determine per-side sidewalk visibility
    const sidewalkSetting = (zone.properties?.sidewalks as string) || (zone.properties?.has_sidewalks === false ? 'none' : 'both');
    const hasLeftSidewalk = sidewalkSetting === 'both' || sidewalkSetting === 'left';
    const hasRightSidewalk = sidewalkSetting === 'both' || sidewalkSetting === 'right';

    const leftSW = hasLeftSidewalk ? buildOffsetRibbon(centerPoints, leftInner, leftOuter, 0.20) : null;
    const rightSW = hasRightSidewalk ? buildOffsetRibbon(centerPoints, rightInner, rightOuter, 0.20) : null;

    // --- Detail layers ---
    const laneCount = (zone.properties?.lane_count as number) || 2;

    // Edge lines: solid white ribbons along left and right road edges
    let edgeLineLeftGeo: THREE.BufferGeometry | null = null;
    let edgeLineRightGeo: THREE.BufferGeometry | null = null;
    if (style.showLaneMarkings) {
      const edgeOffset = halfWidth - 0.15;
      edgeLineLeftGeo = buildOffsetRibbon(centerPoints, edgeOffset - 0.06, edgeOffset + 0.06, 0.17);
      edgeLineRightGeo = buildOffsetRibbon(centerPoints, -(edgeOffset - 0.06), -(edgeOffset + 0.06), 0.17);
    }

    // Lane divider lines: dashed white ribbons between lanes
    const laneDividerGeoList: THREE.BufferGeometry[] = [];
    if (style.showLaneMarkings && laneCount > 1) {
      const laneWidth = roadWidth / laneCount;
      for (let lane = 1; lane < laneCount; lane++) {
        const offset = -halfWidth + lane * laneWidth;
        const geo = buildDashedRibbon(centerPoints, offset, 0.06, 0.17, 3, 3);
        if (geo) laneDividerGeoList.push(geo);
      }
    }

    // Center divider: solid yellow ribbon for even lane counts (opposing traffic)
    let centerDividerGeo: THREE.BufferGeometry | null = null;
    if (style.showLaneMarkings && laneCount >= 2 && laneCount % 2 === 0) {
      centerDividerGeo = buildOffsetRibbon(centerPoints, -0.05, 0.05, 0.18);
    }

    // Gutter strips: dark narrow ribbons between road edge and curb
    let gutterLeftGeo: THREE.BufferGeometry | null = null;
    let gutterRightGeo: THREE.BufferGeometry | null = null;
    if (hasLeftSidewalk) {
      gutterLeftGeo = buildOffsetRibbon(centerPoints, halfWidth, halfWidth + 0.2, 0.16);
    }
    if (hasRightSidewalk) {
      gutterRightGeo = buildOffsetRibbon(centerPoints, -halfWidth, -(halfWidth + 0.2), 0.16);
    }

    // Sidewalk expansion joints
    let leftJointGeo: THREE.BufferGeometry | null = null;
    let rightJointGeo: THREE.BufferGeometry | null = null;
    if (hasLeftSidewalk) {
      leftJointGeo = buildSidewalkJoints(centerPoints, leftInner, leftOuter, 0.11, 1.5);
    }
    if (hasRightSidewalk) {
      rightJointGeo = buildSidewalkJoints(centerPoints, rightInner, rightOuter, 0.11, 1.5);
    }

    // Surface pattern lines (cobblestone/brick/paver only)
    let surfacePatternGeo: THREE.BufferGeometry | null = null;
    if (!style.showLaneMarkings && (surface === 'cobblestone' || surface === 'brick' || surface === 'paver')) {
      surfacePatternGeo = buildSurfacePattern(centerPoints, halfWidth, 0.165, surface);
    }

    // Crosswalk anchors near each road end for better pedestrian readability.
    const crosswalkDescriptors: { position: [number, number, number]; angle: number; span: number }[] = [];
    const totalLen = polylineLength(centerPoints);
    if (style.showLaneMarkings && totalLen > 12 && (hasLeftSidewalk || hasRightSidewalk)) {
      const edgeInset = Math.min(Math.max(2.2, roadWidth * 0.32), totalLen / 3);
      const first = sampleCenterlineAtDistance(centerPoints, edgeInset);
      const last = sampleCenterlineAtDistance(centerPoints, Math.max(edgeInset, totalLen - edgeInset));
      const span = Math.max(2.4, roadWidth * 0.88);
      if (first) crosswalkDescriptors.push({ position: [first.x, 0, first.z], angle: first.angle, span });
      if (last && (!first || Math.hypot(last.x - first.x, last.z - first.z) > 4)) {
        crosswalkDescriptors.push({ position: [last.x, 0, last.z], angle: last.angle, span });
      }
    }

    return {
      roadGeometry: roadGeom,
      centerLineGeometry: centerLineGeom,
      leftSidewalk: leftSW,
      rightSidewalk: rightSW,
      measuredWidth: roadWidth,
      edgeLineLeftGeo,
      edgeLineRightGeo,
      laneDividerGeos: laneDividerGeoList,
      centerDividerGeo,
      gutterLeftGeo,
      gutterRightGeo,
      leftJointGeo,
      rightJointGeo,
      surfacePatternGeo,
      hasLeftSidewalk,
      hasRightSidewalk,
      centerPoints,
      halfWidth,
      laneCount,
      sidewalkWidth,
      crosswalkDescriptors,
    };
  }, [points2D, zone.properties]);

  const surfaceMat = useMemo(() => {
    const surface = (zone.properties?.road_surface as string) || 'asphalt';
    return ROAD_SURFACE_STYLES[surface] || ROAD_SURFACE_STYLES.asphalt;
  }, [zone.properties?.road_surface]);

  // Whether to show center lane markings (not for cobblestone/brick/gravel — they don't have lane markings)
  const showCenterLine = surfaceMat.showLaneMarkings !== false;

  if (!roadGeometry) return null;

  const surface = (zone.properties?.road_surface as string) || 'asphalt';
  const surfacePatternColor = surface === 'brick' ? '#5a3a2a' : '#4a3a2a';
  const surfacePatternOpacity = surface === 'brick' ? 0.20 : 0.18;

  return (
    <group>
      {/* Road surface — with vertex colors for weathered variation */}
      <mesh geometry={roadGeometry} receiveShadow>
        <meshStandardMaterial
          vertexColors
          roughness={surfaceMat.roughness}
          metalness={surfaceMat.metalness}
          polygonOffset
          polygonOffsetFactor={1}
          polygonOffsetUnits={1}
        />
      </mesh>

      {/* Gutter strips — dark narrow bands between road edge and curb */}
      {gutterLeftGeo && (
        <mesh geometry={gutterLeftGeo}>
          <meshStandardMaterial color="#2a2a2a" roughness={0.95} metalness={0.0} />
        </mesh>
      )}
      {gutterRightGeo && (
        <mesh geometry={gutterRightGeo}>
          <meshStandardMaterial color="#2a2a2a" roughness={0.95} metalness={0.0} />
        </mesh>
      )}

      {/* Surface pattern lines — cobblestone/brick/paver grid/herringbone */}
      {surfacePatternGeo && (
        <lineSegments geometry={surfacePatternGeo}>
          <lineBasicMaterial color={surfacePatternColor} transparent opacity={surfacePatternOpacity} />
        </lineSegments>
      )}

      {/* Edge lines — solid white ribbons at road edges */}
      {edgeLineLeftGeo && (
        <mesh geometry={edgeLineLeftGeo}>
          <meshStandardMaterial color="#ffffff" transparent opacity={0.6} roughness={0.5} metalness={0.0} depthWrite={false} />
        </mesh>
      )}
      {edgeLineRightGeo && (
        <mesh geometry={edgeLineRightGeo}>
          <meshStandardMaterial color="#ffffff" transparent opacity={0.6} roughness={0.5} metalness={0.0} depthWrite={false} />
        </mesh>
      )}

      {/* Lane divider lines — dashed white ribbons between lanes */}
      {laneDividerGeos.map((geo, i) => (
        <mesh key={`lane-div-${i}`} geometry={geo}>
          <meshStandardMaterial color="#ffffff" transparent opacity={0.7} roughness={0.5} metalness={0.0} depthWrite={false} />
        </mesh>
      ))}

      {/* Center divider — solid yellow ribbon for opposing traffic (even lane counts) */}
      {centerDividerGeo && (
        <mesh geometry={centerDividerGeo}>
          <meshStandardMaterial color="#e8b800" transparent opacity={0.85} roughness={0.5} metalness={0.0} depthWrite={false} />
        </mesh>
      )}

      {/* Center line stripe — fallback for odd lane counts with lane markings */}
      {showCenterLine && !centerDividerGeo && centerLineGeometry && (
        <line geometry={centerLineGeometry}>
          <lineBasicMaterial color={surfaceMat.lineColor || '#e0e0e0'} transparent opacity={0.7} />
        </line>
      )}

      {/* End crosswalks */}
      {crosswalkDescriptors.map((cw, i) => (
        <ZebraCrosswalk
          key={`crosswalk-${i}`}
          position={cw.position}
          angle={cw.angle}
          span={cw.span}
        />
      ))}


      {/* Sidewalks — per-side based on sidewalks property */}
      {leftSidewalk && (
        <mesh geometry={leftSidewalk} receiveShadow>
          <meshStandardMaterial color={surfaceMat.sidewalkColor || '#a0a0a0'} roughness={0.85} metalness={0.0} />
        </mesh>
      )}
      {rightSidewalk && (
        <mesh geometry={rightSidewalk} receiveShadow>
          <meshStandardMaterial color={surfaceMat.sidewalkColor || '#a0a0a0'} roughness={0.85} metalness={0.0} />
        </mesh>
      )}

      {/* Sidewalk expansion joints — perpendicular lines every ~1.5m */}
      {leftJointGeo && (
        <lineSegments geometry={leftJointGeo}>
          <lineBasicMaterial color="#888888" transparent opacity={0.35} />
        </lineSegments>
      )}
      {rightJointGeo && (
        <lineSegments geometry={rightJointGeo}>
          <lineBasicMaterial color="#888888" transparent opacity={0.35} />
        </lineSegments>
      )}

      {/* Curb lines — per-side */}
      {(hasLeftSidewalk || hasRightSidewalk) && (
        <RoadCurbs points2D={points2D} roadWidth={measuredWidth} showLeft={hasLeftSidewalk} showRight={hasRightSidewalk} />
      )}

      {/* Road aesthetic street furniture */}
      {centerPoints.length >= 2 && (
        <RoadAestheticFurniture
          aesthetic={(zone.properties?.road_aesthetic as string) || ''}
          centerPoints={centerPoints}
          halfWidth={halfWidth}
          laneCount={laneCount}
          sidewalkWidth={sidewalkWidth}
          hasLeftSidewalk={hasLeftSidewalk}
          hasRightSidewalk={hasRightSidewalk}
        />
      )}
    </group>
  );
}

// =============================================================================
// Road aesthetic furniture — trees, poles, bollards, benches, median, railing
// =============================================================================

function RoadAestheticFurniture({
  aesthetic,
  centerPoints,
  halfWidth,
  laneCount,
  sidewalkWidth,
  hasLeftSidewalk,
  hasRightSidewalk,
}: {
  aesthetic: string;
  centerPoints: { x: number; z: number }[];
  halfWidth: number;
  laneCount: number;
  sidewalkWidth: number;
  hasLeftSidewalk: boolean;
  hasRightSidewalk: boolean;
}) {
  const elements = useMemo(() => {
    const config = ROAD_AESTHETIC_CONFIGS[aesthetic] || ROAD_AESTHETIC_CONFIGS.neighborhood_high_street;
    if (centerPoints.length < 2) return null;

    const trees: { pos: [number, number, number]; scale: number; type: TreeVariant }[] = [];
    const poles: [number, number, number][] = [];
    const bollards: [number, number, number][] = [];
    const benches: { pos: [number, number, number]; rot: number }[] = [];
    const railingPosts: { pos: [number, number, number]; angle: number }[] = [];

    // Sidewalk midpoint offset from road edge
    const swMid = halfWidth + sidewalkWidth / 2;
    // Inner sidewalk edge (near road)
    const swInner = halfWidth + 0.3;
    // Outer sidewalk edge
    const swOuter = halfWidth + sidewalkWidth - 0.3;

    const rand = makeRand(Math.abs(Math.round(centerPoints[0].x * 100)) + centerPoints.length * 7);

    for (const slot of config.furniture) {
      const points = walkCenterline(centerPoints, slot.spacing, slot.spacing * 0.3);
      const sides: ('left' | 'right')[] =
        slot.side === 'both' ? ['left', 'right'] :
        [slot.side];

      for (const side of sides) {
        if (side === 'left' && !hasLeftSidewalk) continue;
        if (side === 'right' && !hasRightSidewalk) continue;

        const sign = side === 'left' ? 1 : -1;
        let count = 0;

        for (const pt of points) {
          if (count >= 100) break;

          if (slot.type === 'tree') {
            const offset = swMid * sign;
            trees.push({
              pos: [pt.x + pt.nx * offset, 0, pt.z + pt.nz * offset],
              scale: 0.7 + rand() * 0.5,
              type: aesthetic === 'kyoto_philosophers_path' ? (rand() > 0.45 ? 'ornamental' : 'deciduous') : (rand() > 0.35 ? 'deciduous' : 'conifer'),
            });
          } else if (slot.type === 'lightpole') {
            const offset = swOuter * sign;
            poles.push([pt.x + pt.nx * offset, 0, pt.z + pt.nz * offset]);
          } else if (slot.type === 'bollard') {
            const offset = swInner * sign;
            bollards.push([pt.x + pt.nx * offset, 0, pt.z + pt.nz * offset]);
          } else if (slot.type === 'bench') {
            const offset = swMid * sign;
            benches.push({
              pos: [pt.x + pt.nx * offset, 0, pt.z + pt.nz * offset],
              rot: pt.angle + (side === 'right' ? Math.PI : 0),
            });
          } else if (slot.type === 'railing') {
            const offset = swOuter * sign;
            railingPosts.push({
              pos: [pt.x + pt.nx * offset, 0, pt.z + pt.nz * offset],
              angle: pt.angle,
            });
          }
          count++;
        }
      }
    }

    // Median strip (grand_boulevard with 4+ lanes)
    let medianGeo: THREE.BufferGeometry | null = null;
    const medianTrees: { pos: [number, number, number]; scale: number; type: TreeVariant }[] = [];
    if (config.median && laneCount >= 4) {
      const medianHalf = 0.8;
      medianGeo = buildOffsetRibbon(centerPoints, -medianHalf, medianHalf, 0.18);
      // Place smaller trees along the median
      const medianPts = walkCenterline(centerPoints, 12, 4);
      let mCount = 0;
      for (const pt of medianPts) {
        if (mCount >= 100) break;
        medianTrees.push({
          pos: [pt.x, 0, pt.z],
          scale: 0.5 + rand() * 0.3,
          type: 'deciduous',
        });
        mCount++;
      }
    }

    return { trees, poles, bollards, benches, railingPosts, medianGeo, medianTrees };
  }, [aesthetic, centerPoints, halfWidth, laneCount, sidewalkWidth, hasLeftSidewalk, hasRightSidewalk]);

  if (!elements) return null;

  const { trees, poles, bollards, benches, railingPosts, medianGeo, medianTrees } = elements;

  return (
    <group>
      {/* Street trees */}
      {trees.map((t, i) => (
        <DetailedTree key={`st-${i}`} position={t.pos} scale={t.scale} variant={t.type} />
      ))}

      {/* Light poles */}
      {poles.map((p, i) => (
        <LightPole key={`lp-${i}`} position={p} />
      ))}

      {/* Bollards */}
      {bollards.map((p, i) => (
        <Bollard key={`bl-${i}`} position={p} />
      ))}

      {/* Benches */}
      {benches.map((b, i) => (
        <Bench key={`bn-${i}`} position={b.pos} rotation={b.rot} />
      ))}

      {/* Railing (water_centric) */}
      {railingPosts.map((r, i) => (
        <group key={`rl-${i}`} position={r.pos}>
          {/* Vertical post */}
          <mesh position={[0, 0.45, 0]} castShadow>
            <cylinderGeometry args={[0.03, 0.03, 0.9, 6]} />
            <meshStandardMaterial color="#5a5a5a" roughness={0.3} metalness={0.8} />
          </mesh>
          {/* Top horizontal rail bar */}
          <mesh position={[0, 0.9, 0]} rotation={[0, r.angle, Math.PI / 2]}>
            <cylinderGeometry args={[0.025, 0.025, 1.5, 4]} />
            <meshStandardMaterial color="#5a5a5a" roughness={0.3} metalness={0.8} />
          </mesh>
        </group>
      ))}

      {/* Median strip (green ribbon + trees) */}
      {medianGeo && (
        <mesh geometry={medianGeo} receiveShadow>
          <meshStandardMaterial color="#4a8c3f" roughness={0.9} />
        </mesh>
      )}
      {medianTrees.map((t, i) => (
        <DetailedTree key={`mt-${i}`} position={t.pos} scale={t.scale} variant={t.type} />
      ))}
    </group>
  );
}

/** Thin curb strips along road edges */
function RoadCurbs({
  points2D,
  roadWidth,
  showLeft = true,
  showRight = true,
}: {
  points2D: THREE.Vector2[];
  roadWidth: number;
  showLeft?: boolean;
  showRight?: boolean;
}) {
  const curbGeometries = useMemo(() => {
    const n = points2D.length;
    if (n < 4) return { left: null, right: null };

    const half = Math.floor(n / 2);
    const centerPoints: { x: number; z: number }[] = [];
    for (let i = 0; i < half; i++) {
      const a = points2D[i];
      const b = points2D[n - 1 - i];
      centerPoints.push({ x: (a.x + b.x) / 2, z: -((a.y + b.y) / 2) });
    }

    if (centerPoints.length < 2) return { left: null, right: null };

    const halfWidth = roadWidth / 2;
    const curbHalfW = 0.1;

    function buildCurbLine(sign: number): THREE.BufferGeometry | null {
      const verts: number[] = [];
      const idx: number[] = [];

      for (let i = 0; i < centerPoints.length; i++) {
        let dx = 0, dz = 0;
        if (i < centerPoints.length - 1) { dx += centerPoints[i + 1].x - centerPoints[i].x; dz += centerPoints[i + 1].z - centerPoints[i].z; }
        if (i > 0) { dx += centerPoints[i].x - centerPoints[i - 1].x; dz += centerPoints[i].z - centerPoints[i - 1].z; }
        const len = Math.sqrt(dx * dx + dz * dz) || 1;
        const nx = -dz / len;
        const nz = dx / len;

        const cx = centerPoints[i].x + nx * sign * (halfWidth + 0.15);
        const cz = centerPoints[i].z + nz * sign * (halfWidth + 0.15);

        // Swap vertex order for CCW winding (normals up)
        verts.push(
          cx - nx * curbHalfW, 0.15, cz - nz * curbHalfW,
          cx + nx * curbHalfW, 0.15, cz + nz * curbHalfW,
        );

        if (i < centerPoints.length - 1) {
          const base = i * 2;
          idx.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
        }
      }

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
      geom.setIndex(idx);
      // Explicit upward normals for flat surface
      const normals = new Float32Array(verts.length);
      for (let j = 1; j < normals.length; j += 3) normals[j] = 1;
      geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
      return geom;
    }

    return {
      left: showLeft ? buildCurbLine(1) : null,
      right: showRight ? buildCurbLine(-1) : null,
    };
  }, [points2D, roadWidth, showLeft, showRight]);

  return (
    <>
      {curbGeometries.left && (
        <mesh geometry={curbGeometries.left}>
          <meshStandardMaterial color="#888888" roughness={0.8} />
        </mesh>
      )}
      {curbGeometries.right && (
        <mesh geometry={curbGeometries.right}>
          <meshStandardMaterial color="#888888" roughness={0.8} />
        </mesh>
      )}
    </>
  );
}

interface GreenSpaceVisualConfig {
  groundColor: string;
  groundAccentColor: string;
  pathColor: string;
  shrubColor: string;
  pathPattern: 'organic' | 'formal' | 'linear' | 'boardwalk';
  pathCount: number;
  treeVariants: TreeVariant[];
  shrubDensity: number;
}

const GREEN_SPACE_VISUAL_CONFIGS: Record<string, GreenSpaceVisualConfig> = {
  default: {
    groundColor: '#4a8c3f',
    groundAccentColor: '#6ba35d',
    pathColor: '#c5b59a',
    shrubColor: '#4e8c48',
    pathPattern: 'organic',
    pathCount: 2,
    treeVariants: ['deciduous', 'conifer'],
    shrubDensity: 1,
  },
  central_park_english_landscape: {
    groundColor: '#5b9648',
    groundAccentColor: '#7bbd63',
    pathColor: '#ccb997',
    shrubColor: '#4f8e45',
    pathPattern: 'organic',
    pathCount: 3,
    treeVariants: ['deciduous', 'deciduous', 'conifer'],
    shrubDensity: 1.2,
  },
  versailles_formal_garden: {
    groundColor: '#75a35a',
    groundAccentColor: '#8fc072',
    pathColor: '#d8c8a8',
    shrubColor: '#6d984f',
    pathPattern: 'formal',
    pathCount: 3,
    treeVariants: ['deciduous'],
    shrubDensity: 1.4,
  },
  high_line_linear_park: {
    groundColor: '#5f8f4d',
    groundAccentColor: '#7dad66',
    pathColor: '#8f8b7a',
    shrubColor: '#4f8452',
    pathPattern: 'linear',
    pathCount: 2,
    treeVariants: ['deciduous', 'ornamental'],
    shrubDensity: 1.25,
  },
  philosophers_path_garden: {
    groundColor: '#5f944f',
    groundAccentColor: '#84b76e',
    pathColor: '#b8b1a2',
    shrubColor: '#5b904f',
    pathPattern: 'linear',
    pathCount: 2,
    treeVariants: ['ornamental', 'ornamental', 'deciduous'],
    shrubDensity: 1.1,
  },
  superkilen_cultural_park: {
    groundColor: '#5d8d46',
    groundAccentColor: '#75aa5f',
    pathColor: '#8f3e3e',
    shrubColor: '#5f8a4a',
    pathPattern: 'linear',
    pathCount: 2,
    treeVariants: ['deciduous'],
    shrubDensity: 0.75,
  },
  civic_lawn_commons: {
    groundColor: '#63a24f',
    groundAccentColor: '#7ac55f',
    pathColor: '#c8c1ab',
    shrubColor: '#4b8a45',
    pathPattern: 'organic',
    pathCount: 1,
    treeVariants: ['deciduous', 'conifer'],
    shrubDensity: 0.8,
  },
  houtan_ecological_park: {
    groundColor: '#557f43',
    groundAccentColor: '#6ea45b',
    pathColor: '#a58a63',
    shrubColor: '#507c48',
    pathPattern: 'boardwalk',
    pathCount: 2,
    treeVariants: ['conifer', 'deciduous'],
    shrubDensity: 1.35,
  },
  bishan_river_park: {
    groundColor: '#5a8b48',
    groundAccentColor: '#74b561',
    pathColor: '#ad997a',
    shrubColor: '#4d7f47',
    pathPattern: 'organic',
    pathCount: 2,
    treeVariants: ['deciduous', 'conifer'],
    shrubDensity: 1.2,
  },
  wetland_boardwalk_park: {
    groundColor: '#4f7a3f',
    groundAccentColor: '#669b52',
    pathColor: '#9a7c57',
    shrubColor: '#4f7a44',
    pathPattern: 'boardwalk',
    pathCount: 3,
    treeVariants: ['conifer', 'deciduous'],
    shrubDensity: 1.4,
  },
  botanical_garden: {
    groundColor: '#5f944e',
    groundAccentColor: '#83c169',
    pathColor: '#c6ba9b',
    shrubColor: '#4f8a4c',
    pathPattern: 'organic',
    pathCount: 3,
    treeVariants: ['ornamental', 'deciduous', 'conifer'],
    shrubDensity: 1.6,
  },
};

function resolveGreenSpaceVisualConfig(aesthetic?: string): GreenSpaceVisualConfig {
  if (!aesthetic) return GREEN_SPACE_VISUAL_CONFIGS.default;
  return GREEN_SPACE_VISUAL_CONFIGS[aesthetic] || GREEN_SPACE_VISUAL_CONFIGS.default;
}

function ParkPathNetwork({
  points2D,
  visual,
  enabled,
}: {
  points2D: THREE.Vector2[];
  visual: GreenSpaceVisualConfig;
  enabled: boolean;
}) {
  const pathGeometries = useMemo(() => {
    if (!enabled || points2D.length < 3) return [] as THREE.BufferGeometry[];

    const bounds = computePolygonBounds(points2D);
    if (bounds.area < 140) return [] as THREE.BufferGeometry[];

    const majorAxisIsX = bounds.width >= bounds.height;
    const crossSpan = majorAxisIsX ? bounds.height : bounds.width;
    const alongSpan = majorAxisIsX ? bounds.width : bounds.height;
    const padding = 1.2;
    const pathHalfW = visual.pathPattern === 'boardwalk' ? 1.05 : visual.pathPattern === 'formal' ? 0.9 : 0.8;
    const pathCount = Math.max(1, Math.min(visual.pathCount, 1 + Math.floor(crossSpan / 18)));
    const steps = Math.max(8, Math.floor(alongSpan / 5));
    const geos: THREE.BufferGeometry[] = [];

    const pushClippedPolyline = (raw: THREE.Vector2[]) => {
      let chunk: { x: number; z: number }[] = [];
      for (const p of raw) {
        if (pointInPolygon(p.x, p.y, points2D)) {
          chunk.push({ x: p.x, z: -p.y });
        } else {
          if (chunk.length >= 2) {
            const g = buildOffsetRibbon(chunk, -pathHalfW, pathHalfW, 0.145);
            if (g) geos.push(g);
          }
          chunk = [];
        }
      }
      if (chunk.length >= 2) {
        const g = buildOffsetRibbon(chunk, -pathHalfW, pathHalfW, 0.145);
        if (g) geos.push(g);
      }
    };

    for (let i = 0; i < pathCount; i++) {
      const frac = pathCount === 1 ? 0.5 : i / (pathCount - 1);
      const points: THREE.Vector2[] = [];
      for (let s = 0; s <= steps; s++) {
        const t = s / steps;
        const wave =
          visual.pathPattern === 'organic'
            ? Math.sin(t * Math.PI * 2 + i * 0.75) * crossSpan * 0.08
            : 0;

        if (majorAxisIsX) {
          const x = bounds.minX + padding + t * (bounds.width - padding * 2);
          const yBase = bounds.minY + padding + frac * (bounds.height - padding * 2);
          points.push(new THREE.Vector2(x, yBase + wave));
        } else {
          const y = bounds.minY + padding + t * (bounds.height - padding * 2);
          const xBase = bounds.minX + padding + frac * (bounds.width - padding * 2);
          points.push(new THREE.Vector2(xBase + wave, y));
        }
      }
      pushClippedPolyline(points);
    }

    if (pathCount > 1 && visual.pathPattern !== 'boardwalk' && crossSpan > 10) {
      const connector: THREE.Vector2[] = [];
      for (let s = 0; s <= steps; s++) {
        const t = s / steps;
        if (majorAxisIsX) {
          const x = bounds.minX + padding + (bounds.width - padding * 2) * 0.5;
          const y = bounds.minY + padding + t * (bounds.height - padding * 2);
          connector.push(new THREE.Vector2(x, y));
        } else {
          const x = bounds.minX + padding + t * (bounds.width - padding * 2);
          const y = bounds.minY + padding + (bounds.height - padding * 2) * 0.5;
          connector.push(new THREE.Vector2(x, y));
        }
      }
      pushClippedPolyline(connector);
    }

    return geos;
  }, [points2D, visual, enabled]);

  if (pathGeometries.length === 0) return null;

  return (
    <group>
      {pathGeometries.map((geo, i) => (
        <mesh key={`park-path-${i}`} geometry={geo} receiveShadow>
          <meshStandardMaterial color={visual.pathColor} roughness={0.88} metalness={0.03} />
        </mesh>
      ))}
    </group>
  );
}

function ParkShrubClusters({
  points2D,
  density,
  visual,
}: {
  points2D: THREE.Vector2[];
  density: number;
  visual: GreenSpaceVisualConfig;
}) {
  const shrubs = useMemo(() => {
    const bounds = computePolygonBounds(points2D);
    if (bounds.area < 80) return [] as { pos: [number, number, number]; scale: number; color: string }[];

    const clusterCount = Math.min(80, Math.max(6, Math.floor(bounds.area * Math.max(0.1, density) * 0.003 * visual.shrubDensity)));
    const rand = makeRand(points2D.length * 777 + Math.abs(Math.round(bounds.minX * 10)) + Math.round(bounds.minY * 10));
    const base = new THREE.Color(visual.shrubColor);

    const result: { pos: [number, number, number]; scale: number; color: string }[] = [];
    for (let i = 0; i < clusterCount; i++) {
      const cx = bounds.minX + rand() * bounds.width;
      const cy = bounds.minY + rand() * bounds.height;
      if (!pointInPolygon(cx, cy, points2D)) continue;

      const localCount = 2 + Math.floor(rand() * 3);
      for (let j = 0; j < localCount; j++) {
        const ang = rand() * Math.PI * 2;
        const dist = 0.35 + rand() * 1.15;
        const px = cx + Math.cos(ang) * dist;
        const py = cy + Math.sin(ang) * dist;
        if (!pointInPolygon(px, py, points2D)) continue;

        const color = base.clone();
        color.offsetHSL((rand() - 0.5) * 0.04, 0, (rand() - 0.5) * 0.08);
        result.push({
          pos: [px, 0.08, -py],
          scale: 0.35 + rand() * 0.55,
          color: `#${color.getHexString()}`,
        });
      }
    }

    return result;
  }, [points2D, density, visual]);

  return (
    <>
      {shrubs.map((s, i) => (
        <mesh key={`shrub-${i}`} position={s.pos} scale={s.scale} castShadow>
          <icosahedronGeometry args={[0.8, 1]} />
          <meshStandardMaterial color={s.color} roughness={0.86} metalness={0.0} />
        </mesh>
      ))}
    </>
  );
}
// =============================================================================
// 3. GREEN SPACE ZONE — Mixed trees + benches + light poles
// =============================================================================

function GreenSpaceZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const density = zone.properties?.tree_density ?? 0.3;
  const greenAesthetic = (zone.properties?.green_space_aesthetic as string) || '';
  const visual = useMemo(() => resolveGreenSpaceVisualConfig(greenAesthetic), [greenAesthetic]);
  const hasPaths = zone.properties?.has_paths !== false;
  const hasBenches = zone.properties?.has_benches !== false;

  const groundGeometry = useMemo(() => {
    try {
      const shape = new THREE.Shape(points2D);
      const geom = new THREE.ShapeGeometry(shape);
      geom.rotateX(-Math.PI / 2);

      const posAttr = geom.getAttribute('position');
      const colors = new Float32Array(posAttr.count * 3);
      const base = new THREE.Color(visual.groundColor);
      const accent = new THREE.Color(visual.groundAccentColor);
      const color = new THREE.Color();

      for (let i = 0; i < posAttr.count; i++) {
        const x = posAttr.getX(i);
        const z = posAttr.getZ(i);
        const noise = (Math.sin(x * 0.08) + Math.cos(z * 0.06)) * 0.5;
        const blend = 0.35 + ((noise + 1) * 0.5) * 0.45;
        const shade = 0.95 + Math.sin((x + z) * 0.03) * 0.05;

        color.copy(base).lerp(accent, blend).multiplyScalar(shade);
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
      }

      geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      return geom;
    } catch {
      return null;
    }
  }, [points2D, visual]);

  if (!groundGeometry) return null;

  return (
    <group position={[0, 0.12, 0]}>
      {/* Green ground surface */}
      <mesh geometry={groundGeometry} receiveShadow>
        <meshStandardMaterial
          vertexColors
          roughness={0.95}
          metalness={0.0}
          polygonOffset
          polygonOffsetFactor={2}
          polygonOffsetUnits={2}
        />
      </mesh>

      {/* Primary path network */}
      <ParkPathNetwork points2D={points2D} visual={visual} enabled={hasPaths} />

      {/* Low planting and shrub structure */}
      <ParkShrubClusters points2D={points2D} density={density} visual={visual} />

      {/* Mixed trees */}
      <GreenSpaceTrees points2D={points2D} density={density} aesthetic={greenAesthetic} />

      {/* Park benches */}
      {hasBenches && <ParkBenches points2D={points2D} density={density} />}

      {/* Light poles along perimeter */}
      <PerimeterLightPoles points2D={points2D} />
    </group>
  );
}

function GreenSpaceTrees({
  points2D,
  density,
  aesthetic,
}: {
  points2D: THREE.Vector2[];
  density: number;
  aesthetic?: string;
}) {
  const trees = useMemo(() => {
    const bounds = computePolygonBounds(points2D);
    if (bounds.area < 40) return [] as { pos: [number, number, number]; scale: number; type: TreeVariant }[];

    const visual = resolveGreenSpaceVisualConfig(aesthetic);
    const variantPool: TreeVariant[] = visual.treeVariants.length > 0 ? visual.treeVariants : ['deciduous', 'conifer'];
    const count = Math.min(260, Math.max(4, Math.floor(bounds.area * (0.004 + Math.max(0.1, density) * 0.02))));
    const rand = makeRand(points2D.length * 1000 + Math.abs(Math.round(bounds.minX * 100)));

    const result: { pos: [number, number, number]; scale: number; type: TreeVariant }[] = [];
    for (let i = 0; i < count; i++) {
      const px = bounds.minX + rand() * bounds.width;
      const py = bounds.minY + rand() * bounds.height;
      if (!pointInPolygon(px, py, points2D)) continue;

      const type: TreeVariant = variantPool[Math.floor(rand() * variantPool.length)] || 'deciduous';
      result.push({
        pos: [px, 0, -py],
        scale: 0.62 + rand() * 0.72,
        type,
      });
    }
    return result;
  }, [points2D, density, aesthetic]);

  return (
    <>
      {trees.map((t, i) => (
        <DetailedTree key={`park-tree-${i}`} position={t.pos} scale={t.scale} variant={t.type} />
      ))}
    </>
  );
}

function ParkBenches({
  points2D,
  density,
}: {
  points2D: THREE.Vector2[];
  density: number;
}) {
  const benches = useMemo(() => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const p of points2D) {
      minX = Math.min(minX, p.x);
      maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y);
      maxY = Math.max(maxY, p.y);
    }

    const width = maxX - minX;
    const height = maxY - minY;
    const area = width * height;
    const count = Math.max(1, Math.floor(area * density * 0.002));

    const rand = makeRand(points2D.length * 2000 + Math.abs(Math.round(minX * 50)));

    const result: { pos: [number, number, number]; rot: number }[] = [];

    for (let i = 0; i < Math.min(count, 30); i++) {
      const px = minX + rand() * width;
      const py = minY + rand() * height;

      if (pointInPolygon(px, py, points2D)) {
        // Shape (x, y) → 3D (x, 0, -y) to match rotated ShapeGeometry
        result.push({
          pos: [px, 0, -py],
          rot: rand() * Math.PI * 2,
        });
      }
    }

    return result;
  }, [points2D, density]);

  return (
    <>
      {benches.map((b, i) => (
        <Bench key={i} position={b.pos} rotation={b.rot} />
      ))}
    </>
  );
}

function PerimeterLightPoles({ points2D }: { points2D: THREE.Vector2[] }) {
  const poles = useMemo(() => {
    const walls = computeWallSegments(points2D);
    const result: [number, number, number][] = [];
    const minSpacing = 15; // minimum 15m between poles

    for (const wall of walls) {
      const numPoles = Math.max(1, Math.floor(wall.length / minSpacing));
      for (let i = 0; i < numPoles; i++) {
        const t = (i + 0.5) / numPoles;
        const x = wall.startX + wall.dirX * wall.length * t;
        const z = wall.startZ + wall.dirZ * wall.length * t;
        result.push([x, 0, z]);
      }
    }

    return result;
  }, [points2D]);

  return (
    <>
      {poles.map((pos, i) => (
        <LightPole key={i} position={pos} />
      ))}
    </>
  );
}

// =============================================================================
// 4. PARKING ZONE — Asphalt + markings + bollards
// =============================================================================

function ParkingZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const { groundGeometry, markings, bollardPositions } = useMemo(() => {
    let groundGeom: THREE.BufferGeometry | null = null;
    try {
      const shape = new THREE.Shape(points2D);
      groundGeom = new THREE.ShapeGeometry(shape);
      groundGeom.rotateX(-Math.PI / 2);
    } catch {
      // degenerate polygon
    }

    // Find longest edge to orient parking lines
    const walls = computeWallSegments(points2D);
    let longestWall = walls[0];
    for (const w of walls) {
      if (w.length > (longestWall?.length ?? 0)) longestWall = w;
    }

    const markingData: { pos: [number, number, number]; rotY: number; width: number; depth: number }[] = [];
    const bollards: [number, number, number][] = [];

    if (longestWall) {
      // Compute bounding box in 3D world coordinates
      // Shape (x, y) → 3D (x, -y) so negate the y component
      const pts3D = points2D.map((p) => ({ x: p.x, z: -p.y }));
      let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
      for (const p of pts3D) {
        minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
        minZ = Math.min(minZ, p.z); maxZ = Math.max(maxZ, p.z);
      }

      const spaceWidth = 2.7;
      const spaceDepth = 5.5;
      const centerX = (minX + maxX) / 2;
      const centerZ = (minZ + maxZ) / 2;
      const parkWidth = maxX - minX;
      const parkDepth = maxZ - minZ;

      // Compute direction along longest wall for orientation
      const angle = Math.atan2(longestWall.dirZ, longestWall.dirX);

      // Place parking lines in a grid aligned to the longest edge
      const numSpaces = Math.floor(Math.max(parkWidth, parkDepth) / spaceWidth);
      const numRows = Math.max(1, Math.floor(Math.min(parkWidth, parkDepth) / (spaceDepth + 1)));

      for (let row = 0; row < numRows; row++) {
        for (let s = 0; s <= numSpaces; s++) {
          const localX = -numSpaces * spaceWidth / 2 + s * spaceWidth;
          const localZ = -numRows * (spaceDepth + 1) / 2 + row * (spaceDepth + 1);

          // Transform to world space using wall orientation
          const cosA = Math.cos(angle);
          const sinA = Math.sin(angle);
          const wx = centerX + localX * cosA - localZ * sinA;
          const wz = centerZ + localX * sinA + localZ * cosA;

          // Convert 3D back to shape space for point-in-polygon test: (x, -z)
          if (pointInPolygon(wx, -wz, points2D)) {
            markingData.push({
              pos: [wx, 0.04, wz],
              rotY: angle,
              width: 0.1,
              depth: spaceDepth,
            });
          }
        }
      }

      // Front lines for rows
      for (let row = 0; row < numRows; row++) {
        const localZ = -numRows * (spaceDepth + 1) / 2 + row * (spaceDepth + 1) - spaceDepth / 2;
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);
        const wx = centerX - localZ * sinA;
        const wz = centerZ + localZ * cosA;

        markingData.push({
          pos: [wx, 0.04, wz],
          rotY: angle,
          width: numSpaces * spaceWidth,
          depth: 0.1,
        });
      }
    }

    // Bollards along perimeter
    for (const wall of walls) {
      const numBollards = Math.max(1, Math.floor(wall.length / 5));
      for (let i = 0; i < numBollards; i++) {
        const t = (i + 0.5) / numBollards;
        const x = wall.startX + wall.dirX * wall.length * t;
        const z = wall.startZ + wall.dirZ * wall.length * t;
        bollards.push([x, 0, z]);
      }
    }

    return { groundGeometry: groundGeom, markings: markingData, bollardPositions: bollards };
  }, [points2D]);

  if (!groundGeometry) return null;

  return (
    <group position={[0, 0.10, 0]}>
      {/* Asphalt surface */}
      <mesh geometry={groundGeometry} receiveShadow>
        <meshStandardMaterial color="#3a3a3a" roughness={0.95} metalness={0.0} polygonOffset polygonOffsetFactor={2} polygonOffsetUnits={2} />
      </mesh>

      {/* Parking space markings */}
      {markings.map((m, i) => (
        <mesh key={`mark-${i}`} position={m.pos} rotation={[-Math.PI / 2, 0, m.rotY]}>
          <planeGeometry args={[m.width, m.depth]} />
          <meshBasicMaterial color="#ffffff" side={THREE.DoubleSide} />
        </mesh>
      ))}

      {/* Perimeter bollards */}
      {bollardPositions.map((pos, i) => (
        <Bollard key={`bollard-${i}`} position={pos} />
      ))}
    </group>
  );
}

// =============================================================================
// 5. WATER ZONE — Reflective surface with gentle waves
// =============================================================================

function WaterZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  const geometry = useMemo(() => {
    try {
      const shape = new THREE.Shape(points2D);
      const geom = new THREE.ShapeGeometry(shape, 8);
      geom.rotateX(-Math.PI / 2);
      return geom;
    } catch {
      return null;
    }
  }, [points2D]);

  // Gentle wave animation
  useFrame(({ clock }) => {
    if (!meshRef.current || !geometry) return;
    const posAttr = meshRef.current.geometry.getAttribute('position');
    if (!posAttr) return;

    const time = clock.getElapsedTime();
    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const z = posAttr.getZ(i);
      const wave = Math.sin(x * 0.5 + time * 1.2) * 0.08 + Math.cos(z * 0.3 + time * 0.8) * 0.05;
      posAttr.setY(i, 0.01 + wave);
    }
    posAttr.needsUpdate = true;
  });

  if (!geometry) return null;

  return (
    <mesh ref={meshRef} geometry={geometry} position={[0, 0.05, 0]} receiveShadow>
      <meshPhysicalMaterial
        color="#1a6b8a"
        roughness={0.05}
        metalness={0.1}
        transmission={0.4}
        ior={1.33}
        transparent
        opacity={0.85}
        side={THREE.DoubleSide}
        polygonOffset
        polygonOffsetFactor={3}
        polygonOffsetUnits={3}
      />
    </mesh>
  );
}

// =============================================================================
// 6. FALLBACK ZONE — Generic flat surface
// =============================================================================

function FallbackZone({
  zone,
  points2D,
}: {
  zone: SiteZone;
  points2D: THREE.Vector2[];
}) {
  const geometry = useMemo(() => {
    try {
      const shape = new THREE.Shape(points2D);
      const geom = new THREE.ShapeGeometry(shape);
      geom.rotateX(-Math.PI / 2);
      return geom;
    } catch {
      return null;
    }
  }, [points2D]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry} position={[0, 0.08, 0]} receiveShadow>
      <meshStandardMaterial
        color={zone.color}
        roughness={0.7}
        metalness={0.05}
        transparent
        opacity={0.75}
        polygonOffset
        polygonOffsetFactor={2}
        polygonOffsetUnits={2}
      />
    </mesh>
  );
}

// =============================================================================
// Shared street furniture components
// =============================================================================

function Bench({
  position,
  rotation,
}: {
  position: [number, number, number];
  rotation: number;
}) {
  return (
    <group position={position} rotation={[0, rotation, 0]}>
      {/* Steel frame */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <boxGeometry args={[1.18, 0.08, 0.42]} />
        <meshStandardMaterial color="#4d4f57" roughness={0.45} metalness={0.55} />
      </mesh>

      {/* Seat slats */}
      {[-0.24, -0.12, 0, 0.12, 0.24].map((z) => (
        <mesh key={`seat-${z}`} position={[0, 0.45, z]} castShadow>
          <boxGeometry args={[1.18, 0.04, 0.06]} />
          <meshStandardMaterial color="#8f6a3f" roughness={0.74} metalness={0.05} />
        </mesh>
      ))}

      {/* Backrest rails */}
      {[-0.2, -0.05, 0.1, 0.25].map((y) => (
        <mesh key={`back-${y}`} position={[0, 0.62 + y, -0.22]} rotation={[0.16, 0, 0]} castShadow>
          <boxGeometry args={[1.16, 0.035, 0.06]} />
          <meshStandardMaterial color="#8f6a3f" roughness={0.74} metalness={0.05} />
        </mesh>
      ))}

      {/* Legs */}
      {[-0.5, 0.5].map((lx) => (
        <group key={`legs-${lx}`}>
          <mesh position={[lx, 0.24, 0.13]} castShadow>
            <boxGeometry args={[0.06, 0.48, 0.06]} />
            <meshStandardMaterial color="#4d4f57" roughness={0.45} metalness={0.55} />
          </mesh>
          <mesh position={[lx, 0.24, -0.13]} castShadow>
            <boxGeometry args={[0.06, 0.48, 0.06]} />
            <meshStandardMaterial color="#4d4f57" roughness={0.45} metalness={0.55} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function LightPole({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Base */}
      <mesh position={[0, 0.08, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.18, 0.16, 10]} />
        <meshStandardMaterial color="#51545c" roughness={0.42} metalness={0.6} />
      </mesh>

      {/* Main shaft */}
      <mesh position={[0, 2.7, 0]} castShadow>
        <cylinderGeometry args={[0.035, 0.055, 5.3, 10]} />
        <meshStandardMaterial color="#676a73" roughness={0.34} metalness={0.75} />
      </mesh>

      {/* Arm */}
      <mesh position={[0.2, 4.85, 0]} rotation={[0, 0, -0.42]} castShadow>
        <cylinderGeometry args={[0.02, 0.025, 0.72, 8]} />
        <meshStandardMaterial color="#676a73" roughness={0.34} metalness={0.75} />
      </mesh>

      {/* Fixture housing */}
      <mesh position={[0.38, 4.56, 0]} castShadow>
        <boxGeometry args={[0.24, 0.12, 0.16]} />
        <meshStandardMaterial color="#5e6169" roughness={0.45} metalness={0.65} />
      </mesh>

      {/* Lens */}
      <mesh position={[0.38, 4.5, 0]}>
        <sphereGeometry args={[0.08, 10, 8]} />
        <meshStandardMaterial color="#fff6cf" emissive="#fff1b8" emissiveIntensity={0.34} roughness={0.2} metalness={0.0} />
      </mesh>
    </group>
  );
}

function Bollard({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={[position[0], 0.35, position[2]]} castShadow>
      <cylinderGeometry args={[0.08, 0.08, 0.7, 8]} />
      <meshStandardMaterial color="#555555" roughness={0.4} metalness={0.7} />
    </mesh>
  );
}

// =============================================================================
// AI Layout Infrastructure — Roads and Green Spaces from layout metadata
// =============================================================================

function LayoutInfrastructure({
  zone,
  origin,
  roads,
  greenSpaces,
}: {
  zone: SiteZone;
  origin: { lat: number; lon: number };
  roads?: LayoutRoadData[];
  greenSpaces?: LayoutGreenSpaceData[];
}) {
  // Compute zone centroid for offset conversion
  const centroid = useMemo(() => {
    const coords = zone.coordinates;
    let cx = 0, cy = 0;
    for (const p of coords) {
      cx += p[0];
      cy += p[1];
    }
    return { lon: cx / coords.length, lat: cy / coords.length };
  }, [zone.coordinates]);

  return (
    <group name={`layout-infra-${zone.id}`}>
      {roads?.map((road, i) => (
        <LayoutRoadMesh key={`road-${i}`} road={road} centroid={centroid} origin={origin} />
      ))}
      {greenSpaces?.map((gs, i) => (
        <LayoutGreenMesh key={`green-${i}`} greenSpace={gs} centroid={centroid} origin={origin} />
      ))}
    </group>
  );
}

function LayoutRoadMesh({
  road,
  centroid,
  origin,
}: {
  road: LayoutRoadData;
  centroid: { lon: number; lat: number };
  origin: { lat: number; lon: number };
}) {
  const geometry = useMemo(() => {
    if (road.centerline.length < 2) return null;

    const mLon = metersPerDegLon(origin.lat);
    const halfW = road.width_m / 2;

    // Convert centerline offsets to local meter positions
    const points = road.centerline.map(([ox, oy]) => {
      const absLon = centroid.lon + ox;
      const absLat = centroid.lat + oy;
      const x = (absLon - origin.lon) * mLon;
      const z = -((absLat - origin.lat) * METERS_PER_DEG_LAT);
      return { x, z };
    });

    // Build ribbon geometry
    const vertices: number[] = [];
    const indices: number[] = [];

    for (let i = 0; i < points.length; i++) {
      let dx = 0, dz = 0;
      if (i < points.length - 1) {
        dx += points[i + 1].x - points[i].x;
        dz += points[i + 1].z - points[i].z;
      }
      if (i > 0) {
        dx += points[i].x - points[i - 1].x;
        dz += points[i].z - points[i - 1].z;
      }
      const len = Math.sqrt(dx * dx + dz * dz) || 1;
      const nx = -dz / len;
      const nz = dx / len;

      vertices.push(
        points[i].x - nx * halfW, 0.15, points[i].z - nz * halfW,
        points[i].x + nx * halfW, 0.15, points[i].z + nz * halfW,
      );

      if (i < points.length - 1) {
        const base = i * 2;
        indices.push(base, base + 1, base + 2);
        indices.push(base + 1, base + 3, base + 2);
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    return geo;
  }, [road, centroid, origin]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry} receiveShadow>
      <meshStandardMaterial color="#444444" roughness={0.9} />
    </mesh>
  );
}

function LayoutGreenMesh({
  greenSpace,
  centroid,
  origin,
}: {
  greenSpace: LayoutGreenSpaceData;
  centroid: { lon: number; lat: number };
  origin: { lat: number; lon: number };
}) {
  const geometry = useMemo(() => {
    if (greenSpace.polygon.length < 3) return null;

    const mLon = metersPerDegLon(origin.lat);

    // Convert offsets to local 2D points
    const pts = greenSpace.polygon.map(([ox, oy]) => {
      const absLon = centroid.lon + ox;
      const absLat = centroid.lat + oy;
      const x = (absLon - origin.lon) * mLon;
      const y = (absLat - origin.lat) * METERS_PER_DEG_LAT;
      return new THREE.Vector2(x, y);
    });

    const shape = new THREE.Shape(pts);
    const geo = new THREE.ShapeGeometry(shape);
    geo.rotateX(-Math.PI / 2);
    return geo;
  }, [greenSpace, centroid, origin]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry} position={[0, 0.12, 0]} receiveShadow>
      <meshStandardMaterial color="#27ae60" roughness={0.8} polygonOffset polygonOffsetFactor={2} polygonOffsetUnits={2} />
    </mesh>
  );
}

// =============================================================================
// Layout Preview Overlay
// =============================================================================

function LayoutPreviewOverlay({
  zones,
  origin,
}: {
  zones: SiteZone[];
  origin: { lat: number; lon: number };
}) {
  const layoutPreview = useViewerStore((s) => s.layoutPreview);
  const sitePreview = useViewerStore((s) => s.sitePreview);

  // Site-wide preview: render overlays for ALL zones
  if (sitePreview) {
    const { zoneLayouts, activeIndex } = sitePreview;
    const entries = Object.entries(zoneLayouts);
    return (
      <group name="layout-preview-overlay">
        {entries.map(([zoneId, options]) => {
          const zone = zones.find((z) => z.id === zoneId);
          if (!zone) return null;
          const option = options[activeIndex];
          if (!option) return null;
          return (
            <ZoneLayoutOverlay
              key={zoneId}
              zone={zone}
              option={option}
              origin={origin}
            />
          );
        })}
      </group>
    );
  }

  // Per-zone preview (existing behavior)
  if (!layoutPreview) return null;

  const zone = zones.find((z) => z.id === layoutPreview.zoneId);
  if (!zone) return null;

  const activeOption = layoutPreview.options[layoutPreview.activeIndex];
  if (!activeOption) return null;

  return (
    <group name="layout-preview-overlay">
      <ZoneLayoutOverlay zone={zone} option={activeOption} origin={origin} />
    </group>
  );
}

/** Renders buildings/roads/green spaces for a single zone's layout option */
function ZoneLayoutOverlay({
  zone,
  option,
  origin,
}: {
  zone: SiteZone;
  option: LayoutOption;
  origin: { lat: number; lon: number };
}) {
  // Zone centroid for converting offsets
  const centroid = useMemo(() => {
    const coords = zone.coordinates;
    let cx = 0, cy = 0;
    for (const p of coords) {
      cx += p[0];
      cy += p[1];
    }
    return { lon: cx / coords.length, lat: cy / coords.length };
  }, [zone.coordinates]);

  return (
    <group name={`zone-overlay-${zone.id}`}>
      {option.buildings.map((bld, i) => (
        <PreviewBuildingFootprint
          key={`preview-bld-${zone.id}-${i}`}
          building={bld}
          centroid={centroid}
          origin={origin}
          height={bld.height_m || (zone.properties?.height as number) || 12}
        />
      ))}
      {option.roads.map((road, i) => (
        <LayoutRoadMesh
          key={`preview-road-${zone.id}-${i}`}
          road={road}
          centroid={centroid}
          origin={origin}
        />
      ))}
      {option.green_spaces.map((gs, i) => (
        <LayoutGreenMesh
          key={`preview-green-${zone.id}-${i}`}
          greenSpace={gs}
          centroid={centroid}
          origin={origin}
        />
      ))}
    </group>
  );
}

function PreviewBuildingFootprint({
  building,
  centroid,
  origin,
  height,
}: {
  building: LayoutOption['buildings'][0];
  centroid: { lon: number; lat: number };
  origin: { lat: number; lon: number };
  height: number;
}) {
  const mesh = useMemo(() => {
    const mLon = metersPerDegLon(origin.lat);

    const absLon = centroid.lon + building.center_x;
    const absLat = centroid.lat + building.center_y;
    const x = (absLon - origin.lon) * mLon;
    const z = -((absLat - origin.lat) * METERS_PER_DEG_LAT);

    const geo = new THREE.BoxGeometry(building.width_m, height, building.depth_m);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x6366f1,
      wireframe: true,
      transparent: true,
      opacity: 0.6,
    });

    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, height / 2, z);
    m.rotation.y = -((building.rotation_deg * Math.PI) / 180);

    return m;
  }, [building, centroid, origin, height]);

  return <primitive object={mesh} />;
}


























