import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchCalgaryDistricts, readCalgaryDistrict } from './calgaryDistricts';

afterEach(()=>vi.unstubAllGlobals());
describe('published Calgary district choices',()=>{
  it('uses a bounded current City query and excludes generic DC choices',async()=>{
    const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>[
      {lu_code:'M-C1',description:'Multi-Residential - Contextual Low Profile'},
      {lu_code:'M-C1'}, {lu_code:'DC',description:'Direct Control'},
    ]});
    vi.stubGlobal('fetch',fetch);
    expect(await fetchCalgaryDistricts(new AbortController().signal)).toEqual([
      {code:'M-C1',designation:'M-C1',description:'Multi-Residential - Contextual Low Profile'},
    ]);
    const url=new URL(fetch.mock.calls[0][0]);
    expect(url.hostname).toBe('data.calgary.ca');
    expect(url.searchParams.get('$limit')).toBe('257');
    expect(url.searchParams.get('$where')).toContain("lu_code != 'DC'");
  });
  it('fails visibly for unavailable, incomplete, or malformed lists',async()=>{
    const fetch=vi.fn();vi.stubGlobal('fetch',fetch);
    for(const response of [{ok:false},...[[{}],[],Array(257).fill({lu_code:'M-C1'}),{error:true}].map(rows=>({ok:true,json:async()=>rows}))]) {
      fetch.mockResolvedValueOnce(response);
      await expect(fetchCalgaryDistricts(new AbortController().signal)).rejects.toThrow();
    }
  });
  it('validates saved identity without guessing a code from a designation',()=>{
    expect(readCalgaryDistrict({designation:' DC48Z84 '})).toEqual({designation:'DC48Z84'});
    expect(readCalgaryDistrict({designation:' ',code:'DC'})).toBeUndefined();
    expect(readCalgaryDistrict({designation:'M-C1 d75',description:23})).toBeUndefined();
  });
});
