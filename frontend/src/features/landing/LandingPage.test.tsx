import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LandingPage } from './LandingPage';
import { useAuthStore } from '@/store';
import { authApi } from '@/services/api';
vi.mock('@/services/api', () => ({ authApi: { login: vi.fn(), me: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));
function setup() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter><Routes><Route path="/" element={<LandingPage />} /><Route path="/projects" element={<h1>Saved projects</h1>} /></Routes></MemoryRouter></QueryClientProvider>);
}
beforeEach(() => { vi.clearAllMocks(); useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false }); });
describe('student landing page', () => {
  it('shows the requested course text and a working inline login without the redundant project CTA', () => {
    setup();
    expect(screen.getByText('City Prompt is a tool to help you understand, build and visualize your final project for Urban Studies 451.')).toBeDefined();
    expect(screen.queryByRole('link', { name: /^open your project/i })).toBeNull();
    expect(screen.getByLabelText('Email')).toHaveProperty('disabled', false);
    expect(screen.getByLabelText('Password')).toHaveProperty('disabled', false);
  });
  it('uses the existing login flow and opens projects after successful sign-in', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'test', refresh_token: 'test-refresh', token_type: 'bearer', user: { id: 'test', email: 'student@example.com', full_name: 'Student', role: 'editor', is_active: true, render_credits: 0, created_at: '2026-10-09T00:00:00Z' } });
    setup(); const user = userEvent.setup();
    await user.type(screen.getByLabelText('Email'), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'test-password');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Saved projects' })).toBeDefined());
    expect(authApi.login).toHaveBeenCalledWith('student@example.com', 'test-password');
  });
  it('keeps a failed login on the page with feedback', async () => {
    vi.mocked(authApi.login).mockRejectedValue({ response: { data: { detail: 'Invalid credentials' } } });
    setup(); const user = userEvent.setup();
    await user.type(screen.getByLabelText('Email'), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'wrong-password');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByText('Invalid credentials')).toBeDefined());
    expect(screen.getByLabelText('Email')).toBeDefined();
  });
  it('provides a real projects link for an existing signed-in session', () => {
    useAuthStore.setState({ isAuthenticated: true }); setup();
    expect(screen.getByRole('link', { name: 'Continue to projects' }).getAttribute('href')).toBe('/projects');
    expect(screen.queryByLabelText('Password')).toBeNull();
  });
});
