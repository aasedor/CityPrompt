import { useMemo, useState, type ReactNode } from 'react';
import { MousePointer, HelpCircle, Layers3, Eye, Building2, History, Ruler } from 'lucide-react';
import type { SiteZoneType } from '@/types';
import { useViewerStore } from '@/store';
import { UndoRedoButtons } from '@/components/ui/UndoRedoButtons';
import siteBoundaryIcon from '@/assets/site-planner-tools/site-boundary.svg';
import buildingsIcon from '@/assets/site-planner-tools/buildings.svg';
import streetsPathsIcon from '@/assets/site-planner-tools/streets-paths.svg';
import parksPlazasIcon from '@/assets/site-planner-tools/parks-plazas.svg';

type CoreToolId = 'siteBoundary' | 'buildings' | 'streetsPaths' | 'parksPlazas';
type ParksSubtype = 'park' | 'plaza';

interface CoreToolDef {
  id: CoreToolId;
  label: string;
  drawType: 'Polygon' | 'Line';
  description: string;
  icon: string;
}

const CORE_TOOLS: CoreToolDef[] = [
  {
    id: 'siteBoundary',
    label: 'Site Boundary',
    drawType: 'Polygon',
    description: 'Define the generation area',
    icon: siteBoundaryIcon,
  },
  {
    id: 'streetsPaths',
    label: 'Streets and Paths',
    drawType: 'Line',
    description: 'Draw streets, routes, and corridors',
    icon: streetsPathsIcon,
  },
  {
    id: 'buildings',
    label: 'Buildings',
    drawType: 'Polygon',
    description: 'Place building development zones',
    icon: buildingsIcon,
  },
  {
    id: 'parksPlazas',
    label: 'Parks / Plazas',
    drawType: 'Polygon',
    description: 'Create park and plaza public spaces',
    icon: parksPlazasIcon,
  },
];

interface SitePlannerToolbarProps {
  onShowGuide?: () => void;
  onToggleHistory?: () => void;
  historyOpen?: boolean;
  measureActive?: boolean;
  onMeasureModeChange?: (active: boolean) => void;
  isGlobeMode?: boolean;
  /** 'sidebar' stacks zone-type cards in a single column (for left-rail placement).
   *  'default' keeps the existing 2x2 / 1x4 grid (for bottom-center placement). */
  layout?: 'default' | 'sidebar';
  /** Optional content rendered at the bottom of the toolbar card (e.g. AI Render action). */
  bottomSlot?: ReactNode;
}

function mapToolToCoreTool(tool: SiteZoneType | null): CoreToolId | null {
  if (tool === 'site_boundary') return 'siteBoundary';
  if (tool === 'building') return 'buildings';
  if (tool === 'road') return 'streetsPaths';
  if (tool === 'green_space' || tool === 'parking') return 'parksPlazas';
  return null;
}

function resolveZoneTypeForCoreTool(id: CoreToolId, parksSubtype: ParksSubtype): SiteZoneType {
  if (id === 'siteBoundary') return 'site_boundary';
  if (id === 'buildings') return 'building';
  if (id === 'streetsPaths') return 'road';
  return parksSubtype === 'plaza' ? 'parking' : 'green_space';
}

