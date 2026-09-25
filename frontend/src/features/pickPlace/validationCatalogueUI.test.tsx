import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';

describe('local student validation discovery',()=>{
  it('shows only the exact 12/8/7 selection and distinguishes fixtures from drawable streets',()=>{
    const onPick=vi.fn(),onPickStreet=vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Buildings'}));
    expect(within(screen.getByLabelText('Catalogue collection')).getAllByRole('option')).toHaveLength(1);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    for(const article of screen.getAllByRole('article'))expect(within(article).getAllByRole('option')).toHaveLength(1);
    fireEvent.click(screen.getAllByRole('button',{name:'Parks'})[1]);
    expect(screen.getAllByRole('article')).toHaveLength(8);
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    expect(screen.getAllByRole('article')).toHaveLength(2);
    expect(screen.getAllByText('Choose & draw route')).toHaveLength(2);
    fireEvent.click(screen.getByRole('button',{name:/Neighbourhood Main Street.*Choose & draw route/}));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({id:'validation_student_main_street_v1'}));
    fireEvent.click(screen.getByRole('button',{name:'Streets'}));
    fireEvent.click(screen.getByRole('button',{name:'Show 5 fixed review segments (placement only)'}));
    expect(screen.getAllByRole('article')).toHaveLength(7);
    expect(screen.getAllByText('Place fixed review segment')).toHaveLength(5);
    fireEvent.click(screen.getByRole('button',{name:/Tied-arch gateway bridge.*Place fixed review segment/}));
    expect(onPick).toHaveBeenCalledWith('validation_landmark_signature_bridge_v2');
  });
  it('starts point-by-point road drawing directly from the sidebar',()=>{
    const onPickStreet=vi.fn();
    render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="idle" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Draw a road route'}));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({kind:'street',id:'validation_student_main_street_v1'}));
  });
});
