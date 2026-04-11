/**
 * GlobePegman.tsx — Street view camera marker on the 3D globe.
 *
 * Shows an amber sphere at the pegman position with a view cone
 * indicating the camera direction.
 */

import { useMemo } from 'react';
import * as THREE from 'three';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { Html } from '@react-three/drei';
// geoUtils available if needed for distance calculations

const DEG_TO_RAD = Math.PI / 180;

interface GlobePegmanProps {
  position: [number, number]; // [lng, lat]
  angle: number; // compass degrees, 0=N
  terrainHeight?: number; // meters above WGS84 ellipsoid
}

export function GlobePegman({ position, angle, terrainHeight = 1045 }: GlobePegmanProps) {
  const [lng, lat] = position;

  // View cone geometry in local ENU coordinates
  const coneGeometry = useMemo(() => {
    const fovDeg = 70;
    const distanceMeters = 100; // Shorter than the 200m cone for visual clarity
    const halfFov = (fovDeg / 2) * DEG_TO_RAD;

    // Convert compass heading to math angle (0=North → +Y in ENU, East = +X)
    const headingRad = angle * DEG_TO_RAD;

    // Left and right angles of the cone
    const leftAngle = headingRad - halfFov;
    const rightAngle = headingRad + halfFov;

    // Create triangle fan: origin → arc from left to right
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    // Arc from left to right
    const steps = 12;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const a = leftAngle + t * (rightAngle - leftAngle);
      shape.lineTo(Math.sin(a) * distanceMeters, Math.cos(a) * distanceMeters);
    }
    shape.lineTo(0, 0);

    return new THREE.ShapeGeometry(shape);
  }, [angle]);

  return (
    <EastNorthUpFrame lat={lat * DEG_TO_RAD} lon={lng * DEG_TO_RAD} height={terrainHeight}>
      {/* Pegman sphere */}
      <mesh position={[0, 0, 5]}>
        <sphereGeometry args={[5, 16, 16]} />
        <meshBasicMaterial color="#f59e0b" depthWrite={false} />
      </mesh>

      {/* View cone */}
      <mesh geometry={coneGeometry} position={[0, 0, 1]} rotation={[0, 0, 0]}>
        <meshBasicMaterial
          color="#f59e0b"
          transparent
          opacity={0.25}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Cone outline */}
      <mesh geometry={coneGeometry} position={[0, 0, 1.1]}>
        <meshBasicMaterial
          color="#f59e0b"
          transparent
          opacity={0.6}
          wireframe
          depthWrite={false}
        />
      </mesh>

      {/* Direction label */}
      <Html position={[0, 0, 15]} center style={{ pointerEvents: 'none' }}>
        <div className="rounded-full bg-amber-500/90 px-2 py-0.5 text-[10px] font-bold text-white">
          👁️
        </div>
      </Html>
    </EastNorthUpFrame>
  );
}
