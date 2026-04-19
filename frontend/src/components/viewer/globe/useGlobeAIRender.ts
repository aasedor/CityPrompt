/**
 * useGlobeAIRender.ts — AI render pipeline for the 3D globe.
 *
 * Captures the R3F canvas screenshot (with photorealistic 3D tiles context),
 * generates a binary mask from zone polygons using Three.js camera projection,
 * builds the prompt from zone archetypes, and sends to the Gemini API.
 *
 * Key advantage over Mapbox version: the screenshot includes real 3D buildings
 * from Google Photorealistic Tiles, giving Gemini much better spatial context.
 */

import { useCallback, useRef } from 'react';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { api } from '@/services/api';
import { resolveZoneColor } from '../mapEngine/geoUtils';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';

const DEG_TO_RAD = Math.PI / 180;

// ─── SHARED STYLE PROMPTS ────────────────────────────────────────────
// Single source of truth for all render style prompts (used by single-shot, per-zone, and ground passes)
// Style prompts: the overlapping ones are imported from codex verbatim for
// richer material/lens/weathering language. Stable-only styles (spring, night,
// marker-render, collage, risograph, pixel-art) are preserved as-is. Codex-only
// styles (site-plan variants, isometric) are added.
const GLOBE_STYLE_PROMPTS: Record<string, string> = {
  photorealistic: 'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography.',
  photomontage: 'Professional architectural photomontage indistinguishable from a real drone photograph. DJI Mavic 3 at 60m altitude, Hasselblad sensor, 24mm lens f/5.6. Proposed development appears fully constructed within existing site context. Lighting and shadows match surroundings. Atmospheric haze increasing with distance. Realistic material weathering 1-2 years post-completion. Natural lens vignetting and chromatic aberration. Documentary aerial photography of an existing place.',
  atmospheric: 'Cinematic aerial architectural photograph with dramatic atmospheric conditions. CRITICAL: Replace all colored polygon fills with photorealistic building materials — real brick, stone, glass, concrete, metal roofing. No flat colored surfaces. Final minutes of golden hour, low-angle warm sunlight casting extremely long shadows. Towering cumulus clouds lit amber and rose overhead. Ground-level haze creating depth layers. Wet surfaces with mirror-like reflections. Interior lights glowing warm amber through windows. Medium format digital with exceptional dynamic range.',
  'site-plan': 'Top-down 2D architectural site plan in strict orthographic projection. Clean architectural linework with soft flat pastel colors. Stylized trees as simple green circles from above. Professional urban planning drawing quality.',
  'site-plan-photo': 'Professional near-top-down drone photomontage at 100m altitude, 15-20 degrees from nadir. DJI Mavic 3, Hasselblad sensor, 24mm lens f/5.6. Photorealistic materials, accurate short shadows, real rooftop equipment visible. Seamless integration with surrounding satellite context. Documentary drone survey photography of a completed development. CRITICAL: Replace all colored polygon fills completely with photorealistic materials. No flat green, red, blue, or orange overlay colors should remain visible.',
  'site-plan-watercolor': 'Near-top-down architectural site plan as a hand-painted watercolor on textured paper, 15-20 degrees from nadir. Soft translucent washes — warm ochre for buildings, sage green for parks, soft grey for roads, ultramarine for water. Faint pencil construction lines beneath washes. Trees as loose circular watercolor daubs. Shadows as soft blue-grey washes. White paper glowing through as highlights. Pigment granulation, wet-on-wet blooms, bleeding edges at zone boundaries. Architectural competition entry quality.',
  spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors.',
  winter: 'Photorealistic winter scene. Snow-covered roofs with drift patterns. Bare deciduous trees, snow-laden evergreens. Frosted surfaces, salt-grit on plowed paths. Soft diffuse winter light, pale blue-grey sky, long blue-tinted shadows. Specular melt/ice sheen on horizontal surfaces. Warm window glow.',
  night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
  watercolour: 'Beautiful watercolor architectural painting on textured paper. Soft bleeding edges where colors mix organically, translucent layered washes with white paper glowing through. Loose and artistic, pigment granulation in shadows. Muted earth-tone palette with sage green, ochre, and ultramarine accents.',
  charcoal: 'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows. High contrast black and white, full tonal range. Soft blended areas for atmosphere, sharp charcoal edge lines for architectural definition. Gallery-quality architectural drawing.',
  isometric: 'Isometric 3D architectural diagram with clean parallel projection and zero perspective distortion. Perfect 30-degree axonometric geometry. Smooth matte pastel colors with crisp hard edges and thin black outlines. Vector-art aesthetic, contemporary infographic style.',
  'marker-render': 'Handcrafted architectural marker rendering on smooth paper. Precise black ink linework with Copic marker shading. Visible overlapping streaky strokes following surface planes. Warm greys and ochres for facades, olive greens for landscape. White gaps for highlights.',
  'clay-maquette': 'Photorealistic macro photography of a physical architectural scale model carved from a single block of PURE WHITE matte plaster. CRITICAL: Every single element — buildings, trees, roads, parks, vehicles — is the SAME pure white material with ZERO color. No green, no gray, no brown, no color of any kind. Only white plaster with shadows defining form. Studio lighting with soft overhead softbox and deep ambient occlusion shadows. High-angle isometric view with tilt-shift miniature effect. Monochromatic white architectural maquette on white base board.',
  woodblock: 'Stylized woodblock print. Bold thick black outlines, flat limited vintage color palette of 4-6 colors with crisp separation. Visible wood grain texture. Zero gradation or blending. Graphic retro architectural illustration, museum-quality fine art print.',
  collage: 'Vibrant post-digital architectural collage as a mixed media composition. Flat unshaded colour blocks, photographic texture cut-outs with torn edges. Vintage botanical illustrations for trees. Flat illustrative lighting. Visible paper texture. Avant-garde competition aesthetic.',
  risograph: 'Risograph-printed architectural visualization. Halftone dot patterns, limited 2-3 spot color palette (fluorescent pink, teal, yellow), slight misregistration between color layers, grain texture, overprint where colors overlap.',
  'pixel-art': '16-bit pixel art architectural scene, grid-aligned with uniform square pixels. Nearest-neighbour scaling, zero anti-aliasing. Strict limited palette of 16 colors. Shading via checkerboard dithering patterns. Dark selective outlines. SNES-era JRPG city aesthetic.',
};
const catalog = [
  ...((archetypeCatalog as any)?.archetypes || []),
  ...((openSpaceCatalog as any)?.archetypes || (openSpaceCatalog as any) || []),
  ...((streetPathCatalog as any)?.archetypes || (streetPathCatalog as any) || []),
] as any[];

export interface GlobeRenderResult {
  imageUrl: string;  // data:image/png;base64,...
  prompt: string;
  seed?: number;
}

/**
 * Capture the R3F canvas as a base64 JPEG string.
 * JPEG at 85% quality reduces payload from ~2-5MB (PNG) to ~300-800KB,
 * significantly reducing API call latency.
 * Requires Canvas gl={{ preserveDrawingBuffer: true }}
 */
function captureCanvasBase64(canvas: HTMLCanvasElement): Promise<string> {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      if (!blob) { resolve(''); return; }
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1]); // Raw base64 without prefix
      };
      reader.readAsDataURL(blob);
    }, 'image/jpeg', 0.85);
  });
}

/**
 * Project a [lng, lat] coordinate to screen pixels using Three.js camera.
 */
function projectToPixels(
  lng: number, lat: number, height: number,
  camera: THREE.Camera, width: number, height_px: number,
): { x: number; y: number } | null {
  const pos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, height, pos);
  pos.project(camera);

  // Behind camera check
  if (pos.z > 1) return null;

  return {
    x: (pos.x + 1) / 2 * width,
    y: (1 - pos.y) / 2 * height_px,
  };
}

// ─── OCCLUSION CULLING ─────────────────────────────────────────────────

/**
 * Check which zones are significantly occluded by other (taller) zones
 * in screen space. Returns a Set of zone IDs that should be culled.
 *
 * Algorithm: For each zone, render all OTHER building zones (that are taller
 * or in front) as filled polygons onto a test canvas, then check how many
 * pixels of the target zone's footprint are covered.
 * If >60% covered, the zone is occluded and should be removed from the prompt.
 */
