import { useState, useEffect, useMemo, useRef } from 'react';
import type { ReactNode } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Trash2, Sparkles, Loader2, X, RefreshCw, Building2, Route, TreePine, Droplets, ParkingCircle, MapPin, LayoutGrid, ChevronDown, ArrowDownToLine, Check, BookmarkPlus, Library, Box } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZone, SiteZoneProperties, Building, BoundaryAnalysisResponse, LayoutOption, PreviewHistoryEntry, ModelLibraryEntry, CustomStyleDomain } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { getShadeForArchetype, getCustomZoneShade } from '@/data/archetypeShadeMap';
import { CustomStyleEditor } from './CustomStyleEditor';
import { siteZonesApi, buildingsApi, getApiErrorMessage, modelLibraryApi, resolveApiFileUrl } from '@/services/api';
import { useViewerStore } from '@/store';
import { undoableActionMatchesZoneId, useUndoRedoStore } from '@/store/undoRedo';
import { LayoutPreviewPanel } from './LayoutPreviewPanel';
import { SiteIntelligencePanel } from './SiteIntelligencePanel';
import { BuildingModelViewer } from './BuildingModelViewer';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import { formatArea, polygonDimensionsMeters } from './mapEngine/geoUtils';
import { compileBoundaryCommunity3D } from '@/features/legoAssembly/communityCompiler';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import stickerMethodPilots from '@/data/stickerMethodPilots.json';
import neighborhoodParkV0StickerKit from '@/data/neighborhoodParkV0StickerKit.json';
import { ARCHETYPE_OWNED_PARK_KITS } from './globe/parkArchetypeOwnedKits';
import {
  BUILDING_AESTHETIC_CATEGORIES_V2,
  BUILDING_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_CATEGORIES_V2,
  ROADWAY_AESTHETIC_OPTIONS_V2,
  GREEN_SPACE_AESTHETIC_CATEGORIES_V2,
  GREEN_SPACE_AESTHETIC_OPTIONS_V2,
  PLAZA_AESTHETIC_CATEGORIES_V2,
  PLAZA_AESTHETIC_OPTIONS_V2,
  OPENSPACE_AESTHETIC_CATEGORIES_V2,
  OPENSPACE_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_PRESETS_V2,
  GREEN_SPACE_AESTHETIC_PRESETS_V2,
  PLAZA_AESTHETIC_PRESETS_V2,
  inferTransportModesFromProperties,
  applyModeDrivenRoadDefaults,
  normalizeTransportModes,
  getAllowedDevelopmentTypes,
  filterOptionsByDevelopmentType,
  type ArchetypeImage as CatalogArchetypeImage,
  type ArchetypeVariant as CatalogArchetypeVariant,
  type GenerationStyleInput as CatalogGenerationStyleInput,
  type StyleProfile as CatalogStyleProfile,
  type TransportModeKey as CatalogTransportModeKey,
} from './aestheticCatalog';

const SHOW_LEGACY_SITE_BOUNDARY_TOOLS =
  import.meta.env.VITE_ENABLE_LEGACY_SITE_BOUNDARY_TOOLS === 'true';

interface ZonePropertiesPanelProps {
  zone: SiteZone;
  onUpdate: (zoneId: string, data: { name?: string; color?: string; properties?: SiteZoneProperties }) => void;
  onDelete: (zoneId: string) => void;
  onClose: () => void;
  onAIGenerate?: (buildingId: string, initialPrompt?: string) => void;
  buildings?: Building[];
  allZones?: SiteZone[];
  onOpenBlockEditor?: (draftZone: SiteZone) => void;
}

type DevelopmentAestheticCategory = {
  id: string;
  label: string;
  description: string;
};

/** Snapshot of the custom-style fields used to detect edits worth auto-saving. */
const customStyleKeyOf = (p: SiteZoneProperties): string => JSON.stringify([
  p.custom_style_enabled,
  p.custom_style_prompt,
  p.custom_style_expanded_prompt,
  p.custom_style_expanded_edited,
  p.custom_style_expansion_hash,
  p.custom_style_attachments,
]);

/** Snapshot of the catalogue identity that must be persisted as one choice. */
const aestheticSelectionKeyOf = (p: SiteZoneProperties): string => JSON.stringify([
  p.development_subcategory,
  p.development_archetype_id,
  (p.development_selected_reference as { id?: string } | undefined)?.id,
  p.development_selected_variant_id,
  p.road_subcategory,
  p.road_archetype_id,
  (p.road_selected_reference as { id?: string } | undefined)?.id,
  p.road_selected_variant_id,
  p.green_space_subcategory,
  p.green_space_archetype_id,
  (p.green_space_selected_reference as { id?: string } | undefined)?.id,
  p.green_space_selected_variant_id,
  p.plaza_subcategory,
  p.plaza_archetype_id,
  (p.plaza_selected_reference as { id?: string } | undefined)?.id,
  p.plaza_selected_variant_id,
]);

type TransportModeKey = CatalogTransportModeKey;

type DevelopmentAestheticOption = {
  id: string;
  categoryId?: string;
  label: string;
  description: string;
  photoUrl: string;
  catalogCardImageUrl?: string;
  photoUrls?: string[];
  transportModes?: TransportModeKey[];
  generationTags?: string[];
  archetypeImages?: CatalogArchetypeImage[];
  styleProfile?: CatalogStyleProfile;
  generationStyleInput?: Partial<CatalogGenerationStyleInput>;
  minFloors?: number;
  maxFloors?: number;
  suggestedFloorHeight?: number;
  suggestedAreaSqm?: number;
  minAreaSqm?: number;
  maxAreaSqm?: number;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  minWidth_m?: number;
  maxWidth_m?: number;
  minDepth_m?: number;
  maxDepth_m?: number;
  aspectRatio?: string;
  variants?: CatalogArchetypeVariant[];
  standardSection?: {
    sectionSvgUrl: string | null;
    standardFamily: string;
    citation: string | null;
    rowM: number | null;
    targetSpeedKmh: number | null;
  };
};

const DEVELOPMENT_AESTHETIC_CATEGORIES: DevelopmentAestheticCategory[] = BUILDING_AESTHETIC_CATEGORIES_V2;
const DEVELOPMENT_AESTHETIC_OPTIONS: DevelopmentAestheticOption[] = BUILDING_AESTHETIC_OPTIONS_V2;

const ROADWAY_AESTHETIC_CATEGORIES: DevelopmentAestheticCategory[] = ROADWAY_AESTHETIC_CATEGORIES_V2;
const ROADWAY_AESTHETIC_OPTIONS: DevelopmentAestheticOption[] = ROADWAY_AESTHETIC_OPTIONS_V2;

const GREEN_SPACE_AESTHETIC_CATEGORIES: DevelopmentAestheticCategory[] = GREEN_SPACE_AESTHETIC_CATEGORIES_V2;
const GREEN_SPACE_AESTHETIC_OPTIONS: DevelopmentAestheticOption[] = GREEN_SPACE_AESTHETIC_OPTIONS_V2;

const PLAZA_AESTHETIC_CATEGORIES: DevelopmentAestheticCategory[] = PLAZA_AESTHETIC_CATEGORIES_V2;
const PLAZA_AESTHETIC_OPTIONS: DevelopmentAestheticOption[] = PLAZA_AESTHETIC_OPTIONS_V2;

// Combined parks + plazas — used by the unified "Parks / Plazas" picker.
const OPENSPACE_AESTHETIC_CATEGORIES: DevelopmentAestheticCategory[] = OPENSPACE_AESTHETIC_CATEGORIES_V2;
const OPENSPACE_AESTHETIC_OPTIONS: DevelopmentAestheticOption[] = OPENSPACE_AESTHETIC_OPTIONS_V2;
const STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE = new Map(
  stickerMethodPilots.buildings.map((entry) => [entry.archetypeId, entry.variantId]),
);
const STICKER_METHOD_BUILDING_IDS = new Set(STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE.keys());
const STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE = new Map(
  stickerMethodPilots.parks.map((entry) => [entry.archetypeId, entry.variantId]),
);
const STICKER_METHOD_PARK_IDS = new Set(STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE.keys());
const PARK_LEGO_READY_VARIANT_IDS = new Set([
  ...Object.values(ARCHETYPE_OWNED_PARK_KITS).map((kit) => kit.variantId),
  neighborhoodParkV0StickerKit.variantId,
]);

const ROADWAY_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = ROADWAY_AESTHETIC_PRESETS_V2;
const GREEN_SPACE_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = GREEN_SPACE_AESTHETIC_PRESETS_V2;
const PLAZA_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = PLAZA_AESTHETIC_PRESETS_V2;

const FRONT_DAY_VARIANT_ID = 'variant_0';

type BuildingWorkflowStep = 1 | 2 | 3 | 4;

const BUILDING_WORKFLOW_STEPS: Array<{ step: BuildingWorkflowStep; label: string }> = [
  { step: 1, label: 'Type' },
  { step: 2, label: 'Archetype' },
  { step: 3, label: 'Scale' },
  { step: 4, label: 'Details' },
];

function formatCompactArea(areaSqm: number): string {
  if (!Number.isFinite(areaSqm) || areaSqm <= 0) return '0 m²';
  return areaSqm >= 10000
    ? `${(areaSqm / 10000).toFixed(2)} ha`
    : `${Math.round(areaSqm).toLocaleString()} m²`;
}

function getAestheticAreaFit(
  option: DevelopmentAestheticOption | undefined,
  selectedVariantId: string | undefined,
  areaSqm: number,
) {
  if (!option || !Number.isFinite(areaSqm) || areaSqm <= 0) return null;

  const variants = Array.isArray(option.variants) ? option.variants : [];
  const selectedVariant = selectedVariantId
    ? variants.find((variant) => variant.id === selectedVariantId)
    : undefined;
  const selectedVariantFitCandidate = selectedVariant
    ? {
      ...option,
      ...selectedVariant,
      suggestedAreaSqm: selectedVariant.suggestedAreaSqm ?? option.suggestedAreaSqm,
      minAreaSqm: selectedVariant.minAreaSqm ?? option.minAreaSqm,
      maxAreaSqm: selectedVariant.maxAreaSqm ?? option.maxAreaSqm,
      suggestedWidth_m: selectedVariant.suggestedWidth_m ?? option.suggestedWidth_m,
      suggestedDepth_m: selectedVariant.suggestedDepth_m ?? option.suggestedDepth_m,
      minFloors: selectedVariant.minFloors ?? option.minFloors,
      maxFloors: selectedVariant.maxFloors ?? option.maxFloors,
    }
    : undefined;
  const candidates = selectedVariantFitCandidate ? [selectedVariantFitCandidate] : variants.concat(option);

  const rankedCandidates = candidates
    .map((candidate) => {
      const suggestedArea = candidate.suggestedAreaSqm;
      const minArea = candidate.minAreaSqm;
      const maxArea = candidate.maxAreaSqm;
      if (suggestedArea == null && minArea == null && maxArea == null) return null;

      const ratio = suggestedArea ? areaSqm / suggestedArea : null;
      const tooSmall = minArea != null ? areaSqm < minArea : ratio != null && ratio < 0.7;
      const tooLarge = maxArea != null ? areaSqm > maxArea : ratio != null && ratio > 1.5;
      const isGoodFit = !tooSmall && !tooLarge;
      const fitSort = ratio != null
        ? (isGoodFit ? 0 : 1) + Math.abs(Math.log(ratio))
        : isGoodFit ? 0.25 : 2;

      return {
        candidate,
        suggestedArea,
        minArea,
        maxArea,
        ratio,
        tooSmall,
        tooLarge,
        isGoodFit,
        fitSort,
      };
    })
    .filter(Boolean) as Array<{
      candidate: DevelopmentAestheticOption | CatalogArchetypeVariant;
      suggestedArea?: number;
      minArea?: number;
      maxArea?: number;
      ratio: number | null;
      tooSmall: boolean;
      tooLarge: boolean;
      isGoodFit: boolean;
      fitSort: number;
    }>;

  if (rankedCandidates.length === 0) return null;

  const best = rankedCandidates.sort((a, b) => a.fitSort - b.fitSort)[0];
  const candidate = best.candidate;
  const suggestedArea = best.suggestedArea;
  const minArea = best.minArea;
  const maxArea = best.maxArea;
  const ratio = best.ratio;
  const pct = ratio == null ? null : Math.round((ratio - 1) * 100);
  const message = best.isGoodFit
    ? pct == null ? 'Good fit' : `Good fit (${pct > 0 ? '+' : ''}${pct}%)`
    : best.tooSmall
      ? pct == null ? 'Small for this archetype' : `Small (${pct}%)`
      : pct == null ? 'Large for this archetype' : `Large (+${pct}%)`;
  const floorLabel = candidate.minFloors != null && candidate.maxFloors != null
    ? `${candidate.minFloors}-${candidate.maxFloors} floors`
    : undefined;
  const footprintLabel = candidate.suggestedWidth_m && candidate.suggestedDepth_m
    ? `${candidate.suggestedWidth_m}m x ${candidate.suggestedDepth_m}m`
    : undefined;

  return {
    isGoodFit: best.isGoodFit,
    fitSort: best.fitSort,
    message,
    zoneAreaLabel: formatCompactArea(areaSqm),
    suggestedAreaLabel: suggestedArea ? `~${formatCompactArea(suggestedArea)}` : undefined,
    typicalRangeLabel: minArea != null && maxArea != null
      ? `${formatCompactArea(minArea)} - ${formatCompactArea(maxArea)}`
      : undefined,
    floorLabel,
    footprintLabel,
  };
}

function PanelStep({
  step,
  title,
  children,
  muted = false,
  roomy = false,
}: {
  step: string;
  title: string;
  children: ReactNode;
  muted?: boolean;
  roomy?: boolean;
}) {
  return (
    <section className={`border-l-2 border-[#151515] ${roomy ? 'py-3 pl-3 pr-1.5' : 'py-2 pl-2.5 pr-1'} ${muted ? 'opacity-60' : ''}`}>
      <div className={`${roomy ? 'mb-2.5' : 'mb-2'} flex items-center gap-2`}>
        <span className={`flex shrink-0 items-center justify-center rounded-full border-2 border-[#151515] bg-[#c9ff3d] font-black text-[#151515] ${roomy ? 'h-6 w-6 text-[11px]' : 'h-5 w-5 text-[10px]'}`}>
          {step}
        </span>
        <h4 className={`${roomy ? 'text-[11px]' : 'text-[10px]'} font-black uppercase text-[#151515]`}>{title}</h4>
      </div>
      <div className={roomy ? 'space-y-3' : 'space-y-2'}>
        {children}
      </div>
    </section>
  );
}

