import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { buildingsApi } from '@/services/api';
import type { ArchitecturalStyle } from '@/types';

interface StyleSelectorProps {
  selectedStyle: string | null;
  onSelect: (styleId: string | null) => void;
  compact?: boolean;
}

const TAG_COLORS: Record<string, string> = {
  contemporary: 'bg-blue-100 text-blue-700',
  minimal: 'bg-gray-100 text-gray-700',
  glass: 'bg-cyan-100 text-cyan-700',
  traditional: 'bg-amber-100 text-amber-700',
  ornamental: 'bg-yellow-100 text-yellow-700',
  concrete: 'bg-stone-100 text-stone-700',
  wood: 'bg-orange-100 text-orange-700',
  urban: 'bg-violet-100 text-violet-700',
  residential: 'bg-pink-100 text-pink-700',
  steel: 'bg-slate-100 text-slate-700',
};

export function StyleSelector({ selectedStyle, onSelect, compact }: StyleSelectorProps) {
  const [styles, setStyles] = useState<ArchitecturalStyle[]>([]);
  const [search, setSearch] = useState('');
  const [tagFilter, setTagFilter] = useState<string | null>(null);

  useEffect(() => {
    buildingsApi.getStyles().then(setStyles).catch(() => {});
  }, []);

  // Collect all unique tags
  const allTags = [...new Set(styles.flatMap((s) => s.tags))].sort();

  const filtered = styles.filter((s) => {
    const matchesSearch =
      !search ||
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.description.toLowerCase().includes(search.toLowerCase()) ||
      s.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));
    const matchesTag = !tagFilter || s.tags.includes(tagFilter);
    return matchesSearch && matchesTag;
  });

  if (compact) {
    return (
      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => onSelect(null)}
          className={`rounded-full px-2.5 py-1 text-xs font-medium transition-all ${
            !selectedStyle
              ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Default
        </button>
        {styles.slice(0, 8).map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            title={s.description}
            className={`rounded-full px-2.5 py-1 text-xs font-medium transition-all ${
              selectedStyle === s.id
                ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {s.name}
          </button>
        ))}
        {styles.length > 8 && (
          <span className="self-center text-xs text-gray-400">+{styles.length - 8} more</span>
        )}
      </div>
    );
  }

  return (
    <div>
      {/* Search + tag filters */}
      <div className="mb-3 flex items-center gap-2">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search styles..."
            className="w-full rounded-lg border border-gray-200 py-1.5 pl-8 pr-3 text-xs focus:border-purple-400 focus:outline-none focus:ring-1 focus:ring-purple-400"
          />
        </div>
      </div>

      {/* Tag filter chips */}
      <div className="mb-3 flex flex-wrap gap-1">
        <button
          onClick={() => setTagFilter(null)}
          className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
            !tagFilter ? 'bg-purple-100 text-purple-700' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
          }`}
        >
          All
        </button>
        {allTags.map((tag) => (
          <button
            key={tag}
            onClick={() => setTagFilter(tagFilter === tag ? null : tag)}
            className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
              tagFilter === tag
                ? TAG_COLORS[tag] || 'bg-purple-100 text-purple-700'
                : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
            }`}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* Style grid */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {/* Default / None option */}
        <button
          onClick={() => onSelect(null)}
          className={`rounded-lg border p-2.5 text-left transition-all ${
            !selectedStyle
              ? 'border-purple-300 bg-purple-50 ring-1 ring-purple-200'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          }`}
        >
          <p className="text-xs font-semibold text-gray-800">Default</p>
          <p className="mt-0.5 text-[10px] text-gray-500">No style applied</p>
        </button>

        {filtered.map((style) => (
          <button
            key={style.id}
            onClick={() => onSelect(style.id)}
            className={`rounded-lg border p-2.5 text-left transition-all ${
              selectedStyle === style.id
                ? 'border-purple-300 bg-purple-50 ring-1 ring-purple-200'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <p className="text-xs font-semibold text-gray-800">{style.name}</p>
            <p className="mt-0.5 line-clamp-2 text-[10px] text-gray-500">{style.description}</p>
            <div className="mt-1.5 flex flex-wrap gap-0.5">
              {style.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className={`rounded px-1 py-0.5 text-[9px] font-medium ${
                    TAG_COLORS[tag] || 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {tag}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="mt-4 text-center text-xs text-gray-400">No styles match your search.</p>
      )}
    </div>
  );
}
