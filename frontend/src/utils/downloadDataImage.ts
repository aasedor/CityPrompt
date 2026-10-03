/** Download a generated image through a Blob URL instead of a large data URL. */
export function downloadDataImage(imageUrl: string, filename: string): void {
  const match = /^data:([^;,]+);base64,([\s\S]+)$/.exec(imageUrl);
  if (!match) throw new Error('Expected a base64 image data URL');

  const binary = atob(match[2]);
  const buffer = new ArrayBuffer(binary.length);
  const bytes = new Uint8Array(buffer);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);

  const objectUrl = URL.createObjectURL(new Blob([buffer], { type: match[1] }));
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}
