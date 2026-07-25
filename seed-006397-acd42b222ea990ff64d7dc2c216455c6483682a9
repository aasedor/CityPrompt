import { Monitor, Moon, Sun } from 'lucide-react';
import { useThemeStore } from '@/store/themeStore';

type ThemeOption = 'light' | 'system' | 'dark';

const options: Array<{
  value: ThemeOption;
  title: string;
  icon: typeof Sun;
  className: string;
}> = [
  { value: 'light', title: 'Light mode', icon: Sun, className: 'rounded-l-full' },
  { value: 'system', title: 'System theme', icon: Monitor, className: '' },
  { value: 'dark', title: 'Dark mode', icon: Moon, className: 'rounded-r-full' },
];

export function ThemeToggle({ className = '' }: { className?: string }) {
  const { theme, setTheme } = useThemeStore();

  const buttonClassName = (value: ThemeOption) =>
    `p-1.5 transition-colors ${
      theme === value
        ? 'bg-[#c9ff3d] text-[#151515]'
        : 'text-[#151515]/45 hover:bg-[#151515]/5 hover:text-[#151515]'
    }`;

  return (
    <div
      className={`flex items-center rounded-full border-2 border-[#151515] bg-white text-[#151515] shadow-[3px_3px_0_0_#151515] ${className}`}
      aria-label="Theme selector"
    >
      {options.map(({ value, title, icon: Icon, className: optionClassName }) => (
        <button
          key={value}
          type="button"
          onClick={() => setTheme(value)}
          className={`${optionClassName} ${buttonClassName(value)}`}
          title={title}
          aria-label={title}
          aria-pressed={theme === value}
        >
          <Icon size={14} />
        </button>
      ))}
    </div>
  );
}
