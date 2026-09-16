import type { SiteZoneProperties } from '@/types';
import {
  BUILDING_AESTHETIC_CATEGORIES_V2 as DEVELOPMENT_AESTHETIC_CATEGORIES,
  ROADWAY_AESTHETIC_CATEGORIES_V2 as ROADWAY_AESTHETIC_CATEGORIES,
  GREEN_SPACE_AESTHETIC_CATEGORIES_V2 as GREEN_SPACE_AESTHETIC_CATEGORIES,
  PLAZA_AESTHETIC_CATEGORIES_V2 as PLAZA_AESTHETIC_CATEGORIES,
  type AestheticOption, type ArchetypeImage, type StyleProfile as CatalogStyleProfile,
  type GenerationStyleInput as CatalogGenerationStyleInput,
} from './aestheticCatalog';

const getFrontDayArchetypeImage = (images: ArchetypeImage[]) => images.find(image => image.id.endsWith('_variant_0'));

/** Shared saved catalogue identity for property editing and manual placement. */
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

export const buildAestheticSelectionProps = (
  current: SiteZoneProperties,
  key: 'development_aesthetic' | 'road_aesthetic' | 'green_space_aesthetic' | 'plaza_aesthetic',
  next: string | undefined,
  options: AestheticOption[],
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
