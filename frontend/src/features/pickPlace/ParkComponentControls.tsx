import { useState } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { resolveParkSpecialtyStructureKind } from '@/components/viewer/globe/parkGroundProfiles';

/** A bounded furniture edit leaves the reviewed skate programme untouched. */
export function ParkComponentControls({ zone, disabled, onSave }: {
  zone: SiteZone; disabled: boolean; onSave: (properties: SiteZoneProperties) => void;
}) {
  const [edge, setEdge] = useState(zone.properties?.skate_spectator_edge === 'south' ? 'south' : 'north');
  if (resolveParkSpecialtyStructureKind(zone) !== 'skate_park_v0_assembly') return null;
  return <form className="mb-3 border-b border-slate-300 pb-3" onSubmit={event => {
    event.preventDefault(); onSave({ ...zone.properties, skate_spectator_edge: edge });
  }}>
    <label className="text-xs font-semibold text-slate-800">Spectator bench
      <select aria-label="Spectator bench position" value={edge} onChange={event => setEdge(event.target.value)}
        className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900">
        <option value="north">Back edge</option><option value="south">Front edge</option>
      </select>
    </label>
    <p className="my-2 text-xs text-slate-600">Both seating positions face the bowls and keep the skating area clear.</p>
    <button disabled={disabled} className="min-h-11 w-full rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40">Apply seating</button>
  </form>;
}
