import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';

describe('local student validation discovery',()=>{
  it('shows the exact 20/15/10 selection and keeps every street drawable',()=>{
    const onPick=vi.fn(),onPickStreet=vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Buildings'}));
    expect(within(screen.getByLabelText('Catalogue collection')).getAllByRole('option')).toHaveLength(1);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    expect(screen.getByText(/20 buildings, 15 parks, 10 streets/)).toBeInTheDocument();
    for(const article of screen.getAllByRole('article'))expect(within(article).getAllByRole('option')).toHaveLength(1);
    fireEvent.click(screen.getAllByRole('button',{name:'Parks'})[1]);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    expect(screen.getAllByRole('article')).toHaveLength(10);
    expect(screen.getAllByText('Choose & draw route')).toHaveLength(10);
    fireEvent.click(screen.getByRole('button',{name:/Neighbourhood Main Street.*Choose & draw route/}));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({id:'validation_student_main_street_v1'}));
    fireEvent.click(screen.getByRole('button',{name:'Streets'}));
    expect(screen.getAllByRole('article')).toHaveLength(10);
    fireEvent.click(screen.getByRole('button',{name:/Landmark Signature Bridge.*Choose & draw route/}));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({id:'landmark_signature_bridge_v2'}));
    expect(onPick).not.toHaveBeenCalled();
  });
  it('starts point-by-point road drawing directly from the sidebar',()=>{
    const onPickStreet=vi.fn();
    render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="idle" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Draw a road route'}));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({kind:'street',id:'amsterdam_gracht_v1'}));
  });
});