function BuildingWorkflowStepper({
  activeStep,
  developmentSelected,
  onStepChange,
}: {
  activeStep: BuildingWorkflowStep;
  developmentSelected: boolean;
  onStepChange: (step: BuildingWorkflowStep) => void;
}) {
  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white/80 p-2 shadow-[3px_3px_0_0_rgba(21,21,21,0.16)]">
      <div className="grid grid-cols-4 gap-1">
        {BUILDING_WORKFLOW_STEPS.map(({ step, label }) => {
          const disabled = step > 1 && !developmentSelected;
          const active = activeStep === step;
          return (
            <button
              key={step}
              type="button"
              disabled={disabled}
              onClick={() => onStepChange(step)}
              className={`rounded-md border px-1 py-1 text-[9px] font-black uppercase transition ${
                active
                  ? 'border-[#151515] bg-[#c9ff3d] text-[#151515] shadow-[2px_2px_0_0_#151515]'
                  : 'border-[#151515]/20 bg-[#fff9ec] text-[#151515]/55 hover:border-[#151515]/50'
              } disabled:cursor-not-allowed disabled:opacity-35`}
            >
              <span className="block text-[10px] leading-none">{step}</span>
              <span className="block truncate">{label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function BuildingWorkflowPager({
  activeStep,
  developmentSelected,
  onStepChange,
}: {
  activeStep: BuildingWorkflowStep;
  developmentSelected: boolean;
  onStepChange: (step: BuildingWorkflowStep) => void;
}) {
  const previousStep = Math.max(1, activeStep - 1) as BuildingWorkflowStep;
  const nextStep = Math.min(4, activeStep + 1) as BuildingWorkflowStep;
  const nextDisabled = activeStep === 4 || (nextStep > 1 && !developmentSelected);

  return (
    <div className="flex items-center justify-between gap-2 pt-1">
      <button
        type="button"
        disabled={activeStep === 1}
        onClick={() => onStepChange(previousStep)}
        className="rounded-full border border-[#151515]/20 bg-white px-3 py-1 text-[10px] font-black uppercase text-[#151515]/65 hover:border-[#151515]/50 disabled:cursor-not-allowed disabled:opacity-35"
      >
        Back
      </button>
      <span className="text-[10px] font-black uppercase text-[#151515]/40">
        Step {activeStep} of 4
      </span>
      <button
        type="button"
        disabled={nextDisabled}
        onClick={() => onStepChange(nextStep)}
        className="rounded-full border-2 border-[#151515] bg-[#151515] px-3 py-1 text-[10px] font-black uppercase text-white shadow-[2px_2px_0_0_#c9ff3d] hover:bg-[#2b2b2b] disabled:cursor-not-allowed disabled:opacity-35"
      >
        Next
      </button>
    </div>
  );
}

const LEGACY_CATEGORY_ALIASES: Record<'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic', Record<string, string>> = {
  development_aesthetic: {
    historic: 'historical',
    contemporary: 'contemporary_urban',
    glass_modern: 'glass_tower_modern',
  },
  road_aesthetic: {
    transportation: 'complete_streets',
    transit_corridor: 'transit_priority',
    complete_street: 'complete_streets',
    walkable_street: 'historic_walkways',
  },
  green_space_aesthetic: {
    historic_landscape: 'landscape_parks',
    historic_landscape_park: 'landscape_parks',
    historic_gardens: 'landscape_parks',
    english_landscape: 'landscape_parks',
    ecological_park: 'ecological_resilience',
    ecological_landscape: 'ecological_resilience',
    neighborhood_park: 'neighborhood_public_realm',
    waterfront: 'waterfront_spaces',
  },
  plaza_aesthetic: {
    civic_square: 'civic_plazas',
    urban_square: 'civic_plazas',
    event_plaza: 'social_event_spaces',
    festival_space: 'social_event_spaces',
  },
};

function normalizeLegacyCategoryValue(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[\s/-]+/g, '_')
    .replace(/[^a-z0-9_]/g, '');
}

function normalizeAestheticCategory(
  key: 'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic',
  value: string | undefined,
): string | undefined {
  if (!value) return undefined;

  const normalized = normalizeLegacyCategoryValue(value);
  const aliases = LEGACY_CATEGORY_ALIASES[key] || {};
  return aliases[normalized] || value;
}

function getFrontDayArchetypeImage(images: CatalogArchetypeImage[]): CatalogArchetypeImage | undefined {
  return images.find((image) => image.id.endsWith(`_${FRONT_DAY_VARIANT_ID}`));
}

export function ZonePropertiesPanel({ zone, onUpdate, onDelete, onClose, onAIGenerate, buildings, allZones, onOpenBlockEditor }: ZonePropertiesPanelProps) {
  const config = ZONE_TYPE_CONFIG[zone.zone_type];
  const osmContext = useViewerStore((s) => s.osmContext);
  const layoutPreview = useViewerStore((s) => s.layoutPreview);
  const undoRedoHistoryVersion = useUndoRedoStore((s) => s.historyVersion);
  const lastAppliedUndoRedoAction = useUndoRedoStore((s) => s.lastAppliedAction);
  const [name, setName] = useState(zone.name || '');
  const [props, setProps] = useState<SiteZoneProperties>(zone.properties || {});
  const panelRef = useRef<HTMLDivElement>(null);
  const lastSyncedUndoRedoVersionRef = useRef(0);
  // Custom-style auto-save machinery. handleSaveRef always points at the
  // latest render's handleSave so a debounce timer never persists stale props.
  const handleSaveRef = useRef<(closeAfterSave?: boolean) => void>(() => {});
  const customStyleSaveTimerRef = useRef<number | null>(null);
  const customStyleSavePendingRef = useRef(false);
  const prevCustomStyleKeyRef = useRef<string | undefined>(undefined);
  const prevAestheticSelectionKeyRef = useRef<string | undefined>(undefined);
  const usesBuildingWorkflow = zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area';
  const [activeBuildingStep, setActiveBuildingStep] = useState<BuildingWorkflowStep>(1);

  // Scroll panel to top when zone changes (e.g. after "Preview All" switches to buildable zone)
  useEffect(() => {
    panelRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [zone.id]);

  // Sync when zone changes ? only on zone.id since key={zone.id} forces remount.
  // Do NOT depend on zone.properties ? React Query background refetches would
  // overwrite the user's unsaved edits (e.g. reference images added but not yet saved).
  useEffect(() => {
    setName(zone.name || '');
    setProps(zone.properties || {});
    setActiveBuildingStep(1);
  }, [zone.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (usesBuildingWorkflow && !props.development_type && activeBuildingStep > 1) {
      setActiveBuildingStep(1);
    }
  }, [activeBuildingStep, props.development_type, usesBuildingWorkflow]);

  useEffect(() => {
    if (undoRedoHistoryVersion === 0) return;
    if (lastSyncedUndoRedoVersionRef.current === undoRedoHistoryVersion) return;
    lastSyncedUndoRedoVersionRef.current = undoRedoHistoryVersion;
    if (lastAppliedUndoRedoAction?.label !== 'Update zone') return;
    if (!undoableActionMatchesZoneId(lastAppliedUndoRedoAction, zone.id)) return;
    setName(zone.name || '');
    setProps(zone.properties || {});
    // Undo/redo restored these props — don't let the custom-style auto-save
    // treat the restore as a user edit (it would re-commit the undone state
    // and wipe the redo stack).
    prevCustomStyleKeyRef.current = customStyleKeyOf(zone.properties || {});
    prevAestheticSelectionKeyRef.current = aestheticSelectionKeyOf(zone.properties || {});
  }, [lastAppliedUndoRedoAction, undoRedoHistoryVersion, zone.id, zone.name, zone.properties]);

  const handleSave = (closeAfterSave = false) => {
    // Unsaved zones carry an optimistic temp- id while the create round-trip
    // is in flight; every zone endpoint UUID-validates its path and 422s on
    // them. Edits stay in local state — the panel remounts with the real id
    // once the create lands (key={zone.id}).
    if (!isPersistedZoneId(zone.id)) {
      if (closeAfterSave) {
        // Explicit "Save Changes" click — tell the user instead of silently
        // dropping the save; keep the panel open so edits stay visible.
        toast.error('Zone is still saving — try again in a moment');
      } else {
        console.debug(`[ZoneProps] Save skipped — zone ${zone.id} not persisted yet`);
      }
      return;
    }

    // Custom-style zone: color comes from the per-zone custom palette, not an archetype
    if (props.custom_style_enabled) {
      const customDomain = (props.custom_style_domain as CustomStyleDomain)
        || (zone.zone_type === 'road' ? 'street'
          : zone.zone_type === 'green_space' || zone.zone_type === 'parking' ? 'open_space'
            : 'building');
      // Colors already used by other zones — avoids two custom zones sharing
      // a mask color (which would mis-route their prompts/photos in renders)
      const takenColors = (allZones || [])
        .filter((z) => z.id !== zone.id && z.color)
        .map((z) => z.color);
      const customShade = getCustomZoneShade(customDomain, zone.id, takenColors);
      console.log(`[ZoneProps] Save (custom style) — domain="${customDomain}", shade="${customShade}"`);
      onUpdate(zone.id, {
        name: name || undefined,
        color: customShade,
        properties: props,
      });
      if (closeAfterSave) onClose();
      return;
    }

    // Resolve shade color from assigned archetype.
    // Check variant-specific shadeId first, then try subcategory ID (option-level,
    // e.g. "parisian_midrise_block") which directly matches shade map keys, then
    // fall back to archetype_id (image-level) which uses prefix matching.
    const variantShadeId = (props.development_variant_shade_id as string)
      || (props.road_variant_shade_id as string)
      || (props.green_space_variant_shade_id as string)
      || (props.plaza_variant_shade_id as string);
    const archetypeId = (props.development_subcategory as string)
      || (props.road_subcategory as string)
      || (props.green_space_subcategory as string)
      || (props.plaza_subcategory as string)
      || (props.development_archetype_id as string)
      || (props.road_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || (props.plaza_archetype_id as string);
    // Try variant palette.primary color first (most specific),
    // then variant shadeId, then archetype-level shade map
    const variantPalettePrimary = (props.development_palette as any)?.primary
      || (props.road_palette as any)?.primary
      || (props.green_space_palette as any)?.primary
      || (props.plaza_palette as any)?.primary;
    const shadeColor = variantPalettePrimary
      || (variantShadeId ? getShadeForArchetype(variantShadeId) : undefined)
      || (archetypeId ? getShadeForArchetype(archetypeId) : undefined);
    console.debug(`[ZoneProps] Save — variantPalette="${variantPalettePrimary}", variantShade="${variantShadeId}", archetypeId="${archetypeId}", shade="${shadeColor}"`);

    onUpdate(zone.id, {
      name: name || undefined,
      color: shadeColor && shadeColor !== '#888888' ? shadeColor : undefined,
      properties: props,
    });

    if (closeAfterSave) {
      onClose();
    }
  };

  // Keep the ref pointing at the latest handleSave (fresh props/name closure)
  handleSaveRef.current = handleSave;

  const handleOpenBlockEditor = () => {
    onOpenBlockEditor?.({
      ...zone,
      name,
      properties: { ...props },
    });
  };

  // Auto-save the complete catalogue identity (parent, reference and design
  // variant). In particular, variant -> Automatic must save even when the
  // parent archetype itself did not change.
  const aestheticSelectionKey = aestheticSelectionKeyOf(props);
  useEffect(() => {
    // Skip initial mount and zone resets. The latest-save ref is updated during
    // render, so this effect always persists the fully computed next props.
    if (prevAestheticSelectionKeyRef.current === undefined) {
      prevAestheticSelectionKeyRef.current = aestheticSelectionKey;
      return;
    }
    if (aestheticSelectionKey === prevAestheticSelectionKeyRef.current) return;
    prevAestheticSelectionKeyRef.current = aestheticSelectionKey;
    handleSaveRef.current();
  }, [aestheticSelectionKey]);

  // Auto-save custom-style edits (debounced — the prompt textarea fires on every keystroke)
  useEffect(() => {
    const key = customStyleKeyOf(props);
    // Skip initial mount (panel remounts per zone via key={zone.id})
    if (prevCustomStyleKeyRef.current === undefined) {
      prevCustomStyleKeyRef.current = key;
      return;
    }
    if (key === prevCustomStyleKeyRef.current) return;
    prevCustomStyleKeyRef.current = key;

    if (customStyleSaveTimerRef.current) window.clearTimeout(customStyleSaveTimerRef.current);
    customStyleSavePendingRef.current = true;
    customStyleSaveTimerRef.current = window.setTimeout(() => {
      customStyleSavePendingRef.current = false;
      handleSaveRef.current();
    }, 800);
  }, [props.custom_style_enabled, props.custom_style_prompt, props.custom_style_expanded_prompt, props.custom_style_expanded_edited, props.custom_style_expansion_hash, props.custom_style_attachments]); // eslint-disable-line react-hooks/exhaustive-deps

  // FLUSH (never discard) a pending custom-style save on unmount — the panel
  // unmounts on zone switch/close, and dropping the timer would silently lose
  // everything typed in the last 800ms (or the whole setup if never idle).
  useEffect(() => () => {
    if (customStyleSaveTimerRef.current) window.clearTimeout(customStyleSaveTimerRef.current);
    if (customStyleSavePendingRef.current) {
      customStyleSavePendingRef.current = false;
      handleSaveRef.current();
    }
  }, []);

  const isRemoteReferenceImage = (value: string): boolean => /^https?:\/\//i.test(value);

  const DOMAIN_STYLE_FIELD_PREFIX: Record<'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic', string> = {
  development_aesthetic: 'development',
  road_aesthetic: 'road',
  green_space_aesthetic: 'green_space',
  plaza_aesthetic: 'plaza',
};

const DOMAIN_STYLE_INPUT_KEY: Record<'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic', string> = {
  development_aesthetic: 'building',
  road_aesthetic: 'streets_paths',
  green_space_aesthetic: 'parks',
  plaza_aesthetic: 'plazas',
};

const DOMAIN_GENERATION_DOMAIN: Record<'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic', CatalogGenerationStyleInput['domain']> = {
  development_aesthetic: 'building',
  road_aesthetic: 'street_pathway',
  green_space_aesthetic: 'park_plaza',
  plaza_aesthetic: 'park_plaza',
};

const clearDomainStyleFields = (
  target: SiteZoneProperties,
  key: 'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic',
): void => {
  const prefix = DOMAIN_STYLE_FIELD_PREFIX[key];
  target[`${prefix}_subcategory`] = undefined;
  target[`${prefix}_selected_reference`] = undefined;
  target[`${prefix}_archetype_id`] = undefined;
  target[`${prefix}_archetype_label`] = undefined;
  target[`${prefix}_archetype_image`] = undefined;
  target[`${prefix}_archetype_images`] = undefined;
  target[`${prefix}_archetype_prompt`] = undefined;
  target[`${prefix}_generation_tags`] = undefined;
  target[`${prefix}_style_profile`] = undefined;
  target[`${prefix}_selected_variant_id`] = undefined;
  target[`${prefix}_variant_shade_id`] = undefined;
  target[`${prefix}_facade_detail`] = undefined;
  target[`${prefix}_roof_detail`] = undefined;
  target[`${prefix}_palette`] = undefined;

  if (key === 'development_aesthetic') {
    target.generation_style_input = undefined;
  }

  const domainInputKey = DOMAIN_STYLE_INPUT_KEY[key];
  const currentGenerationMap = target.generation_style_inputs;
  if (currentGenerationMap && typeof currentGenerationMap === 'object' && !Array.isArray(currentGenerationMap)) {
    const nextMap = { ...(currentGenerationMap as Record<string, unknown>) };
    delete nextMap[domainInputKey];
    target.generation_style_inputs = Object.keys(nextMap).length > 0 ? nextMap : undefined;
  }

  if (key === 'road_aesthetic') {
    target.road_standard_section_svg_url = undefined;
    target.road_standard_family = undefined;
    target.road_standard_citation = undefined;
    target.road_standard_row_m = undefined;
    target.road_standard_target_speed_kmh = undefined;
  }
};

const buildAestheticSelectionProps = (
  current: SiteZoneProperties,
  key: 'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic',
  next: string | undefined,
  options: DevelopmentAestheticOption[],
  presets?: Record<string, Partial<SiteZoneProperties>>,
  selectedArchetypeImageId?: string,
  selectedVariantId?: string,
): SiteZoneProperties => {
  const nextProps: SiteZoneProperties = { ...current, [key]: next || undefined };
  const existing = Array.isArray(current.reference_images) ? (current.reference_images as string[]) : [];
  const optionImages = options.map((option) => option.photoUrl);
  const selectedOption = options.find((option) => option.id === next);
  const imageUrl = selectedOption?.photoUrl;

  if (next && presets?.[next]) {
    Object.assign(nextProps, presets[next]);
  }

  if (selectedOption) {
    // Picking a catalog archetype turns off custom-style mode (data is retained
    // so toggling back to Custom restores the user's prompt and uploads)
    nextProps.custom_style_enabled = false;

    const stylePrefix = DOMAIN_STYLE_FIELD_PREFIX[key];
    const inputMapKey = DOMAIN_STYLE_INPUT_KEY[key];
    const generationDomain = DOMAIN_GENERATION_DOMAIN[key];
    const archetypeImages = Array.isArray(selectedOption.archetypeImages) ? selectedOption.archetypeImages : [];
    const frontDayArchetype = selectedOption.standardSection
      ? archetypeImages[0]
      : getFrontDayArchetypeImage(archetypeImages);
    const resolvedArchetype = archetypeImages.find((image) => image.id === selectedArchetypeImageId) || frontDayArchetype || archetypeImages[0];
    const resolvedArchetypeImage = resolvedArchetype?.imageUrl || selectedOption.photoUrl;

    const categoriesForKey = key === 'development_aesthetic'
      ? DEVELOPMENT_AESTHETIC_CATEGORIES
      : key === 'road_aesthetic'
        ? ROADWAY_AESTHETIC_CATEGORIES
        : key === 'green_space_aesthetic'
          ? GREEN_SPACE_AESTHETIC_CATEGORIES
          : PLAZA_AESTHETIC_CATEGORIES;

    const resolvedCategoryLabel = categoriesForKey.find((category) => category.id === selectedOption.categoryId)?.label;
    const resolvedStyleProfile = selectedOption.styleProfile || selectedOption.generationStyleInput?.styleProfile;
    const resolvedGenerationTags = Array.isArray(selectedOption.generationTags)
      ? selectedOption.generationTags
      : (Array.isArray(selectedOption.generationStyleInput?.generationTags) ? selectedOption.generationStyleInput?.generationTags : []);

    const referenceArchetypeId = resolvedArchetype?.id || selectedOption.id;
    // Public Realm LEGO compiles against the catalog's parent archetype ID
    // (for example `main_street_complete`), while the image picker resolves a
    // camera/lighting reference ID (for example
    // `main_street_complete_variant_0`). Keep those identities separate so a
    // manual road/park selection remains both compilable and visually traced.
    // Building selection intentionally retains its existing image-qualified
    // archetype ID contract.
    const archetypeId = key === 'development_aesthetic'
      ? referenceArchetypeId
      : selectedOption.id;
    const archetypeLabel = resolvedArchetype?.label || selectedOption.label;

    nextProps[`${stylePrefix}_subcategory`] = selectedOption.id;
    nextProps[`${stylePrefix}_aesthetic_category`] = selectedOption.categoryId || nextProps[`${stylePrefix}_aesthetic_category`];
    nextProps[`${stylePrefix}_archetype_id`] = archetypeId;
    nextProps[`${stylePrefix}_archetype_label`] = archetypeLabel;
    nextProps[`${stylePrefix}_archetype_image`] = resolvedArchetypeImage;
    nextProps[`${stylePrefix}_archetype_prompt`] = resolvedArchetype?.prompt;
    nextProps[`${stylePrefix}_generation_tags`] = resolvedGenerationTags;
    nextProps[`${stylePrefix}_archetype_images`] = archetypeImages.map((image) => ({
      id: image.id,
      label: image.label,
      description: image.description,
      camera: image.camera,
      lighting: image.lighting,
      imagePath: image.imagePath,
      imageUrl: image.imageUrl,
      prompt: image.prompt,
    }));

    nextProps[`${stylePrefix}_selected_reference`] = {
      id: referenceArchetypeId,
      label: archetypeLabel,
      imageUrl: resolvedArchetypeImage,
      imagePath: resolvedArchetype?.imagePath,
      description: resolvedArchetype?.description || selectedOption.description,
      camera: resolvedArchetype?.camera,
      lighting: resolvedArchetype?.lighting,
      prompt: resolvedArchetype?.prompt,
    };

    if (key === 'road_aesthetic') {
      nextProps.road_standard_section_svg_url = selectedOption.standardSection?.sectionSvgUrl;
      nextProps.road_standard_family = selectedOption.standardSection?.standardFamily;
      nextProps.road_standard_citation = selectedOption.standardSection?.citation;
      nextProps.road_standard_row_m = selectedOption.standardSection?.rowM;
      nextProps.road_standard_target_speed_kmh = selectedOption.standardSection?.targetSpeedKmh;
    }

    if (resolvedStyleProfile) {
      nextProps[`${stylePrefix}_style_profile`] = resolvedStyleProfile;
    }

    const baseGenerationInput = selectedOption.generationStyleInput || {};
    const generationStyleInput: Partial<CatalogGenerationStyleInput> = {
      ...baseGenerationInput,
      domain: generationDomain,
      developmentType: key === 'development_aesthetic' && typeof current.development_type === 'string'
        ? (current.development_type as string)
        : baseGenerationInput.developmentType,
      buildingSubcategory: key === 'development_aesthetic'
        ? selectedOption.id
        : (baseGenerationInput.buildingSubcategory || selectedOption.id),
      subtype: key === 'green_space_aesthetic'
        ? 'park'
        : key === 'plaza_aesthetic'
          ? 'plaza'
          : (baseGenerationInput.subtype || selectedOption.id),
      aestheticCategoryId: selectedOption.categoryId,
      aestheticCategoryLabel: resolvedCategoryLabel,
      archetypeId: referenceArchetypeId,
      archetypeLabel,
      archetypeImageUrl: resolvedArchetypeImage,
      archetypeImagePath: resolvedArchetype?.imagePath || baseGenerationInput.archetypeImagePath,
      archetypeImageIds: archetypeImages.map((image) => image.id),
      generationTags: resolvedGenerationTags,
      imagePrompt: resolvedArchetype?.prompt || baseGenerationInput.imagePrompt,
      styleProfile: (resolvedStyleProfile || baseGenerationInput.styleProfile) as CatalogStyleProfile,
      downstreamHints: {
        sceneDressing: resolvedGenerationTags,
        materialDirection: Array.isArray((resolvedStyleProfile as CatalogStyleProfile | undefined)?.materials)
          ? ((resolvedStyleProfile as CatalogStyleProfile).materials as string[])
          : [],
        reuseKeys: [
          selectedOption.id,
          selectedOption.categoryId,
          key,
          referenceArchetypeId,
        ].filter(Boolean) as string[],
      },
    };

    if (key === 'development_aesthetic') {
      nextProps.generation_style_input = generationStyleInput;
    }

    const generationInputs = current.generation_style_inputs;
    const generationInputsMap = generationInputs && typeof generationInputs === 'object' && !Array.isArray(generationInputs)
      ? { ...(generationInputs as Record<string, unknown>) }
      : {};
    generationInputsMap[inputMapKey] = generationStyleInput;
    nextProps.generation_style_inputs = generationInputsMap;
  } else {
    clearDomainStyleFields(nextProps, key);
  }

  if (imageUrl && isRemoteReferenceImage(imageUrl)) {
    const deduped = existing.filter((img) => img && img !== imageUrl);
    nextProps.reference_images = [imageUrl, ...deduped].slice(0, 3);
  } else if (!imageUrl) {
    const cleaned = existing.filter((img) => !optionImages.includes(img));
    nextProps.reference_images = cleaned.length > 0 ? cleaned : undefined;
  }

  // Auto-populate descriptive text from archetype metadata
  // Only if the user hasn't manually customized it (or it was auto-generated before)
  if (selectedOption) {
    const sp = selectedOption.styleProfile || (selectedOption.generationStyleInput?.styleProfile as Record<string, unknown>) || {};
    const fd = (selectedOption as Record<string, unknown>).facadeDetail as Record<string, string> | undefined;
    const rd = (selectedOption as Record<string, unknown>).roofDetail as Record<string, string> | undefined;
    const descParts: string[] = [];

    if (key === 'development_aesthetic') {
      // Building: facade, materials, roof
      if (fd?.primaryMaterial) descParts.push(fd.primaryMaterial);
      if (fd?.groundFloor) descParts.push(`Ground floor: ${fd.groundFloor}`);
      if (fd?.upperFloors) descParts.push(`Upper floors: ${fd.upperFloors}`);
      if (rd?.form) descParts.push(`Roof: ${rd.form}`);
      if (rd?.material) descParts.push(rd.material);
      if (sp.materials) descParts.push(`Materials: ${Array.isArray(sp.materials) ? (sp.materials as string[]).join(', ') : sp.materials}`);
      if ((sp as Record<string, unknown>).heightTendency) descParts.push(String((sp as Record<string, unknown>).heightTendency));
    } else if (key === 'road_aesthetic') {
      // Road: corridor character, surface, planting
      if ((sp as Record<string, unknown>).corridorCharacter) descParts.push(String((sp as Record<string, unknown>).corridorCharacter));
      if ((sp as Record<string, unknown>).surfaceType) descParts.push(`Surface: ${(sp as Record<string, unknown>).surfaceType}`);
      if ((sp as Record<string, unknown>).plantingCharacter) descParts.push(String((sp as Record<string, unknown>).plantingCharacter));
      if ((sp as Record<string, unknown>).edgeConditions) descParts.push(`Edges: ${(sp as Record<string, unknown>).edgeConditions}`);
      if ((sp as Record<string, unknown>).publicRealm) descParts.push(String((sp as Record<string, unknown>).publicRealm));
    } else if (key === 'green_space_aesthetic' || key === 'plaza_aesthetic') {
      // Park/plaza: character, planting, public realm
      if ((sp as Record<string, unknown>).corridorCharacter) descParts.push(String((sp as Record<string, unknown>).corridorCharacter));
      if ((sp as Record<string, unknown>).plantingCharacter) descParts.push(String((sp as Record<string, unknown>).plantingCharacter));
      if ((sp as Record<string, unknown>).publicRealm) descParts.push(String((sp as Record<string, unknown>).publicRealm));
      if (sp.materials) descParts.push(`Materials: ${Array.isArray(sp.materials) ? (sp.materials as string[]).join(', ') : sp.materials}`);
    }

    // Fall back to the archetype description if no specific fields found
    if (descParts.length === 0 && selectedOption.description) {
      descParts.push(selectedOption.description);
    }

    if (descParts.length > 0) {
      nextProps.description_text = descParts.join('. ') + '.';
    }

    // Apply variant overrides when a design variant is selected
    const vPrefix = DOMAIN_STYLE_FIELD_PREFIX[key];
    const variants = Array.isArray(selectedOption.variants) ? selectedOption.variants : [];
    const selectedVariant = selectedVariantId ? variants.find((v) => v.id === selectedVariantId) : undefined;
    if (selectedVariant) {
      nextProps[`${vPrefix}_selected_variant_id`] = selectedVariant.id;
      if (selectedVariant.renderPrompt) {
        nextProps[`${vPrefix}_archetype_prompt`] = selectedVariant.renderPrompt;
      }
      if (selectedVariant.facadeDetail) {
        nextProps[`${vPrefix}_facade_detail`] = selectedVariant.facadeDetail;
      }
      if (selectedVariant.roofDetail) {
        nextProps[`${vPrefix}_roof_detail`] = selectedVariant.roofDetail;
      }
      if (selectedVariant.shadeId) {
        nextProps[`${vPrefix}_variant_shade_id`] = selectedVariant.shadeId;
      }
      if (selectedVariant.palette) {
        nextProps[`${vPrefix}_palette`] = selectedVariant.palette;
      }
      if (selectedVariant.description) {
        nextProps.description_text = selectedVariant.description;
      }
    } else {
      nextProps[`${vPrefix}_selected_variant_id`] = undefined;
      nextProps[`${vPrefix}_variant_shade_id`] = undefined;
      nextProps[`${vPrefix}_facade_detail`] = undefined;
      nextProps[`${vPrefix}_roof_detail`] = undefined;
      nextProps[`${vPrefix}_palette`] = undefined;
    }
  }

  return nextProps;
};

const resolveOptionCategory = (
    options: DevelopmentAestheticOption[],
    aestheticId?: string,
  ): string | undefined => {
    if (!aestheticId) return undefined;
    return options.find((o) => o.id === aestheticId)?.categoryId;
  };

  const selectedRoadAestheticCategory = normalizeAestheticCategory(
    'road_aesthetic',
    (props.road_aesthetic_category as string)
      || resolveOptionCategory(ROADWAY_AESTHETIC_OPTIONS, (props.road_aesthetic as string) || undefined),
  );

  const selectedGreenSpaceCategory = normalizeAestheticCategory(
    'green_space_aesthetic',
    (props.green_space_aesthetic_category as string)
      || resolveOptionCategory(GREEN_SPACE_AESTHETIC_OPTIONS, (props.green_space_aesthetic as string) || undefined),
  );

  const selectedPlazaCategory = normalizeAestheticCategory(
    'plaza_aesthetic',
    (props.plaza_aesthetic_category as string)
      || resolveOptionCategory(PLAZA_AESTHETIC_OPTIONS, (props.plaza_aesthetic as string) || undefined),
  );

  const selectedRoadReferenceId = ((props.road_selected_reference as { id?: string } | undefined)?.id) || (props.road_archetype_id as string) || undefined;
  const selectedGreenSpaceReferenceId = ((props.green_space_selected_reference as { id?: string } | undefined)?.id) || (props.green_space_archetype_id as string) || undefined;
  const selectedPlazaReferenceId = ((props.plaza_selected_reference as { id?: string } | undefined)?.id) || (props.plaza_archetype_id as string) || undefined;

  // Unified Parks / Plazas selection — reads from whichever prefix has data
  const selectedOpenSpaceAesthetic = (props.green_space_aesthetic as string) || (props.plaza_aesthetic as string) || undefined;
  const selectedOpenSpaceCategory = selectedGreenSpaceCategory || selectedPlazaCategory;
  const selectedOpenSpaceReferenceId = selectedGreenSpaceReferenceId || selectedPlazaReferenceId;
  const selectedOpenSpaceVariantId = (props.green_space_selected_variant_id as string) || (props.plaza_selected_variant_id as string) || undefined;

  const applyBuildingDevelopmentType = (nextDevelopmentType: string | undefined) => {
    setProps((p) => {
      const nextProps: SiteZoneProperties = {
        ...p,
        development_type: nextDevelopmentType || undefined,
      };

      const currentGenerationInput = p.generation_style_input as Record<string, unknown> | undefined;
      if (currentGenerationInput && typeof currentGenerationInput === 'object') {
        nextProps.generation_style_input = {
          ...currentGenerationInput,
          developmentType: nextDevelopmentType || undefined,
        };
      }

      const generationInputs = p.generation_style_inputs;
      if (generationInputs && typeof generationInputs === 'object' && !Array.isArray(generationInputs)) {
        const nextGenerationInputs = { ...(generationInputs as Record<string, unknown>) };
        const buildingInput = nextGenerationInputs.building;
        if (buildingInput && typeof buildingInput === 'object') {
          nextGenerationInputs.building = {
            ...(buildingInput as Record<string, unknown>),
            developmentType: nextDevelopmentType || undefined,
          };
        }
        nextProps.generation_style_inputs = nextGenerationInputs;
      }

      return nextProps;
    });
  };

  const applyBuildingAesthetic = (next: string | undefined, selectedArchetypeImageId?: string, variantId?: string) => {
    setProps((p) => {
      const nextProps = buildAestheticSelectionProps(
        p,
        'development_aesthetic',
        next,
        DEVELOPMENT_AESTHETIC_OPTIONS,
        undefined,
        selectedArchetypeImageId,
        variantId,
      );
      const selectedOption = DEVELOPMENT_AESTHETIC_OPTIONS.find((o) => o.id === next);
      if (selectedOption?.categoryId) {
        nextProps.development_aesthetic_category = selectedOption.categoryId;
      }
      // Auto-populate floors from variant or archetype suggestion.
      // Variant-level specs take priority over archetype-level.
      // When switching variants, always update floors/height to match the new variant.
      const selectedVariant = variantId && selectedOption?.variants
        ? selectedOption.variants.find((v) => v.id === variantId)
        : undefined;
      const variantMinFloors = selectedVariant?.minFloors;
      const variantMaxFloors = selectedVariant?.maxFloors;
      const variantFloorHeight = selectedVariant?.suggestedFloorHeight;
      const hasVariantOverride = variantMinFloors != null && variantMaxFloors != null;

      const archetypeFloorHeight = selectedOption?.suggestedFloorHeight;
      if (hasVariantOverride) {
        // Variant has per-variant floor specs — always apply when switching variants.
        // Floor-height precedence: variant override > existing zone value > archetype typology default > 3m fallback.
        const suggestedFloors = Math.floor((variantMinFloors + variantMaxFloors) / 2);
        nextProps.floors = suggestedFloors;
        const floorH = variantFloorHeight || (p.floor_height as number) || archetypeFloorHeight || 3;
        nextProps.floor_height = floorH;
        nextProps.height = Math.round(suggestedFloors * floorH * 10) / 10;
      } else if (selectedOption?.minFloors && selectedOption?.maxFloors && !p.floors) {
        // Fallback to archetype-level floors only when floors haven't been set
        const suggestedFloors = Math.floor((selectedOption.minFloors + selectedOption.maxFloors) / 2);
        nextProps.floors = suggestedFloors;
        const floorH = (p.floor_height as number) || archetypeFloorHeight || 3;
        nextProps.floor_height = floorH;
        nextProps.height = Math.round(suggestedFloors * floorH * 10) / 10;
      }
      return nextProps;
    });
  };

  // Toggle custom-style mode for a domain. Nothing is cleared in either
  // direction — the render pipelines give the custom prompt/photos precedence
  // over any archetype fields whenever custom_style_enabled is true, so the
  // user's archetype pick, description text, and custom setup all survive
  // toggling back and forth.
  const setCustomStyleEnabled = (enabled: boolean, customDomain: CustomStyleDomain) => {
    setProps((p) => ({
      ...p,
      custom_style_enabled: enabled || undefined,
      custom_style_domain: customDomain,
    }));
  };

  // Segmented "Catalog / Custom" toggle shown above each archetype picker
  const renderCustomStyleToggle = (customDomain: CustomStyleDomain) => (
    <div className="mb-1.5 grid grid-cols-2 gap-1 rounded-lg border-2 border-[#151515]/15 bg-[#151515]/[0.03] p-0.5">
      {([['catalog', 'Catalog'], ['custom', 'Custom']] as const).map(([mode, label]) => {
        const active = props.custom_style_enabled ? mode === 'custom' : mode === 'catalog';
        return (
          <button
            key={mode}
            type="button"
            onClick={() => setCustomStyleEnabled(mode === 'custom', customDomain)}
            className={`rounded-md px-2 py-1 text-[10px] font-black uppercase transition-colors ${
              active
                ? 'bg-[#151515] text-[#c9ff3d]'
                : 'text-[#151515]/50 hover:text-[#151515]'
            }`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );

  const applyRoadAestheticCategory = (nextCategory: string | undefined) => {
    setProps((p) => {
      const selectedCategory = normalizeAestheticCategory('road_aesthetic', nextCategory || undefined);
      const nextProps: SiteZoneProperties = {
        ...p,
        road_aesthetic_category: selectedCategory,
      };

      const currentAesthetic = (p.road_aesthetic as string) || undefined;
      if (!currentAesthetic) {
        return nextProps;
      }

      const optionsForCategory = selectedCategory
        ? ROADWAY_AESTHETIC_OPTIONS.filter((o) => o.categoryId === selectedCategory)
        : ROADWAY_AESTHETIC_OPTIONS;

      if (optionsForCategory.some((o) => o.id === currentAesthetic)) {
        return nextProps;
      }

      return buildAestheticSelectionProps(nextProps, 'road_aesthetic', undefined, ROADWAY_AESTHETIC_OPTIONS);
    });
  };

  const applyRoadAesthetic = (next: string | undefined, selectedArchetypeImageId?: string, selectedVariantId?: string) => {
    setProps((p) => {
      let nextProps = buildAestheticSelectionProps(
        p,
        'road_aesthetic',
        next,
        ROADWAY_AESTHETIC_OPTIONS,
        ROADWAY_AESTHETIC_PRESETS,
        selectedArchetypeImageId,
        selectedVariantId,
      );

      const selectedOption = ROADWAY_AESTHETIC_OPTIONS.find((o) => o.id === next);
      if (selectedOption?.categoryId) {
        nextProps.road_aesthetic_category = selectedOption.categoryId;
      }

      const modeDefaults = normalizeTransportModes(selectedOption?.transportModes);
      if (modeDefaults.length > 0) {
        nextProps = applyModeDrivenRoadDefaults(nextProps, modeDefaults, (nextProps.volume as string) || undefined);

        // Mode-derived defaults are only a fallback. Catalog archetypes own
        // their engineered section dimensions (for example the 18 m Complete
        // Main Street and 16 m Calgary Local), so restore the explicit preset
        // after deriving generic mobility priorities. Otherwise the broad
        // low/medium/high rules silently rewrite a selected LEGO family to an
        // incompatible width before Community 3D compilation.
        const catalogPreset = next ? ROADWAY_AESTHETIC_PRESETS[next] : undefined;
        if (catalogPreset) {
          nextProps = { ...nextProps, ...catalogPreset };
        }
      }

      return nextProps;
    });
  };

  const applyGreenSpaceCategory = (nextCategory: string | undefined) => {
    setProps((p) => {
      const selectedCategory = normalizeAestheticCategory('green_space_aesthetic', nextCategory || undefined);
      const nextProps: SiteZoneProperties = {
        ...p,
        green_space_aesthetic_category: selectedCategory,
      };

      const currentAesthetic = (p.green_space_aesthetic as string) || undefined;
      if (!currentAesthetic) {
        return nextProps;
      }

      const optionsForCategory = selectedCategory
        ? GREEN_SPACE_AESTHETIC_OPTIONS.filter((o) => o.categoryId === selectedCategory)
        : GREEN_SPACE_AESTHETIC_OPTIONS;

      if (optionsForCategory.some((o) => o.id === currentAesthetic)) {
        return nextProps;
      }

      return buildAestheticSelectionProps(nextProps, 'green_space_aesthetic', undefined, GREEN_SPACE_AESTHETIC_OPTIONS);
    });
  };

  const applyGreenSpaceAesthetic = (next: string | undefined, selectedArchetypeImageId?: string, selectedVariantId?: string) => {
    setProps((p) => {
      const nextProps = buildAestheticSelectionProps(
        p,
        'green_space_aesthetic',
        next,
        GREEN_SPACE_AESTHETIC_OPTIONS,
        GREEN_SPACE_AESTHETIC_PRESETS,
        selectedArchetypeImageId,
        selectedVariantId,
      );

      const selectedOption = GREEN_SPACE_AESTHETIC_OPTIONS.find((o) => o.id === next);
      if (selectedOption?.categoryId) {
        nextProps.green_space_aesthetic_category = selectedOption.categoryId;
      }
      return nextProps;
    });
  };

  const applyPlazaCategory = (nextCategory: string | undefined) => {
    setProps((p) => {
      const selectedCategory = normalizeAestheticCategory('plaza_aesthetic', nextCategory || undefined);
      const nextProps: SiteZoneProperties = {
        ...p,
        plaza_aesthetic_category: selectedCategory,
      };

      const currentAesthetic = (p.plaza_aesthetic as string) || undefined;
      if (!currentAesthetic) {
        return nextProps;
      }

      const optionsForCategory = selectedCategory
        ? PLAZA_AESTHETIC_OPTIONS.filter((o) => o.categoryId === selectedCategory)
        : PLAZA_AESTHETIC_OPTIONS;

      if (optionsForCategory.some((o) => o.id === currentAesthetic)) {
        return nextProps;
      }

      return buildAestheticSelectionProps(nextProps, 'plaza_aesthetic', undefined, PLAZA_AESTHETIC_OPTIONS);
    });
  };

  const applyPlazaAesthetic = (next: string | undefined, selectedArchetypeImageId?: string, selectedVariantId?: string) => {
    setProps((p) => {
      const nextProps = buildAestheticSelectionProps(
        p,
        'plaza_aesthetic',
        next,
        PLAZA_AESTHETIC_OPTIONS,
        PLAZA_AESTHETIC_PRESETS,
        selectedArchetypeImageId,
        selectedVariantId,
      );
      const selectedOption = PLAZA_AESTHETIC_OPTIONS.find((o) => o.id === next);
      if (selectedOption?.categoryId) {
        nextProps.plaza_aesthetic_category = selectedOption.categoryId;
      }
      return nextProps;
    });
  };

  // Unified Parks / Plazas handlers — route by archetype's spaceType so a
  // single picker can drive both park-typed and plaza-typed archetypes from
  // the same panel. The renderer iterates all prefixes (development, road,
  // green_space, plaza) and picks up whichever has data, so it doesn't matter
  // for rendering which prefix the data lands in — but we keep the data tidy
  // by clearing the OTHER prefix when switching spaceTypes.
  const applyOpenSpaceCategory = (nextCategory: string | undefined) => {
    applyGreenSpaceCategory(nextCategory);
    applyPlazaCategory(nextCategory);
  };

  const applyOpenSpaceAesthetic = (next: string | undefined, archetypeImageId?: string, variantId?: string) => {
    if (!next) {
      applyGreenSpaceAesthetic(undefined);
      applyPlazaAesthetic(undefined);
      return;
    }
    const isPlaza = PLAZA_AESTHETIC_OPTIONS.some((o) => o.id === next);
    if (isPlaza) {
      applyGreenSpaceAesthetic(undefined);
      applyPlazaAesthetic(next, archetypeImageId, variantId);
    } else {
      applyPlazaAesthetic(undefined);
      applyGreenSpaceAesthetic(next, archetypeImageId, variantId);
    }
  };

  const applyRoadVolume = (nextVolume: string | undefined) => {
    setProps((p) => {
      const nextProps: SiteZoneProperties = { ...p, volume: nextVolume || undefined };
      return applyModeDrivenRoadDefaults(nextProps, inferTransportModesFromProperties(nextProps), nextVolume);
    });
  };

  const footprintMetrics = zone.coordinates && zone.coordinates.length >= 3
    ? polygonDimensionsMeters(zone.coordinates)
    : { width: 0, depth: 0, area: 0 };
  const area = footprintMetrics.area;
  const panelLabelClass = 'block text-[10px] font-black uppercase text-[#151515]/55';
  const panelMetricLabelClass = 'text-[10px] font-black uppercase text-[#151515]/50';
  const panelMetricValueClass = 'text-xs font-black text-[#151515]/65';
  const panelFieldClass = 'mt-0.5 w-full rounded-lg border-2 border-[#151515] bg-white px-2.5 py-1.5 text-sm font-semibold text-[#151515] shadow-[2px_2px_0_0_rgba(21,21,21,0.2)] focus:bg-[#fff9ec] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d]';
  const panelTextareaClass = `${panelFieldClass} resize-none`;

  return (
    <>
      {/* Backdrop overlay ? mobile only */}
      <div
        className="pointer-events-auto fixed inset-0 z-20 bg-black/30 sm:hidden"
        onClick={onClose}
      />
      <div ref={panelRef} className="pointer-events-auto fixed inset-x-0 bottom-0 z-30 max-h-[70dvh] w-full overflow-x-hidden overflow-y-auto rounded-t-lg border-2 border-[#151515] bg-[#fff9ec]/95 p-4 shadow-[8px_8px_0_0_#151515] backdrop-blur-xl sm:absolute sm:inset-auto sm:right-4 sm:top-16 sm:bottom-auto sm:left-auto sm:z-40 sm:w-96 sm:max-w-[calc(100vw-2rem)] sm:max-h-[calc(100dvh-5rem)] sm:rounded-lg xl:w-[28rem]">
        {/* Drag handle ? mobile visual cue */}
        <div className="mb-3 flex justify-center sm:hidden">
          <div className="h-1 w-10 rounded-full bg-[#151515]" />
        </div>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span
              className="inline-block h-4 w-4 rounded border-2 border-[#151515]"
              style={{ backgroundColor: zone.color }}
            />
            <h3 className="text-sm font-black uppercase text-[#151515]">{config?.label || zone.zone_type}</h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-full border-2 border-[#151515] bg-white p-1 text-[#151515] shadow-[2px_2px_0_0_#151515] transition hover:bg-[#ff5a3d] hover:text-white"
          >
            <X size={14} />
          </button>
        </div>

        <div className="mt-3 space-y-2.5 text-sm">
        {/* Name */}
        <div>
          <label className={panelLabelClass}>Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={config?.label || 'Zone'}
            className={panelFieldClass}
          />
        </div>

        {/* Area display */}
        <div className="flex justify-between">
          <span className={panelMetricLabelClass}>Map area</span>
          <span className={panelMetricValueClass}>
            {formatArea(area)}
          </span>
        </div>
        {footprintMetrics.width > 0 && footprintMetrics.depth > 0 && (
          <div className="flex justify-between">
            <span className={panelMetricLabelClass}>Footprint</span>
            <span className={panelMetricValueClass}>
              {Math.round(footprintMetrics.width).toLocaleString()} m x {Math.round(footprintMetrics.depth).toLocaleString()} m
            </span>
          </div>
        )}

        {/* ============================================================= */}
        {/* LAYOUT PREVIEW ? shown at top when preview is active           */}
        {/* ============================================================= */}
        {layoutPreview?.zoneId === zone.id &&
          (zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') &&
          onAIGenerate && (
          <LayoutPreviewPanel
            zone={zone}
            onApplied={() => {}}
            onAIGenerate={onAIGenerate}
            referenceContext={osmContext}
            siblingZones={allZones?.filter((z) => z.id !== zone.id)}
          />
        )}

        {/* ============================================================= */}
        {/* SITE BOUNDARY ? analysis + generate                           */}
        {/* ============================================================= */}
        {zone.zone_type === 'site_boundary' && (
          <>
            <SiteIntelligencePanel zone={zone} />
            {SHOW_LEGACY_SITE_BOUNDARY_TOOLS && (
              <SiteBoundarySection
                zone={zone}
                allZones={allZones}
                onOpenBlockEditor={onOpenBlockEditor ? handleOpenBlockEditor : undefined}
              />
            )}
          </>
        )}

        {/* ============================================================= */}
        {/* BUILDING / RESIDENTIAL                                         */}
        {/* ============================================================= */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && (
          <>
            <BuildingWorkflowStepper
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            {activeBuildingStep === 1 && (
            <PanelStep step="1" title="Choose development type">
            <div>
              <label className={panelLabelClass}>Development Type</label>
              <select
                value={(props.development_type as string) || ''}
                onChange={(e) => {
                  const nextDevelopmentType = e.target.value || undefined;
                  applyBuildingDevelopmentType(nextDevelopmentType);
                  if (nextDevelopmentType) setActiveBuildingStep(2);
                }}
                className={panelFieldClass}
              >
                <option value="">-- Select --</option>
                <optgroup label="Residential">
                  <option value="residential_single_family">Single Family</option>
                  <option value="residential_duplex">Duplex</option>
                  <option value="residential_multifamily">Multi-Family</option>
                  <option value="residential_highrise">High-Rise</option>
                </optgroup>
                <optgroup label="Commercial">
                  <option value="commercial_light">Light Commercial</option>
                  <option value="commercial_retail">Retail</option>
                  <option value="commercial_office">Office</option>
                  <option value="commercial">General Commercial</option>
                </optgroup>
                <option value="mixed_use">Mixed Use</option>
                <optgroup label="Institutional">
                  <option value="institutional">General Institutional</option>
                  <option value="institutional_education">Education</option>
                  <option value="institutional_health">Health Care</option>
                </optgroup>
                <optgroup label="Industrial">
                  <option value="industrial_light">Light Industrial</option>
                  <option value="industrial">General Industrial</option>
                  <option value="industrial_heavy">Heavy Industrial</option>
                  <option value="industrial_warehouse">Warehouse</option>
                </optgroup>
                <option value="recreational">Recreational</option>
                <option value="recreational_centre">Rec Centre</option>
                <option value="sports_arena">Sports Arena</option>
                <option value="hotel">Hotels</option>
                <optgroup label="Transportation">
                  <option value="transit_station">Transit Station</option>
                  <option value="transit_hub">Transit Hub</option>
                  <option value="mobility_infrastructure">Mobility Infrastructure</option>
                </optgroup>
                <optgroup label="Energy">
                  <option value="energy_renewable">Renewable Energy</option>
                  <option value="energy_infrastructure">Energy Infrastructure</option>
                </optgroup>
                <option value="other">Other</option>
              </select>
            </div>
            <BuildingWorkflowPager
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            </PanelStep>
            )}
            {/* Development Aesthetic – only shown after a development type is chosen */}
            {activeBuildingStep === 2 && props.development_type && (
            <PanelStep step="2" title="Pick an archetype and check fit">
            <div>
              {renderCustomStyleToggle('building')}
              {props.custom_style_enabled ? (
                <CustomStyleEditor
                  domain="building"
                  zone={zone}
                  props={props}
                  setProps={setProps}
                  areaSqm={area}
                />
              ) : (
                <>
                  <label className={panelLabelClass}>Building Sub-Category</label>
                  <div className="mt-1">
                    <DevelopmentAestheticPicker
                      value={(props.development_aesthetic as string) || undefined}
                      selectedReferenceId={(props.development_archetype_id as string) || undefined}
                      selectedVariantId={(props.development_selected_variant_id as string) || undefined}
                      zoneType={zone.zone_type}
                      developmentType={(props.development_type as string) || undefined}
                      areaSqm={area}
                      onChange={(next, archetypeImageId, variantId) => {
                        applyBuildingAesthetic(next, archetypeImageId, variantId);
                      }}
                    />
                  </div>
                </>
              )}
            </div>
            <BuildingWorkflowPager
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            </PanelStep>
            )}
            {activeBuildingStep === 2 && !props.development_type && (
              <PanelStep step="2" title="Pick an archetype and check fit" muted>
                <p className="text-[11px] font-semibold text-[#151515]/55">
                  Choose a development type first to narrow the archetype list.
                </p>
                <BuildingWorkflowPager
                  activeStep={activeBuildingStep}
                  developmentSelected={!!props.development_type}
                  onStepChange={setActiveBuildingStep}
                />
              </PanelStep>
            )}
            {activeBuildingStep === 3 && (() => {
              const selectedBuildingOption = DEVELOPMENT_AESTHETIC_OPTIONS.find((o) => o.id === (props.development_aesthetic as string));
              // Check for per-variant overrides (e.g. Vertical Farm variants have different floor/area specs)
              const selectedBuildingVariant = (props.development_selected_variant_id && selectedBuildingOption?.variants)
                ? selectedBuildingOption.variants.find((v) => v.id === props.development_selected_variant_id)
                : undefined;
              const archMinFloors = selectedBuildingVariant?.minFloors ?? selectedBuildingOption?.minFloors;
              const archMaxFloors = selectedBuildingVariant?.maxFloors ?? selectedBuildingOption?.maxFloors;
              const archSuggestedArea = selectedBuildingVariant?.suggestedAreaSqm ?? selectedBuildingOption?.suggestedAreaSqm;
              const currentFloors = (props.floors as number) || (config?.defaultProperties.floors as number);
              const floorOutOfRange = archMinFloors != null && archMaxFloors != null && currentFloors != null
                && (currentFloors < archMinFloors || currentFloors > archMaxFloors);
              return (
                <PanelStep step="3" title="Tune height and scale">
                  <div>
                    <label className={panelLabelClass}>Floors</label>
                    <input
                      type="number"
                      step="1"
                      min={archMinFloors ?? 1}
                      max={archMaxFloors}
                      value={props.floors ?? config?.defaultProperties.floors ?? ''}
                      onChange={(e) => {
                        const floors = parseInt(e.target.value) || undefined;
                        setProps((p) => {
                          if (!floors) return { ...p, floors: undefined };
                          const floorH = (p.floor_height as number) || 3;
                          return { ...p, floors, height: Math.round(floors * floorH * 10) / 10 };
                        });
                      }}
                      className={panelFieldClass}
                    />
                    {archMinFloors != null && archMaxFloors != null && (
                      <p className="mt-0.5 text-[10px] text-primary-950/40">Suggested: {archMinFloors}–{archMaxFloors} floors</p>
                    )}
                    {floorOutOfRange && (
                      <p className="mt-0.5 text-[10px] text-orange-500">Floor count is outside the typical range for this archetype ({archMinFloors}–{archMaxFloors})</p>
                    )}
                  </div>
                  <div>
                    <label className={panelLabelClass}>Height (m)</label>
                    <input
                      type="number"
                      step="1"
                      value={props.height ?? config?.defaultProperties.height ?? ''}
                      onChange={(e) => {
                        const height = parseFloat(e.target.value) || undefined;
                        setProps((p) => {
                          if (!height) return { ...p, height: undefined };
                          const floors = (p.floors as number) || (config?.defaultProperties.floors as number) || 1;
                          return { ...p, height, floor_height: Math.round((height / floors) * 100) / 100 };
                        });
                      }}
                      className={panelFieldClass}
                    />
                    {(() => {
                      const floors = (props.floors as number) || (config?.defaultProperties.floors as number);
                      const height = (props.height as number) || (config?.defaultProperties.height as number);
                      if (floors && height) {
                        return <p className="mt-0.5 text-[10px] text-primary-950/40">{(height / floors).toFixed(1)}m per floor</p>;
                      }
                      return null;
                    })()}
                  </div>
                  {archSuggestedArea != null && (() => {
                    const ratio = area / archSuggestedArea;
                    const pct = Math.round((ratio - 1) * 100);
                    const isClose = ratio >= 0.7 && ratio <= 1.5;
                    return (
                      <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.03] px-2 py-1.5">
                        <div className="flex justify-between items-baseline">
                          <span className="text-[10px] text-primary-950/50">Zone area</span>
                          <span className="text-[11px] font-medium text-primary-950/70">{Math.round(area).toLocaleString()} m²</span>
                        </div>
                        <div className="flex justify-between items-baseline mt-0.5">
                          <span className="text-[10px] text-primary-950/50">Suggested</span>
                          <span className="text-[11px] font-medium text-primary-950/70">~{archSuggestedArea.toLocaleString()} m²</span>
                        </div>
                        <div className={`mt-1 text-[10px] font-medium ${isClose ? 'text-green-600' : 'text-orange-500'}`}>
                          {isClose
                            ? `Good fit (${pct > 0 ? '+' : ''}${pct}%)`
                            : ratio < 0.7
                              ? `Zone is small for this archetype (${pct}%) — render may look cramped`
                              : `Zone is large for this archetype (+${pct}%) — render may look sparse`}
                        </div>
                        {(() => {
                          const opt = (selectedBuildingVariant ?? selectedBuildingOption) as any;
                          if (!opt?.suggestedWidth_m || !opt?.suggestedDepth_m) return null;
                          return (
                            <div className="mt-1.5 pt-1.5 border-t border-primary-950/[0.06]">
                              <div className="flex justify-between items-baseline">
                                <span className="text-[10px] text-primary-950/50">Optimal footprint</span>
                                <span className="text-[11px] font-medium text-primary-950/70">{opt.suggestedWidth_m}m × {opt.suggestedDepth_m}m</span>
                              </div>
                              {opt.minWidth_m != null && opt.maxWidth_m != null && (
                                <div className="flex justify-between items-baseline mt-0.5">
                                  <span className="text-[10px] text-primary-950/50">Width range</span>
                                  <span className="text-[11px] text-primary-950/50">{opt.minWidth_m}–{opt.maxWidth_m}m</span>
                                </div>
                              )}
                              {opt.minDepth_m != null && opt.maxDepth_m != null && (
                                <div className="flex justify-between items-baseline mt-0.5">
                                  <span className="text-[10px] text-primary-950/50">Depth range</span>
                                  <span className="text-[11px] text-primary-950/50">{opt.minDepth_m}–{opt.maxDepth_m}m</span>
                                </div>
                              )}
                              {opt.aspectRatio && (
                                <div className="flex justify-between items-baseline mt-0.5">
                                  <span className="text-[10px] text-primary-950/50">Proportions</span>
                                  <span className="text-[11px] text-primary-950/50">{opt.aspectRatio}</span>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    );
                  })()}
                  <BuildingWorkflowPager
                    activeStep={activeBuildingStep}
                    developmentSelected={!!props.development_type}
                    onStepChange={setActiveBuildingStep}
                  />
                </PanelStep>
              );
            })()}
          </>
        )}


        {/* ============================================================= */}
        {/* PARKS / PLAZAS (combined park + plaza picker)                  */}
        {/* ============================================================= */}
        {(zone.zone_type === 'green_space' || zone.zone_type === 'parking') && (
          <>
            {renderCustomStyleToggle('open_space')}
            {props.custom_style_enabled ? (
              <CustomStyleEditor
                domain="open_space"
                zone={zone}
                props={props}
                setProps={setProps}
                areaSqm={area}
              />
            ) : (
            <>
            <div>
              <label className={panelLabelClass}>Park / Plaza Category</label>
              <select
                value={selectedOpenSpaceCategory || ''}
                onChange={(e) => applyOpenSpaceCategory(e.target.value || undefined)}
                className={panelFieldClass}
              >
                <option value="">-- Select Category --</option>
                {OPENSPACE_AESTHETIC_CATEGORIES.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.label}
                  </option>
                ))}
              </select>
              {selectedOpenSpaceCategory && (
                <p className="mt-0.5 text-[10px] text-primary-950/50">
                  {OPENSPACE_AESTHETIC_CATEGORIES.find((item) => item.id === selectedOpenSpaceCategory)?.description}
                </p>
              )}
            </div>
            <div>
              <label className={panelLabelClass}>Park / Plaza Typology</label>
              <div className="mt-1">
                <OpenSpaceAestheticPicker
                  value={selectedOpenSpaceAesthetic}
                  category={selectedOpenSpaceCategory}
                  selectedReferenceId={selectedOpenSpaceReferenceId}
                  selectedVariantId={selectedOpenSpaceVariantId}
                  areaSqm={area}
                  onChange={applyOpenSpaceAesthetic}
                />
              </div>
            </div>
            {/* Area size check for selected archetype (works across both spaceTypes) */}
            {(() => {
              const selectedOption = OPENSPACE_AESTHETIC_OPTIONS.find(
                (o) => o.id === selectedOpenSpaceAesthetic,
              );
              if (!selectedOption) return null;
              const selectedVariant = (selectedOpenSpaceVariantId && selectedOption?.variants)
                ? selectedOption.variants.find((v) => v.id === selectedOpenSpaceVariantId)
                : undefined;
              const minArea = selectedVariant?.minAreaSqm ?? selectedOption?.minAreaSqm;
              const maxArea = selectedVariant?.maxAreaSqm ?? selectedOption?.maxAreaSqm;
              const suggestedArea = selectedVariant?.suggestedAreaSqm ?? selectedOption?.suggestedAreaSqm;
              if (suggestedArea == null && minArea == null) return null;
              const tooSmall = minArea != null && area < minArea;
              const tooLarge = maxArea != null && area > maxArea;
              const areaOutOfRange = tooSmall || tooLarge;
              return (
                <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.03] px-2 py-1.5">
                  <div className="flex justify-between items-baseline">
                    <span className="text-[10px] text-primary-950/50">Zone area</span>
                    <span className="text-[11px] font-medium text-primary-950/70">
                      {area >= 10000
                        ? `${(area / 10000).toFixed(2)} ha`
                        : `${Math.round(area).toLocaleString()} m²`}
                    </span>
                  </div>
                  {minArea != null && maxArea != null && (
                    <div className="flex justify-between items-baseline mt-0.5">
                      <span className="text-[10px] text-primary-950/50">Typical range</span>
                      <span className="text-[11px] font-medium text-primary-950/70">
                        {minArea >= 10000
                          ? `${(minArea / 10000).toFixed(1)} ha`
                          : `${minArea.toLocaleString()} m²`}
                        {' – '}
                        {maxArea >= 10000
                          ? `${(maxArea / 10000).toFixed(1)} ha`
                          : `${maxArea.toLocaleString()} m²`}
                      </span>
                    </div>
                  )}
                  <div className={`mt-1 text-[10px] font-medium ${areaOutOfRange ? 'text-orange-500' : 'text-green-600'}`}>
                    {tooSmall
                      ? `Zone is too small for this typology — minimum ${minArea!.toLocaleString()} m² recommended`
                      : tooLarge
                        ? `Zone is very large for this typology — maximum ${maxArea!.toLocaleString()} m² typical`
                        : 'Good fit for this typology'}
                  </div>
                </div>
              );
            })()}
            </>
            )}
          </>
        )}

        {/* ============================================================= */}
        {/* ROAD                                                           */}
        {/* ============================================================= */}
        {zone.zone_type === 'road' && (
          <>
            {renderCustomStyleToggle('street')}
            {props.custom_style_enabled ? (
              <CustomStyleEditor
                domain="street"
                zone={zone}
                props={props}
                setProps={setProps}
                areaSqm={area}
              />
            ) : (
            <>
            {/* Transportation Aesthetic Category */}
            <div>
              <label className={panelLabelClass}>Streets and Paths Category</label>
              <select
                value={selectedRoadAestheticCategory || ''}
                onChange={(e) => applyRoadAestheticCategory(e.target.value || undefined)}
                className={panelFieldClass}
              >
                <option value="">-- Select Category --</option>
                {ROADWAY_AESTHETIC_CATEGORIES.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.label}
                  </option>
                ))}
              </select>
              {selectedRoadAestheticCategory && (
                <p className="mt-0.5 text-[10px] text-primary-950/50">
                  {ROADWAY_AESTHETIC_CATEGORIES.find((item) => item.id === selectedRoadAestheticCategory)?.description}
                </p>
              )}
            </div>

            {/* Transportation Aesthetic */}
            <div>
              <label className={panelLabelClass}>Streets and Paths Aesthetic (Top 20)</label>
              <div className="mt-1">
                <RoadwayAestheticPicker
                  value={(props.road_aesthetic as string) || undefined}
                  category={selectedRoadAestheticCategory}
                  selectedReferenceId={selectedRoadReferenceId}
                  selectedVariantId={(props.road_selected_variant_id as string) || undefined}
                  onChange={applyRoadAesthetic}
                />
              </div>
            </div>
            </>
            )}

            {/* Volume */}
            <div>
              <label className={panelLabelClass}>Streets and Paths Volume</label>
              <select
                value={(props.volume as string) || ''}
                onChange={(e) => applyRoadVolume(e.target.value || undefined)}
                className={panelFieldClass}
              >
                <option value="">-- Select --</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className={panelLabelClass}>Width (m)</label>
              <input
                type="number"
                step="1"
                value={props.width ?? config?.defaultProperties.width ?? 10}
                onChange={(e) => setProps((p) => ({ ...p, width: parseFloat(e.target.value) || undefined }))}
                className={panelFieldClass}
              />
            </div>
          </>
        )}

        {/* PARKING block merged into combined PARKS / PLAZAS block above */}

        {/* ============================================================= */}
        {/* DEVELOPMENT AREA                                               */}
        {/* ============================================================= */}
        {zone.zone_type === 'development_area' && (
          <>
            <BuildingWorkflowStepper
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            {activeBuildingStep === 1 && (
            <PanelStep step="1" title="Choose development type">
            <div>
              <label className={panelLabelClass}>Development Type</label>
              <select
                value={(props.development_type as string) || ''}
                onChange={(e) => {
                  const nextDevelopmentType = e.target.value || undefined;
                  applyBuildingDevelopmentType(nextDevelopmentType);
                  if (nextDevelopmentType) setActiveBuildingStep(2);
                }}
                className={panelFieldClass}
              >
                <option value="">-- Select --</option>
                <optgroup label="Residential">
                  <option value="residential_single_family">Single Family</option>
                  <option value="residential_duplex">Duplex</option>
                  <option value="residential_multifamily">Multi-Family</option>
                  <option value="residential_highrise">High-Rise</option>
                </optgroup>
                <optgroup label="Commercial">
                  <option value="commercial_light">Light Commercial</option>
                  <option value="commercial_retail">Retail</option>
                  <option value="commercial_office">Office</option>
                  <option value="commercial">General Commercial</option>
                </optgroup>
                <option value="mixed_use">Mixed Use</option>
                <optgroup label="Institutional">
                  <option value="institutional">General Institutional</option>
                  <option value="institutional_education">Education</option>
                  <option value="institutional_health">Health Care</option>
                </optgroup>
                <optgroup label="Industrial">
                  <option value="industrial_light">Light Industrial</option>
                  <option value="industrial">General Industrial</option>
                  <option value="industrial_heavy">Heavy Industrial</option>
                  <option value="industrial_warehouse">Warehouse</option>
                </optgroup>
                <optgroup label="Transportation">
                  <option value="transit_station">Transit Station</option>
                  <option value="transit_hub">Transit Hub</option>
                  <option value="mobility_infrastructure">Mobility Infrastructure</option>
                </optgroup>
                <optgroup label="Energy">
                  <option value="energy_renewable">Renewable Energy</option>
                  <option value="energy_infrastructure">Energy Infrastructure</option>
                </optgroup>
              </select>
            </div>
            <BuildingWorkflowPager
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            </PanelStep>
            )}
            {activeBuildingStep === 2 && props.development_type && (
            <PanelStep step="2" title="Pick an archetype and check fit">
            <div>
              {renderCustomStyleToggle('building')}
              {props.custom_style_enabled ? (
                <CustomStyleEditor
                  domain="building"
                  zone={zone}
                  props={props}
                  setProps={setProps}
                  areaSqm={area}
                />
              ) : (
                <>
                  <label className={panelLabelClass}>Building Sub-Category</label>
                  <div className="mt-1">
                    <DevelopmentAestheticPicker
                      value={(props.development_aesthetic as string) || undefined}
                      selectedReferenceId={(props.development_archetype_id as string) || undefined}
                      selectedVariantId={(props.development_selected_variant_id as string) || undefined}
                      zoneType={zone.zone_type}
                      developmentType={(props.development_type as string) || undefined}
                      areaSqm={area}
                      onChange={(next, archetypeImageId, variantId) => {
                        applyBuildingAesthetic(next, archetypeImageId, variantId);
                      }}
                    />
                  </div>
                </>
              )}
            </div>
            <BuildingWorkflowPager
              activeStep={activeBuildingStep}
              developmentSelected={!!props.development_type}
              onStepChange={setActiveBuildingStep}
            />
            </PanelStep>
            )}
            {activeBuildingStep === 2 && !props.development_type && (
              <PanelStep step="2" title="Pick an archetype and check fit" muted>
                <p className="text-[11px] font-semibold text-[#151515]/55">
                  Choose a development type first to narrow the archetype list.
                </p>
                <BuildingWorkflowPager
                  activeStep={activeBuildingStep}
                  developmentSelected={!!props.development_type}
                  onStepChange={setActiveBuildingStep}
                />
              </PanelStep>
            )}
            {activeBuildingStep === 3 && (() => {
              const selectedDevOption = DEVELOPMENT_AESTHETIC_OPTIONS.find((o) => o.id === (props.development_aesthetic as string));
              const selectedDevVariant = (props.development_selected_variant_id && selectedDevOption?.variants)
                ? selectedDevOption.variants.find((v) => v.id === props.development_selected_variant_id)
                : undefined;
              const devMinFloors = selectedDevVariant?.minFloors ?? selectedDevOption?.minFloors;
              const devMaxFloors = selectedDevVariant?.maxFloors ?? selectedDevOption?.maxFloors;
              const devSuggestedArea = selectedDevVariant?.suggestedAreaSqm ?? selectedDevOption?.suggestedAreaSqm;
              const devCurrentFloors = (props.floors as number);
              const devFloorOutOfRange = devMinFloors != null && devMaxFloors != null && devCurrentFloors != null
                && (devCurrentFloors < devMinFloors || devCurrentFloors > devMaxFloors);
              return (
                <PanelStep step="3" title="Tune height and scale">
                  <div>
                    <label className={panelLabelClass}>Floors</label>
                    <input
                      type="number"
                      step="1"
                      min={devMinFloors ?? 1}
                      max={devMaxFloors}
                      value={props.floors ?? ''}
                      onChange={(e) => {
                        const floors = parseInt(e.target.value) || undefined;
                        setProps((p) => {
                          if (!floors) return { ...p, floors: undefined };
                          const floorH = (p.floor_height as number) || 3;
                          return { ...p, floors, height: Math.round(floors * floorH * 10) / 10 };
                        });
                      }}
                      className={panelFieldClass}
                    />
                    {devMinFloors != null && devMaxFloors != null && (
                      <p className="mt-0.5 text-[10px] text-primary-950/40">Suggested: {devMinFloors}–{devMaxFloors} floors</p>
                    )}
                    {devFloorOutOfRange && (
                      <p className="mt-0.5 text-[10px] text-orange-500">Floor count is outside the typical range for this archetype ({devMinFloors}–{devMaxFloors})</p>
                    )}
                  </div>
                  <div>
                    <label className={panelLabelClass}>Height (m)</label>
                    <input
                      type="number"
                      step="1"
                      value={props.height ?? ''}
                      onChange={(e) => {
                        const height = parseFloat(e.target.value) || undefined;
                        setProps((p) => {
                          if (!height) return { ...p, height: undefined };
                          const floors = (p.floors as number) || 1;
                          return { ...p, height, floor_height: Math.round((height / floors) * 100) / 100 };
                        });
                      }}
                      className={panelFieldClass}
                    />
                    {(() => {
                      const floors = (props.floors as number);
                      const height = (props.height as number);
                      if (floors && height) {
                        return <p className="mt-0.5 text-[10px] text-primary-950/40">{(height / floors).toFixed(1)}m per floor</p>;
                      }
                      return null;
                    })()}
                  </div>
                  {devSuggestedArea != null && (() => {
                    const ratio = area / devSuggestedArea;
                    const pct = Math.round((ratio - 1) * 100);
                    const isClose = ratio >= 0.7 && ratio <= 1.5;
                    return (
                      <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.03] px-2 py-1.5">
                        <div className="flex justify-between items-baseline">
                          <span className="text-[10px] text-primary-950/50">Zone area</span>
                          <span className="text-[11px] font-medium text-primary-950/70">{Math.round(area).toLocaleString()} m²</span>
                        </div>
                        <div className="flex justify-between items-baseline mt-0.5">
                          <span className="text-[10px] text-primary-950/50">Suggested</span>
                          <span className="text-[11px] font-medium text-primary-950/70">~{devSuggestedArea.toLocaleString()} m²</span>
                        </div>
                        <div className={`mt-1 text-[10px] font-medium ${isClose ? 'text-green-600' : 'text-orange-500'}`}>
                          {isClose
                            ? `Good fit (${pct > 0 ? '+' : ''}${pct}%)`
                            : ratio < 0.7
                              ? `Zone is small for this archetype (${pct}%) — render may look cramped`
                              : `Zone is large for this archetype (+${pct}%) — render may look sparse`}
                        </div>
                      </div>
                    );
                  })()}
                  <BuildingWorkflowPager
                    activeStep={activeBuildingStep}
                    developmentSelected={!!props.development_type}
                    onStepChange={setActiveBuildingStep}
                  />
                </PanelStep>
              );
            })()}
          </>
        )}

        {/* ============================================================= */}
        {/* SHARED: Descriptive Text + Reference Images                    */}
        {/* ============================================================= */}
        {zone.zone_type !== 'site_boundary' && (
          usesBuildingWorkflow ? (
            activeBuildingStep === 4 ? (
              <PanelStep step="4" title="Add details" roomy>
              <div>
                <label className={panelLabelClass}>Descriptive Text</label>
                <textarea
                  value={(props.description_text as string) || ''}
                  onChange={(e) => setProps((p) => ({ ...p, description_text: e.target.value || undefined }))}
                  placeholder="E.g. Make the trees maple trees. Use cobblestone for the sidewalk."
                  rows={4}
                  className={`${panelTextareaClass} min-h-28 leading-relaxed`}
                />
              </div>
              <ReferenceImagesSection
                images={(props.reference_images as string[]) || []}
                onChange={(imgs) => setProps((p) => ({ ...p, reference_images: imgs.length > 0 ? imgs : undefined }))}
                roomy
              />
              <BuildingWorkflowPager
                activeStep={activeBuildingStep}
                developmentSelected={!!props.development_type}
                onStepChange={setActiveBuildingStep}
              />
            </PanelStep>
            ) : null
          ) : (
            <>
              <div>
                <label className={panelLabelClass}>Descriptive Text</label>
                <textarea
                  value={(props.description_text as string) || ''}
                  onChange={(e) => setProps((p) => ({ ...p, description_text: e.target.value || undefined }))}
                  placeholder="E.g. Make the trees maple trees. Use cobblestone for the sidewalk."
                  rows={2}
                  className={panelTextareaClass}
                />
              </div>
              <ReferenceImagesSection
                images={(props.reference_images as string[]) || []}
                onChange={(imgs) => setProps((p) => ({ ...p, reference_images: imgs.length > 0 ? imgs : undefined }))}
              />
            </>
          )
        )}

        <button
          onClick={() => handleSave(true)}
          className="mt-1 w-full rounded-full border-2 border-[#151515] bg-[#151515] px-3 py-2 text-xs font-black uppercase text-white shadow-[4px_4px_0_0_#c9ff3d] transition hover:bg-[#2b2b2b]"
        >
          Save Changes
        </button>


        {/* Quick Regenerate ? visible when zone already has a generated building */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') && zone.building_id && (() => {
          const linkedBuilding = buildings?.find((b) => b.id === zone.building_id);
          if (!linkedBuilding || linkedBuilding.generation_status !== 'completed') return null;
          return (
            <QuickRegenerateSection
              building={linkedBuilding}
            />
          );
        })()}

        {/* Build with LEGO modules ? modular assembly composer */}
        {onOpenBlockEditor
          && ((['building', 'residential', 'development_area', 'development'] as string[]).includes(zone.zone_type)
            || !!props.development_archetype_id) && (
          <button
            onClick={handleOpenBlockEditor}
            className="flex w-full items-center justify-center gap-1.5 rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase text-[#151515] shadow-[3px_3px_0_0_#151515] transition hover:bg-[#d9ff70]"
          >
            <Box size={12} />
            Build with LEGO modules
          </button>
        )}

        {/* Preview History ? buildable zones */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') && (
          <PreviewHistorySection zone={zone} />
        )}

        <button
          onClick={() => onDelete(zone.id)}
          className="flex w-full items-center justify-center gap-1.5 rounded-full border-2 border-[#151515] bg-[#fff0ec] px-3 py-2 text-xs font-black uppercase text-[#d92618] shadow-[3px_3px_0_0_#151515] transition hover:bg-[#ffddd4]"
        >
          <Trash2 size={12} />
          Delete Zone
        </button>
      </div>
    </div>
    </>
  );
}

// =============================================================================
// Site Boundary Section
// =============================================================================

const ZONE_TYPE_ICONS: Record<string, typeof Building2> = {
  building: Building2,
  residential: Building2,
  road: Route,
  green_space: TreePine,
  water: Droplets,
  parking: ParkingCircle,
  development_area: MapPin,
};

/** Capture two screenshots from the Mapbox map: satellite-only and with zones drawn */
async function captureMapScreenshots(
  mapInstance: unknown,
  boundaryCoords?: number[][],
  allZones?: SiteZone[],
): Promise<{ satellite: string; withZones: string } | null> {
  const map = mapInstance as any;
  if (!map || typeof map.getCanvas !== 'function') {
    console.warn('[captureMapScreenshots] No valid map instance');
    return null;
  }
  console.log('[captureMapScreenshots] Starting capture, innerZones:', allZones?.filter(z => z.zone_type !== 'site_boundary').length);

  const ZONE_LAYERS = [
    'site-zones-boundary-fill', 'site-zones-fill', 'site-zones-outline', 'site-zones-selected',
    'site-zones-labels', 'zone-edit-vertices-layer',
    'drawing-preview-fill', 'drawing-preview-line',
  ];

  /** Wait for the map to finish rendering after a change */
  const waitForIdle = (): Promise<void> =>
    new Promise((resolve) => {
      const onIdle = () => resolve();
      if (map.isMoving() || map.isZooming()) {
        map.once('idle', onIdle);
      } else {
        map.once('render', () => resolve());
        map.triggerRepaint();
      }
    });

  try {
    // 0. Fit the map EXACTLY to the inner zones ? zero padding.
    //    Gemini receives ONLY the development area filling the entire frame.
    const innerZones = (allZones || []).filter((z) => z.zone_type !== 'site_boundary');
    const cropCoords = innerZones.length > 0
      ? innerZones.flatMap((z) => z.coordinates || [])
      : boundaryCoords || [];

    if (cropCoords.length > 0) {
      let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
      for (const [lng, lat] of cropCoords) {
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
      }
      // Zero expand ? the zones should fill the entire frame
      map.fitBounds(
        [[minLng, minLat], [maxLng, maxLat]],
        { padding: 10, animate: false },
      );
      await waitForIdle();
    }

    // 1. Hide ALL zone layers and capture clean satellite of just the development area
    const prevVisibility: Record<string, string> = {};
    for (const layerId of ZONE_LAYERS) {
      try {
        prevVisibility[layerId] = map.getLayoutProperty(layerId, 'visibility') || 'visible';
        map.setLayoutProperty(layerId, 'visibility', 'none');
      } catch { /* layer might not exist */ }
    }
    await waitForIdle();

    // 2. Pixel-crop the canvas to exactly the zone bounding box.
    //    fitBounds respects the canvas aspect ratio, so if zones are portrait
    //    but the canvas is landscape, there's wasted space on the sides.
    //    We solve this by projecting zone coords to pixels and cropping.
    let satellite: string;
    const mapCanvas = map.getCanvas();
    if (cropCoords.length > 0) {
      let pxMinX = Infinity, pxMaxX = -Infinity, pxMinY = Infinity, pxMaxY = -Infinity;
      for (const [lng, lat] of cropCoords) {
        const pt = map.project([lng, lat]);
        if (pt.x < pxMinX) pxMinX = pt.x;
        if (pt.x > pxMaxX) pxMaxX = pt.x;
        if (pt.y < pxMinY) pxMinY = pt.y;
        if (pt.y > pxMaxY) pxMaxY = pt.y;
      }
      // Add a tiny margin (2% of zone dimensions) so edges aren't cut off
      const marginX = (pxMaxX - pxMinX) * 0.02;
      const marginY = (pxMaxY - pxMinY) * 0.02;
      pxMinX = Math.max(0, pxMinX - marginX);
      pxMinY = Math.max(0, pxMinY - marginY);
      pxMaxX = Math.min(mapCanvas.width, pxMaxX + marginX);
      pxMaxY = Math.min(mapCanvas.height, pxMaxY + marginY);

      const cropW = Math.round(pxMaxX - pxMinX);
      const cropH = Math.round(pxMaxY - pxMinY);

      // Account for devicePixelRatio ? canvas pixels != CSS pixels
      const dpr = window.devicePixelRatio || 1;
      const offscreen = document.createElement('canvas');
      offscreen.width = Math.round(cropW * dpr);
      offscreen.height = Math.round(cropH * dpr);
      const ctx = offscreen.getContext('2d')!;
      ctx.drawImage(
        mapCanvas,
        Math.round(pxMinX * dpr), Math.round(pxMinY * dpr),
        offscreen.width, offscreen.height,
        0, 0,
        offscreen.width, offscreen.height,
      );
      satellite = offscreen.toDataURL('image/jpeg', 0.92);
    } else {
      satellite = mapCanvas.toDataURL('image/jpeg', 0.92);
    }

    // 3. Restore zone layers
    for (const layerId of ZONE_LAYERS) {
      try {
        map.setLayoutProperty(layerId, 'visibility', prevVisibility[layerId] || 'visible');
      } catch { /* ignore */ }
    }

    console.log('[captureMapScreenshots] Done, satellite size:', satellite.length);
    return { satellite, withZones: satellite };
  } catch (e) {
    console.error('[captureMapScreenshots] FAILED:', e);
    return null;
  }
}

function SiteBoundarySection({ zone, allZones, onOpenBlockEditor }: { zone: SiteZone; allZones?: SiteZone[]; onOpenBlockEditor?: () => void }) {
  const queryClient = useQueryClient();
  const [analysis, setAnalysis] = useState<BoundaryAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [previewingAll, setPreviewingAll] = useState(false);
  const [renderingIndices, setRenderingIndices] = useState<Set<number>>(new Set());
  const [failedSiteRenderIndices, setFailedSiteRenderIndices] = useState<Set<number>>(new Set());
  const autoRenderTriggered = useRef(false);
  const generationInFlight = useRef(false);
  const mapScreenshotsRef = useRef<{ satellite: string; withZones: string } | null>(null);
  const selectZone = useViewerStore((s) => s.selectZone);
  const mapInstance = useViewerStore((s) => s.mapInstance);
  const {
    sitePreview, setSitePreview, clearSitePreview,
    setActiveSitePreviewIndex, setSitePreviewImageUrl,
    setLightboxImage,
    clearLockedLayers,
  } = useViewerStore();

  useEffect(() => {
    // Unsaved zones carry a temp- id; the endpoint 422s on non-UUID ids.
    if (!isPersistedZoneId(zone.id)) {
      setAnalysis(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    siteZonesApi.getBoundaryAnalysis(zone.id)
      .then((data) => { if (!cancelled) setAnalysis(data); })
      .catch(() => { if (!cancelled) setAnalysis(null); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [zone.id]);

  const isSitePreviewActive = sitePreview?.boundaryZoneId === zone.id;
  const siteOptions = isSitePreviewActive ? sitePreview!.zoneLayouts : {};
  const siteImageUrls = isSitePreviewActive ? sitePreview!.imageUrls : {};
  const siteActiveIndex = isSitePreviewActive ? sitePreview!.activeIndex : 0;

  // Figure out how many option sets we have (max across zones)
  const optionCount = Object.values(siteOptions).reduce(
    (max, opts) => Math.max(max, opts.length), 0
  );

  // Auto-render site previews after layout generation
  useEffect(() => {
    if (!isSitePreviewActive || optionCount === 0 || autoRenderTriggered.current) return;
    const allRendered = Array.from({ length: optionCount }, (_, i) => i).every((i) => siteImageUrls[i]);
    if (allRendered) return;

    autoRenderTriggered.current = true;
    for (let idx = 0; idx < optionCount; idx++) {
      if (siteImageUrls[idx]) continue;
      renderSiteOption(idx);
    }
  }, [isSitePreviewActive, optionCount]); // eslint-disable-line react-hooks/exhaustive-deps

  // Reset auto-render flag and failed state when zone changes
  useEffect(() => {
    autoRenderTriggered.current = false;
    setFailedSiteRenderIndices(new Set());
  }, [zone.id]);

  const renderSiteOption = async (idx: number) => {
    setRenderingIndices((prev) => new Set(prev).add(idx));
    setFailedSiteRenderIndices((prev) => {
      const next = new Set(prev);
      next.delete(idx);
      return next;
    });
    try {
      // Build a map of zoneId -> chosen option for this index
      const zoneLayoutsForOption: Record<string, LayoutOption> = {};
      for (const [zid, opts] of Object.entries(siteOptions)) {
        if (opts[idx]) {
          zoneLayoutsForOption[zid] = opts[idx];
        }
      }
      // Build zone metadata (color, name, type) for Gemini prompt context
      const zoneMeta: Record<string, { color: string; name: string; zone_type: string }> = {};
      if (allZones) {
        for (const z of allZones) {
          if (z.id !== zone.id) { // skip the boundary itself
            zoneMeta[z.id] = {
              color: z.color,
              name: z.name || ZONE_TYPE_CONFIG[z.zone_type as keyof typeof ZONE_TYPE_CONFIG]?.label || z.zone_type,
              zone_type: z.zone_type,
            };
          }
        }
      }
      const result = await siteZonesApi.renderSitePreview(
        zone.id, idx, zoneLayoutsForOption,
        mapScreenshotsRef.current || undefined,
        Object.keys(zoneMeta).length > 0 ? zoneMeta : undefined,
      );
      setSitePreviewImageUrl(idx, result.image_url);
    } catch (err: any) {
      const detail = getApiErrorMessage(err, 'Unknown error');
      console.error('[renderSiteOption] Failed for index', idx, detail, err);
      setFailedSiteRenderIndices((prev) => new Set(prev).add(idx));
      toast.error(`Site preview ${idx + 1}: ${detail}`, { duration: 8000 });
    } finally {
      setRenderingIndices((prev) => {
        const next = new Set(prev);
        next.delete(idx);
        return next;
      });
    }
  };

  const handlePreviewAll = async () => {
    if (!analysis) return;
    const zonesToPreview = analysis.contained_zones.filter((z) => {
      return z.zone_type === 'building' || z.zone_type === 'residential' || z.zone_type === 'development_area';
    });
    if (zonesToPreview.length === 0) {
      toast.error('No buildable zones found ? add building or residential zones first');
      return;
    }

    // Capture map screenshots BEFORE anything changes
    mapScreenshotsRef.current = await captureMapScreenshots(mapInstance, zone.coordinates, allZones);

    setPreviewingAll(true);
    autoRenderTriggered.current = false;
    setFailedSiteRenderIndices(new Set());
    try {
      // Run all zone previews in parallel
      const results = await Promise.allSettled(
        zonesToPreview.map((cz) => siteZonesApi.previewLayouts(cz.id))
      );
      // Collect all zone layouts into a single map
      const allZoneLayouts: Record<string, LayoutOption[]> = {};
      let generated = 0;
      for (let i = 0; i < results.length; i++) {
        if (results[i].status === 'fulfilled') {
          const res = (results[i] as PromiseFulfilledResult<{ options: LayoutOption[] }>).value;
          allZoneLayouts[zonesToPreview[i].id] = res.options;
          generated++;
        }
      }
      clearLockedLayers();
      if (generated > 0) {
        // Store site-wide preview ? stay on boundary
        setSitePreview(zone.id, allZoneLayouts);
        toast.success(`Generated layouts for ${generated} zone${generated > 1 ? 's' : ''} ? rendering site previews...`);
      } else {
        toast.error('No layout previews could be generated');
      }
    } catch {
      toast.error('Failed to generate layout previews');
    } finally {
      setPreviewingAll(false);
    }
  };

  const handleGenerateCommunity3D = async (
    selectedLayouts?: Record<string, LayoutOption>,
    optionIndex = 0,
  ) => {
    // Belt-and-braces: the button is disabled for unsaved zones, but guard the
    // shared lightbox/history paths too because every compiler input must have
    // a persisted UUID and a current source fingerprint.
    if (!isPersistedZoneId(zone.id)) {
      toast.error('Save the boundary first (Save Changes above) — then generate.');
      return;
    }
    if (generationInFlight.current) return;
    generationInFlight.current = true;
    setGenerating(true);
    try {
      const layoutEntries = Object.entries(selectedLayouts ?? {});
      if (layoutEntries.length > 0) {
        const invalidLayouts = layoutEntries.filter(([, layout]) => layout.buildings.length !== 1);
        if (invalidLayouts.length > 0) {
          const sampleZoneIds = invalidLayouts.slice(0, 3).map(([zoneId]) => zoneId).join(', ');
          throw new Error(
            `${invalidLayouts.length} selected preview layout${invalidLayouts.length === 1 ? '' : 's'} `
            + 'must contain exactly one building before Community 3D can be generated. '
            + `No preview layouts were applied.${sampleZoneIds ? ` Check zones: ${sampleZoneIds}.` : ''}`,
          );
        }
        const applyResults = await Promise.allSettled(
          layoutEntries.map(([zoneId, layout]) => (
            siteZonesApi.applyLayout(zoneId, optionIndex, layout)
          )),
        );
        const failedCount = applyResults.filter((result) => result.status === 'rejected').length;
        if (failedCount > 0) {
          throw new Error(
            `${failedCount} selected layout${failedCount === 1 ? '' : 's'} could not be applied. `
            + 'Community 3D was not compiled; retry after the zones finish saving.',
          );
        }
        clearSitePreview();
        clearLockedLayers();
        toast.success(
          `Applied ${layoutEntries.length} previewed layout${layoutEntries.length === 1 ? '' : 's'}`,
        );
      }

      const summary = await compileBoundaryCommunity3D(zone.project_id, zone.id);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] }),
        queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] }),
      ]);
      const residualArea = summary.response.residual_landscape?.area_sqm ?? 0;
      toast.success(
        `Built ${summary.detailedBuildings} archetyped LEGO building${summary.detailedBuildings === 1 ? '' : 's'}, `
        + `${summary.parks} park${summary.parks === 1 ? '' : 's'}, and `
        + `${summary.streets} street/path layer${summary.streets === 1 ? '' : 's'}`
        + (residualArea > 0
          ? `; landscaped ${Math.round(residualArea).toLocaleString()} m² of remaining site.`
          : '.'),
      );
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Community 3D generation failed'), { duration: 8000 });
      // ImageLightbox closes only after a fulfilled onApply callback. Preserve
      // the preview on strict/preflight failures so the user can inspect it,
      // adjust the plan, and retry without losing context.
      throw error;
    } finally {
      generationInFlight.current = false;
      setGenerating(false);
    }
  };

  const selectedPreviewLayouts = (index: number): Record<string, LayoutOption> => (
    Object.fromEntries(
      Object.entries(siteOptions).flatMap(([zoneId, options]) => (
        options[index] ? [[zoneId, options[index]]] : []
      )),
    )
  );

  const handleGenerate = () => {
    void handleGenerateCommunity3D(
      isSitePreviewActive ? selectedPreviewLayouts(siteActiveIndex) : undefined,
      siteActiveIndex,
    ).catch(() => undefined);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-primary-950/50">
        <Loader2 size={12} className="animate-spin" />
        Analyzing boundary...
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-xs text-primary-950/50 italic">
        Could not analyze boundary contents.
      </div>
    );
  }

  const hasZones = analysis.total_contained > 0;
  const buildableTypes = ['building', 'residential', 'development_area'];
  const buildableZones = analysis.contained_zones.filter(
    (z) => buildableTypes.includes(z.zone_type)
  );
  const hasBuildableZones = buildableZones.length > 0;
  const osmBuildings = analysis.osm_context?.buildings;
  const osmRoads = analysis.osm_context?.roads;
  const hasOsm = (osmBuildings?.count ?? 0) > 0 || (osmRoads?.count ?? 0) > 0;

  const renderingCount = renderingIndices.size;

  return (
    <div className="space-y-2">
      {/* Contained zones ? clickable to select */}
      <div>
        <label className="block text-xs font-medium text-primary-950/60 mb-1">
          Contained Zones ({analysis.total_contained})
        </label>
        {hasZones ? (
          <div className="space-y-0.5">
            {analysis.contained_zones.map((cz) => {
              const config = ZONE_TYPE_CONFIG[cz.zone_type as keyof typeof ZONE_TYPE_CONFIG];
              const Icon = ZONE_TYPE_ICONS[cz.zone_type] || MapPin;
              const isBuildable = buildableTypes.includes(cz.zone_type);
              return (
                <button
                  key={cz.id}
                  onClick={() => selectZone(cz.id)}
                  className={`flex w-full items-center gap-2 rounded px-1.5 py-1 text-xs text-left transition-colors ${
                    isBuildable
                      ? 'text-primary-950/60 hover:bg-indigo-500/10 cursor-pointer'
                      : 'text-primary-950/50 hover:bg-primary-950/[0.04] cursor-pointer'
                  }`}
                  title={isBuildable ? 'Click to edit & preview layout' : 'Click to edit zone'}
                >
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: cz.color || config?.color || '#999' }}
                  />
                  <Icon size={11} className="text-primary-950/50 flex-shrink-0" />
                  <span className="truncate">{cz.name || config?.label || cz.zone_type}</span>
                  {isBuildable && (
                    <span className="ml-auto text-[10px] text-indigo-400 flex-shrink-0">edit</span>
                  )}
                </button>
              );
            })}
          </div>
        ) : (
          <div className="text-xs text-primary-950/50 italic">
            No zones inside this boundary. Draw zones within the boundary to get started.
          </div>
        )}
      </div>

      {/* OSM Infrastructure */}
      {hasOsm && (
        <div>
          <label className="block text-xs font-medium text-primary-950/60 mb-1">
            Nearby Infrastructure (OSM)
          </label>
          <div className="space-y-0.5 text-xs text-primary-950/50">
            {osmBuildings?.count ? (
              <div className="flex items-center gap-1.5">
                <Building2 size={10} />
                <span>{osmBuildings.count} existing buildings</span>
                {osmBuildings.avg_height ? (
                  <span className="text-primary-950/50">(avg {osmBuildings.avg_height.toFixed(0)}m)</span>
                ) : null}
              </div>
            ) : null}
            {osmRoads?.count ? (
              <div className="flex items-center gap-1.5">
                <Route size={10} />
                <span>{osmRoads.count} existing roads</span>
                {osmRoads.named_roads?.length ? (
                  <span className="text-primary-950/50 truncate">
                    ({osmRoads.named_roads.slice(0, 3).join(', ')})
                  </span>
                ) : null}
              </div>
            ) : null}
          </div>
          <p className="mt-0.5 text-[10px] text-primary-950/50">
            Real-world data from OpenStreetMap used for context
          </p>
        </div>
      )}

      {/* Open Block Editor */}
      {hasBuildableZones && onOpenBlockEditor && (
        <div className="space-y-1.5">
          <button
            onClick={onOpenBlockEditor}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 px-3 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-500/20 hover:from-indigo-500 hover:to-purple-500 transition-all"
          >
            <LayoutGrid size={13} />
            Open Block Editor
          </button>
          <p className="text-[10px] text-primary-950/50 text-center">
            Edit building layouts, add descriptions, then generate 3D
          </p>
        </div>
      )}

      {/* Site-wide preview options */}
      {isSitePreviewActive && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-primary-950/60">Site Layout Options</span>
            <div className="flex items-center gap-2">
              {renderingCount > 0 && (
                <span className="flex items-center gap-1 text-[10px] text-purple-500">
                  <Loader2 size={9} className="animate-spin" />
                  Rendering {renderingCount}...
                </span>
              )}
              <button
                onClick={() => { autoRenderTriggered.current = false; handlePreviewAll(); }}
                disabled={previewingAll}
                className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] text-indigo-400 hover:bg-primary-950/[0.04]"
                title="Regenerate all options"
              >
                <RefreshCw size={10} className={previewingAll ? 'animate-spin' : ''} />
                Regenerate
              </button>
            </div>
          </div>

          {/* Option cards */}
          {Array.from({ length: optionCount }, (_, idx) => {
            const isActive = idx === siteActiveIndex;
            const imageUrl = siteImageUrls[idx];
            const isRendering = renderingIndices.has(idx);
            const hasFailed = failedSiteRenderIndices.has(idx);
            // Collect stats for this option across all zones
            let totalBuildings = 0;
            let totalRoads = 0;
            let totalGreen = 0;
            for (const opts of Object.values(siteOptions)) {
              if (opts[idx]) {
                totalBuildings += opts[idx].buildings.length;
                totalRoads += opts[idx].roads.length;
                totalGreen += opts[idx].green_spaces.length;
              }
            }
            // Get label from first zone's option
            const firstOpts = Object.values(siteOptions)[0];
            const label = firstOpts?.[idx]?.option_label || `Option ${idx + 1}`;
            const reasoning = firstOpts?.[idx]?.reasoning || '';

            return (
              <div
                key={idx}
                onClick={() => setActiveSitePreviewIndex(idx)}
                className={`w-full cursor-pointer rounded-lg border p-2 text-left transition-all ${
                  isActive
                    ? 'border-indigo-400/40 bg-indigo-500/15 ring-1 ring-indigo-400/30'
                    : 'border-primary-950/[0.08] bg-white hover:border-primary-950/[0.12] hover:bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-xs font-semibold ${isActive ? 'text-indigo-300' : 'text-primary-950/60'}`}>
                    {label}
                  </span>
                  <span className="text-[10px] text-primary-950/50">
                    {totalBuildings} buildings, {totalRoads} roads, {totalGreen} green
                  </span>
                </div>

                {imageUrl ? (
                  <div className="relative group/card">
                    <img
                      src={imageUrl}
                      alt={`Site layout option ${idx + 1}`}
                      className="w-full rounded cursor-zoom-in"
                      onError={(e) => {
                        console.error('Site preview image failed to load:', imageUrl);
                        (e.target as HTMLImageElement).style.opacity = '0.3';
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setLightboxImage(imageUrl, {
                          onDownload: () => {
                            const link = document.createElement('a');
                            link.href = imageUrl;
                            link.download = `site-layout-option-${idx + 1}.png`;
                            link.click();
                          },
                          onApply: async () => {
                            await handleGenerateCommunity3D(selectedPreviewLayouts(idx), idx);
                          },
                          applyLabel: 'Generate Community',
                        });
                      }}
                    />
                    <div className="absolute bottom-1 right-1 flex gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const link = document.createElement('a');
                          link.href = imageUrl;
                          link.download = `site-layout-option-${idx + 1}.png`;
                          link.click();
                        }}
                        className="rounded bg-black/50 p-1 text-primary-950/80 hover:bg-black/70 hover:text-primary-950 opacity-0 group-hover/card:opacity-100 transition-opacity"
                        title="Download image"
                      >
                        <ArrowDownToLine size={10} />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); renderSiteOption(idx); }}
                        className="rounded bg-black/50 p-1 text-primary-950/80 hover:bg-black/70 hover:text-primary-950"
                        title="Re-render preview"
                      >
                        <RefreshCw size={10} />
                      </button>
                    </div>
                  </div>
                ) : isRendering ? (
                  <div className="flex h-[160px] items-center justify-center rounded bg-primary-950/[0.04]">
                    <div className="flex flex-col items-center gap-1.5">
                      <Loader2 size={16} className="animate-spin text-purple-400" />
                      <span className="text-[9px] text-primary-950/50">Rendering site preview...</span>
                    </div>
                  </div>
                ) : hasFailed ? (
                  <div className="flex h-[100px] items-center justify-center rounded bg-red-50">
                    <div className="flex flex-col items-center gap-1.5">
                      <span className="text-[9px] text-red-600">Render failed</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); renderSiteOption(idx); }}
                        className="flex items-center gap-1 rounded bg-primary-950/[0.04] px-2 py-1 text-[9px] text-primary-950 hover:bg-primary-950/[0.06]"
                      >
                        <RefreshCw size={8} />
                        Retry
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex h-[80px] items-center justify-center rounded bg-primary-950/[0.04]">
                    <span className="text-[10px] text-primary-950/50">Waiting to render...</span>
                  </div>
                )}

                <p className="mt-0.5 text-[10px] leading-tight text-primary-950/50 line-clamp-2">
                  {reasoning}
                </p>
              </div>
            );
          })}

          {/* Expanded active option */}
          {siteImageUrls[siteActiveIndex] && (
            <div className="rounded-lg border border-indigo-400/20 bg-indigo-500/10 p-2">
              <div className="relative group/expanded">
                <img
                  src={siteImageUrls[siteActiveIndex]}
                  alt="Selected site layout"
                  className="w-full rounded cursor-zoom-in"
                  onClick={() => setLightboxImage(siteImageUrls[siteActiveIndex], {
                    onDownload: () => {
                      const link = document.createElement('a');
                      link.href = siteImageUrls[siteActiveIndex];
                      link.download = `site-layout-option-${siteActiveIndex + 1}.png`;
                      link.click();
                    },
                    onApply: async () => {
                      await handleGenerateCommunity3D(
                        selectedPreviewLayouts(siteActiveIndex),
                        siteActiveIndex,
                      );
                    },
                    applyLabel: 'Generate Community',
                  })}
                />
                <button
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = siteImageUrls[siteActiveIndex];
                    link.download = `site-layout-option-${siteActiveIndex + 1}.png`;
                    link.click();
                  }}
                  className="absolute top-1 right-1 rounded bg-black/50 p-1 text-primary-950/80 hover:bg-black/70 hover:text-primary-950 opacity-0 group-hover/expanded:opacity-100 transition-opacity"
                  title="Download image"
                >
                  <ArrowDownToLine size={10} />
                </button>
              </div>
              <p className="mt-1 text-[10px] text-center text-primary-950/50">Click image to expand</p>
            </div>
          )}

          <button
            onClick={() => { clearSitePreview(); clearLockedLayers(); }}
            className="w-full rounded-lg border border-primary-950/[0.08] px-3 py-1.5 text-xs text-primary-950/50 hover:bg-primary-950/[0.04]"
          >
            Cancel Preview
          </button>
        </div>
      )}

      {/* Step 2: Generate Community */}
      {hasBuildableZones && (
        <div className="space-y-1.5">
          <label className="block text-xs font-medium text-primary-950/60">
            {isSitePreviewActive ? 'Step 2: ' : ''}Generate Community
          </label>
          {!isPersistedZoneId(zone.id) && (
            <p className="rounded-lg border-2 border-dashed border-[#151515]/40 px-2.5 py-1.5 text-[11px] text-[#151515]/70">
              Save the boundary first (<b>Save Changes</b> above) — then generate the community.
            </p>
          )}
          <button
            onClick={handleGenerate}
            disabled={generating || !isPersistedZoneId(zone.id)}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-primary-950 hover:bg-purple-700 disabled:opacity-50"
            title="Generate a coordinated community and 3D models for this boundary"
          >
            {generating ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
            {generating ? 'Generating...' : 'Generate Community'}
          </button>
        </div>
      )}

      {!hasBuildableZones && hasZones && (
        <p className="text-[10px] text-primary-950/50 text-center">
          Add building or residential zones inside the boundary to generate
        </p>
      )}

      {/* Preview History ? site boundary */}
      <PreviewHistorySection
        zone={zone}
        onGenerateCommunity3D={handleGenerateCommunity3D}
      />
    </div>
  );
}


