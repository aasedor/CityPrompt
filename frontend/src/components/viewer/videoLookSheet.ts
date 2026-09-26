/**
 * The video look sheet: the short, structured description of the finished
 * footage that replaces the per-zone lock prose in provider prompts.
 *
 * Geometry, camera and timing travel as data (the deterministic route preview
 * and, for depth-guided engines, the depth control track). The student only
 * chooses how the finished video should look. The prompt text itself is built
 * on the server (`backend/app/services/video_prompts.py`); this module only
 * mirrors the vocabulary and the note limit so the panel can validate early.
 */

export type VideoLookStyle =
  | 'photorealistic'
  | 'photomontage'
  | 'development'
  | 'atmospheric'
  | 'night'
  | 'winter'
  | 'survey'
  | 'documentary'
  | 'overcast'
  | 'after_rain';

export type VideoLookGroup = 'Realistic' | 'Accurate' | 'Weather';

export interface VideoLookOption {
  id: VideoLookStyle;
  label: string;
  detail: string;
  group: VideoLookGroup;
  /** Direct 3D image style that renders the matching anchor frame, when one exists. */
  imageStyle: string | null;
}

export const DEFAULT_VIDEO_LOOK: VideoLookStyle = 'photorealistic';
export const VIDEO_STUDENT_NOTE_MAX = 240;

export const VIDEO_LOOK_STYLES: readonly VideoLookOption[] = Object.freeze([
  { id: 'photorealistic', label: 'Photo Realistic', detail: 'Soft daylight · true materials', group: 'Realistic', imageStyle: 'photorealistic' },
  { id: 'photomontage', label: 'Photomontage', detail: 'One sun with the city', group: 'Realistic', imageStyle: 'photomontage' },
  { id: 'development', label: 'Development', detail: 'Bright · completed look', group: 'Realistic', imageStyle: 'development' },
  { id: 'atmospheric', label: 'Atmospheric', detail: 'Golden late-day light', group: 'Realistic', imageStyle: 'atmospheric' },
  { id: 'night', label: 'Night', detail: 'Blue hour · lit windows', group: 'Realistic', imageStyle: 'night' },
  { id: 'winter', label: 'Winter', detail: 'Thin snow · cold light', group: 'Realistic', imageStyle: 'winter' },
  { id: 'survey', label: 'Survey', detail: 'Even light · legible', group: 'Accurate', imageStyle: 'survey' },
  { id: 'documentary', label: 'Documentary', detail: 'Flat daylight · honest', group: 'Accurate', imageStyle: 'documentary' },
  { id: 'overcast', label: 'Overcast', detail: 'Diffuse · no hard shadows', group: 'Weather', imageStyle: 'documentary' },
  { id: 'after_rain', label: 'After rain', detail: 'Damp paving · clearing sky', group: 'Weather', imageStyle: 'photomontage' },
]);

export const VIDEO_LOOK_GROUPS: readonly VideoLookGroup[] = Object.freeze(['Realistic', 'Accurate', 'Weather']);

export function isVideoLookStyle(value: unknown): value is VideoLookStyle {
  return VIDEO_LOOK_STYLES.some((option) => option.id === value);
}

export function videoLookLabel(id: string | null | undefined): string {
  if (!id) return '';
  return VIDEO_LOOK_STYLES.find((option) => option.id === id)?.label ?? id.split('_').join(' ');
}

/** Mirror of the server's `sanitize_student_note`: one clean line, at most 240 characters. */
export function sanitizeStudentNote(note: string | null | undefined): string {
  if (!note) return '';
  let collapsed = note.replace(/\s+/g, ' ').trim();
  if (collapsed.length > VIDEO_STUDENT_NOTE_MAX) {
    collapsed = collapsed.slice(0, VIDEO_STUDENT_NOTE_MAX).trimEnd();
  }
  if (collapsed && !/[.!?]$/.test(collapsed)) collapsed = `${collapsed}.`;
  return collapsed;
}
