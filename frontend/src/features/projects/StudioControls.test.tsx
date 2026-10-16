import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useEffect } from 'react';
import { StudioSaveStatus, StudioToolSheet } from './StudioControls';
afterEach(()=>vi.unstubAllGlobals());

describe('drawing save recovery',()=>{
  it('keeps narrow-screen tools collapsed until requested and can return to the map',()=>{
    vi.stubGlobal('matchMedia',()=>({matches:true,addEventListener:vi.fn(),removeEventListener:vi.fn()}));
    render(<StudioToolSheet navigation={<p>Workflow</p>}><button>Draw site boundary</button></StudioToolSheet>);
    expect(screen.getByRole('button',{name:'Draw site boundary',hidden:true})).not.toBeVisible();
    fireEvent.click(screen.getByRole('button',{name:'Show design tools'}));
    expect(screen.getByRole('button',{name:'Draw site boundary'})).toBeVisible();
    fireEvent.click(screen.getByRole('button',{name:'Hide design tools'}));
    expect(screen.getByRole('button',{name:'Draw site boundary',hidden:true})).not.toBeVisible();
  });
  it('shows the rejection reason alongside retained draft recovery',()=>{
    render(<StudioSaveStatus saving={false} draftCount={1} loadError={false}
      saveError="Polygon boundary self-intersects" discardableCount={1}
      onRetry={vi.fn()} onReload={vi.fn()} onDiscardRejected={vi.fn()} />);
    expect(screen.getByText(/Polygon boundary self-intersects/)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Save again'})).toBeEnabled();
    expect(screen.getByRole('button',{name:'Discard rejected drawing'})).toBeEnabled();
  });
  it('keeps catalogue ownership mounted when crossing the compact breakpoint',()=>{
    let narrow=false;
    vi.stubGlobal('matchMedia',()=>({matches:narrow,addEventListener:vi.fn(),removeEventListener:vi.fn()}));
    const unmount=vi.fn();
    function CatalogueOwner(){useEffect(()=>()=>unmount(),[]);return <button>Browse buildings</button>;}
    const content=<StudioToolSheet navigation={<p>Workflow</p>}><CatalogueOwner/></StudioToolSheet>;
    const view=render(content);
    narrow=true;
    view.rerender(<StudioToolSheet navigation={<p>Workflow</p>}><CatalogueOwner/></StudioToolSheet>);
    expect(unmount).not.toHaveBeenCalled();
    expect(screen.getByRole('button',{name:'Browse buildings',hidden:true})).not.toBeVisible();
    fireEvent.click(screen.getByRole('button',{name:'Show design tools'}));
    expect(screen.getByRole('button',{name:'Browse buildings'})).toBeVisible();
  });
});