const AESTHETIC_EXAMPLE_COUNT = 4;

function normalizeExactLegoArchetypeId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function dedupeImageSources(sources: Array<string | null | undefined>): string[] {
  const deduped: string[] = [];
  for (const source of sources) {
    if (source && !deduped.includes(source)) deduped.push(source);
  }
  return deduped;
}

function useLegoReadyArchetypeIds(): ReadonlySet<string> {
  const { data: modules = [] } = useQuery({
    queryKey: ['lego-assembly', 'modules'],
    queryFn: () => legoAssemblyApi.listModules(),
    staleTime: 15_000,
    retry: 1,
  });

  return useMemo(() => {
    const ids = new Set<string>();
    for (const module of modules) {
      for (const archetypeId of module.archetype_ids) {
        const normalized = normalizeExactLegoArchetypeId(archetypeId);
        if (normalized) ids.add(normalized);
      }
    }
    return ids;
  }, [modules]);
}

function isLegoReady(
  legoReadyArchetypeIds: ReadonlySet<string> | undefined,
  archetypeId: string | null | undefined,
): boolean {
  return Boolean(
    legoReadyArchetypeIds
    && archetypeId
    && legoReadyArchetypeIds.has(normalizeExactLegoArchetypeId(archetypeId)),
  );
}

