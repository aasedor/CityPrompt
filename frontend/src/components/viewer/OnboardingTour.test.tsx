import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { OnboardingTour } from './OnboardingTour';

describe('Quick-start guide', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() })));
  });
  it('follows drawing to 3D to render without triggering a generation', () => {
    const renderAction = vi.fn();
    const finish = vi.fn();
    render(<><button data-tour="generate-3d-btn" onClick={renderAction}>Generate 3D</button><button data-tour="ai-render-btn" onClick={renderAction}>AI Render</button><OnboardingTour forceShow onComplete={finish} /></>);
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Start with one building');
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Add a park');
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Connect places with a road');
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Build your 3D scene');
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Create a presentation image');
    fireEvent.click(screen.getByRole('button', { name: 'Start drawing' }));
    expect(finish).toHaveBeenCalledOnce();
    expect(renderAction).not.toHaveBeenCalled();
  });
  it('contains keyboard focus, makes Enter operate only the focused button, and restores focus', async () => {
    const user = userEvent.setup();
    const backgroundKey = vi.fn();
    window.addEventListener('keydown', backgroundKey);
    const opener = document.createElement('button');
    document.body.append(opener);
    opener.focus();
    const { unmount } = render(<OnboardingTour forceShow />);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveFocus();
    await user.tab({ shift: true });
    expect(screen.getByRole('button', { name: 'Next' })).toHaveFocus();
    await user.keyboard('{Enter}');
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Add a park');
    screen.getByRole('button', { name: 'Back' }).focus();
    await user.keyboard('{Enter}');
    expect(screen.getByRole('dialog')).toHaveAccessibleName('Start with one building');
    await user.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(backgroundKey).not.toHaveBeenCalled();
    expect(opener).toHaveFocus();
    unmount(); opener.remove(); window.removeEventListener('keydown', backgroundKey);
  });
  it('stays closed when not requested and remains usable without a visible tour target', () => {
    const { rerender } = render(<OnboardingTour forceShow={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    rerender(<OnboardingTour forceShow />);
    expect(screen.getByRole('dialog')).toBeVisible();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close guide' }));
    expect(localStorage.getItem('onboarding-tour-completed')).toBe('true');
  });
});
