import { useState, useRef, useEffect } from 'react';
import { Eye, MousePointer, Sparkles, Loader2, Footprints, RefreshCw, Building2, Route, TreePine, Map as MapIcon, ChevronUp } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZoneType, SiteZone, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG, ROAD_PRESETS } from '@/types';
import { useViewerStore } from '@/store';
import { siteZonesApi } from '@/services/api';

/** Logical groupings for zone types */
const ZONE_GROUPS = [
  {
    key: 'structures',
    label: 'Structures',
    Icon: Building2,
    types: ['building', 'residential'] as SiteZoneType[],
  },
  {
    key: 'infrastructure',
    label: 'Infra',
    Icon: Route,
    types: ['road', 'parking'] as SiteZoneType[],
  },
  {
    key: 'natural',
    label: 'Natural',
    Icon: TreePine,
    types: ['green_space', 'water'] as SiteZoneType[],
  },
  {
    key: 'planning',
    label: 'Planning',
    Icon: MapIcon,
    types: ['site_boundary', 'development_area'] as SiteZoneType[],
  },
] as const;

/** Maximum width across all road presets — used to scale visual width bars */
const MAX_ROAD_WIDTH = Math.max(...ROAD_PRESETS.map((p) => p.width));

interface ZoneGroupDropdownProps {
  group: (typeof ZONE_GROUPS)[number];
  isOpen: boolean;
  onToggle: () => void;
  activeTool: SiteZoneType | null;
  onSelectTool: (type: SiteZoneType, properties?: SiteZoneProperties) => void;
}

function ZoneGroupDropdown({ group, isOpen, onToggle, activeTool, onSelectTool }: ZoneGroupDropdownProps) {
  const { Icon, label, types } = group;
  const activeChild = types.find((t) => t === activeTool);
  const activeColor = activeChild ? ZONE_TYPE_CONFIG[activeChild].color : undefined;

  // Track which zone type is expanded to show sub-presets (e.g. road)
  const [expandedType, setExpandedType] = useState<SiteZoneType | null>(null);

  return (
    <div className="relative">
      {/* Upward flyout */}
      {isOpen && (
        <div className="absolute bottom-full left-1/2 z-30 mb-2 -translate-x-1/2 rounded-lg bg-gray-800 p-1.5 shadow-xl ring-1 ring-white/10">
          <div className="flex flex-col gap-1">
            {types.map((type) => {
              const config = ZONE_TYPE_CONFIG[type];
              const isActive = activeTool === type;
              const hasPresets = type === 'road';
              const isExpanded = expandedType === type;

              return (
                <div key={type} className="flex flex-col">
                  <button
                    onClick={() => {
                      if (hasPresets) {
                        setExpandedType(isExpanded ? null : type);
                      } else {
                        onSelectTool(type);
                      }
                    }}
                    className={`flex items-center gap-2 whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-white/20 text-white ring-1 ring-white/40'
                        : 'text-gray-300 hover:bg-white/10 hover:text-white'
                    }`}
                    title={hasPresets ? `Expand ${config.label} presets` : `Draw ${config.label} zone`}
                  >
                    <span
                      className="inline-block h-3 w-3 flex-shrink-0 rounded-sm border border-white/30"
                      style={{ backgroundColor: config.color }}
                    />
                    <span>{config.label}</span>
                    {hasPresets && (
                      <ChevronUp
                        size={10}
                        className={`ml-auto transition-transform ${isExpanded ? '' : 'rotate-180'}`}
                      />
                    )}
                    {isActive && !hasPresets && (
                      <span className="ml-auto rounded bg-white/20 px-1.5 py-0.5 text-[10px] leading-none">
                        Active
                      </span>
                    )}
                  </button>

                  {/* Road preset sub-menu */}
                  {hasPresets && isExpanded && (
                    <div className="ml-2 mt-1 flex flex-col gap-1 border-l border-white/10 pl-2">
                      {ROAD_PRESETS.map((preset) => (
                        <button
                          key={preset.label}
                          onClick={() => {
                            onSelectTool('road', { width: preset.width, lane_count: preset.lanes });
                            setExpandedType(null);
                          }}
                          className="group flex items-center gap-2 whitespace-nowrap rounded-md px-2 py-1.5 text-xs text-gray-300 transition-all hover:bg-white/10 hover:text-white"
                          title={`${preset.label} — ${preset.width}m, ${preset.lanes} lane${preset.lanes > 1 ? 's' : ''}`}
                        >
                          {/* Width-proportional bar */}
                          <span
                            className="inline-block h-2 flex-shrink-0 rounded-sm"
                            style={{
                              width: `${Math.max(8, (preset.width / MAX_ROAD_WIDTH) * 48)}px`,
                              backgroundColor: config.color,
                            }}
                          />
                          <span className="font-medium">{preset.label}</span>
                          <span className="ml-auto text-[10px] text-gray-500 group-hover:text-gray-400">
                            {preset.width}m
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Category trigger button */}
      <button
        onClick={onToggle}
        className={`flex items-center gap-1.5 rounded-lg px-2 py-2 text-xs font-medium transition-all sm:px-3 sm:py-1.5 ${
          isOpen
            ? 'bg-white/20 text-white ring-2 ring-white/40'
            : activeChild
              ? 'bg-white/15 text-white'
              : 'text-gray-300 hover:bg-white/10 hover:text-white'
        }`}
        title={label}
      >
        {activeColor ? (
          <span
            className="inline-block h-3 w-3 rounded-sm border border-white/30"
            style={{ backgroundColor: activeColor }}
          />
        ) : (
          <Icon size={14} />
        )}
        <span>{label}</span>
        <ChevronUp
          size={12}
          className={`transition-transform ${isOpen ? '' : 'rotate-180'}`}
        />
      </button>
    </div>
  );
}

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
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const groupsRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (groupsRef.current && !groupsRef.current.contains(e.target as Node)) {
        setOpenGroup(null);
      }
    }
    if (openGroup) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [openGroup]);

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

  const handleSelectTool = (type: SiteZoneType, properties?: SiteZoneProperties) => {
    if (!properties && activeSitePlannerTool === type) {
      setActiveSitePlannerTool(null);
    } else {
      setActiveSitePlannerTool(type, properties);
    }
    setOpenGroup(null);
  };

  return (
    <div className="flex w-full flex-col items-stretch gap-1.5 rounded-xl bg-gray-900/90 px-3 py-2 shadow-2xl backdrop-blur-sm sm:flex-row sm:items-center sm:justify-center sm:gap-2">
      {/* Zone tools row — wraps on mobile */}
      <div ref={groupsRef} className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        {/* Select / Move tool */}
        <button
          onClick={() => { setActiveSitePlannerTool(null); setOpenGroup(null); }}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all sm:py-1.5 ${
            activeSitePlannerTool === null
              ? 'bg-white/20 text-white ring-2 ring-white/40'
              : 'text-gray-300 hover:bg-white/10 hover:text-white'
          }`}
          title="Select / Move zones"
        >
          <MousePointer size={14} />
          <span>Select</span>
        </button>

        <div className="mx-0.5 hidden h-6 w-px bg-white/20 sm:block" />

        {ZONE_GROUPS.map((group) => (
          <ZoneGroupDropdown
            key={group.key}
            group={group}
            isOpen={openGroup === group.key}
            onToggle={() => setOpenGroup(openGroup === group.key ? null : group.key)}
            activeTool={activeSitePlannerTool}
            onSelectTool={handleSelectTool}
          />
        ))}
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
