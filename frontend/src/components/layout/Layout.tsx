import { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { BarChart3, Box, ChevronDown, Crown, KeyRound, LogIn, LogOut, Shield, User, Menu, X, Sun, Moon, Monitor } from 'lucide-react';
import { useThemeStore } from '@/store/themeStore';
import { useAuthStore } from '@/store';

export function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { theme, setTheme } = useThemeStore();
  const userMenuRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false);
    setUserMenuOpen(false);
    navigate('/login');
  };

  // Close desktop dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    if (userMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [userMenuOpen]);

  return (
    <div className="min-h-screen">
      <header className="relative border-b border-primary-950/[0.06] bg-accent-50/80 backdrop-blur-xl dark:border-white/[0.06] dark:bg-primary-950/80">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:h-16 sm:px-6 lg:px-8">
          <Link to="/projects" className="flex items-center gap-2">
            <Box className="h-7 w-7 text-coral-500 sm:h-8 sm:w-8" />
            <span className="text-lg font-bold text-primary-950 dark:text-accent-50 sm:text-xl">SiteForge</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-4 sm:flex">
            <Link to="/projects" className="text-sm font-medium text-primary-950/60 dark:text-white/60 transition-colors hover:text-primary-950 dark:hover:text-white">
              Projects
            </Link>
            {user?.role && ['admin', 'cofounder'].includes(user.role) && (
              <Link to="/admin" className="flex items-center gap-1 text-sm font-medium text-primary-950/60 dark:text-white/60 transition-colors hover:text-primary-950 dark:hover:text-white">
                {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {user?.role === 'cofounder' && (
              <Link to="/admin/analytics" className="flex items-center gap-1 text-sm font-medium text-primary-950/60 transition-colors hover:text-primary-950">
                <BarChart3 size={14} />
                Analytics
              </Link>
            )}
            {/* Theme toggle */}
            <div className="flex items-center rounded-lg border border-primary-950/[0.06] dark:border-white/[0.06]">
              <button
                onClick={() => setTheme('light')}
                className={`rounded-l-lg p-1.5 transition-colors ${theme === 'light' ? 'bg-primary-950/[0.06] text-primary-950 dark:bg-white/[0.1] dark:text-white' : 'text-primary-950/40 hover:text-primary-950 dark:text-white/40 dark:hover:text-white'}`}
                title="Light mode"
              >
                <Sun size={14} />
              </button>
              <button
                onClick={() => setTheme('system')}
                className={`p-1.5 transition-colors ${theme === 'system' ? 'bg-primary-950/[0.06] text-primary-950 dark:bg-white/[0.1] dark:text-white' : 'text-primary-950/40 hover:text-primary-950 dark:text-white/40 dark:hover:text-white'}`}
                title="System theme"
              >
                <Monitor size={14} />
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`rounded-r-lg p-1.5 transition-colors ${theme === 'dark' ? 'bg-primary-950/[0.06] text-primary-950 dark:bg-white/[0.1] dark:text-white' : 'text-primary-950/40 hover:text-primary-950 dark:text-white/40 dark:hover:text-white'}`}
                title="Dark mode"
              >
                <Moon size={14} />
              </button>
            </div>

            {isAuthenticated ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen((v) => !v)}
                  className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-primary-950/60 dark:text-white/60 transition-colors hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                >
                  <User size={14} />
                  {user?.full_name || user?.email}
                  <ChevronDown size={14} className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 z-50 mt-2 w-48 rounded-xl border border-primary-950/[0.08] dark:border-white/[0.08] bg-white dark:bg-primary-900 py-1 shadow-elevated backdrop-blur-xl animate-scale-in">
                    {user?.role && ['admin', 'cofounder'].includes(user.role) && (
                      <Link
                        to="/admin"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                      >
                        {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                        Admin Dashboard
                      </Link>
                    )}
                    {user?.role === 'cofounder' && (
                      <Link
                        to="/admin/analytics"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                      >
                        <BarChart3 size={14} />
                        Analytics
                      </Link>
                    )}
                    <Link
                      to="/settings/password"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                    >
                      <KeyRound size={14} />
                      Change Password
                    </Link>
                    <div className="my-1 border-t border-primary-950/[0.06] dark:border-white/[0.06]" />
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                    >
                      <LogOut size={14} />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-1 rounded-lg border border-primary-950/[0.1] dark:border-white/[0.1] px-3 py-1.5 text-sm font-medium text-primary-950/70 dark:text-white/70 transition-colors hover:bg-primary-950/[0.04]"
              >
                <LogIn size={14} />
                Sign in
              </Link>
            )}
          </nav>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="rounded-lg p-2 text-primary-950/60 dark:text-white/60 transition-colors hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white sm:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="border-t border-primary-950/[0.06] dark:border-white/[0.06] bg-accent-50/95 dark:bg-primary-950/95 px-4 pb-4 pt-2 backdrop-blur-xl sm:hidden">
            <Link
              to="/projects"
              onClick={() => setMobileMenuOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
            >
              Projects
            </Link>
            {user?.role && ['admin', 'cofounder'].includes(user.role) && (
              <Link
                to="/admin"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
              >
                {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {user?.role === 'cofounder' && (
              <Link
                to="/admin/analytics"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
              >
                <BarChart3 size={14} />
                Analytics
              </Link>
            )}
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-1.5 px-3 py-2 text-sm text-primary-950/40 dark:text-white/40">
                  <User size={14} />
                  {user?.full_name || user?.email}
                </div>
                <Link
                  to="/settings/password"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                >
                  <KeyRound size={14} />
                  Change Password
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-primary-950/60 dark:text-white/60 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.06] hover:text-primary-950 dark:hover:text-white"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </>
            ) : (
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="mt-1 flex items-center gap-1 rounded-lg border border-primary-950/[0.1] px-3 py-2 text-sm font-medium text-primary-950/70 hover:bg-primary-950/[0.04]"
              >
                <LogIn size={14} />
                Sign in
              </Link>
            )}
          </div>
        )}
        {/* Glow accent line */}
        <div className="absolute inset-x-0 bottom-0 glow-line" />
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
