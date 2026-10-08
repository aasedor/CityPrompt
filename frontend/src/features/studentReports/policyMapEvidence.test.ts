import { describe, expect, it, vi } from 'vitest';
import { collectPolicyMapEvidence } from './policyMapEvidence';
vi.mock('@/features/policyPlans/localAreaPlans', () => ({
  matchLocalAreaPlans: () => ({ matches: [{ id:'test', title:'Test plan', edition:'2026 edition', source:'https://www.calgary.ca/plan.pdf', snapshot:'test-1',
    designations:[{name:'City Civic and Recreation', summary:'Public recreation land.', considerations:['Check local policies.'], page:26, section:'2.2'}] }] }),
  loadLocalAreaPlan: async () => ({boundary:{type:'Polygon',coordinates:[[[0,0],[2,0],[2,2],[0,2],[0,0]]]}, features:[
    {id:'inside',properties:{category:'City Civic and Recreation'},geometry:{type:'Polygon',coordinates:[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}
  ]}),
}));
describe('site policy evidence for reports', () => {
  it('includes intersecting designations and their source edition without requiring a visible overlay', async () => {
    const result=await collectPolicyMapEvidence([[0,0],[.5,0],[.5,.5],[0,.5]]);
    expect(result?.sources[0].title).toContain('City Civic and Recreation');
    expect(result?.sources[0].excerpt).toContain('2026 edition');
    expect(result?.sources[0].excerpt).toContain('Public recreation land.');
    expect(result?.sources[0].url).toBe('https://www.calgary.ca/plan.pdf');
  });
  it('does not attach designations outside the site', async () => {
    expect((await collectPolicyMapEvidence([[1.2,1.2],[1.5,1.2],[1.5,1.5],[1.2,1.5]]))?.sources).toEqual([]);
  });
});