function findOccludedZones(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
  threshold = 0.95,
): Set<string> {
  const occluded = new Set<string>();
  const renderZones = zones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);

  // Project all zones to screen pixels and calculate their properties
  const projected = renderZones.map(zone => {
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    // Project roof height too for buildings
    const roofPixels = buildingHeight > 0
      ? zone.coordinates
          .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
          .filter(Boolean) as { x: number; y: number }[]
      : [];

    // Average Y position (lower Y = higher on screen = closer to camera in oblique view)
    const avgY = pixels.length > 0 ? pixels.reduce((s, p) => s + p.y, 0) / pixels.length : 0;

    return { zone, pixels, roofPixels, buildingHeight, avgY };
  });

  // Use a small canvas for fast pixel testing (1/4 resolution)
  const scale = 0.25;
  const sw = Math.round(width * scale);
  const sh = Math.round(height * scale);

  // Ground-level zone types should never be culled — they're visible between buildings
  const GROUND_TYPES = new Set(['water', 'green_space', 'park', 'parking', 'road', 'street', 'path', 'plaza', 'development_area']);

  for (const target of projected) {
    if (target.pixels.length < 3) continue;
    if (GROUND_TYPES.has(target.zone.zone_type)) continue; // Never cull ground zones

    // Find zones that could occlude this one:
    // - taller buildings whose screen footprint overlaps
    // - zones that are closer to camera (lower avgY in oblique view)
    const occluders = projected.filter(other =>
      other.zone.id !== target.zone.id &&
      other.pixels.length >= 3 &&
      (other.buildingHeight > target.buildingHeight || other.avgY > target.avgY) &&
      ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(other.zone.zone_type),
    );

    if (occluders.length === 0) continue;

    // Draw target zone footprint
    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = sw;
    targetCanvas.height = sh;
    const targetCtx = targetCanvas.getContext('2d')!;
    targetCtx.fillStyle = '#ffffff';
    targetCtx.beginPath();
    targetCtx.moveTo(target.pixels[0].x * scale, target.pixels[0].y * scale);
    for (let i = 1; i < target.pixels.length; i++) {
      targetCtx.lineTo(target.pixels[i].x * scale, target.pixels[i].y * scale);
    }
    targetCtx.closePath();
    targetCtx.fill();

    // Count target pixels
    const targetData = targetCtx.getImageData(0, 0, sw, sh).data;
    let targetPixelCount = 0;
    for (let i = 0; i < targetData.length; i += 4) {
      if (targetData[i] > 128) targetPixelCount++;
    }
    if (targetPixelCount === 0) continue;

    // Draw occluder buildings (footprint + height extent) on top
    const occluderCanvas = document.createElement('canvas');
    occluderCanvas.width = sw;
    occluderCanvas.height = sh;
    const occCtx = occluderCanvas.getContext('2d')!;

    for (const occ of occluders) {
      occCtx.fillStyle = '#ffffff';
      // Draw footprint
      occCtx.beginPath();
      occCtx.moveTo(occ.pixels[0].x * scale, occ.pixels[0].y * scale);
      for (let i = 1; i < occ.pixels.length; i++) {
        occCtx.lineTo(occ.pixels[i].x * scale, occ.pixels[i].y * scale);
      }
      // Extend upward with roof pixels for 3D height
      if (occ.roofPixels.length >= 3) {
        for (const p of occ.roofPixels) {
          occCtx.lineTo(p.x * scale, p.y * scale);
        }
      }
      occCtx.closePath();
      occCtx.fill();
    }

    // Check overlap: how many target pixels are covered by occluders
    const occData = occCtx.getImageData(0, 0, sw, sh).data;
    let coveredCount = 0;
    for (let i = 0; i < targetData.length; i += 4) {
      if (targetData[i] > 128 && occData[i] > 128) coveredCount++;
    }

    const coverageRatio = coveredCount / targetPixelCount;
    if (coverageRatio >= threshold) {
      occluded.add(target.zone.id || '');
      console.log(`[GlobeAIRender] Occlusion: "${target.zone.name || target.zone.zone_type}" is ${(coverageRatio * 100).toFixed(0)}% occluded — CULLED from prompt`);
    }
  }

  if (occluded.size > 0) {
    console.log(`[GlobeAIRender] Occlusion culling: ${occluded.size} zone(s) removed from render`);
  }

  return occluded;
}

/**
 * Generate a COLOR-CODED mask from zone polygons.
 * Each zone drawn in its actual map color so Gemini can match the COLOR-TO-ZONE legend.
 * Black = keep as-is, colored = render this zone.
 */
function generateMask(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  // Start with black (preserve everything)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  // If site boundary exists, clip all zone rendering to within it
  const siteBoundary = zones.find(z => z.zone_type === 'site_boundary' && z.coordinates?.length >= 3);
  if (siteBoundary) {
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    if (boundaryPixels.length >= 3) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(boundaryPixels[0].x, boundaryPixels[0].y);
      for (let i = 1; i < boundaryPixels.length; i++) ctx.lineTo(boundaryPixels[i].x, boundaryPixels[i].y);
      ctx.closePath();
      ctx.clip(); // All subsequent drawing is clipped to the boundary
      console.log(`[GlobeAIRender] Mask clipped to site boundary (${boundaryPixels.length} vertices)`);
    }
  }

  // Draw each zone as WHITE (binary mask) with ~2m dilation — skip site_boundary
  // Binary mask: white = edit area, black = preserve. No colors in the mask.
  // Zone identification comes from the colored polygons already visible in the
  // screenshot + prompt text + archetype reference images.
  // The dilation gives Gemini "peripheral vision" to see adjacent context.
  const DILATION_PX = 8; // ~2m at typical aerial zoom
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    if (pixels.length < 3) continue;

    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x, pixels[i].y);
    }
    ctx.closePath();

    // For buildings, expand upward to include building height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2
      || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
        .filter(Boolean) as { x: number; y: number }[];

      if (topPixels.length >= 3) {
        for (const p of topPixels) ctx.lineTo(p.x, p.y);
      }
    }

    ctx.fill();
    ctx.stroke(); // Dilation: thick white stroke adds ~2m bleed room
  }

  // Restore context (remove clip)
  if (siteBoundary) ctx.restore();

  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Compress an image blob to JPEG at a target max width.
 * Returns base64 string without data URI prefix.
 */
function compressImage(blob: Blob, maxWidth = 512, quality = 0.7): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxWidth / img.naturalWidth);
      const w = Math.round(img.naturalWidth * scale);
      const h = Math.round(img.naturalHeight * scale);

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, w, h);

      canvas.toBlob((outBlob) => {
        if (!outBlob) return reject(new Error('Compression failed'));
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.readAsDataURL(outBlob);
      }, 'image/jpeg', quality);
    };
    img.onerror = () => reject(new Error('Failed to load image for compression'));
    img.src = URL.createObjectURL(blob);
  });
}

/** Cap on total reference images sent to Gemini. Raised from 6 → 48 to allow
 *  multi-angle references per zone (street-level + 30°/60°/90° aerials).
 *  Per pilot memory: Gemini accepts ~3600 images / 20MB total; 48 at ~40KB
 *  each = ~2MB, well within limits. Sweet spot for reference-count was 3
 *  angles per zone (street + 60° + 90°), so up to ~16 zones × 3 = 48. */
const MAX_ARCHETYPE_IMAGES = 48;

/** Aerial angle suffixes to look for alongside the street-level variant_N.png.
 *  Files are named `variant_N_angle_XX.jpg` where XX is one of these values.
 *  Order matters — each zone's refs go to Gemini in this order. Street-level
 *  always comes first; then aerials from low-oblique to top-down. */
const AERIAL_ANGLE_SUFFIXES: Array<{ suffix: number; label: string }> = [
  { suffix: 30, label: '30° low-oblique aerial' },
  { suffix: 60, label: '60° steep-oblique aerial' },
  { suffix: 90, label: '90° nadir / top-down aerial' },
];

/**
 * Collect archetype reference card images for multi-image rendering.
 *
 * For each zone, discovers and loads up to 4 reference images:
 *   1. street-level (the variant_N.png thumbnail)
 *   2. 30° low-oblique aerial (variant_N_angle_30.jpg, if present)
 *   3. 60° steep-oblique aerial (variant_N_angle_60.jpg, if present)
 *   4. 90° nadir / top-down aerial (variant_N_angle_90.jpg, if present)
 *
 * Each image is compressed to 512px JPEG @ 0.7 (~30-50KB) and tagged with
 * the viewing angle so the prompt can explain what each reference shows.
 *
 * Aerial variants that don't exist on disk (most archetypes don't have them
 * generated yet — pilot covers only 4 building + 3 open-space archetypes)
 * are silently skipped; the zone falls back to just its street-level ref.
 */
