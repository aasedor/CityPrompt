/**
 * Google Maps Photorealistic 3D Tiles.
 *
 * Uses the library's ReorientationPlugin to handle ECEF-to-local transforms.
 * After tiles load, a downward raycast auto-aligns the tile ground with Y=0.
 * azimuth=π rotates tile axes to match the scene convention (+X=East, +Z=South).
 */
import { useEffect, useRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { TilesRenderer } from '3d-tiles-renderer/three';
import {
  GoogleCloudAuthPlugin,
  GLTFExtensionsPlugin,
  ReorientationPlugin,
} from '3d-tiles-renderer/plugins';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

const GOOGLE_TILES_URL =
  'https://tile.googleapis.com/v1/3dtiles/root.json';
const DRACO_DECODER_PATH =
  'https://www.gstatic.com/draco/versioned/decoders/1.5.7/';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath(DRACO_DECODER_PATH);

/** Shared ref so other components (TerrainMesh) can raycast against the tiles. */
export const tilesGroupRef: { current: THREE.Group | null } = { current: null };

interface Google3DTilesProps {
  latitude: number;
  longitude: number;
  apiKey: string;
}

export function Google3DTiles({
  latitude,
  longitude,
  apiKey,
}: Google3DTilesProps) {
  const { scene, camera, gl } = useThree();
  const tilesRef = useRef<InstanceType<typeof TilesRenderer> | null>(null);
  const alignedRef = useRef(false);

  useEffect(() => {
    if (!apiKey) return;

    const latRad = (latitude * Math.PI) / 180;
    const lonRad = (longitude * Math.PI) / 180;

    const tiles = new TilesRenderer(GOOGLE_TILES_URL);

    tiles.registerPlugin(new GoogleCloudAuthPlugin({
      apiToken: apiKey,
      autoRefreshToken: true,
    }));
    tiles.registerPlugin(new GLTFExtensionsPlugin({ dracoLoader }));
    tiles.registerPlugin(new ReorientationPlugin({
      lat: latRad,
      lon: lonRad,
      height: 0,
      azimuth: Math.PI,
      recenter: true,
    }));

    tiles.errorTarget = 2;
    tiles.maxDepth = 50;
    tiles.loadSiblings = false;
    tiles.lruCache.maxSize = 800;
    tiles.lruCache.minSize = 400;

    tiles.setCamera(camera);
    tiles.setResolutionFromRenderer(camera, gl);
    scene.add(tiles.group);

    tilesRef.current = tiles;
    tilesGroupRef.current = tiles.group;
    alignedRef.current = false;

    return () => {
      scene.remove(tiles.group);
      tiles.dispose();
      tilesRef.current = null;
      tilesGroupRef.current = null;
      alignedRef.current = false;
    };
  }, [latitude, longitude, apiKey, scene, camera, gl]);

  const raycaster = useRef(new THREE.Raycaster());

  useFrame(() => {
    const tiles = tilesRef.current;
    if (!tiles) return;

    const perspCam = camera as THREE.PerspectiveCamera;
    if (perspCam.far < 100000) {
      perspCam.far = 100000;
      perspCam.near = 1;
      perspCam.updateProjectionMatrix();
    }

    camera.updateMatrixWorld();
    tiles.setResolutionFromRenderer(camera, gl);
    tiles.update();

    tiles.group.traverse((obj: any) => {
      if (obj.isMesh) obj.frustumCulled = false;
    });

    // Auto-align: raycast downward from above origin to find the tile
    // ground level, then shift the group so ground aligns with Y=0
    if (!alignedRef.current) {
      const meshes: THREE.Mesh[] = [];
      tiles.group.traverse((obj: any) => {
        if (obj.isMesh) meshes.push(obj);
      });

      if (meshes.length > 20) {
        raycaster.current.set(
          new THREE.Vector3(0, 10000, 0),
          new THREE.Vector3(0, -1, 0)
        );
        raycaster.current.far = 20000;

        const hits = raycaster.current.intersectObjects(meshes, false);
        if (hits.length > 0) {
          tiles.group.position.y -= hits[0].point.y;
          tiles.group.updateMatrixWorld(true);
          alignedRef.current = true;
        }
      }
    }
  });

  return null;
}
