import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { LocalAreaPlanPanel } from './LocalAreaPlanPanel';
import { PolicyDetailsCard } from './PolicyDetailsCard';
import { useLocalAreaPolicy } from './useLocalAreaPolicy';
import { LOCAL_AREA_PLANS, loadLocalAreaPlan, localAreaPlan } from './localAreaPlans';
import type { PolicySnapshot } from './rileyPolicy';

vi.mock('./localAreaPlans', async original => ({ ...await original<object>(), loadLocalAreaPlan: vi.fn() }));
const site = (x: number, y: number) => ({ id:'site', zone_type:'site_boundary', is_active_boundary:true, properties:{}, coordinates:[[x-.001,y-.001],[x+.001,y-.001],[x+.001,y+.001],[x-.001,y+.001]] }) as SiteZone;
const riley = site(-114.10,51.056);
const chinook = site(-114.0813912,51.0087248);
function App({ zones = [riley], project = 'one' }: { zones?: SiteZone[]; project?: string }) {
  const state = useLocalAreaPolicy(project, zones);
  return <><LocalAreaPlanPanel state={state} /><PolicyDetailsCard selected={state.selected} onClose={state.clearSelection} />
    <output data-testid="geometry">{state.data?.districts[0]?.id ?? 'none'}</output></>;
}
function setup() {
  const client = new QueryClient({ defaultOptions:{ queries:{ retry:false } } });
  return (props: Parameters<typeof App>[0] = {}) => <QueryClientProvider client={client}><App {...props} /></QueryClientProvider>;
}
beforeEach(async () => {
  localStorage.clear(); vi.clearAllMocks();
  const actual = await vi.importActual<typeof import('./localAreaPlans')>('./localAreaPlans');
  vi.mocked(loadLocalAreaPlan).mockImplementation(actual.loadLocalAreaPlan);
});

describe('local area plan workflow', () => {
  it('loads only the enabled selection and opens each plan’s own explanations and PDF pages', async () => {
    render(setup()());
    expect(loadLocalAreaPlan).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('switch'));
    await screen.findByText('Urban form legend');
    for (const plan of LOCAL_AREA_PLANS) {
      fireEvent.change(screen.getByRole('combobox'), { target:{ value:plan.id } });
      await waitFor(() => expect(screen.getByTestId('geometry')).toHaveTextContent(`${plan.id}-urban-form`));
      fireEvent.click(screen.getByRole('button', { name:'About Neighbourhood Flex' }));
      const card = screen.getByRole('region', { name:'Neighbourhood Flex' });
      expect(card).toHaveFocus();
      const definition = plan.designations.find(d => d.name === 'Neighbourhood Flex')!;
      expect(screen.getByRole('link', { name:/^Read section/ })).toHaveAttribute('href', `${plan.source}#page=${definition.pdfPage}`);
      expect(card).toHaveTextContent(`approved ${plan.name} plan`);
      fireEvent.keyDown(card, { key:'Escape' });
    }
    expect(loadLocalAreaPlan).toHaveBeenCalledTimes(8);
  });
  it('follows a moved site automatically, clears old selections and prevents stale geometry on deletion', async () => {
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByRole('switch')); await screen.findByText('Urban form legend');
    fireEvent.click(screen.getByRole('button', { name:'About Neighbourhood Flex' }));
    rerender(view({ zones:[chinook] }));
    expect(screen.queryByRole('region', { name:'Neighbourhood Flex' })).not.toBeInTheDocument();
    await waitFor(() => expect(screen.getByTestId('geometry')).toHaveTextContent('chinook-'));
    rerender(view({ zones:[] }));
    expect(screen.getByTestId('geometry')).toHaveTextContent('none');
    expect(screen.getByText(/Draw a site boundary/)).toBeInTheDocument();
    rerender(view({ project:'two' }));
    expect(screen.getByRole('switch')).not.toBeChecked();
  });
  it('does not let a late download paint or relabel a newly selected plan', async () => {
    let finish!: (data: PolicySnapshot) => void;
    vi.mocked(loadLocalAreaPlan).mockImplementationOnce(() => new Promise(resolve => { finish=resolve; }));
    render(setup()()); fireEvent.click(screen.getByRole('switch'));
    fireEvent.change(screen.getByRole('combobox'), { target:{ value:'chinook' } });
    await waitFor(() => expect(screen.getByTestId('geometry')).toHaveTextContent('chinook-'));
    const actual = await vi.importActual<typeof import('./localAreaPlans')>('./localAreaPlans');
    finish(await actual.loadLocalAreaPlan('riley'));
    await waitFor(() => expect(screen.getByRole('switch')).toHaveAccessibleName('Show Chinook policy map'));
    expect(screen.getByTestId('geometry')).toHaveTextContent('chinook-');
  });
  it('explains manual browsing outside a site, clips to nothing, and persists the selected plan and opacity', async () => {
    const view = setup(); const { unmount } = render(view());
    fireEvent.change(screen.getByRole('combobox'), { target:{ value:'heritage' } });
    expect(loadLocalAreaPlan).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('switch'));
    await screen.findByText(/Browsing Heritage/);
    fireEvent.click(screen.getByRole('button', { name:'About Natural Areas' }));
    fireEvent.change(screen.getByRole('slider'), { target:{ value:'0' } });
    expect(screen.queryByRole('region', { name:'Natural Areas' })).not.toBeInTheDocument();
    fireEvent.change(screen.getByRole('slider'), { target:{ value:'45' } });
    fireEvent.click(screen.getByLabelText('Only show inside my site'));
    expect(screen.getByText(/This plan has no coverage inside your site/)).toBeInTheDocument();
    expect(screen.getByTestId('geometry')).toHaveTextContent('none');
    unmount(); render(view());
    expect(screen.getByRole('combobox')).toHaveValue('heritage');
    expect(screen.getByRole('slider')).toHaveValue('45');
    expect(screen.getByLabelText('Only show inside my site')).toBeChecked();
    expect(localAreaPlan('heritage')).toBeDefined();
  });
});
