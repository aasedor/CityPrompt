import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ReferenceLayersPanel } from './ReferenceLayersPanel';
import type { ReferenceLayer } from './api';

const layer: ReferenceLayer = {
  id: 'reference-a', project_id: 'project-a', name: 'City zoning', kind: 'zoning',
  source_filename: 'districts.geojson', source_crs: 'WGS84', source_url: 'https://city.example/zoning',
  description: null, feature_count: 1, bounds: [-114, 51, -113, 52], warnings: [],
  color: '#7c3aed', opacity: 0.8, created_at: '2026-09-04T00:00:00Z',
  feature_collection: { type: 'FeatureCollection', features: [{ type: 'Feature',
    properties: { DISTRICT: 'R-CG', MAX_HEIGHT: 11 }, geometry: { type: 'Point', coordinates: [-114, 51] },
  }] },
};

describe('Reference layer controls', () => {
  it('toggles only display state and retains inspectable source attributes', () => {
    const onToggle = vi.fn();
    render(<ReferenceLayersPanel layers={[layer]} hiddenIds={new Set()} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole('button', { name: 'Hide City zoning' }));
    expect(onToggle).toHaveBeenCalledWith('reference-a');
    fireEvent.click(screen.getByRole('button', { name: 'City zoning' }));
    expect(screen.getByText('MAX_HEIGHT')).toBeInTheDocument();
    expect(screen.getByText('11')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open source' })).toHaveAttribute('href', layer.source_url);
    expect(screen.queryByRole('button', { name: 'Remove City zoning' })).not.toBeInTheDocument();
  });
  it('requires a separate remove action without changing visibility', () => {
    const onDelete = vi.fn();
    const onToggle = vi.fn();
    render(<ReferenceLayersPanel layers={[layer]} hiddenIds={new Set(['reference-a'])} onToggle={onToggle} onDelete={onDelete} />);
    fireEvent.click(screen.getByRole('button', { name: 'Remove City zoning' }));
    expect(onDelete).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Remove layer' }));
    expect(onDelete).toHaveBeenCalledWith('reference-a');
    expect(onToggle).not.toHaveBeenCalled();
  });
});
