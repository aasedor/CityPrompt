import { installPolicyMapFetch } from './policyMapFetch.test-support';
import { describe, expect, it, vi } from 'vitest';
import { LOCAL_AREA_PLANS, loadLocalAreaPlan, localAreaPlan, matchLocalAreaPlans, readLocalPolicyPreferences } from './localAreaPlans';
import { selectPolicySite } from './rileyPolicy';

installPolicyMapFetch();

// Independent named street junctions from the City Street Centreline dataset.
export const SITES: Record<string, [number, number]> = {
  riley: [-114.0947104, 51.0525233],
  westbrook: [-114.1412255,51.0377995],
  'west-elbow': [-114.0947243,51.0378309],
  'north-hill': [-114.0715601,51.0742462],
  heritage: [-114.0831626,50.979579],
  chinook: [-114.0813912,51.0087248],
  'south-shaganappi': [-114.1063124,51.0742834],
  'east-calgary': [-113.9757489,51.0424919],
};
const square = ([x,y]: [number,number]) => [[x-.0002,y-.0002],[x+.0002,y-.0002],[x+.0002,y+.0002],[x-.0002,y+.0002]];

describe('approved local area plan collection', () => {
  it('does not cache failed requests or accept a failed/mismatched asset response', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response('Unavailable', { status:503 }));
    await expect(loadLocalAreaPlan('chinook')).rejects.toThrow('unavailable');
    await expect(loadLocalAreaPlan('chinook')).resolves.toMatchObject({ snapshot:localAreaPlan('chinook')!.snapshot });
    vi.mocked(fetch).mockResolvedValueOnce(new Response('null'));
    await expect(loadLocalAreaPlan('chinook')).rejects.toThrow('Invalid');
    const wrongPlan = await loadLocalAreaPlan('heritage');
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify(wrongPlan)));
    await expect(loadLocalAreaPlan('chinook')).rejects.toThrow('edition');
  });
  it('matches real sites to all eight plans using exact plan boundaries', () => {
    for (const [id, point] of Object.entries(SITES)) {
      const match = matchLocalAreaPlans(square(point));
      expect(match.problem, id).toBeNull();
      expect(match.matches[0]?.id, id).toBe(id);
    }
    expect(matchLocalAreaPlans([]).problem).toContain('Draw a site');
    expect(matchLocalAreaPlans(square([-114.20,51.14])).matches).toEqual([]);
    // Inside Riley's bounding box, beyond its actual northeast perimeter.
    expect(matchLocalAreaPlans(square([-114.0695,51.0655])).matches.map(p => p.id)).not.toContain('riley');
  });
  it('reports both plans for a site crossing the North Hill / Riley boundary', () => {
    const match = matchLocalAreaPlans([[-114.102,51.065],[-114.09,51.065],[-114.09,51.069],[-114.102,51.069]]);
    expect(new Set(match.matches.map(p => p.id))).toEqual(new Set(['riley','north-hill']));
  });
  it('loads reviewed snapshots with a matching explanation and source for every category', async () => {
    expect(LOCAL_AREA_PLANS).toHaveLength(8);
    for (const plan of LOCAL_AREA_PLANS) {
      const data = await loadLocalAreaPlan(plan.id);
      expect(data.snapshot).toBe(plan.snapshot);
      expect(data.boundary).toEqual(plan.boundary);
      expect(data.features.length).toBeGreaterThan(300);
      expect(new Set(data.features.map(f => f.id)).size).toBe(data.features.length);
      for (const category of new Set(data.features.map(f => f.properties.category))) {
        const definition = plan.designations.find(d => d.name === category);
        expect(definition, `${plan.id}: ${category}`).toBeDefined();
        expect(definition!.summary.length).toBeGreaterThan(100);
        expect(definition!.considerations).toHaveLength(3);
        expect(definition!.pdfPage).toBeGreaterThan(20);
        expect(definition!.page).toBeGreaterThan(0);
        expect(data.features.filter(f => f.properties.category === category).every(f => f.properties.color === definition!.color)).toBe(true);
      }
      const clipped = selectPolicySite(data, square(SITES[plan.id]));
      expect(clipped.hasCoverage, plan.id).toBe(true);
      expect(clipped.features.length, plan.id).toBeGreaterThan(0);
    }
  });
  it('retains plan-specific editions, colours and source page offsets', () => {
    expect(localAreaPlan('chinook')!.designations.find(d => d.name === 'Neighbourhood Local')).toMatchObject({ color:'#fcecad', section:'2.2.1.6', page:39, pdfPage:43 });
    expect(localAreaPlan('east-calgary')!.designations.find(d => d.name === 'Industrial Heavy')).toMatchObject({ section:'2.2.3.2', page:42, pdfPage:42 });
    expect(localAreaPlan('west-elbow')!.designations.find(d => d.name === 'Regional Campus')).toMatchObject({ section:'2.2.4', page:49, pdfPage:53 });
    expect(localAreaPlan('north-hill')!.edition).toContain('2022');
    expect(localAreaPlan('riley')!.designations.find(d => d.name === 'Natural Areas')!.considerations.join(' ')).toContain('McHugh Bluff');
    expect(localAreaPlan('heritage')!.designations.find(d => d.name === 'Natural Areas')!.considerations.join(' ')).not.toContain('McHugh Bluff');
  });
  it('migrates Riley preferences and rejects unknown or malformed saved plan choices', async () => {
    expect(readLocalPolicyPreferences('{"enabled":true,"opacity":0.4,"clipToSite":true}')).toEqual({ enabled:true, opacity:.4, clipToSite:true, planId:'auto' });
    expect(readLocalPolicyPreferences('{"planId":"chinook"}').planId).toBe('chinook');
    for (const raw of ['{broken','null','5','{"planId":"draft-plan"}']) expect(readLocalPolicyPreferences(raw).planId).toBe('auto');
    await expect(loadLocalAreaPlan('draft-plan')).rejects.toThrow('Unknown');
  });
});
