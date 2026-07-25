import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';

import { PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { StreetParkedVehiclePlacement } from './streetFamilyFurniture';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

export interface StreetVehicleInstanceTransform {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scaleX: number;
  scaleY: number;
  scaleZ: number;
  color: string;
}

export interface StreetVehicleInstanceParts {
  bodies: StreetVehicleInstanceTransform[];
  cabins: StreetVehicleInstanceTransform[];
  roofs: StreetVehicleInstanceTransform[];
  wheels: StreetVehicleInstanceTransform[];
}

function localPartTransform(
  placement: StreetParkedVehiclePlacement,
  localX: number,
  localY: number,
  z: number,
  scaleX: number,
  scaleY: number,
  scaleZ: number,
  color: string,
): StreetVehicleInstanceTransform {
  const cos = Math.cos(placement.yawRad);
  const sin = Math.sin(placement.yawRad);
  return {
    x: placement.x + localX * cos - localY * sin,
    y: placement.y + localX * sin + localY * cos,
    z,
    yawRad: placement.yawRad,
    scaleX,
    scaleY,
    scaleZ,
    color,
  };
}

/** Converts semantic vehicle placements into four bounded instanced parts.
 * Geometry stays intentionally low-poly at globe scale, while the distinct
 * body, glazing, roof and wheel silhouettes read as parked cars rather than
 * anonymous blocks. */
export function buildStreetVehicleInstanceParts(
  placements: readonly StreetParkedVehiclePlacement[],
): StreetVehicleInstanceParts {
  const parts: StreetVehicleInstanceParts = {
    bodies: [],
    cabins: [],
    roofs: [],
    wheels: [],
  };
  placements.forEach((placement) => {
    const isSuv = placement.vehicleType === 'suv';
    const roadZ = placement.z + PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS;
    const wheelRadiusM = Math.min(0.34, placement.widthM * 0.21);
    const wheelThicknessM = Math.min(0.18, placement.widthM * 0.12);
    const bodyHeightM = placement.heightM * (isSuv ? 0.34 : 0.32);
    const bodyBottomZ = roadZ + wheelRadiusM * 0.55;
    const bodyTopZ = bodyBottomZ + bodyHeightM;
    const cabinHeightM = placement.heightM * (isSuv ? 0.49 : 0.46);
    const cabinLengthM = placement.lengthM * (isSuv ? 0.58 : 0.5);
    const roofHeightM = isSuv ? 0.09 : 0.07;

    parts.bodies.push(localPartTransform(
      placement,
      0,
      0,
      bodyBottomZ + bodyHeightM / 2,
      placement.lengthM * 0.96,
      placement.widthM,
      bodyHeightM,
      placement.bodyColor,
    ));
    parts.cabins.push(localPartTransform(
      placement,
      placement.lengthM * (isSuv ? -0.015 : -0.035),
      0,
      bodyTopZ + cabinHeightM / 2,
      cabinLengthM,
      placement.widthM * 0.84,
      cabinHeightM,
      '#26323a',
    ));
    parts.roofs.push(localPartTransform(
      placement,
      placement.lengthM * (isSuv ? -0.015 : -0.035),
      0,
      bodyTopZ + cabinHeightM + roofHeightM / 2,
      cabinLengthM * (isSuv ? 0.88 : 0.78),
      placement.widthM * 0.8,
      roofHeightM,
      placement.bodyColor,
    ));

    const wheelX = placement.lengthM * (isSuv ? 0.31 : 0.3);
    const wheelY = Math.max(0, placement.widthM / 2 - wheelThicknessM / 2);
    [-wheelX, wheelX].forEach((localX) => {
      [-wheelY, wheelY].forEach((localY) => {
        parts.wheels.push(localPartTransform(
          placement,
          localX,
          localY,
          roadZ + wheelRadiusM,
          wheelRadiusM,
          wheelThicknessM,
          wheelRadiusM,
          '#202427',
        ));
      });
    });
  });
  return parts;
}

function VehicleInstancedPart({
  geometry,
  transforms,
  renderOrder,
  metalness,
  roughness,
}: {
  geometry: THREE.BufferGeometry;
  transforms: StreetVehicleInstanceTransform[];
  renderOrder: number;
  metalness: number;
  roughness: number;
}) {
  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    if (!ref.current) return;
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const color = new THREE.Color();
    const zAxis = new THREE.Vector3(0, 0, 1);
    transforms.forEach((transform, index) => {
      position.set(transform.x, transform.y, transform.z);
      rotation.setFromAxisAngle(zAxis, transform.yawRad);
      scale.set(transform.scaleX, transform.scaleY, transform.scaleZ);
      matrix.compose(position, rotation, scale);
      ref.current?.setMatrixAt(index, matrix);
      ref.current?.setColorAt(index, color.set(transform.color));
    });
    ref.current.count = transforms.length;
    ref.current.instanceMatrix.needsUpdate = true;
    if (ref.current.instanceColor) ref.current.instanceColor.needsUpdate = true;
    ref.current.computeBoundingSphere();
  }, [transforms]);

  if (transforms.length === 0) return null;
  return (
    <instancedMesh
      ref={ref}
      args={[geometry, undefined, transforms.length]}
      renderOrder={renderOrder}
      frustumCulled
    >
      <meshStandardMaterial color="#ffffff" metalness={metalness} roughness={roughness} />
    </instancedMesh>
  );
}

interface GlobeStreetVehicleInstancesProps {
  placements: StreetParkedVehiclePlacement[];
  renderOrder?: number;
}

function StreetVehicleInstancesContent({
  placements,
  renderOrder = 148,
}: GlobeStreetVehicleInstancesProps) {
  const boxGeometry = useMemo(() => new THREE.BoxGeometry(1, 1, 1), []);
  const wheelGeometry = useMemo(() => new THREE.CylinderGeometry(1, 1, 1, 14), []);
  useEffect(() => {
    const releaseBox = retainResourceForDeferredDisposal(
      boxGeometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    );
    const releaseWheel = retainResourceForDeferredDisposal(
      wheelGeometry,
      (ownedGeometry) => ownedGeometry.dispose(),
    );
    return () => {
      releaseBox();
      releaseWheel();
    };
  }, [boxGeometry, wheelGeometry]);
  const parts = useMemo(() => buildStreetVehicleInstanceParts(placements), [placements]);

  return (
    <>
      <VehicleInstancedPart geometry={boxGeometry} transforms={parts.bodies} renderOrder={renderOrder} metalness={0.3} roughness={0.42} />
      <VehicleInstancedPart geometry={boxGeometry} transforms={parts.cabins} renderOrder={renderOrder + 1} metalness={0.12} roughness={0.24} />
      <VehicleInstancedPart geometry={boxGeometry} transforms={parts.roofs} renderOrder={renderOrder + 1} metalness={0.28} roughness={0.4} />
      <VehicleInstancedPart geometry={wheelGeometry} transforms={parts.wheels} renderOrder={renderOrder} metalness={0.05} roughness={0.84} />
    </>
  );
}

/** Keep the hook/resource-owning subtree unmounted when there is no work.
 * This also preserves normal cleanup when a populated batch becomes empty. */
export function GlobeStreetVehicleInstances(
  props: GlobeStreetVehicleInstancesProps,
) {
  if (props.placements.length === 0) return null;
  return <StreetVehicleInstancesContent {...props} />;
}
