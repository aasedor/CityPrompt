import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';

import kitManifest from '@/data/neighborhoodParkV0StickerKit.json';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { fitFixedParkProgram, type SkateParkPoint } from './skateParkFit';

const RENDER_ORDER = 148;
const FIXED_PROGRAM = Object.freeze({ widthM: 50, depthM: 38, clearanceM: 1.5 });

type SkinRole = 'asphalt' | 'paver' | 'safety';
type AssetId = keyof typeof kitManifest.assets;

interface MaterialMaps {
  map: THREE.Texture;
  normalMap: THREE.Texture;
  roughnessMap: THREE.Texture;
  aoMap: THREE.Texture;
}

function useStickerMaps(role: SkinRole, repeat: readonly [number, number]): MaterialMaps {
  const root = `${kitManifest.skin.baseUrl}/${role}`;
  const source = useTexture({
    map: `${root}/albedo.jpg`,
    normalMap: `${root}/normal.png`,
    roughnessMap: `${root}/roughness.jpg`,
    aoMap: `${root}/ao.jpg`,
  });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat[0], repeat[1]);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as MaterialMaps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function StickerPatch({
  kind,
  role,
  centerM,
  sizeM,
  yawDeg = 0,
  zM,
}: {
  kind: string;
  role: SkinRole;
  centerM: readonly [number, number];
  sizeM: readonly [number, number];
  yawDeg?: number;
  zM: number;
}) {
  const tileM = role === 'paver' ? 2.4 : role === 'asphalt' ? 3.2 : 2.8;
  const maps = useStickerMaps(role, [sizeM[0] / tileM, sizeM[1] / tileM]);
  const material = (
    <meshStandardMaterial
      {...maps}
      color="#ffffff"
      roughness={0.9}
      normalScale={new THREE.Vector2(0.42, 0.42)}
    />
  );
  return (
    <mesh
      position={[centerM[0], centerM[1], zM]}
      rotation={[0, 0, THREE.MathUtils.degToRad(yawDeg)]}
      scale={kind === 'ellipse' ? [sizeM[0] / 2, sizeM[1] / 2, 1] : undefined}
      receiveShadow
      renderOrder={RENDER_ORDER}
      userData={{ stickerOwner: 'neighborhood_park_v0', materialRole: role }}
    >
      {kind === 'ellipse'
        ? <circleGeometry args={[1, 72]} />
        : <planeGeometry args={[sizeM[0], sizeM[1]]} />}
      {material}
    </mesh>
  );
}

function MetricStickerObject({
  assetId,
  positionM,
  yawDeg,
}: {
  assetId: AssetId;
  positionM: readonly [number, number, number];
  yawDeg: number;
}) {
  const asset = kitManifest.assets[assetId];
  const { scene } = useGLTF(asset.url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.renderOrder = RENDER_ORDER + 2;
    });
    return next;
  }, [scene]);
  return (
    <group
      position={[positionM[0], positionM[1], positionM[2]]}
      rotation={[0, 0, THREE.MathUtils.degToRad(yawDeg)]}
      scale={1}
      userData={{
        stickerOwner: 'neighborhood_park_v0',
        fixedMetricObject: true,
        nonuniformScalingAllowed: false,
        semanticRole: asset.semantic,
      }}
    >
      <group rotation={[Math.PI / 2, 0, 0]}>
        <primitive object={clone} />
      </group>
    </group>
  );
}

export function GlobeNeighborhoodParkV0StickerAssembly({
  boundary,
  terrainZ,
}: {
  boundary: readonly SkateParkPoint[];
  terrainZ: (x: number, y: number) => number;
}) {
  const fit = useMemo(() => fitFixedParkProgram(boundary, FIXED_PROGRAM), [boundary]);
  if (!fit) return null;
  const baseZ = terrainZ(fit.center.x, fit.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  return (
    <group
      name="neighborhood-park-v0-sticker-method-assembly"
      position={[fit.center.x, fit.center.y, baseZ]}
      rotation={[0, 0, fit.rotationRad]}
      scale={1}
      userData={{
        archetypeId: kitManifest.archetypeId,
        variantId: kitManifest.variantId,
        representation: 'site_adaptive_whole_program',
        sourcePixelsProjected: false,
        wholeFixedKit: true,
      }}
    >
      {kitManifest.groundPatches.map((patch) => (
        <StickerPatch
          key={patch.id}
          kind={patch.kind}
          role={patch.role as SkinRole}
          centerM={patch.centerM as [number, number]}
          sizeM={patch.sizeM as [number, number]}
          yawDeg={'yawDeg' in patch ? patch.yawDeg : 0}
          zM={patch.zM}
        />
      ))}
      {kitManifest.placements.map((placement) => (
        <MetricStickerObject
          key={placement.id}
          assetId={placement.assetId as AssetId}
          positionM={placement.positionM as [number, number, number]}
          yawDeg={placement.yawDeg}
        />
      ))}
    </group>
  );
}

Object.values(kitManifest.assets).forEach((asset) => useGLTF.preload(asset.url));
