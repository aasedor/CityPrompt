/**
 * Enhanced context building rendering with pitched roofs, windows, doors,
 * garage doors, floor lines, and parapets.
 *
 * This file replaces the basic ContextBuildingsGroup / ContextBuildingMesh
 * that lived inside SceneViewer.tsx.
 */
import { useRef, useEffect, useMemo } from 'react';
import * as THREE from 'three';
import * as ctxGeo from './contextBuildingGeometry';
import { resolveRoofShape } from './contextBuildingGeometry';

// Re-define the interface locally to avoid circular import with SceneViewer
export interface ContextBuildingData {
  osm_id: number;
  height: number;
  levels?: number;
  building_type?: string;
  footprint: number[][]; // [[lon, lat], ...]
  roof_shape?: string;
}

export interface ContextRoadData {
  osm_id: number;
  name?: string;
  highway_type: string;
  width: number;
  coords: number[][]; // [[lon, lat], ...]
}

// Building-type color mapping for context buildings
const CONTEXT_BUILDING_COLORS: Record<string, string> = {
  apartments: '#c9a882',
  commercial: '#8ca8b8',
  school: '#c8b87a',
  industrial: '#a09080',
  residential: '#b8a898',
  retail: '#a8b8a0',
  office: '#98a8b8',
  house: '#b8a898',
  detached: '#b8a898',
  terrace: '#b0a090',
  church: '#c8b87a',
  warehouse: '#a09080',
  garage: '#a0a0a0',
  yes: '#b0a898',
};

