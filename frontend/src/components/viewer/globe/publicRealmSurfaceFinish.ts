/** Material variation only: retain every path, pad and planting-room boundary.
 * Grain is evaluated in metres, so resizing a park never enlarges aggregate.
 * No baked trees, people, furniture or directional shadows. */
export function finishParkSurface(data: Uint8ClampedArray, width: number, pixelsPerMetre: number): void {
  for (let i = 0; i < data.length; i += 4) {
    const p = i / 4, x = p % width, y = Math.floor(p / width);
    const mx = x / pixelsPerMetre, my = y / pixelsPerMetre;
    const green = data[i + 1] > data[i] * 1.035 && data[i + 1] > data[i + 2] * 1.15;
    let n = Math.imul(x + 17, 374761393) ^ Math.imul(y + 31, 668265263);
    n = Math.imul(n ^ (n >>> 13), 1274126177);
    const grain = ((n >>> 0) / 4294967295 - .5) * (green ? 14 : 9);
    const drift = green ? 5 * Math.sin(mx * .77 + Math.sin(my * .39)) + 3 * Math.sin(my * 1.61 + mx * .3) : 0;
    for (let c = 0; c < 3; c++) data[i + c] = Math.max(0, Math.min(255, data[i + c] + grain + drift));
  }
}
