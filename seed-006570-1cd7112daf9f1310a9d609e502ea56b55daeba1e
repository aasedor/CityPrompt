/**
 * overlayArchitecturalFigures — Post-processing step that composites
 * minimalist architectural scale figures onto rendered site images.
 *
 * These are simple line-drawn silhouettes (like architectural entourage)
 * placed on walkable surfaces: parks, plazas, sidewalks, paths.
 */

import type { SiteZone } from '@/types';
import type { Map as MapboxMap } from 'mapbox-gl';

// ---------------------------------------------------------------------------
// SVG Figure Library — minimalist architectural silhouettes
// ---------------------------------------------------------------------------

/** Each figure is an SVG path at a normalized 40×80 viewBox (width×height) */
const FIGURE_PATHS = [
  // Standing person, relaxed
  'M20,8 a6,6 0 1,0 0.01,0 M20,14 L20,48 M8,28 L20,22 L32,28 M20,48 L10,76 M20,48 L30,76',
  // Walking person, arms swinging
  'M20,8 a6,6 0 1,0 0.01,0 M20,14 L20,48 M8,32 L20,22 L32,24 M20,48 L12,76 M20,48 L28,76',
  // Person with bag
  'M20,8 a6,6 0 1,0 0.01,0 M20,14 L20,48 M8,28 L20,22 L32,28 L34,40 L28,40 M20,48 L10,76 M20,48 L30,76',
  // Couple standing close
  'M15,8 a5,5 0 1,0 0.01,0 M15,13 L15,44 M6,26 L15,20 L24,26 M15,44 L8,72 M15,44 L22,72 M28,8 a5,5 0 1,0 0.01,0 M28,13 L28,44 M20,26 L28,20 L36,26 M28,44 L22,72 M28,44 L34,72',
  // Person walking dog (simplified)
  'M20,8 a6,6 0 1,0 0.01,0 M20,14 L20,48 M8,30 L20,22 L32,28 M20,48 L12,76 M20,48 L28,76 M32,28 L38,36 M38,36 L38,42 M34,42 L42,42 M38,36 L42,36',
  // Child figure (shorter)
  'M20,10 a5,5 0 1,0 0.01,0 M20,15 L20,44 M10,28 L20,22 L30,28 M20,44 L12,64 M20,44 L28,64',
  // Person on phone
  'M20,8 a6,6 0 1,0 0.01,0 M20,14 L20,48 M10,32 L20,22 L28,14 M20,48 L10,76 M20,48 L30,76',
  // Jogger
  'M22,8 a6,6 0 1,0 0.01,0 M22,14 L20,48 M10,24 L20,20 L34,30 M20,48 L8,72 M20,48 L34,72',
];

// ---------------------------------------------------------------------------
// Placement logic
// ---------------------------------------------------------------------------

interface FigurePlacement {
  x: number;  // canvas pixel x
  y: number;  // canvas pixel y
  scale: number;
  opacity: number;
  figureIndex: number;
}

/**
 * Determine where to place figures based on zone polygons.
 * Only places figures in "walkable" zones: parks, plazas, paths, green_space.
 */
