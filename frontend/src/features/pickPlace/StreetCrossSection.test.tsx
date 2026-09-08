import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { STREET_ASSETS } from './assetRegistry';
import { StreetCrossSection } from './StreetCrossSection';
import { StreetRoutePanel } from './StreetRoutePanel';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import type { SiteZone } from '@/types';

describe('street section dimensions', () => {
  it.each(STREET_ASSETS.map(a=>[a.label,a] as const))('shows %s with dimensions from the rendered section', (_, asset) => {
    render(<StreetCrossSection asset={asset} expanded />);
    expect(screen.getByRole('img', { name: `${asset.label}: ${asset.sectionWidth} metre cross-section` })).toBeInTheDocument();
    expect(screen.getByText(`Cross-section · ${asset.sectionWidth} m total`)).toBeInTheDocument();
    expect(screen.getByText(/Widths to scale/)).toBeInTheDocument();
  });
  it('shows the selected narrow street instead of hard-coded local-street instructions', () => {
    const asset=STREET_ASSETS.find(a=>a.sectionWidth===5)!;
    const zone = {zone_type:'road',properties:asset.properties,coordinates:bufferLineToPolygon([[-114,51],[-113.999,51]],5)} as SiteZone;
    render(<StreetRoutePanel zone={zone} disabled={false} onReshape={()=>{}} onClose={()=>{}} onDelete={()=>{}} onMore={()=>{}} />);
    expect(screen.getByRole('heading',{name:'Planted laneway'})).toBeInTheDocument();
    expect(screen.getByText(/This section stays 5 m wide/)).toBeInTheDocument();
    expect(screen.queryByText(/16 m/)).not.toBeInTheDocument();
    expect(screen.getByText(/Teaching design, not a City standard/)).toBeInTheDocument();
  });
});
