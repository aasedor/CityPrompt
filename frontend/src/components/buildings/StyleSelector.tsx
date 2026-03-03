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
  contemporary: 'bg-blue-500/20 text-blue-400',
  minimal: 'bg-neutral-500/20 text-neutral-400',
  glass: 'bg-cyan-500/20 text-cyan-400',
  traditional: 'bg-amber-500/20 text-amber-400',
  ornamental: 'bg-yellow-500/20 text-yellow-400',
  concrete: 'bg-stone-500/20 text-stone-400',
  wood: 'bg-orange-500/20 text-orange-400',
  urban: 'bg-violet-500/20 text-violet-400',
  residential: 'bg-pink-500/20 text-pink-400',
  steel: 'bg-slate-500/20 text-slate-400',
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
              ? 'bg-purple-500/20 text-purple-400 ring-1 ring-purple-400/30'
              : 'bg-white/10 text-neutral-400 hover:bg-white/[0.15]'
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
                ? 'bg-purple-500/20 text-purple-400 ring-1 ring-purple-400/30'
                : 'bg-white/10 text-neutral-400 hover:bg-white/[0.15]'
            }`}
          >
            {s.name}
          </button>
        ))}
        {styles.length > 8 && (
          <span className="self-center text-xs text-neutral-400">+{styles.length - 8} more</span>
        )}
      </div>
    );
  }

  return (
    <div>
      {/* Search + tag filters */}
      <div className="mb-3 flex items-center gap-2">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search styles..."
            className="w-full rounded-lg border border-white/[0.08] bg-white/[0.04] py-1.5 pl-8 pr-3 text-xs text-neutral-100 focus:border-purple-400 focus:outline-none focus:ring-1 focus:ring-purple-400"
          />
        </div>
      </div>

      {/* Tag filter chips */}
      <div className="mb-3 flex flex-wrap gap-1">
        <button
          onClick={() => setTagFilter(null)}
          className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
            !tagFilter ? 'bg-purple-500/20 text-purple-400' : 'bg-white/[0.03] text-neutral-400 hover:bg-white/10'
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
                ? TAG_COLORS[tag] || 'bg-purple-500/20 text-purple-400'
                : 'bg-white/[0.03] text-neutral-400 hover:bg-white/10'
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
              ? 'border-purple-400/40 bg-purple-500/15 ring-1 ring-purple-400/20'
              : 'border-white/[0.08] hover:border-white/[0.15] hover:bg-white/[0.06]'
          }`}
        >
          <p className="text-xs font-semibold text-neutral-100">Default</p>
          <p className="mt-0.5 text-[10px] text-neutral-400">No style applied</p>
        </button>

        {filtered.map((style) => (
          <button
            key={style.id}
            onClick={() => onSelect(style.id)}
            className={`rounded-lg border p-2.5 text-left transition-all ${
              selectedStyle === style.id
                ? 'border-purple-400/40 bg-purple-500/15 ring-1 ring-purple-400/20'
                : 'border-white/[0.08] hover:border-white/[0.15] hover:bg-white/[0.06]'
            }`}
          >
            <p className="text-xs font-semibold text-neutral-100">{style.name}</p>
            <p className="mt-0.5 line-clamp-2 text-[10px] text-neutral-400">{style.description}</p>
            <div className="mt-1.5 flex flex-wrap gap-0.5">
              {style.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className={`rounded px-1 py-0.5 text-[9px] font-medium ${
                    TAG_COLORS[tag] || 'bg-white/10 text-neutral-400'
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
        <p className="mt-4 text-center text-xs text-neutral-400">No styles match your search.</p>
      )}
    </div>
  );
}
