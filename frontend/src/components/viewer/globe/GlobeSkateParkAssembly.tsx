import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';

import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { fitSkateParkV0Program, type SkateParkPoint } from './skateParkFit';
import { batch16ParkSkinForSelection } from './parkBatch16Skins';

const SKATE_RENDER_ORDER = 148;
const ASSET_ROOT = '/park-kits/skate-park';

const ASSETS = Object.freeze({
  bowl: `${ASSET_ROOT}/skate-bowl-module.glb`,
  hubba: `${ASSET_ROOT}/stair-hubba-module.glb`,
  rail: `${ASSET_ROOT}/skate-rail.glb`,
  ledge: `${ASSET_ROOT}/skate-ledge.glb`,
});

interface SkateMaterialMaps {
  map: THREE.Texture;
  normalMap: THREE.Texture;
  roughnessMap: THREE.Texture;
  aoMap: THREE.Texture;
}

function useArchetypeMaterial(skinSlug: string, role: 'paver' | 'lawn', metresPerTile: number): SkateMaterialMaps {
  const skinRoot = `/park-skins/${skinSlug}/adaptive-v1`;
  const source = useTexture({
    map: `${skinRoot}/${role}/albedo.jpg`,
    normalMap: `${skinRoot}/${role}/normal.png`,
    roughnessMap: `${skinRoot}/${role}/roughness.jpg`,
    aoMap: `${skinRoot}/${role}/ao.jpg`,
  });
  const tiled = useMemo(() => {
    const entries = Object.entries(source).map(([key, texture]) => {
      const clone = texture.clone();
      clone.wrapS = THREE.RepeatWrapping;
      clone.wrapT = THREE.RepeatWrapping;
      // Shape/Extrude UVs are authored in local metres.
      clone.repeat.set(1 / metresPerTile, 1 / metresPerTile);
      clone.needsUpdate = true;
      return [key, clone];
    });
    const maps = Object.fromEntries(entries) as unknown as SkateMaterialMaps;
    maps.map.colorSpace = THREE.SRGBColorSpace;
    return maps;
  }, [metresPerTile, source]);
  useEffect(() => () => Object.values(tiled).forEach((texture) => texture.dispose()), [tiled]);
  return tiled;
}

function ensureUv1(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
  const uv = geometry.getAttribute('uv');
  if (uv && !geometry.getAttribute('uv1')) geometry.setAttribute('uv1', uv.clone());
  return geometry;
}

function buildSkateDeckGeometry(): THREE.ExtrudeGeometry {
  const shape = new THREE.Shape();
  shape.moveTo(-20, -15);
  shape.lineTo(20, -15);
  shape.lineTo(20, 15);
  shape.lineTo(-20, 15);
  shape.closePath();
  for (const centerX of [-10.25, 10.25]) {
    const opening = new THREE.Path();
    opening.absellipse(centerX, 0, 7, 11.2, 0, Math.PI * 2, true, 0);
    shape.holes.push(opening);
  }
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.22,
    bevelEnabled: false,
    curveSegments: 72,
  });
  geometry.translate(0, 0, -0.11);
  return ensureUv1(geometry) as THREE.ExtrudeGeometry;
}

function buildGrassBufferGeometry(
  boundary: readonly SkateParkPoint[],
  fit: NonNullable<ReturnType<typeof fitSkateParkV0Program>>,
): THREE.ShapeGeometry {
  const outer = new THREE.Shape();
  outer.moveTo(boundary[0].x, boundary[0].y);
  boundary.slice(1).forEach(({ x, y }) => outer.lineTo(x, y));
  outer.closePath();
  const halfWidth = fit.widthM / 2;
  const halfDepth = fit.depthM / 2;
  const cos = Math.cos(fit.rotationRad);
  const sin = Math.sin(fit.rotationRad);
  const at = (x: number, y: number): SkateParkPoint => ({
    x: fit.center.x + x * cos - y * sin,
    y: fit.center.y + x * sin + y * cos,
  });
  const corners = [
    at(-halfWidth, -halfDepth),
    at(-halfWidth, halfDepth),
    at(halfWidth, halfDepth),
    at(halfWidth, -halfDepth),
  ];
  const hole = new THREE.Path();
  hole.moveTo(corners[0].x, corners[0].y);
  corners.slice(1).forEach(({ x, y }) => hole.lineTo(x, y));
  hole.closePath();
  outer.holes.push(hole);
  return ensureUv1(new THREE.ShapeGeometry(outer, 24)) as THREE.ShapeGeometry;
}

