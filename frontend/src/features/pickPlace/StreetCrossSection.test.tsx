import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { STREET_ASSETS } from './assetRegistry';
import { StreetCrossSection } from './StreetCrossSection';
import { StreetRoutePanel } from './StreetRoutePanel';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import type { SiteZone } from '@/types';

describe('street section dimensions', () => {
  it.each(STREET_ASSETS.map(a=>[a.label,a] as const))('shows %s with dimensions from the rendered section', (_, asset) => {
    const profile = resolvePilotStreetSectionProfile({ properties: asset.properties });
    expect(profile?.rowM).toBe(asset.sectionWidth);
    expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(asset.sectionWidth, 8);
    const displayedWidth = Number(asset.sectionWidth.toFixed(2));
    render(<StreetCrossSection asset={asset} expanded />);
    expect(screen.getByRole('img', { name: `${asset.label}: ${displayedWidth} metre cross-section` })).toBeInTheDocument();
    expect(screen.getByText(new RegExp(`cross-section · ${displayedWidth} m total`, 'i'))).toBeInTheDocument();
    expect(screen.getByText(/Widths to scale/)).toBeInTheDocument();
  });
  it('rounds the green bridge label while drawing its exact source-width bands', () => {
    const asset = STREET_ASSETS.find(item => item.model.variantId === 'planted_green_bridge_route_v1')!;
    expect(asset.sectionWidth).toBe(36.971);
    render(<StreetCrossSection asset={asset} expanded />);
    const diagram = screen.getByRole('img', {name:'Planted Green Bridge — Draw Route: 36.97 metre cross-section'});
    const bands = [...diagram.querySelectorAll('rect')];
    expect(bands).toHaveLength(3);
    const expectedMetres = [16.1855, 4.6, 16.1855];
    bands.forEach((band, index) => {
      expect(Number(band.getAttribute('width')) / 280 * 36.971).toBeCloseTo(expectedMetres[index], 8);
    });
    expect(screen.getByText('Cross-section · 36.97 m total')).toBeInTheDocument();
  });
  it('shows the selected narrow street instead of hard-coded local-street instructions', () => {
    const asset=STREET_ASSETS.find(a=>a.model.variantId==='student_planted_shared_lane_v1')!;
    const zone = {zone_type:'road',properties:asset.properties,coordinates:bufferLineToPolygon([[-114,51],[-113.999,51]],14)} as SiteZone;
    render(<StreetRoutePanel zone={zone} disabled={false} onReshape={()=>{}} onClose={()=>{}} onDelete={()=>{}} onMore={()=>{}} />);
    expect(screen.getByRole('heading',{name:'Planted Shared Lane'})).toBeInTheDocument();
    expect(screen.getByText(/This section stays 14 m wide/)).toBeInTheDocument();
    expect(screen.queryByText(/16 m/)).not.toBeInTheDocument();
  });
});
