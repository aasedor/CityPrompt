import { useMemo, useState } from 'react';
import type { Building, SiteZone, SiteZoneType } from '@/types';

const LABELS: Record<SiteZoneType, string> = { building: 'Building', road: 'Road / path', green_space: 'Park', parking: 'Plaza', water: 'Water', residential: 'Residential area', development_area: 'Development area', site_boundary: 'Site boundary' };
const COLORS: Record<SiteZoneType, string> = { building: '#7c3aed', road: '#475569', green_space: '#15803d', parking: '#b45309', water: '#0284c7', residential: '#a855f7', development_area: '#64748b', site_boundary: '#0f172a' };
interface PlanFeature { id: string; name: string; type: SiteZoneType; coordinates: number[][]; }

/** Public cartographic view: stored outlines only, with no editing or generation handlers. */
export function SharedPlanPreview({ zones, buildings = [] }: { zones: SiteZone[]; buildings?: Building[] }) {
  const [selectedId, setSelectedId] = useState('');
  const plan = useMemo(() => {
    const linkedBuildings = new Set(zones.flatMap((zone) => [...(zone.building_ids ?? []), ...(zone.building_id ? [zone.building_id] : [])]));
    const features: PlanFeature[] = [
      ...zones.map((zone) => ({ id: zone.id, name: zone.name || LABELS[zone.zone_type], type: zone.zone_type, coordinates: zone.coordinates })),
      ...buildings.filter((building) => !linkedBuildings.has(building.id) && building.footprint_coordinates?.length).map((building) => ({ id: building.id, name: building.name || 'Building', type: 'building' as const, coordinates: building.footprint_coordinates! })),
    ].filter((feature) => feature.coordinates.length >= (feature.type === 'road' ? 2 : 3) && feature.coordinates.every((point) => point.length >= 2 && Number.isFinite(point[0]) && Number.isFinite(point[1]) && Math.abs(point[0]) <= 180 && Math.abs(point[1]) <= 90));
    if (!features.length) return null;
    const points = features.flatMap((feature) => feature.coordinates);
    let west = Infinity; let south = Infinity; let east = -Infinity; let north = -Infinity;
    for (const point of points) { west = Math.min(west, point[0]); east = Math.max(east, point[0]); south = Math.min(south, point[1]); north = Math.max(north, point[1]); }
    const centerLon = (west + east) / 2;
    const centerLat = (south + north) / 2;
    const xScale = Math.max(0.0001, Math.cos(centerLat * Math.PI / 180)) * 111_320;
    const yScale = 111_320;
    const width = Math.max(20, (east - west) * xScale);
    const height = Math.max(20, (north - south) * yScale);
    const padding = Math.max(width, height) * 0.08;
    return {
      features: features.map((feature) => ({ ...feature, points: feature.coordinates.map(([lon, lat]) => ((lon - centerLon) * xScale) + ',' + ((centerLat - lat) * yScale)).join(' ') })),
      viewBox: [-width / 2 - padding, -height / 2 - padding, width + padding * 2, height + padding * 2].join(' '),
    };
  }, [zones, buildings]);
  if (!plan) return <p className="rounded-lg bg-slate-50 p-4 text-slate-600">No saved plan outlines are available yet.</p>;
  const selected = plan.features.find((feature) => feature.id === selectedId);
  return <div className="space-y-3">
    <div className="relative overflow-hidden rounded-xl border border-slate-300 bg-[#f8faf5]">
      <span aria-hidden className="absolute right-3 top-3 rounded bg-white/90 px-2 py-1 text-sm font-semibold">↑ N</span>
      <svg role="img" aria-label="Community plan, north up. Choose a feature below to inspect its name and type." viewBox={plan.viewBox} className="h-[min(55vh,520px)] min-h-64 w-full">
        {plan.features.map((feature) => feature.type === 'road'
          ? <polyline key={feature.id} points={feature.points} fill="none" stroke={selectedId === feature.id ? '#dc2626' : COLORS[feature.type]} strokeWidth={selectedId === feature.id ? 5 : 3} vectorEffect="non-scaling-stroke" strokeLinecap="round" onClick={() => setSelectedId(feature.id)}><title>{feature.name}</title></polyline>
          : <polygon key={feature.id} points={feature.points} fill={feature.type === 'site_boundary' ? 'none' : COLORS[feature.type]} fillOpacity={0.3} stroke={selectedId === feature.id ? '#dc2626' : COLORS[feature.type]} strokeWidth={selectedId === feature.id ? 4 : 2} strokeDasharray={feature.type === 'site_boundary' ? '8 5' : undefined} vectorEffect="non-scaling-stroke" onClick={() => setSelectedId(feature.id)}><title>{feature.name}</title></polygon>)}
      </svg>
    </div>
    <p className="text-sm text-slate-600">Saved design outlines · North is up · Reference layers and terrain are not shown.</p>
    <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm">{[...new Set(plan.features.map((feature) => feature.type))].map((type) => <span key={type} className="inline-flex items-center gap-2"><span aria-hidden className="h-3 w-3 rounded-sm" style={{ backgroundColor: COLORS[type] }} />{LABELS[type]}</span>)}</div>
    <label className="block text-sm font-semibold">Inspect a drawing<select value={selectedId} onChange={(event) => setSelectedId(event.target.value)} className="mt-1 block min-h-11 w-full max-w-md rounded-lg border border-slate-300 px-3 font-normal"><option value="">Choose a drawing</option>{plan.features.map((feature) => <option key={feature.id} value={feature.id}>{feature.name} · {LABELS[feature.type]}</option>)}</select></label>
    {selected && <p role="status" className="text-sm text-slate-700"><strong>{selected.name}</strong> · {LABELS[selected.type]}</p>}
  </div>;
}
