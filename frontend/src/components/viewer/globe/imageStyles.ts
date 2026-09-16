export const STYLES = [
  // ── Realistic — photo-style final-stage visualization ──
  { id: 'photorealistic', label: 'Photo Realistic' },
  { id: 'photomontage', label: 'Photomontage' },
  { id: 'development', label: 'Development' },
  { id: 'atmospheric', label: 'Atmospheric' },
  { id: 'winter', label: 'Winter' },
  { id: 'night', label: 'Night' },
  // ── Concept — hand-drawn / painterly early-stage exploration ──
  { id: 'watercolour', label: 'Watercolour' },
  { id: 'charcoal', label: 'Charcoal' },
  { id: 'marker-render', label: 'Marker' },
  { id: 'pen-and-ink', label: 'Pen & Ink' },
  // ── Accurate — geometry-faithful architectural photography ──
  { id: 'survey', label: 'Survey' },
  { id: 'documentary', label: 'Documentary' },
  // ── Plan — top-down orthographic / drafted planning views ──
  { id: 'site-plan', label: 'Site Plan' },
  { id: 'site-plan-photo', label: 'Site Plan Photo' },
  { id: 'blueprint', label: 'Blueprint' },
  { id: 'site-plan-watercolor', label: 'Site Plan WC' },
  // ── Stylized — bold, graphic, distinctive ──
  { id: 'isometric', label: 'Isometric' },
  { id: 'clay-maquette', label: 'Clay' },
  { id: 'woodblock', label: 'Wood Block' },
  { id: 'collage', label: 'Collage' },
  { id: 'risograph', label: 'Risograph' },
  { id: 'pixel-art', label: 'Pixel Art' },
] as const;

// UI grouping for the style picker — keeps the new-user taxonomy visible.
// Update this when adding a style so it lands in the right group in the UI.
export const STYLE_GROUPS = [
  { label: 'Realistic', ids: ['photorealistic', 'photomontage', 'development', 'atmospheric', 'winter', 'night'] },
  { label: 'Accurate', ids: ['survey', 'documentary'] },
  { label: 'Concept', ids: ['watercolour', 'charcoal', 'marker-render', 'pen-and-ink'] },
  { label: 'Plan', ids: ['site-plan', 'site-plan-photo', 'blueprint', 'site-plan-watercolor'] },
  { label: 'Stylized', ids: ['isometric', 'clay-maquette', 'woodblock', 'collage', 'risograph', 'pixel-art'] },
] as const;

