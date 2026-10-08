export type TransportNetwork = 'transit' | '5a';
export type TransportCategory = keyof typeof TRANSPORT_STYLES;
export type TransportFeature = {
  type: 'Feature'; id: string;
  properties: { category: TransportCategory; designation?: string; priority?: string | null; source: string };
  geometry: { type: 'Point'; coordinates: number[] } | { type: 'LineString'; coordinates: number[][] } | { type: 'MultiLineString'; coordinates: number[][][] };
};
export type TransportSnapshot = { type: 'FeatureCollection'; network: TransportNetwork; retrieved: string;
  sources: Record<string, { url: string; featureCount: number }>; featureCount: number; features: TransportFeature[] };
export const TRANSPORT_ASSETS = '/policy-maps/transport-vectors-v1';
export const TRANSPORT_STYLES = {
  'existing-pathway': { label: 'Existing pathway · 5A', color: '#b60000', dashed: false, description: 'An existing off-street pathway in the Council-approved 5A network. It may still need upgrades for accessibility, separation, lighting or year-round reliability.' },
  'proposed-pathway': { label: 'Recommended pathway · 5A', color: '#b60000', dashed: true, description: 'A proposed off-street pathway connection in the Council-approved 5A network. Use it to consider future walking and wheeling access; it does not confirm construction funding or an opening date.' },
  'existing-bikeway': { label: 'Existing on-street bikeway · 5A', color: '#008bff', dashed: false, description: 'An existing on-street cycling connection in the Council-approved 5A network. Inclusion does not mean it already meets every 5A principle.' },
  'proposed-bikeway': { label: 'Recommended on-street bikeway · 5A', color: '#008bff', dashed: true, description: 'A proposed on-street cycling connection. Its eventual design depends on local conditions; consider how your development could connect to this corridor.' },
  'primary-transit': { label: 'Primary Transit Network', color: '#60369b', dashed: false, description: 'A long-term primary transit corridor connecting communities and key destinations. Plan complementary land uses and pedestrian access; this designation is not a current bus timetable.' },
  'transit-undetermined': { label: 'Primary Transit Network · to be determined', color: '#60369b', dashed: true, description: 'A connection whose primary transit alignment remains to be determined. Treat its location as conceptual when planning access or development.' },
  lrt: { label: 'Skeletal Light Rail Transit', color: '#253f68', dashed: false, description: 'A light rail corridor in the City’s primary network dataset. Confirm current services separately; this policy layer describes the network structure.' },
  'future-lrt': { label: 'Future skeletal Light Rail Transit', color: '#253f68', dashed: true, description: 'A future light rail corridor in the City’s policy network. Its presence is not confirmation of final engineering, funding or an opening date.' },
  hub: { label: 'Primary Transit Hub', color: '#60369b', dashed: false, description: 'A primary transit connection point. Consider convenient transfers, safe walking access and nearby destinations when designing your community.' },
  'transit-centre': { label: 'Transit Centre', color: '#253f68', dashed: false, description: 'A transit centre identified in the City’s long-term network. Consider connections and access in the surrounding area; verify current facilities separately.' },
  'regional-hub': { label: 'Regional / inter-city gateway hub', color: '#ffd100', dashed: false, description: 'A gateway for regional or inter-city transit connections identified by the policy network. It describes a long-term connection role, not a confirmed service schedule.' },
} as const;
export function transportStyle(category: TransportCategory) { return TRANSPORT_STYLES[category]; }
export function transportNetworkForMap(id: string): TransportNetwork | undefined {
  return id === 'ctp-1' ? '5a' : id === 'mdp-2' || id === 'ctp-2' ? 'transit' : undefined;
}
export function parseTransportSnapshot(value: unknown, network: TransportNetwork): TransportSnapshot {
  const data = value as TransportSnapshot;
  const position = (p: unknown): boolean => Array.isArray(p) && p.length >= 2 && p.slice(0, 2).every(Number.isFinite)
    && p[0] > -115.5 && p[0] < -112.5 && p[1] > 49.5 && p[1] < 52.5;
  const line = (p: unknown): boolean => Array.isArray(p) && p.length >= 2 && p.every(position);
  if (!data || data.type !== 'FeatureCollection' || data.network !== network || !data.retrieved || !data.sources
    || !Array.isArray(data.features) || !data.features.length || data.features.length !== data.featureCount) throw new Error('Incomplete transport map');
  const ids = new Set<string>();
  for (const f of data.features) {
    const g = f?.geometry;
    if (!f?.id || ids.has(f.id) || !f.properties || !(f.properties.category in TRANSPORT_STYLES) || !g
      || !(g.type === 'Point' ? position(g.coordinates) : g.type === 'LineString' ? line(g.coordinates)
        : g.type === 'MultiLineString' && g.coordinates.length > 0 && g.coordinates.every(line))) throw new Error('Invalid transport feature');
    ids.add(f.id);
  }
  return data;
}