async function collectArchetypeImages(
  zones: SiteZone[],
): Promise<Array<{ image_base64: string; label: string; zone_color: string; angle: string }>> {
  const images: Array<{ image_base64: string; label: string; zone_color: string; angle: string }> = [];

  for (const zone of zones) {
    if (images.length >= MAX_ARCHETYPE_IMAGES) break;
    if (zone.zone_type === 'site_boundary') continue;

    const props = zone.properties || {};
    const archetypeId = (props.development_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || (props.road_archetype_id as string)
      || (props.plaza_archetype_id as string)
      || (props.development_subcategory as string)
      || (props.green_space_subcategory as string)
      || '';

    // Selected variant ID is stored separately from the parent archetype ID.
    // Without this, we'd always resolve to the archetype's hero.png and miss
    // the user's actual variant choice. See `ZonePropertiesPanel.tsx:470`.
    const selectedVariantId = (props.development_selected_variant_id as string)
      || (props.green_space_selected_variant_id as string)
      || (props.road_selected_variant_id as string)
      || (props.plaza_selected_variant_id as string)
      || '';

    if (!archetypeId) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — no archetype ID`);
      continue;
    }

    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" not found in catalog`);
      continue;
    }

    // Resolve the specific variant the user selected. Preference order:
    //   1. Variant whose id matches `*_selected_variant_id`.
    //   2. Variant whose id matches the archetypeId directly (legacy).
    //   3. First variant in the list (sensible default — avoids hero.png).
    //   4. Parent entry.thumbnailUrl (last resort — usually the hero).
    let variant: any = null;
    if (Array.isArray(entry.variants) && entry.variants.length > 0) {
      if (selectedVariantId) {
        variant = entry.variants.find((v: any) => v.id === selectedVariantId);
      }
      if (!variant) {
        variant = entry.variants.find((v: any) => v.id === archetypeId);
      }
      if (!variant) {
        variant = entry.variants[0];
      }
    }
    const thumbnailUrl: string | undefined = variant?.thumbnailUrl || entry.thumbnailUrl;
    if (!thumbnailUrl) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" has no thumbnailUrl`);
      continue;
    }
    if (variant) {
      console.log(`[GlobeAIRender] Zone variant resolved: archetype="${archetypeId}" → variant="${variant.id}" → ${thumbnailUrl}`);
    } else {
      console.warn(`[GlobeAIRender] Zone "${zone.name || zone.zone_type}" has no variant — using parent hero (${thumbnailUrl}). Aerial refs won't match.`);
    }

    const zoneColor = colorName(resolveZoneColor(zone));
    const title = entry.title || archetypeId;

    // Build the list of thumbnail stems we'll probe for aerials.
    //   1. The SELECTED variant's stem (preferred — exact archetype match).
    //   2. ALL other variants of the same archetype as fallback.
    // If the user picked variant 0 but we only generated aerials for
    // variant 3 of the same archetype, the fallback still finds them.
    // Variants within an archetype share the archetype's functional type,
    // so even a fallback aerial is the right *typology* of reference.
    const stripExt = (u: string) => u.replace(/\.[^./]+$/, '');
    const selectedStem = stripExt(thumbnailUrl);
    const stems: string[] = [selectedStem];
    if (Array.isArray(entry.variants)) {
      for (const v of entry.variants) {
        if (v.thumbnailUrl) {
          const s = stripExt(v.thumbnailUrl);
          if (!stems.includes(s)) stems.push(s);
        }
      }
    }

    console.log(`[GlobeAIRender] Zone "${zone.name || zone.zone_type}" → archetype="${archetypeId}", selected stem=${selectedStem}, ${stems.length - 1} fallback stem(s)`);

    // 1. Street-level: always the selected variant's thumbnail (no fallback).
    if (images.length < MAX_ARCHETYPE_IMAGES) {
      try {
        const resp = await fetch(thumbnailUrl);
        if (resp.ok) {
          const blob = await resp.blob();
          const base64 = await compressImage(blob, 512, 0.7);
          const sizeKB = Math.round(base64.length * 0.75 / 1024);
          console.log(`[GlobeAIRender] Archetype image: ${title} [street-level ground view] — ${sizeKB}KB`);
          images.push({
            image_base64: base64,
            label: `${title} — street-level ground view`,
            zone_color: zoneColor,
            angle: 'street-level ground view',
          });
        } else {
          console.warn(`[GlobeAIRender] street-level fetch ${resp.status}: ${thumbnailUrl}`);
        }
      } catch (e) {
        console.warn(`[GlobeAIRender] street-level fetch error: ${thumbnailUrl}`, e);
      }
    }

    // 2. Aerial angles: probe selected stem first, then fall back to other
    //    variants of the same archetype. Use the first hit per angle.
    for (const angleConfig of AERIAL_ANGLE_SUFFIXES) {
      if (images.length >= MAX_ARCHETYPE_IMAGES) break;
      let found = false;
      for (const stem of stems) {
        const url = `${stem}_angle_${angleConfig.suffix}.jpg`;
        try {
          const resp = await fetch(url);
          if (!resp.ok) continue;
          const blob = await resp.blob();
          const base64 = await compressImage(blob, 512, 0.7);
          const sizeKB = Math.round(base64.length * 0.75 / 1024);
          const fallbackNote = stem === selectedStem ? '' : ' (fallback variant)';
          console.log(`[GlobeAIRender] Archetype image: ${title} [${angleConfig.label}]${fallbackNote} — ${sizeKB}KB`);
          images.push({
            image_base64: base64,
            label: `${title} — ${angleConfig.label}`,
            zone_color: zoneColor,
            angle: angleConfig.label,
          });
          found = true;
          break;
        } catch {
          /* probe next stem */
        }
      }
      if (!found) {
        console.log(`[GlobeAIRender]   no ${angleConfig.label} found for ${title} (tried ${stems.length} stem(s))`);
      }
    }
  }

  return images;
}

// ─── COLOR NAMING ──────────────────────────────────────────────────────

function hexToHsl(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return [0, 0, l * 100];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;
  return [h * 360, s * 100, l * 100];
}

/**
 * Map hex color to a visually descriptive, unique name for prompts.
 * Uses specific color vocabulary so Gemini can distinguish similar shades.
 * Always includes the hex value for precise matching.
 */
function colorName(hex: string): string {
  const normalized = hex.toLowerCase();
  const knownNames: Record<string, string> = {
    '#e03c31': 'bright vermillion',
    '#ff6b6b': 'light coral pink',
    '#e8927c': 'warm salmon',
    '#f5a623': 'vivid amber',
    '#ffd700': 'bright gold',
    '#ffeb3b': 'lemon yellow',
    '#f0e68c': 'pale khaki',
    '#4caf50': 'medium green',
    '#66bb6a': 'fresh spring green',
    '#2e7d32': 'deep forest green',
    '#009688': 'dark teal',
    '#4169e1': 'royal blue',
    '#3f51b5': 'deep indigo',
    '#2196f3': 'sky blue',
    '#9c27b0': 'rich purple',
    '#795548': 'warm brown',
    '#607d8b': 'cool blue-grey',
    '#bdbdbd': 'light silver',
    '#c62828': 'deep maroon',
    '#d84315': 'burnt sienna',
    '#ad1457': 'dark magenta',
    '#6a1b9a': 'deep violet',
    '#4527a0': 'dark royal purple',
    '#b71c1c': 'dark crimson',
    '#e65100': 'dark burnt orange',
    '#ff5722': 'bright orange-red',
    '#ff9800': 'bright orange',
    '#8bc34a': 'lime green',
    '#00bcd4': 'bright cyan',
    '#e91e63': 'hot pink',
    '#ff7043': 'warm tangerine',
    '#a1887f': 'dusty mauve',
    '#90a4ae': 'steel grey',
  };

  const name = knownNames[normalized];
  if (name) return `${name} ${hex}`;

  try {
    const [h, s, l] = hexToHsl(hex);
    const lightDesc = l < 25 ? 'very dark ' : l < 40 ? 'dark ' : l > 75 ? 'very light ' : l > 60 ? 'light ' : '';
    const satDesc = s < 20 ? 'muted ' : s > 80 ? 'vivid ' : '';
    let hueName = 'brown';
    if (h < 10 || h >= 350) hueName = 'red';
    else if (h < 20) hueName = 'red-orange';
    else if (h < 35) hueName = 'orange';
    else if (h < 50) hueName = 'amber-orange';
    else if (h < 65) hueName = 'golden yellow';
    else if (h < 80) hueName = 'yellow-green';
    else if (h < 140) hueName = 'green';
    else if (h < 170) hueName = 'teal-green';
    else if (h < 200) hueName = 'cyan';
    else if (h < 230) hueName = 'blue';
    else if (h < 260) hueName = 'blue-violet';
    else if (h < 290) hueName = 'purple';
    else if (h < 320) hueName = 'magenta';
    else if (h < 350) hueName = 'rose';
    return `${lightDesc}${satDesc}${hueName} ${hex}`;
  } catch {
    return hex;
  }
}

/**
 * Get the map overlay render prompt for a zone's archetype.
 */
function getMapOverlayPrompt(zone: SiteZone): string | undefined {
  const props = zone.properties || {};
  const archetypeId = (props.development_archetype_id as string)
    || (props.green_space_archetype_id as string)
    || (props.road_archetype_id as string)
    || (props.plaza_archetype_id as string)
    || '';

  if (!archetypeId) return undefined;

  const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
  if (!entry) return undefined;

  // Check for variant-specific description (e.g., "cul_de_sac_v2" → European cobblestone variant)
  const variant = entry.variants?.find((v: any) => v.id === archetypeId);
  const variantDesc = variant?.description ? ` Style: ${variant.description}` : '';

  const base = entry.renderPrompt?.mapOverlay || entry.prompt?.subject || '';
  return base ? `${base}${variantDesc}` : variantDesc || undefined;
}

/**
 * Extract archetype metadata from zone properties.
 */
