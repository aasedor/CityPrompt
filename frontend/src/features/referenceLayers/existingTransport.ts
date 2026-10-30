import type { ReferenceLayer } from './api';

export const CALGARY_TRANSPORT_ROOT = 'https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services';
export const TRANSPORT_SOURCES = ['Street_Centreline', 'Pathways_close_view', 'Walkway_Sidewalk_Connections_view'] as const;
export interface ExistingTransportLine {
  id: string; label: string; kind: 'road' | 'path'; points: [number, number][]; widthM: number | null;
}
export interface ExistingTransport { lines: ExistingTransportLine[] }
export const EMPTY_TRANSPORT: ExistingTransport = { lines: [] };

/** Identify the retired one-click route imports, not unrelated City data or
 * student GIS layers. Their records remain for existing saved connections. */
export function isLegacyCalgaryTransportLayer(layer: ReferenceLayer): boolean {
  return layer.kind === 'reference' && layer.source_url === CALGARY_TRANSPORT_ROOT
    && (layer.source_filename === 'calgary-existing-transport.geojson'
      || layer.feature_collection.features.some(feature => TRANSPORT_SOURCES.some(source => source === feature.properties.cp_transport_source)));
}

/** Only the known City snapshot format is interpreted as transport. Generic
 * GIS imports retain their existing reference-only behaviour. Z is deliberately
 * ignored: these layers do not establish the proposal's terrain datum. */
export function existingTransport(layers: readonly ReferenceLayer[]): ExistingTransport {
  const lines: ExistingTransportLine[] = [], seen = new Set<string>();
  for (const layer of [...layers].sort((a,b)=>a.id.localeCompare(b.id))) {
    if (layer.source_url !== CALGARY_TRANSPORT_ROOT) continue;
    for (const feature of layer.feature_collection.features) {
      const p = feature.properties, source = String(p.cp_transport_source ?? '');
      if (!TRANSPORT_SOURCES.some(value=>value===source)) continue;
      const kind = source === 'Street_Centreline' ? 'road' : 'path';
      const state = String(kind === 'road' ? p.BUILT_STATUS : p.LIFE_CYCLE_STATUS).toUpperCase();
      if (kind === 'road' ? state !== 'BUILT' : !['ACTIVE','INSTALLED'].includes(state)) continue;
      if (kind === 'path' && String(p.OPERATIONAL).toUpperCase() !== 'OPEN') continue;
      if (kind === 'path' && /PRIVATE|BRIDGE|TUNNEL|STAIR/i.test([p.OWNERSHIP,p.ASSET_TYPE,p.PATH_NAME,p.USAGE_TYPE].join(' '))) continue;
      const sharedAccess=/ACCESS ROAD/i.test(String(p.ASSET_TYPE));
      if(kind==='path'&&sharedAccess&&!/MULTIUSE|PEDESTRIAN/i.test(String(p.USAGE_TYPE)))continue;
      const key = String(p.GLOBALID ?? p.SEGMENT_ID ?? feature.id ?? '');
      if (!key) continue;
      const identity = `${kind}:${key}`;
      if (seen.has(identity)) continue;
      seen.add(identity);
      const paths = feature.geometry.type === 'LineString' ? [feature.geometry.coordinates]
        : feature.geometry.type === 'MultiLineString' ? feature.geometry.coordinates : [];
      paths.forEach((path, part) => {
        if (path.length < 2 || path.length > 2000 || path.some(p=>!Number.isFinite(p[0])||!Number.isFinite(p[1])||Math.abs(p[0])>180||Math.abs(p[1])>85)) return;
        const width = typeof p.WIDTH === 'number' && p.WIDTH > 0 && p.WIDTH <= 20 ? p.WIDTH : null;
        lines.push({ id: `existing:${layer.id}:${identity}:${part}`, kind, widthM: width,
          label: String(p.PATH_NAME || p.FULL_NAME || (sharedAccess?'Shared access route':p.ASSET_TYPE) || (kind==='path'?'Mapped path':'Existing street')),
          points: path.map(p=>[p[0],p[1]]) });
      });
    }
  }
  return { lines };
}
