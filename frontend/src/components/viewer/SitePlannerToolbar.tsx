import { useState } from 'react';
import { Eye, MousePointer, Sparkles, Loader2, Footprints, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZoneType, SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';
import { siteZonesApi } from '@/services/api';

const ZONE_TYPES: SiteZoneType[] = ['site_boundary', 'building', 'residential', 'road', 'green_space', 'parking', 'water', 'development_area'];

/** Short labels for mobile (< sm breakpoint) */
const ZONE_SHORT_LABELS: Record<SiteZoneType, string> = {
  site_boundary: 'Bdry',
  building: 'Bldg',
  residential: 'Res',
  road: 'Road',
  green_space: 'Green',
  parking: 'Park',
  water: 'Water',
  development_area: 'Dev',
};

interface SitePlannerToolbarProps {
  onViewIn3D: () => void;
  onWalkThrough: () => void;
  projectId?: string;
  zones?: SiteZone[];
}

export function SitePlannerToolbar({ onViewIn3D, onWalkThrough, projectId, zones }: SitePlannerToolbarProps) {
  const { activeSitePlannerTool, setActiveSitePlannerTool } = useViewerStore();
  const [generating, setGenerating] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [confirmRegenerate, setConfirmRegenerate] = useState(false);

  // Count building/residential zones that already have buildings
  const buildingZones = (zones || []).filter(
    (z) => (z.zone_type === 'building' || z.zone_type === 'residential')
  );
  const zonesWithBuildings = buildingZones.filter((z) => z.building_id);
  const hasExistingBuildings = zonesWithBuildings.length > 0;

  const handleGenerateAll = async () => {
    if (!projectId) return;
    setGenerating(true);
    try {
      const result = await siteZonesApi.generateAll(projectId);
      toast.success(
        `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
      );
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Generation failed';
      toast.error(message);
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerateAll = async () => {
    if (!projectId) return;
    if (!confirmRegenerate) {
      setConfirmRegenerate(true);
      return;
    }
    setConfirmRegenerate(false);
    setRegenerating(true);
    try {
      const result = await siteZonesApi.generateAll(projectId);
      toast.success(
        `${result.generations_queued} buildings queued for regeneration`,
      );
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Regeneration failed';
      toast.error(message);
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div className="absolute bottom-4 left-1/2 z-20 flex w-[calc(100%-2rem)] max-w-fit -translate-x-1/2 flex-col items-stretch gap-1.5 rounded-xl bg-gray-900/90 px-3 py-2 shadow-2xl backdrop-blur-sm sm:w-auto sm:flex-row sm:items-center sm:gap-2">
      {/* Zone tools row — wraps on mobile */}
      <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        {/* Select / Move tool */}
        <button
          onClick={() => setActiveSitePlannerTool(null)}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all sm:py-1.5 ${
            activeSitePlannerTool === null
              ? 'bg-white/20 text-white ring-2 ring-white/40'
              : 'text-gray-300 hover:bg-white/10 hover:text-white'
          }`}
          title="Select / Move zones"
        >
          <MousePointer size={14} />
          <span className="sm:hidden">Select</span>
          <span className="hidden sm:inline">Select</span>
        </button>

        <div className="mx-0.5 hidden h-6 w-px bg-white/20 sm:block" />

        {ZONE_TYPES.map((type) => {
          const config = ZONE_TYPE_CONFIG[type];
          const isActive = activeSitePlannerTool === type;
          return (
            <button
              key={type}
              onClick={() => setActiveSitePlannerTool(isActive ? null : type)}
              className={`flex items-center gap-1 rounded-lg px-2 py-2 text-xs font-medium transition-all sm:gap-1.5 sm:px-3 sm:py-1.5 ${
                isActive
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'text-gray-300 hover:bg-white/10 hover:text-white'
              }`}
              title={`Draw ${config.label} zone`}
            >
              <span
                className="inline-block h-3 w-3 rounded-sm border border-white/30"
                style={{ backgroundColor: config.color }}
              />
              <span className="sm:hidden">{ZONE_SHORT_LABELS[type]}</span>
              <span className="hidden sm:inline">{config.label}</span>
            </button>
          );
        })}
      </div>

      {/* Divider — visible only on desktop between zone tools and action buttons */}
      <div className="mx-1 hidden h-6 w-px bg-white/20 sm:block" />
      {/* Thin horizontal divider on mobile */}
      <div className="h-px w-full bg-white/10 sm:hidden" />

      {/* Action buttons row */}
      <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        {/* Generate All */}
        {projectId && (
          <button
            onClick={handleGenerateAll}
            disabled={generating}
            className="flex items-center gap-1.5 rounded-lg bg-purple-600 px-3 py-2 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50 sm:px-4 sm:py-1.5"
            title="Generate 3D models for all building/residential zones"
          >
            {generating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            <span className="sm:hidden">{generating ? '...' : 'Generate'}</span>
            <span className="hidden sm:inline">{generating ? 'Generating...' : 'Generate All'}</span>
          </button>
        )}

        {/* Regenerate All — visible when buildings already exist */}
        {projectId && hasExistingBuildings && (
          confirmRegenerate ? (
            <div className="flex items-center gap-1">
              <button
                onClick={handleRegenerateAll}
                disabled={regenerating}
                className="flex items-center gap-1 rounded-lg bg-orange-500 px-3 py-2 text-xs font-medium text-white hover:bg-orange-600 disabled:opacity-50 sm:py-1.5"
              >
                {regenerating ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                <span>Confirm ({zonesWithBuildings.length})</span>
              </button>
              <button
                onClick={() => setConfirmRegenerate(false)}
                className="rounded-lg px-2 py-2 text-xs text-gray-300 hover:text-white sm:py-1.5"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={handleRegenerateAll}
              disabled={regenerating}
              className="flex items-center gap-1.5 rounded-lg bg-purple-500/80 px-3 py-2 text-xs font-medium text-white hover:bg-purple-600 disabled:opacity-50 sm:py-1.5"
              title={`Regenerate ${zonesWithBuildings.length} existing buildings`}
            >
              <RefreshCw size={14} />
              <span className="sm:hidden">Regen</span>
              <span className="hidden sm:inline">Regen All</span>
            </button>
          )
        )}

        <button
          onClick={onWalkThrough}
          className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-700 sm:px-4 sm:py-1.5"
          title="Walk through the site at street level"
        >
          <Footprints size={14} />
          <span className="sm:hidden">Walk</span>
          <span className="hidden sm:inline">Walk Through</span>
        </button>

        <button
          onClick={onViewIn3D}
          className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white hover:bg-primary-700 sm:px-4 sm:py-1.5"
        >
          <Eye size={14} />
          <span className="sm:hidden">3D</span>
          <span className="hidden sm:inline">View in 3D</span>
        </button>
      </div>
    </div>
  );
}
