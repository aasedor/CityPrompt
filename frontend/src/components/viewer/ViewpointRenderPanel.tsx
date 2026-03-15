import React, { useState, useMemo } from 'react';
import type { Map as MapboxMap } from 'mapbox-gl';
import type { SiteZone } from '@/types';
import { useViewpointPicker } from './useViewpointPicker';
import type { Viewpoint } from './useViewpointPicker';
import { useAIRender, AI_RENDER_STYLES } from './useAIRender';
import type { AIRenderResult } from './useAIRender';
import { collectArchetypeRenderInputs, mergeArchetypePrompts } from './collectArchetypeRenderInputs';

// Street-level render uses different base prompts than aerial
const STREET_BASE_PROMPT =
  'street level architectural photography, eye level perspective, ' +
  'photorealistic, professional render, sharp focus, 8k detail, ' +
  'natural daylight, pedestrian scale, activated ground floor, ';

function Spinner() {
  return (
    <svg style={{ animation: 'spin 1s linear infinite', width: 14, height: 14 }} viewBox="0 0 24 24" fill="none">
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.25)" strokeWidth="3" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ViewpointRenderPanelProps {
  map: MapboxMap | null;
  /** Render style inherited from the aerial panel */
  renderStyleId?: string;
  /** Site zones for archetype prompt extraction */
  siteZones?: SiteZone[];
  onRenderComplete?: (result: AIRenderResult, viewpoint: Viewpoint) => void;
  className?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ViewpointRenderPanel({
  map,
  renderStyleId,
  siteZones = [],
  onRenderComplete,
  className,
}: ViewpointRenderPanelProps) {
  const {
    viewpoints,
    activeViewpoint,
    isPlacing,
    startPlacing,
    cancelPlacing,
    previewViewpoint,
    returnToAerial,
    removeViewpoint,
    renameViewpoint,
  } = useViewpointPicker(map);

  const { render, isRendering, progress, result, error, reset } = useAIRender();

  const [customPrompt, setCustomPrompt]   = useState('');
  const [editingId, setEditingId]         = useState<string | null>(null);
  const [editLabel, setEditLabel]         = useState('');
  const [renderResults, setRenderResults] = useState<Record<string, AIRenderResult>>({});

  // Extract archetype data
  const archetypeInputs = useMemo(
    () => collectArchetypeRenderInputs(siteZones),
    [siteZones],
  );

  // Resolve the inherited style label for display
  const activeStyleLabel = useMemo(() => {
    if (!renderStyleId) return 'Modern Glass';
    return AI_RENDER_STYLES.find(s => s.id === renderStyleId)?.label ?? renderStyleId;
  }, [renderStyleId]);

  async function handleRender() {
    if (!map || !activeViewpoint) return;
    reset();

    // Build street-level prompt: base + inherited style + archetype + custom
    const archetype = archetypeInputs.positivePrompts.length > 0
      ? mergeArchetypePrompts(archetypeInputs)
      : { archetypePrompt: undefined, archetypeNegative: undefined };

    const fullPrompt = STREET_BASE_PROMPT +
      [activeStyleLabel, customPrompt].filter(Boolean).join(', ');

    try {
      const res = await render(map, {
        style: renderStyleId || 'modern-glass',
        customPrompt: fullPrompt,
        controlStrength: 0.8,
        archetypePrompt: archetype.archetypePrompt || undefined,
        archetypeNegative: archetype.archetypeNegative || undefined,
        referenceImageUrls: archetypeInputs.referenceImageUrls.length > 0
          ? archetypeInputs.referenceImageUrls
          : undefined,
        imageSize: { width: 1024, height: 1024 },
        steps: 45,
      });
      if (res) {
        setRenderResults(prev => ({ ...prev, [activeViewpoint.id]: res }));
        onRenderComplete?.(res, activeViewpoint);
      }
    } catch { /* error shown in panel */ }
  }

  // ── Styles ─────────────────────────────────────────────────────────────────

  const panel: React.CSSProperties = {
    position: 'absolute',
    bottom: 24,
    right: 12,
    zIndex: 20,
    width: 288,
    borderRadius: 16,
    background: 'rgba(14, 17, 23, 0.92)',
    backdropFilter: 'blur(12px)',
    boxShadow: '0 12px 40px rgba(0,0,0,0.4)',
    border: '1px solid rgba(255,255,255,0.07)',
    color: '#f3f4f6',
    fontFamily: "'DM Sans', system-ui, sans-serif",
    fontSize: 13,
    overflow: 'hidden',
  };

  const sectionLabel: React.CSSProperties = {
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    color: 'rgba(255,255,255,0.35)',
    marginBottom: 6,
    display: 'block',
  };

  const vpRow = (active: boolean): React.CSSProperties => ({
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '7px 10px',
    borderRadius: 9,
    background: active ? 'rgba(99,102,241,0.18)' : 'rgba(255,255,255,0.04)',
    border: active ? '1px solid rgba(99,102,241,0.4)' : '1px solid transparent',
    cursor: 'pointer',
    marginBottom: 4,
    transition: 'all 0.15s',
  });

  const smallBtn = (color = 'rgba(255,255,255,0.08)'): React.CSSProperties => ({
    background: color,
    border: 'none',
    borderRadius: 6,
    padding: '3px 7px',
    color: '#f3f4f6',
    fontSize: 11,
    cursor: 'pointer',
    flexShrink: 0,
  });

  const renderBtn: React.CSSProperties = {
    width: '100%',
    padding: '10px 0',
    borderRadius: 10,
    border: 'none',
    background: (!activeViewpoint || isRendering)
      ? 'rgba(255,255,255,0.06)'
      : 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
    color: (!activeViewpoint || isRendering) ? 'rgba(255,255,255,0.3)' : '#fff',
    fontWeight: 700,
    fontSize: 13,
    cursor: (!activeViewpoint || isRendering) ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div style={panel} className={className}>

      {/* Header */}
      <div style={{ padding: '14px 16px 10px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 16 }}>👁</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 13 }}>Street Renders</div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 1 }}>
            {viewpoints.length === 0
              ? 'Drop a viewpoint pin to start'
              : `${viewpoints.length} viewpoint${viewpoints.length !== 1 ? 's' : ''}`}
          </div>
        </div>
        {activeViewpoint && (
          <button
            style={{ ...smallBtn('rgba(99,102,241,0.2)'), marginLeft: 'auto', color: '#a5b4fc' }}
            onClick={returnToAerial}
          >
            ↑ Aerial
          </button>
        )}
      </div>

      <div style={{ padding: '12px 16px' }}>

        {/* Place pin button */}
        <button
          style={{
            width: '100%',
            padding: '9px 0',
            borderRadius: 9,
            border: isPlacing
              ? '1px solid rgba(245,158,11,0.6)'
              : '1px dashed rgba(255,255,255,0.2)',
            background: isPlacing ? 'rgba(245,158,11,0.1)' : 'transparent',
            color: isPlacing ? '#fcd34d' : 'rgba(255,255,255,0.5)',
            fontWeight: 600,
            fontSize: 12,
            cursor: 'pointer',
            marginBottom: 12,
            transition: 'all 0.15s',
          }}
          onClick={isPlacing ? cancelPlacing : startPlacing}
        >
          {isPlacing ? '✕  Click map to place pin…' : '＋  Add viewpoint pin'}
        </button>

        {/* Viewpoint list */}
        {viewpoints.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <span style={sectionLabel}>Viewpoints</span>
            {viewpoints.map(vp => {
              const isActive = activeViewpoint?.id === vp.id;
              const hasResult = !!renderResults[vp.id];

              return (
                <div
                  key={vp.id}
                  style={vpRow(isActive)}
                  onClick={() => previewViewpoint(vp)}
                >
                  {/* Edit label inline */}
                  {editingId === vp.id ? (
                    <input
                      autoFocus
                      value={editLabel}
                      onChange={e => setEditLabel(e.target.value)}
                      onBlur={() => {
                        if (editLabel.trim()) renameViewpoint(vp.id, editLabel.trim());
                        setEditingId(null);
                      }}
                      onKeyDown={e => {
                        if (e.key === 'Enter') {
                          if (editLabel.trim()) renameViewpoint(vp.id, editLabel.trim());
                          setEditingId(null);
                        }
                      }}
                      style={{
                        flex: 1,
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(99,102,241,0.5)',
                        borderRadius: 5,
                        color: '#fff',
                        fontSize: 12,
                        padding: '2px 6px',
                        outline: 'none',
                      }}
                      onClick={e => e.stopPropagation()}
                    />
                  ) : (
                    <span
                      style={{ flex: 1, fontSize: 12, fontWeight: isActive ? 600 : 400 }}
                      onDoubleClick={e => {
                        e.stopPropagation();
                        setEditingId(vp.id);
                        setEditLabel(vp.label);
                      }}
                      title="Double-click to rename"
                    >
                      {hasResult ? '✓ ' : ''}{vp.label}
                    </span>
                  )}

                  {/* View result button */}
                  {hasResult && (
                    <a
                      href={renderResults[vp.id].imageUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ ...smallBtn('rgba(99,102,241,0.25)'), color: '#a5b4fc', textDecoration: 'none' }}
                      onClick={e => e.stopPropagation()}
                    >
                      View
                    </a>
                  )}

                  {/* Delete */}
                  <button
                    style={{ ...smallBtn('rgba(239,68,68,0.15)'), color: '#fca5a5', padding: '3px 6px' }}
                    onClick={e => { e.stopPropagation(); removeViewpoint(vp.id); }}
                    title="Remove viewpoint"
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Only show render controls when a viewpoint is active */}
        {activeViewpoint && (
          <>
            {/* Inherited style indicator */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 10px',
              borderRadius: 8,
              background: 'rgba(255,255,255,0.04)',
              marginBottom: 8,
              fontSize: 11,
              color: 'rgba(255,255,255,0.5)',
            }}>
              <span style={{ color: '#f59e0b' }}>Style:</span>
              <span style={{ color: '#fff', fontWeight: 600 }}>{activeStyleLabel}</span>
              <span style={{ fontSize: 10, opacity: 0.5 }}>(from aerial panel)</span>
            </div>

            {/* Custom prompt override */}
            <span style={sectionLabel}>Extra Prompt (optional)</span>
            <textarea
              style={{
                width: '100%', boxSizing: 'border-box',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 7, padding: '7px 9px',
                color: '#f3f4f6', fontSize: 12,
                resize: 'vertical', minHeight: 42,
                outline: 'none', marginBottom: 10,
                fontFamily: 'inherit',
              }}
              placeholder="e.g. warm brick, activated retail, evening light…"
              value={customPrompt}
              onChange={e => setCustomPrompt(e.target.value)}
            />

            {/* Render button */}
            <button style={renderBtn} onClick={handleRender} disabled={!activeViewpoint || isRendering}>
              {isRendering
                ? <><Spinner />{progress || 'Rendering…'}</>
                : `⚡ Render "${activeViewpoint.label}"`
              }
            </button>

            {error && (
              <div style={{
                marginTop: 8, padding: '7px 9px', borderRadius: 7,
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
                color: '#fca5a5', fontSize: 11,
              }}>
                {error}
              </div>
            )}

            {/* Latest result preview */}
            {result && (
              <div style={{ marginTop: 10, borderRadius: 9, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)', position: 'relative' }}>
                <img src={result.imageUrl} alt="Street render" style={{ width: '100%', display: 'block' }} />
                <div style={{
                  position: 'absolute', bottom: 0, left: 0, right: 0,
                  padding: '5px 9px',
                  background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.5)' }}>
                    {activeViewpoint.label}
                  </span>
                  <a
                    href={result.imageUrl}
                    download={`render-${activeViewpoint.label}.png`}
                    style={{ fontSize: 11, color: '#a5b4fc', textDecoration: 'none', fontWeight: 600 }}
                  >
                    ↓ Save
                  </a>
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty state */}
        {viewpoints.length === 0 && !isPlacing && (
          <div style={{ textAlign: 'center', padding: '16px 0 4px', color: 'rgba(255,255,255,0.25)', fontSize: 12, lineHeight: 1.6 }}>
            Click "Add viewpoint pin"<br />
            then click anywhere on your site<br />
            to place a street-level camera
          </div>
        )}
      </div>
    </div>
  );
}
