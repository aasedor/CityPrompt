/**
 * MassingOptionPicker.tsx
 *
 * Displays 3 massing option cards. Clicking a card updates the active massing
 * preview on the map. "Use This Layout" advances to Step 3.
 */

import type { SiteMassingOption } from '@/types';

interface MassingOptionPickerProps {
  options: SiteMassingOption[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onConfirm: () => void;
}

export function MassingOptionPicker({ options, activeIndex, onSelect, onConfirm }: MassingOptionPickerProps) {
  if (options.length === 0) return null;

  return (
    <div className="flex flex-col gap-3 p-3">
      <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
        Choose a Massing Layout
      </h3>

      <div className="grid grid-cols-3 gap-3">
        {options.map((opt, idx) => {
          const isActive = idx === activeIndex;
          return (
            <button
              key={idx}
              onClick={() => onSelect(idx)}
              className={`
                relative flex flex-col gap-2 p-4 rounded-lg border-2 text-left transition-all
                ${isActive
                  ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                  : 'border-gray-700 bg-gray-800/50 hover:border-gray-500 hover:bg-gray-800'
                }
              `}
            >
              {/* Option label */}
              <div className="flex items-center justify-between">
                <span className={`text-sm font-bold ${isActive ? 'text-blue-400' : 'text-gray-200'}`}>
                  {opt.option_label}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${isActive ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-400'}`}>
                  {idx + 1}/{options.length}
                </span>
              </div>

              {/* Stats */}
              <div className="flex gap-3 text-xs text-gray-400">
                <span>
                  <strong className="text-gray-200">{opt.total_building_count}</strong> buildings
                </span>
                {opt.density_achieved != null && (
                  <span>
                    <strong className="text-gray-200">{opt.density_achieved.toFixed(1)}</strong> /ha
                  </span>
                )}
                {opt.total_floor_area_m2 != null && (
                  <span>
                    <strong className="text-gray-200">{(opt.total_floor_area_m2 / 1000).toFixed(0)}k</strong> m²
                  </span>
                )}
              </div>

              {/* Reasoning */}
              <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                {opt.reasoning}
              </p>

              {/* Active indicator */}
              {isActive && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full border-2 border-gray-900" />
              )}
            </button>
          );
        })}
      </div>

      {/* Confirm button */}
      <button
        onClick={onConfirm}
        className="mt-2 w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg transition-colors"
      >
        Use This Layout
      </button>
    </div>
  );
}