export function SitePlannerToolbar({
  onShowGuide,
  onToggleHistory,
  historyOpen,
  measureActive = false,
  onMeasureModeChange,
  isGlobeMode = false,
  layout = 'default',
  bottomSlot,
}: SitePlannerToolbarProps) {
  const {
    activeSitePlannerTool,
    setActiveSitePlannerTool,
    streetViewPegman,
    setStreetViewActive,
    settings,
    updateSettings,
  } = useViewerStore();
  const [parksSubtype, setParksSubtype] = useState<ParksSubtype>('park');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const isSidebar = layout === 'sidebar';
  const showExistingBuildings = settings.showExistingBuildings;
  const smallToolButtonBase = 'flex items-center gap-1.5 rounded-full border-2 border-[#151515] px-2.5 py-1.5 text-[11px] font-black uppercase text-[#151515] transition-all';
  const smallToolButtonActive = 'bg-[#c9ff3d] shadow-[3px_3px_0_0_#151515]';
  const smallToolButtonIdle = 'bg-white hover:bg-[#fff9ec] hover:shadow-[2px_2px_0_0_#151515]';

  const activeCoreTool = useMemo(
    () => mapToolToCoreTool(activeSitePlannerTool),
    [activeSitePlannerTool],
  );

  const activateCoreTool = (id: CoreToolId) => {
    // Deactivate street view when switching to a drawing tool
    if (streetViewPegman) setStreetViewActive(false);
    onMeasureModeChange?.(false);
    const zoneType = resolveZoneTypeForCoreTool(id, parksSubtype);
    if (activeSitePlannerTool === zoneType) {
      setActiveSitePlannerTool(null);
      return;
    }
    setActiveSitePlannerTool(zoneType);
  };

  const handleSelectMode = () => {
    // Deactivate street view when switching to select mode
    if (streetViewPegman) setStreetViewActive(false);
    onMeasureModeChange?.(false);
    setActiveSitePlannerTool(null);
  };

  const handleMeasureMode = () => {
    if (streetViewPegman) setStreetViewActive(false);
    setActiveSitePlannerTool(null);
    onMeasureModeChange?.(!measureActive);
  };

  const onChangeParksSubtype = (next: ParksSubtype) => {
    setParksSubtype(next);
    if (activeCoreTool === 'parksPlazas') {
      setActiveSitePlannerTool(next === 'plaza' ? 'parking' : 'green_space');
    }
  };

  return (
    <div className={`flex w-full flex-col gap-2 rounded-lg border-2 border-[#151515] bg-[#fff9ec]/95 ${isSidebar ? 'px-2.5 py-2' : 'px-3 py-2'} shadow-[8px_8px_0_0_#151515] backdrop-blur-xl`}>
      <div className={`grid gap-2 ${isSidebar ? 'grid-cols-1' : 'grid-cols-2 sm:grid-cols-4'}`}>
        {CORE_TOOLS.map((tool) => {
          const isActive = activeCoreTool === tool.id;
          return (
            <button
              key={tool.id}
              data-tour={`tool-${tool.id}`}
              onClick={() => activateCoreTool(tool.id)}
              className={`group flex rounded-lg border-2 text-left transition-all ${
                isSidebar
                  ? 'min-h-[56px] items-center gap-2.5 px-2.5 py-2'
                  : 'min-h-[86px] flex-col items-start px-3 py-2'
              } ${
                isActive
                  ? 'border-[#151515] bg-[#c9ff3d] shadow-[3px_3px_0_0_#151515]'
                  : 'border-[#151515] bg-white hover:bg-[#fff9ec] hover:shadow-[3px_3px_0_0_#151515]'
              }`}
              title={`${tool.label} (${tool.drawType})`}
            >
              <img
                src={tool.icon}
                alt=""
                className={`${isSidebar ? 'h-8 w-8' : 'h-9 w-9'} rounded-md object-cover`}
                aria-hidden
              />
              {isSidebar ? (
                <div className="flex min-w-0 flex-col leading-tight">
                  <span className="truncate text-[13px] font-black text-[#151515]">{tool.label}</span>
                  <span className="truncate text-[10px] font-bold uppercase text-[#151515]/55">{tool.drawType}</span>
                </div>
              ) : (
                <>
                  <span className="mt-2 text-sm font-black text-[#151515]">{tool.label}</span>
                  <span className="mt-0.5 text-[10px] font-bold uppercase text-[#151515]/55">{tool.drawType}</span>
                </>
              )}
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border-2 border-[#151515] bg-white px-2 py-1.5">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            data-tour="select-btn"
            onClick={handleSelectMode}
            className={`${smallToolButtonBase} ${
              activeSitePlannerTool === null
                ? smallToolButtonActive
                : smallToolButtonIdle
            }`}
            title="Select and edit existing zones"
          >
            <MousePointer size={14} />
            Select
          </button>

          <UndoRedoButtons />

          <button
            onClick={() => {
              onMeasureModeChange?.(false);
              setStreetViewActive(!streetViewPegman);
            }}
            className={`${smallToolButtonBase} ${
              streetViewPegman
                ? 'bg-[#ffb000] shadow-[3px_3px_0_0_#151515]'
                : smallToolButtonIdle
            }`}
            title="Drop a pin to generate a street-level view"
          >
            <Eye size={14} />
            Street View
          </button>

          {onMeasureModeChange && (
            <button
              onClick={handleMeasureMode}
              className={`${smallToolButtonBase} ${
                measureActive
                  ? 'bg-[#28c7e8] shadow-[3px_3px_0_0_#151515]'
                  : smallToolButtonIdle
              }`}
              title="Measure distance"
            >
              <Ruler size={14} />
              Measure
            </button>
          )}

          {!isGlobeMode && (
            <button
              onClick={() => updateSettings({ showExistingBuildings: !showExistingBuildings })}
              className={`${smallToolButtonBase} ${
                showExistingBuildings
                  ? smallToolButtonActive
                  : smallToolButtonIdle
              }`}
              title={showExistingBuildings ? 'Hide existing 3D buildings' : 'Show existing 3D buildings'}
            >
              <Building2 size={14} />
              Buildings
            </button>
          )}

          {onToggleHistory && (
            <button
              onClick={onToggleHistory}
              className={`${smallToolButtonBase} ${
                historyOpen
                  ? smallToolButtonActive
                  : smallToolButtonIdle
              }`}
              title="Version history"
            >
              <History size={14} />
              History
            </button>
          )}

          <button
            onClick={() => setShowAdvanced((v) => !v)}
            className={`${smallToolButtonBase} ${
              showAdvanced
                ? smallToolButtonActive
                : smallToolButtonIdle
            }`}
            title="Show additional technical tools"
          >
            <Layers3 size={14} />
            More Tools
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {activeCoreTool === 'parksPlazas' && (
            <div className="mr-1 inline-flex rounded-full border-2 border-[#151515] bg-white p-0.5 text-xs shadow-[3px_3px_0_0_#151515]">
              <button
                onClick={() => onChangeParksSubtype('park')}
                className={`rounded-full px-2 py-1 font-black uppercase ${
                  parksSubtype === 'park' ? 'bg-[#c9ff3d] text-[#151515]' : 'text-[#151515]/60 hover:text-[#151515]'
                }`}
                title="Draw park zones"
              >
                Parks
              </button>
              <button
                onClick={() => onChangeParksSubtype('plaza')}
                className={`rounded-full px-2 py-1 font-black uppercase ${
                  parksSubtype === 'plaza' ? 'bg-[#28c7e8] text-[#151515]' : 'text-[#151515]/60 hover:text-[#151515]'
                }`}
                title="Draw plaza zones"
              >
                Plazas
              </button>
            </div>
          )}

          {onShowGuide && (
            <button
              onClick={onShowGuide}
              className={`${smallToolButtonBase} bg-[#ff5a3d] text-white shadow-[3px_3px_0_0_#151515] hover:bg-[#ff725c]`}
              title="Show quick-start guide"
            >
              <HelpCircle size={14} />
              Guide
            </button>
          )}
        </div>
      </div>

      {showAdvanced && (
        <div className={`rounded-lg border-2 border-[#151515] bg-white px-2 py-1.5 ${isSidebar ? 'flex flex-col items-stretch gap-1.5' : 'flex flex-wrap items-center gap-1.5'}`}>
          <span className="text-[10px] font-black uppercase text-[#151515]/55">Advanced</span>
          <button
            onClick={() => {
              onMeasureModeChange?.(false);
              setActiveSitePlannerTool('residential');
            }}
            className="rounded-full border-2 border-[#151515] bg-white px-2 py-1 text-[11px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
            title="Residential (Polygon)"
          >
            Residential
          </button>
          <button
            onClick={() => {
              onMeasureModeChange?.(false);
              setActiveSitePlannerTool('development_area');
            }}
            className="rounded-full border-2 border-[#151515] bg-white px-2 py-1 text-[11px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
            title="Development Area (Polygon)"
          >
            Development Area
          </button>
          <button
            onClick={() => {
              onMeasureModeChange?.(false);
              setActiveSitePlannerTool('water');
            }}
            className="rounded-full border-2 border-[#151515] bg-white px-2 py-1 text-[11px] font-black uppercase text-[#151515] hover:bg-[#fff9ec]"
            title="Water (Polygon)"
          >
            Water
          </button>
        </div>
      )}

      {bottomSlot}
    </div>
  );
}
