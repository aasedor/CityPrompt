import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';

import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { STREET_TRANSIT_SHELTER_NOMINAL_DEPTH_M } from './streetFamilyFurniture';

/** World-space anchor for a main-street shelter. The heading follows the
 * street tangent; local X runs along the curb and local Y runs across it. */
export interface StreetTransitShelterPlacement {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scale: number;
}

export interface StreetTransitShelterInstanceTransform {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scaleX: number;
  scaleY: number;
  scaleZ: number;
}

export interface StreetTransitShelterInstanceParts {
  frames: StreetTransitShelterInstanceTransform[];
  glass: StreetTransitShelterInstanceTransform[];
  roofs: StreetTransitShelterInstanceTransform[];
  benches: StreetTransitShelterInstanceTransform[];
}

function localPartTransform(
  placement: StreetTransitShelterPlacement,
  localX: number,
  localY: number,
  localZ: number,
  widthM: number,
  depthM: number,
  heightM: number,
): StreetTransitShelterInstanceTransform {
  const scale = Math.max(0.1, placement.scale);
  const cos = Math.cos(placement.yawRad);
  const sin = Math.sin(placement.yawRad);
  const scaledX = localX * scale;
  const scaledY = localY * scale;
  return {
    x: placement.x + scaledX * cos - scaledY * sin,
    y: placement.y + scaledX * sin + scaledY * cos,
    z: placement.z + localZ * scale,
    yawRad: placement.yawRad,
    scaleX: widthM * scale,
    scaleY: depthM * scale,
    scaleZ: heightM * scale,
  };
}

/** Builds a readable contemporary shelter silhouette from a bounded number of
 * unit-box instances. Separating the materials keeps glazing transparent while
 * retaining low draw-call geometry for repeated main-street shelters. */
export function buildStreetTransitShelterInstanceParts(
  placements: readonly StreetTransitShelterPlacement[],
): StreetTransitShelterInstanceParts {
  const parts: StreetTransitShelterInstanceParts = {
    frames: [],
    glass: [],
    roofs: [],
    benches: [],
  };

  placements.forEach((placement) => {
    // Four corner posts plus continuous top rails make the shelter read even
    // when transparent panes blend into a distant globe view.
    [-1.95, 1.95].forEach((localX) => {
      [-0.68, 0.68].forEach((localY) => {
        parts.frames.push(localPartTransform(
          placement,
          localX,
          localY,
          1.25,
          0.09,
          0.09,
          2.5,
        ));
      });
      parts.frames.push(localPartTransform(
        placement,
        localX,
        0,
        2.48,
        0.09,
        1.45,
        0.09,
      ));
    });
    parts.frames.push(localPartTransform(
      placement,
      0,
      0.68,
      2.48,
      3.9,
      0.09,
      0.09,
    ));

    // The two-piece rear screen suggests a framed glass module; end panes
    // protect the bench while retaining clear sightlines into the shelter.
    [-0.98, 0.98].forEach((localX) => {
      parts.glass.push(localPartTransform(
        placement,
        localX,
        0.68,
        1.28,
        1.84,
        0.035,
        2.15,
      ));
    });
    [-1.95, 1.95].forEach((localX) => {
      parts.glass.push(localPartTransform(
        placement,
        localX,
        0,
        1.28,
        0.035,
        1.28,
        2.15,
      ));
    });

    parts.roofs.push(localPartTransform(
      placement,
      0,
      0,
      2.61,
      4.25,
      STREET_TRANSIT_SHELTER_NOMINAL_DEPTH_M,
      0.16,
    ));

    // A timber-toned seat, backrest and two supports remain visibly distinct
    // from the metal enclosure without introducing another geometry family.
    parts.benches.push(localPartTransform(
      placement,
      0,
      0.35,
      0.55,
      2.55,
      0.46,
      0.12,
    ));
    parts.benches.push(localPartTransform(
      placement,
      0,
      0.55,
      0.95,
      2.55,
      0.11,
      0.72,
    ));
    [-0.92, 0.92].forEach((localX) => {
      parts.benches.push(localPartTransform(
        placement,
        localX,
        0.35,
        0.27,
        0.1,
        0.35,
        0.54,
      ));
    });
  });

  return parts;
}