function buildAestheticImageSources(option: DevelopmentAestheticOption): string[] {
  const rawSources: string[] = [];

  if (Array.isArray(option.archetypeImages)) {
    const orderedArchetypeImages = [...option.archetypeImages].sort((a, b) => {
      const aFrontDay = a.id.endsWith(`_${FRONT_DAY_VARIANT_ID}`);
      const bFrontDay = b.id.endsWith(`_${FRONT_DAY_VARIANT_ID}`);
      if (aFrontDay === bFrontDay) return 0;
      return aFrontDay ? -1 : 1;
    });
    rawSources.push(...orderedArchetypeImages.map((image) => image.imageUrl));
  }

  if (Array.isArray(option.photoUrls)) {
    rawSources.push(...option.photoUrls);
  }

  if (option.photoUrl) {
    rawSources.unshift(option.photoUrl);
  }

  return dedupeImageSources(rawSources);
}
function AestheticImage({
  sources,
  alt,
  className,
  onDoubleClick,
}: {
  sources: string[];
  alt: string;
  className: string;
  onDoubleClick?: (activeSource: string) => void;
}) {
  const [sourceIndex, setSourceIndex] = useState(0);
  const [failed, setFailed] = useState(false);
  const sourceKey = sources.join('|');

  useEffect(() => {
    setSourceIndex(0);
    setFailed(false);
  }, [sourceKey]);

  if (sources.length === 0 || failed) {
    return (
      <div className={`${className} flex items-center justify-center bg-primary-950/[0.08] text-[10px] text-primary-950/50`}>
        Photo unavailable
      </div>
    );
  }

  return (
    <img
      src={sources[Math.min(sourceIndex, sources.length - 1)]}
      alt={alt}
      className={className}
      loading="lazy"
      referrerPolicy="no-referrer"
      onDoubleClick={() => {
        const activeSource = sources[Math.min(sourceIndex, sources.length - 1)];
        if (activeSource && onDoubleClick) {
          onDoubleClick(activeSource);
        }
      }}
      onError={() => {
        setSourceIndex((current) => {
          if (current < sources.length - 1) {
            return current + 1;
          }
          setFailed(true);
          return current;
        });
      }}
    />
  );
}


