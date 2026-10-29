import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchStreetNames, streetNameBounds, streetNameLabels, perpendicularLabelRotation } from './streetNames';

const bounds: [number, number, number, number] = [-114.08, 51.04, -114.06, 51.05];
const road = (name: string, coordinates: number[][], state = 'Built') => ({
  properties: { FULL_NAME: name, BUILT_STATUS: state }, geometry: { type: 'LineString', coordinates },
});
afterEach(() => vi.unstubAllGlobals());
describe('street names', () => {
  it('includes surrounding streets and rejects invalid or oversized areas', () => {
    expect(streetNameBounds([[-114.07,51.045],[-114.069,51.045],[-114.069,51.046]])?.[0]).toBeLessThan(-114.07);
    expect(streetNameBounds([])).toBeNull();
    expect(streetNameBounds([[0,0],[1,0],[1,1]])).toBeNull();
    expect(streetNameBounds([[-114.3,51],[-114,51],[-114,51.1]])).toBeNull();
  });
  it('deduplicates names, clips to the view and ignores unbuilt or malformed roads', () => {
    const labels = streetNameLabels([
      road('10 ST NW', [[-114.09,51.045],[-114.05,51.045]]),
      road('10 ST NW', [[-114.075,51.046],[-114.074,51.046]]),
      road('Future road', [[-114.075,51.046],[-114.074,51.046]], 'PLANNED'),
      road('', [[-114.075,51.046],[-114.074,51.046]]),
      road('Bad', [[NaN,51.04],[-114.07,51.04]]), null,
    ], bounds);
    expect(labels).toHaveLength(1);
    expect(labels[0].label).toBe('10 ST NW');
    expect(labels[0].anchor[0]).toBeCloseTo(-114.07);
    expect(labels[0].anchor[1]).toBeCloseTo(51.045);
  });
  it('retains the actual clipped segment used to orient each road label', () => {
    const [label]=streetNameLabels([road('Road',[[-114.09,51.045],[-114.05,51.045]])],bounds);
    expect(label.segment).toEqual([[-114.08,51.045],[-114.06,51.045]]);
  });
  it('rotates 90 degrees from the projected road bearing and stays readable when the bearing reverses', () => {
    expect(Math.abs(perpendicularLabelRotation(10,0)!)).toBeCloseTo(Math.PI/2);
    expect(perpendicularLabelRotation(0,10)).toBeCloseTo(0);
    const angle=perpendicularLabelRotation(4,3)!;
    expect(Math.cos(angle)*4 + Math.sin(angle)*3).toBeCloseTo(0);
    expect(perpendicularLabelRotation(-4,-3)).toBeCloseTo(angle);
    expect(perpendicularLabelRotation(0,0)).toBeNull();
    expect(perpendicularLabelRotation(NaN,2)).toBeNull();
  });
  it('bounds network requests and surfaces service errors', async () => {
    const fetcher = vi.fn().mockResolvedValue({ ok:true, json:async()=>({error:{message:'unavailable'}}) });
    vi.stubGlobal('fetch',fetcher);
    await expect(fetchStreetNames(bounds)).rejects.toThrow('Street names');
    const url = new URL(fetcher.mock.calls[0][0]);
    expect(url.searchParams.get('resultRecordCount')).toBe('600');
    expect(url.searchParams.get('outFields')).toBe('FULL_NAME,BUILT_STATUS');
    await expect(fetchStreetNames([0,0,1,1])).rejects.toThrow();
    expect(fetcher).toHaveBeenCalledTimes(1);
  });
});
