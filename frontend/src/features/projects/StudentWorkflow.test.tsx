import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { StudentStepPanel, StudentWorkflowNav } from './StudentWorkflow';

describe('student workflow', () => {
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
  it('explains unavailable capture without triggering either paid pipeline', () => {
    const onImage = vi.fn(), onVideo = vi.fn();
    render(<StudentStepPanel step="present" hasSite canRender={false} renderReason="The scene is still saving."
      onSite={vi.fn()} onDesign={vi.fn()} onImage={onImage} onVideo={onVideo} />);
    expect(screen.getByRole('status')).toHaveTextContent('The scene is still saving.');
    fireEvent.click(screen.getByRole('button', { name: 'Image' }));
    fireEvent.click(screen.getByRole('button', { name: 'Video' }));
    expect(onImage).not.toHaveBeenCalled();
    expect(onVideo).not.toHaveBeenCalled();
  });
});
