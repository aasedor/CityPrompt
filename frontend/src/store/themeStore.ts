import { create } from 'zustand';

type Theme = 'light' | 'dark' | 'system';

function getEffective(theme: Theme): 'light' | 'dark' {
  if (theme === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return theme;
}

function apply(theme: Theme) {
  const effective = getEffective(theme);
  document.documentElement.classList.toggle('dark', effective === 'dark');
  localStorage.setItem('siteforge-theme', theme);
}

interface ThemeState {
  theme: Theme;
  effective: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
}

const stored = (localStorage.getItem('siteforge-theme') as Theme) || 'light';

export const useThemeStore = create<ThemeState>((set) => ({
  theme: stored,
  effective: getEffective(stored),
  setTheme: (theme) => {
    apply(theme);
    set({ theme, effective: getEffective(theme) });
  },
}));

// Apply on load
apply(stored);

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const { theme } = useThemeStore.getState();
    if (theme === 'system') {
      apply(theme);
      useThemeStore.setState({ effective: getEffective(theme) });
    }
  });
}
