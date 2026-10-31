import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from '@/features/pickPlace/PlacementPalette';
import { CANONICAL_CHOICES } from '@/features/pickPlace/canonicalCatalogue';

function setup(section='Buildings') {
  const onPick=vi.fn(), onPickCanonical=vi.fn(), onPickStreet=vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickCanonical={onPickCanonical}
    onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:section}));
  return {onPick,onPickCanonical,onPickStreet};
}

describe('undergraduate teaching browse',()=>{
  it('opens style browsing directly, explains Neoclassicism and places the identical office asset',()=>{
    const callbacks=setup();
    fireEvent.click(screen.getByRole('button',{name:'Browse by architectural style'}));
    fireEvent.change(screen.getByLabelText('Architectural style'),{target:{value:'neoclassical'}});
    expect(screen.getByRole('region',{name:'About the selected architectural style'})).toHaveTextContent(/symmetry/i);
    expect(screen.getAllByRole('article')).toHaveLength(1);
    expect(callbacks.onPick).not.toHaveBeenCalled();
    const office=CANONICAL_CHOICES.find(c=>c.placements[0]?.id==='clay_neoclassical_brick_headquarters')!.placements[0];
    fireEvent.click(screen.getByRole('button',{name:/.*Choose & place/}));
    expect(callbacks.onPick).toHaveBeenCalledWith(office.id);
    expect(callbacks.onPickCanonical).not.toHaveBeenCalled();
  });

  it('finds street components through New Urbanism without certifying or placing a neighbourhood',()=>{
    const callbacks=setup('Streets');
    fireEvent.click(screen.getByRole('button',{name:'Browse by planning idea'}));
    fireEvent.change(screen.getByLabelText('Planning idea'),{target:{value:'new_urbanism'}});
    const explanation=screen.getByRole('region',{name:'About the selected planning idea'});
    expect(explanation).toHaveTextContent(/connected neighbourhoods/i);
    expect(explanation).toHaveTextContent(/component|whole.plan/i);
    expect(screen.getByRole('button',{name:/Quiet Residential Street.*Choose & draw route/})).toBeVisible();
    expect(callbacks.onPickStreet).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Search objects or district code'),{target:{value:'Quiet Residential Street'}});
    fireEvent.click(screen.getByRole('button',{name:/Quiet Residential Street.*Choose & draw route/}));
    expect(callbacks.onPickStreet).toHaveBeenCalledWith(CANONICAL_CHOICES.find(c=>c.placements[0]?.id==='student_quiet_residential_street_v1')!.placements[0]);
  });

  it('clears every filter from an empty teaching intersection and resets teaching state across sections',()=>{
    setup();
    fireEvent.click(screen.getByRole('button',{name:'Browse by planning idea'}));
    fireEvent.change(screen.getByLabelText('Planning idea'),{target:{value:'new_urbanism'}});
    fireEvent.change(screen.getByLabelText('Search objects or district code'),{target:{value:'zz-no-such-design'}});
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Clear filters'}));
    expect(screen.getByLabelText('Planning idea')).toHaveValue('');
    expect(screen.getByLabelText('Architectural style')).toHaveValue('');
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.change(screen.getByLabelText('Planning idea'),{target:{value:'new_urbanism'}});
    fireEvent.click(within(screen.getByRole('navigation',{name:'Catalogue sections'})).getByRole('button',{name:'Parks'}));
    fireEvent.click(screen.getByRole('button',{name:'Browse by planning idea'}));
    expect(screen.getByLabelText('Planning idea')).toHaveValue('');
    expect(screen.queryByLabelText('Architectural style')).not.toBeInTheDocument();
    expect(screen.queryByRole('region',{name:'About the selected planning idea'})).not.toBeInTheDocument();
  });
});
