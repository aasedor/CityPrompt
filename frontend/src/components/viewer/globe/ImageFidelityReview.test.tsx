import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { ImageFidelityReview, imageFidelityStatus } from './ImageFidelityReview';
import type { Direct3DRenderDiagnostics } from './useDirect3DRender';
afterEach(cleanup);
it('fails closed on an explicit fallback, distinguishes missing evidence and all passed checks', () => {
  const passed = {processing_mode:'scene',macro_design_fidelity:{passed:true},instance_source_presence:{passed:true},unsupported_structure:{passed:true}} as Direct3DRenderDiagnostics;
  expect(imageFidelityStatus(passed)).toBe('passed');
  expect(imageFidelityStatus({...passed,returned_safety_strategy:'authoritative_source'})).toBe('failed');
  expect(imageFidelityStatus({...passed,instance_source_presence:undefined})).toBe('review');
  expect(imageFidelityStatus({...passed,processing_mode:'reproject'})).toBe('review');
});
it('explains a failed finish without declaring it ready or retrying it', () => {
  const onOriginal=vi.fn();render(<ImageFidelityReview status="failed" warnings={['Structure changed']} onOriginal={onOriginal} />);
  expect(screen.getByRole('alert').textContent).toContain('AI finish failed design checks');
  expect(screen.getByRole('alert').textContent).toContain('Showing your original 3D view');
  expect(screen.getByRole('alert').textContent).not.toContain('ready to use');
  expect(onOriginal).not.toHaveBeenCalled();fireEvent.click(screen.getByRole('button',{name:'Inspect unverified AI original'}));expect(onOriginal).toHaveBeenCalledOnce();
});
