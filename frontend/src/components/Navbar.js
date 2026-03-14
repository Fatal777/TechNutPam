import { Link, useLocation } from 'react-router-dom';
import { Shield, Menu, X } from 'lucide-react';
import { useState } from 'react';
import ThemeToggle from './ThemeToggle';

const navLinks = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/reports', label: 'Reports' },
  { path: '/pricing', label: 'Pricing' },
];

export default function Navbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isDashboard = location.pathname === '/dashboard';

  return (
    <nav
      data-testid="navbar"
      className={`sticky top-0 z-50 border-b transition-colors duration-300 ${
        isDashboard
          ? 'bg-slate-900 border-slate-800 text-white'
          : 'bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-slate-200 dark:border-slate-800'
      }`}
    >
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2.5 group" data-testid="nav-logo">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
              isDashboard ? 'bg-emerald-500/20' : 'bg-primary/10 dark:bg-primary/20'
            }`}>
              <Shield size={20} className={isDashboard ? 'text-emerald-400' : 'text-primary'} />
            </div>
            <span className={`font-heading font-bold text-lg ${
              isDashboard ? 'text-white' : 'text-slate-900 dark:text-white'
            }`}>
              ComplianceShield
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navLinks.map(link => (
              <Link
                key={link.path}
                to={link.path}
                data-testid={`nav-link-${link.label.toLowerCase()}`}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  location.pathname === link.path
                    ? isDashboard
                      ? 'bg-white/10 text-white'
                      : 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-blue-400'
                    : isDashboard
                      ? 'text-slate-400 hover:text-white hover:bg-white/5'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            {!isDashboard && <ThemeToggle />}
            <button
              data-testid="mobile-menu-btn"
              className="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 py-3 space-y-1">
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileOpen(false)}
              className={`block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === link.path
                  ? 'bg-primary/10 text-primary'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              {link.label}
            </Link>
          ))}
          <div className="pt-2 px-4">
            <ThemeToggle />
          </div>
        </div>
      )}
    </nav>
  );
}
