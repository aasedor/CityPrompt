import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Trash2, Sparkles, Loader2, X, RefreshCw, Building2, Route, TreePine, Droplets, ParkingCircle, MapPin, LayoutGrid, ChevronDown, ArrowDownToLine, Check, BookmarkPlus, Library } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZone, SiteZoneProperties, Building, BoundaryAnalysisResponse, LayoutOption, PreviewHistoryEntry, ModelLibraryEntry } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { getShadeForArchetype } from '@/data/archetypeShadeMap';
import { siteZonesApi, buildingsApi, getApiErrorMessage, modelLibraryApi, resolveApiFileUrl } from '@/services/api';
import { useViewerStore } from '@/store';
import { undoableActionMatchesZoneId, useUndoRedoStore } from '@/store/undoRedo';
import { LayoutPreviewPanel } from './LayoutPreviewPanel';
import { formatArea, polygonDimensionsMeters } from './mapEngine/geoUtils';
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

interface ZonePropertiesPanelProps {
  zone: SiteZone;
  onUpdate: (zoneId: string, data: { name?: string; color?: string; properties?: SiteZoneProperties }) => void;
  onDelete: (zoneId: string) => void;
  onClose: () => void;
  onAIGenerate?: (buildingId: string, initialPrompt?: string) => void;
  buildings?: Building[];
  allZones?: SiteZone[];
  onOpenBlockEditor?: () => void;
}

type DevelopmentAestheticCategory = {
  id: string;
  label: string;
  description: string;
};

type TransportModeKey = CatalogTransportModeKey;

