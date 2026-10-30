import { describe, expect, it } from 'vitest';
import { sourceSpanBridgeLayout, sourceSpanBridgeWalkingHeight, deformSourceBridgePoint } from './sourceSpanBridgeProgram';

const bridge = {
  approachM: 5, endM: 3, deckHeightM: 3, clearWidthM: 4, trafficKind: 'walk' as const,
  parts: [
    {kind:'left',lengthM:5,mode:'fixed' as const},
    {kind:'span',lengthM:20,mode:'span' as const,companions:[{kind:'plants',pitchM:10,lengthM:8}]},
    {kind:'right',lengthM:5,mode:'fixed' as const},
  ],
  walkingPaths:[{widthM:4,points:[[0,0,0],[0,5,3],[0,25,3],[0,30,0]] as [number,number,number][]}],
};

describe('source-derived bridge span layout',()=>{
  it('keeps complete fixed ends and unscaled landscape companions while adapting the span',()=>{
    const parts=sourceSpanBridgeLayout(bridge,50);
    expect(parts.filter(p=>!p.companion).map(p=>[p.kind,p.startM,p.lengthM,p.scale])).toEqual([
      ['left',0,5,1],['span',5,40,2],['right',45,5,1],
    ]);
    const plants=parts.filter(p=>p.companion);
    expect(plants).toHaveLength(4);
    expect(plants.every(p=>p.scale===1&&p.startM>=5&&p.startM+p.lengthM<=45)).toBe(true);
  });
  it('repeats complete structural bays and shares only the remainder',()=>{
    const parts=sourceSpanBridgeLayout({...bridge,parts:[bridge.parts[0],{kind:'arch',lengthM:8,mode:'repeat'},bridge.parts[2]]},51);
    const bays=parts.filter(p=>p.kind==='arch');
    expect(bays).toHaveLength(5);
    expect(bays.every(p=>Math.abs(p.scale-1.025)<1e-8)).toBe(true);
    expect(parts[parts.length-1]?.startM).toBe(46);
  });
  it('rejects a route that consumes the rigid endpoints',()=>{
    expect(()=>sourceSpanBridgeLayout(bridge,9)).toThrow();
  });
  it('maps compact stairs and deck walking to the same adapted geometry',()=>{
    expect(sourceSpanBridgeWalkingHeight(bridge,0,2.5,50)).toBeCloseTo(1.5);
    expect(sourceSpanBridgeWalkingHeight(bridge,0,25,50)).toBe(3);
    expect(sourceSpanBridgeWalkingHeight(bridge,0,47.5,50)).toBeCloseTo(1.5);
    expect(sourceSpanBridgeWalkingHeight(bridge,4,25,50)).toBeNull();
    expect(sourceSpanBridgeWalkingHeight(bridge,0,-.01,50)).toBeNull();
    expect(sourceSpanBridgeWalkingHeight(bridge,0,50.01,50)).toBeNull();
    expect(sourceSpanBridgeWalkingHeight({...bridge,trafficKind:'rail'},0,25,50)).toBeNull();
  });
  it('selects a switchback flight near the current foot height rather than a different floor',()=>{
    const stairs={...bridge,walkingPaths:[
      {widthM:1.5,points:[[0,5,0],[0,7,1]] as [number,number,number][]},
      {widthM:1.5,points:[[0,5,3],[0,7,4]] as [number,number,number][]},
    ]};
    expect(sourceSpanBridgeWalkingHeight(stairs,0,6,30,.4)).toBeCloseTo(.5);
    expect(sourceSpanBridgeWalkingHeight(stairs,0,6,30,3.4)).toBeCloseTo(3.5);
  });
  it('uses the exact skewed tread polygon instead of an inscribed centreline strip',()=>{
    const tread={...bridge,walkingPaths:[{widthM:.1,points:[[1,5.5,2],[1,6.5,2]] as [number,number,number][],
      surfacePolygon:[[0,5,2],[2,6,2],[2,7,2],[0,6,2]] as [number,number,number][]}]};
    expect(sourceSpanBridgeWalkingHeight(tread,.2,5.5,30,1.9)).toBe(2);
    expect(sourceSpanBridgeWalkingHeight(tread,2.1,7,30,1.9)).toBeNull();
  });
  it('preserves the V/S lateral and vertical shape with rigid terminal bands',()=>{
    const d={mode:'longitudinal-core-v1' as const,nativeLengthM:60,requestedLengthM:80,rigidEndM:10};
    expect(deformSourceBridgePoint([4,7,-30],d)).toEqual([4,7,-40]);
    expect(deformSourceBridgePoint([4,7,-25],d)).toEqual([4,7,-35]);
    expect(deformSourceBridgePoint([4,7,0],d)).toEqual([4,7,0]);
    expect(deformSourceBridgePoint([4,7,10],d)).toEqual([4,7,15]);
  });
  it('changes ring radius while preserving radial deck width and mast size',()=>{
    const d={mode:'circle-radius-v1' as const,nativeLengthM:56,requestedLengthM:67.2,radiusM:33,centerAcrossM:17};
    const inner=deformSourceBridgePoint([47,6.6,0],d,'ring');
    const outer=deformSourceBridgePoint([53,6.6,0],d,'ring');
    expect(outer[0]-inner[0]).toBeCloseTo(6);
    expect(inner[1]).toBe(6.6);
    const mast=deformSourceBridgePoint([17.5,60,0],d,'pylon');
    expect(mast[0]).toBeCloseTo(20.9);
    expect(mast[1]).toBe(60);
  });
});
