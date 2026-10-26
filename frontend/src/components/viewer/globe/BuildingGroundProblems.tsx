import type { SiteZone } from '@/types';
import { StudioDialog } from '@/features/projects/StudioControls';
import { buildingGroundProblemMessage } from './buildingGroundProblemMessage';
import { resolveZoneLabel } from '../mapEngine/geoUtils';
import type { LegoGroundingIssue } from './buildingGroundContact';
import { buildingCaptureIssues, isBuildingAccessAdvisory } from './buildingCaptureReadiness';

export function BuildingGroundProblems({ issues, zones, onClose, onSelect }: {
  issues: LegoGroundingIssue[]; zones: SiteZone[]; onClose: () => void; onSelect: (zone: SiteZone) => void;
}) {
  return <StudioDialog title="Check building placement" onClose={onClose}>
    <p className="mb-3 text-sm text-slate-700">{buildingCaptureIssues(issues).length
      ? 'These buildings need their ground placement resolved before rendering. You can select and move them without removing them from your design.'
      : 'Review the entrance connections when refining your design. You can select and adjust each building here.'}</p>
    <ul className="space-y-3">{issues.filter(issue => issue.reason !== 'ground_not_ready').map(issue => {
      const zone = zones.find(z => z.building_id === issue.buildingId || z.building_ids?.includes(issue.buildingId));
      return <li key={`${issue.buildingId}:${issue.reason}`} className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-slate-900">
        <p className="font-semibold">{zone ? resolveZoneLabel(zone) : 'Building'}</p>
        <p className="my-2 text-sm">{buildingGroundProblemMessage(issue.reason)}</p>
        {isBuildingAccessAdvisory(issue.reason) && <p className="my-2 text-sm">{buildingCaptureIssues(issues).length
          ? 'This entrance connection is advisory. Resolve the ground placement checks before rendering.'
          : 'Rendering is available. This entrance connection remains a design advisory.'}</p>}
        {zone && <button className="min-h-11 rounded-lg border border-slate-800 bg-white px-3 font-semibold" onClick={() => onSelect(zone)}>Select and adjust</button>}
      </li>;
    })}</ul>
  </StudioDialog>;
}
