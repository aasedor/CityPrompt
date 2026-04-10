/**
 * globeProjection.ts — Coordinate projection utilities for AI render pipeline.
 *
 * Replaces Mapbox's map.project()/map.unproject() with Three.js camera projection
 * against the WGS84 ellipsoid.
 */

import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';

const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

/**
 * Project a [lng, lat] to screen pixels using a Three.js camera.
 */
export function projectToScreen(
  lngLat: [number, number],
  camera: THREE.Camera,
  width: number,
  height: number,
  heightAboveSurface = 0,
): { x: number; y: number } | null {
  const pos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    lngLat[1] * DEG_TO_RAD,
    lngLat[0] * DEG_TO_RAD,
    heightAboveSurface,
    pos,
  );

  pos.project(camera);

  // Behind camera check
  if (pos.z > 1) return null;

  return {
    x: (pos.x + 1) / 2 * width,
    y: (1 - pos.y) / 2 * height,
  };
}

/**
 * Project an array of zone coordinates to screen pixels.
 * Returns null for any point behind the camera.
 */
export function projectZoneToPixels(
  coords: number[][],
  camera: THREE.Camera,
  width: number,
  height: number,
): { x: number; y: number }[] {
  const result: { x: number; y: number }[] = [];
  for (const c of coords) {
    const p = projectToScreen([c[0], c[1]], camera, width, height);
    if (p) result.push(p);
  }
  return result;
}

/**
 * Unproject screen pixels to [lng, lat] by raycasting against the WGS84 ellipsoid.
 */
export function unprojectFromScreen(
  point: { x: number; y: number },
  camera: THREE.Camera,
  width: number,
  height: number,
): [number, number] | null {
  const ndc = new THREE.Vector2(
    (point.x / width) * 2 - 1,
    -(point.y / height) * 2 + 1,
  );

  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(ndc, camera);

  const hit = new THREE.Vector3();
  const result = WGS84_ELLIPSOID.intersectRay(raycaster.ray, hit);
  if (!result) return null;

  const cartographic = WGS84_ELLIPSOID.getPositionToCartographic(hit, {} as any);
  return [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG];
}

/**
 * Generate a binary mask canvas from zone polygons projected to screen space.
 * White = zone area (edit), Black = preserve.
 */
export function generateGlobeMask(
  zones: { coordinates: number[][]; zoneType: string; height?: number }[],
  camera: THREE.Camera,
  width: number,
  height: number,
): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  // Start with black (preserve everything)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  // Draw each zone as white
  ctx.fillStyle = '#ffffff';
  for (const zone of zones) {
    const pixels = projectZoneToPixels(zone.coordinates, camera, width, height);
    if (pixels.length < 3) continue;

    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x, pixels[i].y);
    }
    ctx.closePath();

    // For buildings, add headroom above the polygon
    if ((zone.zoneType === 'building' || zone.zoneType === 'residential') && zone.height) {
      // Expand the mask upward to include building height
      const topPx = zone.coordinates.map(c =>
        projectToScreen([c[0], c[1]], camera, width, height, zone.height)
      ).filter(Boolean) as { x: number; y: number }[];

      if (topPx.length >= 3) {
        // Draw expanded polygon including both base and top projections
        ctx.moveTo(topPx[0].x, topPx[0].y);
        for (const p of topPx) ctx.lineTo(p.x, p.y);
      }
    }

    ctx.fill();
  }

  return canvas;
}

/**
 * Capture the R3F canvas as a base64 PNG.
 */
export function captureGlobeScreenshot(renderer: THREE.WebGLRenderer): Promise<string> {
  return new Promise((resolve) => {
    const canvas = renderer.domElement;
    canvas.toBlob((blob) => {
      if (!blob) { resolve(''); return; }
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1]); // Return raw base64 without prefix
      };
      reader.readAsDataURL(blob);
    }, 'image/png');
  });
}
