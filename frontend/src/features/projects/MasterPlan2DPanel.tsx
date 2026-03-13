import { useEffect, useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Box, CheckCircle2, Compass, Download, Eye, ImageIcon, Layers3, List, Loader2, RefreshCcw, Ruler, Sparkles } from 'lucide-react';
import { getApiErrorMessage, masterPlan2DApi } from '@/services/api';
import { useViewerStore } from '@/store';
import type { MasterPlan2DGenerateRequest, MasterPlan2DOption, MasterPlan2DQualityLevel, MasterPlan2DStylePassProvider, MasterPlan2DStylePreset, MasterPlan3DGenerateRequest, MasterPlan3DLightingVariant, MasterPlan3DScope, MasterPlan3DScenePerspective, MasterPlanLightingAtmospherePreset, MasterPlanRenderStylePreset, SiteZone } from '@/types';
import { collectMasterPlan2DReferences } from './masterPlan2DReferences';

interface MasterPlan2DPanelProps {
  projectId: string;
  siteZones: SiteZone[];
  hasSiteGeometry: boolean;
}

const STYLE_OPTIONS: { value: MasterPlan2DStylePreset; label: string; description: string }[] = [
  { value: 'auto', label: 'Auto Cycle', description: 'Generates a stable A/B/C set with styling variations only.' },
  { value: 'rendered_sales_plan', label: 'Rendered Sales Plan', description: 'Crisp developer-board rendering with strong contrast.' },
  { value: 'hybrid_annotated_master_plan', label: 'Hybrid Annotated Master Plan', description: 'Presentation render with legend, north arrow, scale bar, and callouts.' },
  { value: 'illustrative_landscape_plan', label: 'Illustrative Landscape Plan', description: 'Softer landscape-led presentation with painterly planting textures.' },
];

const QUALITY_OPTIONS: { value: MasterPlan2DQualityLevel; label: string; description: string }[] = [
  { value: 'draft', label: 'Draft', description: 'Lighter texture pass for quick iteration.' },
  { value: 'presentation', label: 'Presentation', description: 'Balanced board-quality rendering for planning reviews.' },
  { value: 'board_ready', label: 'Board-Ready', description: 'Highest-quality export with richer texture, hierarchy, and polish.' },
];

const STYLE_PASS_PROVIDER_OPTIONS: { value: MasterPlan2DStylePassProvider; label: string; description: string }[] = [
  { value: 'auto', label: 'Auto', description: 'Try Gemini first, then fallback to Stability.' },
  { value: 'gemini', label: 'Gemini (Nano Banana 2)', description: 'Use Gemini for texture finish only.' },
  { value: 'stability', label: 'Stability AI', description: 'Use Stability SD3 image-to-image finish.' },
];

const RENDER_STYLE_OPTIONS: { value: MasterPlanRenderStylePreset; label: string; description: string }[] = [
  { value: 'photoreal_orthographic_aerial', label: 'Photoreal Orthographic Aerial', description: 'True overhead orthographic aerial with realistic roofs, paving, planting, and subdued context.' },
  { value: 'photorealistic_aerial', label: 'Photorealistic Aerial', description: 'Premium aerial rendering with stronger color, shadow, and developer-board clarity.' },
  { value: 'digital_watercolor_map', label: 'Digital Watercolor Map', description: 'Illustrative planimetric rendering with textured paper and softer graphic stylization.' },
];

const LIGHTING_ATMOSPHERE_OPTIONS: { value: MasterPlanLightingAtmospherePreset; label: string; description: string }[] = [
  { value: 'crisp_summer_day', label: 'Crisp Summer Day', description: 'Bright midday light with clear roof definition and lush planting contrast.' },
  { value: 'golden_hour', label: 'Golden Hour', description: 'Warm lower-angle light with longer shadows and richer surface depth.' },
  { value: 'overcast_soft', label: 'Overcast & Soft', description: 'Diffuse light with softer transitions and muted reflections.' },
  { value: 'winter_snow', label: 'Winter Snow', description: 'Snow-covered site mood with preserved contrast and legibility.' },
];

const EXPORT_WIDTHS = [3000, 4200, 5000];

const THREE_D_PERSPECTIVES: { value: MasterPlan3DScenePerspective; label: string }[] = [
  { value: 'aerial_oblique', label: 'Aerial Oblique' },
  { value: 'street_level_eye_height', label: 'Street-Level Eye Height' },
  { value: 'corner_perspective', label: 'Corner Perspective' },
  { value: 'promenade_view', label: 'Promenade View' },
];

const THREE_D_LIGHTING_OPTIONS: { value: MasterPlan3DLightingVariant; label: string }[] = [
  { value: 'golden_hour', label: 'Golden Hour' },
  { value: 'clear_daylight', label: 'Clear Daylight' },
  { value: 'overcast_soft_light', label: 'Overcast Soft Light' },
  { value: 'blue_hour_dusk', label: 'Blue Hour Dusk' },
];

const THREE_D_SCOPE_OPTIONS: { value: MasterPlan3DScope; label: string; description: string }[] = [
  { value: 'full_site', label: 'Full Site', description: 'Package every eligible zone from the current master plan.' },
  { value: 'selected_zones', label: 'Selected Zones', description: 'Only package the zones you choose below.' },
  { value: 'focused_frontage', label: 'Focused Frontage', description: 'Generate a single close-range study from the selected zone set.' },
];

