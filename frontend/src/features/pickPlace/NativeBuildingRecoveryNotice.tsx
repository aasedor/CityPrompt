import type { SiteZone } from '@/types';

export function NativeBuildingRecoveryNotice({ zones, onSelect }: {
  zones: SiteZone[]; onSelect: (zone: SiteZone) => void;
}) {
  if (zones.length === 0) return null;
  return <section role="alert" className="pointer-events-auto absolute bottom-20 right-4 z-50 max-h-[60vh] w-80 overflow-y-auto rounded-xl border-2 border-amber-700 bg-amber-50 p-3 text-sm text-slate-900 shadow-lg">
    <p className="font-semibold">Saved building {zones.length === 1 ? 'model' : 'models'} unavailable</p>
    <p className="my-2">Restore the matching local model, or choose a replacement in Buildings. Your saved plot is preserved.</p>
    <ul className="space-y-3">{zones.map(zone => <li key={zone.id}>
      <p className="font-semibold">{String(zone.properties?.development_archetype_label || zone.name || 'Saved building')}</p>
      <p className="break-words text-xs">Required model: {String(zone.properties?.pick_place_model_revision || 'revision not recorded')}</p>
      <button type="button" className="mt-2 min-h-11 rounded-lg border border-slate-700 bg-white px-3 font-semibold" onClick={() => onSelect(zone)}>Select saved plot</button>
    </li>)}</ul>
  </section>;
}
