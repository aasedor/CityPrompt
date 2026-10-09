import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { CLASSROOM_CHOICES, CANONICAL_DOMAINS, filterCanonicalChoices } from './canonicalCatalogue';
import { catalogueSizeId, catalogueStyleIds } from './catalogueFacets';

function setup(){
  const onPick=vi.fn(),onPickCanonical=vi.fn(),onPickStreet=vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickCanonical={onPickCanonical} onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Buildings'}));
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  return {onPick,onPickCanonical,onPickStreet};
}
describe('student catalogue facets',()=>{
  it('restores expansion style tags without importing other parent variants or geometry defaults',()=>{
    const restored=CLASSROOM_CHOICES.filter(choice=>choice.domain==='building' && !CANONICAL_DOMAINS.building.some(source=>source.id===choice.option.id));
    expect(restored.length).toBeGreaterThan(0);
    for(const choice of restored){
      expect(choice.placements).toHaveLength(1);
      expect(choice.option.variants?.map(variant=>variant.id)).toEqual([choice.placements[0].model.variantId]);
      expect(choice.option.propertyPresets).toBe(choice.placements[0].properties);
      expect(choice.option.minFloors).toBeUndefined();
      expect(choice.option.maxFloors).toBeUndefined();
      expect(choice.option.suggestedAreaSqm).toBeUndefined();
      expect(choice.option.footprintCompatibility).toBeUndefined();
    }
  });
  it('combines style, plot size and land use, then places the same exact model',()=>{
    const callbacks=setup();
    const nordic=CLASSROOM_CHOICES.find(item=>item.domain==='building' && catalogueStyleIds(item).includes('scandinavian_nordic'))!;
    expect(nordic).toBeDefined();
    fireEvent.change(screen.getByLabelText('Architectural style'),{target:{value:'scandinavian_nordic'}});
    fireEvent.change(screen.getByLabelText('Default plot area'),{target:{value:catalogueSizeId(nordic)}});
    fireEvent.change(screen.getByLabelText('Land-use type'),{target:{value:nordic.placements[0].calgaryGuide.groupId}});
    expect(screen.getByRole('button',{name:new RegExp(`${nordic.placements[0].label}.*Choose & place`)})).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:/Blue glass office tower.*Choose & place/})).not.toBeInTheDocument();
    expect(callbacks.onPick).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button',{name:new RegExp(`${nordic.placements[0].label}.*Choose & place`)}));
    expect(callbacks.onPick).toHaveBeenCalledWith(nordic.placements[0].id);
    expect(callbacks.onPickCanonical).not.toHaveBeenCalled();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
  it('resets all filters from an empty intersection and clears them on a section change',()=>{
    setup();
    fireEvent.change(screen.getByLabelText('Architectural style'),{target:{value:'scandinavian_nordic'}});
    fireEvent.change(screen.getByLabelText('Search objects or district code'),{target:{value:'not-a-real-design-zzzz'}});
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Clear filters'}));
    expect(screen.getByLabelText('Architectural style')).toHaveValue('');
    expect(screen.getByLabelText('Default plot area')).toHaveValue('');
    expect(screen.getByLabelText('Land-use type')).toHaveValue('');
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.change(screen.getByLabelText('Architectural style'),{target:{value:'scandinavian_nordic'}});
    fireEvent.click(screen.getAllByRole('button',{name:'Parks'})[1]);
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(screen.queryByLabelText('Architectural style')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Default plot area')).toHaveValue('');
    expect(screen.getByLabelText('Park purpose')).toHaveValue('');
    fireEvent.click(screen.getAllByRole('button',{name:'Buildings'})[1]);
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(screen.getByLabelText('Architectural style')).toHaveValue('');
  });
  it('searches the Brutalist label even when the source category is Brutalism',()=>{
    // A bounded synthetic registration verifies future style discovery without
    // activating a currently unreviewed Brutalist family in the real roster.
    const parent=CLASSROOM_CHOICES.find(choice=>choice.domain==='building')!;
    const brutalist={...parent,option:{...parent.option,label:'Concrete civic hall',categoryId:'brutalism',generationTags:[]}};
    expect(filterCanonicalChoices('building','Brutalist','',[brutalist])).toEqual([brutalist]);
  });
  it('filters streets by registered width and dispatches the original route asset',()=>{
    const callbacks=setup();
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    fireEvent.change(screen.getByLabelText('Corridor width'),{target:{value:'narrow'}});
    expect(screen.queryByLabelText('Default plot area')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Architectural style')).not.toBeInTheDocument();
    const street=CLASSROOM_CHOICES.find(choice=>choice.domain==='street_pathway' && choice.placements[0]?.kind==='street' && catalogueSizeId(choice)==='narrow')!;
    expect(street).toBeDefined();
    fireEvent.change(screen.getByLabelText('Search objects or district code'),{target:{value:street.placements[0].label}});
    fireEvent.click(screen.getByRole('button',{name:new RegExp(`${street.placements[0].label}.*Choose & draw route`)}));
    expect(callbacks.onPickStreet).toHaveBeenCalledWith(street.placements[0]);
    expect(callbacks.onPick).not.toHaveBeenCalled();
  });
});
