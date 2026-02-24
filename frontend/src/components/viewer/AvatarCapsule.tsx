import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

interface AvatarCapsuleProps {
  position: [number, number, number];
  lookDirection?: [number, number, number];
  color: string;
  name: string;
}

export function AvatarCapsule({ position, lookDirection, color, name }: AvatarCapsuleProps) {
  const groupRef = useRef<THREE.Group>(null);
  const targetPos = useRef(new THREE.Vector3(...position));

  // Update target when position prop changes
  targetPos.current.set(...position);

  useFrame(() => {
    if (!groupRef.current) return;
    // Smooth lerp to target position
    groupRef.current.position.lerp(targetPos.current, 0.1);

    // Derive yaw from look direction
    if (lookDirection) {
      const yaw = Math.atan2(lookDirection[0], lookDirection[2]);
      groupRef.current.rotation.y = yaw;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Body capsule: 0.5m tall, 0.25m radius */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <capsuleGeometry args={[0.15, 0.35, 8, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Head sphere: 0.2m radius */}
      <mesh position={[0, 0.85, 0]} castShadow>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Name label floating above */}
      <Html
        position={[0, 1.15, 0]}
        center
        distanceFactor={10}
        style={{ pointerEvents: 'none' }}
      >
        <div
          className="whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] font-medium text-white shadow-md"
          style={{ backgroundColor: color }}
        >
          {name}
        </div>
      </Html>
    </group>
  );
}
