import { describe, expect, it } from 'vitest';
import { BufferGeometry, Float32BufferAttribute } from 'three';
import { registerSafetySurface, safetySurfaceSupport } from './safetySupport';

function rectangle(x0:number,y0:number,x1:number,y1:number,z=0) {
  return new BufferGeometry().setAttribute('position',new Float32BufferAttribute([
    x0,y0,z,x1,y0,z,x1,y1,z,x0,y0,z,x1,y1,z,x0,y1,z,
  ],3));
}
describe('authored safety surface support',()=> {
  const pose={lng:-114,lat:51,angle:0};
  it('uses the rendered road surface datum and checks the complete nominal footprint',()=> {
    const remove=registerSafetySurface({id:'road',lng:-114,lat:51,height:1000,geometries:[rectangle(-10,-10,10,10,.1)]});
    const supported=safetySurfaceSupport(pose,[-3,-2,3,2],['road']);
    expect(supported).toMatchObject({ok:true,hostId:'road'});
    if(supported.ok)expect(supported.height).toBeCloseTo(1000.1,6);
    expect(safetySurfaceSupport(pose,[-11,-2,3,2],['road']).ok).toBe(false);
    remove();expect(safetySurfaceSupport(pose,[-3,-2,3,2],['road']).ok).toBe(false);
  });
  it('rejects interior holes that are invisible to corner-only sampling',()=> {
    const remove=registerSafetySurface({id:'hole',...pose,height:1000,geometries:[
      rectangle(-10,-10,-.1,10,.1),rectangle(.1,-10,10,10,.1),
      rectangle(-.1,-10,.1,-.1,.1),rectangle(-.1,.1,.1,10,.1),
    ]});
    expect(safetySurfaceSupport(pose,[-3,-2,3,2],['hole']).ok).toBe(false);remove();
  });
  it('rejects slopes and mismatched heights without stretching the asset',()=> {
    const g=rectangle(-10,-10,10,10,.1);const p=g.attributes.position;
    for(let i=0;i<p.count;i++)p.setZ(i,.1+p.getX(i)*.01);
    const remove=registerSafetySurface({id:'slope',...pose,height:1000,geometries:[g]});
    expect(safetySurfaceSupport(pose,[-3,-2,3,2],['slope']).ok).toBe(false);remove();
  });
  it('scopes supports to active zones and keeps a replacement when an old effect cleans up',()=> {
    const old=registerSafetySurface({id:'same',...pose,height:1000,geometries:[rectangle(-10,-10,10,10,.1)]});
    const current=registerSafetySurface({id:'same',...pose,height:1001,geometries:[rectangle(-10,-10,10,10,.1)]});old();
    expect(safetySurfaceSupport(pose,[-3,-2,3,2],['other']).ok).toBe(false);
    const supported=safetySurfaceSupport({...pose,angle:90},[-3,-2,3,2],['same']);
    expect(supported.ok).toBe(true);if(supported.ok)expect(supported.height).toBeCloseTo(1001.1,6);current();
  });
});
