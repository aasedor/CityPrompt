import { useMemo } from 'react';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import type { ReferenceLayer } from './api';
import { referenceGeometryPaths } from './referenceGeometry';
import { closedRing, studyMetadata, studyZones, studyZoneName } from './zoningStudy';
import { zoningAnchor, type ZoningOverlay } from './zoningLabels';
import { GlobeZoningLabels } from './GlobeZoningLabels';

import { GlobeTransportVectors } from '../policyPlans/GlobeTransportVectors';
import type { TransportSnapshot } from '../policyPlans/transportVectors';

/** Imported vector outlines follow geographic ground; authored zoning studies retain their map presentation. */
export function GlobeReferenceLayer({ layers, terrainHeight }: { layers: ReferenceLayer[]; terrainHeight: number }) {
  return <group name="reference-overlays" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    {layers.map((layer) => studyMetadata(layer)
      ? <StudyOverlay key={layer.id} layer={layer} terrainHeight={terrainHeight} />
      : <ReferenceOutline key={layer.id} layer={layer} />)}
  </group>;
}

function StudyOverlay({ layer, terrainHeight }: { layer: ReferenceLayer; terrainHeight: number }) {
  const data = useMemo<ZoningOverlay>(() => ({ bounds: layer.bounds, loadedAt: layer.created_at,
    districts: studyZones(layer).flatMap(zone => {
      const anchor = zoningAnchor(zone.rings);
      return anchor ? [{ id: zone.id, label: studyZoneName(zone), anchor, polygon: zone.rings, color: zone.color }] : [];
    }),
  }), [layer.bounds, layer.created_at, layer.feature_collection]);
  const boundary = useMemo<ZoningOverlay>(() => {
    const points = studyMetadata(layer)?.boundaryCoordinates ?? [];
    return { bounds: layer.bounds, loadedAt: layer.created_at, districts: points.length < 3 ? [] : [
      { id: 'study-site-boundary', label: '', anchor: points[0], polygon: [closedRing(points)] },
    ] };
  }, [layer.bounds, layer.created_at, layer.feature_collection]);
  return <group name={`study-layer:${layer.id}`}>
    <GlobeZoningLabels data={data} terrainHeight={terrainHeight} enabled labels lines fill fillOpacity={layer.opacity} />
    <GlobeZoningLabels data={boundary} terrainHeight={terrainHeight} enabled labels={false} lines fill={false} fillOpacity={0} />
  </group>;
}

function ReferenceOutline({ layer }: { layer: ReferenceLayer }) {
  const data = useMemo<TransportSnapshot>(() => {
    const features: TransportSnapshot['features'] = [];
    for (const [index, feature] of layer.feature_collection.features.entries()) {
      const paths = referenceGeometryPaths(feature.geometry);
      const properties = { category: 'existing-pathway' as const, source: layer.source_filename };
      paths.lines.forEach((line, i) => features.push({ type: 'Feature', id: `${index}:line:${i}`, properties,
        geometry: { type: 'LineString', coordinates: line } }));
      paths.points.forEach((point, i) => features.push({ type: 'Feature', id: `${index}:point:${i}`,
        properties: { ...properties, category: 'service-stop' }, geometry: { type: 'Point', coordinates: point } }));
    }
    return { type: 'FeatureCollection', network: '5a', retrieved: layer.created_at, sources: {}, featureCount: features.length, features };
  }, [layer.feature_collection, layer.created_at, layer.source_filename]);
  return <GlobeTransportVectors data={data} mapId={`reference:${layer.id}`} opacity={layer.opacity} color={layer.color} order={990} />;
}
