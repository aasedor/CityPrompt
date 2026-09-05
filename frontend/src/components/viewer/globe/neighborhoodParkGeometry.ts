import { type ParkModule, type ParkPoint } from './neighborhoodParkLayout';

export type ParkGroundSampler = (x: number, y: number) => number;
export function roundedParkPad(module: ParkModule): ParkPoint[] {
  const r = 1.4, w = module.width / 2, d = module.depth / 2;
  return [[w-r,d-r],[-w+r,d-r],[-w+r,-d+r],[w-r,-d+r]].flatMap(([cx,cy], corner) =>
    Array.from({length: 9}, (_, i) => {
      const t = (corner * 90 + i * 90 / 8) * Math.PI / 180;
      const x = cx + Math.cos(t) * r, y = cy + Math.sin(t) * r;
      return {x: module.center.x + Math.cos(module.yaw) * x - Math.sin(module.yaw) * y,
        y: module.center.y + Math.sin(module.yaw) * x + Math.cos(module.yaw) * y};
    }));
}

/** Sample the whole construction pad, including interior terrain humps. */
export function parkPadDatum(module: ParkModule, ground: ParkGroundSampler): {high: number; low: number} {
  let high = -Infinity, low = Infinity;
  const nx = Math.ceil(module.width), ny = Math.ceil(module.depth);
  for(let i=0;i<=nx;i++) for(let j=0;j<=ny;j++) {
    const x = (i/nx-.5)*module.width, y = (j/ny-.5)*module.depth;
    const z = ground(module.center.x + x*Math.cos(module.yaw)-y*Math.sin(module.yaw), module.center.y+x*Math.sin(module.yaw)+y*Math.cos(module.yaw));
    high = Math.max(high,z); low = Math.min(low,z);
  }
  return {high,low};
}

/** Across the full path width the arrival meets the level pad. The transition
 * blends back to measured ground along the approach, never below it. */
export function parkApproachGround(module: ParkModule, path: readonly ParkPoint[], ground: ParkGroundSampler): ParkGroundSampler {
  const [arrival, end] = path, dx = end.x-arrival.x, dy = end.y-arrival.y, length = Math.hypot(dx,dy);
  const high = parkPadDatum(module,ground).high + .01;
  const rampLength = Math.min(length, Math.max(3, (high-ground(arrival.x,arrival.y))*20));
  return (x,y) => {
    const distance = Math.max(0, ((x-arrival.x)*dx+(y-arrival.y)*dy)/length);
    const weight = Math.max(0,1-distance/rampLength), base = ground(x,y);
    return base+(Math.max(base,high)-base)*weight;
  };
}
