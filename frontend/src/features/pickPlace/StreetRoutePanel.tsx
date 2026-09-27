import type { SiteZone, SiteZoneProperties } from '@/types';
import { StreetDesignControls } from './StreetDesignControls';
import { addStreetBend, streetAssetForZone, streetSectionWidth } from './streetPlacement';
import { StreetCrossSection } from './StreetCrossSection';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';
import { nativeStreetPilot } from '@/components/viewer/globe/nativeStreetPilot';
import { BRT_VARIANT } from '@/components/viewer/globe/brtStreetProgram';
import { BrtStopControls } from './BrtStopControls';
import { isSpecialistStreet, CANAL_VARIANT } from '@/components/viewer/globe/specialistStreetProgram';

export function StreetRoutePanel({ zone, disabled, onReshape, onClose, onDelete, onMore, onConnections, onPublicConnection, connectionLeavesSite = false, onUpdateDesign }: {
  zone: SiteZone; disabled: boolean; onReshape: (coordinates: number[][]) => void;
  onClose: () => void; onDelete: () => void; onMore: () => void;
  onConnections?: () => void;
  onPublicConnection?: (enabled: boolean) => void;
  connectionLeavesSite?: boolean;
  onUpdateDesign?: (data: { coordinates: number[][]; properties: SiteZoneProperties }) => void;
}) {
  const isBrt=zone.properties?.road_selected_variant_id===BRT_VARIANT;
  const specialist=isSpecialistStreet(zone.properties?.road_selected_variant_id);
  const bend = isBrt||specialist?null:addStreetBend(zone);
  const asset = streetAssetForZone(zone);
  const width = streetSectionWidth(zone);
  const program = nativeStreetPilot(String(zone.properties?.road_selected_variant_id))?.program;
  const button = 'min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40';
  return <aside aria-label="Reshape street" className="absolute bottom-4 inset-x-4 z-40 max-h-[42dvh] overflow-y-auto overscroll-contain rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl sm:left-auto sm:w-72 sm:bottom-4 sm:top-28 sm:max-h-none">
    <div className="flex items-center justify-between"><h2 className="font-bold text-slate-900">{asset?.label ?? 'Street'}</h2><button className={button} aria-label="Close street settings" onClick={onClose}>×</button></div>
    <p className="my-3 text-sm text-slate-800">{isBrt||specialist?'Drag a white endpoint to extend this straight corridor. Drag the street to move it.':'Drag a white route point to bend or extend the street. Drag the street to move it.'}</p>
    <p className="mb-3 text-xs text-slate-600">{specialist?(zone.properties?.road_selected_variant_id===CANAL_VARIANT?'The first end holds the basin; extend the open-channel end. Connect paths at the outer bank edge. Use the original arch to cross the water.':'The 84 m arch span stays rigid. The route includes a 100 m deck and gradual approaches; connect other roads at the ground-level ends.'): 'Bring an end close to another street to snap a junction. Leave room away from bends and street ends for both sidewalks. Existing junctions stay connected as you edit. Hold Alt to skip endpoint snapping.'}</p>
    <p className="mb-3 text-xs text-slate-600">This section stays {width} m wide. Keep route points at least {width} m apart. Choose another street type for a different width.</p>
    {program && <p className="mb-3 text-xs text-slate-600">Keep the complete route between {program.minLengthM} and {program.maxLengthM} m on a prepared level site. The original structures and furniture retain their sizes as you extend it.</p>}
    {onUpdateDesign && <StreetDesignControls key={`${zone.id}:${zone.properties?.road_archetype_id}:${zone.properties?.road_selected_variant_id}`} zone={zone} disabled={disabled} onSave={onUpdateDesign} />}
    {onUpdateDesign && zone.properties?.road_selected_variant_id===BRT_VARIANT && <BrtStopControls zone={zone} disabled={disabled} onSave={onUpdateDesign}/>}
    {onPublicConnection && <div className="mb-3 rounded-lg border border-slate-300 p-2 text-sm text-slate-800">
      <label className="flex min-h-11 items-center gap-2"><input type="checkbox" disabled={disabled || connectionLeavesSite}
        checked={zone.properties?.connect_to_public_road === true} onChange={event => onPublicConnection(event.target.checked)} />
        Connect to a public road</label>
      {zone.properties?.connect_to_public_road === true && <p className="text-xs">Drag one end to the existing road edge, up to 30 m outside your site. Check the map or an imported streets layer for its position. This draws a proposed connection.</p>}
      {connectionLeavesSite && <p className="mt-2 text-xs">Move the end back inside your site to turn this off.</p>}
    </div>}
    {asset && <StreetCrossSection asset={asset} expanded />}
    <div className="grid grid-cols-2 gap-2"><button className={button} disabled={disabled || !bend} onClick={()=>bend && onReshape(bend)}>Add bend point</button><button className={button} disabled={disabled} onClick={onDelete}>Delete street</button></div>
    {!bend && !isBrt && !specialist && <p className="mt-2 text-xs text-slate-600">Extend a segment to {2 * width} m before adding another point.</p>}
    {asset && <CalgaryGuideDetails classification={asset.calgaryGuide} />}
    {onConnections && <button className={`${button} mt-3 w-full`} onClick={onConnections}>Connections</button>}
    <button className="mt-2 min-h-11 text-xs text-slate-700 underline" onClick={onMore}>More street types and settings</button>
  </aside>;
}
