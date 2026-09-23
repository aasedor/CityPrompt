import type { SiteZone } from '@/types';
import { StudioDialog } from '@/features/projects/StudioControls';
import { readBuildingEntrance } from '@/features/pickPlace/pedestrianConnections';
import { resolveZoneLabel } from '../mapEngine/geoUtils';
import { buildingGroundProblemMessage } from './buildingGroundProblemMessage';
import type { LegoGroundingIssue } from './buildingGroundContact';
import type { BuildingEntranceReview } from './buildingEntranceReview';

export function BuildingEntranceReviewPanel({zones,reviews,issues,groundRevision,groundCurrent,onClose,onSelect}:{
  zones:SiteZone[];reviews:BuildingEntranceReview[];issues:LegoGroundingIssue[];
  groundRevision:string;groundCurrent:boolean;onClose:()=>void;onSelect:(zone:SiteZone)=>void;
}) {
  const houses=zones.filter(zone=>zone.building_id || zone.building_ids?.length);
  return <StudioDialog title="Review entrances" onClose={onClose}>
    <p className="mb-3 text-sm text-slate-700">Follow each route from the sidewalk to the door. These measurements cover the added approach to the model base; the house’s own steps continue beyond it.</p>
    <div className="mb-4 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-slate-900">
      <p className="font-semibold">Design checks still open</p>
      <p className="mt-1">The platform added beneath a model is support geometry. Its exposed edges are not verified walking areas. Review the join to the house’s steps, rail ends and nearby furniture.</p>
      <p className="mt-2">Step-free access to the door has not been assessed. A nearly level approach can still lead to steps on the house. Explore a flatter placement or an entrance without steps, then review the whole route.</p>
    </div>
    {!groundCurrent&&<p role="status" className="mb-3 text-sm text-slate-700">Ground is updating or unavailable. Current entrance measurements will appear when it is ready.</p>}
    <ul className="space-y-3">{houses.map(zone=>{
      const owns=(id:string)=>zone.building_id===id||zone.building_ids?.includes(id);
      const issue=groundCurrent?issues.find(item=>owns(item.buildingId)):undefined;
      const review=groundCurrent&&!issue?reviews.find(item=>owns(item.buildingId)&&item.groundRevision===groundRevision):undefined;
      return <li key={zone.id} className="rounded-lg border border-slate-300 bg-white p-3 text-slate-900">
        <p className="font-semibold">{zone.name?.trim() || resolveZoneLabel(zone)}</p>
        {issue?<p className="my-2 text-sm">{buildingGroundProblemMessage(issue.reason)}</p>:review?<>
          <p className="my-2 text-sm">{review.generatedSteps>0?`${review.generatedSteps} generated ${review.generatedSteps===1?'step':'steps'}`:'Nearly level approach'} · {Math.abs(review.riseM).toFixed(2)} m {review.riseM<0?'down':'up'} from sidewalk to model base</p>
          <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
            <dt>Clear walking width</dt><dd>{review.clearWidthM.toFixed(2)} m</dd>
            <dt>Support height</dt><dd>Up to {review.supportHeightM.toFixed(2)} m</dd>
          </dl>
        </>:groundCurrent?<p className="my-2 text-sm">{readBuildingEntrance(zone)?'Current approach measurements are unavailable for this model. Review its entrance in 3D.':'No entrance selected. Open Connections to choose the step foot and a sidewalk.'}</p>:null}
        <button type="button" className="mt-3 min-h-11 rounded-lg border border-slate-800 bg-white px-3 font-semibold"
          onClick={()=>onSelect(zone)}>Select and review</button>
      </li>;
    })}</ul>
    {!houses.length&&<p className="text-sm">Place a building to review its entrance.</p>}
    <p className="mt-4 text-xs text-slate-600">An export records this concept design. It does not close these checks or confirm accessibility or structural safety.</p>
  </StudioDialog>;
}
