import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { StudioSaveStatus } from './StudioControls';

describe('drawing save recovery',()=>{
  it('shows the rejection reason alongside retained draft recovery',()=>{
    render(<StudioSaveStatus saving={false} draftCount={1} loadError={false}
      saveError="Polygon boundary self-intersects" discardableCount={1}
      onRetry={vi.fn()} onReload={vi.fn()} onDiscardRejected={vi.fn()} />);
    expect(screen.getByText(/Polygon boundary self-intersects/)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save again'})).toBeEnabled();
    expect(screen.getByRole('button',{name:'Discard rejected drawing'})).toBeEnabled();
  });
});
