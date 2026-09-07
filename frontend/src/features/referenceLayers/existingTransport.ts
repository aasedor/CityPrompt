import type { ReferenceFeature, ReferenceLayer } from './api';

export const CALGARY_TRANSPORT_ROOT = 'https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services';
export const TRANSPORT_SOURCES = ['Street_Centreline', 'Pathways_close_view', 'Walkway_Sidewalk_Connections_view'] as const;
export interface ExistingTransportLine {
  id: string; label: string; kind: 'road' | 'path'; points: [number, number][]; widthM: number | null;
}
export interface ExistingTransport { lines: ExistingTransportLine[] }
export const EMPTY_TRANSPORT: ExistingTransport = { lines: [] };

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

/** Bounded site snapshot, never the whole-city dataset. Fetch all sources before
 * saving one layer so a failed request cannot leave half an import behind. */
export async function fetchCalgaryTransport(bounds: number[], signal?: AbortSignal): Promise<ReferenceFeature[]> {
  if (bounds.length!==4 || bounds.some(n=>!Number.isFinite(n)) || bounds[0]>=bounds[2] || bounds[1]>=bounds[3]
    || bounds[0]<-114.35 || bounds[2]>-113.85 || bounds[1]<50.8 || bounds[3]>51.25
    || bounds[2]-bounds[0]>.025 || bounds[3]-bounds[1]>.015) throw new Error('Choose a Calgary site smaller than about 1 km across.');
  const all: ReferenceFeature[]=[];
  for (const source of TRANSPORT_SOURCES) {
    const query=new URLSearchParams({where:'1=1',geometry:bounds.join(','),geometryType:'esriGeometryEnvelope',
      inSR:'4326',outSR:'4326',spatialRel:'esriSpatialRelIntersects',outFields:'*',returnGeometry:'true',returnZ:'false',
      resultRecordCount:'600',f:'geojson'});
    const response=await fetch(`${CALGARY_TRANSPORT_ROOT}/${source}/FeatureServer/0/query?${query}`,{signal});
    if(!response.ok)throw new Error('Calgary context could not load. Your design has not changed.');
    const data=await response.json();
    if(data.error || data.type!=='FeatureCollection' || !Array.isArray(data.features))throw new Error('Calgary returned an unreadable dataset. Try again later.');
    if(data.exceededTransferLimit || data.properties?.exceededTransferLimit || data.features.length>=600)throw new Error('This area has too many features. Use a smaller site for this pilot.');
    all.push(...data.features.map((feature:ReferenceFeature)=>({...feature,properties:{...feature.properties,cp_transport_source:source}})));
  }
  if(!all.length)throw new Error('No mapped streets or paths were found around this site.');
  return all;
}
