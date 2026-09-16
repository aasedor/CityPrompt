import { useEffect, useMemo } from 'react';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { BufferGeometry, Float32BufferAttribute, DoubleSide } from 'three';
import { useSharedSiteGround } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

/** The exact shared SW–NE triangles; debug surface never supplies another height. */
export function SurveyGroundSurface({ visible }: { visible: boolean }) {
  const ground = useSharedSiteGround();
  const snapshot = ground.snapshot?.source === 'classified_lidar' ? ground.snapshot : null;
  const surface = useMemo(() => {
    if (!snapshot) return null;
    const g = snapshot.grid, lng = g.west + (g.columns - 1) * g.stepLng / 2;
    const lat = g.south + (g.rows - 1) * g.stepLat / 2, height = snapshot.heights[0];
    const positions: number[] = [], indices: number[] = [];
    for (let y = 0; y < g.rows; y++) for (let x = 0; x < g.columns; x++) {
      positions.push((g.west + x * g.stepLng - lng) * metersPerDegLon(lat),
        (g.south + y * g.stepLat - lat) * METERS_PER_DEG_LAT, snapshot.heights[y * g.columns + x] - height);
      if (x < g.columns - 1 && y < g.rows - 1) {
        const sw = y * g.columns + x, se = sw + 1, nw = sw + g.columns, ne = nw + 1;
        indices.push(sw, se, ne, sw, ne, nw);
      }
    }
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new Float32BufferAttribute(positions, 3)); geometry.setIndex(indices); geometry.computeVertexNormals();
    return { geometry, lng, lat, height };
  }, [snapshot]);
  useEffect(() => surface ? retainResourceForDeferredDisposal(surface.geometry, geometry => geometry.dispose()) : undefined, [surface]);
  if (!surface || !visible) return null;
  return <EastNorthUpFrame lat={surface.lat * Math.PI / 180} lon={surface.lng * Math.PI / 180} height={surface.height}>
    <mesh name="survey-ground-debug" geometry={surface.geometry} userData={{ sceneRole: 'existing', contextProvider: 'survey-ground' }}>
      <meshStandardMaterial color="#8eaa69" roughness={1} side={DoubleSide} />
    </mesh>
  </EastNorthUpFrame>;
}
