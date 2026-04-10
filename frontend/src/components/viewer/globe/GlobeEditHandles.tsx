/**
 * GlobeEditHandles.tsx — Vertex and rotation handles for zone editing.
 *
 * Renders white spheres at each vertex of the selected zone,
 * and an amber rotation handle extending from the centroid.
 */

import { useMemo } from 'react';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { computeCentroid, computeRotationHandlePos, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

interface GlobeEditHandlesProps {
  zone: SiteZone;
  onVertexDragStart: (index: number) => void;
  onZoneDragStart?: (zoneId: string, startLngLat: [number, number]) => void;
}

export function GlobeEditHandles({ zone, onVertexDragStart, onZoneDragStart: _onZoneDragStart }: GlobeEditHandlesProps) {
  const centroid = useMemo(() => computeCentroid(zone.coordinates), [zone.coordinates]);
  const rotationHandlePos = useMemo(() => computeRotationHandlePos(zone.coordinates), [zone.coordinates]);

  // Rotation line from centroid to handle in local coords
  const rotationLinePositions = useMemo(() => {
    const [cLng, cLat] = centroid;
    const [hLng, hLat] = rotationHandlePos;
    const mLon = metersPerDegLon(cLat);
    return new Float32Array([
      0, 0, 2,
      (hLng - cLng) * mLon, (hLat - cLat) * METERS_PER_DEG_LAT, 2,
    ]);
  }, [centroid, rotationHandlePos]);

  return (
    <>
      {/* Vertex handles */}
      {zone.coordinates.map((coord, i) => (
        <EastNorthUpFrame
          key={`vh-${i}`}
          lat={coord[1] * DEG_TO_RAD}
          lon={coord[0] * DEG_TO_RAD}
          height={1}
        >
          <mesh
            onPointerDown={(e) => {
              e.stopPropagation();
              onVertexDragStart(i);
            }}
          >
            <sphereGeometry args={[4, 8, 8]} />
            <meshBasicMaterial color="#ffffff" depthWrite={false} />
          </mesh>
        </EastNorthUpFrame>
      ))}

      {/* Rotation handle and line */}
      <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={0}>
        {/* Rotation line */}
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              array={rotationLinePositions}
              count={2}
              itemSize={3}
            />
          </bufferGeometry>
          <lineDashedMaterial color="#f59e0b" dashSize={5} gapSize={3} depthWrite={false} />
        </line>
      </EastNorthUpFrame>

      {/* Rotation handle sphere */}
      <EastNorthUpFrame
        lat={rotationHandlePos[1] * DEG_TO_RAD}
        lon={rotationHandlePos[0] * DEG_TO_RAD}
        height={2}
      >
        <mesh>
          <sphereGeometry args={[5, 8, 8]} />
          <meshBasicMaterial color="#f59e0b" depthWrite={false} />
        </mesh>
      </EastNorthUpFrame>
    </>
  );
}
