import { CanvasTexture, SRGBColorSpace } from 'three';
import type { SiteZone } from '@/types';
import { createGroundSurfaceTexture, GROUND_SURFACES } from '@/features/groundSurfaces/groundSurfaces';
import { drawnParkingZoneLayout, parkingZoneOutline } from './drawnParking';
import { parkingMarkingSegments } from './parkingLot';

/** Paint belongs to the asphalt itself, so terrain refinement cannot bury or float it. */
export function createDrawnParkingTexture(zone: Pick<SiteZone, 'coordinates' | 'properties'>) {
  const outline = parkingZoneOutline(zone);
  const minX = Math.min(...outline.map(p => p[0])), minY = Math.min(...outline.map(p => p[1]));
  const widthM = Math.max(...outline.map(p => p[0])) - minX;
  const heightM = Math.max(...outline.map(p => p[1])) - minY;
  const resolution = (metres: number) => Math.max(64, Math.min(2048, 2 ** Math.ceil(Math.log2(Math.max(1, metres) * 16))));
  const canvas = document.createElement('canvas');
  canvas.width = resolution(widthM); canvas.height = resolution(heightM);
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.fillStyle = '#414446'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    const grain = createGroundSurfaceTexture(GROUND_SURFACES.find(s => s.id === 'asphalt')!);
    const pattern = ctx.createPattern(grain.image as HTMLCanvasElement, 'repeat');
    if (pattern) {
      // Preserve the same 2m grain tile as other ground surfaces, at every lot size.
      ctx.save(); ctx.scale(canvas.width / (widthM * 64), canvas.height / (heightM * 64));
      ctx.fillStyle = pattern; ctx.fillRect(0, 0, widthM * 64, heightM * 64); ctx.restore();
    }
    grain.dispose();
    const sx = canvas.width / widthM, sy = canvas.height / heightM;
    ctx.setTransform(sx, 0, 0, -sy, -minX * sx, canvas.height + minY * sy);
    ctx.strokeStyle = '#f4f1df';
    // Keep concept paint legible at the 300m limit (one raster pixel minimum).
    ctx.lineWidth = Math.max(.1, 1 / Math.min(sx, sy));
    ctx.beginPath();
    for (const [a, b] of parkingMarkingSegments(drawnParkingZoneLayout(zone))) {
      ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]);
    }
    ctx.stroke();
  }
  const texture = new CanvasTexture(canvas); texture.colorSpace = SRGBColorSpace; texture.anisotropy = 4;
  return { texture, minX, minY, widthM, heightM };
}