function getZoneArchetypeInfo(zone: SiteZone): {
  archetypeTitle?: string;
  facadeDescription?: string;
  roofDescription?: string;
  materials?: string;
  aerialAppearance?: string;
  publicRealm?: string;
  colorScheme?: string;
  corridorCharacter?: string;
  minFloors?: number;
  maxFloors?: number;
  suggestedAreaSqm?: number;
  heightTendency?: string;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  aspectRatio?: string;
  typicalWidth_m?: number; // streets
} {
  if (!zone.properties || !catalog) return {};

  for (const prefix of ['development', 'road', 'green_space', 'plaza'] as const) {
    const archetypeId = zone.properties[`${prefix}_archetype_id`] as string | undefined;
    if (!archetypeId) continue;

    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry) continue;

    const sp = entry.styleProfile || {};
    const fd = entry.facadeDetail || {};
    const rd = entry.roofDetail || {};

    const facadeParts: string[] = [];
    if (fd.primaryMaterial) facadeParts.push(fd.primaryMaterial);
    if (fd.groundFloor) facadeParts.push(fd.groundFloor);
    if (fd.upperFloors) facadeParts.push(fd.upperFloors);
    if (fd.colorScheme) facadeParts.push(fd.colorScheme);

    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.aerialAppearance) roofParts.push(rd.aerialAppearance);

    return {
      archetypeTitle: entry.title,
      facadeDescription: facadeParts.join(', ') || undefined,
      roofDescription: roofParts.join(', ') || undefined,
      materials: Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials,
      aerialAppearance: rd.aerialAppearance || undefined,
      publicRealm: sp.publicRealm || undefined,
      colorScheme: fd.colorScheme || undefined,
      corridorCharacter: sp.corridorCharacter || undefined,
      minFloors: entry.minFloors || undefined,
      maxFloors: entry.maxFloors || undefined,
      suggestedAreaSqm: entry.suggestedAreaSqm || undefined,
      heightTendency: sp.heightTendency || undefined,
      suggestedWidth_m: entry.suggestedWidth_m || undefined,
      suggestedDepth_m: entry.suggestedDepth_m || undefined,
      aspectRatio: entry.aspectRatio || undefined,
      typicalWidth_m: entry.typicalWidth_m || undefined,
    };
  }
  return {};
}

/**
 * Build SCHEMA-style structured prompt for aerial renders.
 * Based on the proven Mapbox aerial prompt structure.
 */
function buildPrompt(zones: SiteZone[], style: string, camera?: THREE.Camera, terrainHeight?: number): string {
  // --- CAMERA ANGLE ---
  let pitchDesc = 'oblique aerial (~50°)';
  if (camera && terrainHeight != null) {
    // Estimate pitch from camera direction vs surface normal
    const camDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
    const camPos = camera.position.clone().normalize(); // surface normal at camera position
    const cosAngle = Math.abs(camDir.dot(camPos.clone().negate()));
    const pitchDeg = Math.round(Math.acos(Math.min(1, cosAngle)) * 180 / Math.PI);
    if (pitchDeg < 20) pitchDesc = `near top-down (~${pitchDeg}°)`;
    else if (pitchDeg < 40) pitchDesc = `steep aerial (~${pitchDeg}°)`;
    else if (pitchDeg < 60) pitchDesc = `oblique aerial (~${pitchDeg}°)`;
    else pitchDesc = `low-angle oblique (~${pitchDeg}°)`;
    console.log(`[GlobeAIRender] Camera pitch: ${pitchDeg}° → "${pitchDesc}"`);
  }

  // --- COMPOSITION ---
  const hasBuildings = zones.some(z => z.zone_type === 'building' || z.zone_type === 'residential');
  const composition = hasBuildings
    ? `${pitchDesc} view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context. Render buildings with correct 3D perspective for this viewing angle.`
    : `${pitchDesc} view, ground-level zones only on photorealistic 3D terrain.`;

  // --- LIGHTING ---
  const lightingMap: Record<string, string> = {
    photorealistic: 'Golden hour, low warm southwest sun creating strong directional light. Long crisp architectural shadows with deep material contrast — sunlit facades should read bright and textured, shadowed facades cool and recessive. Sharp highlight-to-shadow transitions emphasizing facade depth (cornices, mullions, balcony edges, podium returns) rather than flat global illumination.',
    winter: 'Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky.',
    atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze.',
    spring: 'Bright spring midday sun, vivid colors, fresh green light.',
    night: 'Moonlight and city glow, artificial lighting, warm window light.',
  };

  // --- ZONES (SCHEMA format) — skip site_boundary, sort by polygon area descending ---
  // Largest zones first = most visually dominant archetypes get highest attention weight
  const renderZones = zones
    .filter(z => z.zone_type !== 'site_boundary')
    .sort((a, b) => {
      const polyArea = (z: SiteZone) => {
        if (!z.coordinates || z.coordinates.length < 3) return 0;
        let area = 0;
        for (let i = 0; i < z.coordinates.length; i++) {
          const j = (i + 1) % z.coordinates.length;
          area += z.coordinates[i][0] * z.coordinates[j][1];
          area -= z.coordinates[j][0] * z.coordinates[i][1];
        }
        return Math.abs(area / 2);
      };
      return polyArea(b) - polyArea(a);
    });
  // --- POSITION ANCHORING (screen-space quadrant per zone) ---
  // Gives Gemini a SECOND identification axis alongside color, reducing the
  // "wrong archetype at wrong polygon" failure mode when fill colors alone
  // aren't discriminating. We use SCREEN-SPACE position (upper-left, center,
  // lower-right, etc.) — not cardinal direction — because Gemini sees a 2D
  // image from some oblique camera bearing, not a north-up map. Screen
  // position is verifiable against pixels Gemini actually sees; cardinal
  // direction would require Gemini to know which way is north.
  const screenPositionForZone = (zone: SiteZone): string => {
    const coords = zone.coordinates || [];
    if (coords.length === 0) return 'CENTER';
    if (!camera || terrainHeight == null) return 'CENTER';
    const lng = coords.reduce((s, c) => s + c[0], 0) / coords.length;
    const lat = coords.reduce((s, c) => s + c[1], 0) / coords.length;
    // Project to a normalized 1000×1000 virtual frame — we only care about
    // the relative quadrant, not absolute pixel values, so the exact size
    // doesn't matter.
    const W = 1000;
    const H = 1000;
    const pixel = projectToPixels(lng, lat, terrainHeight, camera, W, H);
    if (!pixel) return 'BEHIND-CAMERA'; // Gemini won't render it anyway
    const fx = pixel.x / W; // 0 = left, 1 = right
    const fy = pixel.y / H; // 0 = top, 1 = bottom (screen coords)
    // 3×3 grid buckets, relaxed middle band for "center-ish" zones
    const colLeft = fx < 0.35, colRight = fx >= 0.65;
    const rowTop = fy < 0.35, rowBot = fy >= 0.65;
    if (rowTop && colLeft) return 'UPPER-LEFT';
    if (rowTop && colRight) return 'UPPER-RIGHT';
    if (rowTop) return 'UPPER-CENTER';
    if (rowBot && colLeft) return 'LOWER-LEFT';
    if (rowBot && colRight) return 'LOWER-RIGHT';
    if (rowBot) return 'LOWER-CENTER';
    if (colLeft) return 'MIDDLE-LEFT';
    if (colRight) return 'MIDDLE-RIGHT';
    return 'CENTER';
  };

  const zoneLines: string[] = [];
  for (let i = 0; i < renderZones.length; i++) {
    const zone = renderZones[i];
    const color = colorName(resolveZoneColor(zone));
    const position = screenPositionForZone(zone);
    const props = zone.properties || {};
    const info = getZoneArchetypeInfo(zone);

    const floors = (props.floors as number) || 0;
    const heightM = (props.height_m as number) || (props.height as number) || floors * 3.2 || 0;
    const name = info.archetypeTitle || zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type;

    // Scale descriptor
    let scale = '';
    if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
      if (floors > 0 && heightM > 0) scale = `${floors}F ${Math.round(heightM)}m`;
      else if (floors > 0) scale = `${floors}F`;
      else if (heightM > 0) scale = `${Math.round(heightM)}m`;
      else if (info.minFloors && info.maxFloors) {
        scale = info.minFloors === info.maxFloors ? `${info.minFloors}F` : `${info.minFloors}-${info.maxFloors}F`;
      } else scale = 'multi-story';
      if (info.suggestedWidth_m && info.suggestedDepth_m) scale += ` ~${info.suggestedWidth_m}×${info.suggestedDepth_m}m`;
      else if (info.suggestedAreaSqm) scale += ` ~${info.suggestedAreaSqm}m²`;
    } else {
      scale = 'gnd';
    }

    // Map overlay prompt (archetype-specific aerial rendering instruction)
    const overlayPrompt = getMapOverlayPrompt(zone);

    // Feature keywords from archetype metadata
    const features: string[] = [];
    if (overlayPrompt) {
      // Use the archetype's own rendering instruction if available
      features.push(overlayPrompt);
    } else {
      if (info.facadeDescription) features.push(info.facadeDescription);
      if (info.roofDescription) features.push(info.roofDescription);
      if (info.materials) features.push(info.materials);
      if (info.aerialAppearance) features.push(`Aerial: ${info.aerialAppearance}`);
      if (info.publicRealm) features.push(info.publicRealm);
    }

    // User description override
    const userDesc = (props.description as string) || (props.descriptive_text as string) || '';
    if (userDesc.length > 10) features.push(userDesc);

    const featureStr = features.join(', ').substring(0, 200);
    zoneLines.push(`${i + 1}. [${color}] @ ${position} of frame | ${name} | ${scale} | ${featureStr || 'render as described'}`);
  }

  // --- ASSEMBLE SCHEMA PROMPT ---
  const sections = [
    `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`,
    `COMPOSITION: ${composition}`,
    `LIGHTING: ${lightingMap[style] || lightingMap.photorealistic}`,
    `CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.`,
    `COLOR TEMPERATURE MATCHING: Analyze the color temperature and atmospheric conditions of the EXISTING buildings and terrain in the photograph. Match the EXACT same warm/cool tone, haze level, and ambient light color on all rendered zones. If the scene has golden-hour warmth, render buildings with the same warm amber tones — NOT neutral daylight grey. Rendered materials must look like they exist in the same atmosphere and light as the surrounding real buildings.`,
    `ATMOSPHERIC PERSPECTIVE: Apply the same atmospheric haze and aerial perspective visible on surrounding buildings at similar distances. Distant rendered zones should have reduced contrast and shifted color matching the existing depth cues in the photograph.`,
    `NUMERICAL INVENTORY: This scene contains exactly ${renderZones.length} zone${renderZones.length > 1 ? 's' : ''}: ${renderZones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length} building${renderZones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length !== 1 ? 's' : ''}, ${renderZones.filter(z => z.zone_type === 'green_space').length} park${renderZones.filter(z => z.zone_type === 'green_space').length !== 1 ? 's' : ''}, ${renderZones.filter(z => z.zone_type === 'road').length} road${renderZones.filter(z => z.zone_type === 'road').length !== 1 ? 's' : ''}.`,
    `ZONES:\n${zoneLines.join('\n')}`,
    `ZONE IDENTIFICATION: Each zone polygon has TWO visual identifiers: (1) its archetype name written as colored text on the polygon, and (2) a unique bright DASHED BORDER in a distinct color (red, blue, magenta, cyan, yellow, etc.). The text label color matches the border color. Use BOTH the text label AND the border color to identify each zone. Zones with similar fill colors can be distinguished by their different border colors. Road/street zones can be distinguished from existing roads by their dashed border — only polygons with dashed borders are zones to render.`,
    `ZONE ASSIGNMENT: Each zone line in the ZONES list above begins with "@ SCREEN-POSITION" (values: UPPER-LEFT, UPPER-CENTER, UPPER-RIGHT, MIDDLE-LEFT, CENTER, MIDDLE-RIGHT, LOWER-LEFT, LOWER-CENTER, LOWER-RIGHT) — this is the location of that zone's polygon within THIS image's 2D frame. It is a THIRD identification axis alongside color and text label. Verify color, label, AND screen position all match before rendering an archetype at a polygon. If a line says "[magenta] @ LOWER-RIGHT | Grand Magasin", render the Grand Magasin archetype at the polygon in the lower-right region of the frame — NOT at a polygon elsewhere even if its color looks similar. Never swap archetypes between polygons. When two zones have similar fill colors, the SCREEN-POSITION resolves the ambiguity — trust the position anchor over color similarity.`,
    `MANDATORY: The white mask shows the EXACT area to edit. Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials. Read the text label on each polygon to identify what to render there. Realistic rooftop materials, facades, and landscaping. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`,
    `PROHIBITIONS: colored polygon fills visible on ANY rendered surface (rooftops, facades, ground), dashed boundary lines or outlines visible, text labels visible, watermarks, color temperature mismatch between rendered and existing buildings, rendered buildings appearing unnaturally crisp or clean compared to surroundings${style === 'winter' ? ', lush green vegetation, summer foliage, bright green lawns' : ''}`,
    `SITE BOUNDARY: Do NOT add any NEW buildings, structures, roads, people, vehicles, or landscaping outside the colored zone polygons. However, rendered zones MUST blend seamlessly into the surrounding landscape at their edges — match lighting, ground plane, and context so there is no visible seam between rendered and existing areas.`,
    `OCCLUSION: Some zones may be partially or fully hidden behind taller buildings from this camera angle. This is CORRECT — do NOT distort the perspective to make hidden zones visible. If a zone is occluded by a building in front of it, leave it hidden. Render only what would naturally be visible from this specific camera position and angle.`,
    `FINAL CONSTRAINT: Stay strictly within each colored zone polygon. Do not alter pixels outside the mask. Accuracy to the polygon boundary is more important than architectural flair. Each zone renders ONLY within its own colored boundary — never overlapping into adjacent zones.`,
  ];

  return sections.join('\n');
}

