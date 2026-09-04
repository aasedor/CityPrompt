import { useState, type ReactNode } from 'react';
import { Brain, MousePointer, HelpCircle, Layers3, Eye, Building2, History, Ruler } from 'lucide-react';
import type { SiteZoneType } from '@/types';
import { useViewerStore } from '@/store';
import { UndoRedoButtons } from '@/components/ui/UndoRedoButtons';
import buildingsIcon from '@/assets/site-planner-tools/buildings.svg';
import streetsPathsIcon from '@/assets/site-planner-tools/streets-paths.svg';
import parksPlazasIcon from '@/assets/site-planner-tools/parks-plazas.svg';
import siteBoundaryIcon from '@/assets/site-planner-tools/site-boundary.svg';

type CoreToolId = 'siteBoundary' | 'buildings' | 'streetsPaths' | 'parksPlazas';
type ParksSubtype = 'park' | 'plaza';
const CORE_TOOLS: { id: CoreToolId; label: string; description: string; icon: string }[] = [
  { id: 'buildings', label: 'Building', description: 'Draw a building outline', icon: buildingsIcon },
  { id: 'parksPlazas', label: 'Park', description: 'Draw a green space', icon: parksPlazasIcon },
  { id: 'streetsPaths', label: 'Road', description: 'Draw a street or path', icon: streetsPathsIcon },
];
interface SitePlannerToolbarProps {
  onShowGuide?: () => void;
  onToggleHistory?: () => void;
  historyOpen?: boolean;
  measureActive?: boolean;
  onMeasureModeChange?: (active: boolean) => void;
  isGlobeMode?: boolean;
  layout?: 'default' | 'sidebar';
  bottomSlot?: ReactNode;
  uploadSlot?: ReactNode;
  onMasterPlan?: () => void;
  masterPlanActive?: boolean;
  onSiteBoundary?: () => void;
}
function mapToolToCoreTool(tool: SiteZoneType | null): CoreToolId | null {
  if (tool === 'site_boundary') return 'siteBoundary';
  if (tool === 'building') return 'buildings';
  if (tool === 'road') return 'streetsPaths';
  if (tool === 'green_space' || tool === 'parking') return 'parksPlazas';
  return null;
}
export function SitePlannerToolbar({ onShowGuide, onToggleHistory, historyOpen, measureActive = false,
  onMeasureModeChange, isGlobeMode = false, layout = 'default', bottomSlot, uploadSlot,
  onMasterPlan, masterPlanActive = false, onSiteBoundary }: SitePlannerToolbarProps) {
  const { activeSitePlannerTool, setActiveSitePlannerTool, streetViewPegman, setStreetViewActive,
    settings, updateSettings } = useViewerStore();
  const [parksSubtype, setParksSubtype] = useState<ParksSubtype>('park');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const isSidebar = layout === 'sidebar';
  const activeCoreTool = mapToolToCoreTool(activeSitePlannerTool);
  const selectedParksSubtype = activeSitePlannerTool === 'parking' ? 'plaza' : activeSitePlannerTool === 'green_space' ? 'park' : parksSubtype;
  const focusStyle = 'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#151515]';
  const buttonStyle = (active = false) => [
    'site-planner-tool-button flex min-h-11 items-center justify-center gap-2 rounded-lg border-2 border-[#151515] px-3 py-2 text-sm font-semibold text-[#151515]',
    focusStyle, active ? 'bg-[#c9ff3d] shadow-[2px_2px_0_0_#151515]' : 'bg-white hover:bg-[#fff9ec]',
  ].join(' ');
  const leaveOtherModes = () => {
    if (streetViewPegman) setStreetViewActive(false);
    onMeasureModeChange?.(false);
  };
  const activateCoreTool = (id: CoreToolId) => {
    leaveOtherModes();
    if (id === 'siteBoundary' && onSiteBoundary) { onSiteBoundary(); return; }
    const zoneType = id === 'siteBoundary' ? 'site_boundary' : id === 'buildings' ? 'building'
      : id === 'streetsPaths' ? 'road' : selectedParksSubtype === 'plaza' ? 'parking' : 'green_space';
    setActiveSitePlannerTool(activeSitePlannerTool === zoneType ? null : zoneType);
  };
  const activateAdvanced = (type: SiteZoneType) => {
    leaveOtherModes();
    setActiveSitePlannerTool(activeSitePlannerTool === type ? null : type);
  };

  return <div aria-label="Drawing tools" className={['site-planner-toolbar', isSidebar ? 'site-planner-toolbar--sidebar' : 'site-planner-toolbar--default', 'flex min-h-0 w-full flex-col gap-2 overflow-y-auto overscroll-contain rounded-xl border-2 border-[#151515] bg-[#fff9ec]/95 p-2.5 shadow-[4px_4px_0_0_#151515] backdrop-blur-xl'].join(' ')}>
    <p className="px-1 text-sm font-semibold text-[#151515]">Draw your community</p>
    <div className={['site-planner-core-grid grid gap-2', isSidebar ? 'grid-cols-3 sm:grid-cols-1' : 'grid-cols-3'].join(' ')}>
      {CORE_TOOLS.map((tool) => {
        const active = activeCoreTool === tool.id;
        const isPlaza = tool.id === 'parksPlazas' && selectedParksSubtype === 'plaza';
        const label = isPlaza ? 'Plaza' : tool.label;
        return <button key={tool.id} type="button" data-tour={'tool-' + tool.id} aria-label={label} aria-pressed={active}
          onClick={() => activateCoreTool(tool.id)} title={isPlaza ? 'Draw a plaza outline' : tool.description}
          className={['site-planner-core-tool group flex min-h-14 items-center gap-2.5 rounded-lg border-2 border-[#151515] px-2.5 py-2 text-left flex-col justify-center sm:flex-row sm:justify-start', focusStyle, active ? 'bg-[#c9ff3d] shadow-[2px_2px_0_0_#151515]' : 'bg-white hover:bg-[#fff9ec]'].join(' ')}>
          <img src={tool.icon} alt="" aria-hidden className="site-planner-core-icon h-8 w-8 shrink-0 rounded-md object-cover" />
          <span className="min-w-0"><span className="site-planner-core-label block text-sm font-bold text-[#151515]">{label}</span>
            <span className="site-planner-core-drawtype hidden text-xs leading-snug text-slate-600 sm:block">{isPlaza ? 'Draw a public space' : tool.description}</span></span>
        </button>;
      })}
    </div>

    {activeSitePlannerTool && <div role="status" className="rounded-lg bg-white px-3 py-2 text-sm leading-relaxed text-slate-800">
      <p className="hidden sm:block">{activeSitePlannerTool === 'road' ? 'Click at least 2 points along the road.' : 'Click at least 3 corners around the area.'} Press <strong>Enter</strong> to finish, or double-click.</p>
      <p className="sm:hidden">{isGlobeMode ? 'Move the map under the crosshair. Tap to place each point, then tap Finish.' : 'Tap each corner, then double-tap to finish.'}</p>
      <p className="mt-1 hidden text-xs text-slate-600 sm:block">Backspace removes the last point. Esc clears this drawing.</p>
    </div>}

    <div className="site-planner-control-row flex flex-wrap items-center gap-2">
      <button type="button" data-tour="select-btn" aria-pressed={!activeSitePlannerTool && !streetViewPegman && !measureActive}
        onClick={() => { leaveOtherModes(); setActiveSitePlannerTool(null); }} className={buttonStyle(!activeSitePlannerTool && !streetViewPegman && !measureActive)} title="Click a drawing to select and edit it"><MousePointer size={18} /> Select</button>
      <div aria-label="Undo and redo" className="[&_button]:min-h-11 [&_button]:min-w-11 [&_button]:focus-visible:outline [&_button]:focus-visible:outline-2 [&_button]:focus-visible:outline-offset-2"><UndoRedoButtons /></div>
      <button type="button" data-tour="more-tools-btn" aria-expanded={showAdvanced} aria-controls="site-planner-advanced-tools" onClick={() => setShowAdvanced((value) => !value)} className={buttonStyle(showAdvanced)} title="Optional drawing and viewing tools"><Layers3 size={18} /> More Tools</button>
      {onShowGuide && <button type="button" onClick={onShowGuide} className={buttonStyle()} title="Open the quick-start guide"><HelpCircle size={18} /> Guide</button>}
    </div>

    {showAdvanced && <div id="site-planner-advanced-tools" className="site-planner-advanced-row space-y-2 rounded-lg border border-slate-300 bg-white p-2">
      <p className="text-sm font-semibold text-slate-800">Optional tools</p>
      <p className="text-xs leading-relaxed text-slate-600">You can start drawing without a site boundary or imported data.</p>
      <div className={['grid gap-2', isSidebar ? 'grid-cols-1' : 'grid-cols-2 sm:grid-cols-3'].join(' ')}>
        <button type="button" data-tour="tool-siteBoundary" aria-pressed={activeCoreTool === 'siteBoundary'} onClick={() => activateCoreTool('siteBoundary')} className={'site-planner-core-tool ' + buttonStyle(activeCoreTool === 'siteBoundary')} title="Draw or select your site boundary"><img src={siteBoundaryIcon} alt="" aria-hidden className="site-planner-core-icon h-6 w-6" /><span className="site-planner-core-label">Site Boundary</span></button>
        {onMasterPlan && <button type="button" data-tour="tool-masterPlan" aria-pressed={masterPlanActive} onClick={onMasterPlan} className={'site-planner-core-tool ' + buttonStyle(masterPlanActive)} title="Explore planning scenarios for your site boundary"><Brain size={18} /><span className="site-planner-core-label">Master Plan</span></button>}
        <button type="button" aria-pressed={Boolean(streetViewPegman)} onClick={() => { onMeasureModeChange?.(false); setActiveSitePlannerTool(null); setStreetViewActive(!streetViewPegman); }} className={buttonStyle(Boolean(streetViewPegman))} title="Place a camera for a street-level view"><Eye size={18} /> Street View</button>
        {onMeasureModeChange && <button type="button" aria-pressed={measureActive} onClick={() => { if (streetViewPegman) setStreetViewActive(false); setActiveSitePlannerTool(null); onMeasureModeChange(!measureActive); }} className={buttonStyle(measureActive)} title="Measure distance"><Ruler size={18} /> Measure</button>}
        {!isGlobeMode && <button type="button" aria-pressed={settings.showExistingBuildings} onClick={() => updateSettings({ showExistingBuildings: !settings.showExistingBuildings })} className={buttonStyle(settings.showExistingBuildings)} title={settings.showExistingBuildings ? 'Hide existing 3D buildings' : 'Show existing 3D buildings'}><Building2 size={18} /> Existing buildings</button>}
        {onToggleHistory && <button type="button" aria-pressed={Boolean(historyOpen)} onClick={onToggleHistory} className={buttonStyle(Boolean(historyOpen))} title="Version history"><History size={18} /> History</button>}
      </div>
      <div className="flex flex-wrap gap-2" aria-label="Park or plaza">
        {(['park', 'plaza'] as const).map((subtype) => <button key={subtype} type="button" aria-pressed={selectedParksSubtype === subtype} className={buttonStyle(selectedParksSubtype === subtype)} onClick={() => {
          setParksSubtype(subtype);
          leaveOtherModes();
          setActiveSitePlannerTool(subtype === 'plaza' ? 'parking' : 'green_space');
        }}>{subtype === 'park' ? 'Parks' : 'Plazas'}</button>)}
      </div>
      <div className="flex flex-wrap gap-2" aria-label="Other areas">
        {([['residential', 'Residential'], ['development_area', 'Development Area'], ['water', 'Water']] as const).map(([type, label]) => <button key={type} type="button" aria-pressed={activeSitePlannerTool === type} onClick={() => activateAdvanced(type)} className={buttonStyle(activeSitePlannerTool === type)}>{label}</button>)}
      </div>
      {uploadSlot}
    </div>}
    {bottomSlot}
  </div>;
}
