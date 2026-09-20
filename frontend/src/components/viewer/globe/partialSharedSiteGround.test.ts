import { describe, expect, it, vi } from 'vitest';
import React from 'react';
import * as THREE from 'three';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { createPartialSharedSiteGroundSnapshot, createSharedSiteGroundSnapshot, sampleSharedSiteGround,
  sharedSiteGroundContains, type SharedSiteGroundLayout } from './sharedSiteGround';
import { resolveBuildingGroundContact, type GroundPoint } from './buildingGroundContact';
import { createSharedGroundTriangulation, drapeSharedGroundGeometry } from './sharedGroundGeometry';
import { captureSharedGround, assertSharedGroundUnchanged } from './sharedGroundCapture';
import { GroundReviewPanel } from './GroundReviewPanel';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const ll = (x: number, y: number): GroundPoint => [-114 + x / metersPerDegLon(51), 51 + y / METERS_PER_DEG_LAT];
const layout: SharedSiteGroundLayout = { boundaryId:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', boundaryUpdatedAt:'now', sourceSignature:'test',
  boundaryCoordinates: [[0,0],[32,0],[32,32],[0,32]].map(([x,y]) => ll(x,y)),
  grid: { west:-114, south:51, columns:9, rows:9, stepLng:4/metersPerDegLon(51), stepLat:4/METERS_PER_DEG_LAT } };
const rough = () => { const h = Array<number>(81).fill(1102); h[5*9+5] += .623219115; return h; };
function state() {
  const heights=rough(), snapshot=createPartialSharedSiteGroundSnapshot(layout,heights,heights)!;
  return { status:'ready' as const, snapshot, revision:snapshot.signature, contains:(x:number,y:number)=>sharedSiteGroundContains(layout.boundaryCoordinates,x,y),
    heightAt:(x:number,y:number)=>sampleSharedSiteGround(snapshot,x,y), review:{layout,heights,previousHeights:heights} };
}
const ring=(x0:number,y0:number,x1:number,y1:number):GroundPoint[][]=>[[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]];

describe('local measured ground recovery',()=>{
  it('isolates a Currie-sized residual without flattening or weakening the strict snapshot',()=>{
    const heights=rough(), ground=state();
    expect(createSharedSiteGroundSnapshot(layout,heights,heights)).toBeNull();
    expect(ground.snapshot.quality.maxLocalResidualM).toBeCloseTo(.623219115);
    expect(ground.snapshot.heights).toEqual(heights);
    expect(ground.snapshot.excludedCells).toEqual([36,37,44,45]);
    expect(ground.heightAt(...ll(4,4))).toBe(1102);
    for(const point of [[20,20],[18,18],[16,16],[24,22]]) expect(ground.heightAt(...ll(...point as GroundPoint))).toBeNull();
    expect(ground.heightAt(...ll(24.01,22))).toBe(1102);
    expect(ground.heightAt(...ll(-1,4))).toBeNull();
  });
  it('requires complete plausible repeatable measurements even for interactive recovery',()=>{
    const heights=rough();
    for(const value of [null,NaN,Infinity,-28000,1103]) {
      const bad:Array<number|null>=[...heights];bad[0]=value;
      expect(createPartialSharedSiteGroundSnapshot(layout,heights,bad)).toBeNull();
    }
    expect(createPartialSharedSiteGroundSnapshot(layout,heights.slice(1),heights)).toBeNull();
    const steep=heights.map((_,i)=>1102+i%9*4);
    expect(createPartialSharedSiteGroundSnapshot(layout,steep,steep)).toBeNull();
  });
  it('retains either pass’s rejected cells and binds coverage to snapshot identity',()=>{
    const a=rough(),b=[...a];b[50]-=.04;
    const partial=createPartialSharedSiteGroundSnapshot(layout,a,b)!;
    expect(partial.excludedCells).toEqual([36,37,44,45]);
    const complete=createPartialSharedSiteGroundSnapshot(layout,b,b)!;
    expect(complete.excludedCells).toBeUndefined();
    expect(partial.signature).not.toBe(complete.signature);
    expect(complete).toEqual(createSharedSiteGroundSnapshot(layout,b,b));
  });
  it('keeps a supported building ready but rejects covered, crossing and interior holes',()=>{
    const ground=state();
    expect(resolveBuildingGroundContact(ring(4,4,8,8),-114,51,ground).status).toBe('ready');
    for(const pads of [ring(17,17,19,19),ring(8,17,28,17.01),ring(12,12,28,28)])
      expect(resolveBuildingGroundContact(pads,-114,51,ground)).toMatchObject({status:'unresolved',reason:'incomplete_footprint_ground'});
  });
  it('never drapes a park or street face across a hole with valid distant corners',()=>{
    const ground=state(),grid=createSharedGroundTriangulation(ground.snapshot,-114,51);
    const geometry=(x0:number,y0:number,x1:number,y1:number)=>{
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([x0,y0,0,x1,y0,0,x1,y1,0,x0,y1,0],3));g.setIndex([0,1,2,0,2,3]);return g;
    };
    for(const box of [[4,4,8,8],[12,12,28,28],[8,17,28,17.01]]){
      const source=geometry(...box as [number,number,number,number]);
      const result=drapeSharedGroundGeometry(source,(x,y)=>{const h=ground.heightAt(...ll(x,y));return h===null?null:h-1102;},4,60000,grid);
      if(box[0]===4)expect(result).not.toBeNull();else expect(result).toBeNull();
      source.dispose();result?.dispose();
    }
  });
  it('blocks both capture entry and completion for partial coverage',()=>{
    const ground=state();expect(()=>captureSharedGround(ground)).toThrow('exports are paused');
    expect(()=>assertSharedGroundUnchanged(ground.snapshot,ground)).toThrow('exports are paused');
    expect(()=>captureSharedGround({...ground,status:'sampling'})).toThrow();
    expect(()=>captureSharedGround({...ground,isCurrent:()=>false})).toThrow();
  });
  it('offers recovery without describing a partially checked site as consistent',()=>{
    const ground=state(),edit=vi.fn(),apply=vi.fn();
    const boundary:SiteZone={id:layout.boundaryId,properties:{},coordinates:layout.boundaryCoordinates,project_id:'p',zone_type:'site_boundary',color:'#fff',sort_order:0,created_at:'now',updated_at:'now'};
    render(React.createElement(GroundReviewPanel,{boundary,ground,onEditBoundary:edit,onApply:apply,onClose:vi.fn()}));
    expect(screen.getByText(/Some ground areas need review/)).toBeTruthy();
    expect(screen.queryByText(/The visible surface is consistent/)).toBeNull();
    fireEvent.click(screen.getByRole('button',{name:'Adjust site boundary'}));
    expect(edit).toHaveBeenCalledOnce();expect(apply).not.toHaveBeenCalled();cleanup();
  });
});