// ─── POST-PROCESSING: POLYGON CLIP ─────────────────────────────────────

/**
 * Load an image from a data URI and return an HTMLImageElement.
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(new Error(`Failed to load image: ${e}`));
    img.src = src;
  });
}

/**
 * Post-process: clip the AI render to zone polygons with feathered edges.
 * For each zone, only keep the AI render within that zone's polygon
 * (with a soft 6px blur feather). Everything outside zone polygons
 * reverts to the original screenshot.
 *
 * This is the "fail-safe" — no matter what Gemini produces, each zone
 * only shows within its polygon boundary.
 */
async function clipRenderToZones(
  originalBase64: string,
  renderedBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): Promise<string> {
  const [origImg, rendImg] = await Promise.all([
    loadImage(`data:image/png;base64,${originalBase64}`),
    loadImage(`data:image/png;base64,${renderedBase64}`),
  ]);

  const w = origImg.naturalWidth;
  const h = origImg.naturalHeight;

  // Start with the original screenshot as the base
  const resultCanvas = document.createElement('canvas');
  resultCanvas.width = w;
  resultCanvas.height = h;
  const resultCtx = resultCanvas.getContext('2d')!;
  resultCtx.drawImage(origImg, 0, 0, w, h);

  // Build a combined feathered mask for ALL non-boundary zones
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    // Draw zone polygon
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
    maskCtx.closePath();
    maskCtx.fill();

    // For buildings, extend upward for 3D height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, canvasWidth, canvasHeight))
        .filter(Boolean) as { x: number; y: number }[];

      if (topPixels.length >= 3) {
        // Draw expanded rectangle from footprint top to roof top
        const minY = Math.min(...pixels.map(p => p.y));
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const roofMinY = Math.min(...topPixels.map(p => p.y));
        maskCtx.fillRect(minX, roofMinY, maxX - minX, minY - roofMinY);
      }
    }
  }

  // Blur + Clamp: soft feathered edges that never exceed polygon bounds
  // Blur creates gradient in both directions; clamping with the hard mask
  // cuts off all outward bleed, leaving inward-only feathered edges.
  const blurCanvas = document.createElement('canvas');
  blurCanvas.width = w;
  blurCanvas.height = h;
  const blurCtx = blurCanvas.getContext('2d')!;
  blurCtx.filter = 'blur(4px)';
  blurCtx.drawImage(maskCanvas, 0, 0);

  // Clamp: multiply blurred mask with original hard mask — zero pixels escape
  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.drawImage(blurCanvas, 0, 0);
  featherCtx.globalCompositeOperation = 'destination-in';
  featherCtx.drawImage(maskCanvas, 0, 0);

  // Composite: AI render masked with clamped feathered zones, drawn onto original
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(rendImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);

  // Draw the masked AI render on top of the original
  resultCtx.drawImage(aiCanvas, 0, 0);

  console.log('[GlobeAIRender] Post-process: blur+clamp clip (4px inward-only feather)');
  return resultCanvas.toDataURL('image/png').split(',')[1];
}

// ─── PER-ZONE RENDERING HELPERS ──────────────────────────────────────

export interface GlobeRenderProgress {
  step: number;
  total: number;
  zoneName: string;
  phase: 'ground' | 'building';
}

export const PERZONE_THRESHOLD = 99; // Single-shot is always used — per-zone disabled (text labels + borders handle zone identification)

/**
 * Generate a binary mask for a SINGLE zone, with building height extension.
 * Includes site boundary clip.
 */
