import { describe, expect, it } from 'vitest';
import { compareProposedZoning, comparePolicyIntent } from './planComparisons';
import { placeAsset, placementProperties, PLACE_ASSETS } from '@/features/pickPlace/catalogue';
import type { SiteZone } from '@/types';
import type { ReferenceLayer } from '@/features/referenceLayers/api';

const ring: [number,number][] = [[0,0],[1,0],[1,1],[0,1],[0,0]];
const asset = placeAsset('clay_affordable_aspen_original');
const zone: SiteZone = { id:'building-1', project_id:'project-1', name:'Aspen', zone_type:'building', coordinates:ring,
  properties:placementProperties(asset),color:'#ffffff',sort_order:0,created_at:'2026-10-07T00:00:00Z',updated_at:'2026-10-07T00:00:00Z' };
const layer = (custom = false) => ({id:'study',name:'Student proposal',opacity:0,feature_collection:{type:'FeatureCollection',
  _citypromptStudy:{schema:1,condition:'proposed'},features:[{type:'Feature',id:'a',geometry:{type:'Polygon',coordinates:[ring]},
    properties:{label:'My district',custom,district:{designation:'R-CG'}}}]}} as unknown as ReferenceLayer);

describe('report design comparisons', () => {
  it('compares saved proposed districts even when hidden, without treating a caption as a district', () => {
    const result = compareProposedZoning([zone], [layer()]);
    expect(result[0].comparison?.expected).toContain('R-CG');
    expect(result[0].location.zone_ids).toEqual(['building-1']);
    expect(result[0].comparison?.status).not.toBe('permitted');
    expect(compareProposedZoning([zone], [layer(true)])[0].comparison?.status).toBe('review');
  });
  it('flags plots spanning zones and uncovered plots instead of choosing a centroid district', () => {
    const study = layer();
    study.feature_collection.features[0].geometry = {type:'Polygon',coordinates:[[[0,0],[.5,0],[.5,1],[0,1],[0,0]]]};
    const result = compareProposedZoning([zone], [study]);
    expect(result.some(item => item.title.includes('boundary'))).toBe(true);
    expect(compareProposedZoning([zone], [])[0].comparison?.status).toBe('review');
  });
  it('identifies housing on civic land as a potential departure, not automatic approval or refusal', () => {
    const result = comparePolicyIntent(zone, 'City Civic and Recreation');
    expect(result.status).toBe('potential_conflict');
    expect(result.reason).toContain('supporting');
    expect(comparePolicyIntent(zone, 'Neighbourhood Local').status).toBe('review');
  });
  it('distinguishes discretionary routes, mapped height limits and DC review', () => {
    const study = layer();
    study.feature_collection.features[0].properties.district = {designation:'M-C2'};
    expect(compareProposedZoning([zone],[study])[0].comparison?.status).toBe('discretionary');
    study.feature_collection.features[0].properties.district = {designation:'MU-1f2h6'};
    const mixed = PLACE_ASSETS.find(asset => asset.model.variantId === 'parisian_corner_cafe_culture')!;
    expect(compareProposedZoning([{...zone, properties:placementProperties(mixed)}],[study])[0].comparison?.status).toBe('potential_conflict');
    study.feature_collection.features[0].properties.district = {designation:'DC'};
    expect(compareProposedZoning([zone],[study])[0].comparison?.status).toBe('review');
  });
  it('respects zoning holes and does not invent a classification for an unknown revision', () => {
    const study = layer();
    study.feature_collection.features[0].geometry = {type:'Polygon',coordinates:[[[0,0],[3,0],[3,3],[0,3],[0,0]],ring]};
    expect(compareProposedZoning([zone],[study])[0].comparison?.expected).toContain('No saved proposed');
    const unknown = {...zone, properties:{...zone.properties,pick_place_model_revision:'unknown'}};
    expect(compareProposedZoning([unknown],[layer()])[0].comparison?.status).toBe('review');
  });
});