function computeFigurePlacements(
  zones: SiteZone[],
  map: MapboxMap,
  canvasWidth: number,
  canvasHeight: number,
  dpr: number,
): FigurePlacement[] {
  const WALKABLE_TYPES = ['park', 'green_space', 'plaza', 'path', 'street', 'road'];
  const walkableZones = zones.filter(
    (z) => WALKABLE_TYPES.includes(z.zone_type) && z.coordinates?.length >= 3
  );

  if (walkableZones.length === 0) return [];

  const placements: FigurePlacement[] = [];
  const rng = seedRandom(42); // deterministic placement

  for (const zone of walkableZones) {
    const coords = zone.coordinates as number[][];
    if (!coords || coords.length < 3) continue;

    // Get bounding box of polygon in pixel space
    const pixelCoords = coords.map((c) => {
      const pt = map.project({ lng: c[0], lat: c[1] });
      return { x: pt.x * dpr, y: pt.y * dpr };
    });

    const minX = Math.min(...pixelCoords.map((p) => p.x));
    const maxX = Math.max(...pixelCoords.map((p) => p.x));
    const minY = Math.min(...pixelCoords.map((p) => p.y));
    const maxY = Math.max(...pixelCoords.map((p) => p.y));

    const polyWidth = maxX - minX;
    const polyHeight = maxY - minY;
    const polyArea = polyWidth * polyHeight;

    // Scale figures based on zone area — larger zones get more figures
    const figureCount = Math.min(12, Math.max(2, Math.floor(polyArea / 8000)));

    // Figure size based on zoom level / pixels-per-meter
    const figureHeight = Math.max(8, Math.min(24, polyHeight * 0.06));

    for (let i = 0; i < figureCount; i++) {
      // Random point within bounding box, biased toward center
      const attempts = 10;
      for (let a = 0; a < attempts; a++) {
        const x = minX + rng() * (maxX - minX);
        const y = minY + rng() * (maxY - minY) * 0.8 + (maxY - minY) * 0.1; // bias away from edges

        if (x >= 0 && x <= canvasWidth && y >= 0 && y <= canvasHeight) {
          // Simple point-in-polygon check
          if (pointInPolygon(x, y, pixelCoords)) {
            placements.push({
              x,
              y,
              scale: figureHeight / 80, // 80 is the viewBox height
              opacity: 0.4 + rng() * 0.25, // 0.4-0.65 opacity for subtle look
              figureIndex: Math.floor(rng() * FIGURE_PATHS.length),
            });
            break;
          }
        }
      }
    }
  }

  return placements;
}

// ---------------------------------------------------------------------------
// Core overlay function
// ---------------------------------------------------------------------------

/**
 * Overlay architectural scale figures onto a rendered image.
 * Returns a new data-URI with figures composited on top.
 */
export async function overlayArchitecturalFigures(
  baseDataUri: string,
  zones: SiteZone[],
  map: MapboxMap,
  dpr: number = window.devicePixelRatio || 1,
): Promise<string> {
  // Load the base image
  const img = await loadImage(baseDataUri);
  const w = img.width;
  const h = img.height;

  // Compute placements
  const placements = computeFigurePlacements(zones, map, w, h, dpr);

  if (placements.length === 0) {
    return baseDataUri; // No walkable zones, return unchanged
  }

  // Create canvas and draw base
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(img, 0, 0);

  // Draw each figure
  for (const p of placements) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.scale, p.scale);
    ctx.translate(-20, -80); // Center the 40×80 viewBox

    ctx.strokeStyle = `rgba(40, 40, 40, ${p.opacity})`;
    ctx.lineWidth = 2.5 / p.scale; // Keep consistent visual weight
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Parse and draw the SVG path
    drawSVGPath(ctx, FIGURE_PATHS[p.figureIndex]);

    ctx.restore();
  }

  return canvas.toDataURL('image/png');
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

/** Simple seeded PRNG for deterministic figure placement */
function seedRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return s / 2147483647;
  };
}

/** Ray-casting point-in-polygon test */
function pointInPolygon(x: number, y: number, polygon: { x: number; y: number }[]): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x, yi = polygon[i].y;
    const xj = polygon[j].x, yj = polygon[j].y;
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

/**
 * Parse a simplified SVG path string and draw it on a canvas context.
 * Supports: M (moveTo), L (lineTo), a (arc — used for head circles)
 */
function drawSVGPath(ctx: CanvasRenderingContext2D, pathData: string): void {
  const commands = pathData.match(/[MLaZ][^MLaZ]*/gi) || [];
  let curX = 0, curY = 0;

  ctx.beginPath();

  for (const cmd of commands) {
    const type = cmd[0];
    const nums = cmd.slice(1).trim().split(/[\s,]+/).map(Number);

    switch (type) {
      case 'M':
        curX = nums[0];
        curY = nums[1];
        ctx.moveTo(curX, curY);
        break;
      case 'L':
        curX = nums[0];
        curY = nums[1];
        ctx.lineTo(curX, curY);
        break;
      case 'a': {
        // Simplified arc: draw a circle (used for heads)
        const rx = nums[0];
        ctx.moveTo(curX + rx, curY);
        ctx.arc(curX, curY, rx, 0, Math.PI * 2);
        ctx.moveTo(curX, curY + rx); // Move to bottom of head
        break;
      }
    }
  }

  ctx.stroke();
}