function generateSingleZoneMask(
  zone: SiteZone,
  allZones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  // Clip to site boundary if present
  const siteBoundary = allZones.find(z => z.zone_type === 'site_boundary' && z.coordinates?.length >= 3);
  if (siteBoundary) {
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (boundaryPixels.length >= 3) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(boundaryPixels[0].x, boundaryPixels[0].y);
      for (let i = 1; i < boundaryPixels.length; i++) ctx.lineTo(boundaryPixels[i].x, boundaryPixels[i].y);
      ctx.closePath();
      ctx.clip();
    }
  }

  // Draw single zone as white with dilation
  const DILATION_PX = 8;
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';

  const pixels = zone.coordinates
    .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
    .filter(Boolean) as { x: number; y: number }[];

  if (pixels.length >= 3) {
    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);

    // Extend upward for building height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
        .filter(Boolean) as { x: number; y: number }[];
      if (topPixels.length >= 3) {
        for (const p of topPixels) ctx.lineTo(p.x, p.y);
      }
    }

    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }

  if (siteBoundary) ctx.restore();
  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Build a focused prompt for a single building zone.
 */
function buildSingleZonePromptForPerZone(
  zone: SiteZone,
  style: string,
  _camera: THREE.Camera,
  _terrainHeight: number,
  customPrompt?: string,
): string {
  const color = colorName(resolveZoneColor(zone));
  const info = getZoneArchetypeInfo(zone);
  const overlayPrompt = getMapOverlayPrompt(zone);
  const props = zone.properties || {};
  const floors = (props.floors as number) || 0;
  const heightM = (props.height_m as number) || (props.height as number) || floors * 3.2 || 0;
  const name = info.archetypeTitle || zone.name || zone.zone_type;

  let scale = '';
  if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
    if (floors > 0 && heightM > 0) scale = `${floors} floors, ${Math.round(heightM)}m tall`;
    else if (floors > 0) scale = `${floors} floors`;
    else if (heightM > 0) scale = `${Math.round(heightM)}m tall`;
    else if (info.minFloors && info.maxFloors) {
      // Use archetype recommended scale when user hasn't set dimensions
      scale = info.minFloors === info.maxFloors
        ? `${info.minFloors} floors`
        : `${info.minFloors}-${info.maxFloors} floors`;
      if (info.heightTendency) scale += ` (${info.heightTendency})`;
    }
    // Add recommended footprint dimensions so Gemini renders at realistic scale
    if (info.suggestedWidth_m && info.suggestedDepth_m) {
      scale += `, typical footprint ~${info.suggestedWidth_m}m × ${info.suggestedDepth_m}m`;
      if (info.aspectRatio) scale += ` (${info.aspectRatio} proportions)`;
    } else if (info.suggestedAreaSqm) {
      scale += `, typical footprint ~${info.suggestedAreaSqm}m²`;
    }
  }

  const features: string[] = [];
  if (overlayPrompt) features.push(overlayPrompt);
  else {
    if (info.facadeDescription) features.push(info.facadeDescription);
    if (info.roofDescription) features.push(info.roofDescription);
    if (info.materials) features.push(info.materials);
  }

  const sections = [
    `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`,
    `TASK: Render ONE building in the white masked area. The colored polygon [${color}] marks the footprint.`,
    `BUILDING: ${name}${scale ? ` | ${scale}` : ''}`,
    features.length > 0 ? `DETAILS: ${features.join(', ').substring(0, 300)}` : '',
    `CONTEXT: Preserve ALL existing photographic context outside the mask. Match lighting, color temperature, and atmosphere of surrounding real buildings.`,
    `MANDATORY: Replace the colored polygon with a photorealistic building. Render ONLY within the masked area. Match scale and density of surrounding real 3D buildings.`,
    customPrompt ? `ADDITIONAL: ${customPrompt}` : '',
  ].filter(Boolean);

  return sections.join('\n');
}

/**
 * Composite rendered AI image onto cumulative base, clipped to zone polygons.
 * Uses blur+clamp for inward-only feathered edges.
 */
async function compositeZoneRenderForPerZone(
  baseBase64: string,
  renderedBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
  subtractZones?: SiteZone[], // Building footprints to subtract from ground clip mask
): Promise<string> {
  const [baseImg, rendImg] = await Promise.all([
    loadImage(`data:image/png;base64,${baseBase64}`),
    loadImage(`data:image/png;base64,${renderedBase64}`),
  ]);

  const w = baseImg.naturalWidth;
  const h = baseImg.naturalHeight;

  // Result = base image
  const resultCanvas = document.createElement('canvas');
  resultCanvas.width = w;
  resultCanvas.height = h;
  const resultCtx = resultCanvas.getContext('2d')!;
  resultCtx.drawImage(baseImg, 0, 0, w, h);

  // Build hard mask for the zone(s)
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
    maskCtx.closePath();
    maskCtx.fill();

    // Extend upward for buildings
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, canvasWidth, canvasHeight))
        .filter(Boolean) as { x: number; y: number }[];
      if (topPixels.length >= 3) {
        const minY = Math.min(...pixels.map(p => p.y));
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const roofMinY = Math.min(...topPixels.map(p => p.y));
        maskCtx.fillRect(minX, roofMinY, maxX - minX, minY - roofMinY);
      }
    }
  }

  // Subtract building footprints from ground mask (prevents ground content
  // from painting over areas that buildings will occupy in Pass 2)
  if (subtractZones && subtractZones.length > 0) {
    maskCtx.globalCompositeOperation = 'destination-out';
    maskCtx.fillStyle = '#ffffff';
    for (const bz of subtractZones) {
      if (!bz.coordinates || bz.coordinates.length < 3) continue;
      const bPixels = bz.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
        .filter(Boolean) as { x: number; y: number }[];
      if (bPixels.length < 3) continue;
      maskCtx.beginPath();
      maskCtx.moveTo(bPixels[0].x, bPixels[0].y);
      for (let i = 1; i < bPixels.length; i++) maskCtx.lineTo(bPixels[i].x, bPixels[i].y);
      maskCtx.closePath();
      maskCtx.fill();
    }
    maskCtx.globalCompositeOperation = 'source-over';
  }

  // Blur + Clamp: inward-only feathered edges
  const blurCanvas = document.createElement('canvas');
  blurCanvas.width = w;
  blurCanvas.height = h;
  const blurCtx = blurCanvas.getContext('2d')!;
  blurCtx.filter = 'blur(4px)';
  blurCtx.drawImage(maskCanvas, 0, 0);

  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.drawImage(blurCanvas, 0, 0);
  featherCtx.globalCompositeOperation = 'destination-in';
  featherCtx.drawImage(maskCanvas, 0, 0);

  // Mask AI render with feathered polygon
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(rendImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);

  // Composite onto base
  resultCtx.drawImage(aiCanvas, 0, 0);

  return resultCanvas.toDataURL('image/png').split(',')[1];
}

