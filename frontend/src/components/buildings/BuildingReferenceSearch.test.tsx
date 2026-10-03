// @vitest-environment jsdom
import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { BuildingReferenceSearch } from './BuildingReferenceSearch';

const search = vi.hoisted(() => vi.fn());
vi.mock('@/services/api', () => ({ buildingsApi: { searchPhotoReferences: search } }));
afterEach(() => { cleanup(); vi.resetAllMocks(); });
const candidate = { id: 'one', title: 'Hall rear', image_url: 'https://upload.wikimedia.org/a.jpg',
  source_url: 'https://commons.wikimedia.org/wiki/File:Hall.jpg', author: 'Author', license: 'CC0', license_url: '', description: '' };

test('search is optional and selection preserves the source while enforcing capacity', async () => {
  search.mockResolvedValue({ candidates: [candidate, { ...candidate, id: 'two', title: 'Hall roof' }] });
  const onChange = vi.fn();
  const props = { buildingId: 'b', selected: [], onChange, capacity: 1, disabled: false };
  const component = render(<BuildingReferenceSearch {...props} />);
  fireEvent.click(screen.getByText('Find more views online (optional)'));
  fireEvent.change(screen.getByLabelText('Building name'), { target: { value: 'Concert Hall' } });
  fireEvent.change(screen.getByLabelText('Reference viewing angle'), { target: { value: 'rear' } });
  fireEvent.click(screen.getByRole('button', { name: 'Find views' }));
  await waitFor(() => expect(screen.getByLabelText('Use Hall rear')).toBeTruthy());
  expect(search).toHaveBeenCalledWith('b', 'Concert Hall', 'rear');
  fireEvent.click(screen.getByLabelText('Use Hall rear'));
  expect(onChange).toHaveBeenCalledWith([candidate]);
  component.rerender(<BuildingReferenceSearch {...props} selected={[candidate]} />);
  expect((screen.getByLabelText('Use Hall roof') as HTMLInputElement).disabled).toBe(true);
  expect((screen.getByLabelText('Use Hall rear') as HTMLInputElement).disabled).toBe(false);
  expect(screen.getAllByRole('link')[0].getAttribute('href')).toBe(candidate.source_url);
});

test('search failure is recoverable without changing selection', async () => {
  search.mockRejectedValue(new Error('offline'));
  const onChange = vi.fn();
  render(<BuildingReferenceSearch buildingId="b" selected={[]} onChange={onChange} capacity={4} disabled={false} />);
  fireEvent.click(screen.getByText('Find more views online (optional)'));
  fireEvent.change(screen.getByLabelText('Building name'), { target: { value: 'Concert Hall' } });
  fireEvent.click(screen.getByRole('button', { name: 'Find views' }));
  await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('unavailable'));
  expect(onChange).not.toHaveBeenCalled();
  expect((screen.getByRole('button', { name: 'Find views' }) as HTMLButtonElement).disabled).toBe(false);
});