function AestheticOptionCard({
  option,
  value,
  selectedReferenceId,
  selectedVariantId,
  onSelect,
  legoReadyArchetypeIds,
  areaSqm,
  showSiteFit = true,
  stickerMethodVariantId,
}: {
  option: DevelopmentAestheticOption;
  value?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onSelect: (id: string, archetypeImageId?: string, variantId?: string) => void;
  legoReadyArchetypeIds?: ReadonlySet<string>;
  areaSqm?: number;
  showSiteFit?: boolean;
  stickerMethodVariantId?: string;
}) {
  const setLightboxImage = useViewerStore((s) => s.setLightboxImage);
  const sources = buildAestheticImageSources(option);
  const archetypeImages = Array.isArray(option.archetypeImages) ? option.archetypeImages : [];
  const variants = Array.isArray(option.variants) ? option.variants : [];
  const defaultArchetype = option.standardSection
    ? archetypeImages[0]
    : getFrontDayArchetypeImage(archetypeImages) || archetypeImages[0];

  // Catalogue cards are authored-reference UI. Imported family elevations,
  // model thumbnails, and generated 3D previews belong only to runtime/model
  // tooling and must never displace the selected /archetypes variant here.
  const activeVariant = value === option.id && selectedVariantId
    ? variants.find((v) => v.id === selectedVariantId)
    : undefined;

  const selectedArchetype = value === option.id
    ? archetypeImages.find((image) => image.id === selectedReferenceId) || defaultArchetype
    : defaultArchetype;

  // An explicit card render is exclusive: falling back to the known-bad
  // legacy hero would reintroduce a runtime model preview after one load error.
  const heroSources = option.catalogCardImageUrl
    ? [option.catalogCardImageUrl]
    : dedupeImageSources([
        activeVariant?.thumbnailUrl,
        selectedArchetype?.imageUrl,
        ...sources,
      ]);
  const isSelected = value === option.id;
  const isStandardSection = Boolean(option.standardSection?.sectionSvgUrl);
  // A lime Sticker Method badge names one approved child contract. Before the
  // user chooses another child, show that exact pilot's floors/footprint rather
  // than silently pairing its badge with an unrelated area-best variant.
  const displayedFitVariantId = isSelected && selectedVariantId
    ? selectedVariantId
    : stickerMethodVariantId;
  const areaFit = showSiteFit
    ? getAestheticAreaFit(option, displayedFitVariantId, areaSqm ?? 0)
    : null;

  // Determine thumbnail slot content from authored references only.
  const hasDesignVariants = variants.length > 0;
  const archetypeSlots = hasDesignVariants
    ? [] // design variants replace archetype lighting slots
    : archetypeImages.length > 0
      ? archetypeImages.slice(0, AESTHETIC_EXAMPLE_COUNT)
      : sources.slice(1, 1 + AESTHETIC_EXAMPLE_COUNT).map((source, idx) => ({
        id: `${option.id}-example-${idx}`,
        imageUrl: source,
        label: `${option.label} example ${idx + 1}`,
      }));

  const totalSlots = AESTHETIC_EXAMPLE_COUNT;
  const remainingArchetypeSlots = archetypeSlots.slice(0, totalSlots);
  const variantSlots = hasDesignVariants
    ? variants.slice(0, totalSlots)
    : [];

  const openImageLightbox = (imageUrl: string, label: string) => {
    const resolvedUrl = resolveApiFileUrl(imageUrl);
    const safeName = label.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '');
    setLightboxImage(resolvedUrl, {
      onDownload: () => {
        const link = document.createElement('a');
        link.href = resolvedUrl;
        link.download = `${safeName || 'archetype_reference'}.png`;
        link.click();
      },
    });
  };

  return (
    <div
      key={option.id}
      data-aesthetic-option-id={option.id}
      className={`overflow-hidden rounded-lg border text-left transition-all ${
        value === option.id
          ? 'border-primary-500 ring-2 ring-primary-500/25'
          : 'border-primary-950/[0.08] hover:border-primary-950/[0.2]'
      }`}
    >
      <button
        type="button"
        onClick={() => onSelect(option.id, selectedArchetype?.id || defaultArchetype?.id)}
        className="block w-full text-left"
        aria-label={`Select ${option.label} with Automatic / best-fitting family`}
      >
        <div
          className="relative aspect-[4/3] bg-primary-950/[0.06]"
          title="Double-click image to enlarge"
        >
          <AestheticImage
            sources={heroSources}
            alt={option.label}
            className={`h-full w-full ${isStandardSection ? 'bg-white object-contain p-1' : 'object-cover'}`}
            onDoubleClick={(activeSource) => openImageLightbox(activeSource, option.label)}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/20 to-transparent" />
          {stickerMethodVariantId && (
            <div className="absolute left-1.5 top-1.5 rounded-full border border-[#151515] bg-[#c9ff3d] px-1.5 py-0.5 text-[8px] font-black uppercase text-[#151515] shadow-sm">
              Sticker Method
            </div>
          )}
          {showSiteFit && (
            <div className={`absolute right-1.5 top-1.5 rounded-full px-1.5 py-0.5 text-[8px] font-black uppercase shadow-sm ${
              areaFit
                ? areaFit.isGoodFit
                  ? 'bg-green-100 text-green-700'
                  : 'bg-orange-100 text-orange-700'
                : 'bg-white/85 text-[#151515]/55'
            }`}>
              {areaFit ? (areaFit.isGoodFit ? 'Good fit' : areaFit.message.split(' ')[0]) : 'No data'}
            </div>
          )}
          <div className="absolute inset-x-0 bottom-0 p-2">
            <p className="text-[10px] font-semibold text-white">{option.label}</p>
          </div>
        </div>
        <div className="px-2 py-1.5">
          <p className="line-clamp-2 text-[10px] text-primary-950/50">{option.description}</p>
          {option.standardSection && (
            <div className="mt-1.5 rounded border border-sky-700/20 bg-sky-50 px-1.5 py-1 text-[9px] font-semibold leading-tight text-sky-950/70">
              <span className="font-black uppercase">Manual section</span>
              {option.standardSection.rowM ? ` · ${option.standardSection.rowM} m ROW` : ''}
              {option.standardSection.targetSpeedKmh ? ` · ${option.standardSection.targetSpeedKmh} km/h` : ''}
              {option.standardSection.citation ? (
                <span className="mt-0.5 block font-medium opacity-75">{option.standardSection.citation}</span>
              ) : null}
            </div>
          )}
          {showSiteFit && (
            <div className={`mt-1.5 rounded-md border px-1.5 py-1 ${
              areaFit
                ? areaFit.isGoodFit
                  ? 'border-green-600/25 bg-green-50 text-green-700'
                  : 'border-orange-500/25 bg-orange-50 text-orange-600'
                : 'border-primary-950/[0.08] bg-primary-950/[0.03] text-primary-950/45'
            }`}>
              <div className="flex items-center justify-between gap-1">
                <span className="text-[9px] font-black uppercase">Site fit</span>
                <span className="text-[10px] font-black">{areaFit?.message || 'No area data'}</span>
              </div>
              <div className="mt-0.5 text-[9px] font-semibold leading-tight opacity-80">
                Map {areaFit?.zoneAreaLabel || formatCompactArea(areaSqm ?? 0)}
                {areaFit?.suggestedAreaLabel ? ` · Suggested ${areaFit.suggestedAreaLabel}` : ''}
                {!areaFit?.suggestedAreaLabel && areaFit?.typicalRangeLabel ? ` · Typical ${areaFit.typicalRangeLabel}` : ''}
              </div>
              {(areaFit?.floorLabel || areaFit?.footprintLabel) && (
                <div className="mt-0.5 text-[9px] font-semibold leading-tight opacity-75">
                  {areaFit.floorLabel || ''}
                  {areaFit.floorLabel && areaFit.footprintLabel ? ' · ' : ''}
                  {areaFit.footprintLabel ? `Footprint ${areaFit.footprintLabel}` : ''}
                </div>
              )}
            </div>
          )}
          {hasDesignVariants && isSelected && (
            <p className="mt-1.5 text-[9px] font-black text-primary-950/65" aria-live="polite">
              Current selection: {activeVariant?.label || 'Automatic / best-fitting family'}
            </p>
          )}
        </div>
      </button>

      <div className="px-2 pb-1.5">
        {hasDesignVariants && (
          <button
            type="button"
            onClick={() => onSelect(option.id, selectedArchetype?.id || defaultArchetype?.id)}
            aria-pressed={isSelected && !selectedVariantId}
            className={`mb-1.5 flex w-full items-center justify-between rounded border px-1.5 py-1 text-left text-[9px] font-bold ${
              isSelected && !selectedVariantId
                ? 'border-primary-500 bg-primary-500/10 text-primary-950'
                : 'border-primary-950/[0.1] bg-white text-primary-950/60 hover:border-primary-950/[0.25]'
            }`}
          >
            <span>Automatic / best-fitting family</span>
            <span>{isSelected && !selectedVariantId ? 'Selected' : 'Use parent'}</span>
          </button>
        )}
        <div className="mt-1.5 grid grid-cols-2 gap-1.5">
          {/* Design variant thumbnails (if option has variants[]) */}
          {variantSlots.map((variant, variantIndex) => {
            const isActive = value === option.id && selectedVariantId === variant.id;
            const variantLegoReady = isLegoReady(legoReadyArchetypeIds, variant.id);
            const authoredVariantReference = archetypeImages[variantIndex];
            const variantSources = dedupeImageSources([
              variant.thumbnailUrl,
              authoredVariantReference?.imageUrl,
              authoredVariantReference?.thumbnailUrl,
              option.standardSection?.sectionSvgUrl ? option.photoUrl : undefined,
            ]);
            return (
              <button
                key={`${option.id}-variant-${variant.id}`}
                type="button"
                aria-pressed={isActive}
                data-variant-id={variant.id}
                data-lego-ready={variantLegoReady ? 'true' : 'false'}
                onClick={(event) => {
                  event.stopPropagation();
                  onSelect(option.id, selectedArchetype?.id || defaultArchetype?.id, variant.id);
                }}
                className={`relative h-14 overflow-hidden rounded border ${
                  isActive
                    ? variantLegoReady
                      ? 'border-emerald-500 ring-2 ring-primary-500/40'
                      : 'border-primary-500 ring-2 ring-primary-500/35'
                    : variantLegoReady
                      ? 'border-emerald-500 bg-primary-950/[0.06] hover:border-emerald-600'
                      : 'border-primary-950/[0.08] bg-primary-950/[0.06] hover:border-primary-950/[0.2]'
                }`}
                title={`${variant.label} — click to select, double-click to enlarge`}
              >
                <AestheticImage
                  sources={variantSources}
                  alt={variant.label}
                  className="h-full w-full object-cover"
                  onDoubleClick={(activeSource) => openImageLightbox(activeSource, `${option.label} — ${variant.label}`)}
                />
                <span className="absolute inset-x-0 bottom-0 bg-black/55 px-1 py-0.5 text-[8px] font-semibold leading-tight text-white">
                  {variant.label}
                </span>
              </button>
            );
          })}

          {/* Archetype lighting variant thumbnails (fill remaining slots when no design variants) */}
          {remainingArchetypeSlots.map((image, idx) => {
            const isSelected = value === option.id && selectedReferenceId === image.id;
            return (
              <button
                key={`${option.id}-example-${idx}`}
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onSelect(option.id, image.id);
                }}
                className={`relative h-14 overflow-hidden rounded border ${
                  isSelected
                    ? 'border-primary-500 ring-2 ring-primary-500/35'
                    : 'border-primary-950/[0.08] bg-primary-950/[0.06] hover:border-primary-950/[0.2]'
                }`}
                title={`${image.label} (double-click to enlarge)`}
              >
                <AestheticImage
                  sources={[image.imageUrl, ...heroSources]}
                  alt={`${option.label} example ${idx + 1}`}
                  className="h-full w-full object-cover"
                  onDoubleClick={(activeSource) => openImageLightbox(activeSource, image.label || option.label)}
                />
                <span className="absolute inset-x-0 bottom-0 bg-black/55 px-1 py-0.5 text-[8px] font-semibold leading-tight text-white">
                  {image.label || `View ${idx + 1}`}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
function DevelopmentAestheticPicker({
  value,
  selectedReferenceId,
  selectedVariantId,
  zoneType,
  developmentType,
  areaSqm,
  onChange,
}: {
  value?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  zoneType?: string;
  developmentType?: string;
  areaSqm?: number;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const allowedTypes = getAllowedDevelopmentTypes(zoneType || 'building', developmentType);
  const categoryOptions = filterOptionsByDevelopmentType(DEVELOPMENT_AESTHETIC_OPTIONS, allowedTypes);
  const rankedOptions = [...categoryOptions].sort((a, b) => {
    const pilotDelta = Number(STICKER_METHOD_BUILDING_IDS.has(b.id)) - Number(STICKER_METHOD_BUILDING_IDS.has(a.id));
    if (pilotDelta !== 0) return pilotDelta;
    const aFit = getAestheticAreaFit(
      a,
      STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE.get(a.id),
      areaSqm ?? 0,
    );
    const bFit = getAestheticAreaFit(
      b,
      STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE.get(b.id),
      areaSqm ?? 0,
    );
    if (aFit && bFit) return aFit.fitSort - bFit.fitSort;
    if (aFit) return -1;
    if (bFit) return 1;
    return a.label.localeCompare(b.label);
  });
  const bestFitCount = rankedOptions.filter((option) => getAestheticAreaFit(
    option,
    STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE.get(option.id),
    areaSqm ?? 0,
  )?.isGoodFit).length;
  const visibleStickerPilotCount = rankedOptions.filter((option) => STICKER_METHOD_BUILDING_IDS.has(option.id)).length;
  const legoReadyArchetypeIds = useLegoReadyArchetypeIds();

  return (
    <div className="space-y-2">
      {categoryOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No sub-categories found for this development type.
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.03] px-2 py-1.5 text-[10px] font-semibold text-primary-950/55">
          Best fits are sorted first for this drawn zone
          {bestFitCount > 0 ? ` · ${bestFitCount} likely fit${bestFitCount === 1 ? '' : 's'}` : ''}.
        </div>
      )}

      {visibleStickerPilotCount > 0 && (
        <div className="flex items-center gap-1.5 rounded border border-[#151515]/20 bg-[#c9ff3d]/20 px-2 py-1.5 text-[10px] font-semibold text-[#151515]">
          {visibleStickerPilotCount} approved Sticker Method pilot{visibleStickerPilotCount === 1 ? '' : 's'} pinned first for trialing.
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="flex items-center gap-1.5 rounded border border-emerald-500/25 bg-emerald-500/[0.06] px-2 py-1.5 text-[10px] font-semibold text-emerald-900">
          <span className="h-3 w-4 shrink-0 rounded border-2 border-emerald-500" aria-hidden="true" />
          Green frame = this exact variant has an imported LEGO family
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {rankedOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
              legoReadyArchetypeIds={legoReadyArchetypeIds}
              areaSqm={areaSqm}
              stickerMethodVariantId={STICKER_METHOD_BUILDING_VARIANT_BY_ARCHETYPE.get(option.id)}
            />
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={() => onChange(undefined)}
        disabled={!value}
        className="w-full rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-1 text-[11px] font-medium text-primary-950/60 hover:bg-primary-950/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
      >
        Clear Aesthetic
      </button>
    </div>
  );
}
function RoadwayAestheticPicker({
  value,
  category,
  selectedReferenceId,
  selectedVariantId,
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? ROADWAY_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];

  return (
    <div className="space-y-2">
      {!category && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          Select a transportation category to view typologies.
        </div>
      )}

      {category && categoryOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No transportation typologies found for this category.
        </div>
      )}

      {categoryOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {categoryOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
              showSiteFit={false}
            />
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={() => onChange(undefined)}
        disabled={!value}
        className="w-full rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-1 text-[11px] font-medium text-primary-950/60 hover:bg-primary-950/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
      >
        Clear Streets and Paths Aesthetic
      </button>
    </div>
  );
}
// =============================================================================
// Reference Images sub-component
// =============================================================================

/**
 * Combined Parks / Plazas typology picker — shows every openspace archetype
 * regardless of spaceType. The panel routes the selection to the correct
 * persistence prefix (green_space vs plaza) based on the picked archetype's
 * spaceType. Used by the unified "Parks / Plazas" zone block.
 */
function OpenSpaceAestheticPicker({
  value,
  category,
  selectedReferenceId,
  selectedVariantId,
  areaSqm,
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  areaSqm?: number;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? OPENSPACE_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];
  const rankedOptions = [...categoryOptions].sort((a, b) => {
    const pilotDelta = Number(STICKER_METHOD_PARK_IDS.has(b.id)) - Number(STICKER_METHOD_PARK_IDS.has(a.id));
    if (pilotDelta !== 0) return pilotDelta;
    const aFit = getAestheticAreaFit(
      a,
      STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE.get(a.id),
      areaSqm ?? 0,
    );
    const bFit = getAestheticAreaFit(
      b,
      STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE.get(b.id),
      areaSqm ?? 0,
    );
    if (aFit && bFit) return aFit.fitSort - bFit.fitSort;
    if (aFit) return -1;
    if (bFit) return 1;
    return a.label.localeCompare(b.label);
  });
  const bestFitCount = rankedOptions.filter((option) => getAestheticAreaFit(
    option,
    STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE.get(option.id),
    areaSqm ?? 0,
  )?.isGoodFit).length;

  return (
    <div className="space-y-2">
      {!category && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          Select a category to view typologies.
        </div>
      )}

      {category && categoryOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No typologies found for this category.
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.03] px-2 py-1.5 text-[10px] font-semibold text-primary-950/55">
          Best fits are sorted first for this drawn zone
          {bestFitCount > 0 ? ` · ${bestFitCount} likely fit${bestFitCount === 1 ? '' : 's'}` : ''}.
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="flex items-center gap-1.5 rounded border border-emerald-500/25 bg-emerald-500/[0.06] px-2 py-1.5 text-[10px] font-semibold text-emerald-900">
          <span className="h-3 w-4 shrink-0 rounded border-2 border-emerald-500" aria-hidden="true" />
          Green frame = this exact park variant has a reviewed 3D kit
        </div>
      )}

      {rankedOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {rankedOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
              legoReadyArchetypeIds={PARK_LEGO_READY_VARIANT_IDS}
              areaSqm={areaSqm}
              stickerMethodVariantId={STICKER_METHOD_PARK_VARIANT_BY_ARCHETYPE.get(option.id)}
            />
          ))}
        </div>
      )}
      <button
        type="button"
        onClick={() => onChange(undefined)}
        disabled={!value}
        className="w-full rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-1 text-[11px] font-medium text-primary-950/60 hover:bg-primary-950/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
      >
        Clear Typology
      </button>
    </div>
  );
}