const MASTER_PLAN_ZONE_LAYER_IDS = [
  'site-zones-fill',
  'site-zones-outline',
  'site-zones-selected',
  'site-zones-labels',
  'zone-edit-vertices-layer',
  'drawing-preview-fill',
  'drawing-preview-line',
];

async function captureMasterPlanSatelliteUnderlay(mapInstance: unknown): Promise<string | undefined> {
  const map = mapInstance as {
    getCanvas?: () => HTMLCanvasElement;
    getLayer?: (id: string) => unknown;
    getLayoutProperty?: (id: string, name: string) => string | undefined;
    setLayoutProperty?: (id: string, name: string, value: string) => void;
    once?: (event: string, handler: () => void) => void;
    triggerRepaint?: () => void;
  } | null;
  if (!map || typeof map.getCanvas !== 'function') {
    return undefined;
  }

  const previousVisibility: Record<string, string> = {};
  const waitForRender = () => new Promise<void>((resolve) => {
    if (typeof map.once === 'function') {
      map.once('render', () => resolve());
      map.triggerRepaint?.();
      return;
    }
    window.setTimeout(resolve, 120);
  });

  try {
    for (const layerId of MASTER_PLAN_ZONE_LAYER_IDS) {
      if (typeof map.getLayer === 'function' && !map.getLayer(layerId)) continue;
      try {
        previousVisibility[layerId] = map.getLayoutProperty?.(layerId, 'visibility') || 'visible';
        map.setLayoutProperty?.(layerId, 'visibility', 'none');
      } catch {
        // Ignore missing Mapbox layers.
      }
    }
    await waitForRender();
    return map.getCanvas().toDataURL('image/jpeg', 0.92);
  } catch {
    return undefined;
  } finally {
    for (const layerId of MASTER_PLAN_ZONE_LAYER_IDS) {
      if (!(layerId in previousVisibility)) continue;
      try {
        map.setLayoutProperty?.(layerId, 'visibility', previousVisibility[layerId]);
      } catch {
        // Ignore missing Mapbox layers.
      }
    }
  }
}

