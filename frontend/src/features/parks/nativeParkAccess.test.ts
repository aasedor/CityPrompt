import { describe, expect, it } from 'vitest';
import { trimAccessAtNativePaving } from './nativeParkAccess';

describe('native entrance ground ownership',()=>{
  it('keeps a missing approach over the lawn and stops before existing paving',()=>{
    const result=trimAccessAtNativePaving([[0,-20],[0,-13.5]],1.8,([x,y])=>Math.abs(x)<2 && y>=-14.7?0:null);
    expect(result.path[0]).toEqual([0,-20]);
    expect(result.path[result.path.length-1][1]).toBeCloseTo(-14.7,2);
  });
  it('requires paving under the entire path width, not a narrow sliver',()=>{
    const result=trimAccessAtNativePaving([[0,-20],[0,-13.5]],1.8,([x,y])=>Math.abs(x)<.2 && y>=-14.7?0:null);
    expect(result.path[result.path.length-1]).toEqual([0,-13.5]);
  });
  it('preserves the authored paving height at a connection',()=>{
    expect(trimAccessAtNativePaving([[0,-5],[0,0]],1.8,([,y])=>y>=-2?.22:null).endHeight).toBeCloseTo(.225);
  });
});
