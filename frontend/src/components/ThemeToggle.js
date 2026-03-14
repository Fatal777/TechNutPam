import { useTheme } from './ThemeContext';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const { isDark, toggle } = useTheme();
  return (
    <button
      data-testid="theme-toggle-btn"
      onClick={toggle}
      className="relative w-14 h-7 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-primary/50 bg-slate-200 dark:bg-slate-700"
      aria-label="Toggle theme"
    >
      <span
        className={`absolute top-0.5 left-0.5 w-6 h-6 rounded-full bg-white dark:bg-slate-900 shadow-md flex items-center justify-center transition-transform duration-300 ${
          isDark ? 'translate-x-7' : 'translate-x-0'
        }`}
      >
        {isDark ? <Moon size={14} className="text-blue-400" /> : <Sun size={14} className="text-amber-500" />}
      </span>
    </button>
  );
}
