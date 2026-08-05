import { useEffect, useMemo } from 'react';
import { useLoader } from '@react-three/fiber';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  resolveParkKitSkin,
  type ParkKitSkin,
  type ParkSkinTextureSet,
} from '@/data/parkKitSkins';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  fitParkGroundGuides,
  resolveParkGroundProfile,
} from './parkGroundProfiles';

const RENDER_ORDER_SURFACE = 144;

function useParkSurfaceProgram(
  zone: SiteZone,
  centroid: { lng: number; lat: number },
  skin: ParkKitSkin,
) {
  return useMemo(() => {
    const mPerLon = metersPerDegLon(centroid.lat);
    const ring = zone.coordinates.map(([lng, lat]) => ([
      (lng - centroid.lng) * mPerLon,
      (lat - centroid.lat) * METERS_PER_DEG_LAT,
    ] as [number, number]));
    const minX = Math.min(...ring.map(([x]) => x));
    const maxX = Math.max(...ring.map(([x]) => x));
    const minY = Math.min(...ring.map(([, y]) => y));
    const maxY = Math.max(...ring.map(([, y]) => y));
    const width = maxX - minX;
    const height = maxY - minY;
    const normalizedRing = ring.map(([x, y]) => ([
      width > 0 ? (x - minX) / width : 0.5,
      height > 0 ? (maxY - y) / height : 0.5,
    ] as [number, number]));
    const guides = fitParkGroundGuides(
      resolveParkGroundProfile(zone).guides,
      { width, height },
      normalizedRing,
    ).guides;
    const baseShape = new THREE.Shape();
    ring.forEach(([x, y], index) => {
      if (index === 0) baseShape.moveTo(x, y);
      else baseShape.lineTo(x, y);
    });
    baseShape.closePath();
    return { minX, maxY, width, height, guides, baseShape };
  }, [centroid.lat, centroid.lng, skin, zone]);
}

