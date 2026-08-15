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
import { api, resolveApiFileUrl } from '@/services/api';
import { useViewerStore } from '@/store';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { getCustomZoneStyle } from '../customZoneStyle';
import { formatArea, polygonDimensionsMeters, resolveZoneColor } from '../mapEngine/geoUtils';
import {
  describeCameraAngleForPrompt,
  getAngleFromNadirLabelValue,
  pitchFromNadirToCameraElevation,
} from '../cameraAngles';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';
import { prepareZonesForRender } from '@/components/viewer/resolvePlanZoneArchetypes';
import {
  buildParkRenderQualityInstruction,
  resolveParkGroundProfile,
} from './parkGroundProfiles';
import {
  buildParkDiagram,
  resolveParkGroundFitInstruction,
  selectParkRenderGeometryZones,
} from './parkGroundTexture';
import {
  buildStreetRenderGroundTruthInstruction,
  resolvePilotStreetSectionProfile,
} from './streetSectionProfiles';
import {
  isCommunity3DCompiled,
  resolveCommunity3DKind,
  type Community3DKind,
} from '@/features/community3d/community3d';
import { projectedBoundsIntersectFrame } from './renderZoneVisibility';
import { selectRenderLabelIds } from './renderLabelBudget';
import {
  buildPublicRealmContextPrompt,
  buildPublicRealmSceneContextPrompt,
} from './publicRealmGenerationContext';

const DEG_TO_RAD = Math.PI / 180;
const GROUND_ZONE_TYPES = new Set(['water', 'green_space', 'park', 'parking', 'road', 'street', 'path', 'plaza', 'development_area']);
const BUILDING_ZONE_TYPES = new Set(['building', 'residential', 'commercial', 'industrial', 'mixed_use']);
export type OpenAIImageQuality = 'auto' | 'low' | 'medium' | 'high';

// ─── SHARED STYLE PROMPTS ────────────────────────────────────────────
// Single source of truth for all render style prompts (used by single-shot, per-zone, and ground passes)
// Style prompts: the overlapping ones are imported from codex verbatim for
// richer material/lens/weathering language. Stable-only styles (night,
// marker-render, collage, risograph, pixel-art) are preserved as-is. Codex-only
// styles (site-plan variants, isometric) are added.
export const GLOBE_STYLE_PROMPTS: Record<string, string> = {
  photorealistic: 'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography.',
  photomontage: 'Professional architectural photomontage indistinguishable from a real drone photograph. DJI Mavic 3 at 60m altitude, Hasselblad sensor, 24mm lens f/5.6. Proposed development appears fully constructed within existing site context. Lighting and shadows match surroundings. Atmospheric haze increasing with distance. Realistic material weathering 1-2 years post-completion. Natural lens vignetting and chromatic aberration. Documentary aerial photography of an existing place.',
  atmospheric: 'Cinematic aerial architectural photograph with dramatic atmospheric conditions. CRITICAL: Replace all colored polygon fills with photorealistic building materials — real brick, stone, glass, concrete, metal roofing. No flat colored surfaces. Final minutes of golden hour, low-angle warm sunlight casting extremely long shadows. Towering cumulus clouds lit amber and rose overhead. Ground-level haze creating depth layers. Wet surfaces with mirror-like reflections. Interior lights glowing warm amber through windows. Medium format digital with exceptional dynamic range.',
  'site-plan': 'Top-down 2D architectural site plan in strict orthographic projection. Clean architectural linework with soft flat pastel colors. Stylized trees as simple green circles from above. Professional urban planning drawing quality.',
  'site-plan-photo': 'Professional near-top-down drone photomontage at 100m altitude, 15-20 degrees from nadir. DJI Mavic 3, Hasselblad sensor, 24mm lens f/5.6. Photorealistic materials, accurate short shadows, real rooftop equipment visible. Seamless integration with surrounding satellite context. Documentary drone survey photography of a completed development. CRITICAL: Replace all colored polygon fills completely with photorealistic materials. No flat green, red, blue, or orange overlay colors should remain visible.',
  'site-plan-watercolor': 'Near-top-down architectural site plan as a hand-painted watercolor on textured paper, 15-20 degrees from nadir. Soft translucent washes — warm ochre for buildings, sage green for parks, soft grey for roads, ultramarine for water. Faint pencil construction lines beneath washes. Trees as loose circular watercolor daubs. Shadows as soft blue-grey washes. White paper glowing through as highlights. Pigment granulation, wet-on-wet blooms, bleeding edges at zone boundaries. Architectural competition entry quality.',
  blueprint: 'Architectural blueprint cyanotype rendering on aged blueprint paper. Strict orthographic projection looking straight down. Pure white linework on deep Prussian-blue ground — crisp construction lines defining building footprints, roads, property lines, landscape elements. Hatched line patterns indicate grass and pavement. Trees as small white circular symbols. Roads as parallel white lines. Faint vintage paper mottling. No tonal shading, no gradients, no realistic materials. Drafted-by-hand mid-20th-century architectural drawing convention.',
  winter: 'Photorealistic winter scene. Snow-covered roofs with drift patterns. Bare deciduous trees, snow-laden evergreens. Frosted surfaces, salt-grit on plowed paths. Soft diffuse winter light, pale blue-grey sky, long blue-tinted shadows. Specular melt/ice sheen on horizontal surfaces. Warm window glow.',
  night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
  watercolour: 'Beautiful watercolor architectural painting on textured paper. Soft bleeding edges where colors mix organically, translucent layered washes with white paper glowing through. Loose and artistic, pigment granulation in shadows. Muted earth-tone palette with sage green, ochre, and ultramarine accents.',
  charcoal: 'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows. High contrast black and white, full tonal range. Soft blended areas for atmosphere, sharp charcoal edge lines for architectural definition. Gallery-quality architectural drawing.',
  'pen-and-ink': 'Architectural pen-and-ink line drawing on cream-toned drawing paper. Pure ink-only linework, zero colour, zero tonal smudging — every mark is a discrete pen line. Crisp construction lines for footprints and edges. Cross-hatching and parallel-line hatching for shadow, denser where shadows deepen. Line-weight variation from delicate hairlines for distance to confident foreground strokes. Stippling for foliage and weathered surfaces. Trees as outlined forms. Hand-drafted urban-sketcher / mid-20th-century architectural illustration tradition. Cream paper glowing through as highlights.',
  isometric: 'Isometric 3D architectural diagram with clean parallel projection and zero perspective distortion. Perfect 30-degree axonometric geometry. Smooth matte pastel colors with crisp hard edges and thin black outlines. Vector-art aesthetic, contemporary infographic style.',
  'marker-render': 'Handcrafted architectural marker rendering on smooth paper. Precise black ink linework with Copic marker shading. Visible overlapping streaky strokes following surface planes. Warm greys and ochres for facades, olive greens for landscape. White gaps for highlights.',
  'clay-maquette': 'Photorealistic macro photography of a physical architectural scale model carved from a single block of PURE WHITE matte plaster. CRITICAL: Every single element — buildings, trees, roads, parks, vehicles — is the SAME pure white material with ZERO color. No green, no gray, no brown, no color of any kind. Only white plaster with shadows defining form. Studio lighting with soft overhead softbox and deep ambient occlusion shadows. High-angle isometric view with tilt-shift miniature effect. Monochromatic white architectural maquette on white base board.',
  woodblock: 'Stylized woodblock print. Bold thick black outlines, flat limited vintage color palette of 4-6 colors with crisp separation. Visible wood grain texture. Zero gradation or blending. Graphic retro architectural illustration, museum-quality fine art print.',
  collage: 'Vibrant post-digital architectural collage as a mixed media composition. Flat unshaded colour blocks, photographic texture cut-outs with torn edges. Vintage botanical illustrations for trees. Flat illustrative lighting. Visible paper texture. Avant-garde competition aesthetic.',
  risograph: 'Risograph-printed architectural visualization. Halftone dot patterns, limited 2-3 spot color palette (fluorescent pink, teal, yellow), slight misregistration between color layers, grain texture, overprint where colors overlap.',
  'pixel-art': '16-bit pixel art architectural scene, grid-aligned with uniform square pixels. Nearest-neighbour scaling, zero anti-aliasing. Strict limited palette of 16 colors. Shading via checkerboard dithering patterns. Dark selective outlines. SNES-era JRPG city aesthetic.',
  survey: 'A precise large-format aerial survey photograph of the city block. Rigorously level with edge-to-edge tack-sharp clarity, even flat daylight revealing every roof, street, and material with no drama or deep shadow, and neutral true-to-life colour with clinical encyclopedic precision. Treat the captured massing as exact ground truth: preserve the real footprints, heights, layout, and materials precisely, resolving them into a real photograph. Never restyle, embellish, or reinterpret the geometry.',
  // Development mode: the capture already contains textured 3D massing
  // (placed LEGO stacks / Meshy models) — resolve that geometry into a
  // finished photograph instead of imagining buildings from polygons.
  development: 'A photorealistic visualization of a completed development, photographed from a drone. The detailed 3D buildings standing in the scene are the proposal, already built at the right size with their real facade materials. Resolve each one into a finished building: crisp facade detail, window reflections, entrance doors and canopies, balcony rails, subtle material weathering, rooftop equipment. Ground them with sidewalks, street trees, planting, parked cars and a few pedestrians. The finished buildings sit naturally in the surrounding photograph, in the same light and atmosphere.',
  documentary: 'A deadpan documentary aerial colour photograph of the city block in the New Topographics tradition. Flat even daylight, neutral restrained true-to-life colour, and a calm honest ordinariness with no dramatization. Keep the real massing, proportions, and layout exactly as modelled, resolving them faithfully into a plain, believable photograph rather than a styled render.',
};
// Artistic styles drop the photoreal-specific prompt clauses and the
// photoreal negative prompt ('cartoon, illustration, sketch' would directly
// contradict a watercolour/isometric STYLE instruction).
const ARTISTIC_STYLES = new Set([
  'site-plan',
  'site-plan-watercolor',
  'blueprint',
  'watercolour',
  'charcoal',
  'pen-and-ink',
  'isometric',
  'marker-render',
  'clay-maquette',
  'woodblock',
  'collage',
  'risograph',
  'pixel-art',
]);

// Styles whose prompts dictate a CAMERA re-projection (axonometric, strict
// orthographic plan, near-nadir drone). Output pixels no longer align with
// the input screenshot, so screen-space polygon clipping is geometrically
// incoherent for them — these styles skip clipRenderToZones and return the
// model's full-frame reinterpretation; boundary fidelity comes from the plan
// diagram reference instead. site-plan-photo dictates a 15-20°-from-nadir
// camera too, so it is deliberately included even though it isn't artistic.
export const REPROJECTING_STYLES = new Set([
  'isometric',
  'site-plan',
  'site-plan-watercolor',
  'blueprint',
  'clay-maquette',
  'site-plan-photo',
]);

// P1.8 verification-gate scope: only styles that must keep real streets
// street-like. Artistic styles legitimately repaint streets in their medium.
const VERIFICATION_GATE_STYLES = new Set(['photorealistic', 'photomontage']);

// P1.10 two-pass eligibility: camera-preserving artistic styles. Reprojecting
// styles return full-frame output anyway; photoreal gains nothing from a
// restyle pass. Exported for the panel's "High fidelity" toggle.
export const HIGH_FIDELITY_STYLES: Set<string> = new Set(
  [...ARTISTIC_STYLES].filter((s) => !REPROJECTING_STYLES.has(s)),
);

const catalog = [
  ...((archetypeCatalog as any)?.archetypes || []),
  ...((openSpaceCatalog as any)?.archetypes || (openSpaceCatalog as any) || []),
  ...((streetPathCatalog as any)?.archetypes || (streetPathCatalog as any) || []),
] as any[];

export interface GlobeRenderResult {
  imageUrl: string;  // data:image/png;base64,...
  prompt: string;
  seed?: number;
  model?: string;
  imageQuality?: OpenAIImageQuality;
  providerLabel?: string;
  error?: string;
}

export interface GlobeRenderVariant {
  model: string;
  label: string;
  imageQuality?: OpenAIImageQuality;
}

function getRenderErrorMessage(err: any): string {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (typeof err?.message === 'string' && err.message.trim()) return err.message;
  return 'Render failed. Please try again.';
}

