import { useState } from 'react';
import { Eye, MousePointer, Sparkles, Loader2, Footprints, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZoneType, SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';
import { siteZonesApi } from '@/services/api';

const ZONE_TYPES: SiteZoneType[] = ['site_boundary', 'building', 'residential', 'road', 'green_space', 'parking', 'water', 'development_area'];

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
    <div className="absolute bottom-4 left-1/2 z-20 flex -translate-x-1/2 items-center gap-2 rounded-xl bg-gray-900/90 px-3 py-2 shadow-2xl backdrop-blur-sm">
      {/* Select / Move tool */}
      <button
        onClick={() => setActiveSitePlannerTool(null)}
        className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
          activeSitePlannerTool === null
            ? 'bg-white/20 text-white ring-2 ring-white/40'
            : 'text-gray-300 hover:bg-white/10 hover:text-white'
        }`}
        title="Select / Move zones"
      >
        <MousePointer size={14} />
        <span className="hidden sm:inline">Select</span>
      </button>

      <div className="mx-0.5 h-6 w-px bg-white/20" />

      {ZONE_TYPES.map((type) => {
        const config = ZONE_TYPE_CONFIG[type];
        const isActive = activeSitePlannerTool === type;
        return (
          <button
            key={type}
            onClick={() => setActiveSitePlannerTool(isActive ? null : type)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
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
            <span className="hidden sm:inline">{config.label}</span>
          </button>
        );
      })}

      <div className="mx-1 h-6 w-px bg-white/20" />

      {/* Generate All */}
      {projectId && (
        <button
          onClick={handleGenerateAll}
          disabled={generating}
          className="flex items-center gap-1.5 rounded-lg bg-purple-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          title="Generate 3D models for all building/residential zones"
        >
          {generating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
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
              className="flex items-center gap-1 rounded-lg bg-orange-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-orange-600 disabled:opacity-50"
            >
              {regenerating ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              <span className="hidden sm:inline">Confirm ({zonesWithBuildings.length})</span>
            </button>
            <button
              onClick={() => setConfirmRegenerate(false)}
              className="rounded-lg px-2 py-1.5 text-xs text-gray-300 hover:text-white"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={handleRegenerateAll}
            disabled={regenerating}
            className="flex items-center gap-1.5 rounded-lg bg-purple-500/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-600 disabled:opacity-50"
            title={`Regenerate ${zonesWithBuildings.length} existing buildings`}
          >
            <RefreshCw size={14} />
            <span className="hidden sm:inline">Regen All</span>
          </button>
        )
      )}

      <button
        onClick={onWalkThrough}
        className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
        title="Walk through the site at street level"
      >
        <Footprints size={14} />
        <span className="hidden sm:inline">Walk Through</span>
      </button>

      <button
        onClick={onViewIn3D}
        className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-primary-700"
      >
        <Eye size={14} />
        View in 3D
      </button>
    </div>
  );
}
