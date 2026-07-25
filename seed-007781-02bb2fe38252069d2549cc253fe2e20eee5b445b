import { useEffect, useMemo, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';

import {
  LANDSCAPE_TREE_PROFILES,
  LANDSCAPE_TREE_VARIANTS,
  selectLandscapeTreeVariant,
  type LandscapeTreeProfile,
  type LandscapeTreeVariant,
} from './landscapeKitProfiles';

export interface LandscapeTreePlacement {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scale: number;
}

interface TreeVariantInstancesProps {
  placements: LandscapeTreePlacement[];
  profile: LandscapeTreeProfile;
  texture: THREE.Texture;
  renderOrder: number;
}

function TreeVariantInstances({
  placements,
  profile,
  texture,
  renderOrder,
}: TreeVariantInstancesProps) {
  const trunkRef = useRef<THREE.InstancedMesh>(null);
  const crownARef = useRef<THREE.InstancedMesh>(null);
  const crownBRef = useRef<THREE.InstancedMesh>(null);
  const crownTopRef = useRef<THREE.InstancedMesh>(null);
  const trunkGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(1, 1.28, 1, 10);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const planeGeometry = useMemo(() => new THREE.PlaneGeometry(1, 1), []);

  useEffect(() => () => {
    trunkGeometry.dispose();
    planeGeometry.dispose();
  }, [planeGeometry, trunkGeometry]);

  useEffect(() => {
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const yawQuaternion = new THREE.Quaternion();
    const verticalQuaternion = new THREE.Quaternion();
    const localVertical = new THREE.Quaternion().setFromAxisAngle(
      new THREE.Vector3(1, 0, 0),
      Math.PI / 2,
    );
    const zAxis = new THREE.Vector3(0, 0, 1);

    placements.forEach((placement, index) => {
      const treeScale = placement.scale;
      yawQuaternion.setFromAxisAngle(zAxis, placement.yawRad);

      position.set(
        placement.x,
        placement.y,
        placement.z + profile.trunkHeightM * treeScale * 0.5,
      );
      scale.set(
        profile.trunkRadiusM * treeScale,
        profile.trunkRadiusM * treeScale,
        profile.trunkHeightM * treeScale,
      );
      matrix.compose(position, yawQuaternion, scale);
      trunkRef.current?.setMatrixAt(index, matrix);

      const crownCenterZ = placement.z + (
        profile.trunkHeightM + profile.crownHeightM * 0.40
      ) * treeScale;
      position.set(placement.x, placement.y, crownCenterZ);
      scale.set(
        profile.crownWidthM * treeScale,
        profile.crownHeightM * treeScale,
        1,
      );
      verticalQuaternion.multiplyQuaternions(yawQuaternion, localVertical);
      matrix.compose(position, verticalQuaternion, scale);
      crownARef.current?.setMatrixAt(index, matrix);

      yawQuaternion.setFromAxisAngle(zAxis, placement.yawRad + Math.PI / 2);
      verticalQuaternion.multiplyQuaternions(yawQuaternion, localVertical);
      matrix.compose(position, verticalQuaternion, scale);
      crownBRef.current?.setMatrixAt(index, matrix);

      yawQuaternion.setFromAxisAngle(zAxis, placement.yawRad + Math.PI / 5);
      position.z = placement.z + (
        profile.trunkHeightM + profile.crownHeightM * 0.68
      ) * treeScale;
      scale.set(
        profile.crownWidthM * 0.88 * treeScale,
        profile.crownDepthM * 0.88 * treeScale,
        1,
      );
      matrix.compose(position, yawQuaternion, scale);
      crownTopRef.current?.setMatrixAt(index, matrix);
    });

    for (const ref of [trunkRef, crownARef, crownBRef, crownTopRef]) {
      if (!ref.current) continue;
      ref.current.count = placements.length;
      ref.current.instanceMatrix.needsUpdate = true;
      ref.current.computeBoundingSphere();
    }
  }, [placements, profile]);

  if (placements.length === 0) return null;
  return (
    <>
      <instancedMesh
        ref={trunkRef}
        args={[trunkGeometry, undefined, placements.length]}
        renderOrder={renderOrder}
        frustumCulled={false}
      >
        <meshStandardMaterial color={profile.barkColor} roughness={0.98} />
      </instancedMesh>
      {[crownARef, crownBRef, crownTopRef].map((ref, index) => (
        <instancedMesh
          key={index}
          ref={ref}
          args={[planeGeometry, undefined, placements.length]}
          renderOrder={renderOrder + 1}
          frustumCulled={false}
        >
          <meshStandardMaterial
            map={texture}
            color={profile.foliageTint}
            alphaTest={0.18}
            side={THREE.DoubleSide}
            roughness={0.96}
            metalness={0}
          />
        </instancedMesh>
      ))}
    </>
  );
}

export function GlobeLandscapeTreeStand({
  placements,
  renderOrder = 145,
}: {
  placements: LandscapeTreePlacement[];
  renderOrder?: number;
}) {
  const { gl } = useThree();
  const textureUrls = LANDSCAPE_TREE_VARIANTS.map(
    (variant) => LANDSCAPE_TREE_PROFILES[variant].textureUrl,
  );
  const textures = useTexture(textureUrls);
  useEffect(() => {
    const maxAnisotropy = Math.min(8, gl.capabilities.getMaxAnisotropy());
    for (const texture of textures) {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = maxAnisotropy;
      texture.needsUpdate = true;
    }
  }, [gl, textures]);

  const grouped = useMemo(() => {
    const groups: Record<LandscapeTreeVariant, LandscapeTreePlacement[]> = {
      honey_locust: [],
      maple: [],
      ornamental_pear: [],
    };
    placements.forEach((placement, index) => {
      groups[selectLandscapeTreeVariant(placement, index)].push(placement);
    });
    return groups;
  }, [placements]);

  return (
    <>
      {LANDSCAPE_TREE_VARIANTS.map((variant, index) => (
        <TreeVariantInstances
          key={variant}
          placements={grouped[variant]}
          profile={LANDSCAPE_TREE_PROFILES[variant]}
          texture={textures[index]}
          renderOrder={renderOrder}
        />
      ))}
    </>
  );
}

export interface LandscapeBenchPlacement {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scale: number;
}

export function GlobeLandscapeBenchStand({
  placements,
  renderOrder = 145,
}: {
  placements: LandscapeBenchPlacement[];
  renderOrder?: number;
}) {
  return (
    <>
      {placements.map((placement, index) => (
        <group
          key={`${Math.round(placement.x * 10)}-${Math.round(placement.y * 10)}-${index}`}
          position={[placement.x, placement.y, placement.z]}
          rotation={[0, 0, placement.yawRad]}
          scale={[placement.scale, placement.scale, placement.scale]}
          renderOrder={renderOrder}
        >
          {[-0.20, -0.10, 0, 0.10, 0.20].map((slatY) => (
            <mesh key={`seat-${slatY}`} position={[0, slatY, 0.48]} renderOrder={renderOrder}>
              <boxGeometry args={[1.86, 0.074, 0.055]} />
              <meshStandardMaterial color="#8a5d3d" roughness={0.82} />
            </mesh>
          ))}
          {[0.68, 0.81, 0.94].map((slatZ) => (
            <mesh key={`back-${slatZ}`} position={[0, 0.255, slatZ]} rotation={[Math.PI / 18, 0, 0]} renderOrder={renderOrder}>
              <boxGeometry args={[1.86, 0.055, 0.075]} />
              <meshStandardMaterial color="#7b5036" roughness={0.84} />
            </mesh>
          ))}
          {[-0.68, 0.68].map((legX) => (
            <group key={`frame-${legX}`}>
              <mesh position={[legX, 0, 0.25]} renderOrder={renderOrder}>
                <boxGeometry args={[0.075, 0.42, 0.5]} />
                <meshStandardMaterial color="#343b3c" metalness={0.54} roughness={0.48} />
              </mesh>
              <mesh position={[legX, -0.28, 0.72]} renderOrder={renderOrder}>
                <boxGeometry args={[0.075, 0.075, 0.56]} />
                <meshStandardMaterial color="#343b3c" metalness={0.54} roughness={0.48} />
              </mesh>
              <mesh position={[legX, -0.08, 0.68]} renderOrder={renderOrder}>
                <boxGeometry args={[0.075, 0.46, 0.075]} />
                <meshStandardMaterial color="#343b3c" metalness={0.54} roughness={0.48} />
              </mesh>
            </group>
          ))}
        </group>
      ))}
    </>
  );
}
