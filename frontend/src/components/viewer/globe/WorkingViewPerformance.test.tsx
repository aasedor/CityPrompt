import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { WorkingViewPerformance } from './WorkingViewPerformance';
import { useWorkingViewQuality, WORKING_VIEW_QUALITY_KEY } from './useWorkingViewQuality';

afterEach(() => {cleanup(); localStorage.removeItem(WORKING_VIEW_QUALITY_KEY); vi.restoreAllMocks();});
function Settings() {
  const {quality, changeQuality, dpr} = useWorkingViewQuality();
  return <><output aria-label="Pixel range">{dpr.join(',')}</output><WorkingViewPerformance quality={quality} onQuality={changeQuality} onOpen={vi.fn()} stats={null} /></>;
}
it('defaults to a bounded working view, persists explicit choices, and restores focus', () => {
  const {unmount} = render(<Settings />);
  expect(screen.getByLabelText('Pixel range')).toHaveTextContent('1,1.5');
  const opener = screen.getByRole('button', {name:'3D detail · Balanced'}); opener.focus(); fireEvent.click(opener);
  fireEvent.change(screen.getByRole('combobox', {name:'Working view detail'}), {target:{value:'economy'}});
  expect(screen.getByLabelText('Pixel range')).toHaveTextContent('1,1');
  expect(localStorage.getItem(WORKING_VIEW_QUALITY_KEY)).toBe('economy');
  expect(screen.getByText(/Choose High before capturing/)).toBeInTheDocument();
  fireEvent.keyDown(document, {key:'Escape'});
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument(); expect(opener).toHaveFocus();
  unmount(); render(<Settings />); expect(screen.getByRole('button', {name:'3D detail · Economy'})).toBeInTheDocument();
});
it('recovers from invalid or unavailable storage and keeps preference changes usable', () => {
  localStorage.setItem(WORKING_VIEW_QUALITY_KEY, 'broken');
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {throw new Error('Storage denied');});
  render(<Settings />);
  fireEvent.click(screen.getByRole('button', {name:'3D detail · Balanced'}));
  fireEvent.change(screen.getByRole('combobox', {name:'Working view detail'}), {target:{value:'high'}});
  expect(screen.getByLabelText('Pixel range')).toHaveTextContent('1,2');
});
it('shows supplied live measurements only in the open dialog', () => {
  render(<WorkingViewPerformance quality="balanced" onQuality={vi.fn()} onOpen={vi.fn()} stats={{fps:42,frameMs:24,drawCalls:100,triangles:2000,width:1200,height:800}} />);
  expect(screen.queryByLabelText('Live 3D performance')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name:'3D detail · Balanced'}));
  expect(screen.getByLabelText('Live 3D performance')).toHaveTextContent('42 frames/s');
  expect(screen.getByLabelText('Live 3D performance')).toHaveTextContent('1200 × 800');
});