function ParkLegoPath({
  points,
  width,
  color,
  edgeColor,
}: {
  points: Array<[number, number]>;
  width: number;
  color: string;
  edgeColor: string;
}) {
  if (points.length < 2) return null;
  const segments = points.slice(1).map((end, index) => {
    const start = points[index];
    const dx = end[0] - start[0];
    const dy = end[1] - start[1];
    return {
      x: (start[0] + end[0]) / 2,
      y: (start[1] + end[1]) / 2,
      length: Math.hypot(dx, dy),
      rotation: Math.atan2(dy, dx),
    };
  });
  return (
    <group>
      {segments.map((segment, index) => (
        <group key={`segment-${index}`}>
          <mesh
            position={[segment.x, segment.y, 0.07]}
            rotation={[0, 0, segment.rotation]}
            renderOrder={RENDER_ORDER_SURFACE}
            receiveShadow
          >
            <boxGeometry args={[segment.length + width, width + 0.32, 0.045]} />
            <meshStandardMaterial color={edgeColor} roughness={0.94} />
          </mesh>
          <mesh
            position={[segment.x, segment.y, 0.096]}
            rotation={[0, 0, segment.rotation]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <boxGeometry args={[segment.length + width * 0.82, width, 0.035]} />
            <meshStandardMaterial color={color} roughness={0.9} />
          </mesh>
        </group>
      ))}
      {points.map(([x, y], index) => (
        <group key={`joint-${index}`}>
          <mesh
            position={[x, y, 0.07]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_SURFACE}
            receiveShadow
          >
            <cylinderGeometry args={[width * 0.56, width * 0.56, 0.045, 18]} />
            <meshStandardMaterial color={edgeColor} roughness={0.94} />
          </mesh>
          <mesh
            position={[x, y, 0.097]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <cylinderGeometry args={[width * 0.5, width * 0.5, 0.035, 18]} />
            <meshStandardMaterial color={color} roughness={0.9} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function TiledParkMaterial({
  textureSet,
  widthM,
  heightM,
  worldUv = false,
}: {
  textureSet: ParkSkinTextureSet;
  widthM: number;
  heightM: number;
  worldUv?: boolean;
}) {
  const [loadedAlbedo, loadedNormal, loadedRoughness] = useLoader(THREE.TextureLoader, [
    textureSet.albedo,
    textureSet.normal,
    textureSet.roughness,
  ]);
  const [albedo, normal, roughness] = useMemo(() => [
    loadedAlbedo.clone(),
    loadedNormal.clone(),
    loadedRoughness.clone(),
  ], [loadedAlbedo, loadedNormal, loadedRoughness]);
  useEffect(() => {
    albedo.colorSpace = THREE.SRGBColorSpace;
    normal.colorSpace = THREE.NoColorSpace;
    roughness.colorSpace = THREE.NoColorSpace;
    for (const texture of [albedo, normal, roughness]) {
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.RepeatWrapping;
      texture.anisotropy = 8;
      if (worldUv) {
        texture.matrixAutoUpdate = false;
        texture.matrix.setUvTransform(
          0,
          0,
          1 / textureSet.metresPerTile,
          -1 / textureSet.metresPerTile,
          0,
          0,
          0,
        );
      } else {
        texture.repeat.set(
          Math.max(widthM / textureSet.metresPerTile, 0.2),
          Math.max(heightM / textureSet.metresPerTile, 0.2),
        );
      }
      texture.needsUpdate = true;
    }
    return () => {
      albedo.dispose();
      normal.dispose();
      roughness.dispose();
    };
  }, [albedo, heightM, normal, roughness, textureSet.metresPerTile, widthM, worldUv]);
  return (
    <meshStandardMaterial
      map={albedo}
      normalMap={normal}
      normalScale={new THREE.Vector2(0.22, 0.22)}
      roughnessMap={roughness}
      roughness={0.96}
    />
  );
}

function AdaptiveParkLegoPath({
  points,
  width,
  textureSet,
  edgeColor,
}: {
  points: Array<[number, number]>;
  width: number;
  textureSet: ParkSkinTextureSet;
  edgeColor: string;
}) {
  if (points.length < 2) return null;
  const segments = points.slice(1).map((end, index) => {
    const start = points[index];
    const dx = end[0] - start[0];
    const dy = end[1] - start[1];
    return {
      x: (start[0] + end[0]) / 2,
      y: (start[1] + end[1]) / 2,
      length: Math.hypot(dx, dy),
      rotation: Math.atan2(dy, dx),
    };
  });
  return (
    <group>
      {segments.map((segment, index) => (
        <group key={`adaptive-segment-${index}`}>
          <mesh
            position={[segment.x, segment.y, 0.07]}
            rotation={[0, 0, segment.rotation]}
            renderOrder={RENDER_ORDER_SURFACE}
            receiveShadow
          >
            <boxGeometry args={[segment.length + width, width + 0.32, 0.045]} />
            <meshStandardMaterial color={edgeColor} roughness={0.94} />
          </mesh>
          <mesh
            position={[segment.x, segment.y, 0.096]}
            rotation={[0, 0, segment.rotation]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <boxGeometry args={[segment.length + width * 0.82, width, 0.035]} />
            <TiledParkMaterial
              textureSet={textureSet}
              widthM={segment.length + width * 0.82}
              heightM={width}
            />
          </mesh>
        </group>
      ))}
      {points.map(([x, y], index) => (
        <group key={`adaptive-joint-${index}`}>
          <mesh
            position={[x, y, 0.07]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_SURFACE}
            receiveShadow
          >
            <cylinderGeometry args={[width * 0.56, width * 0.56, 0.045, 18]} />
            <meshStandardMaterial color={edgeColor} roughness={0.94} />
          </mesh>
          <mesh
            position={[x, y, 0.097]}
            rotation={[Math.PI / 2, 0, 0]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <cylinderGeometry args={[width * 0.5, width * 0.5, 0.035, 18]} />
            <TiledParkMaterial textureSet={textureSet} widthM={width} heightM={width} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function AdaptiveNeighborhoodParkLegoSurface({
  zone,
  centroid,
  skin,
}: {
  zone: SiteZone;
  centroid: { lng: number; lat: number };
  skin: ParkKitSkin & { materialKit: NonNullable<ParkKitSkin['materialKit']> };
}) {
  const program = useParkSurfaceProgram(zone, centroid, skin);
  const kit = skin.materialKit;
  const toLocal = (x: number, y: number): [number, number] => ([
    program.minX + x * program.width,
    program.maxY - y * program.height,
  ]);
  return (
    <group name={`AdaptiveParkLegoSurface_${skin.id}`}>
      <mesh position={[0, 0, 0.028]} renderOrder={RENDER_ORDER_SURFACE} receiveShadow>
        <shapeGeometry args={[program.baseShape]} />
        <TiledParkMaterial
          textureSet={kit.base}
          widthM={program.width}
          heightM={program.height}
          worldUv
        />
      </mesh>
      {program.guides.map((guide, index) => {
        if (!guide.materialRole) return null;
        const textureSet = kit.materials[guide.materialRole];
        const fallback = skin.materials[guide.materialRole];
        if (guide.kind === 'polyline' && (guide.points?.length ?? 0) >= 2) {
          return (
            <AdaptiveParkLegoPath
              key={`adaptive-path-${index}`}
              points={guide.points!.map(([x, y]) => toLocal(x, y))}
              width={guide.strokeWidthM ?? 3}
              textureSet={textureSet}
              edgeColor={fallback.edge}
            />
          );
        }
        const width = guide.widthM ?? guide.width * program.width;
        const height = guide.heightM ?? guide.height * program.height;
        const [x, y] = toLocal(guide.x, guide.y);
        if (guide.kind === 'rectangle' || guide.kind === 'rounded_rectangle') {
          return (
            <mesh key={`adaptive-room-${index}`} position={[x, y, 0.09]} renderOrder={RENDER_ORDER_SURFACE + 1} receiveShadow>
              <boxGeometry args={[width, height, 0.08]} />
              <TiledParkMaterial textureSet={textureSet} widthM={width} heightM={height} />
            </mesh>
          );
        }
        return (
          <mesh
            key={`adaptive-room-${index}`}
            position={[x, y, 0.084]}
            scale={[width, height, 1]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <circleGeometry args={[0.5, 48]} />
            <TiledParkMaterial textureSet={textureSet} widthM={width} heightM={height} />
          </mesh>
        );
      })}
    </group>
  );
}

/**
 * One-family LEGO surface pilot. Profile guides own geometry; the catalog
 * variant supplies only the interchangeable material skin. The shallow pieces
 * overlay the existing terrain-conforming park base, so no image API is used.
 */
function NeighborhoodParkLegoSurfaceWithSkin({
  zone,
  centroid,
  skin,
}: {
  zone: SiteZone;
  centroid: { lng: number; lat: number };
  skin: ParkKitSkin;
}) {
  const [loadedAlbedoMap, loadedNormalMap, loadedRoughnessMap] = useLoader(THREE.TextureLoader, [
    skin.atlas.albedo,
    skin.atlas.normal,
    skin.atlas.roughness,
  ]);
  const [albedoMap, normalMap, roughnessMap] = useMemo(() => [
    loadedAlbedoMap.clone(),
    loadedNormalMap.clone(),
    loadedRoughnessMap.clone(),
  ], [loadedAlbedoMap, loadedNormalMap, loadedRoughnessMap]);
  useEffect(() => {
    return () => {
      albedoMap.dispose();
      normalMap.dispose();
      roughnessMap.dispose();
    };
  }, [albedoMap, normalMap, roughnessMap]);
  useEffect(() => {
    albedoMap.colorSpace = THREE.SRGBColorSpace;
    normalMap.colorSpace = THREE.NoColorSpace;
    roughnessMap.colorSpace = THREE.NoColorSpace;
    for (const texture of [albedoMap, normalMap, roughnessMap]) {
      texture.wrapS = THREE.ClampToEdgeWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;
      texture.anisotropy = 8;
      texture.needsUpdate = true;
    }
  }, [albedoMap, normalMap, roughnessMap]);
  const program = useParkSurfaceProgram(zone, centroid, skin);

  useEffect(() => {
    if (!program || program.width <= 0 || program.height <= 0) return;
    for (const texture of [albedoMap, normalMap, roughnessMap]) {
      texture.matrixAutoUpdate = false;
      texture.matrix.setUvTransform(
        -program.minX / program.width,
        program.maxY / program.height,
        1 / program.width,
        -1 / program.height,
        0,
        0,
        0,
      );
      texture.needsUpdate = true;
    }
  }, [albedoMap, normalMap, program, roughnessMap]);

  if (!program) return null;
  const toLocal = (x: number, y: number): [number, number] => ([
    program.minX + x * program.width,
    program.maxY - y * program.height,
  ]);

  return (
    <group name={`ParkLegoSurface_${skin.id}`}>
      <mesh position={[0, 0, 0.028]} renderOrder={RENDER_ORDER_SURFACE} receiveShadow>
        <shapeGeometry args={[program.baseShape]} />
        <meshStandardMaterial
          map={albedoMap}
          normalMap={normalMap}
          normalScale={new THREE.Vector2(0.24, 0.24)}
          roughnessMap={roughnessMap}
          roughness={0.96}
        />
      </mesh>
      {program.guides.map((guide, index) => {
        if (!guide.materialRole) return null;
        const material = skin.materials[guide.materialRole];
        if (guide.kind === 'polyline' && (guide.points?.length ?? 0) >= 2) {
          return (
            <ParkLegoPath
              key={`path-${index}`}
              points={guide.points!.map(([x, y]) => toLocal(x, y))}
              width={guide.strokeWidthM ?? 3}
              color={material.fill}
              edgeColor={material.edge}
            />
          );
        }
        const width = guide.widthM ?? guide.width * program.width;
        const height = guide.heightM ?? guide.height * program.height;
        const [x, y] = toLocal(guide.x, guide.y);
        if (guide.kind === 'rectangle' || guide.kind === 'rounded_rectangle') {
          return (
            <mesh key={`room-${index}`} position={[x, y, 0.09]} renderOrder={RENDER_ORDER_SURFACE + 1} receiveShadow>
              <boxGeometry args={[width, height, 0.08]} />
              <meshStandardMaterial color={material.fill} roughness={0.92} />
            </mesh>
          );
        }
        return (
          <mesh
            key={`room-${index}`}
            position={[x, y, 0.084]}
            scale={[width, height, 1]}
            renderOrder={RENDER_ORDER_SURFACE + 1}
            receiveShadow
          >
            <circleGeometry args={[0.5, 48]} />
            <meshStandardMaterial color={material.fill} roughness={0.94} />
          </mesh>
        );
      })}
    </group>
  );
}

export function NeighborhoodParkLegoSurface({
  zone,
  centroid,
}: {
  zone: SiteZone;
  centroid: { lng: number; lat: number };
}) {
  const skin = resolveParkKitSkin(zone);
  if (!skin) return null;
  if (skin.materialKit) {
    return (
      <AdaptiveNeighborhoodParkLegoSurface
        zone={zone}
        centroid={centroid}
        skin={skin as ParkKitSkin & { materialKit: NonNullable<ParkKitSkin['materialKit']> }}
      />
    );
  }
  return <NeighborhoodParkLegoSurfaceWithSkin zone={zone} centroid={centroid} skin={skin} />;
}
