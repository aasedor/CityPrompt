/**
 * Shared DOM-event helpers.
 */

/**
 * True when a keyboard event originated from an editable field (input, textarea,
 * select, or contenteditable). Window-level keyboard shortcuts — especially ones
 * that call preventDefault on printable keys like A/D — must bail out on these so
 * they don't swallow keystrokes meant for a focused field (e.g. the Edit Render box).
 */
export function isTextEntryTarget(target: EventTarget | null): boolean {
  const element = target as HTMLElement | null;
  return Boolean(element?.closest('input, textarea, select, [contenteditable="true"]'));
}
