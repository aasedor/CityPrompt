import { describe, expect, it } from 'vitest';
import { availableCatalogueSizes, availableCatalogueStyles, catalogueAssetSize, catalogueSizeId, catalogueSizeLabel, catalogueStyleIds, catalogueStyleLabel, choiceMatchesFacets } from './catalogueFacets';
import type { CanonicalChoice } from './canonicalCatalogue';
import type { PlaceAsset, StreetAsset } from './assetRegistry';

const plot: PlaceAsset = {
  id:'home', kind:'object', definitionVersion:1, label:'Home', description:'A reviewed home',
  thumbnail:'/home.png', readiness:'pilot', model:{variantId:'home-v1',revision:null,method:'RLASM 6.1'},
  calgaryGuide:{groupId:'detached',basis:'form_reference'}, properties:{floors:20},
  zoneType:'building', reshapeMode:'fixed_native', width:20, depth:20, minWidth:20, minDepth:20,
  maxSize:100, nativeDimensions:[10,10,60], reshapeDescription:'Preserve the model.',
};
const choice: CanonicalChoice = {
  id:'building:home:home-v1', domain:'building', placements:[plot],
  option:{id:'home',label:'Home',description:'A Nordic design',photoUrl:'/home.png',categoryId:'scandinavian_nordic'},
};
describe('catalogue size and style evidence',()=>{
  it.each([
    ['civic_modernism_rec', 'Civic Modernism'],
    ['civic_monumental', 'Monumental Civic'],
    ['daylight_factory', 'Industrial'],
    ['glass_tower_modern', 'Modern Glass'],
    ['modern_bigbox', 'Modern Commercial'],
    ['roadside_commercial', 'Roadside Commercial'],
    ['corrugated_vernacular', 'Corrugated-Metal Vernacular'],
    ['japanese_contemporary', 'Contemporary Japanese'],
    ['parkitecture', 'Rustic Park Architecture'],
  ])('presents the source style %s with a readable label', (id, label)=>{
    expect(catalogueStyleLabel(id)).toBe(label);
    const styled={...choice,option:{...choice.option,categoryId:id}};
    expect(availableCatalogueStyles([styled],[])).toEqual([{id,label}]);
    expect(catalogueStyleIds(styled)).toEqual([id]);
  });
  it('uses reserved plot area rather than model envelope or total floor area',()=>{
    expect(catalogueAssetSize(plot)).toBe(400);
    expect(catalogueSizeLabel(plot)).toBe('Default plot 20 × 20 m · 400 m²');
    expect(catalogueSizeId(choice)).toBe('small');
  });
  it.each([[499.9,'small'],[500,'medium'],[2000,'large'],[10000,'district']])('classifies a %s m² default plot as %s', (area,id)=>{
    const sized={...choice,placements:[{...plot,width:Number(area),depth:1}]};
    expect(catalogueSizeId(sized)).toBe(id);
  });
  it('uses corridor width for routes and does not assume a route length',()=>{
    const street:StreetAsset={...plot,kind:'street',reshapeMode:'fixed_section_route',sectionWidth:12};
    const route={...choice,domain:'street_pathway' as const,placements:[street]};
    expect(catalogueAssetSize(street)).toBe(12);
    expect(catalogueSizeId(route)).toBe('local');
    expect(catalogueSizeLabel(street)).toBe('12 m corridor width');
  });
  it('keeps missing and invalid dimensions discoverable without guessing a size',()=>{
    const unknown={...choice,placements:[{...plot,width:NaN}]};
    expect(catalogueSizeId(unknown)).toBe('unknown');
    expect(catalogueAssetSize({...plot,depth:0})).toBeUndefined();
    expect(availableCatalogueSizes('building',[choice,unknown]).map(item=>item.id)).toEqual(['small','unknown']);
  });
  it('supports Scandinavian aliases and positive Brutalist tags alongside the original style',()=>{
    expect(catalogueStyleIds(choice)).toEqual(['scandinavian_nordic']);
    const mixed={...choice,option:{...choice.option,categoryId:'modernist',generationTags:['brutalist','concrete','modernist']}};
    expect(catalogueStyleIds(mixed)).toEqual(['modernist','brutalism']);
    expect(availableCatalogueStyles([choice,mixed],[])).toContainEqual({id:'brutalism',label:'Brutalist'});
    expect(availableCatalogueStyles([choice],[])).toEqual([{id:'scandinavian_nordic',label:'Scandinavian / Nordic'}]);
  });
  it('does not infer style from a material, a description, a render prompt, or a park',()=>{
    const untagged={...choice,option:{...choice.option,categoryId:'institutional_education',description:'Concrete Brutalist inspiration',generationTags:['concrete']}};
    expect(catalogueStyleIds(untagged)).toEqual([]);
    expect(catalogueStyleIds({...choice,domain:'park_plaza'})).toEqual([]);
    expect(availableCatalogueStyles([untagged],[])).toEqual([{id:'unknown',label:'Style not catalogued'}]);
  });
  it('combines filters without mutating the selected placement or saved model contract',()=>{
    const original=JSON.stringify(choice);
    expect(choiceMatchesFacets(choice,{sizeId:'small',styleId:'scandinavian_nordic'})).toBe(true);
    expect(choiceMatchesFacets(choice,{sizeId:'large',styleId:'scandinavian_nordic'})).toBe(false);
    expect(choiceMatchesFacets(choice,{sizeId:'small',styleId:'brutalism'})).toBe(false);
    expect(JSON.stringify(choice)).toBe(original);
    expect(choice.placements[0]).toBe(plot);
  });
});
