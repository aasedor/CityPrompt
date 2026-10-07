import clipping from 'polygon-clipping';
import { zoningBounds, type Position } from '@/features/referenceLayers/zoningLabels';
import index from './data/localPlanIndex.json';
import { localDesignations, type DesignationReference } from './localDesignations';
import { loadRileyPolicy, type PolicySnapshot, type PolicyPreferences, readPolicyPreferences } from './rileyPolicy';
import { loadPolicySnapshot } from './policySnapshotLoader';

type PlanIndex = Omit<PolicySnapshot, 'features'> & {
  id: string; name: string; title: string; edition: string; source: string; pageUrl: string;
  mapPage: number; references: DesignationReference[]; alignmentChecks: number; alignmentMaxMetres: number;
};
export const LOCAL_AREA_PLANS = (index as unknown as PlanIndex[]).map(plan => ({ ...plan, designations: localDesignations(plan.id, plan.references) }));
export type LocalAreaPlan = typeof LOCAL_AREA_PLANS[number];
export const localAreaPlan = (id: string) => LOCAL_AREA_PLANS.find(plan => plan.id === id);
export type LocalPolicyPreferences = PolicyPreferences & { planId: string };
export function readLocalPolicyPreferences(raw: string | null): LocalPolicyPreferences {
  const basic = readPolicyPreferences(raw);
  try {
    const saved = JSON.parse(raw ?? 'null') as { planId?: unknown } | null;
    return { ...basic, planId: typeof saved?.planId === 'string' && localAreaPlan(saved.planId) ? saved.planId : 'auto' };
  } catch { return { ...basic, planId: 'auto' }; }
}

// Each map is a separate cached asset; no PDF processing or eight-map download
// during project startup. The index contains only boundaries and small metadata.
const sources: Record<string, URL> = {
  'east-calgary': new URL('./data/east-calgaryUrbanForm.json', import.meta.url),
  chinook: new URL('./data/chinookUrbanForm.json', import.meta.url),
  heritage: new URL('./data/heritageUrbanForm.json', import.meta.url),
  'north-hill': new URL('./data/north-hillUrbanForm.json', import.meta.url),
  'south-shaganappi': new URL('./data/south-shaganappiUrbanForm.json', import.meta.url),
  westbrook: new URL('./data/westbrookUrbanForm.json', import.meta.url),
  'west-elbow': new URL('./data/west-elbowUrbanForm.json', import.meta.url),
};
export async function loadLocalAreaPlan(id: string): Promise<PolicySnapshot> {
  if (id === 'riley') return loadRileyPolicy();
  const source = sources[id];
  if (!source) throw new Error('Unknown local area plan');
  const data = await loadPolicySnapshot(source);
  if (data.snapshot !== localAreaPlan(id)?.snapshot) throw new Error('Unexpected policy map edition');
  return data;
}

function ringArea(ring: Position[]) {
  // Translate first to avoid cancellation in small Calgary site coordinates.
  const [x, y] = ring[0];
  return Math.abs(ring.reduce((sum, p, i) => {
    const next = ring[(i + 1) % ring.length];
    return sum + (p[0]-x)*(next[1]-y) - (next[0]-x)*(p[1]-y);
  }, 0) / 2);
}

/** Exact boundary intersection, ranked by overlap. Bbox gates avoid unnecessary
 * clipping; touching a boundary at a point/line does not constitute coverage. */
export function matchLocalAreaPlans(coordinates: number[][]) {
  const bounds = zoningBounds(coordinates);
  if (!bounds) return { matches: [], problem: 'Draw a site boundary to explore the local area plan.' };
  if (bounds[0] >= bounds[2] || bounds[1] >= bounds[3]) return { matches: [], problem: 'Draw a valid site boundary to explore the local area plan.' };
  const ring = coordinates.map(([x,y]) => [x,y] as Position);
  if (ring[0][0] !== ring[ring.length-1][0] || ring[0][1] !== ring[ring.length-1][1]) ring.push([...ring[0]]);
  try {
    const matches = LOCAL_AREA_PLANS.flatMap(plan => {
      const [w,s,e,n] = plan.bounds;
      if (bounds[2] < w || bounds[0] > e || bounds[3] < s || bounds[1] > n) return [];
      const intersection = clipping.intersection(plan.boundary.coordinates, [ring]);
      const area = intersection.reduce((sum, polygon) => sum + ringArea(polygon[0]) - polygon.slice(1).reduce((holes, hole) => holes + ringArea(hole), 0), 0);
      return area > 1e-12 ? [{ plan, area }] : [];
    }).sort((a,b) => b.area - a.area).map(match => match.plan);
    return { matches, problem: matches.length ? null : 'No approved local area plan in this collection covers your site. You can browse the plans below.' };
  } catch { return { matches: [], problem: 'The plan could not be matched to this boundary. Check the site outline.' }; }
}