type DevelopmentAestheticOption = {
  id: string;
  categoryId?: string;
  label: string;
  description: string;
  photoUrl: string;
  photoUrls?: string[];
  transportModes?: TransportModeKey[];
  generationTags?: string[];
  archetypeImages?: CatalogArchetypeImage[];
  styleProfile?: CatalogStyleProfile;
  generationStyleInput?: Partial<CatalogGenerationStyleInput>;
  minFloors?: number;
  maxFloors?: number;
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

const ROADWAY_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = ROADWAY_AESTHETIC_PRESETS_V2;
const GREEN_SPACE_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = GREEN_SPACE_AESTHETIC_PRESETS_V2;
const PLAZA_AESTHETIC_PRESETS: Record<string, Partial<SiteZoneProperties>> = PLAZA_AESTHETIC_PRESETS_V2;

const FRONT_DAY_VARIANT_ID = 'variant_0';

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
    .replace(/[\s\-\/]+/g, '_')
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
  const navigate = useNavigate();

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
  }, [zone.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (undoRedoHistoryVersion === 0) return;
    if (lastSyncedUndoRedoVersionRef.current === undoRedoHistoryVersion) return;
    lastSyncedUndoRedoVersionRef.current = undoRedoHistoryVersion;
    if (lastAppliedUndoRedoAction?.label !== 'Update zone') return;
    if (!undoableActionMatchesZoneId(lastAppliedUndoRedoAction, zone.id)) return;
    setName(zone.name || '');
    setProps(zone.properties || {});
  }, [lastAppliedUndoRedoAction, undoRedoHistoryVersion, zone.id, zone.name, zone.properties]);

  const handleSave = (closeAfterSave = false) => {
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
    console.log(`[ZoneProps] Save — variantPalette="${variantPalettePrimary}", variantShade="${variantShadeId}", archetypeId="${archetypeId}", shade="${shadeColor}"`);

    onUpdate(zone.id, {
      name: name || undefined,
      color: shadeColor && shadeColor !== '#888888' ? shadeColor : undefined,
      properties: props,
    });

    if (closeAfterSave) {
      onClose();
    }
  };

  // Auto-save when the user picks a new archetype card (any zone type)
  const prevArchetypeRef = useRef<string | undefined>(undefined);
  useEffect(() => {
    const currentArchetype = (props.development_subcategory as string)
      || (props.road_subcategory as string)
      || (props.green_space_subcategory as string)
      || (props.plaza_subcategory as string)
      || (props.development_archetype_id as string)
      || (props.road_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || (props.plaza_archetype_id as string);

    // Skip initial mount and zone resets — only fire when archetype actually changes
    if (prevArchetypeRef.current !== undefined && currentArchetype && currentArchetype !== prevArchetypeRef.current) {
      handleSave();
    }
    prevArchetypeRef.current = currentArchetype;
  }, [props.development_subcategory, props.road_subcategory, props.green_space_subcategory, props.plaza_subcategory, props.development_archetype_id, props.road_archetype_id, props.green_space_archetype_id, props.plaza_archetype_id]); // eslint-disable-line react-hooks/exhaustive-deps

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
    const stylePrefix = DOMAIN_STYLE_FIELD_PREFIX[key];
    const inputMapKey = DOMAIN_STYLE_INPUT_KEY[key];
    const generationDomain = DOMAIN_GENERATION_DOMAIN[key];
    const archetypeImages = Array.isArray(selectedOption.archetypeImages) ? selectedOption.archetypeImages : [];
    const frontDayArchetype = getFrontDayArchetypeImage(archetypeImages);
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

    const archetypeId = resolvedArchetype?.id || selectedOption.id;
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
      id: archetypeId,
      label: archetypeLabel,
      imageUrl: resolvedArchetypeImage,
      imagePath: resolvedArchetype?.imagePath,
      description: resolvedArchetype?.description || selectedOption.description,
      camera: resolvedArchetype?.camera,
      lighting: resolvedArchetype?.lighting,
      prompt: resolvedArchetype?.prompt,
    };

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
      archetypeId,
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
          archetypeId,
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

  const selectedRoadReferenceId = (props.road_archetype_id as string) || ((props.road_selected_reference as { id?: string } | undefined)?.id) || undefined;
  const selectedGreenSpaceReferenceId = (props.green_space_archetype_id as string) || ((props.green_space_selected_reference as { id?: string } | undefined)?.id) || undefined;
  const selectedPlazaReferenceId = (props.plaza_archetype_id as string) || ((props.plaza_selected_reference as { id?: string } | undefined)?.id) || undefined;

  // Unified Parks / Plazas selection — reads from whichever prefix has data
  const selectedOpenSpaceAesthetic = (props.green_space_aesthetic as string) || (props.plaza_aesthetic as string) || undefined;
  const selectedOpenSpaceCategory = selectedGreenSpaceCategory || selectedPlazaCategory;
  const selectedOpenSpaceReferenceId = selectedGreenSpaceReferenceId || selectedPlazaReferenceId;
  const selectedOpenSpaceVariantId = (props.green_space_selected_variant_id as string) || (props.plaza_selected_variant_id as string) || undefined;

  const selectedTransportModes = inferTransportModesFromProperties(props);

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
        className="fixed inset-0 z-20 bg-black/30 sm:hidden"
        onClick={onClose}
      />
      <div ref={panelRef} className="fixed inset-x-0 bottom-0 z-30 max-h-[70vh] w-full overflow-y-auto rounded-t-lg border-2 border-[#151515] bg-[#fff9ec]/95 p-4 shadow-[8px_8px_0_0_#151515] backdrop-blur-xl sm:absolute sm:inset-auto sm:right-4 sm:top-16 sm:bottom-auto sm:left-auto sm:z-20 sm:w-80 sm:max-h-[calc(100%-5rem)] sm:rounded-lg">
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
          <SiteBoundarySection zone={zone} allZones={allZones} onOpenBlockEditor={onOpenBlockEditor} />
        )}

        {/* ============================================================= */}
        {/* BUILDING / RESIDENTIAL                                         */}
        {/* ============================================================= */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && (
          <>
            {/* Development Type */}
            <div>
              <label className={panelLabelClass}>Development Type</label>
              <select
                value={(props.development_type as string) || ''}
                onChange={(e) => applyBuildingDevelopmentType(e.target.value || undefined)}
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
            {/* Development Aesthetic – only shown after a development type is chosen */}
            {props.development_type && (
            <div>
              <label className={panelLabelClass}>Building Sub-Category</label>
              <div className="mt-1">
                <DevelopmentAestheticPicker
                  value={(props.development_aesthetic as string) || undefined}
                  selectedReferenceId={(props.development_archetype_id as string) || undefined}
                  selectedVariantId={(props.development_selected_variant_id as string) || undefined}
                  zoneType={zone.zone_type}
                  developmentType={(props.development_type as string) || undefined}
                  onChange={applyBuildingAesthetic}
                />
              </div>
            </div>
            )}
            {(() => {
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
                <>
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
                </>
              );
            })()}
          </>
        )}


        {/* ============================================================= */}
        {/* PARKS / PLAZAS (combined park + plaza picker)                  */}
        {/* ============================================================= */}
        {(zone.zone_type === 'green_space' || zone.zone_type === 'parking') && (
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

        {/* ============================================================= */}
        {/* ROAD                                                           */}
        {/* ============================================================= */}
        {zone.zone_type === 'road' && (
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
                  selectedModes={selectedTransportModes}
                  onChange={applyRoadAesthetic}
                />
              </div>
            </div>

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
            <div>
              <label className={panelLabelClass}>Development Type</label>
              <select
                value={(props.development_type as string) || ''}
                onChange={(e) => applyBuildingDevelopmentType(e.target.value || undefined)}
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
            {props.development_type && (
            <div>
              <label className={panelLabelClass}>Building Sub-Category</label>
              <div className="mt-1">
                <DevelopmentAestheticPicker
                  value={(props.development_aesthetic as string) || undefined}
                  selectedReferenceId={(props.development_archetype_id as string) || undefined}
                  selectedVariantId={(props.development_selected_variant_id as string) || undefined}
                  zoneType={zone.zone_type}
                  developmentType={(props.development_type as string) || undefined}
                  onChange={applyBuildingAesthetic}
                />
              </div>
            </div>
            )}
            {(() => {
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
                <>
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
                </>
              );
            })()}
          </>
        )}

        {/* ============================================================= */}
        {/* SHARED: Descriptive Text (all zone types except site_boundary) */}
        {/* ============================================================= */}
        {zone.zone_type !== 'site_boundary' && (
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
        )}

        {/* ============================================================= */}
        {/* SHARED: Reference Images (all zone types except site_boundary) */}
        {/* ============================================================= */}
        {zone.zone_type !== 'site_boundary' && (
          <ReferenceImagesSection
            images={(props.reference_images as string[]) || []}
            onChange={(imgs) => setProps((p) => ({ ...p, reference_images: imgs.length > 0 ? imgs : undefined }))}
          />
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      // Auto-apply any active site preview selections before generating
      if (isSitePreviewActive) {
        let appliedCount = 0;
        const applyResults = await Promise.all(
          Object.entries(siteOptions).map(async ([zoneId, options]) => {
            if (!options[siteActiveIndex]) return null;
            try {
              await siteZonesApi.applyLayout(zoneId, siteActiveIndex, options[siteActiveIndex]);
              return zoneId;
            } catch (e) {
              console.warn(`Failed to apply layout for zone ${zoneId}:`, e);
              return null;
            }
          })
        );
        appliedCount = applyResults.filter(Boolean).length;
        clearSitePreview();
        clearLockedLayers();
        if (appliedCount > 0) {
          toast.success(`Applied ${appliedCount} previewed layout${appliedCount > 1 ? 's' : ''}`);
        }
      }

      const result = await siteZonesApi.generateForBoundary(zone.project_id, zone.id);
      queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] });
      queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] });
      toast.success(
        `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
      );
    } catch {
      toast.error('Generation failed');
    } finally {
      setGenerating(false);
    }
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
                            // Auto-apply layouts then generate 3D
                            const applyResults = await Promise.all(
                              Object.entries(siteOptions).map(async ([zoneId, options]) => {
                                if (!options[idx]) return null;
                                try {
                                  await siteZonesApi.applyLayout(zoneId, idx, options[idx]);
                                  return zoneId;
                                } catch (err) {
                                  console.warn(`Failed to apply layout for zone ${zoneId}:`, err);
                                  return null;
                                }
                              })
                            );
                            const appliedCount = applyResults.filter(Boolean).length;
                            if (appliedCount > 0) {
                              clearSitePreview();
                              clearLockedLayers();
                            }
                            const result = await siteZonesApi.generateForBoundary(zone.project_id, zone.id);
                            queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] });
                            queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] });
                            toast.success(
                              `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
                            );
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
                      const applyResults = await Promise.all(
                        Object.entries(siteOptions).map(async ([zoneId, options]) => {
                          if (!options[siteActiveIndex]) return null;
                          try {
                            await siteZonesApi.applyLayout(zoneId, siteActiveIndex, options[siteActiveIndex]);
                            return zoneId;
                          } catch (err) {
                            console.warn(`Failed to apply layout for zone ${zoneId}:`, err);
                            return null;
                          }
                        })
                      );
                      const appliedCount = applyResults.filter(Boolean).length;
                      if (appliedCount > 0) {
                        clearSitePreview();
                        clearLockedLayers();
                      }
                      const result = await siteZonesApi.generateForBoundary(zone.project_id, zone.id);
                      queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] });
                      queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] });
                      toast.success(
                        `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
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
          <button
            onClick={handleGenerate}
            disabled={generating}
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
      <PreviewHistorySection zone={zone} />
    </div>
  );
}


const AESTHETIC_EXAMPLE_COUNT = 4;

// ---------------------------------------------------------------------------
// Archetype model previews — cached fetch of real 3D model thumbnails
// ---------------------------------------------------------------------------

type ArchetypeModelPreview = { id: string; name: string; preview_url: string; model_url: string; project_id?: string };

let _archetypePreviewsCache: Record<string, ArchetypeModelPreview[]> | null = null;
let _archetypePreviewsFetching = false;

function useArchetypeModelPreviews(): Record<string, ArchetypeModelPreview[]> {
  const [previews, setPreviews] = useState<Record<string, ArchetypeModelPreview[]>>(_archetypePreviewsCache || {});

  useEffect(() => {
    if (_archetypePreviewsCache) {
      setPreviews(_archetypePreviewsCache);
      return;
    }
    if (_archetypePreviewsFetching) return;
    _archetypePreviewsFetching = true;
    modelLibraryApi.archetypePreviews()
      .then((data) => {
        _archetypePreviewsCache = data;
        setPreviews(data);
      })
      .catch(() => {
        // Silently fail — just means no model thumbnails
      })
      .finally(() => {
        _archetypePreviewsFetching = false;
      });
  }, []);

  return previews;
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

  const deduped: string[] = [];
  for (const source of rawSources) {
    if (source && !deduped.includes(source)) {
      deduped.push(source);
    }
  }

  return deduped;
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
  modelPreviews,
}: {
  option: DevelopmentAestheticOption;
  value?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onSelect: (id: string, archetypeImageId?: string, variantId?: string) => void;
  modelPreviews?: ArchetypeModelPreview[];
}) {
  const setLightboxImage = useViewerStore((s) => s.setLightboxImage);
  const sources = buildAestheticImageSources(option);
  const archetypeImages = Array.isArray(option.archetypeImages) ? option.archetypeImages : [];
  const variants = Array.isArray(option.variants) ? option.variants : [];
  const defaultArchetype = getFrontDayArchetypeImage(archetypeImages) || archetypeImages[0];

  // If a variant is selected, use its thumbnailUrl as hero override
  const activeVariant = value === option.id && selectedVariantId
    ? variants.find((v) => v.id === selectedVariantId)
    : undefined;

  const selectedArchetype = value === option.id
    ? archetypeImages.find((image) => image.id === selectedReferenceId) || defaultArchetype
    : defaultArchetype;

  const heroSources = activeVariant?.thumbnailUrl
    ? [activeVariant.thumbnailUrl, ...(selectedArchetype ? [selectedArchetype.imageUrl] : []), ...sources]
    : selectedArchetype
      ? [selectedArchetype.imageUrl, ...sources.filter((source) => source !== selectedArchetype.imageUrl)]
      : sources.slice(0, Math.max(1, sources.length));

  // Determine thumbnail slot content: prefer design variants, fall back to lighting variants
  const hasDesignVariants = variants.length > 0;
  const modelSlots = (modelPreviews || []).slice(0, AESTHETIC_EXAMPLE_COUNT);
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
  const remainingArchetypeSlots = archetypeSlots.slice(0, totalSlots - modelSlots.length);
  const variantSlots = hasDesignVariants
    ? variants.slice(0, totalSlots - modelSlots.length)
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
    <button
      key={option.id}
      type="button"
      onClick={() => onSelect(option.id, selectedArchetype?.id || defaultArchetype?.id)}
      className={`overflow-hidden rounded-lg border text-left transition-all ${
        value === option.id
          ? 'border-primary-500 ring-2 ring-primary-500/25'
          : 'border-primary-950/[0.08] hover:border-primary-950/[0.2]'
      }`}
    >
      <div className="relative aspect-[4/3] bg-primary-950/[0.06]" title="Double-click image to enlarge">
        <AestheticImage
          sources={heroSources}
          alt={option.label}
          className="h-full w-full object-cover"
          onDoubleClick={(activeSource) => openImageLightbox(activeSource, option.label)}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/20 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-2">
          <p className="text-[10px] font-semibold text-white">{option.label}</p>
        </div>
      </div>
      <div className="px-2 py-1.5">
        <p className="line-clamp-2 text-[10px] text-primary-950/50">{option.description}</p>
        <div className="mt-1 grid grid-cols-4 gap-1">
          {/* Model preview thumbnails (from real Meshy-generated buildings) */}
          {modelSlots.map((model, idx) => (
            <button
              key={`${option.id}-model-${idx}`}
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                openImageLightbox(model.preview_url, model.name || option.label);
              }}
              className="relative h-9 overflow-hidden rounded border border-amber-500/40 bg-primary-950/[0.06] hover:border-amber-500/70"
              title={`${model.name || 'Generated model'} — click to preview`}
            >
              <img
                src={resolveApiFileUrl(model.preview_url)}
                alt={model.name || 'Model preview'}
                className="h-full w-full object-cover"
                loading="lazy"
              />
              {/* 3D badge */}
              <span className="absolute bottom-0 right-0 rounded-tl bg-amber-500/80 px-0.5 text-[7px] font-bold leading-tight text-white">
                3D
              </span>
            </button>
          ))}

          {/* Design variant thumbnails (if option has variants[]) */}
          {variantSlots.map((variant) => {
            const isActive = value === option.id && selectedVariantId === variant.id;
            return (
              <button
                key={`${option.id}-variant-${variant.id}`}
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onSelect(option.id, selectedArchetype?.id || defaultArchetype?.id, variant.id);
                }}
                onDoubleClick={(event) => {
                  event.stopPropagation();
                  if (variant.thumbnailUrl) {
                    openImageLightbox(variant.thumbnailUrl, `${option.label} — ${variant.label}`);
                  }
                }}
                className={`h-9 overflow-hidden rounded border ${
                  isActive
                    ? 'border-primary-500 ring-2 ring-primary-500/35'
                    : 'border-primary-950/[0.08] bg-primary-950/[0.06] hover:border-primary-950/[0.2]'
                }`}
                title={`${variant.label} — click to select, double-click to enlarge`}
              >
                {variant.thumbnailUrl ? (
                  <img
                    src={resolveApiFileUrl(variant.thumbnailUrl)}
                    alt={variant.label}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <span className="flex h-full w-full items-center justify-center text-[7px] text-primary-950/40 leading-tight px-0.5 text-center">
                    {variant.label}
                  </span>
                )}
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
                className={`h-9 overflow-hidden rounded border ${
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
              </button>
            );
          })}
        </div>
      </div>
    </button>
  );
}
function DevelopmentAestheticPicker({
  value,
  selectedReferenceId,
  selectedVariantId,
  zoneType,
  developmentType,
  onChange,
}: {
  value?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  zoneType?: string;
  developmentType?: string;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const allowedTypes = getAllowedDevelopmentTypes(zoneType || 'building', developmentType);
  const filteredOptions = filterOptionsByDevelopmentType(DEVELOPMENT_AESTHETIC_OPTIONS, allowedTypes);
  const archetypeModelPreviews = useArchetypeModelPreviews();

  return (
    <div className="space-y-2">
      {filteredOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No sub-categories found for this development type.
        </div>
      )}

      {filteredOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {filteredOptions.map((option) => (
            <AestheticOptionCard
              key={option.id}
              option={option}
              value={value}
              selectedReferenceId={selectedReferenceId}
              selectedVariantId={selectedVariantId}
              onSelect={(id, archetypeImageId, variantId) => onChange(id, archetypeImageId, variantId)}
              modelPreviews={archetypeModelPreviews[option.id]}
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
  selectedModes,
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  selectedModes: TransportModeKey[];
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? ROADWAY_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];

  const filteredOptions = categoryOptions.filter((option) => {
    if (option.id === 'other') return true;
    if (!option.transportModes || option.transportModes.length === 0) return true;
    return option.transportModes.some((mode) => selectedModes.includes(mode));
  });

  return (
    <div className="space-y-2">
      {!category && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          Select a transportation category to view typologies.
        </div>
      )}

      {category && filteredOptions.length === 0 && (
        <div className="rounded border border-primary-950/[0.08] bg-primary-950/[0.04] px-2 py-2 text-[11px] text-primary-950/60">
          No transportation typologies match the selected mode combination.
        </div>
      )}

      {filteredOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {filteredOptions.map((option) => (
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
  onChange,
}: {
  value?: string;
  category?: string;
  selectedReferenceId?: string;
  selectedVariantId?: string;
  onChange: (next: string | undefined, archetypeImageId?: string, variantId?: string) => void;
}) {
  const categoryOptions = category
    ? OPENSPACE_AESTHETIC_OPTIONS.filter((option) => option.categoryId === category)
    : [];

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
        Clear Typology
      </button>
    </div>
  );
}

// Legacy individual pickers — kept for any callers that still reference them.
// New code should use OpenSpaceAestheticPicker above.
function GreenSpaceAestheticPicker({
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
function PlazaAestheticPicker({
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
}: {
  images: string[];
  onChange: (imgs: string[]) => void;
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
        <div className="flex gap-1.5 mb-1.5 flex-wrap">
          {images.map((imgUrl, idx) => (
            <div key={idx} className="group relative h-16 w-16 overflow-hidden rounded-lg border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_#151515]">
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
        <div className="flex gap-1">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste image URL and press Enter"
            className="min-w-0 flex-1 rounded-lg border-2 border-[#151515] bg-white px-2 py-1.5 text-xs font-semibold text-[#151515] focus:bg-[#fff9ec] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d]"
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd(); } }}
          />
          <button
            onClick={handleAdd}
            disabled={!url.trim()}
            className="rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1 text-[11px] font-black uppercase text-[#151515] shadow-[2px_2px_0_0_#151515] transition hover:bg-[#d8ff68] disabled:opacity-40"
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

function PreviewHistorySection({ zone }: { zone: SiteZone }) {
  const queryClient = useQueryClient();
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
    } else if (entry.preview_type === 'site' && zone.zone_type === 'site_boundary') {
      applyLabel = 'Generate Community';
      apply = async () => {
        // If this history entry has stored zone layouts, apply them first
        const zoneLayouts = entry.layout_data && 'zone_layouts' in entry.layout_data
          ? (entry.layout_data as { zone_layouts: Record<string, LayoutOption> }).zone_layouts
          : null;
        if (zoneLayouts) {
          const applyResults = await Promise.all(
            Object.entries(zoneLayouts).map(async ([zoneId, layout]) => {
              try {
                await siteZonesApi.applyLayout(zoneId, entry.option_index, layout);
                return zoneId;
              } catch (err) {
                console.warn(`Failed to apply layout for zone ${zoneId}:`, err);
                return null;
              }
            })
          );
          const appliedCount = applyResults.filter(Boolean).length;
          if (appliedCount > 0) {
            toast.success(`Applied layouts for ${appliedCount} zone${appliedCount > 1 ? 's' : ''}`);
          }
        }
        const result = await siteZonesApi.generateForBoundary(zone.project_id, zone.id);
        queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] });
        queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] });
        toast.success(
          `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
        );
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
      const data = await modelLibraryApi.recommendForBuilding(buildingId, {
        limit: 6,
        min_score: 0.45,
      });
      setRecommended(data);
    } catch {
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

