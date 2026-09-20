import {describe,it,expect} from 'vitest';
import {currentEntranceReviews,entranceReviewRevision,updateEntranceReviews,type BuildingEntranceReview} from './buildingEntranceReview';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

const snapshot={signature:'measured-surface',sourceSignature:'parcel'} as SharedSiteGroundSnapshot;
const display:SharedSiteGroundState={status:'ready',snapshot,revision:'parcel:surface',heightAt:()=>0,contains:()=>true};
const verified:SharedSiteGroundState={...display,revision:'parcel:2:surface',isCurrent:()=>true};
describe('entrance evidence freshness',()=>{
  it('uses the verification generation for the same rendered surface despite different display revisions',()=>{
    expect(entranceReviewRevision(display,verified)).toBe('parcel:2:surface');
    expect(entranceReviewRevision(display,{...verified,revision:'parcel:3:surface'})).toBe('parcel:3:surface');
  });
  it('withholds retained geometry during sampling, synchronous invalidation, previews and surface/source changes',()=>{
    for(const state of [
      {...verified,status:'sampling' as const}, {...verified,isCurrent:()=>false}, {...verified,preview:true},
      {...verified,snapshot:null}, {...verified,snapshot:{...snapshot,signature:'new-surface'}},
      {...verified,snapshot:{...snapshot,sourceSignature:'other-parcel'}},
    ])expect(entranceReviewRevision(display,state)).toBeNull();
    expect(entranceReviewRevision({...display,preview:true},verified)).toBeNull();
  });
});

const review:BuildingEntranceReview={buildingId:'house',groundRevision:'current',generatedSteps:10,riseM:1.8,clearWidthM:1.64,supportHeightM:2};
describe('entrance review ownership',()=>{
  it('keeps current detail evidence when a fallback departs and retires deleted buildings',()=>{
    let records=updateEntranceReviews(new Map(),'detail',review);
    records=updateEntranceReviews(records,'fallback',null);
    expect(currentEntranceReviews(records,new Set(['house']))).toEqual([review]);
    expect(currentEntranceReviews(records,new Set())).toEqual([]);
    records=updateEntranceReviews(records,'detail',null);
    expect(records.size).toBe(0);
  });
  it('publishes changed measurements and avoids repeating unchanged notifications',()=>{
    const initial=updateEntranceReviews(new Map(),'detail',review);
    expect(updateEntranceReviews(initial,'detail',{...review})).toBe(initial);
    const next=updateEntranceReviews(initial,'detail',{...review,groundRevision:'new',riseM:2});
    expect(currentEntranceReviews(next,new Set(['house']))[0]).toMatchObject({groundRevision:'new',riseM:2});
  });
});
