import { Component, Suspense, useMemo, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import type { NativeStreetPose } from './nativeStreetPilot';

class ModuleBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed
    ? <group userData={{ publicRealmTrialStatus: 'unavailable' }} /> : this.props.children; }
}

function RigidModule({ pose }: { pose: NativeStreetPose }) {
  const { scene } = useGLTF(pose.url);
  const copy = useMemo(() => scene.clone(true), [scene]);
  return <group position={[pose.x, pose.y, pose.z + pose.surfaceLiftM]} rotation={[0, 0, pose.yaw]}>
    {pose.wellWidthM && pose.wellDepthM && <mesh position={[0, 0, -0.015]} receiveShadow renderOrder={149}>
      <planeGeometry args={[pose.wellWidthM - 0.08, pose.wellDepthM - 0.08]} />
      <meshStandardMaterial color="#392e25" roughness={1} side={THREE.DoubleSide} />
    </mesh>}
    <group rotation={[Math.PI / 2, 0, 0]} scale={pose.scale}>
      <primitive object={copy} dispose={null} />
    </group>
  </group>;
}

/** DEV-only component trial above the metric street bands. The checked-in
 * modules keep their native dimensions and are not a public catalogue model. */
export function GlobeNativeStreetPilotModules({ poses }: { poses: NativeStreetPose[] }) {
  return <ModuleBoundary><Suspense fallback={<group userData={{ publicRealmTrialStatus: 'loading' }} />}>
    <group userData={{ publicRealmTrialStatus: 'ready' }}>
      {poses.map((pose, index) => <RigidModule key={`${pose.kind}-${index}`} pose={pose} />)}
    </group>
  </Suspense></ModuleBoundary>;
}
