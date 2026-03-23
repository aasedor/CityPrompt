import { useMemo, useState } from 'react';
import { MousePointer, HelpCircle, Layers3, Eye } from 'lucide-react';
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
    id: 'buildings',
    label: 'Buildings',
    drawType: 'Polygon',
    description: 'Place building development zones',
    icon: buildingsIcon,
  },
  {
    id: 'streetsPaths',
    label: 'Streets and Paths',
    drawType: 'Line',
    description: 'Draw streets, routes, and corridors',
    icon: streetsPathsIcon,
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

export function SitePlannerToolbar({ onShowGuide }: SitePlannerToolbarProps) {
  const { activeSitePlannerTool, setActiveSitePlannerTool, streetViewPegman, setStreetViewActive } = useViewerStore();
  const [parksSubtype, setParksSubtype] = useState<ParksSubtype>('park');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const activeCoreTool = useMemo(
    () => mapToolToCoreTool(activeSitePlannerTool),
    [activeSitePlannerTool],
  );

  const activateCoreTool = (id: CoreToolId) => {
    const zoneType = resolveZoneTypeForCoreTool(id, parksSubtype);
    if (activeSitePlannerTool === zoneType) {
      setActiveSitePlannerTool(null);
      return;
    }
    setActiveSitePlannerTool(zoneType);
  };

  const handleSelectMode = () => {
    setActiveSitePlannerTool(null);
  };

  const onChangeParksSubtype = (next: ParksSubtype) => {
    setParksSubtype(next);
    if (activeCoreTool === 'parksPlazas') {
      setActiveSitePlannerTool(next === 'plaza' ? 'parking' : 'green_space');
    }
  };

  return (
    <div className="flex w-full flex-col gap-2 rounded-xl bg-white/95 px-3 py-2 shadow-2xl backdrop-blur-sm">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {CORE_TOOLS.map((tool) => {
          const isActive = activeCoreTool === tool.id;
          return (
            <button
              key={tool.id}
              onClick={() => activateCoreTool(tool.id)}
              className={`group flex min-h-[86px] flex-col items-start rounded-xl border px-3 py-2 text-left transition-all ${
                isActive
                  ? 'border-primary-500 bg-primary-500/10 ring-2 ring-primary-500/25'
                  : 'border-primary-950/[0.08] bg-white hover:border-primary-300 hover:bg-primary-950/[0.03]'
              }`}
              title={`${tool.label} (${tool.drawType})`}
            >
              <img
                src={tool.icon}
                alt=""
                className="h-9 w-9 rounded-md object-cover"
                aria-hidden
              />
              <span className="mt-2 text-sm font-semibold text-primary-950">{tool.label}</span>
              <span className="mt-0.5 text-[11px] text-primary-950/60">{tool.drawType}</span>
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-primary-950/[0.03] px-2 py-1.5">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={handleSelectMode}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
              activeSitePlannerTool === null
                ? 'bg-primary-950/[0.08] text-primary-950 ring-1 ring-primary-950/20'
                : 'text-primary-950/70 hover:bg-primary-950/[0.05] hover:text-primary-950'
            }`}
            title="Select and edit existing zones"
          >
            <MousePointer size={14} />
            Select
          </button>

          <button
            onClick={() => setStreetViewActive(!streetViewPegman)}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
              streetViewPegman
                ? 'bg-amber-500/15 text-amber-700 ring-1 ring-amber-500/25'
                : 'text-primary-950/70 hover:bg-primary-950/[0.05] hover:text-primary-950'
            }`}
            title="Drop a pin to generate a street-level view"
          >
            <Eye size={14} />
            Street View
          </button>

          <UndoRedoButtons />

          <button
            onClick={() => setShowAdvanced((v) => !v)}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
              showAdvanced
                ? 'bg-primary-950/[0.08] text-primary-950'
                : 'text-primary-950/70 hover:bg-primary-950/[0.05] hover:text-primary-950'
            }`}
            title="Show additional technical tools"
          >
            <Layers3 size={14} />
            More Tools
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {activeCoreTool === 'parksPlazas' && (
            <div className="mr-1 inline-flex rounded-lg border border-primary-950/[0.1] bg-white p-0.5 text-xs">
              <button
                onClick={() => onChangeParksSubtype('park')}
                className={`rounded-md px-2 py-1 font-medium ${
                  parksSubtype === 'park' ? 'bg-emerald-500/15 text-emerald-700' : 'text-primary-950/60 hover:text-primary-950'
                }`}
                title="Draw park zones"
              >
                Parks
              </button>
              <button
                onClick={() => onChangeParksSubtype('plaza')}
                className={`rounded-md px-2 py-1 font-medium ${
                  parksSubtype === 'plaza' ? 'bg-sky-500/15 text-sky-700' : 'text-primary-950/60 hover:text-primary-950'
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
              className="flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs text-primary-950/60 hover:bg-primary-950/[0.05] hover:text-primary-950"
              title="Show quick-start guide"
            >
              <HelpCircle size={14} />
            </button>
          )}
        </div>
      </div>

      {showAdvanced && (
        <div className="flex flex-wrap items-center gap-1.5 rounded-lg border border-primary-950/[0.08] bg-white px-2 py-1.5">
          <span className="text-[11px] font-medium uppercase tracking-wide text-primary-950/50">Advanced</span>
          <button
            onClick={() => setActiveSitePlannerTool('residential')}
            className="rounded-md border border-primary-950/[0.08] px-2 py-1 text-xs text-primary-950/70 hover:bg-primary-950/[0.04] hover:text-primary-950"
            title="Residential (Polygon)"
          >
            Residential
          </button>
          <button
            onClick={() => setActiveSitePlannerTool('development_area')}
            className="rounded-md border border-primary-950/[0.08] px-2 py-1 text-xs text-primary-950/70 hover:bg-primary-950/[0.04] hover:text-primary-950"
            title="Development Area (Polygon)"
          >
            Development Area
          </button>
          <button
            onClick={() => setActiveSitePlannerTool('water')}
            className="rounded-md border border-primary-950/[0.08] px-2 py-1 text-xs text-primary-950/70 hover:bg-primary-950/[0.04] hover:text-primary-950"
            title="Water (Polygon)"
          >
            Water
          </button>
        </div>
      )}
    </div>
  );
}