export function ContextBuildingsGroup({ buildings, roads, projectLat, projectLng, getTerrainY }: {
  buildings: ContextBuildingData[];
  roads?: ContextRoadData[];
  projectLat?: number;
  projectLng?: number;
  getTerrainY?: (x: number, z: number) => number;
}) {
  const originRef = useMemo(() => {
    if (projectLat != null && projectLng != null) {
      return { lat: projectLat, lon: projectLng };
    }
    if (buildings.length === 0) return { lat: 0, lon: 0 };
    let totalLat = 0, totalLon = 0, count = 0;
    for (const b of buildings) {
      for (const p of b.footprint) {
        totalLon += p[0];
        totalLat += p[1];
        count++;
      }
    }
    return { lat: totalLat / count, lon: totalLon / count };
  }, [buildings, projectLat, projectLng]);

  // Pre-compute coordinate conversion and per-building data
  const precomputed = useMemo(() => {
    const metersPerDegLat = 111320;
    const metersPerDegLon = metersPerDegLat * Math.cos((originRef.lat * Math.PI) / 180);
    return buildings.map((b) => {
      const points2D = b.footprint.map((p) => {
        const x = (p[0] - originRef.lon) * metersPerDegLon;
        const z = (p[1] - originRef.lat) * metersPerDegLat;
        return new THREE.Vector2(x, z);
      });
      // Centroid in scene XZ for terrain lookups
      const cx = points2D.reduce((s, p) => s + p.x, 0) / (points2D.length || 1);
      const cz = points2D.reduce((s, p) => s + p.y, 0) / (points2D.length || 1);
      const roofShape = resolveRoofShape(b as any);
      const levels = b.levels ?? Math.max(1, Math.round(b.height / 3));
      return { building: b, points2D, roofShape, levels, cx, cz };
    });
  }, [buildings, originRef]);

  // Precompute road segments in local meters for door-facing computation
  const roadSegments = useMemo<ctxGeo.RoadSegment2D[]>(() => {
    if (!roads || roads.length === 0) return [];
    const metersPerDegLat = 111320;
    const metersPerDegLon = metersPerDegLat * Math.cos((originRef.lat * Math.PI) / 180);
    const segs: ctxGeo.RoadSegment2D[] = [];
    for (const road of roads) {
      for (let i = 0; i < road.coords.length - 1; i++) {
        const ax = (road.coords[i][0] - originRef.lon) * metersPerDegLon;
        const ay = (road.coords[i][1] - originRef.lat) * metersPerDegLat;
        const bx = (road.coords[i + 1][0] - originRef.lon) * metersPerDegLon;
        const by = (road.coords[i + 1][1] - originRef.lat) * metersPerDegLat;
        segs.push({ a: new THREE.Vector2(ax, ay), b: new THREE.Vector2(bx, by) });
      }
    }
    return segs;
  }, [roads, originRef]);

  // Batched window instances across ALL buildings (with centroid for terrain offset)
  const { windowData, windowCount, windowCentroids } = useMemo(() => {
    const allWindows: ctxGeo.WindowInstance[] = [];
    const centroids: { cx: number; cz: number }[] = [];
    for (const { points2D, building, roofShape, levels, cx, cz } of precomputed) {
      if (points2D.length < 3 || levels < 1) continue;
      const floorH = building.height / Math.max(1, levels);
      const roofH = roofShape === 'flat' ? 0 : Math.min(building.height * 0.15, floorH * 0.8, 2.5);
      const wallH = roofShape === 'flat' ? building.height : building.height - roofH;
      const windows = ctxGeo.computeWindowPositions(points2D, wallH, levels, floorH, building.building_type, building.height);
      for (const w of windows) centroids.push({ cx, cz });
      allWindows.push(...windows);
    }
    return { windowData: allWindows, windowCount: allWindows.length, windowCentroids: centroids };
  }, [precomputed]);

  // Batched door instances across ALL buildings (regular doors + garage doors)
  const { doorData, doorCount, doorCentroids, garageDoorData, garageDoorCount, garageDoorCentroids } = useMemo(() => {
    const doors: ctxGeo.DoorInstance[] = [];
    const garageDoors: ctxGeo.DoorInstance[] = [];
    const dCentroids: { cx: number; cz: number }[] = [];
    const gdCentroids: { cx: number; cz: number }[] = [];
    for (const { points2D, building, cx, cz } of precomputed) {
      if (points2D.length < 3) continue;
      const instances = ctxGeo.computeDoorPositions(points2D, building.building_type, building.height, roadSegments);
      for (const inst of instances) {
        if (inst.kind === 'garage') { garageDoors.push(inst); gdCentroids.push({ cx, cz }); }
        else { doors.push(inst); dCentroids.push({ cx, cz }); }
      }
    }
    return { doorData: doors, doorCount: doors.length, doorCentroids: dCentroids, garageDoorData: garageDoors, garageDoorCount: garageDoors.length, garageDoorCentroids: gdCentroids };
  }, [precomputed, roadSegments]);

  // Batched floor lines across ALL buildings
  const floorLineGeometry = useMemo(() => {
    const allSegments: number[] = [];
    for (const { points2D, building, roofShape, levels, cx, cz } of precomputed) {
      if (points2D.length < 3 || levels <= 1) continue;
      const floorH = building.height / Math.max(1, levels);
      const roofH = roofShape === 'flat' ? 0 : Math.min(building.height * 0.15, floorH * 0.8, 2.5);
      const wallH = roofShape === 'flat' ? building.height : building.height - roofH;
      const segs = ctxGeo.computeFloorLines(points2D, wallH, levels, floorH);
      const ty = getTerrainY ? getTerrainY(cx, cz) : 0;
      // Floor line segments are triples (x, y, z) — offset Y by terrain
      for (let j = 0; j < segs.length; j++) {
        allSegments.push(j % 3 === 1 ? segs[j] + ty : segs[j]);
      }
    }
    if (allSegments.length === 0) return null;
    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(allSegments), 3));
    return geom;
  }, [precomputed, getTerrainY]);

  // Window geometry + material
  const windowMeshRef = useRef<THREE.InstancedMesh>(null);
  const windowGeom = useMemo(() => new THREE.PlaneGeometry(ctxGeo.WINDOW_WIDTH, ctxGeo.WINDOW_HEIGHT), []);
  const windowMat = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#5a7a8a',
    metalness: 0.4,
    roughness: 0.25,
    transparent: true,
    opacity: 0.85,
    side: THREE.DoubleSide,
  }), []);

  // Door geometry + material
  const doorMeshRef = useRef<THREE.InstancedMesh>(null);
  const doorGeom = useMemo(() => new THREE.PlaneGeometry(ctxGeo.DOOR_WIDTH, ctxGeo.DOOR_HEIGHT), []);
  const doorMat = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#5a3a2a',
    roughness: 0.7,
    metalness: 0.1,
    side: THREE.DoubleSide,
  }), []);

  // Garage door geometry + material
  const garageDoorMeshRef = useRef<THREE.InstancedMesh>(null);
  const garageDoorGeom = useMemo(() => new THREE.PlaneGeometry(ctxGeo.GARAGE_DOOR_WIDTH, ctxGeo.GARAGE_DOOR_HEIGHT), []);
  const garageDoorMat = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#4a4a4e',
    roughness: 0.5,
    metalness: 0.35,
    side: THREE.DoubleSide,
  }), []);

  // Set window instance matrices (with terrain Y offset)
  useEffect(() => {
    if (!windowMeshRef.current || windowCount === 0) return;
    const dummy = new THREE.Object3D();
    for (let i = 0; i < windowCount; i++) {
      const w = windowData[i];
      dummy.position.copy(w.position);
      if (getTerrainY) dummy.position.y += getTerrainY(windowCentroids[i].cx, windowCentroids[i].cz);
      dummy.quaternion.copy(w.quaternion);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      windowMeshRef.current.setMatrixAt(i, dummy.matrix);
    }
    windowMeshRef.current.instanceMatrix.needsUpdate = true;
  }, [windowData, windowCount, getTerrainY, windowCentroids]);

  // Set door instance matrices (with terrain Y offset)
  useEffect(() => {
    if (!doorMeshRef.current || doorCount === 0) return;
    const dummy = new THREE.Object3D();
    for (let i = 0; i < doorCount; i++) {
      const d = doorData[i];
      dummy.position.copy(d.position);
      if (getTerrainY) dummy.position.y += getTerrainY(doorCentroids[i].cx, doorCentroids[i].cz);
      dummy.quaternion.copy(d.quaternion);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      doorMeshRef.current.setMatrixAt(i, dummy.matrix);
    }
    doorMeshRef.current.instanceMatrix.needsUpdate = true;
  }, [doorData, doorCount, getTerrainY, doorCentroids]);

  // Set garage door instance matrices (with terrain Y offset)
  useEffect(() => {
    if (!garageDoorMeshRef.current || garageDoorCount === 0) return;
    const dummy = new THREE.Object3D();
    for (let i = 0; i < garageDoorCount; i++) {
      const d = garageDoorData[i];
      dummy.position.copy(d.position);
      if (getTerrainY) dummy.position.y += getTerrainY(garageDoorCentroids[i].cx, garageDoorCentroids[i].cz);
      dummy.quaternion.copy(d.quaternion);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      garageDoorMeshRef.current.setMatrixAt(i, dummy.matrix);
    }
    garageDoorMeshRef.current.instanceMatrix.needsUpdate = true;
  }, [garageDoorData, garageDoorCount, getTerrainY, garageDoorCentroids]);

  return (
    <group>
      {precomputed.map(({ building, points2D, roofShape, levels, cx, cz }) => {
        const ty = getTerrainY ? getTerrainY(cx, cz) : 0;
        return (
          <group key={building.osm_id} position={[0, ty, 0]}>
            <ContextBuildingMesh
              building={building}
              points2D={points2D}
              roofShape={roofShape}
              levels={levels}
            />
          </group>
        );
      })}

      {/* All windows — single InstancedMesh */}
      {windowCount > 0 && (
        <instancedMesh
          ref={windowMeshRef}
          args={[windowGeom, windowMat, windowCount]}
          frustumCulled={false}
        />
      )}

      {/* Floor lines — single LineSegments */}
      {floorLineGeometry && (
        <lineSegments geometry={floorLineGeometry} frustumCulled={false}>
          <lineBasicMaterial color="#555555" transparent opacity={0.4} />
        </lineSegments>
      )}

      {/* All doors — single InstancedMesh */}
      {doorCount > 0 && (
        <instancedMesh
          ref={doorMeshRef}
          args={[doorGeom, doorMat, doorCount]}
          frustumCulled={false}
        />
      )}

      {/* All garage doors — single InstancedMesh */}
      {garageDoorCount > 0 && (
        <instancedMesh
          ref={garageDoorMeshRef}
          args={[garageDoorGeom, garageDoorMat, garageDoorCount]}
          frustumCulled={false}
        />
      )}
    </group>
  );
}

