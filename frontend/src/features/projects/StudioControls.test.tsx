import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { StudioSaveStatus, StudioToolSheet } from './StudioControls';
afterEach(()=>vi.unstubAllGlobals());

describe('drawing save recovery',()=>{
  it('keeps narrow-screen tools collapsed until requested and can return to the map',()=>{
    vi.stubGlobal('matchMedia',()=>({matches:true,addEventListener:vi.fn(),removeEventListener:vi.fn()}));
    render(<StudioToolSheet navigation={<p>Workflow</p>}><button>Draw site boundary</button></StudioToolSheet>);
    expect(screen.queryByRole('button',{name:'Draw site boundary'})).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Show design tools'}));
    expect(screen.getByRole('button',{name:'Draw site boundary'})).toBeVisible();
    fireEvent.click(screen.getByRole('button',{name:'Hide design tools'}));
    expect(screen.queryByRole('button',{name:'Draw site boundary'})).not.toBeInTheDocument();
  });
  it('shows the rejection reason alongside retained draft recovery',()=>{
    render(<StudioSaveStatus saving={false} draftCount={1} loadError={false}
      saveError="Polygon boundary self-intersects" discardableCount={1}
      onRetry={vi.fn()} onReload={vi.fn()} onDiscardRejected={vi.fn()} />);
    expect(screen.getByText(/Polygon boundary self-intersects/)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save again'})).toBeEnabled();
    expect(screen.getByRole('button',{name:'Discard rejected drawing'})).toBeEnabled();
  });
});
