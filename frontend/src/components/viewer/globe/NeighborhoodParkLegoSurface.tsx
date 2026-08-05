import { useMemo } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { resolveParkKitSkin } from '@/data/parkKitSkins';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  fitParkGroundGuides,
  resolveParkGroundProfile,
} from './parkGroundProfiles';

const RENDER_ORDER_SURFACE = 144;

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

/**
 * One-family LEGO surface pilot. Profile guides own geometry; the catalog
 * variant supplies only the interchangeable material skin. The shallow pieces
 * overlay the existing terrain-conforming park base, so no image API is used.
 */
export function NeighborhoodParkLegoSurface({
  zone,
  centroid,
}: {
  zone: SiteZone;
  centroid: { lng: number; lat: number };
}) {
  const skin = resolveParkKitSkin(zone);
  const program = useMemo(() => {
    if (!skin) return null;
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

  if (!skin || !program) return null;
  const toLocal = (x: number, y: number): [number, number] => ([
    program.minX + x * program.width,
    program.maxY - y * program.height,
  ]);

  return (
    <group name={`ParkLegoSurface_${skin.id}`}>
      <mesh position={[0, 0, 0.028]} renderOrder={RENDER_ORDER_SURFACE} receiveShadow>
        <shapeGeometry args={[program.baseShape]} />
        <meshStandardMaterial color={skin.baseGround} roughness={0.96} />
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
