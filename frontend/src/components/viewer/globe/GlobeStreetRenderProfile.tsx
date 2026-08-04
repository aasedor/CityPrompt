import { useEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';

const DEG_TO_RAD = Math.PI / 180;
const SHADOW_ROOT_NAMES = [
  'siteforge-direct3d-ground',
  'siteforge-direct3d-landscape',
  'siteforge-direct3d-street',
  'siteforge-direct3d-park',
  'siteforge-direct3d-building',
] as const;

interface GlobeStreetRenderProfileProps {
  latitude: number;
  longitude: number;
  terrainHeight: number;
}

/** High-quality deterministic renderer state used only while an authored
 * City Prompt street frame or route is being captured. */
export function GlobeStreetRenderProfile({
  latitude,
  longitude,
  terrainHeight,
}: GlobeStreetRenderProfileProps) {
  const { gl, scene } = useThree();
  const lighting = useMemo(() => {
    const targetPosition = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(
      latitude * DEG_TO_RAD,
      longitude * DEG_TO_RAD,
      terrainHeight,
      targetPosition,
    );
    const east = new THREE.Vector3();
    const north = new THREE.Vector3();
    const up = new THREE.Vector3();
    WGS84_ELLIPSOID.getEastNorthUpAxes(
      latitude * DEG_TO_RAD,
      longitude * DEG_TO_RAD,
      east,
      north,
      up,
    );
    const sunPosition = targetPosition.clone()
      .addScaledVector(east, -110)
      .addScaledVector(north, -140)
      .addScaledVector(up, 190);
    const target = new THREE.Object3D();
    target.position.copy(targetPosition);
    return { sunPosition, target };
  }, [latitude, longitude, terrainHeight]);

  useEffect(() => {
    const previous = {
      toneMapping: gl.toneMapping,
      toneMappingExposure: gl.toneMappingExposure,
      shadowEnabled: gl.shadowMap.enabled,
      shadowType: gl.shadowMap.type,
      shadowAutoUpdate: gl.shadowMap.autoUpdate,
    };
    gl.toneMapping = THREE.ACESFilmicToneMapping;
    gl.toneMappingExposure = 1.05;
    gl.shadowMap.enabled = true;
    gl.shadowMap.type = THREE.PCFSoftShadowMap;
    gl.shadowMap.autoUpdate = true;
    gl.shadowMap.needsUpdate = true;

    const meshState: Array<{
      mesh: THREE.Mesh;
      castShadow: boolean;
      receiveShadow: boolean;
    }> = [];
    SHADOW_ROOT_NAMES.forEach((name) => {
      const root = scene.getObjectByName(name);
      const casts = name !== 'siteforge-direct3d-ground' && name !== 'siteforge-direct3d-street';
      root?.traverse((object) => {
        const mesh = object as THREE.Mesh;
        if (!mesh.isMesh) return;
        meshState.push({
          mesh,
          castShadow: mesh.castShadow,
          receiveShadow: mesh.receiveShadow,
        });
        mesh.castShadow = casts;
        mesh.receiveShadow = true;
      });
    });

    return () => {
      meshState.forEach(({ mesh, castShadow, receiveShadow }) => {
        mesh.castShadow = castShadow;
        mesh.receiveShadow = receiveShadow;
      });
      gl.toneMapping = previous.toneMapping;
      gl.toneMappingExposure = previous.toneMappingExposure;
      gl.shadowMap.enabled = previous.shadowEnabled;
      gl.shadowMap.type = previous.shadowType;
      gl.shadowMap.autoUpdate = previous.shadowAutoUpdate;
      gl.shadowMap.needsUpdate = true;
    };
  }, [gl, scene]);

  return (
    <>
      <ambientLight intensity={0.28} color="#eef4ff" />
      <hemisphereLight args={['#dcecff', '#6f675b', 0.72]} />
      <primitive object={lighting.target} />
      <directionalLight
        position={lighting.sunPosition}
        target={lighting.target}
        intensity={2.35}
        color="#fff1d2"
        castShadow
        shadow-mapSize-width={4096}
        shadow-mapSize-height={4096}
        shadow-camera-near={0.5}
        shadow-camera-far={520}
        shadow-camera-left={-120}
        shadow-camera-right={120}
        shadow-camera-top={120}
        shadow-camera-bottom={-120}
        shadow-bias={-0.00012}
        shadow-normalBias={0.035}
      />
    </>
  );
}
