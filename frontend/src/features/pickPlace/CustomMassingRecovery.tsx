import type { Building, SiteZone, SiteZoneProperties } from '@/types';
import { useEffect, useRef, useState } from 'react';
import { getCommunity3DMeta } from '@/features/community3d/community3d';
import { buildPlanRequestForItem, deriveItems } from '@/features/legoAssembly/communityCompiler';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import { getApiErrorMessage } from '@/services/api';
import { BuildingDesignControls } from './BuildingDesignControls';
import { assetForZone } from './catalogue';
import * as THREE from 'three';
import type { LegoAssemblyPlan } from '@/features/legoAssembly/legoAssemblyApi';
import { authoredHomePlotFrame, preservesAuthoredPlotAxes } from '@/features/legoAssembly/detachedPlot';
import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import { placedNativeFootprints } from '@/components/viewer/globe/buildingGroundContact';
import { computeLegoStackYaw, legoInstanceTransform } from '@/components/viewer/globe/legoGlobePlacement';
import { preparedSiteContainsZone } from '@/components/viewer/globe/sitePreparationSurface';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

interface RecoveryProps {
  zone: SiteZone;
  buildings?: Building[];
  onReplace: (properties: SiteZoneProperties) => void;
}

/** An old style card and custom prompt do not establish an original 3D asset. */
export function CustomMassingRecovery({zone, buildings, onReplace}: RecoveryProps) {
  const building = buildings?.find(item => item.id === zone.building_id && item.project_id === zone.project_id);
  if (getCommunity3DMeta(zone)?.generator !== 'planned_massing'
    || zone.properties?.custom_style_enabled !== true || zone.properties.pick_place_asset
    || zone.properties.user_generated_source_id || !building
    || building.model_url || Object.values(building.lod_urls ?? {}).some(Boolean)
    || building.specifications?.legoAssembly || building.specifications?.rlasm
    || ['pending','queued','processing','generating','in_progress'].includes(building.generation_status ?? '')) return null;
  // Any saved or local authored change cancels the old selection and check.
  return <RecoveryEditor key={JSON.stringify([zone.id,zone.updated_at,zone.coordinates,zone.properties])}
    zone={zone} onReplace={onReplace}/>;
}

/** Use the renderer's native bounds, origin and transforms, then the shared
 * full-edge containment check. A programme's target rectangle alone cannot
 * establish that the detailed geometry fits a tapered saved reservation.
 * Bounds follow the catalogue's bottom-centred whole-clay contract; arbitrary
 * generated or legacy model URLs require measured origin/bounds first. */
function planFitsSavedPlot(zone: SiteZone, plan: LegoAssemblyPlan): boolean {
  const frame = computeFootprintFrame(zone.coordinates);
  if (!frame || !plan.instances.length) return false;
  const authored = preservesAuthoredPlotAxes(zone.properties) ? authoredHomePlotFrame(zone.coordinates) : undefined;
  const yaw = authored?.yawRad ?? computeLegoStackYaw(frame.bearingRad,plan.target,0);
  return plan.instances.every(instance=>{
    const [width,depth,height] = instance.native_dimensions_m;
    if (![width,depth,height,...instance.scale].every(value=>Number.isFinite(value) && value>0)
      || !instance.position.every(Number.isFinite) || !Number.isFinite(instance.rotation_degrees)) return false;
    // Check every occupied module, including upper floors and roof overhangs.
    const footprint = placedNativeFootprints([{bounds:new THREE.Box3(
      new THREE.Vector3(-width/2,0,-depth/2),new THREE.Vector3(width/2,height,depth/2)),
    transform:legoInstanceTransform(instance)}],yaw,frame.rectCenterLocal);
    if (footprint.length!==1) return false;
    const occupied = {...zone,coordinates:footprint[0].map(([x,y])=>[
      frame.centroidLng+x/metersPerDegLon(frame.centroidLat),frame.centroidLat+y/METERS_PER_DEG_LAT,
    ])};
    // Ten micrometres absorbs coordinate round trips, while exact shared
    // edges remain legal and every concave edge interval is still checked.
    return preparedSiteContainsZone(zone,occupied,0.00001);
  });
}

function RecoveryEditor({zone,onReplace}: Pick<RecoveryProps,'zone'|'onReplace'>) {
  const [choosing,setChoosing] = useState(false);
  const [candidate,setCandidate] = useState<SiteZoneProperties>();
  const [checking,setChecking] = useState(false);
  const [error,setError] = useState('');
  const request = useRef(0);
  useEffect(() => () => { request.current += 1; }, []);
  const cancel = () => { request.current += 1; setChoosing(false); setCandidate(undefined); setChecking(false); setError(''); };
  const replace = async () => {
    if (!candidate || checking) return;
    const token = ++request.current;
    setChecking(true); setError('');
    try {
      const item = deriveItems([{...zone,properties:candidate}])[0];
      if (!item) throw new Error('Choose a supported detailed building.');
      // Check the real saved plot, selected revision and storeys before writing.
      const plan = await legoAssemblyApi.plan(buildPlanRequestForItem(item));
      if (!planFitsSavedPlot(item.zone,plan)) throw new Error('This detailed building extends outside the saved plot. Choose a smaller reviewed footprint percentage or another building.');
      if (request.current === token) onReplace(candidate);
    } catch (failure) {
      if (request.current === token) setError(`Your custom design is unchanged. ${getApiErrorMessage(failure)} Choose another building or keep this design.`);
    } finally {
      if (request.current === token) setChecking(false);
    }
  };
  const selected = candidate ? assetForZone({properties:candidate}) : undefined;
  const button = 'min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold disabled:opacity-50';
  return <section aria-label="Custom building model" className="space-y-2 rounded-lg border border-amber-700 bg-amber-50 p-3 text-sm text-slate-900">
    <p className="font-semibold">This custom design is shown as a simple building volume.</p>
    <p>No detailed model was saved for it. Refresh checks available models; it cannot create this custom design.</p>
    <p>Keep this design, or choose a detailed building and review the replacement before saving.</p>
    {!choosing ? <button type="button" className={button} onClick={()=>setChoosing(true)}>Choose a detailed building</button>
      : <>
        {!candidate ? <BuildingDesignControls zone={zone} disabled={checking} requireExplicitSelection onSave={properties=>{
          setCandidate({...properties,custom_style_enabled:false}); setError('');
        }}/>
          : <>
            <p>Replace your {Number(zone.properties?.floor_count ?? zone.properties?.floors ?? 1)} storeys with {selected?.label ?? String(candidate.development_archetype_label ?? 'the selected building')} · {Number(candidate.floor_count ?? candidate.floors)} storeys · {Number(candidate.height_m ?? candidate.height).toFixed(1)} m high. The saved plot stays in place.</p>
            <button type="button" className={button} disabled={checking} onClick={replace}>{checking?'Checking detailed model…':'Replace custom massing'}</button>
            <button type="button" className={button} disabled={checking} onClick={()=>{setCandidate(undefined);setError('');}}>Choose another building</button>
          </>}
        <button type="button" className={button} onClick={cancel}>Keep custom design</button>
      </>}
    {error && <p role="alert" className="text-sm text-red-800">{error}</p>}
  </section>;
}
