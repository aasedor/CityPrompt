import { installPolicyMapFetch } from './policyMapFetch.test-support';
import { describe, expect, it } from 'vitest';
import { loadLocalAreaPlan, localAreaPlan, matchLocalAreaPlans } from './localAreaPlans';
import { selectPolicySite } from './rileyPolicy';
installPolicyMapFetch();
const square = (x:number,y:number) => [[x-.00015,y-.00015],[x+.00015,y-.00015],[x+.00015,y+.00015],[x-.00015,y+.00015]];
describe('approved Beltline ARP land-use concept maps',()=>{
  it('matches western and eastern Beltline separately using published City plan boundaries',()=>{
    expect(matchLocalAreaPlans(square(-114.08,51.04)).matches[0]?.id).toBe('beltline-part-1');
    expect(matchLocalAreaPlans(square(-114.052,51.04)).matches[0]?.id).toBe('beltline-part-2');
    expect(matchLocalAreaPlans(square(-114.08,51.035)).matches.map(plan=>plan.id)).not.toContain('beltline-part-1');
  });
  it('loads source-derived concept areas and retains each ARP map identity and legend',async()=>{
    for(const [id,x,y] of [['beltline-part-1',-114.08,51.04],['beltline-part-2',-114.052,51.04]] as const){
      const plan=localAreaPlan(id)!;
      expect(plan).toBeDefined();
      expect(plan.mapLabel).toBe('Land Use Concept');
      const data=await loadLocalAreaPlan(id);
      expect(data.snapshot).toBe(plan.snapshot);
      expect(data.boundary).toEqual(plan.boundary);
      expect(selectPolicySite(data,square(x,y)).features.length).toBeGreaterThan(0);
      expect(new Set(data.features.map(feature=>feature.id)).size).toBe(data.features.length);
      for(const feature of data.features){
        const definition=plan.designations.find(item=>item.name===feature.properties.category);
        expect(definition).toBeDefined();
        expect(feature.properties.color).toBe(definition!.color);
        expect(definition!.summary).not.toContain('Neighbourhood Flex');
      }
    }
    expect(localAreaPlan('beltline-part-1')!.designations.map(item=>item.name)).toContain('Primarily Residential');
    expect(localAreaPlan('beltline-part-2')!.designations.map(item=>item.name)).toContain('Potential Open Space');
  });
});