function ContextBuildingMesh({
  building,
  points2D,
  roofShape,
  levels,
}: {
  building: ContextBuildingData;
  points2D: THREE.Vector2[];
  roofShape: ctxGeo.RoofShape;
  levels: number;
}) {
  const geometries = useMemo(() => {
    if (points2D.length < 3) return null;

    const floorH = building.height / Math.max(1, levels);
    // Modest roof height: 15% of building, capped at 2.5m
    const roofHeight = roofShape === 'flat' ? 0 : Math.min(building.height * 0.15, floorH * 0.8, 2.5);
    const wallH = roofShape === 'flat' ? building.height : building.height - roofHeight;

    const shape = new THREE.Shape(points2D);
    const wallGeom = new THREE.ExtrudeGeometry(shape, {
      steps: 1,
      depth: wallH,
      bevelEnabled: false,
    });
    wallGeom.rotateX(-Math.PI / 2);

    const edgesGeom = new THREE.EdgesGeometry(wallGeom, 30);

    let roofGeom: THREE.BufferGeometry | null = null;
    let parapetGeom: THREE.BufferGeometry | null = null;

    if (roofShape === 'pitched') {
      roofGeom = ctxGeo.buildSlopedRoofGeometry(points2D, wallH, roofHeight);
    } else {
      const capGeom = new THREE.ShapeGeometry(shape);
      capGeom.rotateX(-Math.PI / 2);
      capGeom.translate(0, wallH, 0);
      roofGeom = capGeom;
      parapetGeom = ctxGeo.buildParapetGeometry(points2D, wallH, 0.4);
    }

    return { wallGeom, roofGeom, edgesGeom, parapetGeom };
  }, [building, points2D, roofShape, levels]);

  const wallColor = CONTEXT_BUILDING_COLORS[building.building_type || ''] || '#b0a898';

  const roofColor = useMemo(() => {
    if (roofShape !== 'flat') return '#8b6b4a';
    const c = new THREE.Color(wallColor);
    c.multiplyScalar(0.85);
    return '#' + c.getHexString();
  }, [roofShape, wallColor]);

  const parapetColor = useMemo(() => {
    const c = new THREE.Color(wallColor);
    c.multiplyScalar(0.78);
    return '#' + c.getHexString();
  }, [wallColor]);

  if (!geometries) return null;

  return (
    <group>
      {/* Walls */}
      <mesh geometry={geometries.wallGeom} receiveShadow castShadow>
        <meshStandardMaterial
          color={wallColor}
          roughness={0.85}
          metalness={0.05}
        />
      </mesh>
      {/* Roof */}
      {geometries.roofGeom && (
        <mesh geometry={geometries.roofGeom} receiveShadow>
          <meshStandardMaterial
            color={roofColor}
            roughness={0.65}
            metalness={0.05}
          />
        </mesh>
      )}
      {/* Parapet (flat roofs only) */}
      {geometries.parapetGeom && (
        <mesh geometry={geometries.parapetGeom} receiveShadow castShadow>
          <meshStandardMaterial
            color={parapetColor}
            roughness={0.85}
            metalness={0.05}
          />
        </mesh>
      )}
      {/* Edge lines */}
      {geometries.edgesGeom && (
        <lineSegments geometry={geometries.edgesGeom}>
          <lineBasicMaterial color="#777777" transparent opacity={0.35} />
        </lineSegments>
      )}
    </group>
  );
}
