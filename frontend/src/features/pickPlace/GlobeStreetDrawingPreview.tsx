import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Matrix4 } from 'three';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { GlobeStreetDraft } from '@/components/viewer/globe/GlobeStreetDetailLayer';
import { getRepresentativeTerrainHeight } from '@/components/viewer/globe/globeTerrainUtils';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { streetDrawingGeometry, streetPreviewPoints } from './streetDrawingGeometry';
import type { PublicRoadContext } from './publicRoadSuggestions';
import { PublicRoadSuggestionMarker } from './PublicRoadSuggestionMarker';
import { resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';

type Surface = { lngLat: [number, number]; height: number };
/** Cursor updates stay inside this small subtree instead of rerendering the globe. */
export function GlobeStreetDrawingPreview({ points, pointHeights, properties, zones, terrainHeight, raycastSurface, publicRoads, skipSnapping = false }: {
  points: number[][]; pointHeights: number[]; properties: SiteZoneProperties | null;
  zones: SiteZone[]; terrainHeight: number; raycastSurface: (x: number, y: number) => Surface | null;
  publicRoads?: PublicRoadContext; skipSnapping?: boolean;
}) {
  const { gl, camera, invalidate } = useThree();
  const pointer = useRef<[number, number] | null>(null);
  const dirty = useRef(false), last = useRef(0), matrix = useRef(new Matrix4());
  const [surface, setSurface] = useState<Surface | null>(null);
  // Texture/material resources depend on the selected street, never on pointer position.
  const profile = useMemo(() => resolvePilotStreetSectionProfile({ properties: properties ?? {} }), [properties]);
  useEffect(() => { setSurface(null); dirty.current = false; }, [points]);
  useEffect(() => {
    const move = (event: PointerEvent) => {
      const rect = gl.domElement.getBoundingClientRect();
      pointer.current = rect.width < 640 ? [0, 0]
        : [(event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1];
      dirty.current = true; invalidate();
    };
    const leave = () => { pointer.current = null; dirty.current = false; setSurface(null); };
    gl.domElement.addEventListener('pointermove', move);
    gl.domElement.addEventListener('pointerleave', leave);
    return () => {
      gl.domElement.removeEventListener('pointermove', move);
      gl.domElement.removeEventListener('pointerleave', leave);
    };
  }, [gl, invalidate]);
  useFrame(({ clock }) => {
    if (!points.length || !pointer.current || clock.elapsedTime - last.current < .12
      || (!dirty.current && matrix.current.equals(camera.matrixWorld))) return;
    last.current = clock.elapsedTime; dirty.current = false; matrix.current.copy(camera.matrixWorld);
    setSurface(raycastSurface(...pointer.current));
  });
  const height = getRepresentativeTerrainHeight(pointHeights, terrainHeight);
  const zone = useMemo(() => {
    const route = streetPreviewPoints(points, surface?.lngLat ?? null);
    if (route.length < 2) return null;
    const geometry = streetDrawingGeometry(route, { ...ZONE_TYPE_CONFIG.road.defaultProperties,
      ...properties, terrain_elevation_m: height }, zones, { publicRoads, skipSnapping });
    return { id: 'street-drawing-preview', project_id: zones[0]?.project_id ?? '', zone_type: 'road',
      color: '#c9ff3d', sort_order: 0, created_at: '', updated_at: '', ...geometry } satisfies SiteZone;
  }, [points, surface, properties, zones, height, publicRoads, skipSnapping]);
  return zone ? <group name="street-drawing-preview" userData={{ editorPreview: true }}>
    <GlobeStreetDraft zone={zone} zones={zones} terrainHeight={height} profile={profile} />
    {zone.suggestion && <PublicRoadSuggestionMarker suggestion={zone.suggestion}
      height={resolvePreparedSiteTerrainForZone(getActiveSiteBoundary(zones) ?? zone, zones, height) ?? height} />}
  </group> : null;
}