function createErrorPreviewImage(providerLabel: string, message: string): string {
  const safeLabel = providerLabel.replace(/[<>&"]/g, (char) => ({
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
  }[char] || char));
  const safeMessage = message
    .replace(/[<>&"]/g, (char) => ({
      '<': '&lt;',
      '>': '&gt;',
      '&': '&amp;',
      '"': '&quot;',
    }[char] || char))
    .slice(0, 360);
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
      <rect width="1200" height="675" fill="#1f2937"/>
      <rect x="40" y="40" width="1120" height="595" rx="24" fill="#111827" stroke="#ef4444" stroke-width="4"/>
      <text x="80" y="150" fill="#fca5a5" font-family="Arial, sans-serif" font-size="46" font-weight="700">${safeLabel}</text>
      <text x="80" y="215" fill="#ffffff" font-family="Arial, sans-serif" font-size="34" font-weight="700">Preview failed</text>
      <foreignObject x="80" y="260" width="1040" height="280">
        <div xmlns="http://www.w3.org/1999/xhtml" style="color:#d1d5db;font-family:Arial,sans-serif;font-size:26px;line-height:1.35;word-break:break-word;">${safeMessage}</div>
      </foreignObject>
    </svg>
  `;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
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
 * Nearest Gemini-supported aspect ratio for a capture canvas. Sent explicitly
 * on render requests: left unset, the LAST image in the payload governs the
 * output frame (an archetype ref, not the map) — a silent geometry distorter
 * for zone polygons.
 */
const SUPPORTED_ASPECT_RATIOS: Array<[string, number]> = [
  ['21:9', 21 / 9], ['16:9', 16 / 9], ['3:2', 1.5], ['4:3', 4 / 3],
  ['5:4', 1.25], ['1:1', 1], ['4:5', 0.8], ['3:4', 0.75],
  ['2:3', 2 / 3], ['9:16', 9 / 16],
];
export function nearestAspectRatio(width: number, height: number): string {
  if (!width || !height) return '4:3';
  const target = width / height;
  let best = '4:3';
  let bestDiff = Infinity;
  for (const [label, ratio] of SUPPORTED_ASPECT_RATIOS) {
    const diff = Math.abs(Math.log(ratio / target));
    if (diff < bestDiff) { bestDiff = diff; best = label; }
  }
  return best;
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

function readFiniteNumber(value: unknown): number | null {
  const numeric = typeof value === 'number'
    ? value
    : typeof value === 'string' && value.trim().length > 0
      ? Number(value)
      : NaN;
  return Number.isFinite(numeric) ? numeric : null;
}

function getZoneTerrainHeight(zone: SiteZone, fallback: number): number {
  const props = zone.properties as Record<string, unknown> | undefined;
  return readFiniteNumber(props?.terrain_elevation_m)
    ?? readFiniteNumber(props?.terrain_height_m)
    ?? readFiniteNumber(props?.terrain_height)
    ?? readFiniteNumber(props?.terrainElevation)
    ?? readFiniteNumber(props?.terrainHeight)
    ?? fallback;
}

function getZoneBuildingHeight(zone: SiteZone): number {
  const props = zone.properties as Record<string, unknown> | undefined;
  const floors = readFiniteNumber(props?.floors) ?? 0;
  const explicitHeight = readFiniteNumber(props?.height_m) ?? readFiniteNumber(props?.height);
  if (explicitHeight != null && explicitHeight > 0) return explicitHeight;
  return floors > 0 ? floors * 3.2 : 0;
}

function isBuildingZone(zone: SiteZone): boolean {
  return BUILDING_ZONE_TYPES.has(zone.zone_type);
}

function hasAuthoredCommunityGround(zone: SiteZone): boolean {
  const kind = resolveCommunity3DKind(zone);
  if (kind !== 'park' && kind !== 'street') return false;
  if (isCommunity3DCompiled(zone)) return true;
  return kind === 'park' && Boolean(
    (zone.properties as Record<string, unknown> | undefined)?.park_ground_texture,
  );
}

function zoneAreaM2(zone: SiteZone): number {
  if (!zone.coordinates || zone.coordinates.length < 3) return 0;
  return polygonDimensionsMeters(zone.coordinates).area;
}

function formatFootprintMetrics(zone: SiteZone): string {
  if (!zone.coordinates || zone.coordinates.length < 3) return '';
  const metrics = polygonDimensionsMeters(zone.coordinates);
  if (!Number.isFinite(metrics.area) || metrics.area <= 0) return '';
  const width = Math.max(1, Math.round(metrics.width));
  const depth = Math.max(1, Math.round(metrics.depth));
  return `${width.toLocaleString()}m x ${depth.toLocaleString()}m (${formatArea(metrics.area)})`;
}

/**
 * Check which zones are significantly occluded by other (taller) zones
 * in screen space. Returns a Set of zone IDs that should be culled.
 *
 * Algorithm: For each zone, render all OTHER building zones (that are taller
 * or in front) as filled polygons onto a test canvas, then check how many
 * pixels of the target zone's footprint are covered.
 * If its configured coverage threshold is exceeded, the zone is removed from
 * the prompt.
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
    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    const buildingHeight = getZoneBuildingHeight(zone);

    // Project roof height too for buildings
    const roofPixels = buildingHeight > 0
      ? zone.coordinates
          .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight + buildingHeight, camera, width, height))
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
  for (const target of projected) {
    if (target.pixels.length < 3) continue;
    if (GROUND_ZONE_TYPES.has(target.zone.zone_type)) continue; // Never cull ground zones

    // Find zones that could occlude this one:
    // - taller buildings whose screen footprint overlaps
    // - zones that are closer to camera (lower avgY in oblique view)
    const occluders = projected.filter(other =>
      other.zone.id !== target.zone.id &&
      other.pixels.length >= 3 &&
      (other.buildingHeight > target.buildingHeight || other.avgY > target.avgY) &&
      isBuildingZone(other.zone),
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
 * Convex hull of a 2D point set (Andrew's monotone chain). Counter-clockwise.
 * Used to produce a tight silhouette for projected 3D building prisms —
 * the convex hull of base + roof vertices matches the actual screen-space
 * silhouette of a vertical extrusion much better than an axis-aligned bbox.
 */
function convexHull2D(points: { x: number; y: number }[]): { x: number; y: number }[] {
  if (points.length <= 2) return points.slice();
  const sorted = points.slice().sort((a, b) => a.x - b.x || a.y - b.y);
  const cross = (
    o: { x: number; y: number },
    a: { x: number; y: number },
    b: { x: number; y: number },
  ) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
  const lower: { x: number; y: number }[] = [];
  for (const p of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  const upper: { x: number; y: number }[] = [];
  for (let i = sorted.length - 1; i >= 0; i--) {
    const p = sorted[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop();
    upper.push(p);
  }
  lower.pop();
  upper.pop();
  return lower.concat(upper);
}

/**
 * Compute the screen-space silhouette of a zone. For buildings this is the
 * convex hull of base + roof projected vertices (the true prism outline);
 * for ground zones this is just the base polygon.
 */
function zoneSilhouette(
  zone: SiteZone,
  basePixels: { x: number; y: number }[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): { x: number; y: number }[] {
  const buildingHeight = getZoneBuildingHeight(zone);
  if (buildingHeight <= 0 || !isBuildingZone(zone)) {
    return basePixels;
  }
  const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
  const topPixels = zone.coordinates
    .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight + buildingHeight, camera, width, height))
    .filter(Boolean) as { x: number; y: number }[];
  if (topPixels.length < 3) return basePixels;
  return convexHull2D([...basePixels, ...topPixels]);
}

/**
 * P1.9 — OSM road carve stamp (defense-in-depth). Buffered real-road
 * corridors, minus every building hull, as an alpha stamp. Callers erase it
 * from editable-region masks so a real road crossing a ground-zone mask is
 * never repainted. Deliberately does NOT touch in-hull pixels — a tower may
 * legitimately occlude the road behind it from this camera; only
 * per-building compositing fixes in-hull bleed (P2).
 * Returns null when no OSM roads are loaded or none project on screen.
 * Kill switch: localStorage cc_osm_road_carve = '0'.
 */
function buildOsmRoadCarveStamp(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): HTMLCanvasElement | null {
  if (localStorage.getItem('cc_osm_road_carve') === '0') return null;
  const roads = useViewerStore.getState().osmContext?.roads;
  if (!roads || roads.length === 0) return null;

  const stamp = document.createElement('canvas');
  stamp.width = width;
  stamp.height = height;
  const stampCtx = stamp.getContext('2d')!;
  stampCtx.lineCap = 'round';
  stampCtx.lineJoin = 'round';
  stampCtx.strokeStyle = '#ffffff';
  let drawn = 0;
  for (const road of roads) {
    const coords = road.coordinates || [];
    const widthM = Number(road.width_m) || 8;
    let segments = 0;
    for (let i = 0; i + 1 < coords.length; i++) {
      const a = projectToPixels(coords[i][0], coords[i][1], terrainHeight, camera, width, height);
      const b = projectToPixels(coords[i + 1][0], coords[i + 1][1], terrainHeight, camera, width, height);
      // BOTH endpoints must project: dropping a behind-camera vertex and
      // bridging its neighbours would slash a phantom corridor across the frame.
      if (!a || !b) continue;
      // Per-segment pixels-per-meter (1 m east probe at the segment start) —
      // one global scale is off by several x between foreground and horizon
      // in oblique views.
      const dLon = 1 / (111_320 * Math.cos((coords[i][1] * Math.PI) / 180));
      const probe = projectToPixels(coords[i][0] + dLon, coords[i][1], terrainHeight, camera, width, height);
      const ppm = probe ? Math.hypot(probe.x - a.x, probe.y - a.y) : 0;
      if (ppm <= 0.01) continue;
      stampCtx.lineWidth = Math.max(2, widthM * ppm + 4); // ~2 px buffer per side
      stampCtx.beginPath();
      stampCtx.moveTo(a.x, a.y);
      stampCtx.lineTo(b.x, b.y);
      stampCtx.stroke();
      segments++;
    }
    if (segments) drawn++;
  }
  if (!drawn) return null;

  // Building hulls AND drawn street zones stay editable — erase both from the
  // stamp. Plan/user streets are routinely drawn directly OVER real roads;
  // the carve protects roads crossing OTHER ground zones (parks, development
  // areas), never the streets the plan itself claims.
  const streetishTypes = new Set(['road', 'street', 'path']);
  const isStreetZone = (zone: SiteZone): boolean =>
    streetishTypes.has(zone.zone_type as string)
    || (zone.properties as Record<string, unknown> | undefined)?._plan_role === 'street';
  stampCtx.globalCompositeOperation = 'destination-out';
  stampCtx.fillStyle = '#ffffff';
  for (const zone of zones) {
    const isHullBuilding = isBuildingZone(zone) && getZoneBuildingHeight(zone) > 0;
    if (!isHullBuilding && !isStreetZone(zone)) continue;
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;
    const outline = isHullBuilding
      ? zoneSilhouette(zone, pixels, camera, width, height, zoneTerrainHeight)
      : pixels;
    stampCtx.beginPath();
    stampCtx.moveTo(outline[0].x, outline[0].y);
    for (let i = 1; i < outline.length; i++) stampCtx.lineTo(outline[i].x, outline[i].y);
    stampCtx.closePath();
    stampCtx.fill();
  }
  stampCtx.globalCompositeOperation = 'source-over';
  console.log(`[GlobeAIRender] OSM road carve: ${drawn} road corridors stamped (building hulls + drawn streets exempt)`);
  return stamp;
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
  carveRoads = true,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  // Start with black (preserve everything)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  // If site boundary exists, clip all zone rendering to within it
  const siteBoundary = getActiveSiteBoundary(zones);
  if (siteBoundary) {
    const boundaryTerrainHeight = getZoneTerrainHeight(siteBoundary, terrainHeight);
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], boundaryTerrainHeight, camera, width, height))
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

  // Draw each zone as WHITE (binary mask) — skip site_boundary.
  // Buildings use a convex-hull silhouette (base + projected roof) so the
  // editable region follows the true 3D prism, not an axis-aligned bbox.
  // Dilation stroke gives Gemini a small edge of peripheral context.
  const DILATION_PX = 4; // ~1m at typical aerial zoom (halved to reduce leak)
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    if (pixels.length < 3) continue;

    const silhouette = zoneSilhouette(zone, pixels, camera, width, height, zoneTerrainHeight);

    ctx.beginPath();
    ctx.moveTo(silhouette[0].x, silhouette[0].y);
    for (let i = 1; i < silhouette.length; i++) ctx.lineTo(silhouette[i].x, silhouette[i].y);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }

  // Restore context (remove clip)
  if (siteBoundary) ctx.restore();

  // P1.9: real roads crossing the editable region (outside building hulls)
  // are painted back to BLACK (keep-as-is) in the payload mask.
  // GPT gets carveRoads=false — this is a P1 session addition, and the GPT
  // path is pinned to its pre-session mask (it renders "great before" per the
  // user; the carve stays on for Gemini, which keeps the working clip).
  const carveStamp = carveRoads
    ? buildOsmRoadCarveStamp(zones, camera, width, height, terrainHeight)
    : null;
  if (carveStamp) {
    const stampCtx = carveStamp.getContext('2d')!;
    stampCtx.globalCompositeOperation = 'source-in';
    stampCtx.fillStyle = '#000000';
    stampCtx.fillRect(0, 0, width, height);
    ctx.drawImage(carveStamp, 0, 0);
  }

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
 *  multi-angle references per zone (0° street-level + 45° + 90° aerials).
 *  Per pilot memory: Gemini accepts ~3600 images / 20MB total; 48 at ~40KB
 *  each = ~2MB, well within limits. Sweet spot for reference-count was 3
 *  views per zone (0° + 45° + 90°), so up to ~16 zones × 3 = 48. */
const MAX_ARCHETYPE_IMAGES = 48;

/** Aerial angle suffixes to look for alongside the street-level variant_N.png.
 *  Files are named `variant_N_angle_XX.jpg` where XX is one of these values.
 *  Order matters — each zone's refs go to Gemini in this order. Street-level
 *  always comes first; then the aerial(s) from oblique to top-down. */
const AERIAL_ANGLE_SUFFIXES: Array<{ suffix: number; label: string }> = [
  // `suffix` = on-disk filename number (variant_N_angle_60.jpg) — NOT renamed.
  // `label`  = what Gemini sees; reflects the images' TRUE measured angle.
  // The "60°" files actually generated at ~45-50° elevation, so we label them 45°
  // (clean 0/45/90 set). See docs/REFERENCE_IMAGE_ANGLE_AUDIT_2026-05-21.md.
  // The 30° probe was removed — those files exist for only 4 archetypes.
  { suffix: 60, label: '45° oblique aerial' },
  { suffix: 90, label: '90° nadir / top-down aerial' },
];

/**
 * Collect archetype reference card images for multi-image rendering.
 *
 * For each zone, discovers and loads up to 3 reference images:
 *   1. 0° eye-level / street view (the variant_N.png thumbnail)
 *   2. 45° oblique aerial (variant_N_angle_60.jpg — labeled 45° per audit; file kept as _angle_60)
 *   3. 90° nadir / top-down aerial (variant_N_angle_90.jpg, if present)
 *
 * Each image is compressed to 512px JPEG @ 0.7 (~30-50KB) and tagged with
 * the viewing angle so the prompt can explain what each reference shows.
 *
 * Aerial variants that don't exist on disk (most archetypes don't have them
 * generated yet — pilot covers only 4 building + 3 open-space archetypes)
 * are silently skipped; the zone falls back to just its street-level ref.
 */
/**
 * Rasterize the AI-planner plan zones into an annotation-free flat-color
 * nadir diagram (mirrors backend plan_diagram.py): the authoritative-geometry
 * conditioning input. Returns base64 PNG, or null when the visible zone set
 * isn't a drawn plan. Diagram-research rules: one flat color per role, no
 * text, no gradients. Buildings additionally get a thin white outline —
 * abutting same-color bars of a perimeter block otherwise merge into one
 * unreadable mass — and courtyards draw green like parks (their role is
 * 'courtyard', not 'open_space'; without it the block centre reads as
 * unplanned white ground).
 */
function buildPlanConditioningDiagram(zones: SiteZone[], sizePx = 1024): string | null {
  const ROLE_COLORS: Record<string, string> = {
    street: '#808080',
    open_space: '#7cb342',
    courtyard: '#7cb342',
    building: '#b03a2e',
  };
  const planZones = zones.filter((z) => {
    const role = (z.properties as Record<string, unknown> | undefined)?._plan_role as string;
    return ROLE_COLORS[role] && (z.coordinates?.length ?? 0) >= 3;
  });
  if (planZones.length < 4) return null;

  let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
  for (const zone of planZones) {
    for (const [lng, lat] of zone.coordinates) {
      if (lng < minLng) minLng = lng;
      if (lng > maxLng) maxLng = lng;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    }
  }
  const midLat = (minLat + maxLat) / 2;
  const mPerLng = 111_320 * Math.cos((midLat * Math.PI) / 180);
  const mPerLat = 111_320;
  const spanM = Math.max((maxLng - minLng) * mPerLng, (maxLat - minLat) * mPerLat) || 1;
  const padM = spanM * 0.04;
  const originX = minLng * mPerLng - padM;
  const originY = minLat * mPerLat - padM;
  const scale = sizePx / (spanM + 2 * padM);

  const diagramCanvas = document.createElement('canvas');
  diagramCanvas.width = sizePx;
  diagramCanvas.height = sizePx;
  const ctx = diagramCanvas.getContext('2d')!;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, sizePx, sizePx);

  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 3;
  for (const role of ['street', 'open_space', 'courtyard', 'building']) {
    ctx.fillStyle = ROLE_COLORS[role];
    for (const zone of planZones) {
      if ((zone.properties as Record<string, unknown>)._plan_role !== role) continue;
      ctx.beginPath();
      zone.coordinates.forEach(([lng, lat], i) => {
        const x = (lng * mPerLng - originX) * scale;
        const y = sizePx - (lat * mPerLat - originY) * scale;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.fill();
      if (role === 'building') ctx.stroke();
    }
  }
  return diagramCanvas.toDataURL('image/png').split(',')[1];
}

async function collectArchetypeImages(
  zones: SiteZone[],
): Promise<Array<{ image_base64: string; label: string; zone_color: string; angle: string }>> {
  const images: Array<{ image_base64: string; label: string; zone_color: string; angle: string }> = [];
  // Zone colors are assigned per archetype, so one ref set per unique
  // (archetype, variant, color) covers every zone sharing it. Without this an
  // AI-planner plan (16 bars × 1 archetype) floods the budget with 48
  // duplicates — and the repeated hero card starts steering the whole
  // composition instead of the drawn zones.
  const seenRefSets = new Set<string>();

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

    // Custom-style zone: user-uploaded photos replace archetype card images
    const customStyle = getCustomZoneStyle(zone);
    if (customStyle) {
      const zoneColor = colorName(resolveZoneColor(zone));
      const zoneName = zone.name || zone.zone_type;
      for (const url of customStyle.photoUrls) {
        if (images.length >= MAX_ARCHETYPE_IMAGES) break;
        try {
          const resp = await fetch(resolveApiFileUrl(url));
          if (!resp.ok) {
            console.warn(`[GlobeAIRender] custom photo fetch ${resp.status}: ${url}`);
            continue;
          }
          const blob = await resp.blob();
          const base64 = await compressImage(blob, 512, 0.7);
          images.push({
            image_base64: base64,
            label: `User reference photo for ${zoneName} — match the architectural style, materials, and colors shown`,
            zone_color: zoneColor,
            angle: 'user reference',
          });
          console.log(`[GlobeAIRender] Custom zone "${zoneName}": attached user reference photo`);
        } catch (e) {
          console.warn(`[GlobeAIRender] custom photo fetch error: ${url}`, e);
        }
      }
      continue;
    }

    if (!archetypeId) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — no archetype ID`);
      continue;
    }

    // Exact-program parks already attach a to-scale geometry diagram and a
    // detailed material/canopy contract. Their legacy catalog cards can depict
    // attractive but contradictory programs (for example a Japanese-garden
    // card with European parterres and a fountain). Keep those cards out of
    // the render stack so appearance references never overrule topology.
    if (resolveCommunity3DKind(zone) === 'park') {
      const parkProfile = resolveParkGroundProfile(zone);
      if (!parkProfile.id.startsWith('catalog-')) {
        console.log(
          `[GlobeAIRender] Exact-program park "${zone.name || archetypeId}" uses its geometry diagram and profile instead of potentially conflicting catalog cards`,
        );
        continue;
      }
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
    const refSetKey = `${entry.id}|${variant?.id || ''}|${zoneColor}`;
    if (seenRefSets.has(refSetKey)) continue;
    seenRefSets.add(refSetKey);
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
          console.log(`[GlobeAIRender] Archetype image: ${title} [0° eye-level / street view] — ${sizeKB}KB`);
          images.push({
            image_base64: base64,
            label: `${title} — 0° eye-level / street view`,
            zone_color: zoneColor,
            angle: '0° eye-level / street view',
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

/** Keep only zones that can contribute pixels to the captured frame. This is
 * separate from occlusion culling: off-screen polygons are irrelevant even
 * when they are not hidden behind another building. */
function selectZonesInRenderFrame(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): SiteZone[] {
  const marginPx = Math.max(24, Math.min(width, height) * 0.03);
  return zones.filter((zone) => {
    if (zone.zone_type === 'site_boundary') return true;
    if (!zone.coordinates || zone.coordinates.length < 3) return false;
    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const projected = zone.coordinates
      .map((coordinate) => projectToPixels(
        coordinate[0],
        coordinate[1],
        zoneTerrainHeight,
        camera,
        width,
        height,
      ))
      .filter(Boolean) as { x: number; y: number }[];
    const buildingHeight = isBuildingZone(zone) ? getZoneBuildingHeight(zone) : 0;
    if (buildingHeight > 0) {
      projected.push(...zone.coordinates
        .map((coordinate) => projectToPixels(
          coordinate[0],
          coordinate[1],
          zoneTerrainHeight + buildingHeight,
          camera,
          width,
          height,
        ))
        .filter(Boolean) as { x: number; y: number }[]);
    }
    return projectedBoundsIntersectFrame(projected, width, height, marginPx);
  });
}

/** Add a bounded set of local, zero-credit park diagrams to the final render
 * request. The live screenshot carries appearance; these north-up diagrams
 * prevent image models from simplifying a reservoir shoreline, sports field,
 * fountain, bridge alignment, or greenway into generic landscaping. */
function collectParkGeometryImages(
  zones: SiteZone[],
): Array<{ image_base64: string; label: string; zone_color: string; angle: string }> {
  return selectParkRenderGeometryZones(zones).flatMap((zone) => {
    const diagram = buildParkDiagram(zone);
    if (!diagram) return [];
    const profile = resolveParkGroundProfile(zone);
    const imageBase64 = diagram.dataUrl.split(',')[1];
    if (!imageBase64) return [];
    return [{
      image_base64: imageBase64,
      label: `PARK GEOMETRY DIAGRAM — authoritative north-up internal layout for "${zone.name || profile.title}": ${profile.renderSummary}. Preserve the parcel boundary, paths, gateways, water/field footprints, fixed pads and structure alignments exactly. PROGRAM LOCKS: ${profile.guideLegend.join('; ')}. ${diagram.fitInstruction} FORBIDDEN REDESIGN: ${profile.criticalConstraints} Diagram colors are schematic geometry cues, not final materials.`,
      zone_color: colorName(resolveZoneColor(zone)),
      angle: '90° north-up park geometry diagram',
    }];
  });
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
  // Custom-style zone: the user's own (LLM-expanded) description IS the
  // rendering instruction — it replaces any archetype overlay prompt.
  const customStyle = getCustomZoneStyle(zone);
  if (customStyle) return customStyle.promptText;

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
  const selectedVariantId = (props.development_selected_variant_id as string)
    || (props.green_space_selected_variant_id as string)
    || (props.road_selected_variant_id as string)
    || (props.plaza_selected_variant_id as string)
    || '';
  const variant = entry.variants?.find((v: any) => v.id === selectedVariantId);
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

export const MAX_DETAILED_RENDER_PROMPT_ZONES = 80;
export const MAX_DISTRICT_RENDER_GROUP_LINES = 32;
export const MAX_DISTRICT_RENDER_LABELS = 80;

/**
 * Build SCHEMA-style structured prompt for aerial renders.
 * Based on the proven Mapbox aerial prompt structure.
 */
export function buildPrompt(
  zones: SiteZone[],
  style: string,
  camera?: THREE.Camera,
  terrainHeight?: number,
  modeledBuildingIds?: Set<string>,
): string {
  // --- CAMERA ANGLE ---
  let pitchDesc = 'oblique aerial (~40deg camera elevation above ground; ~50deg from nadir)';
  let pitchFromNadirDeg = 50;
  if (camera && terrainHeight != null) {
    // Estimate angle from nadir, then convert to architectural camera elevation.
    const camDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
    const camPos = camera.position.clone().normalize(); // surface normal at camera position
    const cosAngle = THREE.MathUtils.clamp(camDir.dot(camPos.clone().negate()), -1, 1);
    pitchFromNadirDeg = Math.acos(cosAngle) * 180 / Math.PI;
    const cameraElevationDeg = pitchFromNadirToCameraElevation(pitchFromNadirDeg);
    pitchDesc = describeCameraAngleForPrompt(pitchFromNadirDeg);
    console.log(
      `[GlobeAIRender] Camera angle: ${cameraElevationDeg}° elevation, `
      + `${getAngleFromNadirLabelValue(pitchFromNadirDeg)}° from nadir -> "${pitchDesc}"`,
    );
  }

  // --- COMPOSITION ---
  const hasBuildings = zones.some(isBuildingZone);
  const composition = hasBuildings
    ? `${pitchDesc} view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context. Render buildings with correct 3D perspective for this viewing angle.`
    : `${pitchDesc} view, ground-level zones only on photorealistic 3D terrain.`;

  // --- LIGHTING ---
  const lightingMap: Record<string, string> = {
    photorealistic: 'Golden hour, low warm southwest sun creating strong directional light. Long crisp architectural shadows with deep material contrast — sunlit facades should read bright and textured, shadowed facades cool and recessive. Sharp highlight-to-shadow transitions emphasizing facade depth (cornices, mullions, balcony edges, podium returns) rather than flat global illumination.',
    winter: 'Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky.',
    atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze.',
    night: 'Moonlight and city glow, artificial lighting, warm window light.',
    // Development renders composite onto the live capture — invented lighting
    // drama would split the frame from its photographic context.
    development: 'Match the exact sun direction, colour temperature and atmosphere already visible in the surrounding photograph; the development and its context share one consistent daylight.',
  };

  // --- ZONES (SCHEMA format) — skip site_boundary, sort by polygon area descending ---
  // Largest zones first = most visually dominant archetypes get highest attention weight
  const renderZones = zones
    .filter(z => z.zone_type !== 'site_boundary')
    .sort((a, b) => zoneAreaM2(b) - zoneAreaM2(a));
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
    const pixel = projectToPixels(lng, lat, getZoneTerrainHeight(zone, terrainHeight), camera, W, H);
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
  interface DistrictRenderGroup {
    key: string;
    kind: Community3DKind | 'zone';
    title: string;
    count: number;
    positions: Set<string>;
    colors: Set<string>;
    minFloors: number | null;
    maxFloors: number | null;
    minHeightM: number | null;
    maxHeightM: number | null;
    minAreaM2: number;
    maxAreaM2: number;
    featureSummary: string;
    modeledCount: number;
    contextConnectionCount: number;
  }
  const districtGroups = new Map<string, DistrictRenderGroup>();
  for (let i = 0; i < renderZones.length; i++) {
    const zone = renderZones[i];
    const color = colorName(resolveZoneColor(zone));
    const position = screenPositionForZone(zone);
    const props = zone.properties || {};
    const info = getZoneArchetypeInfo(zone);
    const communityKind = resolveCommunity3DKind(zone);

    const floors = readFiniteNumber(props.floors) ?? 0;
    const heightM = getZoneBuildingHeight(zone);
    // Custom-style zones: the retained archetype title is overridden by the
    // user's description — label the zone by its own name instead.
    const name = (getCustomZoneStyle(zone) ? zone.name : undefined)
      || info.archetypeTitle || zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type;
    const footprint = formatFootprintMetrics(zone);

    // Scale descriptor
    let scale = '';
    if (isBuildingZone(zone)) {
      const scaleParts: string[] = [];
      if (floors > 0 && heightM > 0) scale = `${floors}F ${Math.round(heightM)}m`;
      else if (floors > 0) scale = `${floors}F`;
      else if (heightM > 0) scale = `${Math.round(heightM)}m`;
      else if (info.minFloors && info.maxFloors) {
        scale = info.minFloors === info.maxFloors ? `${info.minFloors}F` : `${info.minFloors}-${info.maxFloors}F`;
      } else scale = 'multi-story';
      scaleParts.push(scale);
      if (footprint) scaleParts.push(`drawn footprint ${footprint}`);
      if (info.suggestedWidth_m && info.suggestedDepth_m) scaleParts.push(`archetype typical ${info.suggestedWidth_m}m x ${info.suggestedDepth_m}m`);
      else if (info.suggestedAreaSqm) scaleParts.push(`archetype typical ${info.suggestedAreaSqm} m2`);
      scale = scaleParts.join(' | ');
    } else {
      scale = footprint ? `drawn footprint ${footprint}` : 'gnd';
    }

    // Map overlay prompt (archetype-specific aerial rendering instruction)
    const overlayPrompt = getMapOverlayPrompt(zone);

    // Feature keywords from archetype metadata
    const features: string[] = [];
    const parkProfile = communityKind === 'park'
      ? resolveParkGroundProfile(zone)
      : null;
    const streetProfile = communityKind === 'street'
      ? resolvePilotStreetSectionProfile(zone)
      : null;
    const authoredGround = hasAuthoredCommunityGround(zone);
    const parkFitInstruction = parkProfile ? resolveParkGroundFitInstruction(zone) : '';
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

    // AI-planner park zones: state the program explicitly and first (survives
    // the feature budget) — models otherwise invent ponds/amphitheatres in
    // large green polygons.
    if (props._plan_role === 'open_space' && !authoredGround && !parkProfile?.isPilot) {
      features.unshift('flat neighbourhood park: lawn, tree clusters, walking paths — no water features, no amphitheatre');
    }

    if (parkProfile && authoredGround) {
      features.unshift(
        `3D PARK GROUND TRUTH visible in the screenshot - PRESERVE its exact paths, water/field footprints, fixed pads, shoreline and dam geometry; standing trees and benches are intentionally deferred to the render pass; ${parkProfile.renderSummary}; ${parkFitInstruction}`,
      );
    }
    if (parkProfile) {
      features.unshift(buildParkRenderQualityInstruction(parkProfile, pitchFromNadirDeg));
      // This must precede the longer quality paragraph inside the bounded
      // per-zone feature string. Otherwise mature-planting prose consumes the
      // full budget before the model sees the exact paths/beds/pads it must
      // preserve (the botanical trial otherwise invented a fountain/parterre).
      features.unshift(
        `PARK TOPOLOGY LOCK - more important than planting style: ${parkProfile.renderSummary}; ${parkProfile.guideLegend.join('; ')}; ${parkProfile.criticalConstraints}; ${parkFitInstruction}`,
      );
    }
    if (streetProfile) {
      features.unshift(buildStreetRenderGroundTruthInstruction(streetProfile));
    }
    if (communityKind === 'street' && authoredGround && !streetProfile) {
      features.unshift(
        '3D STREET GROUND TRUTH visible in the screenshot - PRESERVE the exact carriageway/path edges, markings and curb lines already shown; trees and furniture are render-stage elements and may be added only on non-circulation planting/furnishing areas with clear crossings, driveways and sightlines; finish materials without redesigning the section',
      );
    }
    if (props.context_connection === true) {
      const connectionKind = props.street_role === 'path' ? 'walking/cycling path' : 'street';
      features.unshift(
        `CONTEXT CONNECTION: this ${connectionKind} reaches the site boundary to join an existing corridor - keep its centerline, grade and usable surface continuous across the seam; do not terminate it with a curb, lawn, building or planting`,
      );
    }

    // Perimeter blocks under-specify themselves as polygons alone: same-shade
    // bars read as one mass and come back as freestanding slabs in a row
    // (2026-07-10 As-of-Right render). State the block form in words, first,
    // for the courtyard and for every bar of the block.
    if (props._plan_role === 'courtyard') {
      features.unshift('enclosed courtyard at the centre of a perimeter block, ringed by the adjacent buildings on all sides, open to the sky — lawn and trees, not a street or front yard');
    }
    if (props._plan_role === 'building' && props.typology === 'perimeter_block') {
      features.unshift('one bar of a perimeter block — continuous street wall with the adjoining buildings, enclosing the central courtyard; build the drawn footprint, not a freestanding slab');
    }

    // Buildings whose generated 3D model is placed on the globe: the capture
    // already contains the true massing — the strongest geometry conditioning
    // available. Instruct preservation, not replacement. First in the feature
    // list so it survives the budget.
    if (zone.building_id && modeledBuildingIds?.has(zone.building_id)) {
      features.unshift('shown as a 3D massing model in the screenshot — PRESERVE its exact footprint, height, roofline and silhouette; render realistic facades, materials and context onto that geometry in the declared style; do NOT replace it with a different building');
    }

    // Custom-style zones carry the user's full description — give it more room
    // than the compressed archetype keyword budget (expansions run ~600-900 chars).
    const featureBudget = getCustomZoneStyle(zone)
      ? 900
      : parkProfile
        // Park prompts must retain both the geometry-first topology/whole-
        // element locks and the following mature-landscape quality guidance.
        // Concave parcels add a bounded fit override, so the previous 1,200
        // character cap could truncate the quality clause entirely.
        ? 1700
        : streetProfile
          ? 650
          // Preserve the signature material/form cues that commonly appear
          // after the first sentence (fire escapes, awnings, civic glazing,
          // courtyard enclosure) while remaining safely bounded at district
          // scale by the group-line cap below.
          : (isBuildingZone(zone) ? 420 : 200);
    const featureStr = features.join(', ').substring(0, featureBudget);
    zoneLines.push(`${i + 1}. [${color}] @ ${position} of frame | ${name} | ${scale} | ${featureStr || 'render as described'}`);

    const groupKind = communityKind ?? (isBuildingZone(zone) ? 'building' : 'zone');
    const groupKey = [
      groupKind,
      name,
      parkProfile?.id ?? '',
      streetProfile?.archetypeId ?? '',
      String(props._plan_role ?? ''),
      String(props.typology ?? ''),
    ].join('|');
    const areaM2 = Math.max(0, zoneAreaM2(zone));
    const isModeled = Boolean(zone.building_id && modeledBuildingIds?.has(zone.building_id));
    const isContextConnection = props.context_connection === true;
    const existingGroup = districtGroups.get(groupKey);
    if (existingGroup) {
      existingGroup.count += 1;
      existingGroup.positions.add(position);
      existingGroup.colors.add(color);
      if (floors > 0) {
        existingGroup.minFloors = existingGroup.minFloors == null
          ? floors
          : Math.min(existingGroup.minFloors, floors);
        existingGroup.maxFloors = existingGroup.maxFloors == null
          ? floors
          : Math.max(existingGroup.maxFloors, floors);
      }
      if (heightM > 0) {
        existingGroup.minHeightM = existingGroup.minHeightM == null
          ? heightM
          : Math.min(existingGroup.minHeightM, heightM);
        existingGroup.maxHeightM = existingGroup.maxHeightM == null
          ? heightM
          : Math.max(existingGroup.maxHeightM, heightM);
      }
      existingGroup.minAreaM2 = Math.min(existingGroup.minAreaM2, areaM2);
      existingGroup.maxAreaM2 = Math.max(existingGroup.maxAreaM2, areaM2);
      existingGroup.modeledCount += isModeled ? 1 : 0;
      existingGroup.contextConnectionCount += isContextConnection ? 1 : 0;
    } else {
      districtGroups.set(groupKey, {
        key: groupKey,
        kind: groupKind,
        title: name,
        count: 1,
        positions: new Set([position]),
        colors: new Set([color]),
        minFloors: floors > 0 ? floors : null,
        maxFloors: floors > 0 ? floors : null,
        minHeightM: heightM > 0 ? heightM : null,
        maxHeightM: heightM > 0 ? heightM : null,
        minAreaM2: areaM2,
        maxAreaM2: areaM2,
        featureSummary: featureStr || 'render as described',
        modeledCount: isModeled ? 1 : 0,
        contextConnectionCount: isContextConnection ? 1 : 0,
      });
    }
  }

  const useDistrictZoneGroups = renderZones.length > MAX_DETAILED_RENDER_PROMPT_ZONES;
  const allDistrictGroups = [...districtGroups.values()];
  const prioritySortedDistrictGroups = [...allDistrictGroups].sort((left, right) => {
    const priority = (group: DistrictRenderGroup): number => (
      (group.contextConnectionCount > 0 ? 1_000_000_000 : 0)
      + (group.kind === 'park' || group.kind === 'street' ? 10_000_000 : 0)
      + (group.modeledCount > 0 ? 100_000 : 0)
      + group.count
    );
    return priority(right) - priority(left)
      || right.count - left.count
      || left.kind.localeCompare(right.kind)
      || left.title.localeCompare(right.title);
  });
  const hasDistrictGroupOverflow = prioritySortedDistrictGroups.length > MAX_DISTRICT_RENDER_GROUP_LINES;
  const selectedDistrictGroups = hasDistrictGroupOverflow
    ? prioritySortedDistrictGroups.slice(0, MAX_DISTRICT_RENDER_GROUP_LINES - 1)
    : prioritySortedDistrictGroups;
  const overflowDistrictGroups = hasDistrictGroupOverflow
    ? prioritySortedDistrictGroups.slice(MAX_DISTRICT_RENDER_GROUP_LINES - 1)
    : [];
  const districtZoneLines = selectedDistrictGroups
    .sort((left, right) => (
      right.count - left.count
      || left.kind.localeCompare(right.kind)
      || left.title.localeCompare(right.title)
    ))
    .map((group, index) => {
      const scaleParts: string[] = [];
      if (group.minFloors != null && group.maxFloors != null) {
        scaleParts.push(group.minFloors === group.maxFloors
          ? `${group.minFloors}F`
          : `${group.minFloors}-${group.maxFloors}F`);
      }
      if (group.minHeightM != null && group.maxHeightM != null) {
        scaleParts.push(Math.round(group.minHeightM) === Math.round(group.maxHeightM)
          ? `${Math.round(group.minHeightM)}m high`
          : `${Math.round(group.minHeightM)}-${Math.round(group.maxHeightM)}m high`);
      }
      const formatGroupArea = (area: number): string => (
        area >= 10_000 ? `${(area / 10_000).toFixed(1)} ha` : `${Math.max(1, Math.round(area))} m2`
      );
      scaleParts.push(group.minAreaM2 === group.maxAreaM2
        ? `${formatGroupArea(group.minAreaM2)} footprints`
        : `${formatGroupArea(group.minAreaM2)}-${formatGroupArea(group.maxAreaM2)} footprints`);
      const positions = [...group.positions].sort().join(', ');
      const colors = [...group.colors].sort().join(', ');
      const geometryTruth = group.modeledCount > 0
        ? ` ${group.modeledCount}/${group.count} are visible 3D proposal geometries: preserve every individual footprint, height, roofline and silhouette.`
        : '';
      const contextTruth = group.contextConnectionCount > 0
        ? ` ${group.contextConnectionCount} are context connections and must continue through the site edge.`
        : '';
      const featureLimit = group.kind === 'building' ? 420 : 900;
      return `${index + 1}. ${group.count} ${group.kind} zone${group.count === 1 ? '' : 's'} | ${group.title} | fills ${colors} | across ${positions} | ${scaleParts.join(', ')} | ${group.featureSummary.substring(0, featureLimit)}${geometryTruth}${contextTruth}`;
    });
  if (overflowDistrictGroups.length > 0) {
    const overflowByKind = new Map<string, number>();
    let overflowZoneCount = 0;
    let overflowContextConnections = 0;
    for (const group of overflowDistrictGroups) {
      overflowByKind.set(group.kind, (overflowByKind.get(group.kind) ?? 0) + group.count);
      overflowZoneCount += group.count;
      overflowContextConnections += group.contextConnectionCount;
    }
    const overflowInventory = [...overflowByKind.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([kind, count]) => `${count} ${kind}`)
      .join(', ');
    districtZoneLines.push(
      `${districtZoneLines.length + 1}. ${overflowDistrictGroups.length} additional program groups covering ${overflowZoneCount} zones (${overflowInventory}) | Follow the representative on-image labels, group-consistent fills and exact mask/3D geometry; do not merge or omit these instances.${overflowContextConnections > 0 ? ` ${overflowContextConnections} are context connections and must continue through the site edge.` : ''}`,
    );
  }

  const zoneSchemaClause = useDistrictZoneGroups
    ? `DISTRICT ZONE GROUPS (${districtGroups.size} archetype/program groups summarized in ${districtZoneLines.length} bounded lines; all ${renderZones.length} individual polygons remain authoritative in the image and mask):\n${districtZoneLines.join('\n')}`
    : `ZONES:\n${zoneLines.join('\n')}`;
  const zoneIdentificationClause = useDistrictZoneGroups
    ? `DISTRICT IDENTIFICATION: Representative text labels identify each program group; every individual zone remains located by its dashed polygon, group-consistent fill, exact mask and any visible 3D proposal geometry. The grouped list summarizes repeated programs only; it does not merge, relocate, omit or enlarge polygons. Treat every separate masked polygon or visible 3D proposal object as one authoritative instance of its group.`
    : `ZONE IDENTIFICATION: Each zone polygon has TWO visual identifiers: (1) its archetype name written as colored text on the polygon, and (2) a unique bright DASHED BORDER in a distinct color (red, blue, magenta, cyan, yellow, etc.). The text label color matches the border color. Use BOTH the text label AND the border color to identify each zone. Zones with similar fill colors can be distinguished by their different border colors. Road/street zones can be distinguished from existing roads by their dashed border — only polygons with dashed borders are zones to render.`;
  const zoneAssignmentClause = useDistrictZoneGroups
    ? `DISTRICT ASSIGNMENT: Preserve the exact on-screen location, footprint, separation, orientation and occlusion of every individual proposal. Apply each grouped archetype consistently to all matching polygon instances without collapsing a row of buildings into one slab, filling courtyards, moving parks, or simplifying street/path networks. The image geometry and mask override any typical archetype dimensions.`
    : `ZONE ASSIGNMENT: Each zone line in the ZONES list above begins with "@ SCREEN-POSITION" (values: UPPER-LEFT, UPPER-CENTER, UPPER-RIGHT, MIDDLE-LEFT, CENTER, MIDDLE-RIGHT, LOWER-LEFT, LOWER-CENTER, LOWER-RIGHT) — this is the location of that zone's polygon within THIS image's 2D frame. It is a THIRD identification axis alongside color and text label. Verify color, label, AND screen position all match before rendering an archetype at a polygon. If a line says "[magenta] @ LOWER-RIGHT | Grand Magasin", render the Grand Magasin archetype at the polygon in the lower-right region of the frame — NOT at a polygon elsewhere even if its color looks similar. Never swap archetypes between polygons. When two zones have similar fill colors, the SCREEN-POSITION resolves the ambiguity — trust the position anchor over color similarity.`;

  const publicRealmContextClause = buildPublicRealmSceneContextPrompt(
    renderZones,
    { sceneReferenceAttached: true },
  );

  // --- ASSEMBLE SCHEMA PROMPT ---
  // Artistic styles drop the photoreal-specific clauses (color temp matching,
  // atmospheric perspective, "match adjacent real buildings") that otherwise
  // contradict the STYLE instruction and cause Gemini to drift back toward
  // photorealism on some seeds — the ~1-of-3-respects-style failure mode.
  const isArtistic = ARTISTIC_STYLES.has(style);

  const styleClause = `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`;
  const compositionClause = isArtistic
    ? `COMPOSITION: ${pitchDesc} view. The input screenshot provides scene layout and zone positions only — render the output fully in the declared STYLE, not as a photograph.`
    : `COMPOSITION: ${composition}`;
  const lightingClause = isArtistic ? null : `LIGHTING: ${lightingMap[style] || lightingMap.photorealistic}`;
  const contextClause = isArtistic
    ? `CONTEXT: The input screenshot is a layout reference from a 3D city model. Use it to understand WHERE each zone sits and WHAT surrounds it — but render the ENTIRE output in the declared STYLE. Tile photographs outside the mask are still inputs, not targets to match; the final output should read consistently as the declared artistic medium across the full frame.`
    : `CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.`;
  // Zones backed by placed 3D models: the massing in the screenshot is truth.
  const hasModeledZones = Boolean(modeledBuildingIds?.size)
    && renderZones.some(z => z.building_id && modeledBuildingIds!.has(z.building_id));
  const modeledMandatory = hasModeledZones
    ? ` EXCEPTION — 3D MASSING MODELS: some building zones already contain a detailed 3D building model in the screenshot (not a flat colored polygon). For those, KEEP the model's exact geometry — footprint, height, roofline, silhouette — and render facades/materials/entourage onto it in the declared style.`
    : '';
  const hasGroundTruthZones = renderZones.some((zone) => (
    hasAuthoredCommunityGround(zone)
    || (resolveCommunity3DKind(zone) === 'park' && resolveParkGroundProfile(zone).isPilot)
    || (resolveCommunity3DKind(zone) === 'street' && Boolean(resolvePilotStreetSectionProfile(zone)))
  ));
  const groundTruthMandatory = hasGroundTruthZones
    ? ' EXCEPTION - 3D PARK/STREET GROUND TRUTH: pilot park surfaces and street cross-sections already visible in the screenshot are authoritative proposal geometry. Finish and blend them photographically, but do not redesign, move, simplify or replace their paths, fields, ponds, shorelines, dams, lanes, medians, cycle tracks or sidewalks. Park and street trees, benches and other furniture may be intentionally absent from the tile view: add them only on eligible dry planting/furnishing areas with circulation, crossing, sightline and water setbacks.'
    : '';
  const hasParkZones = renderZones.some((zone) => resolveCommunity3DKind(zone) === 'park');
  const parkQualityMandatory = hasParkZones
    ? ` PARK QUALITY: every park must read as a mature designed urban landscape with a legible connected path network, intentional clearings and destinations, layered species-diverse canopy, understory and groundcover. ${pitchFromNadirDeg <= 30 ? 'From this near-nadir view, preserve a crisp aerial mosaic of canopy masses, lawn, beds, paths, water and hardscape.' : 'From this oblique view, show convincing canopy depth, crown variation and grounded shadows while keeping paths, clearings, water and destination structures readable.'} Never return flat green fill, sparse identical tree dots or disconnected decorative paths.`
    : '';
  const hasContextConnections = renderZones.some(
    (zone) => (zone.properties as Record<string, unknown> | undefined)?.context_connection === true,
  );
  const contextConnectionMandatory = hasContextConnections
    ? ' CONTEXT CONNECTIONS: any proposed street or path that reaches the site boundary must visibly continue into the matching existing outside corridor with aligned centerline, grade and usable surface; never cap it with a curb, lawn, building or planting.'
    : '';
  const zoneReadingInstruction = useDistrictZoneGroups
    ? 'Use the representative labels, group-consistent fills, dashed polygons and grouped list together to identify what to render at every individual polygon.'
    : 'Read the text label on each polygon to identify what to render there.';
  const mandatoryClause = (isArtistic
    ? `MANDATORY: The white mask shows the EXACT area to edit. Replace the colored polygon overlays with zone content rendered in the declared STYLE. ${zoneReadingInstruction} Zone content must be rendered in the same style as the rest of the composition — no photorealistic material breakthrough inside the mask.`
    : `MANDATORY: The white mask shows the EXACT area to edit. Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials. ${zoneReadingInstruction} Realistic rooftop materials, facades, and landscaping. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`
  ) + modeledMandatory + groundTruthMandatory + parkQualityMandatory + contextConnectionMandatory;
  const prohibitionsClause = (isArtistic
    ? `PROHIBITIONS: colored polygon fills visible on ANY rendered surface, dashed boundary lines or outlines visible, text labels visible, watermarks, mixing photorealistic passages with the declared artistic style (entire output must be in one style), any photoreal material rendering inside the mask.`
    : `PROHIBITIONS: colored polygon fills visible on ANY rendered surface (rooftops, facades, ground), dashed boundary lines or outlines visible, text labels visible, watermarks, color temperature mismatch between rendered and existing buildings, rendered buildings appearing unnaturally crisp or clean compared to surroundings${style === 'winter' ? ', lush green vegetation, summer foliage, bright green lawns' : ''}`
  ) + (hasModeledZones ? ' Also prohibited: altering the silhouette, massing, footprint or height of any 3D building model visible in the screenshot.' : '');
  const siteBoundaryClause = isArtistic
    ? `SITE BOUNDARY: Do NOT add any NEW buildings, structures, roads, people, vehicles, or landscaping outside the colored zone polygons. The output across the entire frame should read as a coherent composition in the declared STYLE.`
    : `SITE BOUNDARY: Do NOT add any NEW buildings, structures, roads, people, vehicles, or landscaping outside the colored zone polygons. However, rendered zones MUST blend seamlessly into the surrounding landscape at their edges — match lighting, ground plane, and context so there is no visible seam between rendered and existing areas.`;

  const sections = [
    styleClause,
    compositionClause,
    lightingClause,
    contextClause,
    // Photoreal-only: color temperature matching and atmospheric perspective.
    // Artistic styles skip these — they contradict the STYLE instruction.
    !isArtistic ? `COLOR TEMPERATURE MATCHING: Analyze the color temperature and atmospheric conditions of the EXISTING buildings and terrain in the photograph. Match the EXACT same warm/cool tone, haze level, and ambient light color on all rendered zones. If the scene has golden-hour warmth, render buildings with the same warm amber tones — NOT neutral daylight grey. Rendered materials must look like they exist in the same atmosphere and light as the surrounding real buildings.` : null,
    !isArtistic ? `ATMOSPHERIC PERSPECTIVE: Apply the same atmospheric haze and aerial perspective visible on surrounding buildings at similar distances. Distant rendered zones should have reduced contrast and shifted color matching the existing depth cues in the photograph.` : null,
    `MAP SCALE: The drawn footprint measurements in ZONES are computed from the longitude/latitude map and are authoritative. Adapt each archetype to fit that footprint; do not enlarge buildings to match a reference image or typical archetype scale.`,
    `NUMERICAL INVENTORY: This scene contains exactly ${renderZones.length} zone${renderZones.length > 1 ? 's' : ''}: ${renderZones.filter(isBuildingZone).length} building${renderZones.filter(isBuildingZone).length !== 1 ? 's' : ''}, ${renderZones.filter(z => resolveCommunity3DKind(z) === 'park').length} park/plaza${renderZones.filter(z => resolveCommunity3DKind(z) === 'park').length !== 1 ? 's' : ''}, ${renderZones.filter(z => resolveCommunity3DKind(z) === 'street').length} street/path${renderZones.filter(z => resolveCommunity3DKind(z) === 'street').length !== 1 ? 's' : ''}.`,
    zoneSchemaClause,
    zoneIdentificationClause,
    zoneAssignmentClause,
    publicRealmContextClause || null,
    mandatoryClause,
    prohibitionsClause,
    siteBoundaryClause,
    `OCCLUSION: Some zones may be partially or fully hidden behind taller buildings from this camera angle. This is CORRECT — do NOT distort the perspective to make hidden zones visible. If a zone is occluded by a building in front of it, leave it hidden. Render only what would naturally be visible from this specific camera position and angle.`,
    // Merged FOOTPRINT + FINAL constraint (they were redundant); the freed
    // constraint-budget slot pays for the STREETS clause appended after the
    // plan diagram is attached (≤8 constraint budget — do-not-retry ledger).
    `FINAL CONSTRAINT: Stay strictly within each colored zone polygon. Rendered footprints, roofs, podiums, walls, and landscaping must match the drawn footprint — never spilling beyond the polygon or mask, never overlapping into adjacent zones. Do not alter pixels outside the mask. Accuracy to the polygon boundary is more important than architectural flair.`,
    // Artistic styles re-anchor the STYLE instruction at the end, since Gemini
    // weights later instructions more heavily. This fights the drift back to
    // photoreal that happens when surrounding instructions assume photoreal.
    isArtistic ? `STYLE REMINDER: The entire output MUST be in the declared style: ${GLOBE_STYLE_PROMPTS[style]}. This is the single most important constraint. Any output that looks photorealistic is wrong.` : null,
  ].filter((x): x is string => x !== null);

  return sections.join('\n');
}

// ─── POST-COMPOSITE COLOR GRADE ───────────────────────────────────────
// Applied AFTER the AI render is composited onto the tile screenshot.
// Unifies Gemini output + Google 3D Tiles into a single "photograph" so
// the rendered zones don't look pasted on. Artistic styles (watercolour,
// charcoal, etc.) are intentionally NOT graded — they stand alone.

interface StyleGrade {
  shadowLift: number;       // 0-255, added to shadow pixels
  highlightWarmth: number;  // 0-255, R+G boost on highlight pixels (can be negative)
  saturation: number;       // 1.0 = neutral, 1.10 = +10%
  vignette: number;         // 0 = off, 0.2 = 20% edge darkening
  coolCast?: number;        // blue boost across the whole image (winter/night)
  shadowCool?: number;      // cool (blue) tint added specifically to shadow pixels — mimics Google Earth's ambient sky fill
}

const STYLE_GRADES: Record<string, StyleGrade> = {
  // Warm sun on highlights, cool-blue ambient in shadows (matches Google Earth tile look), stronger saturation + vignette
  photorealistic:      { shadowLift: 8,  highlightWarmth: 12, saturation: 1.15, vignette: 0.22, shadowCool: 6 },
  photomontage:        { shadowLift: 4,  highlightWarmth: 5,  saturation: 1.06, vignette: 0.12 },
  // Clean premium, atmosphere comes from the capture (taste memo: grade yes, drama no)
  development:         { shadowLift: 5,  highlightWarmth: 6,  saturation: 1.08, vignette: 0.12 },
  // Dramatic: deep rich shadows, heavily warmed highlights, big vignette
  atmospheric:         { shadowLift: 10, highlightWarmth: 18, saturation: 1.18, vignette: 0.30, shadowCool: 8 },
  'site-plan-photo':   { shadowLift: 5,  highlightWarmth: 6,  saturation: 1.08, vignette: 0.10 },
  winter:              { shadowLift: 8,  highlightWarmth: -3, saturation: 0.85, vignette: 0.10, coolCast: 8 },
  night:               { shadowLift: -8, highlightWarmth: 8,  saturation: 1.08, vignette: 0.35, coolCast: 6 },
};
// Any style not listed gets no grade — artistic stylizations (watercolour,
// charcoal, isometric, woodblock, marker-render, clay-maquette, collage,
// risograph, pixel-art, site-plan, site-plan-watercolor) stand alone.

function applyStyleGrade(canvas: HTMLCanvasElement, style: string): void {
  const grade = STYLE_GRADES[style];
  if (!grade) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const w = canvas.width;
  const h = canvas.height;

  const imgData = ctx.getImageData(0, 0, w, h);
  const d = imgData.data;
  const shadowThresh = 96;
  const highlightThresh = 180;
  const clamp = (v: number) => v < 0 ? 0 : v > 255 ? 255 : v;

  for (let i = 0; i < d.length; i += 4) {
    let r = d[i], g = d[i + 1], b = d[i + 2];
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;

    if (lum < shadowThresh) {
      const f = (shadowThresh - lum) / shadowThresh;
      r += grade.shadowLift * f;
      g += grade.shadowLift * f;
      b += grade.shadowLift * f;
      if (grade.shadowCool) {
        b += grade.shadowCool * f;
        r -= grade.shadowCool * 0.4 * f;
      }
    }
    if (lum > highlightThresh) {
      const f = (lum - highlightThresh) / (255 - highlightThresh);
      r += grade.highlightWarmth * f;
      g += grade.highlightWarmth * 0.6 * f;
    }
    if (grade.coolCast) {
      b += grade.coolCast;
    }
    const dr = r - lum, dg = g - lum, db = b - lum;
    r = lum + dr * grade.saturation;
    g = lum + dg * grade.saturation;
    b = lum + db * grade.saturation;

    d[i]     = clamp(r);
    d[i + 1] = clamp(g);
    d[i + 2] = clamp(b);
  }
  ctx.putImageData(imgData, 0, 0);

  if (grade.vignette > 0) {
    const cx = w / 2, cy = h / 2;
    const maxR = Math.sqrt(cx * cx + cy * cy);
    const radial = ctx.createRadialGradient(cx, cy, maxR * 0.55, cx, cy, maxR);
    radial.addColorStop(0, 'rgba(0,0,0,0)');
    radial.addColorStop(1, `rgba(0,0,0,${grade.vignette})`);
    ctx.fillStyle = radial;
    ctx.fillRect(0, 0, w, h);
  }
  console.log(`[GlobeAIRender] Applied color grade for style: ${style}`);
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
 * Wrap a bare base64 payload in a data URI with the correct MIME type.
 * Raw canvas captures are JPEG ('/9j/'…); backend renders are PNG ('iVBOR'…).
 */
function base64ToDataUri(b64: string): string {
  const mime = b64.startsWith('/9j/') ? 'image/jpeg' : 'image/png';
  return `data:${mime};base64,${b64}`;
}

/**
 * P1.8 — verification gate. Fraction of plan-street pixels (outside every
 * building hull) that still read as the same street surface as the raw
 * capture. Scored RELATIVE to the original with luminance normalization so
 * tower shadows / golden-hour lighting don't false-fail (absolute color
 * thresholds do); computed on the raw model output pre-grade. The spec says
 * "after clip" — scoring pre-clip is equivalent here because the sampled
 * pixels (plan streets minus building hulls, which the carve exempts) are
 * exactly the pixels the clip passes through unchanged, and it avoids
 * running the full composite once per candidate.
 * Returns null when the scene has no plan streets or too few visible street
 * pixels — the gate simply doesn't apply.
 */
async function scorePlanStreetSimilarity(
  rawBase64: string,
  renderedBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): Promise<number | null> {
  const streetZones = zones.filter(z =>
    (z.properties as Record<string, unknown> | undefined)?._plan_role === 'street'
    && z.coordinates?.length >= 3);
  if (!streetZones.length) return null;

  // Street mask (alpha): street polygons minus building hulls.
  const mask = document.createElement('canvas');
  mask.width = width;
  mask.height = height;
  const maskCtx = mask.getContext('2d')!;
  maskCtx.fillStyle = '#ffffff';
  for (const zone of streetZones) {
    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
    maskCtx.closePath();
    maskCtx.fill();
  }
  maskCtx.globalCompositeOperation = 'destination-out';
  for (const zone of zones) {
    if (!isBuildingZone(zone) || getZoneBuildingHeight(zone) <= 0) continue;
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;
    const silhouette = zoneSilhouette(zone, pixels, camera, width, height, zoneTerrainHeight);
    maskCtx.beginPath();
    maskCtx.moveTo(silhouette[0].x, silhouette[0].y);
    for (let i = 1; i < silhouette.length; i++) maskCtx.lineTo(silhouette[i].x, silhouette[i].y);
    maskCtx.closePath();
    maskCtx.fill();
  }

  const [origImg, rendImg] = await Promise.all([
    loadImage(base64ToDataUri(rawBase64)),
    loadImage(base64ToDataUri(renderedBase64)),
  ]);
  const rasterize = (img: HTMLImageElement): Uint8ClampedArray => {
    const c = document.createElement('canvas');
    c.width = width;
    c.height = height;
    const cx = c.getContext('2d')!;
    // Aspect-preserving cover, matching the composite path.
    const aspect = img.naturalWidth / img.naturalHeight;
    const canvasAspect = width / height;
    if (Math.abs(aspect - canvasAspect) / canvasAspect > 0.02) {
      const scale = Math.max(width / img.naturalWidth, height / img.naturalHeight);
      const dw = img.naturalWidth * scale;
      const dh = img.naturalHeight * scale;
      cx.drawImage(img, (width - dw) / 2, (height - dh) / 2, dw, dh);
    } else {
      cx.drawImage(img, 0, 0, width, height);
    }
    return cx.getImageData(0, 0, width, height).data;
  };
  const orig = rasterize(origImg);
  const rend = rasterize(rendImg);
  const maskData = maskCtx.getImageData(0, 0, width, height).data;

  let total = 0;
  let similar = 0;
  for (let i = 0; i < maskData.length; i += 16) { // every 4th pixel
    if (maskData[i + 3] < 128) continue;
    const lumOrig = 0.299 * orig[i] + 0.587 * orig[i + 1] + 0.114 * orig[i + 2];
    const lumRend = 0.299 * rend[i] + 0.587 * rend[i + 1] + 0.114 * rend[i + 2];
    // Tolerate uniform lighting/shadow shifts (luminance scale), flag
    // material changes (chroma) — grass over asphalt fails. Known limit: an
    // achromatic repaint (gray podium on gray asphalt) collapses under any
    // luminance normalization and false-passes; the ≤8-call pilot (R3-R4)
    // validates the metric empirically. The clamp is deliberately tight —
    // [0.5, 2] covers tower shadows and golden hour without letting the
    // normalization neutralize arbitrary repaints.
    const scale = Math.min(2, Math.max(0.5, lumRend / Math.max(8, lumOrig)));
    const d = Math.abs(rend[i] - orig[i] * scale)
      + Math.abs(rend[i + 1] - orig[i + 1] * scale)
      + Math.abs(rend[i + 2] - orig[i + 2] * scale);
    total++;
    if (d < 90) similar++;
  }
  if (total < 50) return null; // too few visible street pixels to judge
  return similar / total;
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
  style: string,
): Promise<string> {
  const [origImg, rendImg] = await Promise.all([
    loadImage(base64ToDataUri(originalBase64)),
    loadImage(base64ToDataUri(renderedBase64)),
  ]);

  const w = origImg.naturalWidth;
  const h = origImg.naturalHeight;

  // Start with the original screenshot as the base
  const resultCanvas = document.createElement('canvas');
  resultCanvas.width = w;
  resultCanvas.height = h;
  const resultCtx = resultCanvas.getContext('2d')!;
  resultCtx.drawImage(origImg, 0, 0, w, h);

  // Build a combined feathered mask for ALL non-boundary zones.
  // TRANSPARENT background, NOT black: every downstream masking step
  // (feather clamp, render masking) uses 'destination-in', which keys on
  // SOURCE ALPHA. An opaque black fill gives alpha=1 everywhere and turns
  // each destination-in into a no-op — the post-render clip silently never
  // clipped anything (pre-existing bug found during P1).
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#ffffff';

  // Site-boundary parity WITHOUT amputation: ground-zone fills are clipped to
  // the site boundary, but building hulls are NOT — a tall tower's painted top
  // legitimately projects past the site edge, and raw boundary clipping would
  // amputate it. Net mask = (ground zones ∩ site boundary) ∪ building hulls.
  const siteBoundary = getActiveSiteBoundary(zones);
  let boundaryPath: Path2D | null = null;
  if (siteBoundary) {
    const boundaryTerrainHeight = getZoneTerrainHeight(siteBoundary, terrainHeight);
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], boundaryTerrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (boundaryPixels.length >= 3) {
      boundaryPath = new Path2D();
      boundaryPath.moveTo(boundaryPixels[0].x, boundaryPixels[0].y);
      for (let i = 1; i < boundaryPixels.length; i++) boundaryPath.lineTo(boundaryPixels[i].x, boundaryPixels[i].y);
      boundaryPath.closePath();
    }
  }

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    // Silhouette = convex hull of base + roof for buildings, base polygon otherwise.
    const silhouette = zoneSilhouette(zone, pixels, camera, canvasWidth, canvasHeight, zoneTerrainHeight);
    const isProjectedBuilding = isBuildingZone(zone) && getZoneBuildingHeight(zone) > 0;
    const clipToBoundary = boundaryPath !== null && !isProjectedBuilding;
    if (clipToBoundary) {
      maskCtx.save();
      maskCtx.clip(boundaryPath!);
    }
    maskCtx.beginPath();
    maskCtx.moveTo(silhouette[0].x, silhouette[0].y);
    for (let i = 1; i < silhouette.length; i++) maskCtx.lineTo(silhouette[i].x, silhouette[i].y);
    maskCtx.closePath();
    maskCtx.fill();
    if (clipToBoundary) maskCtx.restore();
  }

  // P1.9: erase real-road corridors (outside every building hull) from the
  // clip mask — bleed painted on a real road reverts to the original capture.
  const clipCarveStamp = buildOsmRoadCarveStamp(zones, camera, canvasWidth, canvasHeight, terrainHeight);
  if (clipCarveStamp) {
    maskCtx.save();
    maskCtx.globalCompositeOperation = 'destination-out';
    maskCtx.drawImage(clipCarveStamp, 0, 0);
    maskCtx.restore();
  }

  // Instrumentation: clip-mask coverage %. On a multi-tower plan the union of
  // hull sweeps can approach the whole frame — anything the model painted
  // inside that swath survives the clip, which is the silhouette-sweep bleed
  // hypothesis. Confirms/refutes it on the exact scene at zero render cost.
  try {
    const md = maskCtx.getImageData(0, 0, w, h).data;
    let lit = 0;
    let sampled = 0;
    for (let i = 0; i < md.length; i += 64) { // every 16th pixel
      sampled++;
      if (md[i] > 127) lit++;
    }
    const zoneCount = zones.filter(z => z.zone_type !== 'site_boundary').length;
    console.log(`[GlobeAIRender] Clip-mask coverage: ${((100 * lit) / sampled).toFixed(1)}% of frame editable (${zoneCount} zones)`);
  } catch { /* instrumentation only */ }

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
  // GPT sometimes reframes output at a different aspect ratio (ledger §4-B) —
  // a blind stretch to canvas dims produces ghosting. When the ratio is off,
  // composite aspect-preserving (cover, center-crop) instead of stretching.
  const rendAspect = rendImg.naturalWidth / rendImg.naturalHeight;
  const canvasAspect = w / h;
  if (Math.abs(rendAspect - canvasAspect) / canvasAspect > 0.02) {
    console.warn(`[GlobeAIRender] Render dims ${rendImg.naturalWidth}x${rendImg.naturalHeight} don't match canvas ${w}x${h} aspect — compositing aspect-preserving cover instead of stretch`);
    const coverScale = Math.max(w / rendImg.naturalWidth, h / rendImg.naturalHeight);
    const dw = rendImg.naturalWidth * coverScale;
    const dh = rendImg.naturalHeight * coverScale;
    aiCtx.drawImage(rendImg, (w - dw) / 2, (h - dh) / 2, dw, dh);
  } else {
    aiCtx.drawImage(rendImg, 0, 0, w, h);
  }
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);

  // Draw the masked AI render on top of the original
  resultCtx.drawImage(aiCanvas, 0, 0);

  console.log('[GlobeAIRender] Post-process: blur+clamp clip (4px inward-only feather)');

  // Post-composite color grade: unify rendered zones + tile context
  applyStyleGrade(resultCanvas, style);

  return resultCanvas.toDataURL('image/png').split(',')[1];
}

// ─── PER-ZONE RENDERING HELPERS ──────────────────────────────────────

export interface GlobeRenderProgress {
  step: number;
  total: number;
  zoneName: string;
  phase: 'ground' | 'building';
}

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
  const siteBoundary = getActiveSiteBoundary(allZones);
  if (siteBoundary) {
    const boundaryTerrainHeight = getZoneTerrainHeight(siteBoundary, terrainHeight);
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], boundaryTerrainHeight, camera, width, height))
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

  // Draw single zone as white using the true prism silhouette.
  const DILATION_PX = 4; // ~1m at typical aerial zoom (halved to reduce leak)
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';

  const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
  const pixels = zone.coordinates
    .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, width, height))
    .filter(Boolean) as { x: number; y: number }[];

  if (pixels.length >= 3) {
    const silhouette = zoneSilhouette(zone, pixels, camera, width, height, zoneTerrainHeight);
    ctx.beginPath();
    ctx.moveTo(silhouette[0].x, silhouette[0].y);
    for (let i = 1; i < silhouette.length; i++) ctx.lineTo(silhouette[i].x, silhouette[i].y);
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
/**
 * Development-mode tail: one plain sentence of archetype identity per building
 * that stands as real massing in the capture, then the preservation constraint.
 * Appended LAST in renderPreviews (after the reference-image listing) because
 * Gemini weights the tail of the prompt most heavily.
 */
function buildDevelopmentTail(zones: SiteZone[], modeledBuildingIds?: Set<string>): string {
  const placed = zones.filter(
    (z) => isBuildingZone(z) && z.building_id && modeledBuildingIds?.has(z.building_id),
  );
  if (placed.length === 0) return '';

  const lines = placed.slice(0, 12).map((zone) => {
    const info = getZoneArchetypeInfo(zone);
    const props = zone.properties || {};
    const name = info.archetypeTitle || zone.name || 'building';
    const floors = readFiniteNumber(props.floors);
    const parts = [
      `${name}${floors ? ` (${floors} floors)` : ''}`,
      info.materials || info.facadeDescription || '',
      info.roofDescription ? `roof: ${info.roofDescription}` : '',
    ].filter(Boolean);
    return `- ${parts.join(' — ').substring(0, 260)}`;
  });

  return (
    `\n\nDEVELOPMENT BUILDINGS — the textured 3D buildings standing in the screenshot, one per line:\n` +
    lines.join('\n') +
    `\n\nKeep every building exactly where it stands in the reference image; preserve massing, floor counts and roof forms.`
  );
}

function buildSingleZonePromptForPerZone(
  zone: SiteZone,
  style: string,
  _camera: THREE.Camera,
  _terrainHeight: number,
  customPrompt?: string,
  isModeled?: boolean,
): string {
  const color = colorName(resolveZoneColor(zone));
  const info = getZoneArchetypeInfo(zone);
  const overlayPrompt = getMapOverlayPrompt(zone);
  const props = zone.properties || {};
  const floors = readFiniteNumber(props.floors) ?? 0;
  const heightM = getZoneBuildingHeight(zone);
  const name = (getCustomZoneStyle(zone) ? zone.name : undefined)
    || info.archetypeTitle || zone.name || zone.zone_type;
  const footprint = formatFootprintMetrics(zone);

  let scale = '';
  if (isBuildingZone(zone)) {
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
    if (footprint) scale += `${scale ? ', ' : ''}drawn footprint ${footprint}`;
    // Add recommended footprint dimensions as a secondary archetype reference.
    if (info.suggestedWidth_m && info.suggestedDepth_m) {
      scale += `, archetype typical footprint ~${info.suggestedWidth_m}m x ${info.suggestedDepth_m}m`;
      if (info.aspectRatio) scale += ` (${info.aspectRatio} proportions)`;
    } else if (info.suggestedAreaSqm) {
      scale += `, archetype typical footprint ~${info.suggestedAreaSqm} m2`;
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
    isModeled
      ? `TASK: Refine ONE building in the white masked area. The masked area already contains a 3D massing model of the proposed building — its geometry is authoritative.`
      : `TASK: Render ONE building in the white masked area. The colored polygon [${color}] marks the exact map footprint.`,
    `BUILDING: ${name}${scale ? ` | ${scale}` : ''}`,
    footprint ? `DRAWN FOOTPRINT: ${footprint}. This measured longitude/latitude footprint is authoritative; adapt the archetype to fit it exactly.` : '',
    features.length > 0 ? `DETAILS: ${features.join(', ').substring(0, getCustomZoneStyle(zone) ? 900 : 300)}` : '',
    `CONTEXT: Preserve ALL existing photographic context outside the mask. Match lighting, color temperature, and atmosphere of surrounding real buildings.`,
    isModeled
      ? `MANDATORY: PRESERVE the 3D model's exact footprint, height, roofline and silhouette. Render realistic facades, materials, glazing and ground-level detail onto that geometry. Do NOT replace it with a different building or alter its massing.`
      : `MANDATORY: Replace the colored polygon with a photorealistic building. Render ONLY within the masked area. Match surrounding real 3D buildings, but do not enlarge the building beyond the drawn footprint.`,
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
  style: string,
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

    const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    // Silhouette = convex hull of base + roof for buildings, base polygon otherwise.
    const silhouette = zoneSilhouette(zone, pixels, camera, canvasWidth, canvasHeight, zoneTerrainHeight);
    maskCtx.beginPath();
    maskCtx.moveTo(silhouette[0].x, silhouette[0].y);
    for (let i = 1; i < silhouette.length; i++) maskCtx.lineTo(silhouette[i].x, silhouette[i].y);
    maskCtx.closePath();
    maskCtx.fill();
  }

  // Subtract building footprints from ground mask (prevents ground content
  // from painting over areas that buildings will occupy in Pass 2)
  if (subtractZones && subtractZones.length > 0) {
    maskCtx.globalCompositeOperation = 'destination-out';
    maskCtx.fillStyle = '#ffffff';
    for (const bz of subtractZones) {
      if (!bz.coordinates || bz.coordinates.length < 3) continue;
      const buildingTerrainHeight = getZoneTerrainHeight(bz, terrainHeight);
      const bPixels = bz.coordinates
        .map(c => projectToPixels(c[0], c[1], buildingTerrainHeight, camera, canvasWidth, canvasHeight))
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

  // Post-composite color grade: unify rendered zones + tile context
  applyStyleGrade(resultCanvas, style);

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
      imageQuality?: OpenAIImageQuality;
      projectId?: string;
      customPrompt?: string;
      // The site_boundary zone (callers filter it out of the render zones).
      // Used ONLY by the post-render clip for boundary parity — ground-zone
      // clip regions are intersected with it; building hulls are exempt.
      siteBoundaryZone?: SiteZone;
      // P1.10: two-pass artistic (full-frame restyle, then zone inpaint onto
      // the stylized base). 2x cost — opt-in via the panel toggle; only takes
      // effect for HIGH_FIDELITY_STYLES.
      highFidelity?: boolean;
      // Buildings whose generated GLB is placed on the globe (and therefore
      // already in the capture): their zones get preserve-the-massing prompt
      // treatment instead of replace-the-polygon.
      modeledBuildingIds?: Set<string>;
      // Internal: renderPreviews shares one pass-1 restyle across its whole
      // compare batch — the scene is static, so N variants must not pay for
      // (and composite against) N different stylized bases.
      _twoPassRestyleCache?: { promise?: Promise<string | null> };
      // Internal: skip the isRenderingRef lock so renderPreviews can fan out
      // N parallel calls. renderPreviews sets the ref itself around the batch.
      _skipLock?: boolean;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (!options._skipLock && isRenderingRef.current) return null;
    if (!options._skipLock) isRenderingRef.current = true;

    // AI-planner plan zones carry semantic hints, not archetype IDs — resolve
    // them and drop height-framework overlays (reference bands, not content).
    zones = prepareZonesForRender(zones);

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image', imageQuality = 'auto', customPrompt } = options;

      // 0. Auto-frame pilot (localStorage cc_auto_frame='1', DEV builds): fly
      // the camera so the zones fill ~55% of frame at the default oblique
      // pitch — the empirically reliable manual-zoom containment fix,
      // automated. Wired via the DEV __globeDebug handle (pilot scaffolding;
      // promote to an option prop if adopted).
      if (localStorage.getItem('cc_auto_frame') === '1') {
        const frame = (window as unknown as {
          __globeDebug?: { frameZonesForRender?: (z: SiteZone[]) => Promise<boolean> };
        }).__globeDebug?.frameZonesForRender;
        if (typeof frame === 'function') {
          try {
            const framed = await frame(zones.filter(z => z.zone_type !== 'site_boundary'));
            console.log(`[GlobeAIRender] cc_auto_frame: ${framed ? 'framed zones at ~55% of canvas' : 'skipped (no camera/coords)'}`);
          } catch (frameErr) {
            console.warn('[GlobeAIRender] cc_auto_frame failed — rendering from the current camera:', frameErr);
          }
        }
      }

      // 1. Capture the globe canvas
      console.log('[GlobeAIRender] Capturing canvas...');
      const rawBase64 = await captureCanvasBase64(canvas);
      if (!rawBase64) throw new Error('Failed to capture canvas');

      // 1y. Clean-composite pilot (localStorage cc_clean_composite='1', default
      // OFF): capture a second frame with zone overlays hidden. Used ONLY as
      // the composite-back base in clipRenderToZones, so the feathered seam
      // ring blends against real tiles instead of the in-scene grey zone fill.
      // The model still receives the overlaid + labeled screenshot.
      let cleanBase64: string | null = null;
      if (localStorage.getItem('cc_clean_composite') === '1') {
        try {
          window.dispatchEvent(new CustomEvent('cityprompt:hide-zone-overlays', { detail: { hidden: true } }));
          await new Promise<void>(r => requestAnimationFrame(() => requestAnimationFrame(() => r())));
          cleanBase64 = await captureCanvasBase64(canvas);
          (window as any).__renderDebug = {
            ...(window as any).__renderDebug,
            cleanCapture: cleanBase64 ? base64ToDataUri(cleanBase64) : null,
            rawCapture: base64ToDataUri(rawBase64),
          };
          console.log('[GlobeAIRender] cc_clean_composite: captured overlay-free base');
        } finally {
          window.dispatchEvent(new CustomEvent('cityprompt:hide-zone-overlays', { detail: { hidden: false } }));
          await new Promise<void>(r => requestAnimationFrame(() => r()));
        }
      }

      // 1x. P1.10 — high-fidelity two-pass (opt-in, 2x cost): full-frame
      // restyle of the UNLABELED capture first; the normal zone inpaint then
      // runs against the stylized base, so the hard clip composites with no
      // style seam. Restyle always runs on Gemini (ledger #34: never coerce
      // GPT to stylize). Any failure falls back to single-pass.
      let baseBase64 = rawBase64;
      const twoPass = Boolean(options.highFidelity) && HIGH_FIDELITY_STYLES.has(style);
      if (twoPass) {
        const runRestyle = async (): Promise<string | null> => {
          console.log('[GlobeAIRender] High-fidelity two-pass: full-frame restyle first');
          const restyleResp = await api.post(
            '/api/v1/render/generate',
            {
              image_base64: rawBase64,
              prompt:
                `STYLE: ${GLOBE_STYLE_PROMPTS[style]}\n` +
                `TASK: Re-render this exact scene entirely in the declared STYLE. ` +
                `Preserve the scene's geometry, layout and composition exactly — every ` +
                `building, road, and landscape element stays where it is; only the ` +
                `artistic medium changes.`,
              negative_prompt: 'low quality, blurry, text, watermark',
              model: 'gemini-3.1-flash-image',
              image_quality: imageQuality,
              project_id: options.projectId,
              image_size: '2K',
              thinking_budget: 0,
            },
            { timeout: 300000 },
          );
          if (!restyleResp.data?.image_base64) return null;
          // Normalize the restyle back to the CAPTURE's dimensions — every
          // downstream consumer (labels, payload mask, clip geometry, carve
          // stamp) projects in canvas-buffer coordinates; a 2K restyle at
          // different dims would silently misalign all of them.
          const rawImg = await loadImage(base64ToDataUri(rawBase64));
          const styImg = await loadImage(base64ToDataUri(restyleResp.data.image_base64));
          const norm = document.createElement('canvas');
          norm.width = rawImg.naturalWidth;
          norm.height = rawImg.naturalHeight;
          const normCtx = norm.getContext('2d')!;
          const styAspect = styImg.naturalWidth / styImg.naturalHeight;
          const targetAspect = norm.width / norm.height;
          if (Math.abs(styAspect - targetAspect) / targetAspect > 0.02) {
            const coverScale = Math.max(norm.width / styImg.naturalWidth, norm.height / styImg.naturalHeight);
            const dw = styImg.naturalWidth * coverScale;
            const dh = styImg.naturalHeight * coverScale;
            normCtx.drawImage(styImg, (norm.width - dw) / 2, (norm.height - dh) / 2, dw, dh);
          } else {
            normCtx.drawImage(styImg, 0, 0, norm.width, norm.height);
          }
          return norm.toDataURL('image/jpeg', 0.9).split(',')[1];
        };
        try {
          // renderPreviews shares one restyle across its compare batch — the
          // captures are of the same static scene, so the first caller's
          // stylized base serves every variant.
          const cache = options._twoPassRestyleCache;
          let restyled: string | null;
          if (cache) {
            cache.promise ??= runRestyle();
            restyled = await cache.promise;
          } else {
            restyled = await runRestyle();
          }
          if (restyled) {
            baseBase64 = restyled;
          } else {
            console.warn('[GlobeAIRender] Two-pass restyle returned no image — continuing single-pass');
          }
        } catch (restyleErr) {
          console.warn('[GlobeAIRender] Two-pass restyle failed — continuing single-pass:', restyleErr);
        }
      }

      // Two-pass forces Gemini end-to-end: pass 2 is still a stylization onto
      // an artistic base, and GPT won't stylize (ledger #34) — a GPT pass 2
      // would reintroduce the exact seam the toggle exists to remove.
      const effectiveModel = twoPass && baseBase64 !== rawBase64
        ? 'gemini-3.1-flash-image'
        : model;

      const frameZones = selectZonesInRenderFrame(
        zones,
        camera,
        canvas.width,
        canvas.height,
        terrainHeight,
      );
      console.log(
        `[GlobeAIRender] Frame visibility: ${frameZones.length}/${zones.length} zones can contribute pixels`,
      );

      // 1a. Add text labels to screenshot so the image model can read zone names
      const imageBase64 = await (async () => {
        const img = await loadImage(base64ToDataUri(baseBase64));
        const labelCanvas = document.createElement('canvas');
        labelCanvas.width = img.naturalWidth;
        labelCanvas.height = img.naturalHeight;
        const ctx = labelCanvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0);

        const editableZones = frameZones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);
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

          const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
          const pixels = zone.coordinates
            .map(c => projectToPixels(c[0], c[1], zoneTerrainHeight, camera, canvas.width, canvas.height))
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

        const labelEntries = editableZones.map((zone, index) => {
          const props = zone.properties || {};
          const info = getZoneArchetypeInfo(zone);
          const communityKind = resolveCommunity3DKind(zone);
          const parkProfile = communityKind === 'park' ? resolveParkGroundProfile(zone) : null;
          const streetProfile = communityKind === 'street' ? resolvePilotStreetSectionProfile(zone) : null;
          const name = (getCustomZoneStyle(zone) ? zone.name : undefined)
            || info.archetypeTitle
            || zone.name
            || ZONE_TYPE_CONFIG[zone.zone_type]?.label
            || zone.zone_type;
          const groupKind = communityKind ?? (isBuildingZone(zone) ? 'building' : 'zone');
          const groupKey = [
            groupKind,
            name,
            parkProfile?.id ?? '',
            streetProfile?.archetypeId ?? '',
            String(props._plan_role ?? ''),
            String(props.typology ?? ''),
          ].join('|');
          const priority = (props.context_connection === true ? 1_000_000_000 : 0)
            + (communityKind === 'park' || communityKind === 'street' ? 10_000_000 : 0)
            + (getCustomZoneStyle(zone) ? 1_000_000 : 0)
            + (zone.building_id && options.modeledBuildingIds?.has(zone.building_id) ? 100_000 : 0);
          return {
            zone,
            candidate: {
              id: zone.id || `render-zone-${index}`,
              groupKey,
              priority,
              area: Math.max(0, zoneAreaM2(zone)),
            },
          };
        });
        const selectedLabelIds = selectRenderLabelIds(
          labelEntries.map(entry => entry.candidate),
          MAX_DISTRICT_RENDER_LABELS,
        );
        const labelZones = labelEntries
          .filter(entry => selectedLabelIds.has(entry.candidate.id))
          .map(entry => entry.zone);

        // Draw representative text labels at zone centroids. All polygons still
        // retain their border and mask; only the text is budgeted.
        ctx.font = 'bold 28px Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let zi = 0; zi < labelZones.length; zi++) {
          const zone = labelZones[zi];
          const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
          const centroid = zone.coordinates.reduce(
            (acc, c) => [acc[0] + c[0] / zone.coordinates.length, acc[1] + c[1] / zone.coordinates.length],
            [0, 0],
          );
          const screenPos = projectToPixels(centroid[0], centroid[1], zoneTerrainHeight, camera, canvas.width, canvas.height);
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
        console.log(
          `[GlobeAIRender] Added ${labelZones.length}/${editableZones.length} text labels + ${editableZones.length} colored borders to screenshot`,
        );
        return labelCanvas.toDataURL('image/jpeg', 0.85).split(',')[1];
      })();

      // 1b. Occlusion culling — remove zones hidden behind taller buildings
      const occludedIds = findOccludedZones(frameZones, camera, canvas.width, canvas.height, terrainHeight);
      const visibleZones = occludedIds.size > 0
        ? frameZones.filter(z => !occludedIds.has(z.id || ''))
        : frameZones;

      // 2. Generate binary mask from VISIBLE zone polygons only
      console.log('[GlobeAIRender] Generating mask...');
      // GPT is pinned to its pre-session payload mask (no OSM road carve) —
      // Gemini keeps the P1 carve.
      const maskBase64 = generateMask(
        visibleZones, camera, canvas.width, canvas.height, terrainHeight,
        !effectiveModel.startsWith('gpt-image-2'),
      );

      // 3. Build SCHEMA prompt from VISIBLE zone archetypes only
      let prompt = buildPrompt(visibleZones, style, camera, terrainHeight, options.modeledBuildingIds);
      if (customPrompt) prompt += `\nADDITIONAL: ${customPrompt}`;
      if (twoPass && baseBase64 !== rawBase64) {
        // Pass 1 restyles the zone FILL colors away (monochrome media destroy
        // them entirely) — identification must key on what survives: the
        // dashed borders + text labels are drawn AFTER the restyle.
        prompt += (
          `\nTWO-PASS NOTE: the input image is ALREADY rendered in the declared STYLE — ` +
          `match its medium seamlessly and edit ONLY the masked zones. The original zone ` +
          `FILL colors may have been restyled away: identify each zone by its DASHED ` +
          `BORDER color and TEXT LABEL (drawn after the restyle) and by the mask.`
        );
      }

      // 4. Collect archetype reference card images (multi-view: 0° street-level +
      //    up to 2 aerial angles per zone — 45°/90° where available).
      //    Each image is compressed to 512px JPEG @ 0.7 (~30-50KB). Cap 48.
      console.log('[GlobeAIRender] Collecting archetype reference images...');
      let archetypeImages = await collectArchetypeImages(visibleZones);
      // Development A/B lever: cc_development_refs='0' drops the archetype
      // card refs so the textured massing in the capture is the only identity
      // signal. Plan-diagram conditioning (attached below) stays in both arms.
      if (style === 'development' && localStorage.getItem('cc_development_refs') === '0') {
        console.log(`[GlobeAIRender] development refs OFF (A/B): dropped ${archetypeImages.length} archetype refs`);
        archetypeImages = [];
      }

      // 4a. Plan-diagram conditioning: attach the drawn plan as an
      // authoritative nadir layout reference in the first slot (slot priority
      // matters for GPT Image 2's 16-image input cap). Default ON — the
      // 2026-07-07 A/B (docs/PLAN_DIAGRAM_CONDITIONING_PILOT_2026_07_07.md)
      // showed clearly better street/block/park adherence on BOTH engines.
      // Only activates when the view contains a drawn plan (≥4 plan zones);
      // set localStorage cc_plan_diagram_conditioning = '0' to disable.
      let planDiagramAttached = false;
      if (localStorage.getItem('cc_plan_diagram_conditioning') !== '0') {
        const planDiagram = buildPlanConditioningDiagram(visibleZones);
        if (planDiagram) {
          archetypeImages.unshift({
            image_base64: planDiagram,
            label: 'PLAN DIAGRAM — authoritative nadir layout of the proposal: '
              + 'gray = streets, green = parks and courtyards, dark red = building '
              + 'footprints. Each building footprint is outlined in white — '
              + 'adjoining outlined shapes are SEPARATE buildings forming a '
              + 'continuous block edge, not one mass and not freestanding slabs. '
              + 'Preserve the street network topology, block arrangement, park '
              + 'locations and building footprints exactly as drawn. Streets '
              + 'remain open to the sky.',
            zone_color: 'plan layout',
            angle: '90° nadir plan diagram',
          });
          planDiagramAttached = true;
          console.log('[GlobeAIRender] Plan-diagram conditioning attached (slot 1)');
        }
      }

      // 4b. Geometry-critical park diagrams sit immediately after the whole-
      // plan diagram and before visual-style cards. The bounded selector keeps
      // large master plans within a useful reference budget; no API call is
      // made to construct these local canvas diagrams.
      const parkGeometryImages = localStorage.getItem('cc_park_geometry_conditioning') === '0'
        ? []
        : collectParkGeometryImages(visibleZones);
      if (parkGeometryImages.length > 0) {
        archetypeImages.splice(planDiagramAttached ? 1 : 0, 0, ...parkGeometryImages);
        console.log(
          `[GlobeAIRender] Attached ${parkGeometryImages.length} authoritative park geometry diagram(s) `
          + `(afterPlan=${planDiagramAttached})`,
        );
      }

      // GPT Image 2 accepts at most 16 input images — we used to attach up to
      // 48, so "Image N" prompt labels could reference images GPT never saw
      // (silently breaking the slot-1 plan-diagram contract). Clamp BEFORE the
      // label loop below so numbering matches what the model receives; the
      // plan diagram stays in slot 1. Gemini keeps the full set.
      // 15, not 16: the backend counts the source screenshot against the cap
      // (render.py: max_refs = 16 - 1 - previous - context = 15 on this path)
      // and silently slices archetype_images[:15].
      const GPT_MAX_REFS = 15;
      if (effectiveModel.startsWith('gpt-image-2') && archetypeImages.length > GPT_MAX_REFS) {
        const dropped = archetypeImages.length - GPT_MAX_REFS;
        archetypeImages.splice(GPT_MAX_REFS);
        console.warn(`[GlobeAIRender] GPT ref cap: kept first ${GPT_MAX_REFS} reference images (plan diagram in slot 1), dropped ${dropped}`);
      }

      if (archetypeImages.length > 0) {
        prompt += (
          `\n\nRENDER REFERENCE IMAGES (Images 2+): ${archetypeImages.length} ` +
          `images provide authoritative geometry and/or visual identity for the drawn zones. Each image is ` +
          `labeled with its VIEWING ANGLE so you can match your output angle to ` +
          `the right reference:\n` +
          `  • "90° north-up park geometry diagram" — a schematic, to-scale ` +
          `internal park plan. Its paths, gateways, water/field footprints, fixed ` +
          `pads and structure alignments are authoritative; preserve their geometry ` +
          `but replace diagram colors with the finished materials visible in the ` +
          `source scene and style references.\n` +
          `  • "0° eye-level / street view" — ground-level photograph at ~0° ` +
          `elevation (90° from nadir): camera looks at the horizon, NOT downward. ` +
          `Shows facade detail, materials, ornament, colors, ground-level character.\n` +
          `  • "45° oblique aerial" — drone at ~45° elevation (45° from nadir); ` +
          `shows rooftop + upper facades from a corner, triangulates 3D form.\n` +
          `  • "90° nadir / top-down aerial" — drone at 90° elevation (0° from ` +
          `nadir) looking straight down; shows rooftop plan, site layout, roof materials.\n` +
          `HOW TO USE: park geometry diagrams control topology at every camera ` +
          `angle. Style reference images supply appearance only and never ` +
          `authorize a new fountain, pond, path, building, court, bed, axis or ` +
          `feature absent from the geometry diagram and its program locks. If a ` +
          `style reference conflicts with the diagram, follow the diagram. For ` +
          `visual appearance at an oblique angle, weight ` +
          `the 45° aerial and street-level refs most heavily. When rendering top-` +
          `down or near-nadir, weight the 90° nadir ref most heavily. Use ALL ` +
          `available refs per zone to build a complete 3D understanding of its ` +
          `materials, form, and site layout before rendering. Each zone-specific ref is ` +
          `tagged with the zone's fill color in [brackets] to identify which ` +
          `polygon it belongs to.`
        );
        for (let i = 0; i < archetypeImages.length; i++) {
          prompt += `\nImage ${i + 2}: [${archetypeImages[i].zone_color}] ${archetypeImages[i].label}`;
        }
      }

      // Affirmative streets clause — placed last because Gemini weights later
      // instructions more heavily. Budget-neutral: paid for by merging the
      // redundant FOOTPRINT + FINAL constraints in buildPrompt (ledger: ≤8
      // constraints; adding a clause must displace one).
      // GPT-exempt: this is a P1 session prompt addition, and the GPT path is
      // pinned to its pre-session prompt ("great before" per the user).
      if (planDiagramAttached && !effectiveModel.startsWith('gpt-image-2')) {
        prompt += (
          `\n\nSTREETS: the gray corridors in the PLAN DIAGRAM reference (Image 2) are streets — ` +
          `render them as open paved right-of-way, continuous and unobstructed curb to curb; ` +
          `buildings and landscaping meet the curb line and stop.`
        );
      }

      if (visibleZones.some(
        (zone) => (zone.properties as Record<string, unknown> | undefined)?.context_connection === true,
      )) {
        prompt += (
          `\n\nCONTEXT CONNECTIONS: proposed streets and paths marked as boundary connections ` +
          `must cross the site edge continuously into the matching existing corridor. Align the ` +
          `centerline, grade, curb/path edges and usable travel surface across the seam; do not ` +
          `block or terminate a connection with a curb, lawn, building, tree or planting bed.`
        );
      }

      // Development mode: per-building identity + the preservation constraint
      // land at the very end of the prompt, where Gemini weighs hardest.
      if (style === 'development') {
        prompt += buildDevelopmentTail(visibleZones, options.modeledBuildingIds);
      }

      console.log(`[GlobeAIRender] Prompt (${prompt.length} chars, ${zones.filter(z => z.zone_type !== 'site_boundary').length} zones, ${archetypeImages.length} ref images):`, prompt.substring(0, 200) + '...');

      // 5. Send to backend render API with archetype images
      console.log('[GlobeAIRender] Sending to render backend...');
      const requestBody = {
        image_base64: imageBase64,
        mask_base64: maskBase64,
        prompt,
        // Artistic styles must not be told to avoid 'cartoon, illustration,
        // sketch, unrealistic colors' — that directly contradicts their
        // STYLE instruction and pushes seeds back toward photorealism.
        negative_prompt: ARTISTIC_STYLES.has(style)
          ? 'low quality, blurry, text, watermark'
          : 'cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors',
        model: effectiveModel,
        image_quality: imageQuality,
        project_id: options.projectId,
        aspect_ratio: nearestAspectRatio(canvas.width, canvas.height),
        image_size: '2K', // 2K output for architectural detail accuracy
        thinking_budget: 0, // Disable thinking — no benefit for image generation, saves ~30-50% latency
        archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
      };
      let resp = await api.post('/api/v1/render/generate', requestBody, { timeout: 300000 });

      // P1.8 — verification gate + ONE auto re-roll (standing permission),
      // photoreal/photomontage only: when plan streets no longer read as the
      // original street surface, re-roll once and keep the better score.
      // Kill switch: localStorage cc_render_verification_gate = '0'.
      // GPT is exempt: its output is reframed (ledger §4-B), so a pixel-wise
      // comparison against the raw capture false-fails and burns a paid
      // re-roll that would be just as misaligned.
      if (
        VERIFICATION_GATE_STYLES.has(style)
        && !effectiveModel.startsWith('gpt-image-2')
        && localStorage.getItem('cc_render_verification_gate') !== '0'
        && resp.data?.image_base64
      ) {
        const score = await scorePlanStreetSimilarity(
          rawBase64, resp.data.image_base64,
          visibleZones, camera, canvas.width, canvas.height, terrainHeight,
        );
        if (score !== null) {
          console.log(`[GlobeAIRender] Street-similarity gate: ${(score * 100).toFixed(0)}% (threshold 70%)`);
          if (score < 0.7) {
            console.warn('[GlobeAIRender] Below threshold — re-rolling once, keeping the better score');
            try {
              const retry = await api.post('/api/v1/render/generate', requestBody, { timeout: 300000 });
              if (retry.data?.image_base64) {
                const retryScore = await scorePlanStreetSimilarity(
                  rawBase64, retry.data.image_base64,
                  visibleZones, camera, canvas.width, canvas.height, terrainHeight,
                );
                console.log(`[GlobeAIRender] Re-roll street-similarity: ${retryScore === null ? 'n/a' : `${(retryScore * 100).toFixed(0)}%`}`);
                if (retryScore !== null && retryScore > score) resp = retry;
              }
            } catch (retryErr) {
              console.warn('[GlobeAIRender] Re-roll failed — keeping the first render:', retryErr);
            }
          }
        }
      }

      if (resp.data?.image_base64) {
        // Style contract split: re-projecting styles (isometric, orthographic
        // plan, near-nadir drone) command a camera change, so output pixels no
        // longer align with the input screenshot — screen-space clipping is
        // geometrically incoherent for them. Return the full-frame
        // reinterpretation; boundary fidelity comes from the plan diagram.
        // GPT Image 2 gets the same treatment for EVERY style: it reframes
        // its output (ledger §4-B), so clipping its pixels into the zone
        // polygons composites a misaligned patch over the raw capture —
        // full-frame is how GPT renders always shipped before the clip
        // started engaging.
        const fullFrame = REPROJECTING_STYLES.has(style) || effectiveModel.startsWith('gpt-image-2');
        if (fullFrame) {
          console.log(`[GlobeAIRender] Full-frame output (${REPROJECTING_STYLES.has(style) ? `style "${style}" re-projects the camera` : 'GPT reframes — screen-space clip incoherent'}) — polygon clip skipped`);
          // The style grade normally runs inside clipRenderToZones — apply it
          // to the full frame here so graded styles (site-plan-photo) don't
          // silently lose it. Ungraded artistic styles pass through as-is.
          let imageUrl = base64ToDataUri(resp.data.image_base64);
          if (STYLE_GRADES[style]) {
            const fullImg = await loadImage(imageUrl);
            const gradeCanvas = document.createElement('canvas');
            gradeCanvas.width = fullImg.naturalWidth;
            gradeCanvas.height = fullImg.naturalHeight;
            gradeCanvas.getContext('2d')!.drawImage(fullImg, 0, 0);
            applyStyleGrade(gradeCanvas, style);
            imageUrl = gradeCanvas.toDataURL('image/png');
          }
          return {
            imageUrl,
            prompt,
            seed: resp.data.seed,
            model: effectiveModel,
            imageQuality,
          };
        }

        console.log('[GlobeAIRender] Render complete! Applying polygon clip...');

        // Post-process: clip the AI render to zone polygons with feathered
        // edges so no zone bleeds into adjacent zones or outside boundaries.
        // The clip base is the RAW capture — clipping against the labeled
        // screenshot burned the dashed borders + text labels into every final
        // composite (the label-leak bug). Callers filter site_boundary out of
        // the render zones, so it is threaded back in via options for the
        // boundary-parity clip.
        const clipZones = options.siteBoundaryZone
          ? [...visibleZones, options.siteBoundaryZone]
          : visibleZones;
        // Two-pass: composite onto the STYLIZED base so there is no style
        // seam at the clip boundary; single-pass: the clean overlay-free
        // capture when the cc_clean_composite pilot is on, else the raw
        // capture.
        const compositeBase = baseBase64 === rawBase64
          ? (cleanBase64 ?? rawBase64)
          : baseBase64;
        const clippedBase64 = await clipRenderToZones(
          compositeBase, resp.data.image_base64,
          clipZones, camera, canvas.width, canvas.height, terrainHeight,
          style,
        );

        return {
          imageUrl: `data:image/png;base64,${clippedBase64}`,
          prompt,
          seed: resp.data.seed,
          model: effectiveModel,
          imageQuality,
        };
      }

      console.warn('[GlobeAIRender] No image in response');
      return null;

    } catch (err) {
      const message = getRenderErrorMessage(err);
      console.error('[GlobeAIRender] Error:', message, err);
      if (options._skipLock) {
        throw new Error(message);
      }
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
      imageQuality?: OpenAIImageQuality;
      projectId?: string;
      customPrompt?: string;
      siteBoundaryZone?: SiteZone;
      highFidelity?: boolean;
      modeledBuildingIds?: Set<string>;
      count?: number;
      variants?: GlobeRenderVariant[];
    } = {},
  ): Promise<GlobeRenderResult[]> => {
    if (isRenderingRef.current) return [];
    isRenderingRef.current = true;
    const count = options.count ?? 3;
    const previewVariants = options.variants ?? Array.from({ length: count }, (_, index) => ({
      model: options.model ?? 'gemini-3.1-flash-image',
      label: `Preview ${index + 1}`,
      imageQuality: options.imageQuality,
    }));
    const renderOptions = {
      style: options.style,
      projectId: options.projectId,
      customPrompt: options.customPrompt,
      siteBoundaryZone: options.siteBoundaryZone,
      highFidelity: options.highFidelity,
      modeledBuildingIds: options.modeledBuildingIds,
      // One pass-1 restyle for the whole compare batch (see render()).
      _twoPassRestyleCache: {},
    };
    try {
      console.log(`[GlobeAIRender] Generating ${previewVariants.length} previews in parallel...`);
      const promises: Promise<GlobeRenderResult | null>[] = previewVariants.map((variant) =>
        render(canvas, camera, zones, terrainHeight, {
          ...renderOptions,
          model: variant.model,
          imageQuality: variant.imageQuality,
          _skipLock: true,
        })
          .then((renderResult) => renderResult
            // render() reports the ENGINE THAT ACTUALLY RAN (two-pass forces
            // Gemini) — keep it over the variant's requested model.
            ? { ...renderResult, model: renderResult.model || variant.model, imageQuality: variant.imageQuality, providerLabel: variant.label }
            : null)
          .catch((err) => {
            const message = getRenderErrorMessage(err);
            console.warn(`[GlobeAIRender:Preview] ${variant.label} failed:`, message, err);
            return {
              imageUrl: createErrorPreviewImage(variant.label, message),
              prompt: '',
              model: variant.model,
              imageQuality: variant.imageQuality,
              providerLabel: variant.label,
              error: message,
            };
          }),
      );
      const settled = await Promise.all(promises);
      const previews = settled.filter((r): r is GlobeRenderResult => r !== null);
      const successfulCount = previews.filter((preview) => !preview.error).length;
      console.log(`[GlobeAIRender] Previews complete: ${successfulCount}/${previewVariants.length} succeeded`);
      return previews;
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
    waitForTiles?: () => Promise<boolean>,
    captureFrame?: () => Promise<string | null>,
  ): Promise<string | null> => {
    // Save current camera state
    const savedState = saveCameraState(camera);
    if (!savedState) return null;

    // Pin the lens to the street-view contract (70° FOV) so the capture
    // matches the prompt's view-cone zone analysis, then restore.
    const perspective = (camera as THREE.PerspectiveCamera).isPerspectiveCamera
      ? (camera as THREE.PerspectiveCamera)
      : null;
    const savedFov = perspective?.fov;

    try {
      if (perspective) {
        perspective.fov = 70;
        perspective.updateProjectionMatrix();
      }

      // Move camera to street level
      flyToStreetLevel(lat, lng, headingDeg, terrainHeight, camera);

      // Wait for tiles to load at street-level LOD
      // Phase 1: Let renderer process new camera position
      for (let i = 0; i < 10; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Phase 2: Wait for tile streaming. Prefer the tiles renderer's own
      // settle signal (fast + accurate); fall back to a fixed 8s poll.
      console.log('[GlobeAIRender] Waiting for street-level tiles to load...');
      let settled = false;
      if (waitForTiles) {
        try {
          settled = await waitForTiles();
        } catch {
          settled = false;
        }
      }
      if (!settled) {
        for (let attempt = 0; attempt < 16; attempt++) {
          await new Promise(r => setTimeout(r, 500));
          // Render a frame to trigger tile updates
          await new Promise(r => requestAnimationFrame(r));
        }
      }

      // Phase 3: Final frames for render completion
      for (let i = 0; i < 5; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Capture the street-level view. A caller-provided frame capture (e.g.
      // the Direct 3D off-screen pass stack) runs while the camera is still
      // parked at street level; a null result falls back to the screenshot.
      console.log('[GlobeAIRender] Capturing street-level view...');
      let imageBase64: string | null = null;
      if (captureFrame) {
        try {
          imageBase64 = await captureFrame();
        } catch (err) {
          console.warn('[GlobeAIRender] Street frame capture override failed, using screenshot:', err);
        }
      }
      if (!imageBase64) {
        imageBase64 = await captureCanvasBase64(canvas);
      }

      return imageBase64 || null;
    } finally {
      if (perspective && savedFov !== undefined) {
        perspective.fov = savedFov;
        perspective.updateProjectionMatrix();
      }
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
      imageQuality?: OpenAIImageQuality;
      projectId?: string;
      customPrompt?: string;
      modeledBuildingIds?: Set<string>;
      onProgress?: (progress: GlobeRenderProgress) => void;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (isRenderingRef.current) return null;
    isRenderingRef.current = true;

    zones = prepareZonesForRender(zones);

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image', imageQuality = 'auto', customPrompt, onProgress } = options;

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
      const editableZones = visibleZones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);
      const groundZones = editableZones.filter(z => GROUND_ZONE_TYPES.has(z.zone_type));
      const buildingZones = editableZones
        .filter(isBuildingZone)
        .sort((a, b) => zoneAreaM2(b) - zoneAreaM2(a));

      // ALL zones rendered individually — ground first (largest area first), then buildings
      const allRenderZones = [...groundZones, ...buildingZones];
      const totalSteps = allRenderZones.length;
      let currentStep = 0;
      const allPrompts: string[] = [];

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
          const zoneTerrainHeight = getZoneTerrainHeight(zone, terrainHeight);
          const centroid = zone.coordinates.reduce(
            (acc, c) => [acc[0] + c[0] / zone.coordinates.length, acc[1] + c[1] / zone.coordinates.length],
            [0, 0],
          );
          const screenPos = projectToPixels(centroid[0], centroid[1], zoneTerrainHeight, camera, canvas.width, canvas.height);
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
        const isBuilding = isBuildingZone(zone);
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
          const isModeled = Boolean(
            zone.building_id && options.modeledBuildingIds?.has(zone.building_id),
          );
          singlePrompt = buildSingleZonePromptForPerZone(
            zone, style, camera, terrainHeight, customPrompt, isModeled,
          );
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
          const footprint = formatFootprintMetrics(zone);
          if (info.suggestedWidth_m && info.suggestedDepth_m) {
            dimHint = `, archetype typical dimensions ~${info.suggestedWidth_m}m x ${info.suggestedDepth_m}m`;
          }

          singlePrompt = [
            `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`,
            `TASK: Render ONE ground zone in the white masked area. The colored polygon [${color}] marks the exact map footprint.`,
            `ZONE: ${info.archetypeTitle || zoneName}${footprint ? `, drawn footprint ${footprint}` : ''}${dimHint}`,
            features.length > 0 ? `DETAILS: ${features.join(', ').substring(0, 400)}` : '',
            buildPublicRealmContextPrompt(zone, visibleZones, {
              sceneReferenceAttached: true,
              compact: true,
            }),
            `CONTEXT: Preserve ALL existing photographic context outside the mask. Match lighting and atmosphere.`,
            `MANDATORY: Replace the colored polygon with photorealistic ground materials. Render ONLY within the masked area; the drawn footprint is authoritative.`,
            customPrompt ? `ADDITIONAL: ${customPrompt}` : '',
          ].filter(Boolean).join('\n');
        }
        allPrompts.push(singlePrompt);

        // Variant-aware style refs plus an authoritative internal park diagram
        // when this one-zone pass targets a programmed park.
        const archetypeImages = await collectArchetypeImages([zone]);
        const parkGeometryImages = collectParkGeometryImages([zone]);
        const renderReferenceImages = [...parkGeometryImages, ...archetypeImages];
        let prompt = singlePrompt;
        if (parkGeometryImages.length > 0) {
          prompt += (
            `\n\nPARK GEOMETRY REFERENCE: Image 2 is the authoritative north-up internal `
            + `layout. Preserve every path, gateway, water/field footprint, fixed pad and `
            + `structure alignment while replacing schematic colors with the requested finish. `
            + (archetypeImages.length > 0
              ? 'Images 3+ are appearance references only; they must not override Image 2 geometry.'
              : '')
          );
        } else if (archetypeImages.length > 0) {
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
              image_quality: imageQuality,
              project_id: options.projectId,
              image_size: '2K',
              thinking_budget: 0,
              archetype_images: renderReferenceImages.length > 0 ? renderReferenceImages : undefined,
            },
            { timeout: 300000 },
          );

          if (resp.data?.image_base64) {
            // Composite this zone, subtracting building footprints for ground zones
            cumulativeBase64 = await compositeZoneRenderForPerZone(
              cumulativeBase64, resp.data.image_base64,
              [zone], camera, canvas.width, canvas.height, terrainHeight,
              style,
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
        model,
        imageQuality,
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