export function MasterPlan2DPanel({ projectId, siteZones, hasSiteGeometry }: MasterPlan2DPanelProps) {
  const queryClient = useQueryClient();
  const [renderStylePreset, setRenderStylePreset] = useState<MasterPlanRenderStylePreset>('photoreal_orthographic_aerial');
  const [lightingAtmospherePreset, setLightingAtmospherePreset] = useState<MasterPlanLightingAtmospherePreset>('crisp_summer_day');
  const [specificOverrides, setSpecificOverrides] = useState('');
  const [stylePreset, setStylePreset] = useState<MasterPlan2DStylePreset>('auto');
  const [qualityLevel, setQualityLevel] = useState<MasterPlan2DQualityLevel>('board_ready');
  const [exportWidth, setExportWidth] = useState(4200);
  const [showLegend, setShowLegend] = useState(true);
  const [showNorthArrow, setShowNorthArrow] = useState(true);
  const [showScaleBar, setShowScaleBar] = useState(true);
  const [showCalloutMarkers, setShowCalloutMarkers] = useState(true);
  const [showSurroundingContext, setShowSurroundingContext] = useState(true);
  const [aiStylePassEnabled, setAiStylePassEnabled] = useState(true);
  const [aiStylePassProvider, setAiStylePassProvider] = useState<MasterPlan2DStylePassProvider>('auto');
  const [selectedImageUrls, setSelectedImageUrls] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [previewOption, setPreviewOption] = useState<MasterPlan2DOption | null>(null);
  const [exportingOptionId, setExportingOptionId] = useState<string | null>(null);
  const [threeDPerspective, setThreeDPerspective] = useState<MasterPlan3DScenePerspective>('aerial_oblique');
  const [threeDLighting, setThreeDLighting] = useState<MasterPlan3DLightingVariant>('golden_hour');
  const [threeDScope, setThreeDScope] = useState<MasterPlan3DScope>('full_site');
  const [selected3DZoneIds, setSelected3DZoneIds] = useState<string[]>([]);
  const [generating3DForOptionId, setGenerating3DForOptionId] = useState<string | null>(null);
  const {
    masterPlan3D,
    startMasterPlan3DGeneration,
    setMasterPlan3DResult,
    setMasterPlan3DError,
    clearMasterPlan3D,
  } = useViewerStore();
  const mapInstance = useViewerStore((state) => state.mapInstance);

  const referenceImages = useMemo(() => collectMasterPlan2DReferences(siteZones), [siteZones]);
  const selectedReferences = useMemo(
    () => referenceImages.filter((image) => selectedImageUrls.includes(image.url)),
    [referenceImages, selectedImageUrls],
  );
  const eligible3DZones = useMemo(
    () => siteZones.filter((zone) => ['building', 'residential', 'development_area', 'road', 'green_space', 'parking', 'water'].includes(zone.zone_type)),
    [siteZones],
  );
  const activeMasterPlan3D = masterPlan3D?.projectId === projectId ? masterPlan3D : null;
  const requires3DZoneSelection = threeDScope !== 'full_site';
  const hasValid3DSelection = !requires3DZoneSelection || selected3DZoneIds.length > 0;
  const canGenerate3D = eligible3DZones.length > 0 && hasValid3DSelection;
  const threeDDisabledReason = !eligible3DZones.length
    ? 'Add at least one eligible zone with current site geometry before preparing 3D packages.'
    : !hasValid3DSelection
      ? 'Choose at least one zone for the current 3D scope.'
      : null;
  const readyPackagePreview = activeMasterPlan3D?.packages.slice(0, 4) ?? [];
  const skippedZonePreview = activeMasterPlan3D?.skippedZones.slice(0, 3) ?? [];
  const hasCameraConditioning = activeMasterPlan3D?.packages.some((pkg) => Boolean(pkg.conditioning_assets?.perspective_structure_image_url)) ?? false;


  useEffect(() => {
    const available = new Set(referenceImages.map((image) => image.url));
    setSelectedImageUrls((current) => {
      const filtered = current.filter((url) => available.has(url));
      if (filtered.length > 0) return filtered;
      return referenceImages.map((image) => image.url);
    });
  }, [referenceImages]);

  useEffect(() => {
    const available = new Set(eligible3DZones.map((zone) => zone.id));
    setSelected3DZoneIds((current) => current.filter((zoneId) => available.has(zoneId)));
  }, [eligible3DZones]);

  useEffect(() => {
    if (threeDScope === 'full_site') {
      setSelected3DZoneIds([]);
    }
  }, [threeDScope]);

  const { data: options = [], isLoading } = useQuery({
    queryKey: ['master-plan-2d-options', projectId],
    queryFn: () => masterPlan2DApi.list(projectId),
    enabled: !!projectId,
  });

  const buildRequest = async (): Promise<MasterPlan2DGenerateRequest> => {
    const mapScreenshotSatellite = renderStylePreset === 'digital_watercolor_map'
      ? undefined
      : await captureMasterPlanSatelliteUnderlay(mapInstance);

    return {
      render_style_preset: renderStylePreset,
      lighting_atmosphere_preset: lightingAtmospherePreset,
      specific_overrides: specificOverrides.trim() || undefined,
      option_count: 3,
      style_preset: stylePreset,
      quality_level: qualityLevel,
      show_legend: showLegend,
      show_north_arrow: showNorthArrow,
      show_scale_bar: showScaleBar,
      show_callout_markers: showCalloutMarkers,
      show_surrounding_context: showSurroundingContext,
      export_width: exportWidth,
      map_screenshot_satellite: mapScreenshotSatellite,
      reference_images: selectedReferences.length ? selectedReferences.map((image) => image.url) : undefined,
      reference_metadata: selectedReferences.length ? selectedReferences.map((image) => image.metadata) : undefined,
      selected_image_urls: selectedReferences.length ? selectedReferences.map((image) => image.url) : undefined,
      ai_style_pass_enabled: aiStylePassEnabled,
      ai_style_pass_provider: aiStylePassProvider,
      compose_board: true,
      board_template: 'master_plan_board_v1',
      include_photo_strip: true,
    };
  };

  const build3DRequest = (): MasterPlan3DGenerateRequest => {
    const toNumber = (value: unknown): number | undefined => {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : undefined;
    };

    const zoneSnapshots = siteZones
      .filter((zone) => zone.zone_type !== 'site_boundary' && zone.coordinates.length >= 4)
      .map((zone) => {
        const properties = zone.properties || {};
        const archetypeTitle = typeof properties.development_archetype_label === 'string'
          ? properties.development_archetype_label
          : typeof properties.road_archetype_label === 'string'
            ? properties.road_archetype_label
            : typeof properties.green_space_archetype_label === 'string'
              ? properties.green_space_archetype_label
              : typeof properties.plaza_archetype_label === 'string'
                ? properties.plaza_archetype_label
                : undefined;
        const descriptionText = typeof properties.description_text === 'string' ? properties.description_text : undefined;
        const generationStyleInput = typeof properties.generation_style_input === 'object' && properties.generation_style_input !== null
          ? properties.generation_style_input as Record<string, unknown>
          : undefined;
        const generationStyleInputs = typeof properties.generation_style_inputs === 'object' && properties.generation_style_inputs !== null
          ? properties.generation_style_inputs as Record<string, unknown>
          : undefined;

        return {
          zone_id: zone.id,
          zone_label: zone.name,
          zone_type: zone.zone_type,
          color: zone.color,
          polygon: zone.coordinates,
          height_m: toNumber(properties.height ?? properties.height_m),
          floor_count: toNumber(properties.floors ?? properties.floor_count ?? properties.floorCount),
          archetype_title: archetypeTitle,
          archetype_metadata: {
            generation_style_input: generationStyleInput,
            generation_style_inputs: generationStyleInputs,
          },
          user_notes: descriptionText,
        };
      });

    return {
      render_style_preset: renderStylePreset,
      lighting_atmosphere_preset: lightingAtmospherePreset,
      specific_overrides: specificOverrides.trim() || undefined,
      selected_perspective: threeDPerspective,
      lighting_variant: threeDLighting,
      scope: threeDScope,
      selected_zone_ids: requires3DZoneSelection ? selected3DZoneIds : undefined,
      zones: zoneSnapshots,
    };
  };

  const refreshOptions = async () => {
    await queryClient.invalidateQueries({ queryKey: ['master-plan-2d-options', projectId] });
  };

  const handleGenerate = async (mode: 'generate' | 'regenerate' = 'generate') => {
    if (!hasSiteGeometry) {
      toast.error('Draw a site boundary and plan geometry first.');
      return;
    }
    try {
      setGenerating(true);
      const request = await buildRequest();
      if (mode === 'regenerate' && options.length > 0) {
        await masterPlan2DApi.regenerate(projectId, request);
      } else {
        await masterPlan2DApi.generate(projectId, request);
      }
      await refreshOptions();
      clearMasterPlan3D();
      toast.success(mode === 'regenerate' ? '2D master plan alternatives regenerated.' : '2D master plan options generated.');
    } catch (error: any) {
      toast.error(getApiErrorMessage(error, 'Failed to generate 2D master plans.'));
    } finally {
      setGenerating(false);
    }
  };

  const handleSelect = async (option: MasterPlan2DOption) => {
    try {
      await masterPlan2DApi.select(option.id);
      await refreshOptions();
      toast.success(`${option.label} selected.`);
    } catch {
      toast.error('Failed to select this plan.');
    }
  };

  const handleExport = async (option: MasterPlan2DOption, format: 'svg' | 'png') => {
    try {
      setExportingOptionId(option.id);
      if (format === 'png' && option.full_png_url) {
        await downloadFile(option.full_png_url, `${slugify(option.label)}.png`);
      } else if (format === 'svg' && option.svg_url) {
        await downloadFile(option.svg_url, `${slugify(option.label)}.svg`);
      } else {
        const exported = await masterPlan2DApi.export(option.id, exportWidth);
        if (format === 'png' && exported.full_png_url) {
          await downloadFile(exported.full_png_url, `${slugify(option.label)}.png`);
        } else if (format === 'svg' && exported.svg_url) {
          await downloadFile(exported.svg_url, `${slugify(option.label)}.svg`);
        } else if (format === 'svg') {
          downloadText(`${slugify(option.label)}.svg`, exported.svg, 'image/svg+xml');
        } else {
          await downloadPng(`${slugify(option.label)}.png`, exported.svg, exported.width, exported.height);
        }
      }
      toast.success(`${option.label} exported as ${format.toUpperCase()}.`);
    } catch {
      toast.error(`Failed to export ${format.toUpperCase()}.`);
    } finally {
      setExportingOptionId(null);
    }
  };

  const toggle3DZone = (zoneId: string) => {
    setSelected3DZoneIds((current) => current.includes(zoneId) ? current.filter((value) => value !== zoneId) : [...current, zoneId]);
  };

  const handleGenerateTo3D = async (option: MasterPlan2DOption) => {
    if (!eligible3DZones.length) {
      toast.error('Add at least one eligible zone before generating to 3D.');
      return;
    }
    if (!hasValid3DSelection) {
      toast.error('Choose at least one zone for this 3D scope.');
      return;
    }
    try {
      const request = build3DRequest();
      setGenerating3DForOptionId(option.id);
      startMasterPlan3DGeneration({
        projectId,
        optionId: option.id,
        sourceOptionLabel: option.label,
        selectedPerspective: request.selected_perspective || 'aerial_oblique',
        lightingVariant: request.lighting_variant || 'golden_hour',
        scope: request.scope || 'full_site',
        selectedZoneIds: request.selected_zone_ids || [],
        globalStyleNotes: request.global_style_notes,
      });
      const response = await masterPlan2DApi.generate3D(option.id, request);
      setMasterPlan3DResult(projectId, response);
      const skippedCount = response.skipped_zones.length;
      const baseMessage = `${response.render_packages.length} 3D render package${response.render_packages.length === 1 ? '' : 's'} ready.`;
      toast.success(skippedCount > 0 ? `${baseMessage} ${skippedCount} zone${skippedCount === 1 ? '' : 's'} noted.` : baseMessage);
    } catch (error: unknown) {
      const message = getApiErrorMessage(error, 'Failed to generate 3D render packages.');
      setMasterPlan3DError(projectId, option.id, message);
      toast.error(message);
    } finally {
      setGenerating3DForOptionId(null);
    }
  };

  const selectedCount = selectedReferences.length;
  const stylePassLabel = aiStylePassProvider === 'auto'
    ? 'an auto AI texture pass (Gemini -> Stability)'
    : aiStylePassProvider === 'gemini'
      ? 'a Gemini texture pass'
      : 'a Stability AI texture pass';
  const loadingMessage = generating
    ? aiStylePassEnabled
      ? `Generating 3 geometry-locked rendered illustrative master plan options with ${stylePassLabel}...`
      : 'Generating 3 geometry-locked rendered illustrative master plan options...'
    : null;

  return (
    <div className="rounded-b-xl bg-[#f4f1e8] p-4 text-primary-950 sm:p-6">
      <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <section className="space-y-5 rounded-2xl border border-primary-950/10 bg-white/80 p-5 shadow-sm backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary-500">2D Master Plan Generator</p>
            <h3 className="mt-2 text-xl font-semibold text-primary-950">Presentation-grade aerial plans from your actual site geometry</h3>
            <p className="mt-2 text-sm text-primary-950/60">
              The renderer locks the stored boundary, buildings, roads, paths, parks, plazas, and water. A/B/C change graphics only, not layout.
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-primary-950">Style preset</label>
            <div className="mt-2 space-y-2">
              {STYLE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setStylePreset(option.value)}
                  className={`w-full rounded-xl border px-4 py-3 text-left transition ${stylePreset === option.value ? 'border-primary-500 bg-primary-500/10 shadow-sm' : 'border-primary-950/10 bg-white hover:border-primary-950/20'}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-medium text-primary-950">{option.label}</span>
                    {stylePreset === option.value && <CheckCircle2 size={16} className="text-primary-500" />}
                  </div>
                  <p className="mt-1 text-xs text-primary-950/60">{option.description}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-primary-950">Renderer quality</label>
            <div className="mt-2 grid gap-2">
              {QUALITY_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setQualityLevel(option.value)}
                  className={`w-full rounded-xl border px-4 py-3 text-left transition ${qualityLevel === option.value ? 'border-primary-500 bg-primary-500/10 shadow-sm' : 'border-primary-950/10 bg-white hover:border-primary-950/20'}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-medium text-primary-950">{option.label}</span>
                    {qualityLevel === option.value && <CheckCircle2 size={16} className="text-primary-500" />}
                  </div>
                  <p className="mt-1 text-xs text-primary-950/60">{option.description}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 rounded-2xl border border-primary-950/10 bg-[#f7f2e8] p-4">
            <div>
              <label className="text-sm font-medium text-primary-950">Render Style</label>
              <select
                value={renderStylePreset}
                onChange={(event) => setRenderStylePreset(event.target.value as MasterPlanRenderStylePreset)}
                className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              >
                {RENDER_STYLE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <p className="mt-2 text-xs text-primary-950/55">
                {RENDER_STYLE_OPTIONS.find((option) => option.value === renderStylePreset)?.description}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-primary-950">Lighting & Atmosphere</label>
              <select
                value={lightingAtmospherePreset}
                onChange={(event) => setLightingAtmospherePreset(event.target.value as MasterPlanLightingAtmospherePreset)}
                className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              >
                {LIGHTING_ATMOSPHERE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <p className="mt-2 text-xs text-primary-950/55">
                {LIGHTING_ATMOSPHERE_OPTIONS.find((option) => option.value === lightingAtmospherePreset)?.description}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-primary-950">Specific Overrides</label>
              <input
                value={specificOverrides}
                onChange={(event) => setSpecificOverrides(event.target.value)}
                type="text"
                placeholder="Optional: Specific details (e.g. 'Make the brick red')"
                className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              />
              <p className="mt-2 text-xs text-primary-950/55">
                Use this only for a narrow correction. The core render language now comes from the hidden preset matrix.
              </p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-primary-950">Export size</label>
            <div className="mt-2 flex gap-2">
              {EXPORT_WIDTHS.map((width) => (
                <button
                  key={width}
                  type="button"
                  onClick={() => setExportWidth(width)}
                  className={`rounded-full px-3 py-1.5 text-sm transition ${exportWidth === width ? 'bg-primary-950 text-white' : 'bg-primary-950/6 text-primary-950/70 hover:bg-primary-950/10'}`}
                >
                  {width}px
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-primary-950/10 bg-[#f7f2e8] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-primary-950">AI style pass</p>
                <p className="mt-1 text-xs text-primary-950/55">Optional AI texture finish layered over the geometry-locked renderer. Site boundaries and zone geometry stay fixed; only color, grain, planting texture, and board polish change.</p>
              </div>
              <ToggleChip icon={Sparkles} label="Enabled" checked={aiStylePassEnabled} onChange={setAiStylePassEnabled} />
            </div>
            <div className="mt-3">
              <label className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-950/50">Style pass provider</label>
              <div className="mt-2 grid gap-2">
                {STYLE_PASS_PROVIDER_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setAiStylePassProvider(option.value)}
                    className={`w-full rounded-xl border px-3 py-2 text-left transition ${aiStylePassProvider === option.value ? 'border-primary-500 bg-primary-500/10 shadow-sm' : 'border-primary-950/10 bg-white hover:border-primary-950/20'}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-primary-950">{option.label}</span>
                      {aiStylePassProvider === option.value && <CheckCircle2 size={14} className="text-primary-500" />}
                    </div>
                    <p className="mt-1 text-xs text-primary-950/55">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-primary-950">Presentation overlays</p>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              <ToggleChip icon={List} label="Legend" checked={showLegend} onChange={setShowLegend} />
              <ToggleChip icon={Compass} label="North Arrow" checked={showNorthArrow} onChange={setShowNorthArrow} />
              <ToggleChip icon={Ruler} label="Scale Bar" checked={showScaleBar} onChange={setShowScaleBar} />
              <ToggleChip icon={Layers3} label="Callout Markers" checked={showCalloutMarkers} onChange={setShowCalloutMarkers} />
            </div>
            <div className="mt-2">
              <ToggleChip icon={Sparkles} label="Surrounding Context" checked={showSurroundingContext} onChange={setShowSurroundingContext} />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between gap-3">
              <label className="text-sm font-medium text-primary-950">Reference images</label>
              <span className="text-xs text-primary-950/45">{selectedCount} of {referenceImages.length} selected</span>
            </div>
            {referenceImages.length > 0 ? (
              <div className="mt-2 grid max-h-64 gap-2 overflow-auto pr-1">
                {referenceImages.map((image) => {
                  const active = selectedImageUrls.includes(image.url);
                  return (
                    <button
                      key={image.id}
                      type="button"
                      onClick={() => setSelectedImageUrls((current) => active ? current.filter((url) => url !== image.url) : [...current, image.url])}
                      className={`flex items-center gap-3 rounded-xl border p-2 text-left transition ${active ? 'border-primary-500 bg-primary-500/10' : 'border-primary-950/10 bg-white hover:border-primary-950/20'}`}
                    >
                      <img src={image.url} alt={image.label} className="h-14 w-20 rounded-lg object-cover" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-[11px] font-semibold uppercase tracking-[0.16em] text-primary-500">{image.sourceLabel}</p>
                        <p className="truncate text-sm font-medium text-primary-950">{image.label}</p>
                        <p className="truncate text-xs text-primary-950/50">{image.zoneName}</p>
                      </div>
                      {active && <CheckCircle2 size={16} className="text-primary-500" />}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="mt-2 rounded-xl border border-dashed border-primary-950/15 bg-white/70 px-4 py-3 text-sm text-primary-950/55">
                No reference images are selected on the current zones yet. Generation will still work from geometry and zone metadata alone.
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => handleGenerate('generate')}
            disabled={generating || !hasSiteGeometry}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-primary-950/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {generating ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Generate 2D Master Plans
          </button>
          {loadingMessage && <p className="text-sm text-primary-950/60">{loadingMessage}</p>}
        </section>

        <section className="rounded-2xl border border-primary-950/10 bg-white/75 p-5 shadow-sm backdrop-blur">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary-500">Generated Options</p>
              <h3 className="mt-1 text-xl font-semibold text-primary-950">A/B/C presentation boards</h3>
            </div>
            <div className="flex items-center gap-2">
              {isLoading && <Loader2 size={18} className="animate-spin text-primary-500" />}
              {options.length > 0 && (
                <button type="button" onClick={() => handleGenerate('regenerate')} disabled={generating} className="btn-secondary text-xs">
                  {generating ? <Loader2 size={14} className="mr-1 animate-spin" /> : <RefreshCcw size={14} className="mr-1" />}
                  Regenerate
                </button>
              )}
            </div>
          </div>

          {options.length > 0 && (
            <div className="mt-5 rounded-2xl border border-primary-950/10 bg-[#f7f2e8] p-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-sm font-medium text-primary-950">2D to 3D handoff</p>
                  <p className="mt-1 text-xs text-primary-950/55">
                    Prepare structured 3D scene packages from the current geometry-locked master plan. This never auto-runs; it only starts when you click <span className="font-medium text-primary-950">Generate to 3D</span>.
                  </p>
                </div>
                {activeMasterPlan3D?.status === 'ready' && (
                  <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-[11px] font-medium text-emerald-700">
                    {activeMasterPlan3D.packages.length} package{activeMasterPlan3D.packages.length === 1 ? '' : 's'} ready
                  </span>
                )}
              </div>

              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-950/50">Perspective</label>
                  <select value={threeDPerspective} onChange={(event) => setThreeDPerspective(event.target.value as MasterPlan3DScenePerspective)} className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20">
                    {THREE_D_PERSPECTIVES.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-950/50">Lighting</label>
                  <select value={threeDLighting} onChange={(event) => setThreeDLighting(event.target.value as MasterPlan3DLightingVariant)} className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20">
                    {THREE_D_LIGHTING_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-950/50">Scope</label>
                  <select value={threeDScope} onChange={(event) => setThreeDScope(event.target.value as MasterPlan3DScope)} className="mt-2 w-full rounded-xl border border-primary-950/10 bg-white px-3 py-2 text-sm text-primary-950 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20">
                    {THREE_D_SCOPE_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                  <p className="mt-1 text-[11px] text-primary-950/50">{THREE_D_SCOPE_OPTIONS.find((option) => option.value === threeDScope)?.description}</p>
                </div>
              </div>

              {requires3DZoneSelection && (
                <div className="mt-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-950/50">Zones to include</p>
                    <span className="text-[11px] text-primary-950/45">{selected3DZoneIds.length} selected</span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {eligible3DZones.map((zone) => {
                      const active = selected3DZoneIds.includes(zone.id);
                      return (
                        <button
                          key={zone.id}
                          type="button"
                          onClick={() => toggle3DZone(zone.id)}
                          className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${active ? 'border-primary-500 bg-primary-500/10 text-primary-950' : 'border-primary-950/10 bg-white text-primary-950/65 hover:border-primary-950/20'}`}
                        >
                          {zone.name || zone.zone_type.replace(/_/g, ' ')}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {activeMasterPlan3D && (
                <div className={`mt-4 rounded-xl border px-4 py-3 ${activeMasterPlan3D.status === 'failed' ? 'border-red-200 bg-red-50/80' : 'border-primary-950/10 bg-white/80'}`}>
                  {activeMasterPlan3D.status === 'generating' && (
                    <p className="text-sm text-primary-950/65">Preparing geometry-locked 3D render packages from {activeMasterPlan3D.sourceOptionLabel || 'the current 2D plan'}...</p>
                  )}
                  {activeMasterPlan3D.status === 'ready' && (
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-primary-950">3D packages ready from {activeMasterPlan3D.sourceOptionLabel || 'the current 2D plan'}.</p>
                      <p className="text-xs text-primary-950/55">{activeMasterPlan3D.packages.length} scene package{activeMasterPlan3D.packages.length === 1 ? '' : 's'} prepared with {activeMasterPlan3D.selectedPerspective.replace(/_/g, ' ')} framing and {activeMasterPlan3D.lightingVariant.replace(/_/g, ' ')} lighting.</p>
                      <p className="text-xs text-primary-950/55">Conditioning: {hasCameraConditioning ? 'Approved 2D concept + camera-aware control maps' : 'Approved 2D concept image controls only'}.</p>
                      {activeMasterPlan3D.globalStyleNotes && (
                        <p className="text-xs text-primary-950/55">Shared direction: {activeMasterPlan3D.globalStyleNotes}</p>
                      )}
                      {readyPackagePreview.length > 0 && (
                        <div className="mt-3 grid gap-2 md:grid-cols-2">
                          {readyPackagePreview.map((pkg) => (
                            <div key={pkg.scene_id} className="rounded-xl border border-primary-950/10 bg-[#f8f5ee] px-3 py-2">
                              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary-500">{pkg.zone_label}</p>
                              <p className="mt-1 text-sm font-medium text-primary-950">{pkg.archetype_title}</p>
                              <p className="mt-1 text-xs text-primary-950/55">
                                {pkg.height_m > 0 && pkg.floor_count > 0
                                  ? `${pkg.height_m}m over ${pkg.floor_count} levels`
                                  : pkg.zone_type.replace(/_/g, ' ')}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                      {activeMasterPlan3D.packages.length > readyPackagePreview.length && (
                        <p className="text-xs text-primary-950/55">+{activeMasterPlan3D.packages.length - readyPackagePreview.length} more scene package{activeMasterPlan3D.packages.length - readyPackagePreview.length === 1 ? '' : 's'} ready for renderer handoff.</p>
                      )}
                      {activeMasterPlan3D.skippedZones.length > 0 && (
                        <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50/80 px-3 py-2">
                          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-700">Skipped or defaulted zones</p>
                          <div className="mt-2 space-y-1">
                            {skippedZonePreview.map((warning, index) => (
                              <p key={`${warning.zone_id || warning.zone_label || 'warning'}-${index}`} className="text-xs text-amber-800">
                                {(warning.zone_label || 'Selected zone')}: {warning.reason}
                              </p>
                            ))}
                          </div>
                          {activeMasterPlan3D.skippedZones.length > skippedZonePreview.length && (
                            <p className="mt-1 text-xs text-amber-700">+{activeMasterPlan3D.skippedZones.length - skippedZonePreview.length} more note{activeMasterPlan3D.skippedZones.length - skippedZonePreview.length === 1 ? '' : 's'}.</p>
                          )}
                        </div>
                      )}
                      {activeMasterPlan3D.rendererAdapter?.notes && (
                        <p className="pt-1 text-xs text-primary-950/45">Renderer handoff: {activeMasterPlan3D.rendererAdapter.notes}</p>
                      )}
                    </div>
                  )}
                  {activeMasterPlan3D.status === 'failed' && (
                    <p className="text-sm text-red-700">{activeMasterPlan3D.error || '3D package generation failed.'}</p>
                  )}
                </div>
              )}
              {threeDDisabledReason && (
                <p className="mt-3 text-xs text-primary-950/50">{threeDDisabledReason}</p>
              )}
            </div>
          )}

          {!hasSiteGeometry ? (
            <EmptyState title="Site geometry required" description="Draw the site boundary and plan geometry in Master Plan or finalize a layout in Block Editor first." />
          ) : options.length === 0 ? (
            <EmptyState title="No 2D plans generated yet" description="Choose a preset and generate a set of presentation-grade orthographic master plans." />
          ) : (
            <div className="mt-5 grid gap-5 lg:grid-cols-2 2xl:grid-cols-3">
              {options.map((option) => {
                const isExporting = exportingOptionId === option.id;
                const optionExportSize = Number(option.metadata?.export_size_px || option.metadata?.export_width || exportWidth);
                const optionQuality = typeof option.metadata?.quality_level === 'string'
                  ? String(option.metadata.quality_level).replace(/_/g, ' ')
                  : qualityLevel.replace(/_/g, ' ');
                const aiStylePass = option.metadata?.ai_style_pass as {
                  applied?: boolean;
                  requested?: boolean;
                  provider?: string;
                  provider_label?: string;
                } | undefined;
                const aiStylePassLabel = typeof aiStylePass?.provider_label === 'string' && aiStylePass.provider_label.trim().length > 0
                  ? aiStylePass.provider_label
                  : aiStylePass?.provider === 'stability'
                    ? 'Stability AI'
                    : aiStylePass?.provider === 'gemini'
                      ? 'Gemini'
                      : 'AI';
                const aiStylePassBadge = aiStylePass?.applied
                  ? `${aiStylePassLabel} Finish`
                  : aiStylePass?.requested
                    ? 'Renderer Fallback'
                    : 'Renderer Finish';
                const previewSrc = option.preview_png_url || option.preview_url;
                const isGenerating3D = generating3DForOptionId === option.id;
                const is3DReadySource = activeMasterPlan3D?.status === 'ready' && activeMasterPlan3D.optionId === option.id;
                return (
                  <article key={option.id} className="overflow-hidden rounded-2xl border border-primary-950/10 bg-[#fcfaf4] shadow-sm">
                    <button type="button" onClick={() => setPreviewOption(option)} className="block w-full bg-[#ece7da]">
                      <img src={previewSrc} alt={option.label} className="h-56 w-full object-cover" />
                    </button>
                    <div className="space-y-3 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-primary-950">{option.label}</p>
                          <p className="text-xs text-primary-950/55">{option.style_name}</p>
                        </div>
                        {option.is_selected && (
                          <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-[11px] font-medium text-emerald-600">
                            Selected
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs text-primary-950/55">
                        <span className="rounded-full bg-primary-950/6 px-2.5 py-1">{optionExportSize}px export</span>
                        <span className="rounded-full bg-primary-950/6 px-2.5 py-1">{optionQuality}</span>
                        <span className="rounded-full bg-primary-950/6 px-2.5 py-1">Geometry Locked</span>
                        <span className={aiStylePass?.applied ? 'rounded-full bg-amber-500/15 px-2.5 py-1 text-amber-700' : 'rounded-full bg-primary-950/6 px-2.5 py-1 text-primary-950/60'}>{aiStylePassBadge}</span>
                        {is3DReadySource && <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-emerald-700">3D Packages Ready</span>}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => handleGenerateTo3D(option)}
                          disabled={!canGenerate3D || !!generating3DForOptionId}
                          title={generating3DForOptionId ? 'A 3D package run is already in progress.' : (threeDDisabledReason || 'Prepare renderer-ready 3D scene packages from this 2D plan.')}
                          className="btn-secondary text-xs disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isGenerating3D ? <Loader2 size={14} className="mr-1 animate-spin" /> : <Box size={14} className="mr-1" />}
                          Generate to 3D
                        </button>
                        <button type="button" onClick={() => setPreviewOption(option)} className="btn-secondary text-xs">
                          <Eye size={14} className="mr-1" />
                          Open Full Preview
                        </button>
                        <button type="button" onClick={() => handleSelect(option)} className="btn-secondary text-xs">
                          <CheckCircle2 size={14} className="mr-1" />
                          Select this Plan
                        </button>
                        <button type="button" onClick={() => handleExport(option, 'svg')} disabled={isExporting} className="btn-secondary text-xs">
                          {isExporting ? <Loader2 size={14} className="mr-1 animate-spin" /> : <Download size={14} className="mr-1" />}
                          SVG
                        </button>
                        <button type="button" onClick={() => handleExport(option, 'png')} disabled={isExporting} className="btn-secondary text-xs">
                          {isExporting ? <Loader2 size={14} className="mr-1 animate-spin" /> : <ImageIcon size={14} className="mr-1" />}
                          PNG
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </div>

      {previewOption && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-primary-950/70 p-4 backdrop-blur-sm" onClick={() => setPreviewOption(null)}>
          <div className="max-h-[92vh] w-full max-w-6xl overflow-auto rounded-3xl bg-[#f8f4ea] p-4 shadow-2xl" onClick={(event) => event.stopPropagation()}>
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-primary-950">{previewOption.label}</p>
                <p className="text-xs text-primary-950/55">{previewOption.style_name}</p>
              </div>
              <button type="button" onClick={() => setPreviewOption(null)} className="rounded-full bg-primary-950/6 px-3 py-1 text-sm text-primary-950/70">
                Close
              </button>
            </div>
            <img src={previewOption.full_png_url || previewOption.preview_png_url || previewOption.preview_url} alt={previewOption.label} className="w-full rounded-2xl border border-primary-950/10 bg-white object-contain" />
          </div>
        </div>
      )}
    </div>
  );
}

function ToggleChip({ icon: Icon, label, checked, onChange }: { icon: typeof Compass; label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition ${checked ? 'border-primary-500 bg-primary-500/10 text-primary-950' : 'border-primary-950/10 bg-white text-primary-950/65 hover:border-primary-950/20'}`}
    >
      <Icon size={15} />
      <span>{label}</span>
    </button>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="mt-5 rounded-2xl border border-dashed border-primary-950/15 bg-white/70 px-6 py-12 text-center">
      <p className="text-base font-medium text-primary-950">{title}</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-primary-950/55">{description}</p>
    </div>
  );
}

function downloadText(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function downloadFile(url: string, filename: string) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Download failed');
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(objectUrl);
}

async function downloadPng(filename: string, svg: string, width: number, height: number) {
  const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  try {
    const image = await loadImage(url);
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Canvas context not available');
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, width, height);
    context.drawImage(image, 0, 0, width, height);
    const pngUrl = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = pngUrl;
    link.download = filename;
    link.click();
  } finally {
    URL.revokeObjectURL(url);
  }
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new window.Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });
}

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'master-plan';
}




