export function useGlobeAIRender() {
  const isRenderingRef = useRef(false);

  const render = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: {
      style?: string;
      model?: string;
      projectId?: string;
      customPrompt?: string;
      // Internal: skip the isRenderingRef lock so renderPreviews can fan out
      // N parallel calls. renderPreviews sets the ref itself around the batch.
      _skipLock?: boolean;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (!options._skipLock && isRenderingRef.current) return null;
    if (!options._skipLock) isRenderingRef.current = true;

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image-preview', customPrompt } = options;

      // 1. Capture the globe canvas
      console.log('[GlobeAIRender] Capturing canvas...');
      const rawBase64 = await captureCanvasBase64(canvas);
      if (!rawBase64) throw new Error('Failed to capture canvas');

      // 1a. Add text labels to screenshot so Gemini can read zone names
      const imageBase64 = await (async () => {
        const img = await loadImage(`data:image/jpeg;base64,${rawBase64}`);
        const labelCanvas = document.createElement('canvas');
        labelCanvas.width = img.naturalWidth;
        labelCanvas.height = img.naturalHeight;
        const ctx = labelCanvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0);

        const editableZones = zones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);
        const scaleX = labelCanvas.width / canvas.width;
        const scaleY = labelCanvas.height / canvas.height;

        // Unique bright border colors — maximally distinct, cycling through for each zone
        const BORDER_COLORS = [
          '#FF0000', // Red
          '#0000FF', // Blue
          '#FF00FF', // Magenta
          '#00FFFF', // Cyan
          '#FFFF00', // Yellow
          '#FF6600', // Orange
          '#00FF00', // Lime
          '#FF0099', // Hot pink
          '#9900FF', // Purple
          '#00FF99', // Mint
        ];

        // Draw unique colored dashed borders on ALL zone polygons
        // Border color is deterministic per archetype variant — same archetype always gets same border
        const zoneBorderMap: Map<string, string> = new Map();
        for (let zi = 0; zi < editableZones.length; zi++) {
          const zone = editableZones[zi];
          const props = zone.properties || {};
          const archetypeId = (props.development_archetype_id as string)
            || (props.green_space_archetype_id as string)
            || (props.road_archetype_id as string)
            || (props.plaza_archetype_id as string)
            || zone.id || '';
          // Hash the archetype ID to get a consistent border color index
          let hash = 0;
          for (let c = 0; c < archetypeId.length; c++) {
            hash = ((hash << 5) - hash) + archetypeId.charCodeAt(c);
            hash |= 0;
          }
          const borderColor = BORDER_COLORS[Math.abs(hash) % BORDER_COLORS.length];
          zoneBorderMap.set(zone.id, borderColor);

          const pixels = zone.coordinates
            .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvas.width, canvas.height))
            .filter(Boolean) as { x: number; y: number }[];
          if (pixels.length < 2) continue;

          ctx.save();
          ctx.setLineDash([12, 8]);
          ctx.strokeStyle = borderColor;
          ctx.lineWidth = 5;
          ctx.beginPath();
          ctx.moveTo(pixels[0].x * scaleX, pixels[0].y * scaleY);
          for (let j = 1; j < pixels.length; j++) {
            ctx.lineTo(pixels[j].x * scaleX, pixels[j].y * scaleY);
          }
          ctx.closePath();
          ctx.stroke();
          ctx.restore();
        }

        // Draw text labels at each zone centroid
        ctx.font = 'bold 28px Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let zi = 0; zi < editableZones.length; zi++) {
          const zone = editableZones[zi];
          const centroid = zone.coordinates.reduce(
            (acc, c) => [acc[0] + c[0] / zone.coordinates.length, acc[1] + c[1] / zone.coordinates.length],
            [0, 0],
          );
          const screenPos = projectToPixels(centroid[0], centroid[1], terrainHeight, camera, canvas.width, canvas.height);
          if (!screenPos) continue;

          const info = getZoneArchetypeInfo(zone);
          const label = (info.archetypeTitle || zone.name || zone.zone_type).toUpperCase();
          const x = screenPos.x * scaleX;
          const y = screenPos.y * scaleY;

          // Use the zone's border color for the label background for extra association
          const borderColor = zoneBorderMap.get(zone.id) || '#FF6600';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 4;
          ctx.strokeText(label, x, y);
          ctx.fillStyle = borderColor;
          ctx.fillText(label, x, y);
        }
        console.log(`[GlobeAIRender] Added ${editableZones.length} text labels + colored borders to screenshot`);
        return labelCanvas.toDataURL('image/jpeg', 0.85).split(',')[1];
      })();

      // 1b. Occlusion culling — remove zones hidden behind taller buildings
      const occludedIds = findOccludedZones(zones, camera, canvas.width, canvas.height, terrainHeight);
      const visibleZones = occludedIds.size > 0
        ? zones.filter(z => !occludedIds.has(z.id || ''))
        : zones;

      // 2. Generate binary mask from VISIBLE zone polygons only
      console.log('[GlobeAIRender] Generating mask...');
      const maskBase64 = generateMask(visibleZones, camera, canvas.width, canvas.height, terrainHeight);

      // 3. Build SCHEMA prompt from VISIBLE zone archetypes only
      let prompt = buildPrompt(visibleZones, style, camera, terrainHeight);
      if (customPrompt) prompt += `\nADDITIONAL: ${customPrompt}`;

      // 4. Collect archetype reference card images (multi-view: street-level +
      //    up to 3 aerial angles per zone — 30°/60°/90° where available).
      //    Each image is compressed to 512px JPEG @ 0.7 (~30-50KB). Cap 48.
      console.log('[GlobeAIRender] Collecting archetype reference images...');
      const archetypeImages = await collectArchetypeImages(visibleZones);
      if (archetypeImages.length > 0) {
        prompt += (
          `\n\nARCHETYPE REFERENCE IMAGES (Images 2+): ${archetypeImages.length} ` +
          `images provide the visual identity for the drawn zones. Each image is ` +
          `labeled with its VIEWING ANGLE so you can match your output angle to ` +
          `the right reference:\n` +
          `  • "street-level ground view" — eye-level photograph; shows facade ` +
          `detail, materials, ornament, colors, ground-level character.\n` +
          `  • "30° low-oblique aerial" — drone ~50m up looking down shallowly; ` +
          `shows facade + partial rooftop.\n` +
          `  • "60° steep-oblique aerial" — drone ~80m up looking down steeply; ` +
          `shows rooftop + upper facade from a corner, triangulates 3D form.\n` +
          `  • "90° nadir / top-down aerial" — drone ~150m up looking straight ` +
          `down; shows rooftop plan, site layout, roof materials.\n` +
          `HOW TO USE: when rendering at an oblique camera angle (30-70°), weight ` +
          `the 60° aerial and street-level refs most heavily. When rendering top-` +
          `down or near-nadir, weight the 90° nadir ref most heavily. Use ALL ` +
          `available refs per zone to build a complete 3D understanding of its ` +
          `materials, form, and site layout before rendering. Each ref is ` +
          `tagged with the zone's fill color in [brackets] to identify which ` +
          `polygon it belongs to.`
        );
        for (let i = 0; i < archetypeImages.length; i++) {
          prompt += `\nImage ${i + 2}: [${archetypeImages[i].zone_color}] ${archetypeImages[i].label}`;
        }
      }

      console.log(`[GlobeAIRender] Prompt (${prompt.length} chars, ${zones.filter(z => z.zone_type !== 'site_boundary').length} zones, ${archetypeImages.length} ref images):`, prompt.substring(0, 200) + '...');

      // 5. Send to backend render API with archetype images
      console.log('[GlobeAIRender] Sending to Gemini via backend...');
      const resp = await api.post(
        '/api/v1/render/generate',
        {
          image_base64: imageBase64,
          mask_base64: maskBase64,
          prompt,
          negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors',
          model,
          temperature: 0.0,
          guidance_scale: 15,
          image_size: '2K', // 2K output for architectural detail accuracy
          thinking_budget: 0, // Disable thinking — no benefit for image generation, saves ~30-50% latency
          archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
        },
        { timeout: 300000 },
      );

      if (resp.data?.image_base64) {
        console.log('[GlobeAIRender] Render complete! Applying polygon clip...');

        // Post-process: clip the AI render to zone polygons with feathered edges
        // This ensures no zone bleeds into adjacent zones or outside boundaries
        const clippedBase64 = await clipRenderToZones(
          imageBase64, resp.data.image_base64,
          visibleZones, camera, canvas.width, canvas.height, terrainHeight,
        );

        return {
          imageUrl: `data:image/png;base64,${clippedBase64}`,
          prompt,
          seed: resp.data.seed,
        };
      }

      console.warn('[GlobeAIRender] No image in response');
      return null;

    } catch (err) {
      console.error('[GlobeAIRender] Error:', err);
      return null;
    } finally {
      if (!options._skipLock) isRenderingRef.current = false;
    }
  }, []);

  /**
   * Generate N preview renders in parallel with different server-side seeds.
   * Each preview is a full-quality render — this is not a low-res preview pass;
   * it's N independent variants the user can compare and pick the best one.
   *
   * The isRenderingRef lock is held by renderPreviews around the whole batch,
   * and individual render() calls bypass their own lock via _skipLock.
   */
  const renderPreviews = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: {
      style?: string;
      model?: string;
      projectId?: string;
      customPrompt?: string;
      count?: number;
    } = {},
  ): Promise<GlobeRenderResult[]> => {
    if (isRenderingRef.current) return [];
    isRenderingRef.current = true;
    const count = options.count ?? 3;
    try {
      console.log(`[GlobeAIRender] Generating ${count} previews in parallel...`);
      const promises: Promise<GlobeRenderResult | null>[] = Array.from({ length: count }, () =>
        render(canvas, camera, zones, terrainHeight, { ...options, _skipLock: true })
          .catch((err) => {
            console.warn('[GlobeAIRender:Preview] one variant failed:', err);
            return null;
          }),
      );
      const settled = await Promise.all(promises);
      const successful = settled.filter((r): r is GlobeRenderResult => r !== null);
      console.log(`[GlobeAIRender] Previews complete: ${successful.length}/${count} succeeded`);
      return successful;
    } finally {
      isRenderingRef.current = false;
    }
  }, [render]);

  /**
   * Capture the Google 3D Tiles from street level.
   * Moves camera to street height, waits for tiles, captures, then restores camera.
   */
  const captureStreetView = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    lat: number,
    lng: number,
    headingDeg: number,
    terrainHeight: number,
    flyToStreetLevel: (lat: number, lng: number, heading: number, terrainH: number, cam?: THREE.Camera) => void,
    restoreAerialView: (state: any, cam?: THREE.Camera) => void,
    saveCameraState: (cam?: THREE.Camera) => any,
  ): Promise<string | null> => {
    // Save current camera state
    const savedState = saveCameraState(camera);
    if (!savedState) return null;

    try {
      // Move camera to street level
      flyToStreetLevel(lat, lng, headingDeg, terrainHeight, camera);

      // Wait for tiles to load at street-level LOD
      // Phase 1: Let renderer process new camera position
      for (let i = 0; i < 10; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Phase 2: Wait for tile streaming with timeout
      // Poll every 500ms for up to 8 seconds
      console.log('[GlobeAIRender] Waiting for street-level tiles to load...');
      for (let attempt = 0; attempt < 16; attempt++) {
        await new Promise(r => setTimeout(r, 500));
        // Render a frame to trigger tile updates
        await new Promise(r => requestAnimationFrame(r));
      }

      // Phase 3: Final frames for render completion
      for (let i = 0; i < 5; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Capture the street-level view
      console.log('[GlobeAIRender] Capturing street-level view...');
      const imageBase64 = await captureCanvasBase64(canvas);

      return imageBase64 || null;
    } finally {
      // Always restore the camera
      restoreAerialView(savedState, camera);
    }
  }, []);

  // ─── PER-ZONE SEQUENTIAL RENDER ─────────────────────────────────────
  // Renders each building individually for accurate archetype placement.
  // Pass 1: all ground zones in one call. Pass 2: each building one at a time.

  const renderPerZone = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: {
      style?: string;
      model?: string;
      projectId?: string;
      customPrompt?: string;
      onProgress?: (progress: GlobeRenderProgress) => void;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (isRenderingRef.current) return null;
    isRenderingRef.current = true;

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image-preview', customPrompt, onProgress } = options;

      // 1. Capture base screenshot
      console.log('[GlobeAIRender:PerZone] Capturing canvas...');
      const baseBase64 = await captureCanvasBase64(canvas);
      if (!baseBase64) throw new Error('Failed to capture canvas');

      // 2. Occlusion culling
      const occludedIds = findOccludedZones(zones, camera, canvas.width, canvas.height, terrainHeight);
      const visibleZones = occludedIds.size > 0
        ? zones.filter(z => !occludedIds.has(z.id || ''))
        : zones;

      // 3. Classify zones
      const GROUND_TYPES = ['water', 'green_space', 'park', 'parking', 'road', 'street', 'path', 'plaza', 'development_area'];
      const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];

      const editableZones = visibleZones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);
      const groundZones = editableZones.filter(z => GROUND_TYPES.includes(z.zone_type));
      const buildingZones = editableZones
        .filter(z => BUILDING_TYPES.includes(z.zone_type))
        .sort((a, b) => {
          // Largest area first
          const polyArea = (z: SiteZone) => {
            if (!z.coordinates || z.coordinates.length < 3) return 0;
            let area = 0;
            for (let i = 0; i < z.coordinates.length; i++) {
              const j = (i + 1) % z.coordinates.length;
              area += z.coordinates[i][0] * z.coordinates[j][1];
              area -= z.coordinates[j][0] * z.coordinates[i][1];
            }
            return Math.abs(area / 2);
          };
          return polyArea(b) - polyArea(a);
        });

      // ALL zones rendered individually — ground first (largest area first), then buildings
      const allRenderZones = [...groundZones, ...buildingZones];
      const totalSteps = allRenderZones.length;
      let currentStep = 0;
      let allPrompts: string[] = [];

      // Create a labeled version of the screenshot with zone names written on each polygon
      // This helps Gemini identify which zone is which, especially when colors are similar
      const labeledBase64 = await (async () => {
        const img = await loadImage(`data:image/jpeg;base64,${baseBase64}`);
        const labelCanvas = document.createElement('canvas');
        labelCanvas.width = img.naturalWidth;
        labelCanvas.height = img.naturalHeight;
        const ctx = labelCanvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0);

        // Draw zone name labels at each zone's centroid
        ctx.font = 'bold 28px Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (const zone of editableZones) {
          if (!zone.coordinates || zone.coordinates.length < 3) continue;
          const centroid = zone.coordinates.reduce(
            (acc, c) => [acc[0] + c[0] / zone.coordinates.length, acc[1] + c[1] / zone.coordinates.length],
            [0, 0],
          );
          const screenPos = projectToPixels(centroid[0], centroid[1], terrainHeight, camera, canvas.width, canvas.height);
          if (!screenPos) continue;

          const info = getZoneArchetypeInfo(zone);
          const label = (info.archetypeTitle || zone.name || zone.zone_type).toUpperCase();

          // Scale position to labeled canvas dimensions
          const x = screenPos.x * (labelCanvas.width / canvas.width);
          const y = screenPos.y * (labelCanvas.height / canvas.height);

          // Draw white text with black outline for readability
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 4;
          ctx.strokeText(label, x, y);
          ctx.fillStyle = '#ffffff';
          ctx.fillText(label, x, y);
        }

        return labelCanvas.toDataURL('image/jpeg', 0.85).split(',')[1];
      })();

      let cumulativeBase64 = labeledBase64;
      console.log(`[GlobeAIRender:PerZone] ${groundZones.length} ground zones, ${buildingZones.length} buildings, ${totalSteps} total steps (all individual, labeled screenshot)`);

      console.log(`[GlobeAIRender:PerZone] ${groundZones.length} ground zones, ${buildingZones.length} buildings, ${totalSteps} total steps (all individual)`);

      // ── RENDER EACH ZONE INDIVIDUALLY ──
      for (let i = 0; i < allRenderZones.length; i++) {
        const zone = allRenderZones[i];
        const isBuilding = BUILDING_TYPES.includes(zone.zone_type);
        currentStep++;
        const zoneName = zone.name || getZoneArchetypeInfo(zone).archetypeTitle || zone.zone_type;
        onProgress?.({ step: currentStep, total: totalSteps, zoneName, phase: isBuilding ? 'building' : 'ground' });
        console.log(`[GlobeAIRender:PerZone] Zone ${i + 1}/${totalSteps}: "${zoneName}" (${isBuilding ? 'building' : 'ground'})...`);

        // Single-zone mask
        const singleMask = generateSingleZoneMask(
          zone, visibleZones, camera, canvas.width, canvas.height, terrainHeight,
        );

        // Build focused prompt for this single zone
        let singlePrompt: string;
        if (isBuilding) {
          singlePrompt = buildSingleZonePromptForPerZone(zone, style, camera, terrainHeight, customPrompt);
        } else {
          // Ground zone prompt — focused on this single zone
          const info = getZoneArchetypeInfo(zone);
          const overlayPrompt = getMapOverlayPrompt(zone);
          const color = colorName(resolveZoneColor(zone));
          const features: string[] = [];
          if (overlayPrompt) features.push(overlayPrompt);
          else {
            if (info.corridorCharacter) features.push(info.corridorCharacter);
            if (info.materials) features.push(info.materials);
            if (info.publicRealm) features.push(info.publicRealm);
          }
          let dimHint = '';
          if (info.suggestedWidth_m && info.suggestedDepth_m) {
            dimHint = `, typical dimensions ~${info.suggestedWidth_m}m × ${info.suggestedDepth_m}m`;
          }

          singlePrompt = [
            `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`,
            `TASK: Render ONE ground zone in the white masked area. The colored polygon [${color}] marks the zone.`,
            `ZONE: ${info.archetypeTitle || zoneName}${dimHint}`,
            features.length > 0 ? `DETAILS: ${features.join(', ').substring(0, 400)}` : '',
            `CONTEXT: Preserve ALL existing photographic context outside the mask. Match lighting and atmosphere.`,
            `MANDATORY: Replace the colored polygon with photorealistic ground materials. Render ONLY within the masked area.`,
            customPrompt ? `ADDITIONAL: ${customPrompt}` : '',
          ].filter(Boolean).join('\n');
        }
        allPrompts.push(singlePrompt);

        // Single archetype image (variant-aware)
        const archetypeImages = await collectArchetypeImages([zone]);
        let prompt = singlePrompt;
        if (archetypeImages.length > 0) {
          prompt += `\n\nARCHETYPE STYLE REFERENCE: Image 2 shows the exact style for this zone. Replicate this within the masked area.`;
        }

        // Use cumulative image for ALL zones — each zone sees previous renders for context
        const inputImage = cumulativeBase64;

        try {
          const resp = await api.post(
            '/api/v1/render/generate',
            {
              image_base64: inputImage,
              mask_base64: singleMask,
              prompt,
              negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark' + (isBuilding ? ', colored polygon fill' : ''),
              model,
              temperature: 0.0,
              guidance_scale: 15,
              image_size: '2K',
              thinking_budget: 0,
              archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
            },
            { timeout: 300000 },
          );

          if (resp.data?.image_base64) {
            // Composite this zone, subtracting building footprints for ground zones
            cumulativeBase64 = await compositeZoneRenderForPerZone(
              cumulativeBase64, resp.data.image_base64,
              [zone], camera, canvas.width, canvas.height, terrainHeight,
              isBuilding ? undefined : buildingZones, // only subtract buildings from ground zones
            );
            console.log(`[GlobeAIRender:PerZone] Zone ${i + 1}/${totalSteps} composited`);
          }
        } catch (err) {
          console.error(`[GlobeAIRender:PerZone] Zone "${zoneName}" failed:`, err);
        }
      }

      // Return final composite
      return {
        imageUrl: `data:image/png;base64,${cumulativeBase64}`,
        prompt: allPrompts.join('\n---\n'),
        seed: undefined,
      };

    } catch (err) {
      console.error('[GlobeAIRender:PerZone] Error:', err);
      return null;
    } finally {
      isRenderingRef.current = false;
    }
  }, []);

  return { render, renderPreviews, renderPerZone, captureStreetView, isRenderingRef };
}
