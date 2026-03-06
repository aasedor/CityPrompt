/**
 * Terrain-aware ground mesh.
 *
 * Replaces the flat ground plane when Google 3D Tiles are active.
 * A subdivided PlaneGeometry is deformed by raycasting each vertex
 * downward onto the loaded tile meshes, producing a ground surface
 * that follows real-world hills and valleys.
 *
 * Exports `getTerrainHeight(x, z)` for placing buildings at the
 * correct elevation via bilinear interpolation of the sampled grid.
 */
import { useRef, useMemo, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { tilesGroupRef } from './Google3DTiles';

const TERRAIN_SIZE = 500; // meters, centered at origin
const TERRAIN_SEGMENTS = 80;
const TERRAIN_CELLS = TERRAIN_SEGMENTS + 1; // vertices per side
const BATCH_SIZE = 300; // vertices sampled per frame
const RESAMPLE_INTERVAL = 5; // seconds between full resamples

// Module-level height data for getTerrainHeight queries
const heightData = new Float32Array(TERRAIN_CELLS * TERRAIN_CELLS);
let heightDataReady = false;
let terrainVersion = 0;

/**
 * Get terrain elevation at world (x, z) via bilinear interpolation.
 * Returns 0 when terrain hasn't been sampled yet.
 */
export function getTerrainHeight(x: number, z: number): number {
  if (!heightDataReady) return 0;

  const halfSize = TERRAIN_SIZE / 2;
  const gx = ((x + halfSize) / TERRAIN_SIZE) * TERRAIN_SEGMENTS;
  const gz = ((z + halfSize) / TERRAIN_SIZE) * TERRAIN_SEGMENTS;

  const ix = Math.max(0, Math.min(TERRAIN_SEGMENTS - 1, Math.floor(gx)));
  const iz = Math.max(0, Math.min(TERRAIN_SEGMENTS - 1, Math.floor(gz)));

  const fx = gx - ix;
  const fz = gz - iz;

  const h00 = heightData[iz * TERRAIN_CELLS + ix];
  const h10 = heightData[iz * TERRAIN_CELLS + ix + 1];
  const h01 = heightData[(iz + 1) * TERRAIN_CELLS + ix];
  const h11 = heightData[(iz + 1) * TERRAIN_CELLS + ix + 1];

  return (
    h00 * (1 - fx) * (1 - fz) +
    h10 * fx * (1 - fz) +
    h01 * (1 - fx) * fz +
    h11 * fx * fz
  );
}

/** Returns the current terrain sampling version (increments each full resample). */
export function getTerrainVersion(): number {
  return terrainVersion;
}

export function TerrainMesh() {
  const meshRef = useRef<THREE.Mesh>(null);
  const raycaster = useRef(new THREE.Raycaster());
  const sampleIndex = useRef(0);
  const lastResample = useRef(0);
  const totalVertices = TERRAIN_CELLS * TERRAIN_CELLS;

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(
      TERRAIN_SIZE,
      TERRAIN_SIZE,
      TERRAIN_SEGMENTS,
      TERRAIN_SEGMENTS,
    );
    geo.rotateX(-Math.PI / 2);
    return geo;
  }, []);

  const collectMeshes = useCallback(() => {
    const group = tilesGroupRef.current;
    if (!group) return null;
    const meshes: THREE.Mesh[] = [];
    group.traverse((obj: any) => {
      if (obj.isMesh) meshes.push(obj);
    });
    return meshes.length > 20 ? meshes : null;
  }, []);

  useFrame((_, delta) => {
    const meshes = collectMeshes();
    if (!meshes) return;

    const positions = geometry.attributes.position as THREE.BufferAttribute;

    // Periodic full resample as more tile detail loads
    lastResample.current += delta;
    if (sampleIndex.current >= totalVertices && lastResample.current > RESAMPLE_INTERVAL) {
      sampleIndex.current = 0;
      lastResample.current = 0;
    }

    if (sampleIndex.current >= totalVertices) return;

    const end = Math.min(sampleIndex.current + BATCH_SIZE, totalVertices);
    let updated = false;

    for (let i = sampleIndex.current; i < end; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);

      raycaster.current.set(
        new THREE.Vector3(x, 10000, z),
        new THREE.Vector3(0, -1, 0),
      );
      raycaster.current.far = 20000;

      const hits = raycaster.current.intersectObjects(meshes, false);
      if (hits.length > 0) {
        // Use the lowest hit (last in the sorted array) to get the ground
        // surface rather than rooftops of 3D buildings
        const y = hits[hits.length - 1].point.y;
        positions.setY(i, y);

        // Store in height map for getTerrainHeight lookups
        // Vertex layout: row-major, X varies fastest (PlaneGeometry after rotateX)
        const col = i % TERRAIN_CELLS;
        const row = Math.floor(i / TERRAIN_CELLS);
        heightData[row * TERRAIN_CELLS + col] = y;
        updated = true;
      }
    }

    sampleIndex.current = end;

    if (updated) {
      positions.needsUpdate = true;
      geometry.computeVertexNormals();
    }

    if (sampleIndex.current >= totalVertices && !heightDataReady) {
      heightDataReady = true;
      terrainVersion++;
    } else if (sampleIndex.current >= totalVertices) {
      terrainVersion++;
    }
  });

  return (
    <mesh ref={meshRef} geometry={geometry} receiveShadow>
      <shadowMaterial opacity={0.15} />
    </mesh>
  );
}
