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
  minimal: 'bg-neutral-500/20 text-primary-950/50',
  glass: 'bg-cyan-500/20 text-cyan-400',
  traditional: 'bg-amber-500/20 text-amber-400',
  ornamental: 'bg-yellow-500/20 text-yellow-400',
  concrete: 'bg-stone-500/20 text-stone-400',
  wood: 'bg-orange-500/20 text-orange-400',
  urban: 'bg-violet-500/20 text-violet-400',
  residential: 'bg-pink-500/20 text-pink-400',
  steel: 'bg-slate-500/20 text-slate-400',
};

const STYLE_PHOTOS: Record<string, string> = {
  modern: 'https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=900&q=80',
  classical: 'https://images.unsplash.com/photo-1529260830199-42c24126f198?auto=format&fit=crop&w=900&q=80',
  brutalist: 'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=900&q=80',
  art_deco: 'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=900&q=80',
  industrial: 'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=900&q=80',
  victorian: 'https://images.unsplash.com/photo-1464146072230-91cabc968266?auto=format&fit=crop&w=900&q=80',
  mediterranean: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=900&q=80',
  scandinavian: 'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80',
  colonial: 'https://images.unsplash.com/photo-1449844908441-8829872d2607?auto=format&fit=crop&w=900&q=80',
  japanese_modern: 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=900&q=80',
  neo_gothic: 'https://images.unsplash.com/photo-1479510318569-1e327f2b55e3?auto=format&fit=crop&w=900&q=80',
  mid_century_modern: 'https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=900&q=80',
  tropical: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80',
  high_tech: 'https://images.unsplash.com/photo-1486325212027-8081e485255e?auto=format&fit=crop&w=900&q=80',
  postmodern: 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=900&q=80',
  deconstructivist: 'https://images.unsplash.com/photo-1431576901776-e539bd916ba2?auto=format&fit=crop&w=900&q=80',
  organic: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&w=900&q=80',
  minimalist: 'https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=900&q=80',
  cottage: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80',
  warehouse: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=900&q=80',
};

function getStyleImage(style: ArchitecturalStyle): string | undefined {
  if (style.thumbnail_url) return style.thumbnail_url;
  return STYLE_PHOTOS[style.id];
}

export function StyleSelector({ selectedStyle, onSelect, compact }: StyleSelectorProps) {
  const [styles, setStyles] = useState<ArchitecturalStyle[]>([]);
  const [search, setSearch] = useState('');
  const [tagFilter, setTagFilter] = useState<string | null>(null);

  useEffect(() => {
    buildingsApi.getStyles().then(setStyles).catch(() => {});
  }, []);

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
              : 'bg-primary-950/[0.04] text-primary-950/50 hover:bg-primary-950/[0.08]'
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
                : 'bg-primary-950/[0.04] text-primary-950/50 hover:bg-primary-950/[0.08]'
            }`}
          >
            {s.name}
          </button>
        ))}
        {styles.length > 8 && (
          <span className="self-center text-xs text-primary-950/50">+{styles.length - 8} more</span>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-primary-950/50" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search styles..."
            className="w-full rounded-lg border border-primary-950/[0.08] bg-white py-1.5 pl-8 pr-3 text-xs text-neutral-100 focus:border-purple-400 focus:outline-none focus:ring-1 focus:ring-purple-400"
          />
        </div>
      </div>

      <div className="mb-3 flex flex-wrap gap-1">
        <button
          onClick={() => setTagFilter(null)}
          className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
            !tagFilter ? 'bg-purple-500/20 text-purple-400' : 'bg-primary-950/[0.02] text-primary-950/50 hover:bg-primary-950/[0.04]'
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
                : 'bg-primary-950/[0.02] text-primary-950/50 hover:bg-primary-950/[0.04]'
            }`}
          >
            {tag}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <button
          onClick={() => onSelect(null)}
          className={`rounded-lg border p-2.5 text-left transition-all ${
            !selectedStyle
              ? 'border-purple-400/40 bg-purple-500/15 ring-1 ring-purple-400/20'
              : 'border-primary-950/[0.08] hover:border-primary-950/[0.12] hover:bg-white'
          }`}
        >
          <div className="mb-2 flex aspect-[4/3] items-center justify-center rounded-md border border-dashed border-primary-950/[0.12] bg-primary-950/[0.04]">
            <p className="text-xs text-primary-950/50">No photo preset</p>
          </div>
          <p className="text-xs font-semibold text-neutral-100">Default</p>
          <p className="mt-0.5 text-[10px] text-primary-950/50">No style applied</p>
        </button>

        {filtered.map((style) => {
          const imageUrl = getStyleImage(style);
          return (
            <button
              key={style.id}
              onClick={() => onSelect(style.id)}
              className={`rounded-lg border p-2.5 text-left transition-all ${
                selectedStyle === style.id
                  ? 'border-purple-400/40 bg-purple-500/15 ring-1 ring-purple-400/20'
                  : 'border-primary-950/[0.08] hover:border-primary-950/[0.12] hover:bg-white'
              }`}
            >
              <div className="relative mb-2 aspect-[4/3] overflow-hidden rounded-md bg-primary-950/[0.06]">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt={style.name}
                    className="h-full w-full object-cover"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                ) : null}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
                <p className="absolute bottom-1.5 left-2 text-[11px] font-semibold text-white">{style.name}</p>
              </div>
              <p className="line-clamp-2 text-[10px] text-primary-950/50">{style.description}</p>
              <div className="mt-1.5 flex flex-wrap gap-0.5">
                {style.tags.slice(0, 2).map((tag) => (
                  <span
                    key={tag}
                    className={`rounded px-1 py-0.5 text-[9px] font-medium ${
                      TAG_COLORS[tag] || 'bg-primary-950/[0.04] text-primary-950/50'
                    }`}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <p className="mt-4 text-center text-xs text-primary-950/50">No styles match your search.</p>
      )}
    </div>
  );
}

