import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LandingPage } from './LandingPage';
import { useAuthStore } from '@/store';
import { authApi } from '@/services/api';

vi.mock('@/services/api', () => ({ authApi: { login: vi.fn(), me: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

const destination = '/projects/requested?tab=design#walk';
const signup = '/register?returnTo=%2Fprojects%2Frequested%3Ftab%3Ddesign%23walk';

function Destination() {
  const location = useLocation();
  return <h1>{location.pathname}{location.search}{location.hash}</h1>;
}

function setup(source: 'state' | 'query' = 'state') {
  window.history.replaceState(source === 'state'
    ? { usr: { from: { pathname: '/projects/requested', search: '?tab=design', hash: '#walk' } }, key: 'login', idx: 0 }
    : null, '', source === 'state' ? '/login' : '/login?returnTo=%2Fprojects%2Frequested%3Ftab%3Ddesign%23walk');
  render(<QueryClientProvider client={new QueryClient()}><BrowserRouter><Routes>
    <Route path="/login" element={<LandingPage />} />
    <Route path="/projects/:id" element={<Destination />} />
  </Routes></BrowserRouter></QueryClientProvider>);
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
});
afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  sessionStorage.clear();
  window.history.replaceState(null, '', '/');
});

it.each(['state', 'query'] as const)('preserves the %s destination while navigating landing sections', async source => {
  setup(source);
  const user = userEvent.setup();
  for (const [name, hash] of [
    ['Skip to content', '#main-content'], ['Project steps', '#how-it-works'],
    ['See the context', '#perspectives'], ['Sign in', '#studio'],
    ['Start with the steps ↓', '#how-it-works'], ['Sign in to City Prompt ↗', '#studio'],
    ['Back to project steps ↑', '#how-it-works'],
  ]) {
    await user.click(screen.getByRole('link', { name }));
    await waitFor(() => expect(window.location.hash).toBe(hash));
    expect(screen.getByRole('link', { name: 'Sign up' }).getAttribute('href')).toBe(signup);
    expect(document.activeElement?.id).toBe(hash.slice(1));
  }
});

it.each(['password', 'Google', 'signup'] as const)('keeps the project for %s after clicking Sign in', async flow => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
  vi.mocked(authApi.login).mockResolvedValue({ access_token: 'test', refresh_token: 'test-refresh', token_type: 'bearer', user: { id: 'test', email: 'student@example.com', full_name: 'Student', role: 'editor', is_active: true, render_credits: 0, created_at: '2026-10-09T00:00:00Z' } });
  setup();
  const user = userEvent.setup();
  await user.click(screen.getByRole('link', { name: 'Sign in' }));
  await waitFor(() => expect(window.location.hash).toBe('#studio'));
  if (flow === 'signup') {
    expect(screen.getByRole('link', { name: 'Sign up' }).getAttribute('href')).toBe(signup);
  } else if (flow === 'Google') {
    await user.click(screen.getByRole('button', { name: 'Continue with Google' }));
    expect(localStorage.getItem('oauth_return_to')).toBe(destination);
    await waitFor(() => expect(screen.getByRole('button', { name: 'Continue with Google' })).toHaveProperty('disabled', false));
  } else {
    await user.type(screen.getByLabelText('Email'), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'test-password');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByRole('heading', { name: destination })).toBeDefined());
  }
});
