import { useMemo } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { drawnParkingZoneLayout, parkingRowDirection } from './drawnParking';

export function DrawnParkingPanel({ zone, disabled, onChange, onClose, onDelete }: {
  zone: SiteZone; disabled: boolean; onChange: (properties: SiteZoneProperties) => void;
  onClose: () => void; onDelete: () => void;
}) {
  const direction = parkingRowDirection(zone);
  const layout = useMemo(() => drawnParkingZoneLayout(zone), [zone]);
  return <aside aria-label="Parking lot settings" className="absolute right-4 top-28 z-40 w-72 rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl">
    <div className="flex items-center justify-between"><h2 className="font-bold">Parking lot</h2><button type="button" className="min-h-11 min-w-11" aria-label="Close parking lot" onClick={onClose}>×</button></div>
    <p className="text-xl font-bold" role="status">{layout.spaces.length} parking stalls</p>
    <p className="my-2 text-xs text-slate-600">Drag a corner to reshape. Stalls and drive lanes update automatically.</p>
    <label className="text-sm font-semibold">Parking rows<select aria-label="Parking rows" disabled={disabled} value={direction}
      className="my-2 min-h-11 w-full rounded border border-slate-400 bg-white px-2"
      onChange={e => onChange({ ...zone.properties, parking_row_direction: e.target.value })}>
      <option value="auto">Automatic · best fit</option><option value="along">Along the longest edge</option><option value="across">Across the longest edge</option>
    </select></label>
    {layout.problem && <p className="mb-2 text-sm" role="status">No complete rows fit. Enlarge the lot or change the rows.</p>}
    <p className="mb-3 text-xs text-slate-600">2.7 × 5.5 m stalls · 6 m drive lanes. Concept layout. Draw road access separately.</p>
    <button type="button" className="min-h-11 w-full rounded border border-slate-700 bg-white" disabled={disabled} onClick={onDelete}>Delete parking lot</button>
  </aside>;
}
