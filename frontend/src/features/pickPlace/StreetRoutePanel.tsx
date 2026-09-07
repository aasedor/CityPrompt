import type { SiteZone } from '@/types';
import { addStreetBend, streetAssetForZone, streetSectionWidth } from './streetPlacement';
import { StreetCrossSection } from './StreetCrossSection';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';

export function StreetRoutePanel({ zone, disabled, onReshape, onClose, onDelete, onMore, onConnections }: {
  zone: SiteZone; disabled: boolean; onReshape: (coordinates: number[][]) => void;
  onClose: () => void; onDelete: () => void; onMore: () => void;
  onConnections?: () => void;
}) {
  const bend = addStreetBend(zone);
  const asset = streetAssetForZone(zone);
  const width = streetSectionWidth(zone);
  const button = 'min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40';
  return <aside aria-label="Reshape street" className="absolute bottom-4 inset-x-4 z-40 max-h-[42dvh] overflow-y-auto overscroll-contain rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl sm:left-auto sm:w-72 sm:bottom-auto sm:top-20 sm:max-h-[80vh]">
    <div className="flex items-center justify-between"><h2 className="font-bold text-slate-900">{asset?.label ?? 'Street'}</h2><button className={button} aria-label="Close street settings" onClick={onClose}>×</button></div>
    <p className="my-3 text-sm text-slate-800">Drag a white route point to bend or extend the street. Drag the street to move it.</p>
    <p className="mb-3 text-xs text-slate-600">This section stays {width} m wide. Keep route points at least {width} m apart. Choose another street type for a different width.</p>
    {asset && <StreetCrossSection asset={asset} expanded />}
    <div className="grid grid-cols-2 gap-2"><button className={button} disabled={disabled || !bend} onClick={()=>bend && onReshape(bend)}>Add bend point</button><button className={button} disabled={disabled} onClick={onDelete}>Delete street</button></div>
    {!bend && <p className="mt-2 text-xs text-slate-600">Extend a segment to {2 * width} m before adding another point.</p>}
    {asset && <CalgaryGuideDetails classification={asset.calgaryGuide} />}
    {onConnections && <button className={`${button} mt-3 w-full`} onClick={onConnections}>Connections</button>}
    <button className="mt-2 min-h-11 text-xs text-slate-700 underline" onClick={onMore}>More street types and settings</button>
  </aside>;
}
