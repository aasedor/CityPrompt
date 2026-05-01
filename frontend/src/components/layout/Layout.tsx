import { useEffect, useRef, useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import {
  BarChart3,
  ChevronDown,
  Crown,
  KeyRound,
  LogIn,
  LogOut,
  Menu,
  MessageSquare,
  Shield,
  User,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/store';
import { TileTrail } from '@/components/ui/TileTrail';
import { ThemeToggle } from './ThemeToggle';

export function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const canAdmin = Boolean(user?.role && ['admin', 'cofounder'].includes(user.role));
  const canAnalytics = user?.role === 'cofounder';

  const navLinkClassName =
    'rounded-full px-3 py-2 text-xs font-black uppercase text-[#151515]/70 transition hover:bg-[#c9ff3d] hover:text-[#151515]';
  const mobileLinkClassName =
    'rounded-lg border-2 border-transparent px-3 py-2 text-sm font-black uppercase text-[#151515]/70 hover:border-[#151515] hover:bg-[#c9ff3d] hover:text-[#151515]';
  const menuItemClassName =
    'flex w-full items-center gap-2 px-4 py-2 text-sm font-black uppercase text-[#151515]/70 hover:bg-[#c9ff3d] hover:text-[#151515] dark:hover:text-[#151515]';

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false);
    setUserMenuOpen(false);
    navigate('/login');
  };

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
    <div className="relative min-h-screen overflow-x-hidden bg-[#fff9ec] text-[#151515]">
      <div
        className="pointer-events-none fixed inset-0 z-0 opacity-[0.22] dark:opacity-[0.34]"
        style={{
          backgroundImage:
            'linear-gradient(var(--city-grid-line) 2px, transparent 2px), linear-gradient(90deg, var(--city-grid-line) 2px, transparent 2px), linear-gradient(var(--city-grid-line) 1px, transparent 1px), linear-gradient(90deg, var(--city-grid-line) 1px, transparent 1px)',
          backgroundSize: '128px 128px, 128px 128px, 32px 32px, 32px 32px',
        }}
      />
      <TileTrail />

      <header className="relative z-[100] border-b-2 border-[#151515] bg-[#fff9ec]/95 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:h-16 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2">
            <img src="/images/city-prompt-logo.png" alt="City Prompt" className="h-9 w-9 dark:invert sm:h-10 sm:w-10" />
            <span className="text-sm font-black uppercase text-[#151515] sm:text-base">City Prompt</span>
          </Link>

          <nav className="hidden items-center gap-3 sm:flex">
            <Link to="/projects" className={navLinkClassName}>
              Projects
            </Link>
            {canAdmin && (
              <Link to="/admin" className={`flex items-center gap-1 ${navLinkClassName}`}>
                {user?.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {canAnalytics && (
              <Link to="/admin/analytics" className={`flex items-center gap-1 ${navLinkClassName}`}>
                <BarChart3 size={14} />
                Analytics
              </Link>
            )}

            {isAuthenticated && user && !canAdmin && (
              <div
                className={`flex items-center gap-1.5 rounded-full border-2 border-[#151515] px-3 py-1 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] ${
                  user.render_credits <= 0
                    ? 'bg-red-50 text-red-600'
                    : user.render_credits <= 100
                      ? 'bg-[#f2b84b] text-[#151515]'
                      : 'bg-[#c9ff3d] text-[#151515]'
                }`}
              >
                <svg viewBox="0 0 16 16" fill="currentColor" className="h-3.5 w-3.5">
                  <circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" strokeWidth="1.5" />
                  <text x="8" y="11.5" textAnchor="middle" fontSize="9" fontWeight="bold">
                    T
                  </text>
                </svg>
                {user.render_credits.toLocaleString()} tokens
              </div>
            )}

            <ThemeToggle />

            {isAuthenticated ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen((v) => !v)}
                  className="city-account-button flex max-w-[260px] items-center gap-1.5 rounded-full border-2 border-[#151515] bg-white px-3 py-1.5 text-xs font-black uppercase text-[#151515] shadow-[3px_3px_0_0_#151515] transition hover:bg-[#c9ff3d] hover:text-[#151515] dark:text-[#fff9ec] dark:hover:text-[#151515]"
                >
                  <User size={14} />
                  <span className="truncate">{user?.full_name || user?.email}</span>
                  <ChevronDown size={14} className={`shrink-0 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-lg border-2 border-[#151515] bg-white py-1 shadow-[8px_8px_0_0_#151515] backdrop-blur-xl animate-scale-in">
                    {canAdmin && (
                      <Link to="/admin" onClick={() => setUserMenuOpen(false)} className={menuItemClassName}>
                        {user?.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                        Admin Dashboard
                      </Link>
                    )}
                    {canAdmin && (
                      <Link to="/admin/feedback" onClick={() => setUserMenuOpen(false)} className={menuItemClassName}>
                        <MessageSquare size={14} />
                        Feedback Inbox
                      </Link>
                    )}
                    {canAnalytics && (
                      <Link to="/admin/analytics" onClick={() => setUserMenuOpen(false)} className={menuItemClassName}>
                        <BarChart3 size={14} />
                        Analytics
                      </Link>
                    )}
                    <Link to="/settings/password" onClick={() => setUserMenuOpen(false)} className={menuItemClassName}>
                      <KeyRound size={14} />
                      Change Password
                    </Link>
                    <div className="my-1 border-t-2 border-[#151515]" />
                    <button onClick={handleLogout} className={menuItemClassName}>
                      <LogOut size={14} />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-1 rounded-full border-2 border-[#151515] bg-white px-3 py-1.5 text-xs font-black uppercase text-[#151515] shadow-[3px_3px_0_0_#151515] transition hover:bg-[#c9ff3d]"
              >
                <LogIn size={14} />
                Sign in
              </Link>
            )}
          </nav>

          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="rounded-full border-2 border-[#151515] bg-white p-2 text-[#151515] shadow-[3px_3px_0_0_#151515] transition hover:bg-[#c9ff3d] sm:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="border-t-2 border-[#151515] bg-[#fff9ec]/95 px-4 pb-4 pt-2 backdrop-blur-xl sm:hidden">
            <Link to="/projects" onClick={() => setMobileMenuOpen(false)} className={`block ${mobileLinkClassName}`}>
              Projects
            </Link>
            {canAdmin && (
              <Link to="/admin" onClick={() => setMobileMenuOpen(false)} className={`flex items-center gap-1 ${mobileLinkClassName}`}>
                {user?.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {canAnalytics && (
              <Link
                to="/admin/analytics"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-1 ${mobileLinkClassName}`}
              >
                <BarChart3 size={14} />
                Analytics
              </Link>
            )}
            {isAuthenticated ? (
              <>
                <ThemeToggle className="mb-2 w-max" />
                <div className="flex items-center gap-1.5 px-3 py-2 text-sm font-black text-[#151515]/60">
                  <User size={14} />
                  {user?.full_name || user?.email}
                </div>
                <Link
                  to="/settings/password"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-2 ${mobileLinkClassName}`}
                >
                  <KeyRound size={14} />
                  Change Password
                </Link>
                <button onClick={handleLogout} className={`flex w-full items-center gap-2 ${mobileLinkClassName}`}>
                  <LogOut size={14} />
                  Sign out
                </button>
              </>
            ) : (
              <>
                <ThemeToggle className="mb-2 mt-1 w-max" />
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-1 ${mobileLinkClassName}`}
                >
                  <LogIn size={14} />
                  Sign in
                </Link>
              </>
            )}
          </div>
        )}
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