export interface StreetTransitShelterResources {
  geometry: THREE.BoxGeometry;
  frameMaterial: THREE.MeshStandardMaterial;
  glassMaterial: THREE.MeshPhysicalMaterial;
  roofMaterial: THREE.MeshStandardMaterial;
  benchMaterial: THREE.MeshStandardMaterial;
  dispose: () => void;
}

/** Creates one component-owned resource bundle with idempotent cleanup. */
export function createStreetTransitShelterResources(): StreetTransitShelterResources {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: '#303a40',
    metalness: 0.72,
    roughness: 0.34,
  });
  const glassMaterial = new THREE.MeshPhysicalMaterial({
    color: '#b9dbe2',
    metalness: 0,
    roughness: 0.08,
    transparent: true,
    opacity: 0.3,
    transmission: 0.68,
    thickness: 0.03,
    ior: 1.45,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const roofMaterial = new THREE.MeshStandardMaterial({
    color: '#445159',
    metalness: 0.58,
    roughness: 0.38,
  });
  const benchMaterial = new THREE.MeshStandardMaterial({
    color: '#9b6438',
    metalness: 0.04,
    roughness: 0.62,
  });
  let disposed = false;
  return {
    geometry,
    frameMaterial,
    glassMaterial,
    roofMaterial,
    benchMaterial,
    dispose: () => {
      if (disposed) return;
      disposed = true;
      geometry.dispose();
      frameMaterial.dispose();
      glassMaterial.dispose();
      roofMaterial.dispose();
      benchMaterial.dispose();
    },
  };
}

function TransitShelterInstancedPart({
  geometry,
  material,
  transforms,
  renderOrder,
}: {
  geometry: THREE.BufferGeometry;
  material: THREE.Material;
  transforms: readonly StreetTransitShelterInstanceTransform[];
  renderOrder: number;
}) {
  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    if (!ref.current) return;
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    transforms.forEach((transform, index) => {
      position.set(transform.x, transform.y, transform.z);
      rotation.setFromAxisAngle(zAxis, transform.yawRad);
      scale.set(transform.scaleX, transform.scaleY, transform.scaleZ);
      matrix.compose(position, rotation, scale);
      ref.current?.setMatrixAt(index, matrix);
    });
    ref.current.count = transforms.length;
    ref.current.instanceMatrix.needsUpdate = true;
    ref.current.computeBoundingSphere();
  }, [transforms]);

  if (transforms.length === 0) return null;
  return (
    <instancedMesh
      ref={ref}
      args={[geometry, material, transforms.length]}
      renderOrder={renderOrder}
      frustumCulled
    />
  );
}

interface GlobeStreetTransitShelterInstancesProps {
  placements: readonly StreetTransitShelterPlacement[];
  renderOrder?: number;
}

function StreetTransitShelterInstancesContent({
  placements,
  renderOrder = 149,
}: GlobeStreetTransitShelterInstancesProps) {
  const resources = useMemo(() => createStreetTransitShelterResources(), []);
  useEffect(
    () => retainResourceForDeferredDisposal(resources, (owned) => owned.dispose()),
    [resources],
  );
  const parts = useMemo(
    () => buildStreetTransitShelterInstanceParts(placements),
    [placements],
  );

  return (
    <group dispose={null}>
      <TransitShelterInstancedPart
        geometry={resources.geometry}
        material={resources.frameMaterial}
        transforms={parts.frames}
        renderOrder={renderOrder}
      />
      <TransitShelterInstancedPart
        geometry={resources.geometry}
        material={resources.glassMaterial}
        transforms={parts.glass}
        renderOrder={renderOrder + 2}
      />
      <TransitShelterInstancedPart
        geometry={resources.geometry}
        material={resources.roofMaterial}
        transforms={parts.roofs}
        renderOrder={renderOrder + 1}
      />
      <TransitShelterInstancedPart
        geometry={resources.geometry}
        material={resources.benchMaterial}
        transforms={parts.benches}
        renderOrder={renderOrder + 1}
      />
    </group>
  );
}

/** Avoid allocating the shared geometry/material set for an empty batch. */
export function GlobeStreetTransitShelterInstances(
  props: GlobeStreetTransitShelterInstancesProps,
) {
  if (props.placements.length === 0) return null;
  return <StreetTransitShelterInstancesContent {...props} />;
}
