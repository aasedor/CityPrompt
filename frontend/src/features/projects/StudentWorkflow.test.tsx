import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { StudentStepPanel, StudentWorkflowNav, studentLandscapeNeedsRefresh, studentStreetAccessNotice } from './StudentWorkflow';
import type { SiteZone } from '@/types';

const capabilities = vi.hoisted(() => vi.fn());
vi.mock('@/services/api', () => ({ direct3DAttempts: { capabilities } }));

describe('student workflow', () => {
  beforeEach(() => capabilities.mockResolvedValue({ video_enabled: true }));
  it('keeps all steps reachable and identifies the current step', () => {
    const onChange = vi.fn();
    render(<StudentWorkflowNav step="design" onChange={onChange} />);
    expect(screen.getByRole('button', { name: '2 Design' })).toHaveAttribute('aria-current', 'step');
    fireEvent.click(screen.getByRole('button', { name: '1 Site' }));
    expect(onChange).toHaveBeenCalledWith('site');
    fireEvent.click(screen.getByRole('button', { name: '3 Present' }));
    expect(onChange).toHaveBeenLastCalledWith('present');
  });
  it('requires a saved site before confirmation and offers the boundary action', () => {
    const onSite = vi.fn(), onDesign = vi.fn();
    render(<StudentStepPanel step="site" hasSite={false} canRender={false} renderReason="Place a building first."
      onSite={onSite} onDesign={onDesign} onImage={vi.fn()} onVideo={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Confirm site & design' }));
    expect(onDesign).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Draw site boundary' }));
    expect(onSite).toHaveBeenCalledOnce();
  });
  it('explains unavailable capture without triggering either paid pipeline', async () => {
    const onImage = vi.fn(), onVideo = vi.fn();
    render(<StudentStepPanel step="present" hasSite canRender={false} renderReason="The scene is still saving."
      onSite={vi.fn()} onDesign={vi.fn()} onImage={onImage} onVideo={onVideo} />);
    expect(screen.getByRole('status')).toHaveTextContent('The scene is still saving.');
    fireEvent.click(screen.getByRole('button', { name: 'Image' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Video' }));
    expect(onImage).not.toHaveBeenCalled();
    expect(onVideo).not.toHaveBeenCalled();
  });
  it('keeps deferred video out of the classroom presentation controls', async () => {
    capabilities.mockResolvedValue({ video_enabled: false, classroom_release: true });
    render(<StudentStepPanel step="present" hasSite canRender renderReason=""
      onSite={vi.fn()} onDesign={vi.fn()} onImage={vi.fn()} onVideo={vi.fn()} />);
    expect(await screen.findByRole('button', { name: 'Image' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Video' })).toBeNull();
  });
  it('shows an access check before a concept render without blocking it', () => {
    const onImage = vi.fn();
    render(<StudentStepPanel step="present" hasSite canRender renderReason=""
      streetAccessNotice="No public-road connection is marked for this design."
      onSite={vi.fn()} onDesign={vi.fn()} onImage={onImage} onVideo={vi.fn()} />);
    expect(screen.getByRole('status')).toHaveTextContent('No public-road connection');
    fireEvent.click(screen.getByRole('button', { name: 'Image' }));
    expect(onImage).toHaveBeenCalledOnce();
  });
  it('routes a student to refresh a stale landscape before presentation', () => {
    const onSite = vi.fn();
    const boundary: SiteZone = {
      id: 'boundary', project_id: 'project', zone_type: 'site_boundary',
      coordinates: [[0, 0], [1, 0], [1, 1]], color: '#8ba65f', sort_order: 0,
      created_at: '', updated_at: '',
      properties: { community_3d_landscape: { state: 'stale' } },
    };
    expect(studentLandscapeNeedsRefresh(boundary)).toBe(true);
    expect(studentLandscapeNeedsRefresh({ ...boundary, properties: { community_3d_landscape: { state: 'compiled' } } })).toBe(false);
    render(<StudentStepPanel step="present" hasSite canRender renderReason=""
      landscapeNeedsRefresh={studentLandscapeNeedsRefresh(boundary)}
      onSite={onSite} onDesign={vi.fn()} onImage={vi.fn()} onVideo={vi.fn()} />);
    expect(screen.getByRole('status')).toHaveTextContent('site landscape needs a fresh preview');
    fireEvent.click(screen.getByRole('button', { name: 'Refresh site landscape' }));
    expect(onSite).toHaveBeenCalledOnce();
  });
  it('distinguishes an unmarked road from a marked route that still ends inside the site', () => {
    const boundary = { zone_type: 'site_boundary', coordinates: [[0,0],[1,0],[1,1],[0,1]] } as SiteZone;
    const street = { zone_type: 'road', coordinates: [[0.4,0.2],[0.6,0.2],[0.6,0.8],[0.4,0.8]], properties: {} } as SiteZone;
    expect(studentStreetAccessNotice([boundary], boundary)).toBeNull();
    expect(studentStreetAccessNotice([boundary, street], boundary)).toContain('No public-road connection is marked');
    expect(studentStreetAccessNotice([boundary, { ...street, properties: { connect_to_public_road: true } }], boundary))
      .toContain('short off-site route is not valid yet');
  });
});
