import type { ParkWalkingNetwork } from './parkWalking';

/** Fixed metric additions to the four stair-only native parks. A lift changes
 * levels only at its cabin; the bridge is a real visible and walkable deck. */
export interface ParkLiftPlan {
  x: number;
  y: number;
  bridgeStartY: number;
  bridgeEndY: number;
  lowerZ: number;
  upperZ: number;
  bridgeZ: number;
  widthM?: number;
  cabinDepthM?: number;
  connectX?: number;
  lowClearanceY?: [number, number][];
  color: string;
  destination: string;
}

export const STEP_FREE_PARK_LIFTS: Record<string, ParkLiftPlan> = {
  student_quarry_garden_v1: {
    x: 4.5, y: -3.85, bridgeStartY: -28, bridgeEndY: -3.85, cabinDepthM: 2.2,
    lowerZ: -4.5, upperZ: 0, bridgeZ: 0, lowClearanceY: [[-26,-20]], color: '#9c8b72', destination: 'entrance rim',
  },
  student_cascade_water_garden_v1: {
    x: 25, y: -27, bridgeStartY: -27, bridgeEndY: 20,
    lowerZ: 0, upperZ: 4.5, bridgeZ: 4.5, lowClearanceY: [[-3,11]], color: '#b5aa96', destination: 'upper garden',
  },
  student_treetop_walk_v1: {
    x: -19.7, y: -24, bridgeStartY: -24, bridgeEndY: -6.2, connectX: -15,
    lowerZ: 0, upperZ: 4.2, bridgeZ: 4.2, color: '#806044', destination: 'canopy walk',
  },
  student_terraced_rose_v1: {
    x: 11.1, y: -27, bridgeStartY: -27, bridgeEndY: 23, widthM: 1.7,
    lowerZ: 0, upperZ: 2.4, bridgeZ: 2.4, lowClearanceY: [[-12,8]], color: '#c5b69b', destination: 'upper rose garden',
  },
};

const memo = new WeakMap<ParkWalkingNetwork, Map<string, ParkWalkingNetwork>>();

export function stepFreeParkWalkingNetwork(variantId: string, original: ParkWalkingNetwork): ParkWalkingNetwork {
  const plan = STEP_FREE_PARK_LIFTS[variantId];
  if (!plan) return original;
  let variants = memo.get(original);
  if (!variants) { variants = new Map(); memo.set(original, variants); }
  const cached = variants.get(variantId); if (cached) return cached;
  const half = (plan.widthM??2.48)/2, x0 = plan.x - half, x1 = plan.x + half;
  const y0 = Math.min(plan.bridgeStartY, plan.bridgeEndY) - .06;
  const y1 = Math.max(plan.bridgeStartY, plan.bridgeEndY) + .06;
  const z = plan.bridgeZ;
  const a = [x0,y0,z], b = [x1,y0,z], c = [x1,y1,z], d = [x0,y1,z];
  const next: ParkWalkingNetwork = {
    ...original, version: 2,
    triangles: [...original.triangles, [a,b,c], [a,c,d]],
    obstacles: [...original.obstacles,
      ...(plan.lowClearanceY??[]).map(([lo,hi])=>[x0,x1,lo,hi,z-.45,z-.12]),
    ],
  };
  const cabinHalfWidth=1.25,cabinHalfDepth=(plan.cabinDepthM??2.6)/2;
  for(const landingZ of [plan.lowerZ,plan.upperZ]){
    const left=plan.x-cabinHalfWidth,right=plan.x+cabinHalfWidth;
    const bottom=plan.y-cabinHalfDepth,top=plan.y+cabinHalfDepth;
    const p0=[left,bottom,landingZ],p1=[right,bottom,landingZ];
    const p2=[right,top,landingZ],p3=[left,top,landingZ];
    next.triangles.push([p0,p1,p2],[p0,p2,p3]);
  }
  const supports=Math.max(1,Math.floor((y1-y0)/7));
  for(let i=0;i<supports;i++){
    const yy=y0+(i+1)*(y1-y0)/(supports+1);
    for(const side of [-1,1]){
      const xx=plan.x+side*(half-.23);
      next.obstacles.push([xx-.1,xx+.1,yy-.1,yy+.1,plan.lowerZ,z-.12]);
    }
  }
  if (plan.connectX !== undefined) {
    const lo=Math.min(plan.x,plan.connectX),hi=Math.max(plan.x,plan.connectX);
    const q0=[lo,plan.bridgeEndY-half,z],q1=[hi,plan.bridgeEndY-half,z];
    const q2=[hi,plan.bridgeEndY+half,z],q3=[lo,plan.bridgeEndY+half,z];
    next.triangles.push([q0,q1,q2],[q0,q2,q3]);
  }
  variants.set(variantId, next);
  return next;
}
