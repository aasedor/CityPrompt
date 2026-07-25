/**
 * GlobeDrawingPreview.tsx — Visual feedback during polygon/line drawing.
 *
 * Shows vertex dots, edge lines, and fill preview on the 3D globe surface.
 */

import { useMemo } from 'react';
import * as THREE from 'three';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

interface GlobeDrawingPreviewProps {
  points: number[][];
  cursorPosition: [number, number] | null;
  color?: string;
  linear?: boolean;
}

export function GlobeDrawingPreview({
  points,
  cursorPosition,
  color = '#f59e0b',
  linear = false,
}: GlobeDrawingPreviewProps) {
  if (points.length === 0) return null;

  // All points including cursor for preview
  const allPoints = cursorPosition ? [...points, cursorPosition] : points;

  return (
    <>
      {/* Individual vertex dots */}
      {points.map((pt, i) => (
        <EastNorthUpFrame key={`dot-${i}`} lat={pt[1] * DEG_TO_RAD} lon={pt[0] * DEG_TO_RAD} height={1}>
          <mesh>
            <sphereGeometry args={[3, 8, 8]} />
            <meshBasicMaterial color={color} depthWrite={false} />
          </mesh>
        </EastNorthUpFrame>
      ))}

      {/* Edge lines + fill preview */}
      {allPoints.length >= 2 && (
        <DrawingShape points={allPoints} color={color} linear={linear} />
      )}
    </>
  );
}

function DrawingShape({ points, color, linear }: { points: number[][]; color: string; linear: boolean }) {
  const centroid = useMemo(() => computeCentroid(points), [points]);

  const { linePositions, fillGeometry } = useMemo(() => {
    const [cLng, cLat] = centroid;
    const mPerDegLon = metersPerDegLon(cLat);

    // Convert to local meters
    const localPts = points.map(p => ({
      x: (p[0] - cLng) * mPerDegLon,
      y: (p[1] - cLat) * METERS_PER_DEG_LAT,
    }));

    // Line positions (close the loop for polygons)
    const linePts = [...localPts];
    if (!linear && linePts.length >= 3) {
      linePts.push(linePts[0]); // Close polygon
    }
    const lineArray = new Float32Array(linePts.flatMap(p => [p.x, p.y, 1.5]));

    // Fill geometry for polygons with 3+ points
    let fillGeo: THREE.ShapeGeometry | null = null;
    if (!linear && localPts.length >= 3) {
      const shape = new THREE.Shape();
      shape.moveTo(localPts[0].x, localPts[0].y);
      for (let i = 1; i < localPts.length; i++) {
        shape.lineTo(localPts[i].x, localPts[i].y);
      }
      shape.closePath();
      fillGeo = new THREE.ShapeGeometry(shape);
    }

    return { linePositions: lineArray, fillGeometry: fillGeo };
  }, [points, centroid, linear]);

  return (
    <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={0}>
      {/* Edge lines */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            array={linePositions}
            count={linePositions.length / 3}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color={color} linewidth={2} depthWrite={false} />
      </line>

      {/* Fill preview */}
      {fillGeometry && (
        <mesh geometry={fillGeometry} position={[0, 0, 1]}>
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.2}
            side={THREE.DoubleSide}
            depthWrite={false}
          />
        </mesh>
      )}
    </EastNorthUpFrame>
  );
}
