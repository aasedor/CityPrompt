import { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Box, ChevronDown, Crown, KeyRound, LogIn, LogOut, Shield, User, Menu, X } from 'lucide-react';
import { useAuthStore } from '@/store';

export function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
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
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:h-16 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2">
            <Box className="h-7 w-7 text-primary-600 sm:h-8 sm:w-8" />
            <span className="text-lg font-bold text-gray-900 sm:text-xl">3D Dev Platform</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-4 sm:flex">
            <Link to="/" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Projects
            </Link>
            {user?.role && ['admin', 'cofounder'].includes(user.role) && (
              <Link to="/admin" className="flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-gray-900">
                {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {isAuthenticated ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen((v) => !v)}
                  className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100"
                >
                  <User size={14} />
                  {user?.full_name || user?.email}
                  <ChevronDown size={14} className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 z-50 mt-1 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                    {user?.role && ['admin', 'cofounder'].includes(user.role) && (
                      <Link
                        to="/admin"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                        Admin Dashboard
                      </Link>
                    )}
                    <Link
                      to="/settings/password"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <KeyRound size={14} />
                      Change Password
                    </Link>
                    <div className="my-1 border-t border-gray-100" />
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
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
                className="flex items-center gap-1 rounded-lg bg-primary-50 px-3 py-1.5 text-sm font-medium text-primary-700 hover:bg-primary-100"
              >
                <LogIn size={14} />
                Sign in
              </Link>
            )}
          </nav>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 sm:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="border-t border-gray-100 bg-white px-4 pb-4 pt-2 sm:hidden">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
            >
              Projects
            </Link>
            {user?.role && ['admin', 'cofounder'].includes(user.role) && (
              <Link
                to="/admin"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
              >
                {user.role === 'cofounder' ? <Crown size={14} /> : <Shield size={14} />}
                Admin
              </Link>
            )}
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600">
                  <User size={14} />
                  {user?.full_name || user?.email}
                </div>
                <Link
                  to="/settings/password"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
                >
                  <KeyRound size={14} />
                  Change Password
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </>
            ) : (
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="mt-1 flex items-center gap-1 rounded-lg bg-primary-50 px-3 py-2 text-sm font-medium text-primary-700 hover:bg-primary-100"
              >
                <LogIn size={14} />
                Sign in
              </Link>
            )}
          </div>
        )}
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