// Legacy individual pickers — kept for any callers that still reference them.
// New code should use OpenSpaceAestheticPicker above.
void _GreenSpaceAestheticPicker; // suppress unused warning — kept as legacy picker
void _PlazaAestheticPicker; // suppress unused warning — kept as legacy picker
function _GreenSpaceAestheticPicker({
  value,
  category,
  selectedReferenceId,
  selectedVariantId,
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? GREEN_SPACE_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];

  return (
    <div className="space-y-2">
      {!category && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          Select a park category to view typologies.
        </div>
      )}

      {category && categoryOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No park typologies found for this category.
        </div>
      )}

      {categoryOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {categoryOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
            />
          ))}
        </div>
      )}
      <button
        type="button"
        onClick={() => onChange(undefined)}
        disabled={!value}
        className="w-full rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-1 text-[11px] font-medium text-primary-950/60 hover:bg-primary-950/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
      >
        Clear Park Typology
      </button>
    </div>
  );
}
function _PlazaAestheticPicker({
  value,
  category,
  selectedReferenceId,
  selectedVariantId,
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? PLAZA_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];

  return (
    <div className="space-y-2">
      {!category && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          Select a plaza category to view typologies.
        </div>
      )}

      {category && categoryOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No plaza typologies found for this category.
        </div>
      )}

      {categoryOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {categoryOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
            />
          ))}
        </div>
      )}
      <button
        type="button"
        onClick={() => onChange(undefined)}
        disabled={!value}
        className="w-full rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-1 text-[11px] font-medium text-primary-950/60 hover:bg-primary-950/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
      >
        Clear Plaza Typology
      </button>
    </div>
  );
}
function ReferenceImagesSection({
  images,
  onChange,
  roomy = false,
}: {
  images: string[];
  onChange: (imgs: string[]) => void;
  roomy?: boolean;
}) {
  const [url, setUrl] = useState('');

  const handleAdd = () => {
    const trimmed = url.trim();
    if (!trimmed) return;
    if (images.length >= 3) return;
    onChange([...images, trimmed]);
    setUrl('');
  };

  const handleRemove = (idx: number) => {
    onChange(images.filter((_, i) => i !== idx));
  };

  return (
    <div>
      <label className="mb-1 block text-[10px] font-black uppercase text-[#151515]/55">Reference Images</label>
      {/* Thumbnails */}
      {images.length > 0 && (
        <div className={`${roomy ? 'mb-2 gap-2' : 'mb-1.5 gap-1.5'} flex flex-wrap`}>
          {images.map((imgUrl, idx) => (
            <div key={idx} className={`group relative overflow-hidden rounded-lg border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_#151515] ${roomy ? 'h-20 w-20' : 'h-16 w-16'}`}>
              <img
                src={imgUrl}
                alt={`Ref ${idx + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
              <button
                onClick={() => handleRemove(idx)}
                className="absolute right-0 top-0 rounded-bl bg-[#ff5a3d] p-0.5 text-white opacity-0 transition-opacity group-hover:opacity-100"
              >
                <X size={10} />
              </button>
            </div>
          ))}
        </div>
      )}
      {/* Add input */}
      {images.length < 3 && (
        <div className={`${roomy ? 'gap-1.5' : 'gap-1'} flex`}>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste image URL and press Enter"
            className={`min-w-0 flex-1 rounded-lg border-2 border-[#151515] bg-white px-2 font-semibold text-[#151515] focus:bg-[#fff9ec] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d] ${roomy ? 'py-2 text-sm' : 'py-1.5 text-xs'}`}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd(); } }}
          />
          <button
            onClick={handleAdd}
            disabled={!url.trim()}
            className={`rounded-full border-2 border-[#151515] bg-[#c9ff3d] font-black uppercase text-[#151515] shadow-[2px_2px_0_0_#151515] transition hover:bg-[#d8ff68] disabled:opacity-40 ${roomy ? 'px-3.5 py-1.5 text-xs' : 'px-3 py-1 text-[11px]'}`}
          >
            Add
          </button>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Preview History section
// =============================================================================

function PreviewHistorySection({
  zone,
  onGenerateCommunity3D,
}: {
  zone: SiteZone;
  onGenerateCommunity3D?: (
    selectedLayouts?: Record<string, LayoutOption>,
    optionIndex?: number,
  ) => Promise<void>;
}) {
  const [expanded, setExpanded] = useState(false);
  const [applyingIdx, setApplyingIdx] = useState<number | null>(null);
  const { setLightboxImage } = useViewerStore();

  const history: PreviewHistoryEntry[] =
    (zone.properties?._preview_history as PreviewHistoryEntry[]) || [];

  if (history.length === 0) return null;

  // Most recent first
  const sorted = [...history].reverse();

  const handleDownload = (e: React.MouseEvent, entry: PreviewHistoryEntry) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = resolveApiFileUrl(entry.image_url);
    link.download = `${entry.label.replace(/[^a-zA-Z0-9]/g, '_')}.png`;
    link.click();
  };

  const handleApplyLayout = async (e: React.MouseEvent, entry: PreviewHistoryEntry, idx: number) => {
    e.stopPropagation();
    if (!entry.layout_data || applyingIdx !== null) return;
    setApplyingIdx(idx);
    try {
      await siteZonesApi.applyLayout(zone.id, entry.option_index, entry.layout_data as LayoutOption);
      toast.success('Layout applied ? buildings created');
    } catch {
      toast.error('Failed to apply layout');
    } finally {
      setApplyingIdx(null);
    }
  };

  const openLightbox = (entry: PreviewHistoryEntry) => {
    const download = () => {
      const link = document.createElement('a');
      link.href = resolveApiFileUrl(entry.image_url);
      link.download = `${entry.label.replace(/[^a-zA-Z0-9]/g, '_')}.png`;
      link.click();
    };

    let apply: (() => Promise<void>) | undefined;
    let applyLabel = 'Apply Layout';

    if (entry.layout_data && entry.preview_type === 'layout') {
      apply = async () => {
        await siteZonesApi.applyLayout(zone.id, entry.option_index, entry.layout_data as LayoutOption);
        toast.success('Layout applied ? buildings created');
      };
    } else if (
      entry.preview_type === 'site'
      && zone.zone_type === 'site_boundary'
      && onGenerateCommunity3D
    ) {
      applyLabel = 'Generate Community';
      apply = async () => {
        // If this history entry has stored zone layouts, the shared boundary
        // action applies them before its fresh, LEGO-only Community 3D compile.
        const zoneLayouts = entry.layout_data && 'zone_layouts' in entry.layout_data
          ? (entry.layout_data as { zone_layouts: Record<string, LayoutOption> }).zone_layouts
          : undefined;
        await onGenerateCommunity3D(zoneLayouts, entry.option_index);
      };
    }

    setLightboxImage(resolveApiFileUrl(entry.image_url), {
      onDownload: download,
      onApply: apply,
      applyLabel,
    });
  };

  return (
    <div className="rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.04]">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between px-2.5 py-1.5 text-xs font-medium text-primary-950/60 hover:text-primary-950"
      >
        <span>Previous Previews ({history.length})</span>
        <ChevronDown size={12} className={`transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && (
        <div className="grid grid-cols-3 gap-1.5 px-2.5 pb-2.5">
          {sorted.map((entry, idx) => (
            <div
              key={idx}
              className="group relative cursor-pointer overflow-hidden rounded border border-primary-950/[0.08] bg-primary-950/[0.04]"
              onClick={() => openLightbox(entry)}
            >
              <img
                src={resolveApiFileUrl(entry.image_url)}
                alt={entry.label}
                className="aspect-square w-full object-cover"
                onError={(e) => {
                  const img = e.target as HTMLImageElement;
                  img.style.display = 'none';
                  // Show error placeholder in next sibling
                  const placeholder = img.nextElementSibling as HTMLElement;
                  if (placeholder) placeholder.style.display = 'flex';
                }}
              />
              <div className="aspect-square w-full items-center justify-center bg-white/5 text-primary-950/40" style={{ display: 'none' }}>
                <span className="text-[9px]">Image unavailable</span>
              </div>
              <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/60 to-transparent opacity-0 transition-opacity group-hover:opacity-100">
                {/* Action buttons */}
                <div className="absolute top-1 right-1 flex gap-1">
                  <button
                    onClick={(e) => handleDownload(e, entry)}
                    className="rounded bg-black/50 p-1 text-primary-950 hover:bg-black/70"
                    title="Download"
                  >
                    <ArrowDownToLine size={10} />
                  </button>
                  {entry.layout_data && entry.preview_type === 'layout' && (
                    <button
                      onClick={(e) => handleApplyLayout(e, entry, idx)}
                      disabled={applyingIdx !== null}
                      className="rounded bg-black/50 p-1 text-white hover:bg-green-600/80 disabled:opacity-50"
                      title="Apply Layout"
                    >
                      {applyingIdx === idx ? <Loader2 size={10} className="animate-spin" /> : <Check size={10} />}
                    </button>
                  )}
                </div>
                <div className="p-1">
                  <p className="text-[9px] font-medium leading-tight text-primary-950 truncate">{entry.label}</p>
                  <p className="text-[8px] text-primary-950/70">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Model Library section
// =============================================================================

function formatReuseReason(reason: string): string {
  const normalized = reason.replace(/_/g, ' ').trim();
  if (!normalized) return 'match';
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

type ModelLibraryRecommendation = {
  item: ModelLibraryEntry;
  score: number;
  reasons?: string[];
};

void ModelLibrarySection; // kept for the reuse-library workflow
function ModelLibrarySection({ buildingId }: { buildingId: string }) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<ModelLibraryEntry[]>([]);
  const [recommended, setRecommended] = useState<ModelLibraryRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingRecommended, setLoadingRecommended] = useState(false);
  const [applying, setApplying] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [search, setSearch] = useState('');
  const queryClient = useQueryClient();

  const loadLibrary = async () => {
    setLoading(true);
    try {
      const data = await modelLibraryApi.list(search ? { search } : undefined);
      setItems(data);
    } catch {
      toast.error('Failed to load model library');
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    setLoadingRecommended(true);
    try {
      // No recommendation endpoint exists on the backend yet — surface the
      // empty state until modelLibraryApi grows a recommendForBuilding method.
      setRecommended([]);
    } finally {
      setLoadingRecommended(false);
    }
  };

  const handleBulkImport = async () => {
    setImporting(true);
    try {
      const result = await modelLibraryApi.bulkImport();
      toast.success('Imported ' + result.imported + ' models (' + result.skipped + ' skipped)');
      await Promise.all([loadLibrary(), loadRecommendations()]);
    } catch {
      toast.error('Failed to import models');
    } finally {
      setImporting(false);
    }
  };

  useEffect(() => {
    if (!open) return;
    loadLibrary();
    loadRecommendations();
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleApply = async (itemId: string) => {
    setApplying(itemId);
    try {
      await modelLibraryApi.applyToBuilding(itemId, buildingId);
      toast.success('Model applied from library');
      queryClient.invalidateQueries({ queryKey: ['project'] });
      setOpen(false);
    } catch {
      toast.error('Failed to apply model');
    } finally {
      setApplying(null);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    await loadLibrary();
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100"
      >
        <Library size={12} />
        Browse Model Library
      </button>
    );
  }

  return (
    <div className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-2.5">
      <div className="mb-2 flex items-center justify-between">
        <label className="text-[11px] font-medium text-emerald-700">Reusable 3D Asset Library</label>
        <button onClick={() => setOpen(false)} className="text-emerald-500 hover:text-emerald-700">
          <X size={12} />
        </button>
      </div>

      <div className="mb-2 rounded-md border border-emerald-100 bg-white/80 p-2">
        <div className="mb-1.5 flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">Recommended Matches</p>
          {loadingRecommended && <Loader2 size={10} className="animate-spin text-emerald-500" />}
        </div>

        {!loadingRecommended && recommended.length === 0 ? (
          <p className="text-[10px] text-emerald-700/70">
            No close reusable match found yet. Generate a model and save it to improve future reuse.
          </p>
        ) : (
          <div className="space-y-1">
            {recommended.map((rec) => (
              <div key={rec.item.id} className="flex items-center gap-2 rounded border border-emerald-100 bg-white p-1.5">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[11px] font-medium text-primary-950">{rec.item.name}</p>
                  <p className="truncate text-[9px] text-primary-950/60">
                    {'Score ' + Math.round(rec.score * 100) + '%'}
                    {(rec.reasons || []).length > 0 ? ' - ' + (rec.reasons || []).slice(0, 3).map(formatReuseReason).join(', ') : ''}
                  </p>
                </div>
                <button
                  onClick={() => handleApply(rec.item.id)}
                  disabled={applying === rec.item.id}
                  className="shrink-0 rounded bg-emerald-500 px-2 py-0.5 text-[10px] font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
                >
                  {applying === rec.item.id ? <Loader2 size={10} className="animate-spin" /> : 'Reuse'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSearch} className="mb-2 flex gap-1">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search all saved assets..."
          className="flex-1 rounded border border-emerald-200 bg-white px-2 py-1 text-xs text-primary-950 focus:border-emerald-400 focus:outline-none"
        />
        <button type="submit" className="rounded bg-emerald-500 px-2 py-1 text-xs text-white hover:bg-emerald-600">
          Search
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 size={16} className="animate-spin text-emerald-500" />
        </div>
      ) : items.length === 0 ? (
        <div className="py-3 text-center">
          <p className="mb-2 text-[10px] text-emerald-600/70">
            No saved assets yet. Import existing models or generate and save a new one.
          </p>
          <button
            onClick={handleBulkImport}
            disabled={importing}
            className="inline-flex items-center gap-1 rounded bg-emerald-500 px-3 py-1 text-[10px] font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
          >
            {importing ? <Loader2 size={10} className="animate-spin" /> : <ArrowDownToLine size={10} />}
            {importing ? 'Importing...' : 'Import Existing Models'}
          </button>
        </div>
      ) : (
        <div className="max-h-[200px] space-y-1 overflow-y-auto">
          {items.map((item) => (
            <div key={item.id} className="flex items-center gap-2 rounded border border-emerald-100 bg-white p-1.5">
              <div className="min-w-0 flex-1">
                <p className="truncate text-[11px] font-medium text-primary-950">{item.name}</p>
                <p className="truncate text-[9px] text-primary-950/60">
                  {item.generation_engine || 'unknown'} {item.use_count > 0 ? ' - used ' + item.use_count + 'x' : ''}
                </p>
              </div>
              <button
                onClick={() => handleApply(item.id)}
                disabled={applying === item.id}
                className="shrink-0 rounded bg-emerald-500 px-2 py-0.5 text-[10px] font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
              >
                {applying === item.id ? <Loader2 size={10} className="animate-spin" /> : 'Apply'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Quick Regenerate section
// =============================================================================

function QuickRegenerateSection({ building }: { building: Building }) {
  const [prompt, setPrompt] = useState(building.generation_prompt || '');
  const [regenerating, setRegenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showModel, setShowModel] = useState(false);

  useEffect(() => {
    setPrompt(building.generation_prompt || '');
  }, [building.generation_prompt]);

  const handleRegenerate = async () => {
    if (!prompt.trim()) return;
    setRegenerating(true);
    try {
      await buildingsApi.generate(building.id, prompt.trim());
      toast.success('Regeneration started');
    } catch {
      toast.error('Regeneration failed');
    } finally {
      setRegenerating(false);
    }
  };

  const handleSaveToLibrary = async () => {
    setSaving(true);
    try {
      const name = building.name || building.generation_prompt?.slice(0, 60) || 'Untitled Model';
      await modelLibraryApi.saveFromBuilding(
        building.id,
        name,
        building.generation_prompt || undefined,
        building.architectural_style ? 'other' : 'other',
        [],
      );
      toast.success('Model saved to library!');
    } catch {
      toast.error('Failed to save model');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="rounded-lg border border-purple-200 bg-purple-50/50 p-2.5">
      {building.model_url && (
        <>
          <button
            onClick={() => setShowModel(true)}
            className="mb-1.5 flex w-full items-center justify-center gap-1.5 rounded-lg border-2 border-[#151515] bg-[#28c7e8] px-3 py-1.5 text-xs font-black uppercase text-[#151515] shadow-[2px_2px_0_0_#151515] transition hover:bg-[#4dd4ef]"
          >
            <Box size={13} />
            View 3D Model
          </button>
          {showModel && (
            <BuildingModelViewer
              modelUrl={building.model_url}
              name={building.name || 'Building'}
              onClose={() => setShowModel(false)}
            />
          )}
        </>
      )}
      <label className="mb-1 block text-[11px] font-medium text-purple-700">Regenerate with modified prompt</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        className="mb-1.5 w-full rounded border border-purple-200 bg-primary-950/[0.04] px-2 py-1 text-xs text-primary-950 focus:border-purple-400 focus:outline-none"
      />
      <div className="flex gap-1.5">
        <button
          onClick={handleRegenerate}
          disabled={regenerating || !prompt.trim()}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-purple-500 px-3 py-1.5 text-xs font-medium text-primary-950 hover:bg-purple-600 disabled:opacity-50"
        >
          {regenerating ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
          {regenerating ? 'Regenerating...' : 'Regenerate'}
        </button>
        <button
          onClick={handleSaveToLibrary}
          disabled={saving}
          title="Save this model to your library for reuse"
          className="flex items-center justify-center gap-1 rounded-lg bg-emerald-500 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
        >
          {saving ? <Loader2 size={12} className="animate-spin" /> : <BookmarkPlus size={12} />}
          Save
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// AI Generate button
// =============================================================================

void AIGenerateZoneButton; // kept for the AI generation workflow
function AIGenerateZoneButton({ zone, onAIGenerate }: { zone: SiteZone; onAIGenerate: (buildingId: string, initialPrompt?: string) => void }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const building = await siteZonesApi.createBuildingFromZone(zone.id);
      const prompt = composeZonePrompt(zone);
      onAIGenerate(building.id, prompt);
    } catch {
      // Error will be shown in the AI modal
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-primary-950 hover:bg-purple-700 disabled:opacity-50"
    >
      {loading ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
      {loading ? 'Creating...' : 'AI Generate 3D'}
    </button>
  );
}

/**
 * Compose a rich AI generation prompt from zone properties.
 * Mirrors the backend compose_zone_prompt logic.
 */
function composeZonePrompt(zone: SiteZone): string {
  const props = zone.properties || {};
  const parts: string[] = [];

  // Determine unit count from properties or description text
  let unitCount = (props.unit_count as number) || 1;
  const descText = (props.description_text as string) || '';
  const unitMatch = descText.match(/(\d+)\s*(homes?|houses?|units?|buildings?|townhomes?|condos?)/i);
  if (unitMatch) {
    const parsed = parseInt(unitMatch[1]);
    if (parsed > unitCount) unitCount = parsed;
  }

  // 1. Building type + aesthetic
  const aesthetic = ((props.development_aesthetic as string) || '').replace(/_/g, ' ').trim();
  const aestheticCategory = ((props.development_aesthetic_category as string) || '').replace(/_/g, ' ').trim();
  const devType = ((props.development_type as string) || zone.zone_type).replace(/_/g, ' ');
  const typeLabel = devType.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  if (unitCount > 1) {
    if (aesthetic) {
      const aestheticLabel = aesthetic.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
      parts.push(`A single ${aestheticLabel} ${typeLabel} home suitable for a neighborhood of ${unitCount} homes`);
    } else {
      parts.push(`A single ${typeLabel} home suitable for a neighborhood of ${unitCount} homes`);
    }
  } else if (aesthetic) {
    const aestheticLabel = aesthetic.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    parts.push(`A ${aestheticLabel} ${typeLabel} building`);
  } else {
    parts.push(`A ${typeLabel} building`);
  }

  if (aestheticCategory) {
    const categoryLabel = aestheticCategory.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    parts.push(`Aesthetic category: ${categoryLabel}`);
  }
  const archetypeLabel = (props.development_archetype_label as string) || ((props.development_selected_reference as { label?: string } | undefined)?.label || '');
  const archetypeId = (props.development_archetype_id as string) || '';
  if (archetypeLabel) {
    parts.push(`Archetype reference: ${archetypeLabel}${archetypeId ? ` (${archetypeId.replace(/_/g, ' ')})` : ''}`);
  }

  const styleProfile = props.development_style_profile as {
    materials?: unknown;
    massing?: unknown;
    facadeRhythm?: unknown;
    roofForm?: unknown;
    frontageType?: unknown;
    windowStyle?: unknown;
    heightTendency?: unknown;
    streetRelationship?: unknown;
    renderingMood?: unknown;
    articulation?: unknown;
    publicRealm?: unknown;
  } | undefined;

  if (styleProfile) {
    const materials = Array.isArray(styleProfile.materials)
      ? styleProfile.materials.filter((entry): entry is string => typeof entry === 'string' && entry.trim().length > 0)
      : [];
    if (materials.length > 0) {
      parts.push(`Style materials: ${materials.join(', ')}`);
    }
    if (typeof styleProfile.massing === 'string' && styleProfile.massing.trim().length > 0) {
      parts.push(`Style massing: ${styleProfile.massing}`);
    }
    if (typeof styleProfile.facadeRhythm === 'string' && styleProfile.facadeRhythm.trim().length > 0) {
      parts.push(`Facade rhythm: ${styleProfile.facadeRhythm}`);
    }
    if (typeof styleProfile.roofForm === 'string' && styleProfile.roofForm.trim().length > 0) {
      parts.push(`Roof form: ${styleProfile.roofForm}`);
    }
    if (typeof styleProfile.frontageType === 'string' && styleProfile.frontageType.trim().length > 0) {
      parts.push(`Frontage type: ${styleProfile.frontageType}`);
    }
    if (typeof styleProfile.windowStyle === 'string' && styleProfile.windowStyle.trim().length > 0) {
      parts.push(`Window style: ${styleProfile.windowStyle}`);
    }
    if (typeof styleProfile.heightTendency === 'string' && styleProfile.heightTendency.trim().length > 0) {
      parts.push(`Height tendency: ${styleProfile.heightTendency}`);
    }
    if (typeof styleProfile.streetRelationship === 'string' && styleProfile.streetRelationship.trim().length > 0) {
      parts.push(`Street relationship: ${styleProfile.streetRelationship}`);
    }
    if (typeof styleProfile.renderingMood === 'string' && styleProfile.renderingMood.trim().length > 0) {
      parts.push(`Rendering mood: ${styleProfile.renderingMood}`);
    }
    if (typeof styleProfile.articulation === 'string' && styleProfile.articulation.trim().length > 0) {
      parts.push(`Articulation: ${styleProfile.articulation}`);
    }
    if (typeof styleProfile.publicRealm === 'string' && styleProfile.publicRealm.trim().length > 0) {
      parts.push(`Public realm intent: ${styleProfile.publicRealm}`);
    }
  }

  const generationStyleInput = props.generation_style_input as {
    buildingSubcategory?: string;
    aestheticCategoryLabel?: string;
    generationTags?: string[];
    imagePrompt?: { positive?: string; negative?: string };
  } | undefined;
  if (generationStyleInput?.buildingSubcategory) {
    parts.push(`Building subcategory: ${generationStyleInput.buildingSubcategory.replace(/_/g, ' ')}`);
  }
  if (Array.isArray(generationStyleInput?.generationTags) && generationStyleInput.generationTags.length > 0) {
    parts.push(`Generation tags: ${generationStyleInput.generationTags.join(', ')}`);
  }
  if (typeof generationStyleInput?.imagePrompt?.positive === 'string' && generationStyleInput.imagePrompt.positive.trim().length > 0) {
    parts.push(`Canonical style prompt: ${generationStyleInput.imagePrompt.positive}`);
  }

  // 2. Approximate dimensions from coordinates
  if (zone.coordinates && zone.coordinates.length >= 3) {
    const { width, depth, area } = polygonDimensionsMeters(zone.coordinates);
    if (area > 1 && width > 1 && depth > 1) {
      parts.push(`Building footprint approximately ${width.toFixed(0)}m wide by ${depth.toFixed(0)}m deep (${area.toFixed(0)} sq meters)`);
    }
  }

  // 3. Height / floors
  const floors = props.floors as number | undefined;
  const height = props.height as number | undefined;
  const floorHeight = (props.floor_height as number) || 3;
  if (floors && height) {
    parts.push(`${floors} stories tall (${height}m total height), each floor ${floorHeight}m high`);
  } else if (floors) {
    const total = floors * floorHeight;
    parts.push(`${floors} stories tall (${total}m total height), each floor ${floorHeight}m high`);
  }

  // 4. Facade material + roof style
  const facade = props.facade_material as string | undefined;
  const roof = props.roof_style as string | undefined;
  if (facade && roof) {
    parts.push(`${facade} facade material, ${roof} roof style`);
  } else if (facade) {
    parts.push(`${facade} facade material`);
  } else if (roof) {
    parts.push(`${roof} roof style`);
  }

  // 5. User description text
  const desc = props.description_text as string | undefined;
  if (desc) {
    parts.push(desc);
  }

  // 6. Quality directives
  if (unitCount > 1) {
    parts.push(
      'Realistic architectural style with detailed facade, visible windows, ' +
      'entrance doors, and appropriate material textures. ' +
      'Suitable for close-up walkthrough viewing. ' +
      'Single standalone unit, no surrounding buildings or landscape, no background or ground plane.'
    );
  } else {
    parts.push(
      'Realistic architectural style with detailed facade, visible windows, ' +
      'entrance doors, and appropriate material textures. ' +
      'Suitable for close-up walkthrough viewing. ' +
      'Single standalone building, no background or ground plane.'
    );
  }

  return parts.join('. ');
}

