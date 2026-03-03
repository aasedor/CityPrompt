import { useState, useRef, useEffect } from 'react';
import { Eye, MousePointer, Footprints, Building2, Route, TreePine, Map as MapIcon, ChevronUp, HelpCircle } from 'lucide-react';
import type { SiteZoneType, SiteZoneProperties, RoadPresetConfig, BuildingPresetConfig } from '@/types';
import { ZONE_TYPE_CONFIG, ROAD_PRESETS, BUILDING_PRESETS } from '@/types';
import { useViewerStore } from '@/store';
import { UndoRedoButtons } from '@/components/ui/UndoRedoButtons';

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
const MAX_ROAD_WIDTH = Math.max(...ROAD_PRESETS.map((p) => (p.properties.width as number) || 0));

interface ZoneGroupDropdownProps {
  group: (typeof ZONE_GROUPS)[number];
  isOpen: boolean;
  onToggle: () => void;
  activeTool: SiteZoneType | null;
  onSelectTool: (type: SiteZoneType, properties?: SiteZoneProperties) => void;
}

/** Returns the presets list for zone types that have them */
function getPresetsForType(type: SiteZoneType): (RoadPresetConfig | BuildingPresetConfig)[] | null {
  if (type === 'road') return ROAD_PRESETS;
  if (type === 'building' || type === 'residential') return BUILDING_PRESETS;
  return null;
}

/** Compact indicator shown next to each preset label */
function PresetIndicator({ preset, color }: { preset: RoadPresetConfig | BuildingPresetConfig; color: string }) {
  const width = preset.properties.width as number | undefined;
  const floors = preset.properties.floors as number | undefined;

  if (width) {
    // Road: width-proportional bar
    return (
      <span
        className="inline-block h-2 flex-shrink-0 rounded-sm"
        style={{
          width: `${Math.max(8, (width / MAX_ROAD_WIDTH) * 48)}px`,
          backgroundColor: color,
        }}
      />
    );
  }
  if (floors) {
    // Building: small floors badge
    return (
      <span
        className="inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded text-[9px] font-bold leading-none"
        style={{ backgroundColor: color, color: '#fff' }}
      >
        {floors}
      </span>
    );
  }
  // Fallback: colored dot
  return (
    <span
      className="inline-block h-3 w-3 flex-shrink-0 rounded-full"
      style={{ backgroundColor: color }}
    />
  );
}

/** Compact summary shown on the right side of a preset button */
function PresetSummary({ preset }: { preset: RoadPresetConfig | BuildingPresetConfig }) {
  const width = preset.properties.width as number | undefined;
  const floors = preset.properties.floors as number | undefined;

  if (width) return <span className="ml-auto text-[10px] text-neutral-400 group-hover:text-neutral-400">{width}m</span>;
  if (floors) return <span className="ml-auto text-[10px] text-neutral-400 group-hover:text-neutral-400">{floors}F</span>;
  return null;
}

function ZoneGroupDropdown({ group, isOpen, onToggle, activeTool, onSelectTool }: ZoneGroupDropdownProps) {
  const { Icon, label, types } = group;
  const activeChild = types.find((t) => t === activeTool);
  const activeColor = activeChild ? ZONE_TYPE_CONFIG[activeChild].color : undefined;

  // Track which zone type is expanded to show sub-presets
  const [expandedType, setExpandedType] = useState<SiteZoneType | null>(null);

  return (
    <div className="relative">
      {/* Upward flyout */}
      {isOpen && (
        <div className="absolute bottom-full left-1/2 z-30 mb-2 -translate-x-1/2 rounded-lg bg-primary-950 p-1.5 shadow-xl ring-1 ring-white/10">
          <div className="flex flex-col gap-1">
            {types.map((type) => {
              const config = ZONE_TYPE_CONFIG[type];
              const isActive = activeTool === type;
              const presets = getPresetsForType(type);
              const hasPresets = presets !== null;
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
                        : 'text-neutral-300 hover:bg-white/10 hover:text-white'
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

                  {/* Preset sub-menu (road, building, residential) */}
                  {hasPresets && isExpanded && presets && (
                    <div className="ml-2 mt-1 flex flex-col gap-1 border-l border-white/10 pl-2">
                      {presets.map((preset) => (
                        <button
                          key={preset.label}
                          onClick={() => {
                            onSelectTool(type, preset.properties);
                            setExpandedType(null);
                          }}
                          className="group flex items-center gap-2 whitespace-nowrap rounded-md px-2 py-1.5 text-xs text-neutral-300 transition-all hover:bg-white/10 hover:text-white"
                          title={`${preset.label} — ${preset.description}`}
                        >
                          <PresetIndicator preset={preset} color={config.color} />
                          <span className="font-medium">{preset.label}</span>
                          <PresetSummary preset={preset} />
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
              : 'text-neutral-300 hover:bg-white/10 hover:text-white'
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
  onShowGuide?: () => void;
}

export function SitePlannerToolbar({ onViewIn3D, onWalkThrough, onShowGuide }: SitePlannerToolbarProps) {
  const { activeSitePlannerTool, setActiveSitePlannerTool } = useViewerStore();
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

  const handleSelectTool = (type: SiteZoneType, properties?: SiteZoneProperties) => {
    if (!properties && activeSitePlannerTool === type) {
      setActiveSitePlannerTool(null);
    } else {
      setActiveSitePlannerTool(type, properties);
    }
    setOpenGroup(null);
  };

  return (
    <div className="flex w-full flex-col items-stretch gap-1.5 rounded-xl bg-primary-900/90 px-3 py-2 shadow-2xl backdrop-blur-sm sm:flex-row sm:items-center sm:justify-center sm:gap-2">
      {/* Zone tools row — wraps on mobile */}
      <div ref={groupsRef} className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        {/* Select / Move tool */}
        <button
          onClick={() => { setActiveSitePlannerTool(null); setOpenGroup(null); }}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all sm:py-1.5 ${
            activeSitePlannerTool === null
              ? 'bg-white/20 text-white ring-2 ring-white/40'
              : 'text-neutral-300 hover:bg-white/10 hover:text-white'
          }`}
          title="Select / Move zones"
        >
          <MousePointer size={14} />
          <span>Select</span>
        </button>

        <div className="mx-0.5 hidden h-6 w-px bg-white/20 sm:block" />

        <UndoRedoButtons />

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
        <button
          onClick={onWalkThrough}
          className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-700 sm:px-4 sm:py-1.5"
          title="Walk through the site at street level"
        >
          <Footprints size={14} />
          <span className="hidden sm:inline">Explore</span>
        </button>

        <button
          onClick={onViewIn3D}
          className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white hover:bg-primary-700 sm:px-4 sm:py-1.5"
        >
          <Eye size={14} />
          <span className="sm:hidden">3D</span>
          <span className="hidden sm:inline">View in 3D</span>
        </button>

        {onShowGuide && (
          <button
            onClick={onShowGuide}
            className="flex items-center gap-1 rounded-lg px-2 py-2 text-xs text-neutral-300 hover:bg-white/10 hover:text-white sm:py-1.5"
            title="Show quick-start guide"
          >
            <HelpCircle size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
