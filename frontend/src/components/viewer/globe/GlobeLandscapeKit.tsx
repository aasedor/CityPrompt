import { useEffect, useMemo, useRef, type RefObject } from 'react';
import { useThree } from '@react-three/fiber';
import { useLandscapeTreeTextures } from './useLandscapeTreeTextures';
import * as THREE from 'three';

import {
  LANDSCAPE_TREE_PROFILES,
  LANDSCAPE_TREE_VARIANTS,
  selectLandscapeTreeVariant,
  type LandscapeTreeProfile,
  type LandscapeTreeCanopyClass,
  type LandscapeTreeVariant,
} from './landscapeKitProfiles';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

export interface LandscapeTreePlacement {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scale: number;
  /** Optional archetype-owned silhouette constraint. */
  canopyClass?: LandscapeTreeCanopyClass;
  /** Optional explicit catalog selection supplied by an appearance family. */
  treeVariant?: LandscapeTreeVariant;
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

  useEffect(() => {
    const releaseTrunk = retainResourceForDeferredDisposal(
      trunkGeometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    );
    const releasePlane = retainResourceForDeferredDisposal(
      planeGeometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    );
    return () => {
      releaseTrunk();
      releasePlane();
    };
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

const PALM_FRONDS_PER_TREE = 10;
const PALM_TRUNK_RINGS_PER_TREE = 4;

/** Palms use a dedicated radial crown instead of stretching a deciduous
 * billboard. The existing foliage atlas supplies leaf-scale alpha, while a
 * curved procedural strip produces the long, drooping frond silhouette. */
function PalmTreeVariantInstances({
  placements,
  profile,
  texture,
  renderOrder,
}: TreeVariantInstancesProps) {
  const trunkRef = useRef<THREE.InstancedMesh>(null);
  const trunkRingRef = useRef<THREE.InstancedMesh>(null);
  const frondRef = useRef<THREE.InstancedMesh>(null);
  const crownHeartRef = useRef<THREE.InstancedMesh>(null);
  const trunkGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(0.72, 1.34, 1, 12);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const trunkRingGeometry = useMemo(
    () => new THREE.TorusGeometry(1, 0.075, 5, 12),
    [],
  );
  const frondGeometry = useMemo(() => {
    const geometry = new THREE.PlaneGeometry(1, 1, 5, 1);
    const positions = geometry.getAttribute('position');
    for (let index = 0; index < positions.count; index += 1) {
      const outward = positions.getX(index) + 0.5;
      const lateral = positions.getY(index);
      const droop = -0.22 * outward ** 1.65 - Math.abs(lateral) * 0.035;
      positions.setXYZ(index, outward, lateral, droop);
    }
    positions.needsUpdate = true;
    geometry.computeVertexNormals();
    geometry.computeBoundingSphere();
    return geometry;
  }, []);
  const crownHeartGeometry = useMemo(() => new THREE.SphereGeometry(1, 10, 7), []);

  useEffect(() => {
    const releases = [
      trunkGeometry,
      trunkRingGeometry,
      frondGeometry,
      crownHeartGeometry,
    ].map((geometry) => retainResourceForDeferredDisposal(
      geometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    ));
    return () => releases.forEach((release) => release());
  }, [crownHeartGeometry, frondGeometry, trunkGeometry, trunkRingGeometry]);

  useEffect(() => {
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const yawQuaternion = new THREE.Quaternion();
    const tiltQuaternion = new THREE.Quaternion();
    const frondQuaternion = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    const yAxis = new THREE.Vector3(0, 1, 0);

    placements.forEach((placement, placementIndex) => {
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
      trunkRef.current?.setMatrixAt(placementIndex, matrix);

      for (let ring = 0; ring < PALM_TRUNK_RINGS_PER_TREE; ring += 1) {
        const ringIndex = placementIndex * PALM_TRUNK_RINGS_PER_TREE + ring;
        const station = (ring + 1) / (PALM_TRUNK_RINGS_PER_TREE + 1);
        position.set(
          placement.x,
          placement.y,
          placement.z + profile.trunkHeightM * treeScale * station,
        );
        const ringRadius = profile.trunkRadiusM * treeScale * (1.18 - station * 0.18);
        scale.set(ringRadius, ringRadius, ringRadius);
        matrix.compose(position, yawQuaternion, scale);
        trunkRingRef.current?.setMatrixAt(ringIndex, matrix);
      }

      const crownBaseZ = placement.z + profile.trunkHeightM * treeScale * 0.985;
      position.set(placement.x, placement.y, crownBaseZ);
      scale.set(
        profile.trunkRadiusM * 2.2 * treeScale,
        profile.trunkRadiusM * 2.2 * treeScale,
        profile.crownHeightM * 0.18 * treeScale,
      );
      matrix.compose(position, yawQuaternion, scale);
      crownHeartRef.current?.setMatrixAt(placementIndex, matrix);

      for (let frond = 0; frond < PALM_FRONDS_PER_TREE; frond += 1) {
        const frondIndex = placementIndex * PALM_FRONDS_PER_TREE + frond;
        const angle = placement.yawRad
          + frond * Math.PI * 2 / PALM_FRONDS_PER_TREE
          + ((placementIndex + frond) % 3 - 1) * 0.035;
        yawQuaternion.setFromAxisAngle(zAxis, angle);
        tiltQuaternion.setFromAxisAngle(yAxis, frond % 2 === 0 ? -0.08 : 0.035);
        frondQuaternion.multiplyQuaternions(yawQuaternion, tiltQuaternion);
        position.set(
          placement.x,
          placement.y,
          crownBaseZ + profile.crownHeightM * treeScale * (frond % 2 === 0 ? 0.14 : 0.04),
        );
        scale.set(
          profile.crownWidthM * 0.54 * treeScale,
          profile.crownDepthM * 0.115 * treeScale,
          profile.crownHeightM * treeScale,
        );
        matrix.compose(position, frondQuaternion, scale);
        frondRef.current?.setMatrixAt(frondIndex, matrix);
      }
    });

    const instanceGroups: Array<[RefObject<THREE.InstancedMesh>, number]> = [
      [trunkRef, placements.length],
      [trunkRingRef, placements.length * PALM_TRUNK_RINGS_PER_TREE],
      [frondRef, placements.length * PALM_FRONDS_PER_TREE],
      [crownHeartRef, placements.length],
    ];
    for (const [ref, count] of instanceGroups) {
      if (!ref.current) continue;
      ref.current.count = count;
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
        <meshStandardMaterial color={profile.barkColor} roughness={0.97} />
      </instancedMesh>
      <instancedMesh
        ref={trunkRingRef}
        args={[
          trunkRingGeometry,
          undefined,
          placements.length * PALM_TRUNK_RINGS_PER_TREE,
        ]}
        renderOrder={renderOrder + 1}
        frustumCulled={false}
      >
        <meshStandardMaterial color="#6f5138" roughness={0.99} />
      </instancedMesh>
      <instancedMesh
        ref={frondRef}
        args={[frondGeometry, undefined, placements.length * PALM_FRONDS_PER_TREE]}
        renderOrder={renderOrder + 2}
        frustumCulled={false}
      >
        <meshStandardMaterial
          map={texture}
          color={profile.foliageTint}
          alphaTest={0.22}
          side={THREE.DoubleSide}
          roughness={0.97}
          metalness={0}
        />
      </instancedMesh>
      <instancedMesh
        ref={crownHeartRef}
        args={[crownHeartGeometry, undefined, placements.length]}
        renderOrder={renderOrder + 1}
        frustumCulled={false}
      >
        <meshStandardMaterial color="#486837" roughness={0.98} />
      </instancedMesh>
    </>
  );
}

interface GlobeLandscapeTreeStandProps {
  placements: LandscapeTreePlacement[];
  renderOrder?: number;
}

function LandscapeTreeStandContent({
  placements,
  renderOrder = 145,
}: GlobeLandscapeTreeStandProps) {
  const { gl } = useThree();
  const textures = useLandscapeTreeTextures();
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
      mature_oak: [],
      ornamental_pear: [],
      columnar_hornbeam: [],
      pollarded_plane: [],
      tropical_palm: [],
    };
    placements.forEach((placement, index) => {
      groups[placement.treeVariant ?? selectLandscapeTreeVariant(placement, index)].push(placement);
    });
    return groups;
  }, [placements]);

  return (
    <>
      {LANDSCAPE_TREE_VARIANTS.map((variant, index) => {
        const variantPlacements = grouped[variant];
        if (variantPlacements.length === 0) return null;
        return LANDSCAPE_TREE_PROFILES[variant].crownGeometry === 'radial_palm_fronds'
          ? (
            <PalmTreeVariantInstances
              key={variant}
              placements={variantPlacements}
              profile={LANDSCAPE_TREE_PROFILES[variant]}
              texture={textures[index]}
              renderOrder={renderOrder}
            />
          )
          : (
            <TreeVariantInstances
              key={variant}
              placements={variantPlacements}
              profile={LANDSCAPE_TREE_PROFILES[variant]}
              texture={textures[index]}
              renderOrder={renderOrder}
            />
          );
      })}
    </>
  );
}

/** Do not load textures or allocate per-variant geometry for an empty stand. */
export function GlobeLandscapeTreeStand(props: GlobeLandscapeTreeStandProps) {
  if (props.placements.length === 0) return null;
  return <LandscapeTreeStandContent {...props} />;
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

  useEffect(
    () => retainResourceForDeferredDisposal(
      boxGeometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    ),
    [boxGeometry],
  );
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