function MetricGlb({
  url,
  position = [0, 0, 0],
}: {
  url: string;
  position?: [number, number, number];
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.renderOrder = SKATE_RENDER_ORDER + 2;
    });
    return next;
  }, [scene]);
  // Blender exports glTF Y-up. The City Prompt ENU frame is Z-up. No scale or
  // recentering is applied: every GLB remains at its authored metric origin.
  return (
    <group position={position} rotation={[Math.PI / 2, 0, 0]}>
      <primitive object={clone} />
    </group>
  );
}

function SpectatorBench() {
  return (
    <group position={[0, 13, 0.18]} rotation={[0, 0, Math.PI]}>
      {[-0.72, 0, 0.72].map((y) => (
        <mesh key={`bench-board-${y}`} position={[0, y * 0.42, 0.62 + (y + 0.72) * 0.16]} renderOrder={SKATE_RENDER_ORDER + 3}>
          <boxGeometry args={[4.2, 0.28, 0.12]} />
          <meshStandardMaterial color="#927552" roughness={0.88} />
        </mesh>
      ))}
      {[-1.55, 1.55].map((x) => (
        <group key={`bench-frame-${x}`} position={[x, 0, 0]}>
          <mesh position={[0, -0.2, 0.38]} rotation={[0.12, 0, 0]} renderOrder={SKATE_RENDER_ORDER + 2}>
            <boxGeometry args={[0.09, 0.09, 0.78]} />
            <meshStandardMaterial color="#515758" metalness={0.46} roughness={0.56} />
          </mesh>
          <mesh position={[0, 0.25, 0.58]} rotation={[-0.5, 0, 0]} renderOrder={SKATE_RENDER_ORDER + 2}>
            <boxGeometry args={[0.09, 0.09, 0.95]} />
            <meshStandardMaterial color="#515758" metalness={0.46} roughness={0.56} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function LoadedSkatePark({
  boundary,
  fit,
  terrainZ,
  skinSlug,
}: {
  boundary: readonly SkateParkPoint[];
  fit: NonNullable<ReturnType<typeof fitSkateParkV0Program>>;
  terrainZ: (x: number, y: number) => number;
  skinSlug: string;
}) {
  const concrete = useArchetypeMaterial(skinSlug, 'paver', 4);
  const lawn = useArchetypeMaterial(skinSlug, 'lawn', 5);
  const deckGeometry = useMemo(buildSkateDeckGeometry, []);
  const grassGeometry = useMemo(
    () => buildGrassBufferGeometry(boundary, fit),
    [boundary, fit],
  );
  useEffect(() => () => deckGeometry.dispose(), [deckGeometry]);
  useEffect(() => () => grassGeometry.dispose(), [grassGeometry]);
  const baseZ = terrainZ(fit.center.x, fit.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;

  return (
    <group renderOrder={SKATE_RENDER_ORDER}>
      <mesh geometry={grassGeometry} position={[0, 0, baseZ - 0.015]} receiveShadow renderOrder={SKATE_RENDER_ORDER}>
        <meshStandardMaterial {...lawn} roughness={0.96} normalScale={new THREE.Vector2(0.52, 0.52)} />
      </mesh>
      <group
        position={[fit.center.x, fit.center.y, baseZ]}
        rotation={[0, 0, fit.rotationRad]}
        scale={[fit.scale, fit.scale, fit.scale]}
      >
        <mesh geometry={deckGeometry} receiveShadow renderOrder={SKATE_RENDER_ORDER + 1}>
          <meshStandardMaterial {...concrete} roughness={0.9} normalScale={new THREE.Vector2(0.34, 0.34)} />
        </mesh>
        <MetricGlb url={ASSETS.bowl} position={[-10.25, 0, 0]} />
        <MetricGlb url={ASSETS.bowl} position={[10.25, 0, 0]} />
        <MetricGlb url={ASSETS.hubba} />
        <MetricGlb url={ASSETS.rail} position={[0, -8, 0]} />
        <MetricGlb url={ASSETS.ledge} position={[0, 9, 0]} />
        <SpectatorBench />
      </group>
    </group>
  );
}

export function GlobeSkateParkAssembly({
  boundary,
  terrainZ,
  variantId,
}: {
  boundary: readonly SkateParkPoint[];
  terrainZ: (x: number, y: number) => number;
  variantId?: string;
}) {
  const fit = useMemo(() => fitSkateParkV0Program(boundary), [boundary]);
  const skinSlug = batch16ParkSkinForSelection('skate_park', variantId ?? '')?.slug ?? 'skate-park';
  if (!fit) return null;
  return <LoadedSkatePark boundary={boundary} fit={fit} terrainZ={terrainZ} skinSlug={skinSlug} />;
}

Object.values(ASSETS).forEach((url) => useGLTF.preload(url));
