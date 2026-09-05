import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useViewerStore } from '@/store';
import { SitePlannerToolbar } from './SitePlannerToolbar';
import { CALGARY_LOCAL_PLACEMENT } from '@/features/pickPlace/streetPlacement';

describe('Student drawing toolbar', () => {
  it('selects the sourced 16 m street before the first route point is drawn', () => {
    render(<SitePlannerToolbar placementSlot={<span>Objects</span>} streetPlacement={CALGARY_LOCAL_PLACEMENT} />);
    fireEvent.click(screen.getByRole('button', {name:'Calgary local street'}));
    expect(useViewerStore.getState().activeToolProperties).toMatchObject({width:16,road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0'});
    expect(screen.getByText(/based on a draft Street Manual/)).toBeInTheDocument();
  });
  beforeEach(() => useViewerStore.setState({ activeSitePlannerTool: null, streetViewPegman: null }));
  it('starts with building, park and road, keeping optional tools available', () => {
    const boundary = vi.fn();
    render(<SitePlannerToolbar onSiteBoundary={boundary} onMasterPlan={vi.fn()} isGlobeMode />);
    expect(screen.getByRole('button', { name: 'Building' })).toHaveAttribute('data-tour', 'tool-buildings');
    expect(screen.getByRole('button', { name: 'Park' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Road' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Site Boundary' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'More Tools' }));
    expect(screen.getByRole('button', { name: 'More Tools' })).toHaveAttribute('aria-expanded', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'Site Boundary' }));
    expect(boundary).toHaveBeenCalledOnce();
    expect(screen.getByRole('button', { name: 'Master Plan' })).toBeInTheDocument();
  });
  it('switches drawing modes and keeps Select reachable with clear completion instructions', () => {
    const measure = vi.fn();
    render(<SitePlannerToolbar onMeasureModeChange={measure} layout="sidebar" isGlobeMode />);
    fireEvent.click(screen.getByRole('button', { name: 'Building' }));
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('building');
    expect(screen.getByRole('status')).toHaveTextContent('at least 3 corners');
    expect(screen.getByRole('status')).toHaveTextContent('Enter');
    fireEvent.click(screen.getByRole('button', { name: 'Park' }));
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('green_space');
    fireEvent.click(screen.getByRole('button', { name: 'Road' }));
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('road');
    expect(screen.getByRole('status')).toHaveTextContent('at least 2 points');
    fireEvent.click(screen.getByRole('button', { name: 'Select' }));
    expect(useViewerStore.getState().activeSitePlannerTool).toBeNull();
    expect(measure).toHaveBeenLastCalledWith(false);
  });
  it('clears street view before an optional drawing tool and reflects an externally selected plaza', () => {
    render(<SitePlannerToolbar />);
    fireEvent.click(screen.getByRole('button', { name: 'More Tools' }));
    fireEvent.click(screen.getByRole('button', { name: 'Street View' }));
    expect(useViewerStore.getState().streetViewPegman).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Water' }));
    expect(useViewerStore.getState().streetViewPegman).toBeNull();
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('water');
    act(() => useViewerStore.setState({ activeSitePlannerTool: 'parking' }));
    expect(screen.getByRole('button', { name: 'Plaza' })).toHaveAttribute('aria-pressed', 'true');
  });
});
