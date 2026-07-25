/**
 * GlobeMassingPreview.tsx — Renders AI-generated massing blocks on the globe.
 *
 * Takes GeoJSON features (from the AI massing API) and renders them
 * as extruded 3D blocks on the globe surface, same as the Mapbox
 * massing-preview-extrusion layer.
 */

import { useMemo } from 'react';
import * as THREE from 'three';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

interface MassingFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  properties: {
    type?: string;
    color?: string;
    height?: number;
  };
}

interface GlobeMassingPreviewProps {
  features: MassingFeature[];
}

function MassingBlock({ feature }: { feature: MassingFeature }) {
  const coords = feature.geometry.coordinates[0]; // First ring of polygon
  if (!coords || coords.length < 3) return null;

  const lngLatCoords = coords.map(c => [c[0], c[1]] as number[]);
  const centroid = computeCentroid(lngLatCoords);
  const color = feature.properties.color || '#888888';
  const height = feature.properties.height || 10;
  const isBuilding = feature.properties.type === 'building';

  const geometry = useMemo(() => {
    const [cLng, cLat] = centroid;
    const mLon = metersPerDegLon(cLat);

    const localPts = lngLatCoords.map(c =>
      new THREE.Vector2(
        (c[0] - cLng) * mLon,
        (c[1] - cLat) * METERS_PER_DEG_LAT,
      )
    );

    const shape = new THREE.Shape();
    shape.moveTo(localPts[0].x, localPts[0].y);
    for (let i = 1; i < localPts.length; i++) {
      shape.lineTo(localPts[i].x, localPts[i].y);
    }
    shape.closePath();

    if (isBuilding && height > 0) {
      return new THREE.ExtrudeGeometry(shape, {
        depth: height,
        bevelEnabled: false,
      });
    }
    return new THREE.ShapeGeometry(shape);
  }, [lngLatCoords, centroid, height, isBuilding]);

  return (
    <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={0}>
      <mesh geometry={geometry} position={[0, 0, isBuilding ? 0 : 0.3]}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.85}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>
    </EastNorthUpFrame>
  );
}

export function GlobeMassingPreview({ features }: GlobeMassingPreviewProps) {
  if (!features || features.length === 0) return null;

  return (
    <>
      {features.map((f, i) => (
        <MassingBlock key={`massing-${i}`} feature={f} />
      ))}
    </>
  );
}
