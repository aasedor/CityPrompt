/** Only local app paths can be used as an authentication return destination. */
export function safeReturnTo(value: unknown): string {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    && !value.includes('\\') && !Array.from(value).some((char) => char.charCodeAt(0) < 32) ? value : '/projects';
}
