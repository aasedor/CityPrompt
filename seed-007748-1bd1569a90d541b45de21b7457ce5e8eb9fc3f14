import { useEffect, useMemo, useRef, type RefObject } from 'react';
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
  const woodRef = useRef<THREE.InstancedMesh>(null);
  const metalRef = useRef<THREE.InstancedMesh>(null);
  const boxGeometry = useMemo(() => new THREE.BoxGeometry(1, 1, 1), []);
  const woodPartCount = placements.length * 8;
  const metalPartCount = placements.length * 6;

  useEffect(() => () => boxGeometry.dispose(), [boxGeometry]);
  useEffect(() => {
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const yaw = new THREE.Quaternion();
    const localRotation = new THREE.Quaternion();
    const rotation = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    const xAxis = new THREE.Vector3(1, 0, 0);
    let woodIndex = 0;
    let metalIndex = 0;
    const setPart = (
      ref: RefObject<THREE.InstancedMesh | null>,
      index: number,
      placement: LandscapeBenchPlacement,
      localX: number,
      localY: number,
      localZ: number,
      width: number,
      depth: number,
      height: number,
      tiltX = 0,
    ) => {
      const cos = Math.cos(placement.yawRad);
      const sin = Math.sin(placement.yawRad);
      position.set(
        placement.x + (localX * cos - localY * sin) * placement.scale,
        placement.y + (localX * sin + localY * cos) * placement.scale,
        placement.z + localZ * placement.scale,
      );
      yaw.setFromAxisAngle(zAxis, placement.yawRad);
      localRotation.setFromAxisAngle(xAxis, tiltX);
      rotation.multiplyQuaternions(yaw, localRotation);
      scale.set(width * placement.scale, depth * placement.scale, height * placement.scale);
      matrix.compose(position, rotation, scale);
      ref.current?.setMatrixAt(index, matrix);
    };

    placements.forEach((placement) => {
      [-0.20, -0.10, 0, 0.10, 0.20].forEach((slatY) => {
        setPart(woodRef, woodIndex++, placement, 0, slatY, 0.48, 1.86, 0.074, 0.055);
      });
      [0.68, 0.81, 0.94].forEach((slatZ) => {
        setPart(woodRef, woodIndex++, placement, 0, 0.255, slatZ, 1.86, 0.055, 0.075, Math.PI / 18);
      });
      [-0.68, 0.68].forEach((legX) => {
        setPart(metalRef, metalIndex++, placement, legX, 0, 0.25, 0.075, 0.42, 0.5);
        setPart(metalRef, metalIndex++, placement, legX, -0.28, 0.72, 0.075, 0.075, 0.56);
        setPart(metalRef, metalIndex++, placement, legX, -0.08, 0.68, 0.075, 0.46, 0.075);
      });
    });
    if (woodRef.current) {
      woodRef.current.count = woodPartCount;
      woodRef.current.instanceMatrix.needsUpdate = true;
      woodRef.current.computeBoundingSphere();
    }
    if (metalRef.current) {
      metalRef.current.count = metalPartCount;
      metalRef.current.instanceMatrix.needsUpdate = true;
      metalRef.current.computeBoundingSphere();
    }
  }, [metalPartCount, placements, woodPartCount]);

  if (placements.length === 0) return null;
  return (
    <>
      <instancedMesh
        ref={woodRef}
        args={[boxGeometry, undefined, woodPartCount]}
        renderOrder={renderOrder}
        frustumCulled={false}
      >
        <meshStandardMaterial color="#835638" roughness={0.83} />
      </instancedMesh>
      <instancedMesh
        ref={metalRef}
        args={[boxGeometry, undefined, metalPartCount]}
        renderOrder={renderOrder}
        frustumCulled={false}
      >
        <meshStandardMaterial color="#343b3c" metalness={0.54} roughness={0.48} />
      </instancedMesh>
    </>
  );
}
